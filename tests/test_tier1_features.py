import json
from tests.test_base import BaseTestCase

class Tier1FeaturesTestCase(BaseTestCase):

    def test_t1_01_login_successful_with_admin(self):
        res = self.login("admin", "admin123")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Bảng điều khiển".encode("utf-8"), res.data)

    def test_t1_02_login_fails_with_invalid_password(self):
        res = self.login("admin", "wrong_password_999")
        self.assertEqual(res.status_code, 200)
        self.assertIn("không chính xác".encode("utf-8"), res.data)

    def test_t1_03_login_fails_with_nonexistent_user(self):
        res = self.login("non_existent_soldier_xyz", "pass123")
        self.assertEqual(res.status_code, 200)
        self.assertIn("không chính xác".encode("utf-8"), res.data)

    def test_t1_04_logout_clears_session_and_redirects(self):
        self.login("admin", "admin123")
        res = self.logout()
        self.assertEqual(res.status_code, 200)
        self.assertIn("Đã đăng xuất".encode("utf-8"), res.data)
        protected_res = self.client.get("/tong-quan")
        self.assertEqual(protected_res.status_code, 302)

    def test_t1_05_already_logged_in_user_redirected_from_login_page(self):
        self.login("admin", "admin123")
        res = self.client.get("/dang-nhap")
        self.assertEqual(res.status_code, 302)
        self.assertIn("/tong-quan", res.headers.get("Location", ""))

    def test_t1_06_soldier_list_accessible(self):
        self.login("admin", "admin123")
        res = self.client.get("/quan-nhan")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Nguyễn Văn Hùng".encode("utf-8"), res.data)

    def test_t1_07_soldier_detail_view_accessible(self):
        self.login("admin", "admin123")
        res = self.client.get("/quan-nhan/chi-tiet/1")
        self.assertEqual(res.status_code, 200)
        self.assertIn("QN001".encode("utf-8"), res.data)

    def test_t1_08_soldier_create_success(self):
        self.login("admin", "admin123")
        post_data = {
            "ma_quan_nhan": "QN999",
            "ho_ten": "Vũ Văn Tân",
            "khoa_cap_bac": "1",
            "khoa_chuc_vu": "7",
            "khoa_don_vi": "2",
            "ngay_sinh": "2005-01-01",
            "ngay_nhap_ngu": "2026-02-15",
            "ghi_chu": "Tân binh mới"
        }
        res = self.client.post("/quan-nhan/them", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT ho_ten FROM quan_nhan WHERE ma_quan_nhan = 'QN999'")
        row = cur.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "Vũ Văn Tân")

    def test_t1_09_soldier_update_success(self):
        self.login("admin", "admin123")
        post_data = {
            "ho_ten": "Nguyễn Văn Hùng Đã Sửa",
            "khoa_cap_bac": "4",
            "khoa_chuc_vu": "5",
            "khoa_don_vi": "2",
            "ngay_sinh": "2001-08-12",
            "ngay_nhap_ngu": "2021-02-08",
            "ghi_chu": "Cập nhật hồ sơ"
        }
        res = self.client.post("/quan-nhan/sua/1", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT ho_ten FROM quan_nhan WHERE ma_tu_sinh = 1")
        row = cur.fetchone()
        conn.close()
        self.assertEqual(row[0], "Nguyễn Văn Hùng Đã Sửa")

    def test_t1_10_soldier_delete_success(self):
        self.login("admin", "admin123")
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO quan_nhan (ma_quan_nhan, ho_ten, khoa_cap_bac, khoa_chuc_vu, khoa_don_vi) VALUES ('QN998', 'Xóa Tôi Đi', 1, 7, 2)")
        new_id = cur.lastrowid
        conn.commit()
        conn.close()

        res = self.client.post(f"/quan-nhan/xoa/{new_id}", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT da_xoa FROM quan_nhan WHERE ma_tu_sinh = ?", (new_id,))
        da_xoa = cur.fetchone()[0]
        conn.close()
        self.assertEqual(da_xoa, 1)

    def test_t1_11_phone_list_accessible(self):
        self.login("admin", "admin123")
        res = self.client.get("/dien-thoai")
        self.assertEqual(res.status_code, 200)
        self.assertIn("iPhone 13".encode("utf-8"), res.data)

    def test_t1_12_phone_create_success(self):
        self.login("admin", "admin123")
        post_data = {
            "ma_thiet_bi": "DT999",
            "ten_dien_thoai": "Nokia 105",
            "hang_san_xuat": "Nokia",
            "model": "105 Dual Sim",
            "so_imei": "358999999999999",
            "so_dien_thoai": "0912999999",
            "khoa_quan_nhan": "1",
            "ma_ngan": ""
        }
        res = self.client.post("/dien-thoai/them", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT ten_dien_thoai FROM dien_thoai WHERE ma_thiet_bi = 'DT999'")
        row = cur.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "Nokia 105")

    def test_t1_13_phone_update_success(self):
        self.login("admin", "admin123")
        post_data = {
            "ten_dien_thoai": "iPhone 13 Pro Max",
            "hang_san_xuat": "Apple",
            "model": "iPhone 13 Pro Max 256GB",
            "so_imei": "356871102814829",
            "so_dien_thoai": "0981234561",
            "khoa_quan_nhan": "1",
            "ma_ngan": "T01-A01"
        }
        res = self.client.post("/dien-thoai/sua/1", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT ten_dien_thoai FROM dien_thoai WHERE ma_tu_sinh = 1")
        row = cur.fetchone()
        conn.close()
        self.assertEqual(row[0], "iPhone 13 Pro Max")

    def test_t1_14_cabinet_list_accessible(self):
        self.login("admin", "admin123")
        res = self.client.get("/tu-dien-thoai")
        self.assertEqual(res.status_code, 200)
        self.assertIn("T01".encode("utf-8"), res.data)
        self.assertIn("T02".encode("utf-8"), res.data)

    def test_t1_15_locker_24_compartment_view(self):
        self.login("admin", "admin123")
        res = self.client.get("/tu-dien-thoai/T01")
        self.assertEqual(res.status_code, 200)
        self.assertIn("A01".encode("utf-8"), res.data)
        self.assertIn("A24".encode("utf-8"), res.data)

    def test_t1_16_delivery_page_accessible(self):
        self.login("admin", "admin123")
        res = self.client.get("/giao-nhan")
        self.assertEqual(res.status_code, 200)
        self.assertIn("giao".encode("utf-8"), res.data.lower())

    def test_t1_17_api_check_hour_endpoint(self):
        self.login("admin", "admin123")
        res = self.client.get("/api/kiem-tra-gio?khoa_qn=1")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data.decode("utf-8"))
        self.assertIn("hop_le", data)
        self.assertIn("thong_bao", data)

    def test_t1_18_checkout_device_success(self):
        self.login("admin", "admin123")
        post_data = {
            "khoa_quan_nhan": "1",
            "ngay": "2026-10-30",
            "gio": "20:30",
            "la_ngoai_le": "1",
            "ly_do": "Mượn khẩn cấp liên lạc gia đình",
            "ghi_chu": "Kiểm thử tự động",
            "han_nop": "2026-10-30 21:30:00"
        }
        res = self.client.post("/giao-nhan/lay", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT loai FROM lich_su_giao_nhan WHERE khoa_quan_nhan = 1 ORDER BY ma_tu_sinh DESC LIMIT 1")
        row = cur.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "LAY_RA")

    def test_t1_19_checkin_device_success(self):
        self.login("admin", "admin123")
        post_data = {
            "khoa_quan_nhan": "2",
            "ghi_chu": "Nộp máy sau ca sử dụng"
        }
        res = self.client.post("/giao-nhan/nop", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT loai FROM lich_su_giao_nhan WHERE khoa_quan_nhan = 2 ORDER BY ma_tu_sinh DESC LIMIT 1")
        row = cur.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "NOP_VAO")

    def test_t1_20_unreturned_devices_list_accessible(self):
        self.login("admin", "admin123")
        res = self.client.get("/chua-nop")
        self.assertEqual(res.status_code, 200)
        self.assertIn("chưa nộp".encode("utf-8"), res.data.lower())

    def test_t1_21_shift_page_accessible(self):
        self.login("admin", "admin123")
        res = self.client.get("/ca-truc")
        self.assertEqual(res.status_code, 200)
        self.assertIn("bàn giao".encode("utf-8"), res.data.lower())

    def test_t1_22_shift_handover_submission_success(self):
        self.login("admin", "admin123")
        post_data = {
            "khoa_ca": "1",
            "khoa_nguoi_nhan": "2",
            "ghi_chu": "Bàn giao ca sáng đầy đủ quân số"
        }
        res = self.client.post("/ca-truc/xac-nhan", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("thành công".encode("utf-8"), res.data)

    def test_t1_23_general_report_page_accessible(self):
        self.login("admin", "admin123")
        res = self.client.get("/bao-cao")
        self.assertEqual(res.status_code, 200)
        self.assertIn("báo cáo".encode("utf-8"), res.data.lower())

    def test_t1_24_export_excel_report(self):
        self.login("admin", "admin123")
        res = self.client.get("/bao-cao/xuat-excel")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(res.data) > 1000)
        self.assertIn("spreadsheetml", res.headers.get("Content-Type", ""))

    def test_t1_25_a4_print_template_accessible(self):
        self.login("admin", "admin123")
        res = self.client.get("/bao-cao/in-a4")
        self.assertEqual(res.status_code, 200)
        self.assertIn("BÁO CÁO TỔNG HỢP".encode("utf-8"), res.data)
        self.assertIn("ĐẠI ĐỘI 1".encode("utf-8"), res.data)
