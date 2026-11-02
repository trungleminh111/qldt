import os
import json
import sqlite3
import tempfile
import unittest
from datetime import datetime
from unittest.mock import patch
import config
from app import tao_ung_dung
from models.co_so_du_lieu import (
    khoi_tao_co_so_du_lieu,
    kiem_tra_va_nang_cap_bang_ban_giao,
    lay_ket_noi
)
from models.du_lieu_mau import nap_du_lieu_mau
from models.ca_truc_model import (
    lay_ca_hien_tai,
    thuc_hien_ban_giao_ca,
    lay_chi_tiet_ban_giao
)

class MockDateTime:
    def __init__(self, time_string):
        self._dt = datetime.strptime(time_string, "%Y-%m-%d %H:%M")

    def strftime(self, format_spec):
        return self._dt.strftime(format_spec)

class TestOvernightShiftCalculation(unittest.TestCase):
    def setUp(self):
        temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db_path = temp_file.name
        temp_file.close()
        self.original_db_path = config.DATABASE_PATH
        config.DATABASE_PATH = self.temp_db_path
        khoi_tao_co_so_du_lieu()
        nap_du_lieu_mau()
        connection = lay_ket_noi()
        cursor = connection.cursor()
        cursor.execute("UPDATE ca_truc SET gio_ket_thuc = '21:59' WHERE ma_ca = 'CA_TOI'")
        cursor.execute(
            "INSERT INTO ca_truc (ma_ca, ten_ca, gio_bat_dau, gio_ket_thuc) VALUES (?, ?, ?, ?)",
            ("CA_DEM", "Ca gac dem", "22:00", "06:00")
        )
        connection.commit()
        connection.close()

    def tearDown(self):
        config.DATABASE_PATH = self.original_db_path
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_overnight_shift_before_midnight(self):
        with patch("models.ca_truc_model.datetime") as mock_dt:
            mock_dt.now.return_value = MockDateTime("2026-11-02 23:00")
            ca = lay_ca_hien_tai()
            self.assertIsNotNone(ca)
            self.assertEqual(ca["ma_ca"], "CA_DEM")

    def test_overnight_shift_after_midnight(self):
        with patch("models.ca_truc_model.datetime") as mock_dt:
            mock_dt.now.return_value = MockDateTime("2026-11-02 03:00")
            ca = lay_ca_hien_tai()
            self.assertIsNotNone(ca)
            self.assertEqual(ca["ma_ca"], "CA_DEM")

    def test_overnight_shift_boundary_start(self):
        with patch("models.ca_truc_model.datetime") as mock_dt:
            mock_dt.now.return_value = MockDateTime("2026-11-02 22:00")
            ca = lay_ca_hien_tai()
            self.assertIsNotNone(ca)
            self.assertEqual(ca["ma_ca"], "CA_DEM")

    def test_overnight_shift_boundary_end(self):
        with patch("models.ca_truc_model.datetime") as mock_dt:
            mock_dt.now.return_value = MockDateTime("2026-11-02 06:00")
            ca = lay_ca_hien_tai()
            self.assertIsNotNone(ca)
            self.assertEqual(ca["ma_ca"], "CA_DEM")

    def test_daytime_shift_selection(self):
        with patch("models.ca_truc_model.datetime") as mock_dt:
            mock_dt.now.return_value = MockDateTime("2026-11-02 09:00")
            ca = lay_ca_hien_tai()
            self.assertIsNotNone(ca)
            self.assertEqual(ca["ma_ca"], "CA_SANG")

    def test_fallback_when_no_active_shift(self):
        with patch("models.ca_truc_model.lay_danh_sach_ca_truc") as mock_list:
            mock_list.return_value = []
            ca = lay_ca_hien_tai()
            self.assertIsNone(ca)

