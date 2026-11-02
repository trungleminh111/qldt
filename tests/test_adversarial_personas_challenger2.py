import time
from tests.test_base import BaseTestCase

class AdversarialPersonasChallenger2TestCase(BaseTestCase):

    def test_p1_stress_large_roster_search_under_5s(self):
        self.login("tuananh", "12345678")
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT ma_tu_sinh FROM don_vi WHERE ma_don_vi = 'TD1'")
        dv1_id = cur.fetchone()[0]
        cur.execute("SELECT ma_tu_sinh FROM don_vi WHERE ma_don_vi = 'TD2'")
        dv2_id = cur.fetchone()[0]
        cur.execute("SELECT ma_tu_sinh FROM cap_bac WHERE ma_cap_bac = 'B2'")
        cb_id = cur.fetchone()[0]
        cur.execute("SELECT ma_tu_sinh FROM chuc_vu WHERE ma_chuc_vu = 'CHIEN_SI'")
        cv_id = cur.fetchone()[0]

        batch_soldiers = []
        for i in range(100, 400):
            batch_soldiers.append((
                f"STRESS{i:03d}",
                f"Chiến sĩ Thử nghiệm {i}",
                cb_id,
                cv_id,
                dv1_id if i % 2 == 0 else dv2_id
            ))
        cur.executemany(
            "INSERT INTO quan_nhan (ma_quan_nhan, ho_ten, khoa_cap_bac, khoa_chuc_vu, khoa_don_vi) VALUES (?, ?, ?, ?, ?)",
            batch_soldiers
        )
        conn.commit()
        conn.close()

        t_start = time.time()
        res = self.client.get("/giao-nhan")
        duration = time.time() - t_start

        self.assertEqual(res.status_code, 200)
        self.assertLess(duration, 5.0)

        html = res.data.decode("utf-8")
        self.assertIn("STRESS100", html)
        self.assertIn("STRESS399", html)
        self.assertIn("btn-loc-don-vi", html)
        self.assertIn("oTimKiemNhanh", html)
        self.assertIn("locTheoDonVi", html)
        self.assertIn("locDanhSachQuanNhan", html)

    def test_p1_shift_handover_unreturned_warning_and_modal(self):
        self.login("tuananh", "12345678")

        checkout_data = {
            "khoa_quan_nhan": "1",
            "la_ngoai_le": "1",
            "ly_do": "Kiểm thử cảnh báo bàn giao",
            "ghi_chu": "Lấy máy phục vụ kiểm thử",
            "han_nop": "21:30"
        }
        self.client.post("/giao-nhan/lay", data=checkout_data, follow_redirects=True)

        res_warning = self.client.get("/ca-truc")
        self.assertEqual(res_warning.status_code, 200)
        html_warning = res_warning.data.decode("utf-8")

        self.assertIn("canhBaoChuaNop", html_warning)
        self.assertIn("modalCanhBaoBanGiao", html_warning)
        self.assertIn("kiemTraXacNhanBanGiao", html_warning)
        self.assertIn("xacNhanGuiFormBanGiao", html_warning)
        self.assertIn("tbodyChuaNopTrucBan", html_warning)

        res_chuanop = self.client.get("/chua-nop")
        self.assertEqual(res_chuanop.status_code, 200)

        res_dash = self.client.get("/tong-quan")
        self.assertEqual(res_dash.status_code, 200)
        self.assertIn("Quân nhân chưa nộp điện thoại / Quá hạn".encode("utf-8"), res_dash.data)

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT dt.ma_tu_sinh, dt.khoa_quan_nhan
            FROM dien_thoai dt
            INNER JOIN (
                SELECT gn1.khoa_dien_thoai, gn1.loai
                FROM lich_su_giao_nhan gn1
                INNER JOIN (
                    SELECT khoa_dien_thoai, MAX(ma_tu_sinh) AS max_id
                    FROM lich_su_giao_nhan
                    GROUP BY khoa_dien_thoai
                ) gn2 ON gn1.ma_tu_sinh = gn2.max_id
            ) gn ON gn.khoa_dien_thoai = dt.ma_tu_sinh
            WHERE gn.loai = 'LAY_RA'
        """)
        active_loans = cur.fetchall()
        for dt_id, qn_id in active_loans:
            cur.execute(
                "INSERT INTO lich_su_giao_nhan (khoa_quan_nhan, khoa_dien_thoai, thoi_gian, loai, ket_qua, khoa_nguoi_thuc_hien, ten_nguoi_thuc_hien, ghi_chu) VALUES (?, ?, datetime('now', 'localtime'), 'NOP_VAO', 'DUNG_GIO', 1, 'Trực ban', 'Thu hồi')",
                (qn_id, dt_id)
            )
        conn.commit()
        conn.close()

        res_clean = self.client.get("/ca-truc")
        self.assertEqual(res_clean.status_code, 200)
        html_clean = res_clean.data.decode("utf-8")
        self.assertNotIn("canhBaoChuaNop", html_clean)

    def test_p2_platoon_locker_24_compartments_and_isolation(self):
        self.login("vanbinh", "12345678")
        res_t01 = self.client.get("/tu-dien-thoai/T01")
        self.assertEqual(res_t01.status_code, 200)
        html_t01 = res_t01.data.decode("utf-8")

        for i in range(1, 25):
            comp_code = f"A{i:02d}"
            self.assertIn(comp_code, html_t01)

        self.assertNotIn("B01", html_t01)
        self.assertNotIn("C01", html_t01)

        res_t02 = self.client.get("/tu-dien-thoai/T02")
        self.assertEqual(res_t02.status_code, 302)
        self.assertIn("/tu-dien-thoai", res_t02.headers.get("Location", ""))

        res_t03 = self.client.get("/tu-dien-thoai/T03")
        self.assertEqual(res_t03.status_code, 302)
        self.assertIn("/tu-dien-thoai", res_t03.headers.get("Location", ""))

    def test_p2_platoon_tamper_soldier_and_phone_blocked(self):
        self.login("vanbinh", "12345678")

        res_view_other_qn = self.client.get("/quan-nhan/chi-tiet/3")
        self.assertEqual(res_view_other_qn.status_code, 302)
        self.assertIn("/quan-nhan", res_view_other_qn.headers.get("Location", ""))

        res_edit_other_qn = self.client.post("/quan-nhan/sua/3", data={"ho_ten": "Hacked Soldier", "khoa_cap_bac": "1", "khoa_chuc_vu": "1", "khoa_don_vi": "2"})
        self.assertEqual(res_edit_other_qn.status_code, 302)

        res_view_other_dt = self.client.get("/dien-thoai/chi-tiet/3")
        self.assertEqual(res_view_other_dt.status_code, 302)
        self.assertIn("/dien-thoai", res_view_other_dt.headers.get("Location", ""))

        res_add_other_dt = self.client.post("/dien-thoai/them", data={
            "ma_thiet_bi": "HACK_TB_99",
            "ten_dien_thoai": "Tampered Phone",
            "khoa_quan_nhan": "3"
        })
        self.assertEqual(res_add_other_dt.status_code, 302)

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT ma_thiet_bi FROM dien_thoai WHERE ma_thiet_bi = 'HACK_TB_99'")
        self.assertIsNone(cur.fetchone())
        conn.close()

    def test_p3_company_commander_dashboard_overdue_and_1click_a4_print(self):
        self.login("levanson", "12345678")

        res_dash = self.client.get("/tong-quan")
        self.assertEqual(res_dash.status_code, 200)
        html_dash = res_dash.data.decode("utf-8")
        self.assertIn("Quân nhân chưa nộp điện thoại / Quá hạn", html_dash)
        self.assertIn("Thu hồi", html_dash)

        res_print = self.client.get("/bao-cao/in-a4")
        self.assertEqual(res_print.status_code, 200)
        html_print = res_print.data.decode("utf-8")

        self.assertIn("btn-in-ngay", html_print)
        self.assertIn("window.print()", html_print)
        self.assertIn("btn-quay-lai", html_print)
        self.assertIn("history.back()", html_print)
        self.assertIn(".no-print { display: none !important; }", html_print)
        self.assertIn("@page { size: A4;", html_print)

    def test_p4_curious_soldier_unauthorized_routes_and_safe_redirect(self):
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT ma_tu_sinh FROM vai_tro WHERE ma_vai_tro = 'QUAN_NHAN'")
        vt_qn = cur.fetchone()[0]
        cur.execute("SELECT mat_khau_ma_hoa FROM tai_khoan WHERE ten_dang_nhap = 'tuananh'")
        pw_hash = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO tai_khoan (ten_dang_nhap, mat_khau_ma_hoa, ho_ten) VALUES ('chiensi_to_mo_2', ?, 'Chiến sĩ Tò Mò 2')",
            (pw_hash,)
        )
        new_tk_id = cur.lastrowid
        cur.execute(
            "INSERT INTO tai_khoan_vai_tro (khoa_tai_khoan, khoa_vai_tro, pham_vi_loai, hieu_luc_tu) VALUES (?, ?, 'TOAN_BO', datetime('now', 'localtime'))",
            (new_tk_id, vt_qn)
        )
        conn.commit()
        conn.close()

        self.login("chiensi_to_mo_2", "12345678")

        forbidden_get_routes = [
            "/tai-khoan-phan-quyen",
            "/cau-hinh-gio",
        ]
        for route in forbidden_get_routes:
            res = self.client.get(route)
            self.assertIn(res.status_code, [302, 403])
            if res.status_code == 302:
                self.assertIn("/tong-quan", res.headers.get("Location", ""))

        forbidden_post_routes = [
            ("/tai-khoan/them", {"ten_dang_nhap": "fake_admin", "mat_khau": "123", "ho_ten": "Fake", "khoa_vai_tro": "1"}),
            ("/tai-khoan/sua/1", {"ho_ten": "Hacked Admin", "mat_khau_moi": "hacked123", "khoa_vai_tro": "1"}),
            ("/tai-khoan/xoa/1", {}),
            ("/cau-hinh-gio/them", {"khoa_cau_hinh_gio": "1", "thu_trong_tuan": "2", "gio_bat_dau": "10:00", "gio_ket_thuc": "11:00"}),
            ("/ngay-dac-biet/them", {"ngay": "2026-12-25", "ly_do": "Noel"}),
            ("/vai-tro/cap-nhat-quyen/1", {"quyen_ids": ["1", "2"]})
        ]
        for route, data in forbidden_post_routes:
            res = self.client.post(route, data=data)
            self.assertIn(res.status_code, [302, 403])
            if res.status_code == 302:
                self.assertIn("/tong-quan", res.headers.get("Location", ""))

    def test_p4_erratic_inputs_and_tampering_resilience(self):
        self.login("admin", "admin123")

        res_neg = self.client.get("/quan-nhan/chi-tiet/-1")
        self.assertIn(res_neg.status_code, [302, 404])

        res_nonexistent = self.client.get("/quan-nhan/chi-tiet/999999")
        self.assertIn(res_nonexistent.status_code, [302, 404])

        res_sqli = self.client.get("/quan-nhan?tu_khoa=' OR '1'='1")
        self.assertEqual(res_sqli.status_code, 200)

        res_xss = self.client.get("/quan-nhan?tu_khoa=<script>alert(1)</script>")
        self.assertEqual(res_xss.status_code, 200)
        self.assertNotIn(b"<script>alert(1)</script>", res_xss.data)

        res_del_admin = self.client.post("/tai-khoan/xoa/1", follow_redirects=True)
        self.assertEqual(res_del_admin.status_code, 200)

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT dang_dung FROM tai_khoan WHERE ten_dang_nhap = 'admin'")
        admin_row = cur.fetchone()
        self.assertIsNotNone(admin_row)
        self.assertEqual(admin_row[0], 1)
        conn.close()
