import json
from tests.test_base import BaseTestCase

class Tier2BoundariesTestCase(BaseTestCase):

    def test_b01_soldier_create_empty_required_fields_fails(self):
        self.login("admin", "admin123")
        post_data = {
            "ma_quan_nhan": "",
            "ho_ten": "",
            "khoa_cap_bac": "",
            "khoa_chuc_vu": "",
            "khoa_don_vi": ""
        }
        res = self.client.post("/quan-nhan/them", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("thông tin bắt buộc".encode("utf-8"), res.data)

    def test_b02_soldier_create_duplicate_code_handled(self):
        self.login("admin", "admin123")
        post_data = {
            "ma_quan_nhan": "QN001",
            "ho_ten": "Trùng Mã Quân Nhân",
            "khoa_cap_bac": "1",
            "khoa_chuc_vu": "7",
            "khoa_don_vi": "2"
        }
        res = self.client.post("/quan-nhan/them", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("đã tồn tại".encode("utf-8"), res.data)

    def test_b03_soldier_create_max_length_name(self):
        self.login("admin", "admin123")
        long_name = "Nguyễn " + ("A" * 200)
        post_data = {
            "ma_quan_nhan": "QN888",
            "ho_ten": long_name,
            "khoa_cap_bac": "1",
            "khoa_chuc_vu": "7",
            "khoa_don_vi": "2"
        }
        res = self.client.post("/quan-nhan/them", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT ho_ten FROM quan_nhan WHERE ma_quan_nhan = 'QN888'")
        row = cur.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], long_name)

    def test_b04_soldier_detail_nonexistent_id_handled(self):
        self.login("admin", "admin123")
        res = self.client.get("/quan-nhan/chi-tiet/999999", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Không tìm thấy quân nhân".encode("utf-8"), res.data)

    def test_b05_soldier_special_characters_handled(self):
        self.login("admin", "admin123")
        special_name = "<script>alert('test')</script> Nguyễn Văn O'Connor"
        post_data = {
            "ma_quan_nhan": "QN887",
            "ho_ten": special_name,
            "khoa_cap_bac": "1",
            "khoa_chuc_vu": "7",
            "khoa_don_vi": "2",
            "ghi_chu": "' OR 1=1 --"
        }
        res = self.client.post("/quan-nhan/them", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT ho_ten, ghi_chu FROM quan_nhan WHERE ma_quan_nhan = 'QN887'")
        row = cur.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], special_name)

    def test_b06_phone_create_empty_required_fields_fails(self):
        self.login("admin", "admin123")
        post_data = {
            "ma_thiet_bi": "",
            "ten_dien_thoai": "",
            "khoa_quan_nhan": ""
        }
        res = self.client.post("/dien-thoai/them", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("đầy đủ mã thiết bị".encode("utf-8"), res.data)

    def test_b07_phone_create_duplicate_imei_handled(self):
        self.login("admin", "admin123")
        post_data = {
            "ma_thiet_bi": "DT888",
            "ten_dien_thoai": "Trùng IMEI",
            "hang_san_xuat": "Apple",
            "model": "iPhone 13",
            "so_imei": "356871102814829",
            "khoa_quan_nhan": "1"
        }
        res = self.client.post("/dien-thoai/them", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("đã tồn tại".encode("utf-8"), res.data)

    def test_b08_phone_create_max_length_model(self):
        self.login("admin", "admin123")
        long_model = "M" * 200
        post_data = {
            "ma_thiet_bi": "DT887",
            "ten_dien_thoai": "Test Max Model",
            "hang_san_xuat": "Samsung",
            "model": long_model,
            "so_imei": "358123456789012",
            "khoa_quan_nhan": "1"
        }
        res = self.client.post("/dien-thoai/them", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT model FROM dien_thoai WHERE ma_thiet_bi = 'DT887'")
        row = cur.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], long_model)

    def test_b09_phone_detail_nonexistent_id_handled(self):
        self.login("admin", "admin123")
        res = self.client.get("/dien-thoai/chi-tiet/999999", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Không tìm thấy thiết bị".encode("utf-8"), res.data)

    def test_b10_phone_special_characters_handled(self):
        self.login("admin", "admin123")
        special_name = "Phone <b>bold</b> & special 'quote'"
        post_data = {
            "ma_thiet_bi": "DT886",
            "ten_dien_thoai": special_name,
            "hang_san_xuat": "Test",
            "model": "Pro",
            "so_imei": "358123456789013",
            "khoa_quan_nhan": "1"
        }
        res = self.client.post("/dien-thoai/them", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        conn = self.get_db()
        cur = conn.cursor()
        cur.execute("SELECT ten_dien_thoai FROM dien_thoai WHERE ma_thiet_bi = 'DT886'")
        row = cur.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], special_name)

    def test_b11_checkout_nonexistent_soldier_handled(self):
        self.login("admin", "admin123")
        post_data = {
            "khoa_quan_nhan": "999999",
            "la_ngoai_le": "1",
            "ly_do": "Khẩn cấp"
        }
        res = self.client.post("/giao-nhan/lay", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("chưa được gán thiết bị".encode("utf-8"), res.data)

    def test_b12_checkout_already_checked_out_phone_handled(self):
        self.login("admin", "admin123")
        post_data = {
            "khoa_quan_nhan": "2",
            "la_ngoai_le": "1",
            "ly_do": "Thử lấy lần 2"
        }
        res = self.client.post("/giao-nhan/lay", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("ĐÃ LẤY".encode("utf-8"), res.data)

    def test_b13_checkin_already_in_cabinet_phone_handled(self):
        self.login("admin", "admin123")
        post_data = {
            "khoa_quan_nhan": "1",
            "ghi_chu": "Thử nộp máy đang ở trong tủ"
        }
        res = self.client.post("/giao-nhan/nop", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("đã có trong tủ".encode("utf-8"), res.data)

    def test_b14_delivery_invalid_datetime_format_handled(self):
        self.login("admin", "admin123")
        post_data = {
            "khoa_quan_nhan": "1",
            "ngay": "invalid-date",
            "gio": "invalid-time",
            "la_ngoai_le": "1",
            "ly_do": "Kiểm tra định dạng lỗi"
        }
        res = self.client.post("/giao-nhan/lay", data=post_data, follow_redirects=True)
        self.assertIn(res.status_code, [200, 302])

    def test_b15_api_check_hour_empty_soldier_id(self):
        self.login("admin", "admin123")
        res = self.client.get("/api/kiem-tra-gio")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data.decode("utf-8"))
        self.assertFalse(data.get("hop_le", True))

    def test_b16_schedule_start_time_after_end_time_rejected(self):
        self.login("admin", "admin123")
        post_data = {
            "khoa_cau_hinh_gio": "1",
            "thu_trong_tuan": "2",
            "gio_bat_dau": "21:00",
            "gio_ket_thuc": "20:00",
            "ghi_chu": "Giờ ngược"
        }
        res = self.client.post("/cau-hinh-gio/them", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Khung giờ không hợp lệ".encode("utf-8"), res.data)

    def test_b17_schedule_empty_times_rejected(self):
        self.login("admin", "admin123")
        post_data = {
            "khoa_cau_hinh_gio": "1",
            "thu_trong_tuan": "2",
            "gio_bat_dau": "",
            "gio_ket_thuc": "",
            "ghi_chu": ""
        }
        res = self.client.post("/cau-hinh-gio/them", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Khung giờ không hợp lệ".encode("utf-8"), res.data)

    def test_b18_special_day_empty_reason_rejected(self):
        self.login("admin", "admin123")
        post_data = {
            "ngay": "2026-11-01",
            "ly_do": "",
            "cam_su_dung": "0"
        }
        res = self.client.post("/ngay-dac-biet/them", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Vui lòng nhập ngày và lý do".encode("utf-8"), res.data)

    def test_b19_shift_handover_missing_receiver_rejected(self):
        self.login("admin", "admin123")
        post_data = {
            "khoa_ca": "1",
            "khoa_nguoi_nhan": "",
            "ghi_chu": ""
        }
        res = self.client.post("/ca-truc/xac-nhan", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Vui lòng chọn ca trực".encode("utf-8"), res.data)

    def test_b20_shift_handover_missing_shift_rejected(self):
        self.login("admin", "admin123")
        post_data = {
            "khoa_ca": "",
            "khoa_nguoi_nhan": "2",
            "ghi_chu": ""
        }
        res = self.client.post("/ca-truc/xac-nhan", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Vui lòng chọn ca trực".encode("utf-8"), res.data)

    def test_b21_login_empty_credentials_rejected(self):
        res = self.login("", "")
        self.assertEqual(res.status_code, 200)
        self.assertIn("không chính xác".encode("utf-8"), res.data)

    def test_b22_login_whitespace_only_credentials_rejected(self):
        res = self.login("   ", "   ")
        self.assertEqual(res.status_code, 200)
        self.assertIn("không chính xác".encode("utf-8"), res.data)

    def test_b23_account_create_empty_username_rejected(self):
        self.login("admin", "admin123")
        post_data = {
            "ten_dang_nhap": "",
            "mat_khau": "12345678",
            "ho_ten": "Kiểm Tra Rỗng",
            "khoa_vai_tro": "1"
        }
        res = self.client.post("/tai-khoan/them", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("bắt buộc".encode("utf-8"), res.data)

    def test_b24_account_create_empty_password_rejected(self):
        self.login("admin", "admin123")
        post_data = {
            "ten_dang_nhap": "newuser",
            "mat_khau": "",
            "ho_ten": "Kiểm Tra Mật Khẩu",
            "khoa_vai_tro": "1"
        }
        res = self.client.post("/tai-khoan/them", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("bắt buộc".encode("utf-8"), res.data)

    def test_b25_account_create_duplicate_username_handled(self):
        self.login("admin", "admin123")
        post_data = {
            "ten_dang_nhap": "admin",
            "mat_khau": "newpass123",
            "ho_ten": "Trùng Admin",
            "khoa_vai_tro": "1"
        }
        res = self.client.post("/tai-khoan/them", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("đã tồn tại".encode("utf-8"), res.data)
