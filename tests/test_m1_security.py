import hashlib
from tests.test_base import BaseTestCase
from models.phan_quyen_model import (
    ma_hoa_mat_khau,
    xac_thuc_mat_khau,
    xac_thuc_dang_nhap,
    xoa_tai_khoan,
    sua_tai_khoan,
    lay_tat_ca_tai_khoan,
    BAC_VAI_TRO
)

class M1SecurityTestCase(BaseTestCase):

    def test_password_hashing_is_salted(self):
        h1 = ma_hoa_mat_khau("mat_khau_test")
        h2 = ma_hoa_mat_khau("mat_khau_test")
        self.assertNotEqual(h1, h2)
        self.assertTrue(h1.startswith("scrypt:") or h1.startswith("pbkdf2:"))
        self.assertTrue(xac_thuc_mat_khau("mat_khau_test", h1))
        self.assertFalse(xac_thuc_mat_khau("sai_mat_khau", h1))

    def test_legacy_sha256_lazy_migration(self):
        legacy_plain = "matkhaucu123"
        legacy_hash = hashlib.sha256(legacy_plain.encode("utf-8")).hexdigest()
        con = self.get_db()
        cur = con.cursor()
        cur.execute("""
            INSERT INTO tai_khoan (ten_dang_nhap, mat_khau_ma_hoa, ho_ten)
            VALUES (?, ?, ?)
        """, ("chiensi_cu", legacy_hash, "Chiến sĩ cũ"))
        uid = cur.lastrowid
        cur.execute("""
            INSERT INTO tai_khoan_vai_tro (khoa_tai_khoan, khoa_vai_tro, pham_vi_loai, hieu_luc_tu)
            VALUES (?, 4, 'TOAN_BO', '2026-01-01')
        """, (uid,))
        con.commit()

        cur.execute("SELECT mat_khau_ma_hoa FROM tai_khoan WHERE ma_tu_sinh = ?", (uid,))
        h_before = cur.fetchone()[0]
        self.assertEqual(len(h_before), 64)

        user = xac_thuc_dang_nhap("chiensi_cu", legacy_plain)
        self.assertIsNotNone(user)
        self.assertEqual(user["ten_dang_nhap"], "chiensi_cu")

        cur.execute("SELECT mat_khau_ma_hoa FROM tai_khoan WHERE ma_tu_sinh = ?", (uid,))
        h_after = cur.fetchone()[0]
        con.close()
        self.assertNotEqual(h_before, h_after)
        self.assertTrue(h_after.startswith("scrypt:") or h_after.startswith("pbkdf2:"))

        user_retry = xac_thuc_dang_nhap("chiensi_cu", legacy_plain)
        self.assertIsNotNone(user_retry)

    def test_session_cookie_hardening(self):
        self.assertTrue(self.app.config.get("SESSION_COOKIE_HTTPONLY"))
        self.assertEqual(self.app.config.get("SESSION_COOKIE_SAMESITE"), "Lax")
        self.assertIsNotNone(self.app.config.get("PERMANENT_SESSION_LIFETIME"))

    def test_session_cleared_on_login(self):
        with self.client.session_transaction() as sess:
            sess["old_secret_value"] = "attack_123"
        res = self.login("admin", "admin123")
        self.assertEqual(res.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertNotIn("old_secret_value", sess)
            self.assertIn("nguoi_dung", sess)

    def test_unauthenticated_blocked_from_admin_pages(self):
        res1 = self.client.get("/cau-hinh-gio")
        self.assertEqual(res1.status_code, 302)
        self.assertIn("/dang-nhap", res1.headers.get("Location", ""))

        res2 = self.client.get("/tai-khoan-phan-quyen")
        self.assertEqual(res2.status_code, 302)
        self.assertIn("/dang-nhap", res2.headers.get("Location", ""))

    def test_unauthorized_user_blocked_from_admin_pages(self):
        self.login("tuananh", "12345678")

        res1 = self.client.get("/cau-hinh-gio", follow_redirects=True)
        self.assertIn("thẩm quyền".encode("utf-8"), res1.data)

        res2 = self.client.get("/tai-khoan-phan-quyen", follow_redirects=True)
        self.assertIn("thẩm quyền".encode("utf-8"), res2.data)

        res3 = self.client.post("/cau-hinh-gio/them", data={
            "khoa_cau_hinh_gio": "1",
            "thu_trong_tuan": "2",
            "gio_bat_dau": "08:00",
            "gio_ket_thuc": "09:00"
        }, follow_redirects=True)
        self.assertIn("thẩm quyền".encode("utf-8"), res3.data)

    def test_admin_has_full_access(self):
        self.login("admin", "admin123")
        res1 = self.client.get("/cau-hinh-gio")
        self.assertEqual(res1.status_code, 200)
        res2 = self.client.get("/tai-khoan-phan-quyen")
        self.assertEqual(res2.status_code, 200)

    def test_admin_account_deletion_forbidden(self):
        self.login("admin", "admin123")
        res = self.client.post("/tai-khoan/xoa/1", follow_redirects=True)
        self.assertIn("quản trị tối cao".encode("utf-8"), res.data)

        con = self.get_db()
        cur = con.cursor()
        cur.execute("SELECT ten_dang_nhap FROM tai_khoan WHERE ma_tu_sinh = 1")
        row = cur.fetchone()
        con.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "admin")

        with self.assertRaises(PermissionError):
            xoa_tai_khoan(1)

    def test_subordinate_cannot_edit_admin_account(self):
        with self.assertRaises(PermissionError):
            sua_tai_khoan(1, "Hacker Admin", mat_khau_moi="hacked123", nguoi_thuc_hien="tuananh")

        self.login("tuananh", "12345678")
        res = self.client.post("/tai-khoan/sua/1", data={
            "ho_ten": "Hacked",
            "khoa_vai_tro": "1",
            "pham_vi_loai": "TOAN_BO"
        }, follow_redirects=True)
        self.assertIn("thẩm quyền".encode("utf-8"), res.data)

    def test_admin_can_edit_admin_account(self):
        sua_tai_khoan(1, "Nguyễn Minh Quân", nguoi_thuc_hien="admin")
        self.login("admin", "admin123")
        res = self.client.post("/tai-khoan/sua/1", data={
            "ho_ten": "Nguyễn Minh Quân - QL",
            "khoa_vai_tro": "1",
            "pham_vi_loai": "TOAN_BO"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("cập nhật thông tin tài khoản thành công".encode("utf-8"), res.data)

    def test_role_hierarchy_filtering(self):
        all_accounts = lay_tat_ca_tai_khoan(bac_nguoi_xem=None)
        self.assertTrue(any(tk["ten_dang_nhap"] == "admin" for tk in all_accounts))

        subordinate_accounts = lay_tat_ca_tai_khoan(bac_nguoi_xem=50)
        user_names = [tk["ten_dang_nhap"] for tk in subordinate_accounts]
        self.assertNotIn("admin", user_names)
        self.assertNotIn("levanson", user_names)
        self.assertIn("tuananh", user_names)

    def test_subordinate_cannot_grant_superior_role(self):
        con = self.get_db()
        cur = con.cursor()
        cur.execute("SELECT ma_tu_sinh FROM vai_tro WHERE ma_vai_tro = 'QUAN_TRI'")
        admin_role_id = cur.fetchone()[0]
        con.close()

        with self.client.session_transaction() as sess:
            sess["nguoi_dung"] = {
                "ma_tu_sinh": 2,
                "ten_dang_nhap": "tuananh",
                "ho_ten": "Phạm Tuấn Anh",
                "ma_vai_tro": "NGUOI_TRUC",
                "cac_quyen": ["QUANTRI.TAIKHOAN"],
                "danh_sach_quyen": ["QUANTRI.TAIKHOAN"],
                "pham_vi_loai": "TOAN_BO"
            }

        res = self.client.post("/tai-khoan/them", data={
            "ten_dang_nhap": "tanbinh_vip",
            "mat_khau": "12345678",
            "ho_ten": "Tân Binh VIP",
            "khoa_vai_tro": str(admin_role_id),
            "pham_vi_loai": "TOAN_BO"
        }, follow_redirects=True)
        self.assertIn("cao hơn cấp bậc".encode("utf-8"), res.data)

    def test_sidebar_menu_scoping(self):
        self.login("tuananh", "12345678")
        res = self.client.get("/tong-quan")
        self.assertNotIn("/cau-hinh-gio".encode("utf-8"), res.data)
        self.assertNotIn("/tai-khoan-phan-quyen".encode("utf-8"), res.data)

        self.logout()
        self.login("admin", "admin123")
        res_admin = self.client.get("/tong-quan")
        self.assertIn("/cau-hinh-gio".encode("utf-8"), res_admin.data)
        self.assertIn("/tai-khoan-phan-quyen".encode("utf-8"), res_admin.data)

