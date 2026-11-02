import os
import json
import unittest
from tests.test_base import BaseTestCase

class TestResponsiveLayoutAndSmallViewports(BaseTestCase):

    def test_viewport_meta_tag_present_on_all_main_pages(self):
        self.login("admin", "admin123")
        routes = [
            "/",
            "/quan-nhan",
            "/dien-thoai",
            "/tu-dien-thoai",
            "/ca-truc",
            "/bao-cao",
            "/cau-hinh-gio"
        ]
        for route in routes:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200, f"Route {route} failed to render 200 OK")
            html = res.data.decode("utf-8")
            self.assertIn('name="viewport"', html, f"Route {route} missing viewport meta tag")
            self.assertIn('content="width=device-width, initial-scale=1.0"', html, f"Route {route} missing standard viewport content")

    def test_responsive_media_queries_exist_in_css(self):
        css_path = os.path.join(os.path.dirname(__file__), "..", "static", "css", "style.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        self.assertIn("@media (max-width: 1024px)", css_content)
        self.assertIn("@media (max-width: 768px)", css_content)
        self.assertIn("@media (max-width: 480px)", css_content)
        self.assertIn(".grid-responsive-2", css_content)
        self.assertIn(".stats-grid", css_content)
        self.assertIn(".locker-grid", css_content)

    def test_mobile_drawer_and_toggle_controllers_rendered(self):
        self.login("admin", "admin123")
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn('id="btnToggleSidebar"', html)
        self.assertIn('id="btnCloseSidebar"', html)
        self.assertIn('id="sidebarOverlay"', html)
        self.assertIn('id="sidebarMenu"', html)

    def test_shift_handover_elements_responsive_classes(self):
        self.login("admin", "admin123")
        res = self.client.get("/ca-truc")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("grid-3-2", html)
        self.assertIn("grid-responsive-2", html)
        self.assertIn("stats-grid", html)
        self.assertIn("stepper", html)
        self.assertIn("modalCanhBaoBanGiao", html)
        self.assertIn("modalChiTietBanGiao", html)

class TestSecurityXSSAndInputStress(BaseTestCase):

    def test_shift_handover_xss_in_notes_stored_and_escaped_in_html(self):
        self.login("admin", "admin123")
        xss_payload = '<script>alert("XSS_HANDOVER")</script><img src=x onerror=alert(1)>'

        conn = self.get_db() if hasattr(self, "get_db") else None
        res_get = self.client.get("/ca-truc")
        self.assertEqual(res_get.status_code, 200)

        post_data = {
            "khoa_ca": "1",
            "khoa_nguoi_nhan": "2",
            "ghi_chu": xss_payload,
            "chk_kiem_dem": "1",
            "chk_khoa": "1",
            "chk_chia_khoa": "1",
            "chk_cam_ket": "1",
            "bat_thuong": "0"
        }
        res_post = self.client.post("/ca-truc/xac-nhan", data=post_data, follow_redirects=True)
        self.assertEqual(res_post.status_code, 200)
        html = res_post.data.decode("utf-8")

        hash_char = chr(35)
        expected_esc = "&lt;script&gt;alert(&" + hash_char + "34;XSS_HANDOVER&" + hash_char + "34;)&lt;/script&gt;"
        self.assertIn(expected_esc, html)

    def test_shift_handover_xss_in_notes_escaped_in_a4_bien_ban(self):
        self.login("admin", "admin123")
        xss_payload = '<script>alert("XSS_A4")</script><svg onload=alert(2)>'
        post_data = {
            "khoa_ca": "1",
            "khoa_nguoi_nhan": "2",
            "ghi_chu": xss_payload,
            "chk_kiem_dem": "1",
            "chk_khoa": "1",
            "chk_chia_khoa": "1",
            "chk_cam_ket": "1",
            "bat_thuong": "0",
            "in_bien_ban": "1"
        }
        res_post = self.client.post("/ca-truc/xac-nhan", data=post_data, follow_redirects=True)
        self.assertEqual(res_post.status_code, 200)
        html = res_post.data.decode("utf-8")
        hash_char = chr(35)
        expected_esc = "&lt;script&gt;alert(&" + hash_char + "34;XSS_A4&" + hash_char + "34;)&lt;/script&gt;"
        self.assertNotIn(xss_payload, html)
        self.assertIn(expected_esc, html)

    def test_shift_handover_detail_api_returns_raw_json_requiring_client_sanitization(self):
        self.login("admin", "admin123")
        xss_payload = '<img src=x onerror="alert(\'DOM_XSS\')">'
        post_data = {
            "khoa_ca": "1",
            "khoa_nguoi_nhan": "2",
            "ghi_chu": xss_payload,
            "chk_kiem_dem": "1",
            "chk_khoa": "1",
            "chk_chia_khoa": "1",
            "chk_cam_ket": "1",
            "bat_thuong": "0"
        }
        res_post = self.client.post("/ca-truc/xac-nhan", data=post_data, follow_redirects=False)
        self.assertEqual(res_post.status_code, 302)

        from models.ca_truc_model import lay_lich_su_ban_giao_ca
        lich_su = lay_lich_su_ban_giao_ca(1)
        self.assertTrue(len(lich_su) > 0)
        ma_bg = lich_su[0]["ma_tu_sinh"]

        res_api = self.client.get(f"/ca-truc/api/chi-tiet/{ma_bg}")
        self.assertEqual(res_api.status_code, 200)
        api_data = res_api.get_json()
        self.assertTrue(api_data["thanh_cong"])
        self.assertEqual(api_data["ban_giao"]["ghi_chu_ban_giao"], xss_payload)

        js_path = os.path.join(os.path.dirname(__file__), "..", "static", "js", "app.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js_code = f.read()
        self.assertIn("truyenAnToan", js_code)
        self.assertNotIn("${bg.ghi_chu_ban_giao}", js_code)

    def test_shift_handover_unicode_and_emoji_stress(self):
        self.login("admin", "admin123")
        unicode_payload = "Đồng chí Tuấn Anh bàn giao ca đêm: 🛡️📱 100% quân số đã nộp máy! (Cần kiểm tra tem niêm phong \u202E RTL_TEST \u202C & < > ' \")"

        post_data = {
            "khoa_ca": "1",
            "khoa_nguoi_nhan": "2",
            "ghi_chu": unicode_payload,
            "chk_kiem_dem": "1",
            "chk_khoa": "1",
            "chk_chia_khoa": "1",
            "chk_cam_ket": "1",
            "bat_thuong": "0"
        }
        res_post = self.client.post("/ca-truc/xac-nhan", data=post_data, follow_redirects=True)
        self.assertEqual(res_post.status_code, 200)

        from models.ca_truc_model import lay_lich_su_ban_giao_ca
        lich_su = lay_lich_su_ban_giao_ca(1)
        record = lich_su[0]
        self.assertEqual(record["ghi_chu_ban_giao"], unicode_payload)
        self.assertIsNotNone(record.get("snapshot"))
        self.assertEqual(record["snapshot"].get("ghi_chu"), unicode_payload)

    def test_shift_handover_very_long_string_stress(self):
        self.login("admin", "admin123")
        long_notes = "GHI_CHU_DAI_" + ("A" * 10000)

        post_data = {
            "khoa_ca": "1",
            "khoa_nguoi_nhan": "2",
            "ghi_chu": long_notes,
            "chk_kiem_dem": "1",
            "chk_khoa": "1",
            "chk_chia_khoa": "1",
            "chk_cam_ket": "1",
            "bat_thuong": "0"
        }
        res_post = self.client.post("/ca-truc/xac-nhan", data=post_data, follow_redirects=True)
        self.assertEqual(res_post.status_code, 200)

        from models.ca_truc_model import lay_lich_su_ban_giao_ca
        lich_su = lay_lich_su_ban_giao_ca(1)
        self.assertEqual(lich_su[0]["ghi_chu_ban_giao"], long_notes)

    def test_personnel_edit_empty_whitespace_ho_ten_causes_500_bug(self):
        self.login("admin", "admin123")
        res_post = self.client.post("/quan-nhan/sua/2", data={"ho_ten": "   ", "khoa_cap_bac": "1", "khoa_chuc_vu": "1", "khoa_don_vi": "2"}, follow_redirects=True)
        self.assertEqual(res_post.status_code, 200)
        self.assertIn("Họ và tên quân nhân không được để trống.", res_post.data.decode("utf-8"))
        res_get = self.client.get("/quan-nhan/chi-tiet/2")
        self.assertEqual(res_get.status_code, 200)

    def test_personnel_edit_xss_and_unicode_handling(self):
        self.login("admin", "admin123")
        xss_name = 'Nguyen Van <script>alert("XSS_PERSON")</script>'
        unicode_notes = 'Ghi chú quân nhân đặc biệt: 🛡️ ⭐ Quân nhân mẫu mực xuất sắc C1-T1'
        res = self.client.post(
            "/quan-nhan/sua/2",
            data={
                "ho_ten": xss_name,
                "khoa_cap_bac": "1",
                "khoa_chuc_vu": "1",
                "khoa_don_vi": "2",
                "ghi_chu": unicode_notes
            },
            follow_redirects=True
        )
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        hash_char = chr(35)
        expected_esc = "&lt;script&gt;alert(&" + hash_char + "34;XSS_PERSON&" + hash_char + "34;)&lt;/script&gt;"
        self.assertNotIn('<script>alert("XSS_PERSON")</script>', html)
        self.assertIn(expected_esc, html)
        self.assertIn("Quân nhân mẫu mực xuất sắc C1-T1", html)

class TestUnauthorizedAccessAndRBAC(BaseTestCase):

    def test_unauthenticated_access_to_all_handover_endpoints(self):
        routes = [
            ("GET", "/ca-truc"),
            ("POST", "/ca-truc/xac-nhan"),
            ("GET", "/ca-truc/bien-ban/1"),
            ("GET", "/ca-truc/api/chi-tiet/1"),
            ("POST", "/ca-truc/thu-hoi-nhanh")
        ]
        for method, route in routes:
            if method == "GET":
                res = self.client.get(route)
            else:
                res = self.client.post(route)
            self.assertEqual(res.status_code, 302, f"Endpoint {route} should redirect unauthenticated request")
            self.assertIn("/dang-nhap", res.headers.get("Location", ""))

    def test_authenticated_user_without_catruc_permission_denied(self):
        import models.co_so_du_lieu as db
        from werkzeug.security import generate_password_hash
        conn = db.lay_ket_noi()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tai_khoan (ten_dang_nhap, mat_khau_ma_hoa, ho_ten) VALUES ('soliertest', ?, 'Chien Si Test')",
            (generate_password_hash("pass123"),)
        )
        new_uid = cur.lastrowid
        cur.execute("SELECT ma_tu_sinh FROM vai_tro WHERE ma_vai_tro = 'QUAN_NHAN'")
        role_qn = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO tai_khoan_vai_tro (khoa_tai_khoan, khoa_vai_tro, pham_vi_loai, hieu_luc_tu) VALUES (?, ?, 'TOAN_BO', '2026-01-01')",
            (new_uid, role_qn)
        )
        conn.commit()
        conn.close()

        self.login("soliertest", "pass123")

        res_main = self.client.get("/ca-truc")
        self.assertEqual(res_main.status_code, 302)
        self.assertIn(res_main.headers.get("Location"), ["/tong-quan", "/"])

        res_submit = self.client.post("/ca-truc/xac-nhan", data={"khoa_ca": "1", "khoa_nguoi_nhan": "2"})
        self.assertEqual(res_submit.status_code, 302)
        self.assertIn(res_submit.headers.get("Location"), ["/tong-quan", "/"])

        res_bb = self.client.get("/ca-truc/bien-ban/1")
        self.assertEqual(res_bb.status_code, 302)
        self.assertIn(res_bb.headers.get("Location"), ["/tong-quan", "/"])

        res_api = self.client.get("/ca-truc/api/chi-tiet/1")
        self.assertEqual(res_api.status_code, 302)
        self.assertIn(res_api.headers.get("Location"), ["/tong-quan", "/"])

        res_api_json = self.client.get("/ca-truc/api/chi-tiet/1", headers={"Content-Type": "application/json"})
        self.assertEqual(res_api_json.status_code, 403)

        res_nop = self.client.post("/ca-truc/thu-hoi-nhanh", json={"khoa_quan_nhan": 1})
        self.assertEqual(res_nop.status_code, 403)

    def test_cross_unit_quick_return_rejected(self):
        self.login("vanbinh", "12345678")

        import models.co_so_du_lieu as db
        conn = db.lay_ket_noi()
        cur = conn.cursor()
        cur.execute("SELECT ma_tu_sinh, khoa_don_vi FROM quan_nhan WHERE ma_quan_nhan = 'QN004'")
        qn_outside = cur.fetchone()
        conn.close()

        outside_qn_id = qn_outside[0]
        res_nop = self.client.post(
            "/ca-truc/thu-hoi-nhanh",
            json={"khoa_quan_nhan": outside_qn_id}
        )
        self.assertEqual(res_nop.status_code, 400)
        data = res_nop.get_json()
        self.assertFalse(data["thanh_cong"])
        self.assertIn("không thuộc đơn vị quản lý", data["thong_bao"])

class TestZeroClientSideDOMScraping(BaseTestCase):

    def test_no_dom_parser_or_screen_scraping_in_javascript(self):
        js_path = os.path.join(os.path.dirname(__file__), "..", "static", "js", "app.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js_code = f.read()

        self.assertNotIn("DOMParser", js_code)
        self.assertNotIn("/chua-nop", js_code)
        self.assertNotIn("taiDanhSachChuaNopCaTruc", js_code)
        self.assertNotIn("kiemTraNganQuaHan", js_code)

    def test_handover_unreturned_devices_rendered_server_side_jinja2(self):
        self.login("admin", "admin123")
        res = self.client.get("/ca-truc")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        self.assertIn("tbodyChuaNopTrucBan", html)
        self.assertIn("danhSachChuaNopTrucBan", html)
        self.assertIn("thuHoiNhanhCaTruc", html)
        self.assertIn("badge-pulse", html)

if __name__ == "__main__":
    unittest.main()