class TestDatabaseAutoMigration(unittest.TestCase):
    def setUp(self):
        temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db_path = temp_file.name
        temp_file.close()
        self.original_db_path = config.DATABASE_PATH
        config.DATABASE_PATH = self.temp_db_path

        legacy_connection = sqlite3.connect(self.temp_db_path)
        legacy_connection.execute("""
            CREATE TABLE ban_giao_ca (
                ma_tu_sinh INTEGER PRIMARY KEY AUTOINCREMENT,
                khoa_ca_truc INTEGER NOT NULL,
                ngay_truc TEXT NOT NULL,
                khoa_nguoi_ban_giao INTEGER NOT NULL,
                khoa_nguoi_nhan INTEGER NOT NULL,
                tong_thiet_bi INTEGER DEFAULT 0,
                dang_trong_tu INTEGER DEFAULT 0,
                da_lay INTEGER DEFAULT 0,
                chua_nop INTEGER DEFAULT 0,
                bat_thuong INTEGER DEFAULT 0,
                ghi_chu_ban_giao TEXT
            )
        """)
        legacy_connection.commit()
        legacy_connection.close()

    def tearDown(self):
        config.DATABASE_PATH = self.original_db_path
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_auto_migration_adds_all_snapshot_columns(self):
        connection = sqlite3.connect(self.temp_db_path)
        initial_columns = [row[1] for row in connection.execute("PRAGMA table_info(ban_giao_ca)").fetchall()]
        connection.close()

        self.assertNotIn("du_lieu_snapshot", initial_columns)
        self.assertNotIn("ma_tu_snapshot", initial_columns)
        self.assertNotIn("ten_ngan_snapshot", initial_columns)
        self.assertNotIn("so_qua_han", initial_columns)

        kiem_tra_va_nang_cap_bang_ban_giao()

        connection_after = sqlite3.connect(self.temp_db_path)
        upgraded_columns = [row[1] for row in connection_after.execute("PRAGMA table_info(ban_giao_ca)").fetchall()]
        connection_after.close()

        self.assertIn("du_lieu_snapshot", upgraded_columns)
        self.assertIn("ma_tu_snapshot", upgraded_columns)
        self.assertIn("ten_ngan_snapshot", upgraded_columns)
        self.assertIn("so_qua_han", upgraded_columns)

    def test_auto_migration_is_idempotent(self):
        kiem_tra_va_nang_cap_bang_ban_giao()
        kiem_tra_va_nang_cap_bang_ban_giao()

        connection = sqlite3.connect(self.temp_db_path)
        columns = [row[1] for row in connection.execute("PRAGMA table_info(ban_giao_ca)").fetchall()]
        connection.close()

        self.assertEqual(columns.count("du_lieu_snapshot"), 1)
        self.assertEqual(columns.count("ma_tu_snapshot"), 1)
        self.assertEqual(columns.count("ten_ngan_snapshot"), 1)
        self.assertEqual(columns.count("so_qua_han"), 1)

