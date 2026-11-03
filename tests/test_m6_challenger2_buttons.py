import os
import re
import unittest
from html.parser import HTMLParser
from jinja2 import Environment, FileSystemLoader
from tests.test_base import BaseTestCase

class TemplateHTMLAuditor(HTMLParser):
    SELF_CLOSING = {'img', 'input', 'br', 'hr', 'meta', 'link', 'col', 'base'}

    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.buttons = []
        self.tag_stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        classes_str = attr_dict.get('class', '')
        classes = classes_str.split()
        
        is_button_tag = (tag == 'button')
        is_btn_anchor = (tag == 'a' and any('btn' in c for c in classes))
        is_btn_input = (tag == 'input' and attr_dict.get('type') in ['submit', 'button'])
        
        if is_button_tag or is_btn_anchor or is_btn_input:
            self.buttons.append({
                'tag': tag,
                'pos': self.getpos(),
                'classes': classes,
                'attrs': attr_dict
            })
            
        if tag not in self.SELF_CLOSING:
            self.tag_stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in self.SELF_CLOSING:
            return
        if not self.tag_stack:
            self.errors.append(f"Unexpected closing tag </{tag}> at line {self.getpos()[0]} in {self.filename}")
            return
        last_tag, pos = self.tag_stack[-1]
        if last_tag == tag:
            self.tag_stack.pop()
        else:
            found_idx = -1
            for idx in range(len(self.tag_stack) - 1, -1, -1):
                if self.tag_stack[idx][0] == tag:
                    found_idx = idx
                    break
            if found_idx != -1:
                self.tag_stack = self.tag_stack[:found_idx]
            else:
                self.errors.append(f"Closing tag </{tag}> at line {self.getpos()[0]} has no matching start tag in {self.filename}")

