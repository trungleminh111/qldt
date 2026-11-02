import os
import tempfile
import unittest
from datetime import datetime
import config
from app import tao_ung_dung
from models.co_so_du_lieu import khoi_tao_co_so_du_lieu, lay_ket_noi
from models.du_lieu_mau import nap_du_lieu_mau
from models.cau_hinh_model import (
    them_ngay_dac_biet,
    sua_ngay_dac_biet,
    xoa_ngay_dac_biet,
    lay_danh_sach_ngay_dac_biet,
    lay_mo_ta_loai_lap
)
from models.giao_nhan_model import kiem_tra_khung_gio

class TestRecurringSpecialDays(unittest.TestCase):
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

    def test_mo_ta_loai_lap_helper(self):
        self.assertEqual(lay_mo_ta_loai_lap("MOT_LAN", "2026-11-02"), "Một lần")
        self.assertEqual(lay_mo_ta_loai_lap("HANG_NAM", "2026-12-22"), "Hàng năm (22/12)")
        self.assertEqual(lay_mo_ta_loai_lap("HANG_THANG", "2026-11-15"), "Hàng tháng (Ngày 15)")
        self.assertEqual(lay_mo_ta_loai_lap("HANG_TUAN", "2026-11-02"), "Hàng tuần (Thứ 2)")

    def test_ban_recurring_yearly(self):
        them_ngay_dac_biet(
            ngay="2026-12-22",
            ly_do="Ngày thành lập Quân đội nhân dân Việt Nam",
            cam_su_dung=1,
            loai_lap="HANG_NAM"
        )
        res_2026 = kiem_tra_khung_gio(1, datetime(2026, 12, 22, 10, 0))
        self.assertFalse(res_2026["hop_le"])
        self.assertEqual(res_2026["ma_trang_thai"], "CAM_SU_DUNG")
        self.assertIn("Hàng năm (22/12)", res_2026["thong_bao"])

        res_2027 = kiem_tra_khung_gio(1, datetime(2027, 12, 22, 10, 0))
        self.assertFalse(res_2027["hop_le"])
        self.assertEqual(res_2027["ma_trang_thai"], "CAM_SU_DUNG")

        res_other = kiem_tra_khung_gio(1, datetime(2026, 12, 23, 10, 0))
        self.assertNotEqual(res_other["ma_trang_thai"], "CAM_SU_DUNG")

    def test_ban_recurring_monthly(self):
        them_ngay_dac_biet(
            ngay="2026-11-15",
            ly_do="Ngày kỹ thuật toàn quân",
            cam_su_dung=1,
            loai_lap="HANG_THANG"
        )
        res_nov = kiem_tra_khung_gio(1, datetime(2026, 11, 15, 10, 0))
        self.assertFalse(res_nov["hop_le"])
        self.assertEqual(res_nov["ma_trang_thai"], "CAM_SU_DUNG")
        self.assertIn("Hàng tháng (Ngày 15)", res_nov["thong_bao"])

        res_dec = kiem_tra_khung_gio(1, datetime(2026, 12, 15, 10, 0))
        self.assertFalse(res_dec["hop_le"])
        self.assertEqual(res_dec["ma_trang_thai"], "CAM_SU_DUNG")

        res_other = kiem_tra_khung_gio(1, datetime(2026, 11, 16, 10, 0))
        self.assertNotEqual(res_other["ma_trang_thai"], "CAM_SU_DUNG")

    def test_ban_recurring_weekly(self):
        them_ngay_dac_biet(
            ngay="2026-11-02",
            ly_do="Chào cờ và sinh hoạt chính trị đầu tuần",
            cam_su_dung=1,
            loai_lap="HANG_TUAN"
        )
        res_mon1 = kiem_tra_khung_gio(1, datetime(2026, 11, 2, 10, 0))
        self.assertFalse(res_mon1["hop_le"])
        self.assertEqual(res_mon1["ma_trang_thai"], "CAM_SU_DUNG")
        self.assertIn("Hàng tuần (Thứ 2)", res_mon1["thong_bao"])

        res_mon2 = kiem_tra_khung_gio(1, datetime(2026, 11, 9, 10, 0))
        self.assertFalse(res_mon2["hop_le"])
        self.assertEqual(res_mon2["ma_trang_thai"], "CAM_SU_DUNG")

        res_tue = kiem_tra_khung_gio(1, datetime(2026, 11, 3, 10, 0))
        self.assertNotEqual(res_tue["ma_trang_thai"], "CAM_SU_DUNG")

    def test_ban_single_day(self):
        them_ngay_dac_biet(
            ngay="2026-11-05",
            ly_do="Diễn tập đột xuất",
            cam_su_dung=1,
            loai_lap="MOT_LAN"
        )
        res_day = kiem_tra_khung_gio(1, datetime(2026, 11, 5, 10, 0))
        self.assertFalse(res_day["hop_le"])
        self.assertEqual(res_day["ma_trang_thai"], "CAM_SU_DUNG")

        res_next_year = kiem_tra_khung_gio(1, datetime(2027, 11, 5, 10, 0))
        self.assertNotEqual(res_next_year["ma_trang_thai"], "CAM_SU_DUNG")

    def test_controller_them_and_sua_ngay_dac_biet(self):
        with self.client.session_transaction() as sess:
            sess["nguoi_dung"] = {
                "ma_tu_sinh": 1,
                "ten_dang_nhap": "admin",
                "ho_ten": "Quản trị viên",
                "ten_vai_tro": "Quản trị",
                "ma_vai_tro": "QUAN_TRI",
                "quyen": ["CAUHINH.GIO"]
            }

        post_res = self.client.post("/ngay-dac-biet/them", data={
            "ngay": "2026-12-22",
            "ly_do": "Ngày QĐND",
            "cam_su_dung": "1",
            "loai_lap": "HANG_NAM"
        }, follow_redirects=True)
        self.assertEqual(post_res.status_code, 200)

        danh_sach = lay_danh_sach_ngay_dac_biet()
        self.assertEqual(len(danh_sach), 1)
        self.assertEqual(danh_sach[0]["loai_lap"], "HANG_NAM")
        self.assertEqual(danh_sach[0]["mo_ta_loai_lap"], "Hàng năm (22/12)")
        ndb_id = danh_sach[0]["ma_tu_sinh"]

        edit_res = self.client.post(f"/ngay-dac-biet/sua/{ndb_id}", data={
            "ngay": "2026-12-22",
            "ly_do": "Ngày QĐND Đã Đổi",
            "cam_su_dung": "1",
            "loai_lap": "HANG_THANG"
        }, follow_redirects=True)
        self.assertEqual(edit_res.status_code, 200)

        danh_sach_after = lay_danh_sach_ngay_dac_biet()
        self.assertEqual(danh_sach_after[0]["loai_lap"], "HANG_THANG")
        self.assertEqual(danh_sach_after[0]["ly_do"], "Ngày QĐND Đã Đổi")

        del_res = self.client.post(f"/ngay-dac-biet/xoa/{ndb_id}", follow_redirects=True)
        self.assertEqual(del_res.status_code, 200)
        self.assertEqual(len(lay_danh_sach_ngay_dac_biet()), 0)

if __name__ == "__main__":
    unittest.main()
