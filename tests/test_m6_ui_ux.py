import os
import re
from tests.test_base import BaseTestCase

class Milestone6UIUXTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def test_m6_01_fixed_sidebar_css_rules(self):
        css_path = os.path.join(self.root_dir, "static", "css", "style.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
        self.assertIn(".sidebar", css)
        self.assertIn("height: 100vh;", css)
        self.assertIn("position: fixed;", css)
        self.assertIn("margin-left: 260px;", css)
        self.assertIn("width: calc(100% - 260px);", css)
        self.assertIn("scrollbar-width: thin;", css)

    def test_m6_02_responsive_offcanvas_css_rules(self):
        css_path = os.path.join(self.root_dir, "static", "css", "style.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
        self.assertIn("@media (max-width: 1024px)", css)
        self.assertIn(".btn-sidebar-toggle", css)
        self.assertIn(".btn-sidebar-close", css)
        self.assertIn(".sidebar-overlay", css)
        self.assertIn("transform: translateX(-100%);", css)
        self.assertIn("transform: translateX(0);", css)

    def test_m6_03_military_button_system_classes(self):
        css_path = os.path.join(self.root_dir, "static", "css", "style.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
        self.assertIn(".btn, .btn-quan-doi", css)
        self.assertIn("border-radius: 6px !important;", css)
        self.assertIn(".btn-primary, .btn-qd-primary", css)
        self.assertIn(".btn-secondary, .btn-qd-secondary", css)
        self.assertIn(".btn-success, .btn-qd-success", css)
        self.assertIn(".btn-warning, .btn-qd-warning", css)
        self.assertIn(".btn-danger, .btn-qd-danger", css)
        self.assertIn(".btn-ghost, .btn-qd-ghost", css)
        self.assertIn(".btn-qd-sm", css)
        self.assertIn(".btn-qd-md", css)
        self.assertIn(".btn-qd-lg", css)
        self.assertIn(".btn-qd-block", css)

    def test_m6_04_base_html_structure(self):
        self.login("admin", "admin123")
        res = self.client.get("/tong-quan")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn('id="sidebarMenu"', html)
        self.assertIn('id="btnToggleSidebar"', html)
        self.assertIn('id="btnCloseSidebar"', html)
        self.assertIn('id="sidebarOverlay"', html)
        self.assertIn("btn-quan-doi btn-qd-secondary btn-qd-sm", html)

    def test_m6_05_javascript_sidebar_toggle(self):
        js_path = os.path.join(self.root_dir, "static", "js", "app.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertIn("khoiTaoSidebarResponsive", js)
        self.assertIn("btnToggleSidebar", js)
        self.assertIn("btnCloseSidebar", js)
        self.assertIn("sidebarOverlay", js)
        self.assertIn("Escape", js)
        self.assertIn("resize", js)

    def test_m6_06_all_17_templates_adopt_military_button_classes(self):
        templates = [
            "base.html",
            "auth/login.html",
            "bao_cao/in_a4.html",
            "bao_cao/index.html",
            "ca_truc/index.html",
            "cau_hinh/khung_gio.html",
            "cau_hinh/phan_quyen.html",
            "chua_nop/index.html",
            "dashboard/index.html",
            "dien_thoai/chi_tiet.html",
            "dien_thoai/index.html",
            "dien_thoai/so_do_tu.html",
            "dien_thoai/tu.html",
            "giao_nhan/index.html",
            "giao_nhan/lich_su.html",
            "quan_nhan/chi_tiet.html",
            "quan_nhan/index.html",
        ]
        for tpl in templates:
            t_path = os.path.join(self.root_dir, "templates", tpl)
            self.assertTrue(os.path.exists(t_path), f"Missing template: {tpl}")
            with open(t_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertTrue(
                "btn-quan-doi" in content or "btn-in-ngay" in content,
                f"Template {tpl} does not contain military button class"
            )

    def test_m6_07_zero_comments_in_all_m6_files(self):
        files_to_check = [
            os.path.join(self.root_dir, "static", "css", "style.css"),
            os.path.join(self.root_dir, "static", "js", "app.js"),
            os.path.join(self.root_dir, "templates", "base.html"),
            os.path.abspath(__file__),
        ]
        block_comment_start = "/" + "*"
        for fpath in files_to_check:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            if fpath.endswith(".css") or fpath.endswith(".js"):
                self.assertNotIn(block_comment_start, content, f"CSS/JS block comment found in {fpath}")
            if fpath.endswith(".html"):
                self.assertNotIn("<!" + "--", content, f"HTML comment found in {fpath}")
            for idx, line in enumerate(content.splitlines(), 1):
                stripped = line.strip()
                if fpath.endswith(".js"):
                    self.assertFalse(stripped.startswith("//"), f"JS comment found in {fpath}:{idx}")
                elif fpath.endswith(".py") and stripped.startswith("#"):
                    self.fail(f"Python comment found in {fpath}:{idx}")
