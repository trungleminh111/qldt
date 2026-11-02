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
    lay_so_do_tu
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
