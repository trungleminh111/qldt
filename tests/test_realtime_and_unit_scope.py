import os
import tempfile
import unittest
import config
from app import tao_ung_dung
from models.co_so_du_lieu import khoi_tao_co_so_du_lieu, lay_ket_noi
from models.du_lieu_mau import nap_du_lieu_mau

class TestRealtimeAndUnitScope(unittest.TestCase):
    def setUp(self):
        temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db_path = temp_file.name
        temp_file.close()
        self.original_db_path = config.DATABASE_PATH
        config.DATABASE_PATH = self.temp_db_path
        khoi_tao_co_so_du_lieu()
        nap_du_lieu_mau()
        app = tao_ung_dung()
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

    def tearDown(self):
        config.DATABASE_PATH = self.original_db_path
        if os.path.exists(self.temp_db_path):
            try:
                os.remove(self.temp_db_path)
            except OSError:
                pass

    def test_giao_nhan_realtime_clock_elements(self):
        with self.client.session_transaction() as sess:
            sess["nguoi_dung"] = {
                "ma_tu_sinh": 1,
                "ten_dang_nhap": "admin",
                "ho_ten": "Quản trị viên",
                "ten_vai_tro": "Quản trị",
                "ma_vai_tro": "QUAN_TRI",
                "pham_vi_loai": "TOAN_BO",
                "khoa_don_vi": None
            }
        response = self.client.get("/giao-nhan")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("liveClockBadge", html)
        self.assertIn("Thời gian thực (Live)", html)
        self.assertIn("btnResetLiveClock", html)
        self.assertIn("Lấy giờ hiện tại", html)
        self.assertIn('id="transNgay"', html)
        self.assertIn('id="transGio"', html)
        self.assertIn("nguoiDungSuaThoiGian()", html)

    def test_giao_nhan_scoped_unit_filter(self):
        with self.client.session_transaction() as sess:
            sess["nguoi_dung"] = {
                "ma_tu_sinh": 3,
                "ten_dang_nhap": "vanbinh",
                "ho_ten": "Nguyễn Văn Bình",
                "ten_vai_tro": "Chỉ huy",
                "ma_vai_tro": "CHI_HUY",
                "pham_vi_loai": "DON_VI",
                "khoa_don_vi": 2
            }
        response = self.client.get("/giao-nhan")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("Phân quyền quản lý:", html)
        self.assertIn("Trung đội 1", html)
        self.assertNotIn("data-don-vi=\"Trung đội 2\"", html)
        self.assertNotIn("data-don-vi=\"Trung đội 3\"", html)

    def test_giao_nhan_admin_sees_all_units(self):
        with self.client.session_transaction() as sess:
            sess["nguoi_dung"] = {
                "ma_tu_sinh": 1,
                "ten_dang_nhap": "admin",
                "ho_ten": "Quản trị viên",
                "ten_vai_tro": "Quản trị",
                "ma_vai_tro": "QUAN_TRI",
                "pham_vi_loai": "TOAN_BO",
                "khoa_don_vi": None
            }
        response = self.client.get("/giao-nhan")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("data-don-vi=\"ALL\"", html)
        self.assertIn("data-don-vi=\"Trung đội 1\"", html)
        self.assertIn("data-don-vi=\"Trung đội 2\"", html)
        self.assertIn("data-don-vi=\"Trung đội 3\"", html)

    def test_quan_nhan_scoped_unit_badge(self):
        with self.client.session_transaction() as sess:
            sess["nguoi_dung"] = {
                "ma_tu_sinh": 3,
                "ten_dang_nhap": "vanbinh",
                "ho_ten": "Nguyễn Văn Bình",
                "ten_vai_tro": "Chỉ huy",
                "ma_vai_tro": "CHI_HUY",
                "pham_vi_loai": "DON_VI",
                "khoa_don_vi": 2
            }
        response = self.client.get("/quan-nhan")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("Trung đội 1", html)
        self.assertNotIn("Tất cả đơn vị", html)

    def test_dien_thoai_scoped_unit_badge(self):
        with self.client.session_transaction() as sess:
            sess["nguoi_dung"] = {
                "ma_tu_sinh": 3,
                "ten_dang_nhap": "vanbinh",
                "ho_ten": "Nguyễn Văn Bình",
                "ten_vai_tro": "Chỉ huy",
                "ma_vai_tro": "CHI_HUY",
                "pham_vi_loai": "DON_VI",
                "khoa_don_vi": 2
            }
        response = self.client.get("/dien-thoai")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("Trung đội 1", html)
        self.assertNotIn("Tất cả đơn vị", html)

    def test_api_kiem_tra_gio_with_scoped_user(self):
        with self.client.session_transaction() as sess:
            sess["nguoi_dung"] = {
                "ma_tu_sinh": 3,
                "ten_dang_nhap": "vanbinh",
                "ho_ten": "Nguyễn Văn Bình",
                "ten_vai_tro": "Chỉ huy",
                "ma_vai_tro": "CHI_HUY",
                "pham_vi_loai": "DON_VI",
                "khoa_don_vi": 2
            }
        response_self = self.client.get("/api/kiem-tra-gio?khoa_qn=1&ngay=2026-11-02&gio=12:00")
        self.assertEqual(response_self.status_code, 200)
        data_self = response_self.get_json()
        self.assertIn("hop_le", data_self)

        response_other = self.client.get("/api/kiem-tra-gio?khoa_qn=3&ngay=2026-11-02&gio=12:00")
        self.assertEqual(response_other.status_code, 200)
        data_other = response_other.get_json()
        self.assertFalse(data_other["hop_le"])
        self.assertIn("không thuộc đơn vị", data_other["thong_bao"])

if __name__ == "__main__":
    unittest.main()
