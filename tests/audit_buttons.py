import os
import sys
import re
from html.parser import HTMLParser

sys.stdout.reconfigure(encoding="utf-8")

class FullAuditor(HTMLParser):
    def __init__(self, tpl):
        super().__init__()
        self.tpl = tpl
        self.buttons = []
        self.current_btn = None

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        classes = d.get("class", "").split()
        if tag == "button" or (tag == "a" and any("btn" in c for c in classes)) or (tag == "input" and d.get("type") in ["submit", "button"]):
            self.current_btn = {
                "line": self.getpos()[0],
                "tag": tag,
                "class": d.get("class", ""),
                "style": d.get("style", ""),
                "text": ""
            }
            self.buttons.append(self.current_btn)

    def handle_endtag(self, tag):
        if self.current_btn and self.current_btn["tag"] == tag:
            self.current_btn = None

    def handle_data(self, data):
        if self.current_btn:
            self.current_btn["text"] += data.strip()

templates_dir = "templates"
all_items = []
for root, dirs, files in os.walk(templates_dir):
    for f in sorted(files):
        if f.endswith(".html"):
            rel = os.path.relpath(os.path.join(root, f), templates_dir)
            with open(os.path.join(root, f), "r", encoding="utf-8") as fl:
                c = fl.read()
            clean = re.sub(r"\{%.*?%\}", " ", c, flags=re.DOTALL)
            clean = re.sub(r"\{\{.*?\}\}", " PH ", clean, flags=re.DOTALL)
            p = FullAuditor(rel)
            p.feed(clean)
            all_items.extend([(rel, b) for b in p.buttons])

print(f"Total buttons found: {len(all_items)}")
has_style = [item for item in all_items if item[1].get("style")]
print(f"Buttons with inline style: {len(has_style)}")
for rel, b in has_style:
    print(f"{rel:30s} L{b['line']:3d} class=\"{b['class']}\" style=\"{b['style']}\"")
