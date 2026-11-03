import os
import re
import tokenize
from html.parser import HTMLParser
from tests.test_base import BaseTestCase

class Milestone6ChallengerTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.css_path = os.path.join(self.root_dir, "static", "css", "style.css")
        self.js_path = os.path.join(self.root_dir, "static", "js", "app.js")
        self.base_html_path = os.path.join(self.root_dir, "templates", "base.html")

    def test_adv_01_sidebar_css_fixed_and_independent_scroll(self):
        with open(self.css_path, "r", encoding="utf-8") as f:
            css = f.read()
        self.assertIn(".sidebar", css)
        self.assertIn("position: fixed;", css)
        self.assertIn("top: 0;", css)
        self.assertIn("left: 0;", css)
        self.assertIn("bottom: 0;", css)
        self.assertIn("width: 260px;", css)
        self.assertIn("height: 100vh;", css)
        self.assertIn("overflow: hidden;", css)
        self.assertIn(".sidebar-nav", css)
        self.assertIn("overflow-y: auto;", css)
        self.assertIn("overflow-x: hidden;", css)
        self.assertIn("flex: 1;", css)
        self.assertIn(".main-content", css)
        self.assertIn("margin-left: 260px;", css)
        self.assertIn("width: calc(100% - 260px);", css)
        self.assertIn("min-height: 100vh;", css)

    def test_adv_02_responsive_drawer_rules_below_1024(self):
        with open(self.css_path, "r", encoding="utf-8") as f:
            css = f.read()
        self.assertIn("@media (max-width: 1024px)", css)
        mq_start = css.find("@media (max-width: 1024px)")
        mq_block = css[mq_start:mq_start + 1200]
        self.assertIn(".btn-sidebar-toggle", mq_block)
        self.assertIn("display: inline-flex;", mq_block)
        self.assertIn(".btn-sidebar-close", mq_block)
        self.assertIn(".sidebar", mq_block)
        self.assertIn("transform: translateX(-100%);", mq_block)
        self.assertIn("width: 280px;", mq_block)
        self.assertIn("max-width: 85vw;", mq_block)
        self.assertIn("z-index: 1000;", mq_block)
        self.assertIn(".sidebar.is-open", mq_block)
        self.assertIn("transform: translateX(0);", mq_block)
        self.assertIn(".sidebar-overlay.is-open", mq_block)
        self.assertIn("display: block;", mq_block)
        self.assertIn("opacity: 1;", mq_block)
        self.assertIn(".main-content", mq_block)
        self.assertIn("margin-left: 0;", mq_block)
        self.assertIn("width: 100%;", mq_block)

    def test_adv_03_print_rules_cleanliness(self):
        with open(self.css_path, "r", encoding="utf-8") as f:
            css = f.read()
        self.assertIn("@media print", css)
        p_start = css.find("@media print")
        p_block = css[p_start:p_start + 500]
        self.assertIn(".sidebar", p_block)
        self.assertIn(".topbar", p_block)
        self.assertIn(".no-print", p_block)
        self.assertIn(".btn-sidebar-toggle", p_block)
        self.assertIn(".btn-sidebar-close", p_block)
        self.assertIn(".sidebar-overlay", p_block)
        self.assertIn(".btn-quan-doi", p_block)
        self.assertIn("display: none !important;", p_block)
        self.assertIn(".main-content { margin: 0; width: 100%; }", p_block)

    def test_adv_04_military_button_system_spec(self):
        with open(self.css_path, "r", encoding="utf-8") as f:
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
        self.assertIn("transform: translateY(-1px);", css)
        self.assertIn("transform: translateY(0);", css)

    def test_adv_05_all_17_templates_action_buttons_military_conformance(self):
        class ButtonCollector(HTMLParser):
            def __init__(self):
                super().__init__()
                self.buttons = []
            def handle_starttag(self, tag, attrs):
                attr_dict = dict(attrs)
                classes = attr_dict.get("class", "").split()
                b_id = attr_dict.get("id", "")
                if tag == "button":
                    self.buttons.append((tag, b_id, classes, attr_dict))
                elif tag == "a" and any("btn" in c for c in classes):
                    self.buttons.append((tag, b_id, classes, attr_dict))
                elif tag == "input" and attr_dict.get("type") in ["submit", "button"]:
                    self.buttons.append((tag, b_id, classes, attr_dict))

        tpl_dir = os.path.join(self.root_dir, "templates")
        all_templates = []
        for root, _, files in os.walk(tpl_dir):
            for file in files:
                if file.endswith(".html") and file != "bien_ban.html":
                    all_templates.append(os.path.join(root, file))

        self.assertGreaterEqual(len(all_templates), 16)

        total_action_buttons = 0
        for tpath in all_templates:
            rel = os.path.relpath(tpath, self.root_dir)
            with open(tpath, "r", encoding="utf-8") as f:
                content = f.read()
            cleaned = re.sub(r"\{\{.*?\}\}", "EXPR", content)
            cleaned = re.sub(r"\{%.*?%\}", "", cleaned)
            parser = ButtonCollector()
            parser.feed(cleaned)
            for tag, b_id, classes, attrs in parser.buttons:
                if b_id in ["btnToggleSidebar", "btnCloseSidebar"]:
                    continue
                if "modal-close" in classes or "btn-loc-don-vi" in classes:
                    continue
                total_action_buttons += 1
                self.assertIn("btn-quan-doi", classes, f"Missing btn-quan-doi on {tag} in {rel}")
                has_variant = any(c.startswith("btn-qd-") for c in classes)
                self.assertTrue(has_variant, f"Missing btn-qd-* variant on {tag} in {rel} (classes: {classes})")

        self.assertGreaterEqual(total_action_buttons, 60)

    def test_adv_06_rendered_endpoints_contain_ui_contracts(self):
        self.login("admin", "admin123")
        endpoints = [
            "/tong-quan",
            "/giao-nhan",
            "/chua-nop",
            "/lich-su",
            "/phan-doi",
            "/quan-nhan",
            "/dien-thoai",
            "/tu-dien-thoai",
            "/cau-hinh-gio",
            "/tai-khoan-phan-quyen",
            "/bao-cao",
        ]
        for ep in endpoints:
            res = self.client.get(ep)
            self.assertEqual(res.status_code, 200, f"Endpoint {ep} failed with {res.status_code}")
            html = res.data.decode("utf-8")
            self.assertIn('id="sidebarMenu"', html, f"{ep} missing sidebarMenu")
            self.assertIn('id="btnToggleSidebar"', html, f"{ep} missing btnToggleSidebar")
            self.assertIn('id="btnCloseSidebar"', html, f"{ep} missing btnCloseSidebar")
            self.assertIn('id="sidebarOverlay"', html, f"{ep} missing sidebarOverlay")
            self.assertIn("btn-quan-doi", html, f"{ep} missing btn-quan-doi")

        res_a4 = self.client.get("/bao-cao/in-a4")
        self.assertEqual(res_a4.status_code, 200)
        html_a4 = res_a4.data.decode("utf-8")
        self.assertIn("print-toolbar no-print", html_a4)
        self.assertIn("btn-in-ngay", html_a4)
        self.assertIn("btn-quan-doi btn-qd-primary", html_a4)
        self.assertIn("btn-quay-lai", html_a4)
        self.assertIn("window.print()", html_a4)

    def test_adv_07_javascript_event_handlers_and_resilience(self):
        with open(self.js_path, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertIn("function khoiTaoSidebarResponsive()", js)
        self.assertIn("btnToggle.addEventListener", js)
        self.assertIn("btnClose.addEventListener", js)
        self.assertIn("overlay.addEventListener", js)
        self.assertIn("window.addEventListener(\"keydown\"", js)
        self.assertIn("window.addEventListener(\"resize\"", js)
        self.assertIn("sidebar.classList.add(\"is-open\")", js)
        self.assertIn("sidebar.classList.remove(\"is-open\")", js)
        self.assertIn("overlay.classList.add(\"is-open\")", js)
        self.assertIn("overlay.classList.remove(\"is-open\")", js)
        self.assertIn("document.body.style.overflow = \"hidden\"", js)
        self.assertIn("document.body.style.overflow = \"\"", js)
        self.assertIn("if (btnToggle)", js)
        self.assertIn("if (btnClose)", js)
        self.assertIn("if (overlay)", js)
        self.assertIn("if (sidebar)", js)

    def test_adv_08_strict_zero_comments_across_entire_repo(self):
        for root, dirs, files in os.walk(self.root_dir):
            if any(skip in root for skip in [".git", ".agents", "__pycache__", ".gemini"]):
                continue
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                fpath = os.path.join(root, file)
                if ext == ".py":
                    with open(fpath, "rb") as fp:
                        try:
                            tokens = tokenize.tokenize(fp.readline)
                            for toknum, tokval, (srow, _), _, _ in tokens:
                                if toknum == tokenize.COMMENT:
                                    self.fail(f"Python comment found in {fpath}:{srow} -> {tokval}")
                        except Exception:
                            pass
                elif ext == ".css":
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                        for lno, line in enumerate(fp, 1):
                            if "/*" in line:
                                self.fail(f"CSS comment found in {fpath}:{lno} -> {line.strip()}")
                elif ext == ".js":
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                        for lno, line in enumerate(fp, 1):
                            s = line.strip()
                            if s.startswith("//") or "/*" in s:
                                self.fail(f"JS comment found in {fpath}:{lno} -> {line.strip()}")
                elif ext == ".html":
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                        for lno, line in enumerate(fp, 1):
                            if "<!--" in line:
                                self.fail(f"HTML comment found in {fpath}:{lno} -> {line.strip()}")
                            if "{#" in line:
                                self.fail(f"Jinja comment found in {fpath}:{lno} -> {line.strip()}")
