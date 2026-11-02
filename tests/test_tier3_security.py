import hashlib
from tests.test_base import BaseTestCase

class Tier3SecurityTestCase(BaseTestCase):

    def test_sec01_unauthenticated_user_redirected_from_protected_routes(self):
        protected_routes = [
            "/tong-quan",
            "/quan-nhan",
            "/dien-thoai",
            "/giao-nhan",
            "/ca-truc",
            "/cau-hinh-gio",
            "/tai-khoan-phan-quyen",
            "/bao-cao"
        ]
        for route in protected_routes:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 302)
            self.assertIn("/dang-nhap", res.headers.get("Location", ""))

    def test_sec02_session_clearing_on_login_prevents_session_fixation(self):
        with self.client.session_transaction() as sess:
            sess["attacker_planted_token"] = "stolen_session_12345"

        self.login("admin", "admin123")

        with self.client.session_transaction() as sess:
            self.assertNotIn("attacker_planted_token", sess)

    def test_sec03_unauthorized_user_blocked_from_admin_accounts_page(self):
        self.login("tuananh", "12345678")
        res = self.client.get("/tai-khoan-phan-quyen")
        if res.status_code == 302:
            self.assertIn("/tong-quan", res.headers.get("Location", ""))
        else:
            self.assertEqual(res.status_code, 403)

    def test_sec04_unauthorized_user_blocked_from_schedule_config_page(self):
        self.login("tuananh", "12345678")
        res = self.client.get("/cau-hinh-gio")
        if res.status_code == 302:
            self.assertIn("/tong-quan", res.headers.get("Location", ""))
        else:
            self.assertEqual(res.status_code, 403)

    def test_sec05_subordinate_cannot_delete_super_admin(self):
        self.login("tuananh", "12345678")
        self.client.post("/tai-khoan/xoa/1", follow_redirects=True)
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT dang_dung FROM tai_khoan WHERE ten_dang_nhap = 'admin'")
        row = cur.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 1)

    def test_sec06_subordinate_cannot_change_super_admin_password(self):
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT mat_khau_ma_hoa FROM tai_khoan WHERE ten_dang_nhap = 'admin'")
        orig_hash = cur.fetchone()[0]
        conn.close()

        self.login("tuananh", "12345678")
        self.client.post(
            "/tai-khoan/sua/1",
            data={
                "ho_ten": "Hacked Admin",
                "mat_khau_moi": "hacked123456",
                "khoa_vai_tro": "1",
                "dang_dung": "1"
            },
            follow_redirects=True
        )

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT mat_khau_ma_hoa, ho_ten FROM tai_khoan WHERE ten_dang_nhap = 'admin'")
        row = cur.fetchone()
        conn.close()
        self.assertEqual(row[0], orig_hash)
        self.assertNotEqual(row[1], "Hacked Admin")

    def test_sec07_horizontal_data_scoping_unit_cannot_view_other_platoon_soldiers(self):
        self.login("vanbinh", "12345678")
        res = self.client.get("/quan-nhan")
        self.assertEqual(res.status_code, 200)
        self.assertNotIn("QN003".encode("utf-8"), res.data)
        self.assertNotIn("QN004".encode("utf-8"), res.data)

    def test_sec08_horizontal_data_scoping_unit_cannot_access_other_platoon_cabinets(self):
        self.login("vanbinh", "12345678")
        res = self.client.get("/tu-dien-thoai/T02")
        if res.status_code == 200:
            self.assertNotIn("B01".encode("utf-8"), res.data)
        else:
            self.assertIn(res.status_code, [302, 403, 404])

    def test_sec09_salted_password_hashing_verification(self):
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT mat_khau_ma_hoa FROM tai_khoan WHERE ten_dang_nhap = 'admin'")
        admin_hash = cur.fetchone()[0]
        conn.close()

        is_salted_format = admin_hash.startswith("scrypt:") or admin_hash.startswith("pbkdf2:") or ("$" in admin_hash)
        self.assertTrue(is_salted_format)

    def test_sec10_rainbow_table_resistance_verification(self):
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT mat_khau_ma_hoa FROM tai_khoan WHERE ten_dang_nhap = 'admin'")
        admin_hash = cur.fetchone()[0]
        conn.close()

        raw_sha256 = hashlib.sha256("admin123".encode("utf-8")).hexdigest()
        raw_md5 = hashlib.md5("admin123".encode("utf-8")).hexdigest()
        self.assertNotEqual(admin_hash, raw_sha256)
        self.assertNotEqual(admin_hash, raw_md5)