class TestMilestone6Challenger2(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.templates_dir = os.path.join(self.root_dir, "templates")
        self.css_path = os.path.join(self.root_dir, "static", "css", "style.css")
        self.all_templates = [
            "auth/login.html",
            "bao_cao/in_a4.html",
            "bao_cao/index.html",
            "base.html",
            "cau_hinh/phan_doi.html",
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

    def test_css_military_button_system_rules(self):
        with open(self.css_path, "r", encoding="utf-8") as f:
            css = f.read()

        self.assertIn(".btn, .btn-quan-doi", css)
        self.assertIn("border-radius: 6px !important;", css)
        self.assertIn("padding: 9px 16px;", css)
        self.assertIn("font-weight: 600;", css)
        self.assertIn("white-space: nowrap;", css)

        self.assertIn(".btn-primary, .btn-qd-primary", css)
        self.assertIn("#1e4b7b", css)
        self.assertIn("#173653", css)

        self.assertIn(".btn-secondary, .btn-qd-secondary", css)
        self.assertIn("#cbd5e1", css)

        self.assertIn(".btn-success, .btn-qd-success", css)
        self.assertIn("#15803d", css)
        self.assertIn("#166534", css)

        self.assertIn(".btn-warning, .btn-qd-warning", css)
        self.assertIn("#d97706", css)
        self.assertIn("#b45309", css)

        self.assertIn(".btn-danger, .btn-qd-danger", css)
        self.assertIn("#dc2626", css)
        self.assertIn("#b91c1c", css)

        self.assertIn(".btn-ghost, .btn-qd-ghost", css)

        self.assertIn(".btn-qd-sm", css)
        self.assertIn("padding: 5px 10px;", css)
        self.assertIn("font-size: 11px;", css)

        self.assertIn(".btn-qd-md", css)
        self.assertIn("padding: 9px 16px;", css)
        self.assertIn("font-size: 12.5px;", css)

        self.assertIn(".btn-qd-lg", css)
        self.assertIn("padding: 12px 20px;", css)
        self.assertIn("font-size: 13.5px;", css)

        self.assertIn(".btn-qd-block", css)
        self.assertIn("width: 100%;", css)

        self.assertIn("transform: translateY(-1px);", css)

    def test_all_17_templates_exist(self):
        self.assertEqual(len(self.all_templates), 17)
        for tpl in self.all_templates:
            tpl_path = os.path.join(self.templates_dir, tpl)
            self.assertTrue(os.path.isfile(tpl_path), f"Template not found: {tpl_path}")

    def test_html_tag_balance_and_syntax(self):
        for tpl in self.all_templates:
            tpl_path = os.path.join(self.templates_dir, tpl)
            with open(tpl_path, "r", encoding="utf-8") as f:
                content = f.read()

            clean_content = re.sub(r'\{%.*?%\}', ' ', content, flags=re.DOTALL)
            clean_content = re.sub(r'\{\{.*?\}\}', ' PH ', clean_content, flags=re.DOTALL)
            clean_content = re.sub(r'\{#.*?#\}', ' ', clean_content, flags=re.DOTALL)

            parser = TemplateHTMLAuditor(tpl)
            parser.feed(clean_content)

            self.assertEqual(len(parser.errors), 0, f"HTML errors in {tpl}: {parser.errors}")

    def test_button_standardization_across_all_templates(self):
        special_control_classes = {
            'btn-sidebar-toggle', 'btn-sidebar-close', 'modal-close', 'btn-close-modal', 'btn-loc-don-vi'
        }
        valid_variants = {
            'btn-qd-primary', 'btn-qd-secondary', 'btn-qd-success',
            'btn-qd-warning', 'btn-qd-danger', 'btn-qd-ghost',
            'btn-primary', 'btn-secondary', 'btn-success',
            'btn-warning', 'btn-danger', 'btn-ghost'
        }

        total_buttons_found = 0
        variant_distribution = {
            'primary': 0, 'secondary': 0, 'success': 0,
            'warning': 0, 'danger': 0, 'ghost': 0, 'controls': 0
        }

        for tpl in self.all_templates:
            tpl_path = os.path.join(self.templates_dir, tpl)
            with open(tpl_path, "r", encoding="utf-8") as f:
                content = f.read()

            clean_content = re.sub(r'\{%.*?%\}', ' ', content, flags=re.DOTALL)
            clean_content = re.sub(r'\{\{.*?\}\}', ' PH ', clean_content, flags=re.DOTALL)
            clean_content = re.sub(r'\{#.*?#\}', ' ', clean_content, flags=re.DOTALL)

            parser = TemplateHTMLAuditor(tpl)
            parser.feed(clean_content)

            for btn in parser.buttons:
                total_buttons_found += 1
                tag = btn['tag']
                classes = btn['classes']
                attrs = btn['attrs']
                line = btn['pos'][0]

                is_control = any(c in special_control_classes for c in classes)

                if is_control:
                    variant_distribution['controls'] += 1
                else:
                    has_military_base = (
                        'btn-quan-doi' in classes or 
                        'btn' in classes or 
                        'btn-in-ngay' in classes or 
                        'btn-quay-lai' in classes
                    )
                    self.assertTrue(
                        has_military_base, 
                        f"Action button at {tpl}:{line} (<{tag} class='{' '.join(classes)}'>) lacks standard button class"
                    )

                    has_variant = any(c in valid_variants for c in classes)
                    self.assertTrue(
                        has_variant,
                        f"Action button at {tpl}:{line} (<{tag} class='{' '.join(classes)}'>) lacks recognized variant class"
                    )

                    for c in classes:
                        if 'primary' in c:
                            variant_distribution['primary'] += 1
                        elif 'secondary' in c:
                            variant_distribution['secondary'] += 1
                        elif 'success' in c:
                            variant_distribution['success'] += 1
                        elif 'warning' in c:
                            variant_distribution['warning'] += 1
                        elif 'danger' in c:
                            variant_distribution['danger'] += 1
                        elif 'ghost' in c:
                            variant_distribution['ghost'] += 1

                style = attrs.get('style', '')
                if 'border-radius' in style:
                    self.assertIn(
                        '6px', style,
                        f"Button at {tpl}:{line} overrides border-radius to non-6px: {style}"
                    )

        self.assertGreater(total_buttons_found, 40, "Too few buttons found across templates")
        self.assertGreater(variant_distribution['primary'], 0)
        self.assertGreater(variant_distribution['secondary'], 0)
        self.assertGreater(variant_distribution['success'], 0)
        self.assertGreater(variant_distribution['warning'], 0)
        self.assertGreater(variant_distribution['danger'], 0)

    def test_size_variations_usage(self):
        sm_count = 0
        md_count = 0
        lg_count = 0
        block_count = 0

        for tpl in self.all_templates:
            tpl_path = os.path.join(self.templates_dir, tpl)
            with open(tpl_path, "r", encoding="utf-8") as f:
                content = f.read()

            sm_count += len(re.findall(r'btn-qd-sm\b', content))
            md_count += len(re.findall(r'btn-qd-md\b', content))
            lg_count += len(re.findall(r'btn-qd-lg\b', content))
            block_count += len(re.findall(r'btn-qd-block\b', content))

        self.assertGreater(sm_count, 5, "Small buttons should be used for compact actions")
        self.assertGreater(lg_count, 3, "Large buttons should be used for primary call-to-actions")
        self.assertGreater(block_count, 3, "Block buttons should be used for full-width forms")

    def test_jinja2_template_compilation_all_17(self):
        env = Environment(loader=FileSystemLoader(self.templates_dir))
        for tpl in self.all_templates:
            try:
                template = env.get_template(tpl)
                self.assertIsNotNone(template)
            except Exception as e:
                self.fail(f"Jinja compilation failed for {tpl}: {e}")

    def test_rendered_views_contain_military_buttons(self):
        self.login("admin", "admin123")
        routes_to_test = [
            "/tong-quan",
            "/giao-nhan",
            "/chua-nop",
            "/lich-su",
            "/quan-nhan",
            "/dien-thoai",
            "/tu-dien-thoai",
            "/phan-doi",
            "/cau-hinh-gio",
            "/tai-khoan-phan-quyen",
            "/bao-cao"
        ]
        for route in routes_to_test:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200, f"Route {route} failed with status {res.status_code}")
            html = res.data.decode("utf-8")
            self.assertIn("btn-quan-doi", html, f"Route {route} does not render any military buttons")
            self.assertNotIn("undefined", html)
            self.assertNotIn("None", html)

    def test_no_comments_in_all_templates_and_css(self):
        for tpl in self.all_templates:
            tpl_path = os.path.join(self.templates_dir, tpl)
            with open(tpl_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertNotIn("<!" + "--", content, f"HTML comment found in {tpl}")
            self.assertNotIn("{" + "#", content, f"Jinja comment found in {tpl}")

        with open(self.css_path, "r", encoding="utf-8") as f:
            css = f.read()
        self.assertNotIn("/" + "*", css, "CSS block comment found in style.css")
        for idx, line in enumerate(css.splitlines(), 1):
            self.assertFalse(line.strip().startswith("//"), f"Comment found in style.css:{idx}")

if __name__ == "__main__":
    unittest.main()
