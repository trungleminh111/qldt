import time
from tests.test_base import BaseTestCase

class Tier4MilitaryPersonasTestCase(BaseTestCase):

    def test_p1_01_duty_officer_rapid_search_under_5_seconds(self):
        self.login("tuananh", "12345678")

        start_time = time.time()
        res = self.client.get("/quan-nhan?tu_khoa=Nguyễn")
        duration = time.time() - start_time

        self.assertEqual(res.status_code, 200)
        self.assertLess(duration, 5.0)
        self.assertIn("Nguyễn Văn Hùng".encode("utf-8"), res.data)

        start_time_gn = time.time()
        res_gn = self.client.get("/giao-nhan?ma_qn=QN001")
        duration_gn = time.time() - start_time_gn

        self.assertEqual(res_gn.status_code, 200)
        self.assertLess(duration_gn, 5.0)

    def test_p1_02_duty_officer_complete_checkout_checkin_lifecycle(self):
        self.login("tuananh", "12345678")

        checkout_data = {
            "khoa_quan_nhan": "1",
            "la_ngoai_le": "1",
            "ly_do": "Trực ban bàn giao điện thoại sử dụng",
            "ghi_chu": "Bàn giao trong ca",
            "han_nop": "21:30"
        }
        res_out = self.client.post("/giao-nhan/lay", data=checkout_data, follow_redirects=True)
        self.assertEqual(res_out.status_code, 200)
        self.assertIn("thành công".encode("utf-8"), res_out.data)

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT loai FROM lich_su_giao_nhan WHERE khoa_quan_nhan = 1 ORDER BY ma_tu_sinh DESC LIMIT 1")
        self.assertEqual(cur.fetchone()[0], "LAY_RA")
        conn.close()

        checkin_data = {
            "khoa_quan_nhan": "1",
            "ghi_chu": "Trực ban thu hồi máy về tủ an toàn"
        }
        res_in = self.client.post("/giao-nhan/nop", data=checkin_data, follow_redirects=True)
        self.assertEqual(res_in.status_code, 200)
        self.assertIn("thành công".encode("utf-8"), res_in.data)

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT loai FROM lich_su_giao_nhan WHERE khoa_quan_nhan = 1 ORDER BY ma_tu_sinh DESC LIMIT 1")
        self.assertEqual(cur.fetchone()[0], "NOP_VAO")
        conn.close()

    def test_p1_03_duty_officer_unreturned_devices_list(self):
        self.login("tuananh", "12345678")
        res = self.client.get("/chua-nop")
        self.assertEqual(res.status_code, 200)
        page_html = res.data.decode("utf-8")
        has_warning = ("chưa nộp" in page_html.lower()) or ("danh sách" in page_html.lower())
        self.assertTrue(has_warning)

    def test_p2_01_platoon_officer_sees_only_own_platoon_personnel(self):
        self.login("vanbinh", "12345678")
        res = self.client.get("/quan-nhan")
        self.assertEqual(res.status_code, 200)

        self.assertIn("Nguyễn Văn Hùng".encode("utf-8"), res.data)
        self.assertNotIn("Lê Hoàng Nam".encode("utf-8"), res.data)
        self.assertNotIn("Phạm Quốc Bảo".encode("utf-8"), res.data)

    def test_p2_02_platoon_officer_24_compartment_locker_view(self):
        self.login("vanbinh", "12345678")
        res = self.client.get("/tu-dien-thoai/T01")
        self.assertEqual(res.status_code, 200)

        for i in range(1, 25):
            compartment_code = f"A{i:02d}"
            self.assertIn(compartment_code.encode("utf-8"), res.data)

    def test_p2_03_platoon_officer_blocked_from_other_platoon_cabinets(self):
        self.login("vanbinh", "12345678")
        res = self.client.get("/tu-dien-thoai/T02")
        if res.status_code == 200:
            self.assertNotIn("B01".encode("utf-8"), res.data)
        else:
            self.assertIn(res.status_code, [302, 403, 404])

    def test_p3_01_company_commander_dashboard_overdue_list(self):
        self.login("levanson", "12345678")
        res = self.client.get("/tong-quan")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Bảng điều khiển".encode("utf-8"), res.data)
        page_content = res.data.decode("utf-8")
        has_overdue_section = ("chưa nộp" in page_content.lower()) or ("quá hạn" in page_content.lower()) or ("vi phạm" in page_content.lower())
        self.assertTrue(has_overdue_section)

    def test_p3_02_company_commander_1click_a4_print_button_and_css(self):
        self.login("levanson", "12345678")
        res = self.client.get("/bao-cao/in-a4")
        self.assertEqual(res.status_code, 200)

        page_content = res.data.decode("utf-8")
        has_print_trigger = ("window.print" in page_content) or ("btn-in-ngay" in page_content) or ("btn-print" in page_content)
        has_print_css = ("@media print" in page_content) or ("no-print" in page_content)
        self.assertTrue(has_print_trigger)
        self.assertTrue(has_print_css)

    def test_p4_01_curious_soldier_blocked_from_account_management(self):
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT ma_tu_sinh FROM vai_tro WHERE ma_vai_tro = 'QUAN_NHAN'")
        vt_qn = cur.fetchone()[0]
        cur.execute("SELECT mat_khau_ma_hoa FROM tai_khoan WHERE ten_dang_nhap = 'tuananh'")
        pw_hash = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO tai_khoan (ten_dang_nhap, mat_khau_ma_hoa, ho_ten) VALUES ('chiensi_to_mo', ?, 'Chiến sĩ Tò Mò')",
            (pw_hash,)
        )
        new_tk_id = cur.lastrowid
        cur.execute(
            "INSERT INTO tai_khoan_vai_tro (khoa_tai_khoan, khoa_vai_tro, pham_vi_loai, hieu_luc_tu) VALUES (?, ?, 'TOAN_BO', datetime('now', 'localtime'))",
            (new_tk_id, vt_qn)
        )
        conn.commit()
        conn.close()

        self.login("chiensi_to_mo", "12345678")
        res = self.client.get("/tai-khoan-phan-quyen")
        if res.status_code == 302:
            self.assertIn("/tong-quan", res.headers.get("Location", ""))
        else:
            self.assertEqual(res.status_code, 403)

    def test_p4_02_curious_soldier_blocked_from_schedule_config(self):
        self.login("tuananh", "12345678")
        res = self.client.get("/cau-hinh-gio")
        if res.status_code == 302:
            self.assertIn("/tong-quan", res.headers.get("Location", ""))
        else:
            self.assertEqual(res.status_code, 403)

    def test_p4_03_curious_soldier_blocked_from_tampering_admin_password(self):
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT mat_khau_ma_hoa FROM tai_khoan WHERE ten_dang_nhap = 'admin'")
        orig_admin_hash = cur.fetchone()[0]
        conn.close()

        self.login("tuananh", "12345678")
        self.client.post(
            "/tai-khoan/sua/1",
            data={
                "ho_ten": "Hacked By Soldier",
                "mat_khau_moi": "new_unauthorized_pwd",
                "khoa_vai_tro": "1"
            },
            follow_redirects=True
        )

        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT mat_khau_ma_hoa, ho_ten FROM tai_khoan WHERE ten_dang_nhap = 'admin'")
        cur_admin = cur.fetchone()
        conn.close()

        self.assertEqual(cur_admin[0], orig_admin_hash)
        self.assertNotEqual(cur_admin[1], "Hacked By Soldier")
