#!/usr/bin/env python3
"""Build a self-contained preview of the dashboard that works from any folder or web path.

Usage (from the repo root, after update_dashboard.py and `npm ci`):
    python3 scripts/make_preview.py            # writes preview/

The normal build uses absolute paths ("/assets/...", "/reports/..."), which only work at the
root of a website. This builds with relative paths and rewrites image paths inside the bundle,
so the preview can be opened from a file, a sub-folder, or published as a private Claude page.
Prints the list of files in the preview (page + supporting files).
"""
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "preview")


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    npx = "npx.cmd" if os.name == "nt" else "npx"
    r = subprocess.run([npx, "vite", "build", "--base", "./", "--outDir", OUT, "--emptyOutDir"],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-2000:])
        sys.exit("Preview build failed.")

    # every file that ended up in the preview (public/ is copied in by vite)
    present = set()
    for d, _, fs in os.walk(OUT):
        for f in fs:
            present.add(os.path.relpath(os.path.join(d, f), OUT).replace(os.sep, "/"))

    def fix(text):
        # "/reports/2026-09/x.png" -> "./reports/2026-09/x.png" when that file exists in the preview
        def repl(m):
            q, path = m.group(1), m.group(2)
            return f"{q}./{path}{q}" if path in present else m.group(0)
        return re.sub(r'(["\'`])/([^"\'`<>\n]{1,200}?)\1', repl, text)

    changed = 0
    for rel in present:
        if rel.endswith((".js", ".css", ".html")):
            p = os.path.join(OUT, rel)
            src = open(p, encoding="utf-8").read()
            new = fix(src)
            if rel == "index.html":
                # the dev-only import map and missing stylesheet are not needed in the bundled preview
                new = re.sub(r'<script type="importmap">.*?</script>\s*', "", new, flags=re.S)
                new = re.sub(r'<link rel="stylesheet" href="/index\.css">\s*', "", new)
                new = re.sub(r'<link rel="icon"[^>]*>\s*', "", new)
                meta = json.load(open(os.path.join(ROOT, "data", "report.json"), encoding="utf-8"))["meta"]
                month = meta.get("currentLabel") or meta.get("periodEnd", "")
                new = re.sub(r"<title>.*?</title>", f"<title>{month} Dashboard Preview</title>", new, flags=re.S)
            if new != src:
                open(p, "w", encoding="utf-8").write(new)
                changed += 1

    # only the files the page actually uses (public/ also holds old, unused images)
    used_text = ""
    for rel in present:
        if rel.endswith((".js", ".css", ".html")):
            used_text += open(os.path.join(OUT, rel), encoding="utf-8").read()
    files = sorted(f for f in present if f != "index.html" and
                   (f.startswith("assets/") or f"./{f}" in used_text))
    print(json.dumps({"page": os.path.join(OUT, "index.html"), "files": files}, indent=2))


if __name__ == "__main__":
    main()
