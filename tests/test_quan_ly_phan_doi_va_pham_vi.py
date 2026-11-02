import os
import tempfile
import unittest
import config
from app import tao_ung_dung
from models.co_so_du_lieu import khoi_tao_co_so_du_lieu, lay_ket_noi
from models.du_lieu_mau import nap_du_lieu_mau
from models.quan_nhan_model import (
    lay_tat_ca_don_vi,
    lay_chi_tiet_don_vi,
    them_don_vi,
    sua_don_vi,
    xoa_don_vi,
    lay_tat_ca_quan_nhan
)
from models.phan_quyen_model import (
    them_tai_khoan,
    sua_tai_khoan,
    xoa_tai_khoan,
    lay_tat_ca_tai_khoan,
    lay_chi_tiet_tai_khoan,
    xac_thuc_dang_nhap
)
from models.dien_thoai_model import lay_tat_ca_dien_thoai, lay_danh_sach_tu
from models.giao_nhan_model import thuc_hien_lay_dien_thoai

class TestQuanLyPhanDoiVaPhamVi(unittest.TestCase):
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

    def dang_nhap_admin(self):
        return self.client.post("/dang-nhap", data={
            "ten_dang_nhap": "admin",
            "mat_khau": "admin123"
        }, follow_redirects=True)

    def test_danh_sach_phan_doi_view(self):
        self.dang_nhap_admin()
        res = self.client.get("/phan-doi")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Quản lý danh mục phân đội".encode("utf-8"), res.data)
        self.assertIn("Trung đội 1".encode("utf-8"), res.data)
        self.assertIn("Trung đội 2".encode("utf-8"), res.data)

    def test_them_phan_doi_moi_va_sua(self):
        self.dang_nhap_admin()
        res_them = self.client.post("/phan-doi/them", data={
            "ma_don_vi": "B4",
            "ten_don_vi": "Trung đội 4",
            "thu_tu": "5"
        }, follow_redirects=True)
        self.assertEqual(res_them.status_code, 200)

        all_dv = lay_tat_ca_don_vi()
        b4 = next((d for d in all_dv if d["ma_don_vi"] == "B4"), None)
        self.assertIsNotNone(b4)
        self.assertEqual(b4["ten_don_vi"], "Trung đội 4")
        self.assertEqual(b4["so_quan_nhan"], 0)
        self.assertEqual(b4["so_tu"], 0)

        res_sua = self.client.post(f"/phan-doi/sua/{b4['ma_tu_sinh']}", data={
            "ma_don_vi": "B4",
            "ten_don_vi": "Trung đội 4 Cơ động",
            "thu_tu": "6",
            "dang_dung": "1"
        }, follow_redirects=True)
        self.assertEqual(res_sua.status_code, 200)

        b4_updated = lay_chi_tiet_don_vi(b4["ma_tu_sinh"])
        self.assertEqual(b4_updated["ten_don_vi"], "Trung đội 4 Cơ động")

        res_xoa = self.client.post(f"/phan-doi/xoa/{b4['ma_tu_sinh']}", follow_redirects=True)
        self.assertEqual(res_xoa.status_code, 200)
        b4_after_delete = lay_chi_tiet_don_vi(b4["ma_tu_sinh"])
        self.assertIsNone(b4_after_delete)

    def test_xoa_phan_doi_co_quan_nhan_bi_chan(self):
        self.dang_nhap_admin()
        res = self.client.post("/phan-doi/xoa/2", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        b1 = lay_chi_tiet_don_vi(2)
        self.assertIsNotNone(b1)
        self.assertIn("Không thể xóa".encode("utf-8"), res.data)

    def test_them_tai_khoan_pham_vi_nhieu_trung_doi(self):
        self.dang_nhap_admin()
        res_them = self.client.post("/tai-khoan/them", data={
            "ten_dang_nhap": "canbo_b1_b2",
            "mat_khau": "12345678",
            "ho_ten": "Nguyễn Văn Đa Đội",
            "khoa_vai_tro": "2",
            "pham_vi_loai": "DON_VI",
            "pham_vi_khoa_don_vi": ["2", "3"]
        }, follow_redirects=True)
        self.assertEqual(res_them.status_code, 200)

        ds_tk = lay_tat_ca_tai_khoan()
        tk_new = next((t for t in ds_tk if t["ten_dang_nhap"] == "canbo_b1_b2"), None)
        self.assertIsNotNone(tk_new)
        self.assertEqual(str(tk_new["pham_vi_khoa"]), "2,3")
        self.assertIn("Trung đội 1", tk_new["ten_don_vi_pham_vi"])
        self.assertIn("Trung đội 2", tk_new["ten_don_vi_pham_vi"])

        user_auth = xac_thuc_dang_nhap("canbo_b1_b2", "12345678")
        self.assertIsNotNone(user_auth)
        self.assertEqual(user_auth["pham_vi_loai"], "DON_VI")
        self.assertEqual(user_auth["khoa_don_vi"], "2,3")

        self.client.get("/dang-xuat", follow_redirects=True)
        self.client.post("/dang-nhap", data={
            "ten_dang_nhap": "canbo_b1_b2",
            "mat_khau": "12345678"
        }, follow_redirects=True)

        res_giao_nhan = self.client.get("/giao-nhan")
        self.assertEqual(res_giao_nhan.status_code, 200)

        res_dt = self.client.get("/dien-thoai")
        self.assertEqual(res_dt.status_code, 200)
        self.assertNotIn("Trung đội 3".encode("utf-8"), res_dt.data)

    def test_data_isolation_multi_unit_scope(self):
        phones_all = lay_tat_ca_dien_thoai()
        phones_b1_b2 = lay_tat_ca_dien_thoai(khoa_don_vi_gioi_han=[2, 3])
        self.assertGreater(len(phones_all), len(phones_b1_b2))
        for dt in phones_b1_b2:
            self.assertIn(dt["ten_don_vi"], ["Trung đội 1", "Trung đội 2"])

        soldiers_b1_b2 = lay_tat_ca_quan_nhan(khoa_don_vi_gioi_han=[2, 3])
        for qn in soldiers_b1_b2:
            self.assertIn(qn["ten_don_vi"], ["Trung đội 1", "Trung đội 2"])

        qn_b3 = next((q for q in lay_tat_ca_quan_nhan() if q["khoa_don_vi"] == 4), None)
        self.assertIsNotNone(qn_b3)
        ok, msg = thuc_hien_lay_dien_thoai(
            khoa_quan_nhan=qn_b3["ma_tu_sinh"],
            khoa_nguoi_thuc_hien=1,
            ten_nguoi_thuc_hien="Quản trị",
            khoa_don_vi_gioi_han=[2, 3]
        )
        self.assertFalse(ok)
        self.assertIn("không thuộc đơn vị quản lý", msg)

    def test_sua_tai_khoan_doi_pham_vi_trung_doi(self):
        self.dang_nhap_admin()
        ds_tk = lay_tat_ca_tai_khoan()
        tk_vanbinh = next((t for t in ds_tk if t["ten_dang_nhap"] == "vanbinh"), None)
        self.assertIsNotNone(tk_vanbinh)

        res_sua = self.client.post(f"/tai-khoan/sua/{tk_vanbinh['ma_tu_sinh']}", data={
            "ho_ten": "Trần Văn Bình",
            "khoa_vai_tro": str(tk_vanbinh["khoa_vai_tro"]),
            "dang_dung": "1",
            "pham_vi_loai": "DON_VI",
            "pham_vi_khoa_don_vi": ["3", "4"]
        }, follow_redirects=True)
        self.assertEqual(res_sua.status_code, 200)

        tk_updated = lay_chi_tiet_tai_khoan(tk_vanbinh["ma_tu_sinh"])
        self.assertEqual(str(tk_updated["pham_vi_khoa"]), "3,4")

if __name__ == "__main__":
    unittest.main()
