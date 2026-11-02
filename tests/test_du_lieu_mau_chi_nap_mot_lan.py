import os
import tempfile
import unittest
import config
from app import tao_ung_dung
from models.co_so_du_lieu import khoi_tao_co_so_du_lieu, lay_ket_noi, kiem_tra_da_co_du_lieu
from models.du_lieu_mau import nap_du_lieu_mau
from models.phan_quyen_model import them_tai_khoan, xoa_tai_khoan, lay_tat_ca_tai_khoan, lay_chi_tiet_tai_khoan

class TestDuLieuMauVaXoaTaiKhoan(unittest.TestCase):
    def setUp(self):
        temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db_path = temp_file.name
        temp_file.close()
        self.original_db_path = config.DATABASE_PATH
        config.DATABASE_PATH = self.temp_db_path
        khoi_tao_co_so_du_lieu()
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

    def test_kiem_tra_va_nap_du_lieu_mau_mot_lan(self):
        self.assertTrue(kiem_tra_da_co_du_lieu())

        lan_2 = nap_du_lieu_mau()
        self.assertFalse(lan_2)

        ket_noi = lay_ket_noi()
        c = ket_noi.cursor()
        c.execute("SELECT COUNT(*) FROM cap_bac")
        so_cb = c.fetchone()[0]
        self.assertEqual(so_cb, 10)
        ket_noi.close()

    def test_xoa_tai_khoan_va_khong_con_trong_danh_sach(self):
        with self.client.session_transaction() as sess:
            sess["nguoi_dung"] = {
                "ma_tu_sinh": 1,
                "ten_dang_nhap": "admin",
                "ho_ten": "Quản trị viên",
                "ten_vai_tro": "Quản trị",
                "ma_vai_tro": "QUAN_TRI",
                "quyen": ["QUANTRI.TAIKHOAN"]
            }

        tk_id = them_tai_khoan(
            ten_dang_nhap="canbo_xoa_test",
            mat_khau="12345678",
            ho_ten="Cán bộ Cần Xóa",
            khoa_vai_tro=2,
            pham_vi_loai="TOAN_BO"
        )

        all_before = lay_tat_ca_tai_khoan()
        self.assertTrue(any(t["ma_tu_sinh"] == tk_id for t in all_before))

        res_del = self.client.post(f"/tai-khoan/xoa/{tk_id}", follow_redirects=True)
        self.assertEqual(res_del.status_code, 200)

        all_after = lay_tat_ca_tai_khoan()
        self.assertFalse(any(t["ma_tu_sinh"] == tk_id for t in all_after))
        self.assertIsNone(lay_chi_tiet_tai_khoan(tk_id))

        res_del_again = self.client.post(f"/tai-khoan/xoa/{tk_id}", follow_redirects=True)
        self.assertEqual(res_del_again.status_code, 200)
        self.assertIn("không tồn tại hoặc đã được xóa trước đó", res_del_again.data.decode("utf-8"))

    def test_headers_no_cache_tren_cac_trang(self):
        res = self.client.get("/dang-nhap")
        self.assertEqual(res.status_code, 200)
        cache_control = res.headers.get("Cache-Control", "")
        self.assertIn("no-cache", cache_control)
        self.assertIn("no-store", cache_control)

if __name__ == "__main__":
    unittest.main()
