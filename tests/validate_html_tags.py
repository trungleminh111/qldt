import os
import sys
import re
from html.parser import HTMLParser

sys.stdout.reconfigure(encoding="utf-8")

VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr"
}

class StrictHTMLValidator(HTMLParser):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() not in VOID_ELEMENTS:
            self.stack.append((tag.lower(), self.getpos()))

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower in VOID_ELEMENTS:
            return
        if not self.stack:
            self.errors.append(f"Unexpected closing tag </{tag}> at line {self.getpos()[0]} (stack empty)")
            return
        last_tag, pos = self.stack[-1]
        if last_tag == tag_lower:
            self.stack.pop()
        else:
            found_idx = -1
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][0] == tag_lower:
                    found_idx = i
                    break
            if found_idx != -1:
                unclosed = [f"<{t[0]}> (L{t[1][0]})" for t in self.stack[found_idx + 1:]]
                self.errors.append(
                    f"Mismatched tag </{tag}> at L{self.getpos()[0]}. Unclosed before it: {', '.join(unclosed)}"
                )
                self.stack = self.stack[:found_idx]
            else:
                self.errors.append(f"Closing tag </{tag}> at L{self.getpos()[0]} has no opening tag")

templates_dir = "templates"
all_errors = {}
for root, dirs, files in os.walk(templates_dir):
    for f in sorted(files):
        if f.endswith(".html"):
            rel = os.path.relpath(os.path.join(root, f), templates_dir)
            with open(os.path.join(root, f), "r", encoding="utf-8") as fl:
                raw = fl.read()

            clean = re.sub(r"\{%.*?%\}", " ", raw, flags=re.DOTALL)
            clean = re.sub(r"\{\{.*?\}\}", " PH ", clean, flags=re.DOTALL)
            clean = re.sub(r"\{#.*?#\}", " ", clean, flags=re.DOTALL)

            val = StrictHTMLValidator(rel)
            val.feed(clean)

            if val.stack:
                remaining = [f"<{t[0]}> (L{t[1][0]})" for t in val.stack]
                val.errors.append(f"Unclosed tags at EOF: {', '.join(remaining)}")

            if val.errors:
                all_errors[rel] = val.errors

print(f"Validation finished. Errors count: {len(all_errors)}")
for tpl, errs in all_errors.items():
    print(f"Template {tpl}:")
    for e in errs:
        print(f"  - {e}")
