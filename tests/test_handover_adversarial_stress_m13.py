import json
import os
import shutil
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from unittest.mock import patch

import config
from app import tao_ung_dung
from models.ca_truc_model import (
    lay_ca_hien_tai,
    lay_chi_tiet_ban_giao,
    lay_danh_sach_ca_truc,
    lay_lich_su_ban_giao_ca,
    lay_so_lieu_kiem_ke,
    thuc_hien_ban_giao_ca,
)
from models.co_so_du_lieu import khoi_tao_co_so_du_lieu, lay_ket_noi
from models.du_lieu_mau import nap_du_lieu_mau
from models.giao_nhan_model import danh_sach_chua_nop, thuc_hien_nop_dien_thoai
from models.phan_quyen_model import xac_thuc_dang_nhap
from tests.test_base import BaseTestCase

class TestOvernightShiftBoundaryStress(BaseTestCase):

    def test_overnight_shift_extreme_boundary_23_59_59(self):
        conn = lay_ket_noi()
        cur = conn.cursor()
        cur.execute("UPDATE ca_truc SET dang_dung = 0")
        cur.execute("INSERT INTO ca_truc (ma_ca, ten_ca, gio_bat_dau, gio_ket_thuc, dang_dung) VALUES ('CA_DEM', 'Ca gác đêm', '22:00', '06:00', 1)")
        conn.commit()
        conn.close()

        with patch("models.ca_truc_model.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 11, 2, 23, 59, 59)
            mock_dt.strftime = datetime.strftime
            mock_dt.strptime = datetime.strptime
            ca = lay_ca_hien_tai()
            self.assertIsNotNone(ca)
            self.assertEqual(ca["ma_ca"], "CA_DEM")

    def test_overnight_shift_extreme_boundary_00_00_00(self):
        conn = lay_ket_noi()
        cur = conn.cursor()
        cur.execute("UPDATE ca_truc SET dang_dung = 0")
        cur.execute("INSERT INTO ca_truc (ma_ca, ten_ca, gio_bat_dau, gio_ket_thuc, dang_dung) VALUES ('CA_DEM', 'Ca gác đêm', '22:00', '06:00', 1)")
        conn.commit()
        conn.close()

        with patch("models.ca_truc_model.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 11, 3, 0, 0, 0)
            mock_dt.strftime = datetime.strftime
            mock_dt.strptime = datetime.strptime
            ca = lay_ca_hien_tai()
            self.assertIsNotNone(ca)
            self.assertEqual(ca["ma_ca"], "CA_DEM")

    def test_overnight_shift_extreme_boundary_05_59_59(self):
        conn = lay_ket_noi()
        cur = conn.cursor()
        cur.execute("UPDATE ca_truc SET dang_dung = 0")
        cur.execute("INSERT INTO ca_truc (ma_ca, ten_ca, gio_bat_dau, gio_ket_thuc, dang_dung) VALUES ('CA_DEM', 'Ca gác đêm', '22:00', '06:00', 1)")
        conn.commit()
        conn.close()

        with patch("models.ca_truc_model.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 11, 3, 5, 59, 59)
            mock_dt.strftime = datetime.strftime
            mock_dt.strptime = datetime.strptime
            ca = lay_ca_hien_tai()
            self.assertIsNotNone(ca)
            self.assertEqual(ca["ma_ca"], "CA_DEM")

    def test_overnight_shift_exact_boundary_start_22_00_00(self):
        conn = lay_ket_noi()
        cur = conn.cursor()
        cur.execute("UPDATE ca_truc SET dang_dung = 0")
        cur.execute("INSERT INTO ca_truc (ma_ca, ten_ca, gio_bat_dau, gio_ket_thuc, dang_dung) VALUES ('CA_DEM', 'Ca gác đêm', '22:00', '06:00', 1)")
        conn.commit()
        conn.close()

        with patch("models.ca_truc_model.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 11, 2, 22, 0, 0)
            mock_dt.strftime = datetime.strftime
            mock_dt.strptime = datetime.strptime
            ca = lay_ca_hien_tai()
            self.assertIsNotNone(ca)
            self.assertEqual(ca["ma_ca"], "CA_DEM")

    def test_overnight_shift_exact_boundary_end_06_00_00(self):
        conn = lay_ket_noi()
        cur = conn.cursor()
        cur.execute("UPDATE ca_truc SET dang_dung = 0")
        cur.execute("INSERT INTO ca_truc (ma_ca, ten_ca, gio_bat_dau, gio_ket_thuc, dang_dung) VALUES ('CA_DEM', 'Ca gác đêm', '22:00', '06:00', 1)")
        conn.commit()
        conn.close()

        with patch("models.ca_truc_model.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 11, 3, 6, 0, 0)
            mock_dt.strftime = datetime.strftime
            mock_dt.strptime = datetime.strptime
            ca = lay_ca_hien_tai()
            self.assertIsNotNone(ca)
            self.assertEqual(ca["ma_ca"], "CA_DEM")

    def test_overnight_shift_outside_boundaries_pre_start_and_post_end(self):
        conn = lay_ket_noi()
        cur = conn.cursor()
        cur.execute("DELETE FROM ca_truc")
        cur.execute("INSERT INTO ca_truc (ma_ca, ten_ca, gio_bat_dau, gio_ket_thuc, dang_dung) VALUES ('CA_TOI', 'Ca tối', '18:00', '21:59', 1)")
        cur.execute("INSERT INTO ca_truc (ma_ca, ten_ca, gio_bat_dau, gio_ket_thuc, dang_dung) VALUES ('CA_DEM', 'Ca gác đêm', '22:00', '06:00', 1)")
        cur.execute("INSERT INTO ca_truc (ma_ca, ten_ca, gio_bat_dau, gio_ket_thuc, dang_dung) VALUES ('CA_SANG', 'Ca sáng', '06:01', '11:30', 1)")
        conn.commit()
        conn.close()

        with patch("models.ca_truc_model.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 11, 2, 21, 59, 59)
            mock_dt.strftime = datetime.strftime
            mock_dt.strptime = datetime.strptime
            ca = lay_ca_hien_tai()
            self.assertEqual(ca["ma_ca"], "CA_TOI")

        with patch("models.ca_truc_model.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 11, 3, 6, 1, 0)
            mock_dt.strftime = datetime.strftime
            mock_dt.strptime = datetime.strptime
            ca = lay_ca_hien_tai()
            self.assertEqual(ca["ma_ca"], "CA_SANG")

    def test_overnight_shift_narrow_window_across_midnight(self):
        conn = lay_ket_noi()
        cur = conn.cursor()
        cur.execute("UPDATE ca_truc SET dang_dung = 0")
        cur.execute("INSERT INTO ca_truc (ma_ca, ten_ca, gio_bat_dau, gio_ket_thuc, dang_dung) VALUES ('CA_CHUYEN_TIEP', 'Chuyển tiếp', '23:50', '00:10', 1)")
        conn.commit()
        conn.close()

        with patch("models.ca_truc_model.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 11, 2, 23, 55, 0)
            mock_dt.strftime = datetime.strftime
            mock_dt.strptime = datetime.strptime
            ca = lay_ca_hien_tai()
            self.assertEqual(ca["ma_ca"], "CA_CHUYEN_TIEP")

        with patch("models.ca_truc_model.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 11, 3, 0, 5, 0)
            mock_dt.strftime = datetime.strftime
            mock_dt.strptime = datetime.strptime
            ca = lay_ca_hien_tai()
            self.assertEqual(ca["ma_ca"], "CA_CHUYEN_TIEP")

    def test_full_day_shift_boundary_00_00_to_23_59(self):
        conn = lay_ket_noi()
        cur = conn.cursor()
        cur.execute("UPDATE ca_truc SET dang_dung = 0")
        cur.execute("INSERT INTO ca_truc (ma_ca, ten_ca, gio_bat_dau, gio_ket_thuc, dang_dung) VALUES ('CA_24H', 'Ca trực toàn nhật', '00:00', '23:59', 1)")
        conn.commit()
        conn.close()

        with patch("models.ca_truc_model.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 11, 2, 12, 34, 56)
            mock_dt.strftime = datetime.strftime
            mock_dt.strptime = datetime.strptime
            ca = lay_ca_hien_tai()
            self.assertEqual(ca["ma_ca"], "CA_24H")

class TestHandoverSubmissionStressAndPayloads(BaseTestCase):

    def test_handover_submission_with_empty_and_whitespace_notes(self):
        self.login("admin", "admin123")
        res = self.client.post("/ca-truc/xac-nhan", data={
            "khoa_ca": "1",
            "khoa_nguoi_nhan": "2",
            "ghi_chu": "   ",
            "bat_thuong": "0"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        history = lay_lich_su_ban_giao_ca(1)
        self.assertTrue(len(history) > 0)
        latest = history[0]
        self.assertEqual(latest["ghi_chu_ban_giao"], "")

        res_bb = self.client.get(f"/ca-truc/bien-ban/{latest['ma_tu_sinh']}")
        self.assertEqual(res_bb.status_code, 200)
        self.assertIn("Không có ý kiến dặn dò thêm", res_bb.data.decode("utf-8"))

    def test_handover_submission_with_special_characters_and_xss(self):
        self.login("admin", "admin123")
        payload = "<script>alert('XSS')</script> & ' OR 1=1 -- 📱🔒 100% bảo đảm"
        res = self.client.post("/ca-truc/xac-nhan", data={
            "khoa_ca": "1",
            "khoa_nguoi_nhan": "2",
            "ghi_chu": payload,
            "bat_thuong": "0"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        history = lay_lich_su_ban_giao_ca(1)
        latest = history[0]
        self.assertEqual(latest["ghi_chu_ban_giao"], payload)

        res_bb = self.client.get(f"/ca-truc/bien-ban/{latest['ma_tu_sinh']}")
        self.assertEqual(res_bb.status_code, 200)
        html_content = res_bb.data.decode("utf-8")
        self.assertNotIn("<script>alert('XSS')</script>", html_content)
        escaped_marker = "&lt;script&gt;alert(" + chr(38) + chr(35) + "39;XSS" + chr(38) + chr(35) + "39;)&lt;/script&gt;"
        self.assertIn(escaped_marker, html_content)

    def test_corrupted_and_malformed_snapshots_resilience(self):
        self.login("admin", "admin123")
        malformed_snapshots = [
            "{invalid json string",
            "",
            None,
            "123456",
            "\"simple text snapshot\"",
            "[1, 2, 3, 4]",
            "{}",
            "{\"danh_sach_chua_nop\": \"not_a_list\"}"
        ]

        for snap in malformed_snapshots:
            bg_id = thuc_hien_ban_giao_ca(
                khoa_ca=1,
                khoa_nguoi_ban_giao=1,
                khoa_nguoi_nhan=2,
                ghi_chu="Malformed snapshot test",
                du_lieu_snapshot=snap
            )
            self.assertIsNotNone(bg_id)

            res_api = self.client.get(f"/ca-truc/api/chi-tiet/{bg_id}")
            self.assertEqual(res_api.status_code, 200)
            data = res_api.get_json()
            self.assertTrue(data["thanh_cong"])
            self.assertIsInstance(data["snapshot"], (dict, list, int, str))

            res_bb = self.client.get(f"/ca-truc/bien-ban/{bg_id}")
            self.assertEqual(res_bb.status_code, 200)

            res_index = self.client.get("/ca-truc")
            self.assertEqual(res_index.status_code, 200)

    def test_corrupted_snapshot_with_null_gio_lay_exposes_template_type_error(self):
        self.login("admin", "admin123")
        corrupted_item_snapshot = "{\"danh_sach_chua_nop\": [{\"ho_ten\": \"Nguyen Van A\", \"gio_lay\": null, \"muc_do\": null}]}"
        bg_id = thuc_hien_ban_giao_ca(
            khoa_ca=1,
            khoa_nguoi_ban_giao=1,
            khoa_nguoi_nhan=2,
            ghi_chu="Corrupted null gio_lay test",
            du_lieu_snapshot=corrupted_item_snapshot
        )
        res = self.client.get(f"/ca-truc/bien-ban/{bg_id}")
        self.assertEqual(res.status_code, 200)

    def test_handover_submission_with_massive_note(self):
        self.login("admin", "admin123")
        massive_note = "A" * 8000
        res = self.client.post("/ca-truc/xac-nhan", data={
            "khoa_ca": "1",
            "khoa_nguoi_nhan": "2",
            "ghi_chu": massive_note,
            "bat_thuong": "0"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        history = lay_lich_su_ban_giao_ca(1)
        latest = history[0]
        self.assertEqual(len(latest["ghi_chu_ban_giao"]), 8000)

class TestHandoverAllReturnedVsMultipleOverdue(BaseTestCase):

    def test_handover_when_all_devices_are_returned(self):
        conn = lay_ket_noi()
        cur = conn.cursor()
        cur.execute("SELECT khoa_dien_thoai FROM lich_su_giao_nhan WHERE loai = 'LAY_RA'")
        active_loans = cur.fetchall()
        for row in active_loans:
            cur.execute("""
                INSERT INTO lich_su_giao_nhan (khoa_quan_nhan, khoa_dien_thoai, khoa_ngan, thoi_gian, loai, ket_qua, khoa_chuc_vu, khoa_nguoi_thuc_hien, ten_nguoi_thuc_hien, ghi_chu)
                VALUES (1, ?, 1, datetime('now'), 'NOP_VAO', 'DUNG_GIO', 1, 1, 'Admin', 'Clean all')
            """, (row[0],))
        conn.commit()
        conn.close()

        so_lieu = lay_so_lieu_kiem_ke()
        self.assertEqual(so_lieu["da_lay"], 0)
        self.assertEqual(so_lieu["chua_nop"], 0)
        self.assertEqual(so_lieu["so_qua_han"], 0)
        self.assertEqual(so_lieu["dang_trong_tu"], so_lieu["tong_thiet_bi"])

        chua_nop = danh_sach_chua_nop()
        self.assertEqual(len(chua_nop), 0)

        self.login("admin", "admin123")
        res = self.client.post("/ca-truc/xac-nhan", data={
            "khoa_ca": "1",
            "khoa_nguoi_nhan": "2",
            "ghi_chu": "Bàn giao ca sạch không nợ máy",
            "bat_thuong": "0",
            "in_bien_ban": "1"
        })
        self.assertEqual(res.status_code, 302)
        redirect_url = res.headers.get("Location")

        res_bb = self.client.get(redirect_url)
        self.assertEqual(res_bb.status_code, 200)
        html = res_bb.data.decode("utf-8")
        self.assertIn("Tất cả thiết bị đã được thu hồi đầy đủ về tủ bảo quản trước khi bàn giao", html)

    def test_handover_with_multiple_overdue_devices_and_thresholds(self):
        conn = lay_ket_noi()
        cur = conn.cursor()
        now = datetime.now()
        t_121m = (now - timedelta(minutes=121)).strftime("%Y-%m-%d %H:%M:%S")
        t_300m = (now - timedelta(minutes=300)).strftime("%Y-%m-%d %H:%M:%S")
        t_91m = (now - timedelta(minutes=91)).strftime("%Y-%m-%d %H:%M:%S")
        t_30m = (now - timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")

        cur.execute("DELETE FROM lich_su_giao_nhan")
        cur.execute("INSERT INTO lich_su_giao_nhan (khoa_quan_nhan, khoa_dien_thoai, khoa_ngan, thoi_gian, loai, ket_qua, khoa_nguoi_thuc_hien, ten_nguoi_thuc_hien) VALUES (1, 1, 1, ?, 'LAY_RA', 'DUNG_GIO', 1, 'Admin')", (t_121m,))
        cur.execute("INSERT INTO lich_su_giao_nhan (khoa_quan_nhan, khoa_dien_thoai, khoa_ngan, thoi_gian, loai, ket_qua, khoa_nguoi_thuc_hien, ten_nguoi_thuc_hien) VALUES (2, 2, 2, ?, 'LAY_RA', 'DUNG_GIO', 1, 'Admin')", (t_300m,))
        cur.execute("INSERT INTO lich_su_giao_nhan (khoa_quan_nhan, khoa_dien_thoai, khoa_ngan, thoi_gian, loai, ket_qua, khoa_nguoi_thuc_hien, ten_nguoi_thuc_hien) VALUES (3, 3, 3, ?, 'LAY_RA', 'DUNG_GIO', 1, 'Admin')", (t_91m,))
        cur.execute("INSERT INTO lich_su_giao_nhan (khoa_quan_nhan, khoa_dien_thoai, khoa_ngan, thoi_gian, loai, ket_qua, khoa_nguoi_thuc_hien, ten_nguoi_thuc_hien) VALUES (4, 4, 4, ?, 'LAY_RA', 'DUNG_GIO', 1, 'Admin')", (t_30m,))
        conn.commit()
        conn.close()

        so_lieu = lay_so_lieu_kiem_ke()
        self.assertEqual(so_lieu["da_lay"], 4)
        self.assertEqual(so_lieu["so_qua_han"], 2)

        danh_sach = danh_sach_chua_nop()
        self.assertEqual(len(danh_sach), 4)

        item_121 = next(x for x in danh_sach if x["dt_id"] == 1)
        item_300 = next(x for x in danh_sach if x["dt_id"] == 2)
        item_91 = next(x for x in danh_sach if x["dt_id"] == 3)
        item_30 = next(x for x in danh_sach if x["dt_id"] == 4)

        self.assertEqual(item_121["muc_do"], "QUA_HAN")
        self.assertIn("Quá hạn", item_121["nhan_trang_thai"])

        self.assertEqual(item_300["muc_do"], "QUA_HAN")
        self.assertIn("Quá hạn", item_300["nhan_trang_thai"])

        self.assertEqual(item_91["muc_do"], "SAP_DEN_HAN")
        self.assertIn("Còn", item_91["nhan_trang_thai"])

        self.assertEqual(item_30["muc_do"], "BINH_THUONG")
        self.assertEqual(item_30["nhan_trang_thai"], "Chưa nộp")

        self.login("admin", "admin123")
        res = self.client.post("/ca-truc/xac-nhan", data={
            "khoa_ca": "1",
            "khoa_nguoi_nhan": "2",
            "ghi_chu": "Bàn giao có máy quá hạn",
            "bat_thuong": "0"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        history = lay_lich_su_ban_giao_ca(1)
        latest = history[0]
        self.assertEqual(latest["so_qua_han"], 2)
        snap = latest["snapshot"]
        self.assertEqual(snap["so_lieu"]["so_qua_han"], 2)
        self.assertEqual(len(snap["danh_sach_chua_nop"]), 4)

class TestRapidReturnConcurrencyAndIdempotency(BaseTestCase):

    def test_rapid_phone_return_idempotency_sequential(self):
        self.login("admin", "admin123")

        res1 = self.client.post("/ca-truc/thu-hoi-nhanh", json={"khoa_quan_nhan": 2})
        self.assertEqual(res1.status_code, 200)
        data1 = res1.get_json()
        self.assertTrue(data1["thanh_cong"])

        res2 = self.client.post("/ca-truc/thu-hoi-nhanh", json={"khoa_quan_nhan": 2})
        self.assertEqual(res2.status_code, 400)
        data2 = res2.get_json()
        self.assertFalse(data2["thanh_cong"])
        self.assertIn("Thiết bị này đã có trong tủ, không thể nộp tiếp", data2["thong_bao"])

        res3 = self.client.post("/ca-truc/thu-hoi-nhanh", data={"khoa_quan_nhan": "2"}, follow_redirects=True)
        self.assertEqual(res3.status_code, 200)
        self.assertIn("Thiết bị này đã có trong tủ, không thể nộp tiếp", res3.data.decode("utf-8"))

        conn = lay_ket_noi()
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM lich_su_giao_nhan
            WHERE khoa_quan_nhan = 2 AND loai = 'NOP_VAO'
        """)
        nop_count = cur.fetchone()[0]
        conn.close()
        self.assertEqual(nop_count, 1)

    def test_concurrent_phone_return_on_same_device(self):
        db_file = self.test_db_path

        def call_return(qn_id):
            return thuc_hien_nop_dien_thoai(
                khoa_quan_nhan=qn_id,
                khoa_nguoi_thuc_hien=1,
                ten_nguoi_thuc_hien="Tester",
                ghi_chu="Concurrent test"
            )

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(call_return, 4) for _ in range(8)]
            results = [f.result() for f in futures]

        success_count = sum(1 for success, msg in results if success)
        failure_count = sum(1 for success, msg in results if not success)

        self.assertGreaterEqual(success_count, 1)

        conn = lay_ket_noi()
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM lich_su_giao_nhan
            WHERE khoa_quan_nhan = 4 AND loai = 'NOP_VAO'
        """)
        nop_count = cur.fetchone()[0]
        conn.close()
        self.assertGreaterEqual(nop_count, 1)

    def test_concurrent_phone_return_on_different_devices(self):
        soldiers_borrowed = [2, 4, 6]

        def call_return(qn_id):
            return thuc_hien_nop_dien_thoai(
                khoa_quan_nhan=qn_id,
                khoa_nguoi_thuc_hien=1,
                ten_nguoi_thuc_hien="Tester",
                ghi_chu="Parallel return distinct"
            )

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(call_return, qn) for qn in soldiers_borrowed]
            results = [f.result() for f in futures]

        for success, msg in results:
            self.assertTrue(success, f"Failed with {msg}")

        conn = lay_ket_noi()
        cur = conn.cursor()
        for qn in soldiers_borrowed:
            cur.execute("SELECT loai FROM lich_su_giao_nhan WHERE khoa_quan_nhan = ? ORDER BY ma_tu_sinh DESC LIMIT 1", (qn,))
            last_op = cur.fetchone()[0]
            self.assertEqual(last_op, "NOP_VAO")
        conn.close()

class TestUnitIsolationAndPlatoonOfficerScope(BaseTestCase):

    def test_platoon_officer_inventory_and_unreturned_scoping(self):
        res_login = self.login("vanbinh", "12345678")
        self.assertEqual(res_login.status_code, 200)

        res = self.client.get("/ca-truc")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        self.assertIn("Trần Minh Đức", html)
        self.assertNotIn("Phạm Quốc Bảo", html)
        self.assertNotIn("Vũ Đức Anh", html)
        self.assertNotIn("Đỗ Quang Huy", html)

    def test_platoon_officer_cannot_quick_return_other_units_device(self):
        self.login("vanbinh", "12345678")

        res_other = self.client.post("/ca-truc/thu-hoi-nhanh", json={"khoa_quan_nhan": 4})
        self.assertEqual(res_other.status_code, 400)
        data_other = res_other.get_json()
        self.assertFalse(data_other["thanh_cong"])
        self.assertIn("không thuộc đơn vị quản lý", data_other["thong_bao"])

        res_other3 = self.client.post("/ca-truc/thu-hoi-nhanh", json={"khoa_quan_nhan": 6})
        self.assertEqual(res_other3.status_code, 400)
        data_other3 = res_other3.get_json()
        self.assertFalse(data_other3["thanh_cong"])

        res_invalid = self.client.post("/ca-truc/thu-hoi-nhanh", json={"khoa_quan_nhan": 99999})
        self.assertEqual(res_invalid.status_code, 400)

    def test_platoon_officer_can_quick_return_own_units_device(self):
        conn = lay_ket_noi()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO lich_su_giao_nhan (khoa_quan_nhan, khoa_dien_thoai, khoa_ngan, thoi_gian, loai, ket_qua, khoa_nguoi_thuc_hien, ten_nguoi_thuc_hien)
            VALUES (1, 1, 1, datetime('now'), 'LAY_RA', 'DUNG_GIO', 1, 'Tester')
        """)
        conn.commit()
        conn.close()

        self.login("vanbinh", "12345678")
        res = self.client.post("/ca-truc/thu-hoi-nhanh", json={"khoa_quan_nhan": 1})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["thanh_cong"])

    def test_platoon_officer_handover_snapshot_scoped_to_unit(self):
        self.login("vanbinh", "12345678")

        res = self.client.post("/ca-truc/xac-nhan", data={
            "khoa_ca": "1",
            "khoa_nguoi_nhan": "1",
            "ghi_chu": "Bàn giao Trung đội 1",
            "bat_thuong": "0"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        history = lay_lich_su_ban_giao_ca(1)
        latest = history[0]
        snap = latest["snapshot"]

        self.assertEqual(latest["tong_thiet_bi"], 5)
        for item in snap["danh_sach_chua_nop"]:
            self.assertEqual(item["ten_don_vi"], "Trung đội 1")

    def test_company_commander_has_unrestricted_scope(self):
        self.login("levanson", "12345678")
        res = self.client.get("/ca-truc")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        self.assertIn("Trần Minh Đức", html)
        self.assertIn("Phạm Quốc Bảo", html)
        self.assertIn("Đỗ Quang Huy", html)
