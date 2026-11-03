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
            "/chua-nop",
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

    def test_unreturned_elements_responsive_classes(self):
        self.login("admin", "admin123")
        res = self.client.get("/chua-nop")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("panel", html)
        self.assertIn("table-responsive", html)

class TestSecurityXSSAndInputStress(BaseTestCase):

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
            ("GET", "/chua-nop"),
            ("GET", "/lich-su"),
            ("GET", "/giao-nhan"),
            ("POST", "/giao-nhan/lay"),
            ("POST", "/giao-nhan/nop")
        ]
        for method, route in routes:
            if method == "GET":
                res = self.client.get(route)
            else:
                res = self.client.post(route)
            self.assertEqual(res.status_code, 302, f"Endpoint {route} should redirect unauthenticated request")
            self.assertIn("/dang-nhap", res.headers.get("Location", ""))

    def test_authenticated_user_without_permission_denied(self):
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

        res_main = self.client.get("/cau-hinh-gio")
        self.assertEqual(res_main.status_code, 302)
        self.assertIn(res_main.headers.get("Location"), ["/tong-quan", "/"])

    def test_cross_unit_personnel_isolation(self):
        self.login("vanbinh", "12345678")
        res = self.client.get("/quan-nhan")
        self.assertEqual(res.status_code, 200)
        self.assertNotIn("Lê Hoàng Nam".encode("utf-8"), res.data)

class TestZeroClientSideDOMScraping(BaseTestCase):

    def test_no_dom_parser_or_screen_scraping_in_javascript(self):
        js_path = os.path.join(os.path.dirname(__file__), "..", "static", "js", "app.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js_code = f.read()

        self.assertNotIn("DOMParser", js_code)
        self.assertNotIn("taiDanhSachChuaNopCaTruc", js_code)
        self.assertNotIn("kiemTraNganQuaHan", js_code)

    def test_unreturned_devices_rendered_server_side_jinja2(self):
        self.login("admin", "admin123")
        res = self.client.get("/chua-nop")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("table-responsive", html)

if __name__ == "__main__":
    unittest.main()
