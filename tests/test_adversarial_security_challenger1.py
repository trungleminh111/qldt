import hashlib
from tests.test_base import BaseTestCase
from models.phan_quyen_model import (
    xoa_tai_khoan,
    sua_tai_khoan,
    them_tai_khoan,
    xac_thuc_mat_khau,
    xac_thuc_dang_nhap,
    lay_tat_ca_tai_khoan
)

class AdversarialSecurityChallenger1TestCase(BaseTestCase):

    def test_adv_rbac_anonymous_blocked_all_admin_endpoints(self):
        endpoints = [
            ("/tai-khoan-phan-quyen", "GET", None),
            ("/cau-hinh-gio", "GET", None),
            ("/tai-khoan/them", "POST", {"ten_dang_nhap": "hacker", "mat_khau": "123", "ho_ten": "Hacker", "khoa_vai_tro": "1"}),
            ("/tai-khoan/sua/1", "POST", {"ho_ten": "Hacked", "khoa_vai_tro": "1"}),
            ("/tai-khoan/xoa/1", "POST", {}),
            ("/vai-tro/cap-nhat-quyen/1", "POST", {"quyen_ids": ["1", "2"]}),
            ("/cau-hinh-gio/them", "POST", {"khoa_cau_hinh_gio": "1", "gio_bat_dau": "08:00", "gio_ket_thuc": "10:00"}),
            ("/cau-hinh-gio/sua/1", "POST", {"khoa_cau_hinh_gio": "1", "gio_bat_dau": "08:00", "gio_ket_thuc": "10:00"}),
            ("/cau-hinh-gio/xoa/1", "POST", {}),
            ("/ngay-dac-biet/them", "POST", {"ngay": "2026-12-31", "ly_do": "Test"}),
            ("/ngay-dac-biet/sua/1", "POST", {"ngay": "2026-12-31", "ly_do": "Test"}),
            ("/ngay-dac-biet/xoa/1", "POST", {})
        ]
        for url, method, data in endpoints:
            if method == "GET":
                res = self.client.get(url)
            else:
                res = self.client.post(url, data=data)
            self.assertEqual(res.status_code, 302)
            self.assertIn("/dang-nhap", res.headers.get("Location", ""))

    def test_adv_rbac_subordinate_blocked_from_schedule_config(self):
        self.login("tuananh", "12345678")

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM khung_gio")
        initial_kg_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM ngay_dac_biet")
        initial_ndb_count = cur.fetchone()[0]
        conn.close()

        res = self.client.get("/cau-hinh-gio")
        self.assertEqual(res.status_code, 302)
        self.assertIn("/tong-quan", res.headers.get("Location", ""))

        post_res1 = self.client.post(
            "/cau-hinh-gio/them",
            data={
                "khoa_cau_hinh_gio": "1",
                "thu_trong_tuan": "2",
                "gio_bat_dau": "01:00",
                "gio_ket_thuc": "02:00",
                "ghi_chu": "Attacker schedule"
            }
        )
        self.assertEqual(post_res1.status_code, 302)
        self.assertIn("/tong-quan", post_res1.headers.get("Location", ""))

        post_res2 = self.client.post(
            "/ngay-dac-biet/them",
            data={
                "ngay": "2026-11-20",
                "ly_do": "Attacker blackout",
                "cam_su_dung": "1"
            }
        )
        self.assertEqual(post_res2.status_code, 302)
        self.assertIn("/tong-quan", post_res2.headers.get("Location", ""))

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM khung_gio")
        after_kg_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM ngay_dac_biet")
        after_ndb_count = cur.fetchone()[0]
        conn.close()

        self.assertEqual(initial_kg_count, after_kg_count)
        self.assertEqual(initial_ndb_count, after_ndb_count)

    def test_adv_rbac_subordinate_blocked_from_user_management(self):
        self.login("tuananh", "12345678")

        res = self.client.get("/tai-khoan-phan-quyen")
        self.assertEqual(res.status_code, 302)
        self.assertIn("/tong-quan", res.headers.get("Location", ""))

        post_res = self.client.post(
            "/tai-khoan/them",
            data={
                "ten_dang_nhap": "rogue_admin",
                "mat_khau": "rogue123456",
                "ho_ten": "Rogue Admin",
                "khoa_vai_tro": "1",
                "pham_vi_loai": "TOAN_BO"
            }
        )
        self.assertEqual(post_res.status_code, 302)
        self.assertIn("/tong-quan", post_res.headers.get("Location", ""))

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT ma_tu_sinh FROM tai_khoan WHERE ten_dang_nhap = 'rogue_admin'")
        rogue_user = cur.fetchone()
        conn.close()
        self.assertIsNone(rogue_user)

    def test_adv_rbac_privilege_escalation_role_promotion_defense(self):
        self.login("admin", "admin123")
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT ma_tu_sinh FROM vai_tro WHERE ma_vai_tro = 'QUAN_TRI'")
        role_admin_id = cur.fetchone()[0]
        cur.execute("SELECT ma_tu_sinh FROM vai_tro WHERE ma_vai_tro = 'CHI_HUY'")
        role_commander_id = cur.fetchone()[0]
        conn.close()

        sub_admin_id = them_tai_khoan("officer_test", "password123", "Officer Test", role_commander_id, None, "TOAN_BO")
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT ma_tu_sinh FROM quyen_han WHERE ma_quyen = 'QUANTRI.TAIKHOAN'")
        qh_id = cur.fetchone()[0]
        cur.execute("INSERT INTO vai_tro_quyen (khoa_vai_tro, khoa_quyen) VALUES (?, ?)", (role_commander_id, qh_id))
        conn.commit()
        conn.close()

        self.logout()
        self.login("officer_test", "password123")

        esc_res = self.client.post(
            f"/tai-khoan/sua/{sub_admin_id}",
            data={
                "ho_ten": "Promoted Commander",
                "khoa_vai_tro": str(role_admin_id),
                "pham_vi_loai": "TOAN_BO",
                "dang_dung": "1"
            },
            follow_redirects=True
        )
        self.assertIn("không thể gán vai trò cao hơn cấp bậc".encode("utf-8"), esc_res.data)

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT khoa_vai_tro FROM tai_khoan_vai_tro WHERE khoa_tai_khoan = ?", (sub_admin_id,))
        actual_role_id = cur.fetchone()[0]
        conn.close()
        self.assertEqual(actual_role_id, role_commander_id)

    def test_adv_rbac_admin_immutability_enforced(self):
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT mat_khau_ma_hoa, ho_ten FROM tai_khoan WHERE ten_dang_nhap = 'admin'")
        orig_row = cur.fetchone()
        admin_orig_hash = orig_row[0]
        admin_orig_name = orig_row[1]
        conn.close()

        with self.assertRaises(PermissionError):
            xoa_tai_khoan(1)

        with self.assertRaises(PermissionError):
            sua_tai_khoan(1, "Hacked", "newpass123", nguoi_thuc_hien="attacker")

        self.login("vanbinh", "12345678")
        self.client.post("/tai-khoan/xoa/1", follow_redirects=True)
        self.client.post(
            "/tai-khoan/sua/1",
            data={
                "ho_ten": "Hacked Admin",
                "mat_khau_moi": "newpass123",
                "khoa_vai_tro": "1",
                "dang_dung": "0"
            },
            follow_redirects=True
        )

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT mat_khau_ma_hoa, ho_ten, dang_dung FROM tai_khoan WHERE ten_dang_nhap = 'admin'")
        admin_curr = cur.fetchone()
        conn.close()

        self.assertEqual(admin_curr[0], admin_orig_hash)
        self.assertEqual(admin_curr[1], admin_orig_name)
        self.assertEqual(admin_curr[2], 1)

    def test_adv_session_fixation_and_cookie_attributes(self):
        with self.client.session_transaction() as sess:
            sess["attacker_fixation_payload"] = "malicious_token"

        res = self.login("admin", "admin123")
        self.assertEqual(res.status_code, 200)

        with self.client.session_transaction() as sess:
            self.assertNotIn("attacker_fixation_payload", sess)
            self.assertIn("nguoi_dung", sess)
            self.assertEqual(sess["nguoi_dung"]["ten_dang_nhap"], "admin")

        self.assertTrue(self.app.config.get("SESSION_COOKIE_HTTPONLY"))
        self.assertEqual(self.app.config.get("SESSION_COOKIE_SAMESITE"), "Lax")

        self.logout()
        with self.client.session_transaction() as sess:
            self.assertNotIn("nguoi_dung", sess)

    def test_adv_scope_personnel_list_and_parameter_tampering(self):
        self.login("vanbinh", "12345678")

        res_normal = self.client.get("/quan-nhan")
        self.assertEqual(res_normal.status_code, 200)
        html_normal = res_normal.data.decode("utf-8")
        self.assertIn("QN001", html_normal)
        self.assertIn("QN002", html_normal)
        self.assertIn("QN007", html_normal)
        self.assertIn("QN009", html_normal)
        self.assertIn("QN011", html_normal)
        self.assertNotIn("QN003", html_normal)
        self.assertNotIn("QN004", html_normal)
        self.assertNotIn("QN005", html_normal)
        self.assertNotIn("QN006", html_normal)
        self.assertNotIn("QN008", html_normal)
        self.assertNotIn("QN010", html_normal)
        self.assertNotIn("QN012", html_normal)

        for tampered_param in ["TD2", "TD3", "HL", "C1", "2", "3", "4", "TAT_CA"]:
            res_tampered = self.client.get(f"/quan-nhan?don_vi={tampered_param}")
            self.assertEqual(res_tampered.status_code, 200)
            html_tampered = res_tampered.data.decode("utf-8")
            self.assertNotIn("QN003", html_tampered)
            self.assertNotIn("QN004", html_tampered)
            self.assertNotIn("QN005", html_tampered)
            self.assertNotIn("QN006", html_tampered)

    def test_adv_scope_personnel_direct_object_reference(self):
        self.login("vanbinh", "12345678")

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT ma_tu_sinh, ho_ten FROM quan_nhan WHERE ma_quan_nhan = 'QN003'")
        qn003_row = cur.fetchone()
        qn003_id = qn003_row[0]
        qn003_name = qn003_row[1]
        cur.execute("SELECT ma_tu_sinh FROM don_vi WHERE ma_don_vi = 'TD2'")
        td2_id = cur.fetchone()[0]
        conn.close()

        detail_res = self.client.get(f"/quan-nhan/chi-tiet/{qn003_id}", follow_redirects=True)
        self.assertNotIn(qn003_name.encode("utf-8"), detail_res.data)
        self.assertIn("không có quyền truy cập".encode("utf-8"), detail_res.data)

        edit_res = self.client.post(
            f"/quan-nhan/sua/{qn003_id}",
            data={
                "ho_ten": "Hacked Soldier Name",
                "khoa_cap_bac": "1",
                "khoa_chuc_vu": "7",
                "khoa_don_vi": str(td2_id)
            },
            follow_redirects=True
        )
        self.assertIn("không có thẩm quyền sửa quân nhân này".encode("utf-8"), edit_res.data)

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT ho_ten FROM quan_nhan WHERE ma_tu_sinh = ?", (qn003_id,))
        actual_name = cur.fetchone()[0]
        conn.close()
        self.assertEqual(actual_name, qn003_name)

        del_res = self.client.post(f"/quan-nhan/xoa/{qn003_id}", follow_redirects=True)
        self.assertIn("không có thẩm quyền xóa quân nhân này".encode("utf-8"), del_res.data)

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT da_xoa FROM quan_nhan WHERE ma_tu_sinh = ?", (qn003_id,))
        da_xoa_status = cur.fetchone()[0]
        conn.close()
        self.assertEqual(da_xoa_status, 0)

    def test_adv_scope_phones_and_cabinets_idors(self):
        self.login("vanbinh", "12345678")

        res_dt = self.client.get("/dien-thoai")
        html_dt = res_dt.data.decode("utf-8")
        self.assertIn("DT001", html_dt)
        self.assertIn("DT002", html_dt)
        self.assertNotIn("DT003", html_dt)
        self.assertNotIn("DT004", html_dt)

        res_dt_tamper = self.client.get("/dien-thoai?don_vi=TD2")
        html_dt_tamper = res_dt_tamper.data.decode("utf-8")
        self.assertNotIn("DT003", html_dt_tamper)

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT ma_tu_sinh FROM dien_thoai WHERE ma_thiet_bi = 'DT003'")
        dt003_id = cur.fetchone()[0]
        cur.execute("SELECT ma_tu_sinh FROM quan_nhan WHERE ma_quan_nhan = 'QN003'")
        qn003_id = cur.fetchone()[0]
        conn.close()

        dt_detail_res = self.client.get(f"/dien-thoai/chi-tiet/{dt003_id}", follow_redirects=True)
        self.assertNotIn("Reno8".encode("utf-8"), dt_detail_res.data)

        dt_edit_res = self.client.post(
            f"/dien-thoai/sua/{dt003_id}",
            data={
                "ten_dien_thoai": "Hacked Phone",
                "hang_san_xuat": "OPPO",
                "model": "Reno8",
                "khoa_quan_nhan": str(qn003_id)
            },
            follow_redirects=True
        )
        self.assertIn("không có thẩm quyền sửa thiết bị này".encode("utf-8"), dt_edit_res.data)

        res_tu = self.client.get("/tu-dien-thoai")
        html_tu = res_tu.data.decode("utf-8")
        self.assertIn("T01", html_tu)
        self.assertNotIn("T02", html_tu)
        self.assertNotIn("T03", html_tu)
        self.assertNotIn("T04", html_tu)

        for foreign_cabinet in ["T02", "T03", "T04"]:
            res_cabinet = self.client.get(f"/tu-dien-thoai/{foreign_cabinet}", follow_redirects=True)
            self.assertIn("không có thẩm quyền truy cập tủ của đơn vị khác".encode("utf-8"), res_cabinet.data)

    def test_adv_scope_delivery_operations_and_overdue_idors(self):
        self.login("vanbinh", "12345678")

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT ma_tu_sinh FROM quan_nhan WHERE ma_quan_nhan = 'QN003'")
        qn003_id = cur.fetchone()[0]
        cur.execute("SELECT ma_tu_sinh FROM quan_nhan WHERE ma_quan_nhan = 'QN004'")
        qn004_id = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM lich_su_giao_nhan WHERE khoa_quan_nhan = ?", (qn003_id,))
        init_history_qn003 = cur.fetchone()[0]
        conn.close()

        lay_res = self.client.post(
            "/giao-nhan/lay",
            data={
                "khoa_quan_nhan": str(qn003_id),
                "la_ngoai_le": "0"
            },
            follow_redirects=True
        )
        self.assertIn("không có thẩm quyền thao tác với quân nhân ngoài đơn vị".encode("utf-8"), lay_res.data)

        nop_res = self.client.post(
            "/giao-nhan/nop",
            data={
                "khoa_quan_nhan": str(qn004_id)
            },
            follow_redirects=True
        )
        self.assertIn("không có thẩm quyền thao tác với quân nhân ngoài đơn vị".encode("utf-8"), nop_res.data)

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM lich_su_giao_nhan WHERE khoa_quan_nhan = ?", (qn003_id,))
        after_history_qn003 = cur.fetchone()[0]
        conn.close()
        self.assertEqual(init_history_qn003, after_history_qn003)

        res_chua_nop = self.client.get("/chua-nop")
        html_chua_nop = res_chua_nop.data.decode("utf-8")
        self.assertIn("QN002", html_chua_nop)
        self.assertNotIn("QN004", html_chua_nop)
        self.assertNotIn("QN006", html_chua_nop)
        self.assertNotIn("QN012", html_chua_nop)

    def test_adv_password_hashing_salted_scrypt_and_randomness(self):
        id1 = them_tai_khoan("user_salt1", "MilitarySecret2026", "User Salt 1", 3, None, "TOAN_BO")
        id2 = them_tai_khoan("user_salt2", "MilitarySecret2026", "User Salt 2", 3, None, "TOAN_BO")

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT mat_khau_ma_hoa FROM tai_khoan WHERE ma_tu_sinh = ?", (id1,))
        hash1 = cur.fetchone()[0]
        cur.execute("SELECT mat_khau_ma_hoa FROM tai_khoan WHERE ma_tu_sinh = ?", (id2,))
        hash2 = cur.fetchone()[0]
        conn.close()

        self.assertTrue(hash1.startswith("scrypt:") or hash1.startswith("pbkdf2:"))
        self.assertTrue(hash2.startswith("scrypt:") or hash2.startswith("pbkdf2:"))
        self.assertNotEqual(hash1, hash2)
        self.assertTrue(xac_thuc_mat_khau("MilitarySecret2026", hash1))
        self.assertTrue(xac_thuc_mat_khau("MilitarySecret2026", hash2))
        self.assertFalse(xac_thuc_mat_khau("WrongPassword", hash1))

    def test_adv_password_lazy_migration_on_authentication(self):
        raw_pass = "LegacyPass2026"
        legacy_hash = hashlib.sha256(raw_pass.encode("utf-8")).hexdigest()
        self.assertEqual(len(legacy_hash), 64)

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO tai_khoan (ten_dang_nhap, mat_khau_ma_hoa, ho_ten, dang_dung)
            VALUES ('legacy_cadre', ?, 'Legacy Cadre', 1)
        """, (legacy_hash,))
        user_id = cur.lastrowid
        cur.execute("""
            INSERT INTO tai_khoan_vai_tro (khoa_tai_khoan, khoa_vai_tro, pham_vi_loai, hieu_luc_tu)
            VALUES (?, 3, 'TOAN_BO', '2026-01-01')
        """, (user_id,))
        conn.commit()
        conn.close()

        auth_user = xac_thuc_dang_nhap("legacy_cadre", raw_pass)
        self.assertIsNotNone(auth_user)
        self.assertEqual(auth_user["ten_dang_nhap"], "legacy_cadre")

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT mat_khau_ma_hoa FROM tai_khoan WHERE ma_tu_sinh = ?", (user_id,))
        migrated_hash = cur.fetchone()[0]
        conn.close()

        self.assertNotEqual(migrated_hash, legacy_hash)
        self.assertTrue(migrated_hash.startswith("scrypt:") or migrated_hash.startswith("pbkdf2:"))
        self.assertTrue(xac_thuc_mat_khau(raw_pass, migrated_hash))

    def test_adv_scope_add_personnel_overwrites_with_cadre_unit(self):
        self.login("vanbinh", "12345678")

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT ma_tu_sinh FROM don_vi WHERE ma_don_vi = 'TD1'")
        td1_id = cur.fetchone()[0]
        cur.execute("SELECT ma_tu_sinh FROM don_vi WHERE ma_don_vi = 'TD2'")
        td2_id = cur.fetchone()[0]
        conn.close()

        res = self.client.post(
            "/quan-nhan/them",
            data={
                "ma_quan_nhan": "QN_INJECT",
                "ho_ten": "Cross Unit Injected",
                "khoa_cap_bac": "1",
                "khoa_chuc_vu": "7",
                "khoa_don_vi": str(td2_id)
            },
            follow_redirects=True
        )
        self.assertEqual(res.status_code, 200)

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT khoa_don_vi FROM quan_nhan WHERE ma_quan_nhan = 'QN_INJECT'")
        row = cur.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], td1_id)
        self.assertNotEqual(row[0], td2_id)

    def test_adv_scope_add_phone_rejects_foreign_soldier(self):
        self.login("vanbinh", "12345678")

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT ma_tu_sinh FROM quan_nhan WHERE ma_quan_nhan = 'QN003'")
        foreign_qn_id = cur.fetchone()[0]
        conn.close()

        res = self.client.post(
            "/dien-thoai/them",
            data={
                "ma_thiet_bi": "DT_ILLEGAL",
                "ten_dien_thoai": "Illegal Phone",
                "hang_san_xuat": "Nokia",
                "model": "1280",
                "khoa_quan_nhan": str(foreign_qn_id)
            },
            follow_redirects=True
        )
        self.assertIn("không có quyền gán thiết bị cho quân nhân ngoài đơn vị".encode("utf-8"), res.data)

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT ma_tu_sinh FROM dien_thoai WHERE ma_thiet_bi = 'DT_ILLEGAL'")
        illegal_phone = cur.fetchone()
        conn.close()
        self.assertIsNone(illegal_phone)

    def test_adv_scope_reports_and_print_view_isolated_to_unit(self):
        self.login("vanbinh", "12345678")

        res_report = self.client.get("/bao-cao")
        html_report = res_report.data.decode("utf-8")
        self.assertIn("QN001", html_report)
        self.assertNotIn("QN003", html_report)
        self.assertNotIn("QN006", html_report)

        res_print = self.client.get("/bao-cao/in-a4")
        html_print = res_print.data.decode("utf-8")
        self.assertIn("Trung đội 1", html_print)
        self.assertNotIn("Trung đội 2", html_print)
        self.assertNotIn("Trung đội 3", html_print)

    def test_adv_rbac_account_hierarchy_filters_super_admin_for_subordinates(self):
        accounts_seen_by_commander = lay_tat_ca_tai_khoan(bac_nguoi_xem=80)
        usernames_seen = [tk["ten_dang_nhap"] for tk in accounts_seen_by_commander]
        self.assertNotIn("admin", usernames_seen)
        self.assertIn("levanson", usernames_seen)
        self.assertIn("vanbinh", usernames_seen)
        self.assertIn("tuananh", usernames_seen)

        accounts_seen_by_admin = lay_tat_ca_tai_khoan(bac_nguoi_xem=100)
        admin_usernames = [tk["ten_dang_nhap"] for tk in accounts_seen_by_admin]
        self.assertIn("admin", admin_usernames)

