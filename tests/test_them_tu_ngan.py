import os
import tempfile
import unittest
import config
from app import tao_ung_dung
from models.co_so_du_lieu import khoi_tao_co_so_du_lieu, lay_ket_noi
from models.du_lieu_mau import nap_du_lieu_mau
from models.dien_thoai_model import (
    lay_goi_y_tu_tiep_theo,
    them_tu,
    lay_goi_y_ngan_tiep_theo,
    them_ngan,
    lay_danh_sach_tu,
    lay_so_do_tu,
    xoa_tu,
    xoa_ngan
)

class TestThemTuNgan(unittest.TestCase):
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

    def test_lay_goi_y_tu_tiep_theo(self):
        goi_y = lay_goi_y_tu_tiep_theo()
        self.assertIn("ma_tu", goi_y)
        self.assertEqual(goi_y["ma_tu"], "T05")
        self.assertEqual(goi_y["tien_to_ngan"], "E")

    def test_them_tu_moi(self):
        khoa_tu = them_tu(
            ma_tu="T05",
            ten_tu="Tủ Đại đội bộ",
            vi_tri="Phòng giao ban",
            so_ngan=12,
            khoa_don_vi_quan_ly=1,
            tien_to_ngan="E"
        )
        self.assertGreater(khoa_tu, 0)

        ket_noi = lay_ket_noi()
        c = ket_noi.cursor()
        c.execute("SELECT ma_tu, ten_tu, so_ngan FROM tu WHERE ma_tu_sinh = ?", (khoa_tu,))
        tu_row = c.fetchone()
        self.assertIsNotNone(tu_row)
        self.assertEqual(tu_row["ma_tu"], "T05")
        self.assertEqual(tu_row["ten_tu"], "Tủ Đại đội bộ")
        self.assertEqual(tu_row["so_ngan"], 12)

        c.execute("SELECT COUNT(*) as cnt, MIN(ma_ngan) as min_m, MAX(ma_ngan) as max_m FROM ngan WHERE khoa_tu = ?", (khoa_tu,))
        ngan_stat = c.fetchone()
        self.assertEqual(ngan_stat["cnt"], 12)
        self.assertEqual(ngan_stat["min_m"], "T05-E01")
        self.assertEqual(ngan_stat["max_m"], "T05-E12")
        ket_noi.close()

    def test_lay_goi_y_ngan_va_them_ngan(self):
        khoa_tu = them_tu(
            ma_tu="T05",
            ten_tu="Tủ Đại đội bộ",
            vi_tri="Phòng giao ban",
            so_ngan=5,
            khoa_don_vi_quan_ly=1,
            tien_to_ngan="E"
        )
        goi_y = lay_goi_y_ngan_tiep_theo(khoa_tu)
        self.assertEqual(goi_y[0], "E06")
        self.assertEqual(goi_y[1], "T05-E06")

        added_ids = them_ngan(khoa_tu=khoa_tu, ten_ngan="E06", so_luong=2)
        self.assertEqual(len(added_ids), 2)

        ket_noi = lay_ket_noi()
        c = ket_noi.cursor()
        c.execute("SELECT so_ngan FROM tu WHERE ma_tu_sinh = ?", (khoa_tu,))
        self.assertEqual(c.fetchone()["so_ngan"], 7)

        c.execute("SELECT ma_ngan, ten_ngan FROM ngan WHERE khoa_tu = ? ORDER BY ma_tu_sinh ASC", (khoa_tu,))
        all_ngan = c.fetchall()
        self.assertEqual(len(all_ngan), 7)
        self.assertEqual(all_ngan[-2]["ten_ngan"], "E06")
        self.assertEqual(all_ngan[-1]["ten_ngan"], "E07")
        ket_noi.close()

    def test_controller_them_tu_route(self):
        with self.client.session_transaction() as sess:
            sess["nguoi_dung"] = {
                "ma_tu_sinh": 1,
                "ten_dang_nhap": "admin",
                "ho_ten": "Quản trị viên",
                "ten_vai_tro": "Quản trị",
                "ma_vai_tro": "QUAN_TRI",
                "quyen": []
            }

        res = self.client.post("/tu-dien-thoai/them", data={
            "ma_tu": "T05",
            "ten_tu": "Tủ thử nghiệm",
            "vi_tri": "Hành lang",
            "so_ngan": "10",
            "tien_to_ngan": "E",
            "khoa_don_vi_quan_ly": "2"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        so_do_res = self.client.get("/tu-dien-thoai/T05")
        self.assertEqual(so_do_res.status_code, 200)
        self.assertIn(b"T05", so_do_res.data)
        self.assertIn(b"E01", so_do_res.data)

    def test_controller_them_ngan_route(self):
        khoa_tu = them_tu(
            ma_tu="T05",
            ten_tu="Tủ thử nghiệm",
            vi_tri="Hành lang",
            so_ngan=5,
            khoa_don_vi_quan_ly=2,
            tien_to_ngan="E"
        )
        with self.client.session_transaction() as sess:
            sess["nguoi_dung"] = {
                "ma_tu_sinh": 1,
                "ten_dang_nhap": "admin",
                "ho_ten": "Quản trị viên",
                "ten_vai_tro": "Quản trị",
                "ma_vai_tro": "QUAN_TRI",
                "quyen": []
            }

        res = self.client.post("/ngan-tu/them", data={
            "khoa_tu": str(khoa_tu),
            "ma_tu": "T05",
            "ten_ngan": "E06",
            "so_luong": "3"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        so_do_res = self.client.get("/tu-dien-thoai/T05")
        self.assertEqual(so_do_res.status_code, 200)
        self.assertIn(b"E06", so_do_res.data)
        self.assertIn(b"E07", so_do_res.data)
        self.assertIn(b"E08", so_do_res.data)
    def test_so_do_tu_hien_thi_dien_thoai_va_link_chi_tiet(self):
        so_do = lay_so_do_tu("T01")
        co_dien_thoai = [r for r in so_do if r.get("khoa_dien_thoai")]
        self.assertGreater(len(co_dien_thoai), 0)
        first_dt = co_dien_thoai[0]
        self.assertIsNotNone(first_dt["ma_thiet_bi"])
        self.assertIsNotNone(first_dt["ho_ten"])

        with self.client.session_transaction() as sess:
            sess["nguoi_dung"] = {
                "ma_tu_sinh": 1,
                "ten_dang_nhap": "admin",
                "ho_ten": "Quản trị viên",
                "ten_vai_tro": "Quản trị",
                "ma_vai_tro": "QUAN_TRI",
                "quyen": []
            }

        res = self.client.get("/tu-dien-thoai/T01")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn(first_dt["ma_thiet_bi"], html)
        self.assertIn(f"/dien-thoai/chi-tiet/{first_dt['khoa_dien_thoai']}", html)

    def test_them_tu_voi_pham_vi_don_vi_danh_sach(self):
        with self.client.session_transaction() as sess:
            sess["nguoi_dung"] = {
                "ma_tu_sinh": 2,
                "ten_dang_nhap": "canbo_trungdoi",
                "ho_ten": "Cán bộ trung đội",
                "ten_vai_tro": "Cán bộ quản lý",
                "ma_vai_tro": "CAN_BO",
                "pham_vi_loai": "DON_VI",
                "khoa_don_vi": "2,3",
                "quyen": []
            }

        res = self.client.post("/tu-dien-thoai/them", data={
            "ma_tu": "T05",
            "ten_tu": "Tủ Trung đội 1 mở rộng",
            "vi_tri": "Phòng Trung đội 1",
            "so_ngan": "15",
            "tien_to_ngan": "E",
            "khoa_don_vi_quan_ly": "2"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        ket_noi = lay_ket_noi()
        c = ket_noi.cursor()
        c.execute("SELECT ma_tu, khoa_don_vi_quan_ly FROM tu WHERE ma_tu = 'T05'")
        row = c.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["khoa_don_vi_quan_ly"], 2)
        ket_noi.close()
    def test_admin_truy_cap_tat_ca_tu_khong_bi_gioi_han(self):
        with self.client.session_transaction() as sess:
            sess["nguoi_dung"] = {
                "ma_tu_sinh": 1,
                "ten_dang_nhap": "admin",
                "ho_ten": "Quản trị viên",
                "ten_vai_tro": "Quản trị",
                "ma_vai_tro": "QUAN_TRI",
                "pham_vi_loai": "DON_VI",
                "khoa_don_vi": "2",
                "quyen": []
            }

        res = self.client.get("/tu-dien-thoai/T02", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertNotIn("Đồng chí không có thẩm quyền truy cập tủ của đơn vị khác", html)
        self.assertIn("T02", html)
    def test_xoa_tu_that_bai_khi_co_nguoi_va_thanh_cong_khi_rong(self):
        with self.assertRaises(ValueError):
            xoa_tu("T01")

        khoa_tu = them_tu(
            ma_tu="T99",
            ten_tu="Tủ tạm thời",
            vi_tri="Kho",
            so_ngan=2,
            khoa_don_vi_quan_ly=1,
            tien_to_ngan="Z"
        )
        ma_xoa = xoa_tu("T99")
        self.assertEqual(ma_xoa, "T99")

        ds_tu = lay_danh_sach_tu()
        self.assertFalse(any(t["ma_tu"] == "T99" for t in ds_tu))

    def test_xoa_ngan_that_bai_khi_co_nguoi_va_thanh_cong_khi_rong(self):
        so_do_t1 = lay_so_do_tu("T01")
        ngan_co_chu = next(r for r in so_do_t1 if r.get("khoa_quan_nhan"))
        with self.assertRaises(ValueError):
            xoa_ngan(ngan_co_chu["ma_tu_sinh"])

        khoa_tu = them_tu(
            ma_tu="T98",
            ten_tu="Tủ thử nghiệm xóa",
            vi_tri="Kho",
            so_ngan=2,
            khoa_don_vi_quan_ly=1,
            tien_to_ngan="Y"
        )
        so_do_t98 = lay_so_do_tu("T98")
        self.assertEqual(len(so_do_t98), 2)
        ngan_can_xoa = so_do_t98[0]

        res = xoa_ngan(ngan_can_xoa["ma_tu_sinh"])
        self.assertEqual(res["ma_tu"], "T98")

        so_do_t98_sau = lay_so_do_tu("T98")
        self.assertEqual(len(so_do_t98_sau), 1)

    def test_controller_xoa_tu_va_xoa_ngan_route(self):
        khoa_tu = them_tu(
            ma_tu="T97",
            ten_tu="Tủ kiểm tra controller",
            vi_tri="Kho",
            so_ngan=2,
            khoa_don_vi_quan_ly=1,
            tien_to_ngan="X"
        )
        so_do_t97 = lay_so_do_tu("T97")
        ngan_xoa = so_do_t97[0]

        with self.client.session_transaction() as sess:
            sess["nguoi_dung"] = {
                "ma_tu_sinh": 1,
                "ten_dang_nhap": "admin",
                "ho_ten": "Quản trị viên",
                "ten_vai_tro": "Quản trị",
                "ma_vai_tro": "QUAN_TRI",
                "quyen": []
            }

        res_ngan = self.client.post("/ngan-tu/xoa", data={
            "khoa_ngan": str(ngan_xoa["ma_tu_sinh"]),
            "ma_tu": "T97"
        }, follow_redirects=True)
        self.assertEqual(res_ngan.status_code, 200)

        so_do_sau = lay_so_do_tu("T97")
        self.assertEqual(len(so_do_sau), 1)

        res_tu = self.client.post("/tu-dien-thoai/xoa", data={
            "ma_tu": "T97"
        }, follow_redirects=True)
        self.assertEqual(res_tu.status_code, 200)

        ds_sau = lay_danh_sach_tu()
        self.assertFalse(any(t["ma_tu"] == "T97" for t in ds_sau))

    def test_truc_ban_bi_tu_choi_xoa_va_them_tu_ngan(self):
        khoa_tu = them_tu(
            ma_tu="T96",
            ten_tu="Tủ kiểm tra trực ban",
            vi_tri="Phòng trực ban",
            so_ngan=2,
            khoa_don_vi_quan_ly=1,
            tien_to_ngan="Z"
        )
        so_do_t96 = lay_so_do_tu("T96")
        ngan_target = so_do_t96[0]

        with self.client.session_transaction() as sess:
            sess["nguoi_dung"] = {
                "ma_tu_sinh": 2,
                "ten_dang_nhap": "tuananh",
                "ho_ten": "Phạm Tuấn Anh",
                "ten_vai_tro": "Cán bộ trực ca",
                "ma_vai_tro": "NGUOI_TRUC",
                "cac_quyen": ["GIAONHAN.GHI", "GIAONHAN.XEM", "CATRUC.BANGIAO"],
                "danh_sach_quyen": ["GIAONHAN.GHI", "GIAONHAN.XEM", "CATRUC.BANGIAO"]
            }

        res_view = self.client.get("/tu-dien-thoai")
        self.assertNotIn("＋ Thêm tủ bảo quản mới", res_view.data.decode("utf-8"))
        self.assertNotIn("🗑 Xóa", res_view.data.decode("utf-8"))

        res_sodo = self.client.get("/tu-dien-thoai/T96")
        self.assertNotIn("🗑 Xóa tủ này", res_sodo.data.decode("utf-8"))

        res_xoa_tu = self.client.post("/tu-dien-thoai/xoa", data={"ma_tu": "T96"}, follow_redirects=True)
        self.assertIn("không có thẩm quyền", res_xoa_tu.data.decode("utf-8"))
        ds_tu = lay_danh_sach_tu()
        self.assertTrue(any(t["ma_tu"] == "T96" for t in ds_tu))

        res_xoa_ngan = self.client.post("/ngan-tu/xoa", data={
            "khoa_ngan": str(ngan_target["ma_tu_sinh"]),
            "ma_tu": "T96"
        }, follow_redirects=True)
        self.assertIn("không có thẩm quyền", res_xoa_ngan.data.decode("utf-8"))
        so_do_sau = lay_so_do_tu("T96")
        self.assertEqual(len(so_do_sau), 2)

    def test_cap_nhat_quyen_vai_tro_va_hien_thi_checked(self):
        with self.client.session_transaction() as sess:
            sess["nguoi_dung"] = {
                "ma_tu_sinh": 1,
                "ten_dang_nhap": "admin",
                "ho_ten": "Quản trị viên",
                "ten_vai_tro": "Quản trị",
                "ma_vai_tro": "QUAN_TRI",
                "cac_quyen": ["QUANTRI.TAIKHOAN"],
                "danh_sach_quyen": ["QUANTRI.TAIKHOAN"]
            }

        res_post = self.client.post("/vai-tro/cap-nhat-quyen/2", data={
            "quyen_ids": ["1", "2", "3", "5"]
        }, follow_redirects=True)
        self.assertEqual(res_post.status_code, 200)

        res_get = self.client.get("/tai-khoan-phan-quyen")
        html = res_get.data.decode("utf-8")
        self.assertIn("checked", html)

    def test_doi_ten_tai_khoan_mau_thanh_cong(self):
        with self.client.session_transaction() as sess:
            sess["nguoi_dung"] = {
                "ma_tu_sinh": 1,
                "ten_dang_nhap": "admin",
                "ho_ten": "Quản trị viên",
                "ten_vai_tro": "Quản trị",
                "ma_vai_tro": "QUAN_TRI",
                "cac_quyen": ["QUANTRI.TAIKHOAN"],
                "danh_sach_quyen": ["QUANTRI.TAIKHOAN"]
            }

        res = self.client.post("/tai-khoan/sua/2", data={
            "ten_dang_nhap": "tuananh_vip",
            "ho_ten": "Phạm Tuấn Anh (Đã đổi tên)",
            "khoa_vai_tro": "3",
            "dang_dung": "1",
            "pham_vi_loai": "TOAN_BO"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        ket_noi = lay_ket_noi()
        c = ket_noi.cursor()
        c.execute("SELECT ten_dang_nhap, ho_ten, khoa_quan_nhan FROM tai_khoan WHERE ma_tu_sinh = 2")
        tk_row = c.fetchone()
        self.assertIsNotNone(tk_row)
        self.assertEqual(tk_row["ten_dang_nhap"], "tuananh_vip")
        self.assertEqual(tk_row["ho_ten"], "Phạm Tuấn Anh (Đã đổi tên)")

        if tk_row["khoa_quan_nhan"]:
            c.execute("SELECT ho_ten FROM quan_nhan WHERE ma_tu_sinh = ?", (tk_row["khoa_quan_nhan"],))
            qn_row = c.fetchone()
            self.assertIsNotNone(qn_row)
            self.assertEqual(qn_row["ho_ten"], "Phạm Tuấn Anh (Đã đổi tên)")
        ket_noi.close()

        res_trang = self.client.get("/tai-khoan-phan-quyen")
        html = res_trang.data.decode("utf-8")
        self.assertIn("tuananh_vip", html)
        self.assertIn("Phạm Tuấn Anh (Đã đổi tên)", html)

    def test_doi_ten_tai_khoan_trung_lap_bi_tu_choi(self):
        with self.client.session_transaction() as sess:
            sess["nguoi_dung"] = {
                "ma_tu_sinh": 1,
                "ten_dang_nhap": "admin",
                "ho_ten": "Quản trị viên",
                "ten_vai_tro": "Quản trị",
                "ma_vai_tro": "QUAN_TRI",
                "cac_quyen": ["QUANTRI.TAIKHOAN"],
                "danh_sach_quyen": ["QUANTRI.TAIKHOAN"]
            }

        res = self.client.post("/tai-khoan/sua/3", data={
            "ten_dang_nhap": "admin",
            "ho_ten": "Trần Văn Bình",
            "khoa_vai_tro": "3",
            "dang_dung": "1",
            "pham_vi_loai": "TOAN_BO"
        }, follow_redirects=True)
        self.assertIn("đã tồn tại", res.data.decode("utf-8"))
