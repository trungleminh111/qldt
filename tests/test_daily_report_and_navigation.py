from datetime import datetime
from io import BytesIO
import openpyxl
from tests.test_base import BaseTestCase
from models.bao_cao_model import lay_bao_cao_dang_ky_trong_ngay
from models.giao_nhan_model import thuc_hien_lay_dien_thoai, thuc_hien_nop_dien_thoai

class KiemThuBaoCaoNgayVaDieuHuong(BaseTestCase):
    def test_bao_cao_dang_ky_trong_ngay_logic(self):
        ngay_hom_nay = datetime.now().strftime("%Y-%m-%d")
        bc = lay_bao_cao_dang_ky_trong_ngay(ngay=ngay_hom_nay)
        self.assertIn("danh_sach", bc)
        self.assertIn("tong_so", bc)
        self.assertIn("so_da_nop", bc)
        self.assertIn("so_dang_su_dung", bc)
        self.assertIn("so_ngoai_le", bc)

        thuc_hien_lay_dien_thoai(
            khoa_quan_nhan=1,
            khoa_nguoi_thuc_hien=1,
            ten_nguoi_thuc_hien="Trực ban",
            thoi_gian=f"{ngay_hom_nay} 18:00:00",
            la_ngoai_le=True,
            ly_do="Gia đình có việc gấp",
            han_nop="20:00"
        )

        bc_sau_lay = lay_bao_cao_dang_ky_trong_ngay(ngay=ngay_hom_nay)
        self.assertGreaterEqual(bc_sau_lay["tong_so"], 1)
        self.assertGreaterEqual(bc_sau_lay["so_dang_su_dung"], 1)
        self.assertGreaterEqual(bc_sau_lay["so_ngoai_le"], 1)

        thuc_hien_nop_dien_thoai(
            khoa_quan_nhan=1,
            khoa_nguoi_thuc_hien=1,
            ten_nguoi_thuc_hien="Trực ban",
            thoi_gian=f"{ngay_hom_nay} 19:30:00"
        )

        bc_sau_nop = lay_bao_cao_dang_ky_trong_ngay(ngay=ngay_hom_nay)
        self.assertGreaterEqual(bc_sau_nop["so_da_nop"], 1)

    def test_trang_bao_cao_va_in_a4_mau_2(self):
        with self.client:
            self.login("admin", "admin123")
            res = self.client.get("/bao-cao")
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
            self.assertNotIn("BÁO CÁO TỔNG HỢP ĐĂNG KÝ SỬ DỤNG ĐIỆN THOẠI TRONG NGÀY", html)
            self.assertIn("/bao-cao/in-a4", html)
            self.assertIn("Xuất báo cáo", html)

            res_in_a4 = self.client.get("/bao-cao/in-a4")
            self.assertEqual(res_in_a4.status_code, 200)
            html_a4 = res_in_a4.get_data(as_text=True)
            self.assertIn("TIỂU ĐOÀN 3", html_a4)
            self.assertIn("ĐẠI ĐỘI 11", html_a4)
            self.assertIn("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM", html_a4)
            self.assertIn("Độc lập – Tự do – Hạnh phúc", html_a4)
            self.assertIn("Quy định số 763/QyĐ-SĐ", html_a4)
            self.assertIn("I. Số liệu tổng hợp toàn đại đội", html_a4)
            self.assertIn("II. Thống kê chi tiết theo đơn vị trực thuộc", html_a4)
            self.assertIn("Ban Chỉ huy Đại đội 11 báo cáo Ban Chỉ huy Tiểu đoàn theo dõi, tổng hợp./.", html_a4)
            self.assertIn("CHỈ HUY ĐẠI ĐỘI", html_a4)
            self.assertIn("Nơi nhận:", html_a4)
            self.assertIn("Đà Nẵng", html_a4)
            self.assertNotIn("Hà Nội", html_a4)
            self.assertIn("border-top: 1.5px solid #000000", html_a4)

            res_in = self.client.get("/bao-cao/in-ngay")
            self.assertEqual(res_in.status_code, 200)
            html_in = res_in.get_data(as_text=True)
            self.assertIn("Đà Nẵng", html_in)
            self.assertNotIn("Hà Nội", html_in)
            self.assertIn("border-top: 1.5px solid #000000", html_in)

            res_excel = self.client.get("/bao-cao/xuat-excel-ngay")
            self.assertEqual(res_excel.status_code, 200)
            self.assertEqual(res_excel.mimetype, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            wb = openpyxl.load_workbook(BytesIO(res_excel.data))
            self.assertIn("BaoCaoNgay", wb.sheetnames)

    def test_trang_da_lay_su_dung_chuyen_huong_chua_nop(self):
        with self.client:
            self.login("admin", "admin123")
            res = self.client.get("/da-lay", follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Danh sách điện thoại chưa nộp", res.get_data(as_text=True))

            res_alias = self.client.get("/da-lay-su-dung", follow_redirects=True)
            self.assertEqual(res_alias.status_code, 200)
            self.assertIn("Danh sách điện thoại chưa nộp", res_alias.get_data(as_text=True))

    def test_dieu_huong_the_thong_ke_va_loai_bo_ban_giao_ca(self):
        with self.client:
            self.login("admin", "admin123")
            res = self.client.get("/")
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)

            self.assertIn('href="/dien-thoai"', html)
            self.assertIn('href="/tu-dien-thoai"', html)
            self.assertIn('href="/chua-nop"', html)

            self.assertNotIn('⇋ Bàn giao ca', html)
            self.assertNotIn('href="/ca-truc/ban-giao"', html)
            self.assertNotIn('Đã lấy sử dụng</a>', html)
