import os
import tempfile
import unittest
import config
from app import tao_ung_dung
from models.co_so_du_lieu import khoi_tao_co_so_du_lieu, lay_ket_noi
from models.du_lieu_mau import nap_du_lieu_mau
from models.phan_quyen_model import (
    them_tai_khoan,
    sua_tai_khoan,
    lay_tat_ca_tai_khoan,
    lay_chi_tiet_tai_khoan,
    xac_thuc_dang_nhap
)

class TestAccountPlatoonScope(unittest.TestCase):
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

    def test_them_tai_khoan_trung_doi_2(self):
        with self.client.session_transaction() as sess:
            sess["nguoi_dung"] = {
                "ma_tu_sinh": 1,
                "ten_dang_nhap": "admin",
                "ho_ten": "Quản trị viên",
                "ten_vai_tro": "Quản trị",
                "ma_vai_tro": "QUAN_TRI",
                "quyen": ["QUANTRI.TAIKHOAN"]
            }

        post_res = self.client.post("/tai-khoan/them", data={
            "ten_dang_nhap": "canbo_td2",
            "mat_khau": "12345678",
            "ho_ten": "Cán bộ Trung đội 2",
            "khoa_vai_tro": "2",
            "pham_vi_loai": "DON_VI",
            "pham_vi_khoa_don_vi": "3"
        }, follow_redirects=True)
        self.assertEqual(post_res.status_code, 200)

        accounts = lay_tat_ca_tai_khoan()
        created = next((a for a in accounts if a["ten_dang_nhap"] == "canbo_td2"), None)
        self.assertIsNotNone(created)
        self.assertEqual(created["pham_vi_loai"], "DON_VI")
        self.assertEqual(created["pham_vi_khoa"], 3)
        self.assertEqual(created["ten_don_vi_pham_vi"], "Trung đội 2")

        user_auth = xac_thuc_dang_nhap("canbo_td2", "12345678")
        self.assertIsNotNone(user_auth)
        self.assertEqual(user_auth["pham_vi_loai"], "DON_VI")
        self.assertEqual(user_auth["khoa_don_vi"], 3)

    def test_sua_tai_khoan_doi_sang_trung_doi_3(self):
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
            ten_dang_nhap="canbo_test",
            mat_khau="12345678",
            ho_ten="Cán bộ Thử nghiệm",
            khoa_vai_tro=2,
            pham_vi_loai="DON_VI",
            pham_vi_khoa=2
        )

        edit_res = self.client.post(f"/tai-khoan/sua/{tk_id}", data={
            "ho_ten": "Cán bộ Trung đội 3",
            "khoa_vai_tro": "2",
            "pham_vi_loai": "DON_VI",
            "pham_vi_khoa_don_vi": "4",
            "dang_dung": "1"
        }, follow_redirects=True)
        self.assertEqual(edit_res.status_code, 200)

        detail = lay_chi_tiet_tai_khoan(tk_id)
        self.assertEqual(detail["pham_vi_loai"], "DON_VI")
        self.assertEqual(detail["pham_vi_khoa"], 4)

        user_auth = xac_thuc_dang_nhap("canbo_test", "12345678")
        self.assertEqual(user_auth["khoa_don_vi"], 4)

    def test_giao_nhan_view_for_trung_doi_2_user(self):
        user_auth = {
            "ma_tu_sinh": 99,
            "ten_dang_nhap": "cb_td2",
            "ho_ten": "Cán bộ Trung đội 2",
            "ten_vai_tro": "Chỉ huy",
            "ma_vai_tro": "CHI_HUY",
            "pham_vi_loai": "DON_VI",
            "khoa_don_vi": 3
        }
        with self.client.session_transaction() as sess:
            sess["nguoi_dung"] = user_auth

        res = self.client.get("/giao-nhan")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("Phân quyền quản lý:", html)
        self.assertIn("Trung đội 2", html)
        self.assertNotIn("data-don-vi=\"Trung đội 1\"", html)
        self.assertNotIn("data-don-vi=\"Trung đội 3\"", html)

    def test_them_tai_khoan_voi_pham_vi_chon(self):
        with self.client.session_transaction() as sess:
            sess["nguoi_dung"] = {
                "ma_tu_sinh": 1,
                "ten_dang_nhap": "admin",
                "ho_ten": "Quản trị viên",
                "ten_vai_tro": "Quản trị",
                "ma_vai_tro": "QUAN_TRI",
                "quyen": ["QUANTRI.TAIKHOAN"]
            }

        post_res = self.client.post("/tai-khoan/them", data={
            "ten_dang_nhap": "cb_optgroup",
            "mat_khau": "12345678",
            "ho_ten": "Cán bộ Chọn Trực Tiếp",
            "khoa_vai_tro": "2",
            "pham_vi_chon": "DON_VI:3"
        }, follow_redirects=True)
        self.assertEqual(post_res.status_code, 200)

        accounts = lay_tat_ca_tai_khoan()
        created = next((a for a in accounts if a["ten_dang_nhap"] == "cb_optgroup"), None)
        self.assertIsNotNone(created)
        self.assertEqual(created["pham_vi_loai"], "DON_VI")
        self.assertEqual(created["pham_vi_khoa"], 3)

    def test_sua_tai_khoan_voi_pham_vi_chon_tu(self):
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
            ten_dang_nhap="cb_tu_test",
            mat_khau="12345678",
            ho_ten="Cán bộ Tủ",
            khoa_vai_tro=2,
            pham_vi_loai="TOAN_BO"
        )

        edit_res = self.client.post(f"/tai-khoan/sua/{tk_id}", data={
            "ho_ten": "Cán bộ Phụ trách Tủ 2",
            "khoa_vai_tro": "2",
            "pham_vi_chon": "TU:2",
            "dang_dung": "1"
        }, follow_redirects=True)
        self.assertEqual(edit_res.status_code, 200)

        detail = lay_chi_tiet_tai_khoan(tk_id)
        self.assertEqual(detail["pham_vi_loai"], "TU")
        self.assertEqual(detail["pham_vi_khoa"], 2)

if __name__ == "__main__":
    unittest.main()
