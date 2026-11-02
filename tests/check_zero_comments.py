import os
import sys
import tokenize

SOURCE_DIRS = ["controllers", "models", "tests", "templates", "static"]
EXTENSIONS = {".py", ".html", ".js"}

def check_file_for_comments(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    violations = []

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    lines = content.splitlines()

    if ext == ".py":
        with open(filepath, "rb") as f:
            try:
                tokens = tokenize.tokenize(f.readline)
                for toknum, tokval, (srow, scol), _, _ in tokens:
                    if toknum == tokenize.COMMENT:
                        violations.append((srow, tokval))
            except Exception:
                pass
    elif ext == ".js":
        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("/*") or "/*" in stripped:
                violations.append((idx, line))
    elif ext == ".html":
        for idx, line in enumerate(lines, 1):
            if "<!--" in line:
                violations.append((idx, line))

    return violations

def audit_clean_code():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    total_files = 0
    total_violations = 0
    report = []

    for sdir in SOURCE_DIRS:
        full_dir = os.path.join(base_dir, sdir)
        if not os.path.exists(full_dir):
            continue
        for root, _, files in os.walk(full_dir):
            if "__pycache__" in root:
                continue
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in EXTENSIONS:
                    fpath = os.path.join(root, file)
                    v = check_file_for_comments(fpath)
                    total_files += 1
                    if v:
                        total_violations += len(v)
                        rel_path = os.path.relpath(fpath, base_dir)
                        report.append((rel_path, v))

    single_files = ["app.py", "desktop_app.py", "config.py"]
    for sf in single_files:
        fpath = os.path.join(base_dir, sf)
        if os.path.exists(fpath):
            v = check_file_for_comments(fpath)
            total_files += 1
            if v:
                total_violations += len(v)
                report.append((sf, v))

    print(f"Audited {total_files} code files.")
    if total_violations == 0:
        print("PERFECT: 0 comments found across entire codebase! 100% Clean Code.")
        return 0
    else:
        print(f"FAILED: Found {total_violations} comments in {len(report)} files:")
        for rpath, vlist in report:
            for line_no, content in vlist:
                print(f"  {rpath}:{line_no} -> {content.strip()}")
        return 1

if __name__ == "__main__":
    sys.exit(audit_clean_code())
