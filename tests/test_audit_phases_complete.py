import unittest
import uuid
from app import tao_ung_dung
from models.co_so_du_lieu import lay_ket_noi, khoi_tao_co_so_du_lieu, lay_danh_sach_don_vi_truc_thuoc
from models.du_lieu_mau import nap_du_lieu_mau
from models.dien_thoai_model import sua_dien_thoai
from models.giao_nhan_model import thuc_hien_lay_dien_thoai, duyet_ngoai_le
from models.quan_nhan_model import them_don_vi, sua_don_vi

class TestAuditPhasesComplete(unittest.TestCase):
    def setUp(self):
        self.app = tao_ung_dung()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        khoi_tao_co_so_du_lieu()
        nap_du_lieu_mau()

    def login_admin(self):
        with self.client.session_transaction() as sess:
            sess["nguoi_dung"] = {
                "ma_tu_sinh": 1,
                "ten_dang_nhap": "admin",
                "ho_ten": "Nguyễn Minh Quân",
                "ma_vai_tro": "QUAN_TRI",
                "pham_vi_loai": "TOAN_BO",
                "danh_sach_quyen": [
                    "CAUHINH.GIO", "QUANTRI.HETHONG",
                    "CAUHINH.QUANNHAN", "NGOAILE.DUYET", "GIAONHAN.XEM", "GIAONHAN.GHI"
                ]
            }

    def test_emergency_loan_and_approval(self):
        conn = lay_ket_noi()
        cur = conn.cursor()
        cur.execute("DELETE FROM lich_su_giao_nhan WHERE khoa_quan_nhan = 2")
        conn.commit()
        conn.close()
        thanh_cong, msg = thuc_hien_lay_dien_thoai(
            khoa_quan_nhan=2,
            khoa_nguoi_thuc_hien=2,
            ten_nguoi_thuc_hien="Cán bộ trực",
            la_ngoai_le=True,
            ly_do="Gia đình gọi khẩn cấp",
            han_nop="10:00",
            khoa_nguoi_duyet=None
        )
        self.assertTrue(thanh_cong)
        conn = lay_ket_noi()
        cur = conn.cursor()
        cur.execute("SELECT ma_tu_sinh, trang_thai FROM ngoai_le WHERE khoa_quan_nhan = 2 ORDER BY ma_tu_sinh DESC LIMIT 1")
        nl = cur.fetchone()
        self.assertEqual(nl["trang_thai"], "CHO_DUYET")
        duyet_ngoai_le(nl["ma_tu_sinh"], 1)
        cur.execute("SELECT trang_thai, khoa_nguoi_duyet FROM ngoai_le WHERE ma_tu_sinh = ?", (nl["ma_tu_sinh"],))
        nl_sau = cur.fetchone()
        conn.close()
        self.assertEqual(nl_sau["trang_thai"], "DA_DUYET")
        self.assertEqual(nl_sau["khoa_nguoi_duyet"], 1)

    def test_compartment_assignment_collision_prevention(self):
        with self.assertRaises(ValueError):
            sua_dien_thoai(
                ma_tu_sinh=3,
                ten_dien_thoai="Reno8",
                hang_san_xuat="OPPO",
                model="Reno8",
                so_imei="864128059124018",
                so_dien_thoai="0981234563",
                khoa_quan_nhan=3,
                ma_ngan="T01-A01"
            )

    def test_three_tier_unit_hierarchy(self):
        uid = uuid.uuid4().hex[:6].upper()
        ma1 = f"TD_{uid}"
        ma2 = f"MD_{uid}"
        tieu_doi_id = them_don_vi(
            ma_don_vi=ma1,
            ten_don_vi="Tiểu đội 1",
            khoa_don_vi_cha=2,
            thu_tu=1
        )
        self.assertIsNotNone(tieu_doi_id)
        sub_units = lay_danh_sach_don_vi_truc_thuoc(2)
        self.assertIn(tieu_doi_id, sub_units)
        sub_c1 = lay_danh_sach_don_vi_truc_thuoc(1)
        self.assertIn(tieu_doi_id, sub_c1)
        sua_don_vi(tieu_doi_id, ma2, "Tiểu đội 1 Mới", thu_tu=2, dang_dung=1, khoa_don_vi_cha=3)
        sub_b2 = lay_danh_sach_don_vi_truc_thuoc(3)
        self.assertIn(tieu_doi_id, sub_b2)

    def test_route_aliases_work(self):
        self.login_admin()
        res_kg = self.client.get("/khung-gio")
        self.assertEqual(res_kg.status_code, 200)
        res_dl = self.client.get("/da-lay-su-dung")
        self.assertEqual(res_dl.status_code, 302)

if __name__ == "__main__":
    unittest.main()