class TestShiftHandoverSubmission(unittest.TestCase):
    def setUp(self):
        temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db_path = temp_file.name
        temp_file.close()
        self.original_db_path = config.DATABASE_PATH
        config.DATABASE_PATH = self.temp_db_path
        khoi_tao_co_so_du_lieu()
        nap_du_lieu_mau()
        self.app = tao_ung_dung()
        self.client = self.app.test_client()

    def tearDown(self):
        config.DATABASE_PATH = self.original_db_path
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_handover_submission_success(self):
        login_response = self.client.post("/dang-nhap", data={
            "ten_dang_nhap": "admin",
            "mat_khau": "admin123"
        })
        self.assertEqual(login_response.status_code, 302)

        submit_response = self.client.post("/ca-truc/xac-nhan", data={
            "khoa_ca": "1",
            "khoa_nguoi_nhan": "2",
            "ghi_chu": "Ban giao ca kiem tra he thong M13",
            "bat_thuong": "0"
        })
        self.assertEqual(submit_response.status_code, 302)
        self.assertIn("/ca-truc", submit_response.headers.get("Location"))

        connection = lay_ket_noi()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM ban_giao_ca ORDER BY ma_tu_sinh DESC LIMIT 1")
        record = cursor.fetchone()
        self.assertIsNotNone(record)
        self.assertEqual(record["ghi_chu_ban_giao"], "Ban giao ca kiem tra he thong M13")

        snapshot_raw = record["du_lieu_snapshot"]
        self.assertIsNotNone(snapshot_raw)
        self.assertGreater(len(snapshot_raw), 0)

        snapshot = json.loads(snapshot_raw)
        self.assertIn("ca_truc", snapshot)
        self.assertIn("can_bo_ban_giao", snapshot)
        self.assertIn("can_bo_tiep_nhan", snapshot)
        self.assertIn("so_lieu", snapshot)
        self.assertIn("danh_sach_chua_nop", snapshot)
        self.assertIn("kiem_tra_thuc_te", snapshot)
        self.assertEqual(snapshot["ghi_chu"], "Ban giao ca kiem tra he thong M13")

        cursor.execute("SELECT * FROM nhat_ky WHERE hanh_dong = ? ORDER BY ma_tu_sinh DESC LIMIT 1", ("BAN_GIAO_CA",))
        audit_log = cursor.fetchone()
        self.assertIsNotNone(audit_log)
        self.assertEqual(audit_log["ten_bang"], "ban_giao_ca")
        self.assertEqual(audit_log["khoa_ban_ghi"], record["ma_tu_sinh"])
        self.assertIn("Ban giao ca kiem tra he thong M13", audit_log["ly_do"])
        connection.close()

    def test_handover_submission_missing_required_fields(self):
        self.client.post("/dang-nhap", data={
            "ten_dang_nhap": "admin",
            "mat_khau": "admin123"
        })

        connection = lay_ket_noi()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM ban_giao_ca")
        count_before = cursor.fetchone()[0]

        submit_response = self.client.post("/ca-truc/xac-nhan", data={
            "khoa_ca": "",
            "khoa_nguoi_nhan": "",
            "ghi_chu": "Loi thieu truong"
        })
        self.assertEqual(submit_response.status_code, 302)

        cursor.execute("SELECT COUNT(*) FROM ban_giao_ca")
        count_after = cursor.fetchone()[0]
        self.assertEqual(count_before, count_after)
        connection.close()

    def test_handover_submission_redirect_to_print_bien_ban(self):
        self.client.post("/dang-nhap", data={
            "ten_dang_nhap": "admin",
            "mat_khau": "admin123"
        })

        submit_response = self.client.post("/ca-truc/xac-nhan", data={
            "khoa_ca": "1",
            "khoa_nguoi_nhan": "3",
            "ghi_chu": "Ban giao kem in bien ban A4",
            "in_bien_ban": "1"
        })
        self.assertEqual(submit_response.status_code, 302)
        location = submit_response.headers.get("Location")
        self.assertIn("/ca-truc/bien-ban/", location)

class TestShiftHandoverViewsAndApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.temp_db_path = temp_file.name
        temp_file.close()
        cls.original_db_path = config.DATABASE_PATH
        config.DATABASE_PATH = cls.temp_db_path
        khoi_tao_co_so_du_lieu()
        nap_du_lieu_mau()
        cls.app = tao_ung_dung()
        cls.client = cls.app.test_client()

        cls.client.post("/dang-nhap", data={
            "ten_dang_nhap": "admin",
            "mat_khau": "admin123"
        })
        cls.client.post("/ca-truc/xac-nhan", data={
            "khoa_ca": "1",
            "khoa_nguoi_nhan": "2",
            "ghi_chu": "Mau bien ban khoi tao cho test"
        })

    @classmethod
    def tearDownClass(cls):
        config.DATABASE_PATH = cls.original_db_path
        if os.path.exists(cls.temp_db_path):
            os.remove(cls.temp_db_path)

    def test_render_a4_bien_ban_success(self):
        response = self.client.get("/ca-truc/bien-ban/1")
        self.assertEqual(response.status_code, 200)
        html_content = response.data.decode("utf-8")
        self.assertIn("BIÊN BẢN BÀN GIAO", html_content)
        self.assertIn("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM", html_content)
        self.assertIn("Độc lập - Tự do - Hạnh phúc", html_content)
        self.assertIn("BÊN TIẾP NHẬN", html_content)
        self.assertIn("BÊN BÀN GIAO", html_content)

    def test_render_a4_bien_ban_not_found_redirects(self):
        response = self.client.get("/ca-truc/bien-ban/999999")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/ca-truc", response.headers.get("Location"))

    def test_api_chi_tiet_success(self):
        response = self.client.get("/ca-truc/api/chi-tiet/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        payload = response.get_json()
        self.assertTrue(payload.get("thanh_cong"))
        self.assertIn("ban_giao", payload)
        self.assertIn("snapshot", payload)
        self.assertEqual(payload["ban_giao"]["ghi_chu_ban_giao"], "Mau bien ban khoi tao cho test")
        self.assertIn("ca_truc", payload["snapshot"])

    def test_api_chi_tiet_not_found(self):
        response = self.client.get("/ca-truc/api/chi-tiet/999999")
        self.assertEqual(response.status_code, 404)
        payload = response.get_json()
        self.assertFalse(payload.get("thanh_cong"))

class TestShiftHandoverQuickReturn(unittest.TestCase):
    def setUp(self):
        temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db_path = temp_file.name
        temp_file.close()
        self.original_db_path = config.DATABASE_PATH
        config.DATABASE_PATH = self.temp_db_path
        khoi_tao_co_so_du_lieu()
        nap_du_lieu_mau()
        self.app = tao_ung_dung()
        self.client = self.app.test_client()
        self.client.post("/dang-nhap", data={
            "ten_dang_nhap": "admin",
            "mat_khau": "admin123"
        })

    def tearDown(self):
        config.DATABASE_PATH = self.original_db_path
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_quick_return_json_success(self):
        response = self.client.post("/ca-truc/thu-hoi-nhanh", json={
            "khoa_quan_nhan": 2,
            "ghi_chu": "Thu hoi nhanh dien thoai tai cho"
        })
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload.get("thanh_cong"))
        self.assertIn("thành công", payload.get("thong_bao", "").lower())

    def test_quick_return_json_already_returned(self):
        first_attempt = self.client.post("/ca-truc/thu-hoi-nhanh", json={"khoa_quan_nhan": 2})
        self.assertEqual(first_attempt.status_code, 200)

        second_attempt = self.client.post("/ca-truc/thu-hoi-nhanh", json={"khoa_quan_nhan": 2})
        self.assertEqual(second_attempt.status_code, 400)
        payload = second_attempt.get_json()
        self.assertFalse(payload.get("thanh_cong"))

    def test_quick_return_json_missing_param(self):
        response = self.client.post("/ca-truc/thu-hoi-nhanh", json={})
        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertFalse(payload.get("thanh_cong"))

    def test_quick_return_form_post(self):
        response = self.client.post("/ca-truc/thu-hoi-nhanh", data={
            "khoa_quan_nhan": "4",
            "ghi_chu": "Thu hoi qua bieu mau form"
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn("/ca-truc", response.headers.get("Location"))

class TestShiftHandoverRBAC(unittest.TestCase):
    def setUp(self):
        temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db_path = temp_file.name
        temp_file.close()
        self.original_db_path = config.DATABASE_PATH
        config.DATABASE_PATH = self.temp_db_path
        khoi_tao_co_so_du_lieu()
        nap_du_lieu_mau()
        self.app = tao_ung_dung()
        self.client = self.app.test_client()

    def tearDown(self):
        config.DATABASE_PATH = self.original_db_path
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_unauthenticated_access_redirects_to_login(self):
        get_main = self.client.get("/ca-truc")
        self.assertEqual(get_main.status_code, 302)
        self.assertIn("/dang-nhap", get_main.headers.get("Location"))

        post_confirm = self.client.post("/ca-truc/xac-nhan", data={"khoa_ca": "1"})
        self.assertEqual(post_confirm.status_code, 302)
        self.assertIn("/dang-nhap", post_confirm.headers.get("Location"))

        get_receipt = self.client.get("/ca-truc/bien-ban/1")
        self.assertEqual(get_receipt.status_code, 302)
        self.assertIn("/dang-nhap", get_receipt.headers.get("Location"))

        get_api = self.client.get("/ca-truc/api/chi-tiet/1")
        self.assertEqual(get_api.status_code, 302)
        self.assertIn("/dang-nhap", get_api.headers.get("Location"))

        post_return = self.client.post("/ca-truc/thu-hoi-nhanh", json={"khoa_quan_nhan": 2})
        self.assertEqual(post_return.status_code, 302)
        self.assertIn("/dang-nhap", post_return.headers.get("Location"))

    def test_unauthorized_user_without_catruc_permission(self):
        with self.client.session_transaction() as session_store:
            session_store["nguoi_dung"] = {
                "ma_tu_sinh": 88,
                "ten_dang_nhap": "chien_si_test",
                "ho_ten": "Chiến Sĩ Kiểm Thử",
                "ma_vai_tro": "QUAN_NHAN",
                "cac_quyen": ["QUANNHAN.XEM"],
                "danh_sach_quyen": ["QUANNHAN.XEM"]
            }

        get_main = self.client.get("/ca-truc")
        self.assertEqual(get_main.status_code, 302)
        self.assertIn("/tong-quan", get_main.headers.get("Location"))

        post_confirm = self.client.post("/ca-truc/xac-nhan", data={"khoa_ca": "1", "khoa_nguoi_nhan": "2"})
        self.assertEqual(post_confirm.status_code, 302)
        self.assertIn("/tong-quan", post_confirm.headers.get("Location"))

        get_receipt = self.client.get("/ca-truc/bien-ban/1")
        self.assertEqual(get_receipt.status_code, 302)
        self.assertIn("/tong-quan", get_receipt.headers.get("Location"))

        get_api = self.client.get("/ca-truc/api/chi-tiet/1", headers={"Content-Type": "application/json"})
        self.assertEqual(get_api.status_code, 403)

        post_return = self.client.post("/ca-truc/thu-hoi-nhanh", json={"khoa_quan_nhan": 2})
        self.assertEqual(post_return.status_code, 403)

class TestUIIntegrityAllPagesAcrossPersonas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.temp_db_path = temp_file.name
        temp_file.close()
        cls.original_db_path = config.DATABASE_PATH
        config.DATABASE_PATH = cls.temp_db_path
        khoi_tao_co_so_du_lieu()
        nap_du_lieu_mau()
        cls.app = tao_ung_dung()

    @classmethod
    def tearDownClass(cls):
        config.DATABASE_PATH = cls.original_db_path
        if os.path.exists(cls.temp_db_path):
            os.remove(cls.temp_db_path)

    def test_admin_renders_all_7_main_pages(self):
        client = self.app.test_client()
        login_res = client.post("/dang-nhap", data={"ten_dang_nhap": "admin", "mat_khau": "admin123"})
        self.assertEqual(login_res.status_code, 302)

        routes_and_expectations = [
            ("/", "Bảng điều khiển"),
            ("/quan-nhan", "quân nhân"),
            ("/dien-thoai", "điện thoại"),
            ("/tu-dien-thoai", "Tủ"),
            ("/tu-dien-thoai/T01", "T01"),
            ("/ca-truc", "Bàn giao ca trực"),
            ("/bao-cao", "Báo cáo"),
            ("/cau-hinh-gio", "Cấu hình khung giờ"),
            ("/tai-khoan-phan-quyen", "Tài khoản")
        ]
        for route, text_marker in routes_and_expectations:
            response = client.get(route)
            self.assertEqual(response.status_code, 200, f"Route {route} failed with {response.status_code}")
            html_content = response.data.decode("utf-8")
            self.assertIn(text_marker.lower(), html_content.lower())

    def test_commander_renders_accessible_pages(self):
        client = self.app.test_client()
        login_res = client.post("/dang-nhap", data={"ten_dang_nhap": "levanson", "mat_khau": "12345678"})
        self.assertEqual(login_res.status_code, 302)

        routes = [
            "/",
            "/quan-nhan",
            "/dien-thoai",
            "/tu-dien-thoai",
            "/tu-dien-thoai/T01",
            "/ca-truc",
            "/bao-cao"
        ]
        for route in routes:
            response = client.get(route)
            self.assertEqual(response.status_code, 200, f"Commander failed on {route}")

    def test_duty_officer_renders_accessible_pages(self):
        client = self.app.test_client()
        login_res = client.post("/dang-nhap", data={"ten_dang_nhap": "tuananh", "mat_khau": "12345678"})
        self.assertEqual(login_res.status_code, 302)

        routes = [
            "/",
            "/quan-nhan",
            "/dien-thoai",
            "/tu-dien-thoai",
            "/tu-dien-thoai/T01",
            "/ca-truc",
            "/bao-cao"
        ]
        for route in routes:
            response = client.get(route)
            self.assertEqual(response.status_code, 200, f"Duty officer failed on {route}")

    def test_unit_duty_officer_renders_accessible_pages(self):
        client = self.app.test_client()
        login_res = client.post("/dang-nhap", data={"ten_dang_nhap": "vanbinh", "mat_khau": "12345678"})
        self.assertEqual(login_res.status_code, 302)

        routes = [
            "/",
            "/quan-nhan",
            "/dien-thoai",
            "/tu-dien-thoai",
            "/tu-dien-thoai/T01",
            "/ca-truc",
            "/bao-cao"
        ]
        for route in routes:
            response = client.get(route)
            self.assertEqual(response.status_code, 200, f"Unit duty officer failed on {route}")

if __name__ == "__main__":
    unittest.main()
