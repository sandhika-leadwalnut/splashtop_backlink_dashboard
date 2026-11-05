#!/usr/bin/env python3
"""Create the Splashtop monthly data workbook (.xlsx) that marketing fills in instead of the Word doc.

Usage (from the repo root):
    python3 scripts/make_excel_template.py --blank  "templates/Splashtop Dashboard Data - TEMPLATE.xlsx"
    python3 scripts/make_excel_template.py --from-report data/report.json --rankings-docx "monthly-docs/<doc>.docx" "<out>.xlsx"

--from-report fills every sheet from an existing data/report.json (and its screenshots in public/).
--rankings-docx fills the "URL Rankings" sheet from the per-URL tables of a Word doc (report.json
only keeps the calculated summary, not the raw monthly ranks).
"""
import argparse
import json
import os
import re
import sys

from openpyxl import Workbook
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GREEN = "2E7D32"
HEAD_FILL = PatternFill("solid", fgColor="E8F5E9")
NOTE_FONT = Font(italic=True, color="666666", size=9)
HEAD_FONT = Font(bold=True, color=GREEN)
WRAP = Alignment(wrap_text=True, vertical="top")

CHARTS = ["Remote Access / Support Keywords", "Competitor Comparison Keywords", "AEM & PM keywords"]


def header(ws, row, titles, widths=None):
    for c, t in enumerate(titles, 1):
        cell = ws.cell(row=row, column=c, value=t)
        cell.font = HEAD_FONT
        cell.fill = HEAD_FILL
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    if widths:
        for c, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(c)].width = w
    ws.freeze_panes = ws.cell(row=row + 1, column=1)


def note(ws, text):
    ws["A1"] = text
    ws["A1"].font = NOTE_FONT
    ws["A1"].alignment = Alignment(wrap_text=False)


def md_to_rich(text):
    """'plain **bold** plain' -> Excel rich text with real bold runs."""
    if "**" not in text:
        return text
    parts = re.split(r"(\*\*[^*]+\*\*)", text)
    blocks = []
    for p in parts:
        if not p:
            continue
        if p.startswith("**") and p.endswith("**"):
            blocks.append(TextBlock(InlineFont(b=True), p[2:-2]))
        else:
            blocks.append(p)
    return CellRichText(*blocks)


def build(report=None, rank_tables=None, out=None):
    wb = Workbook()

    # ---------------------------------------------------------------- README
    ws = wb.active
    ws.title = "README"
    lines = [
        ("Splashtop Backlink Dashboard: monthly data", Font(bold=True, size=14, color=GREEN)),
        ("Fill one copy of this workbook per month and attach it in Claude with: \"Update the Splashtop dashboard with this sheet\".", None),
        ("Easiest: copy last month's file, then update the numbers, texts and screenshots.", None),
        ("", None),
        ("Sheets", Font(bold=True)),
        ("Overview: month, KPIs, Top 5 / Page 1 counts, sheet link, optional dashboard link name.", None),
        ("Business Impact: one row per keyword in the three charts (baseline vs current rank). Rows show in this order.", None),
        ("Chart Insights: one key takeaway per chart.", None),
        ("Referring Domains: the DA split.", None),
        ("Monthly Growth: backlinks added each month, oldest first.", None),
        ("Keyword Lists: keywords in the Top 5 and on Page 1 (current month), with their baseline rank.", None),
        ("URL Rankings: one block per tracked URL. Put the URL in column A, then rows for Total Backlinks, each keyword, and Page Authority. Month columns run from the baseline month to the current month.", None),
        ("Key Findings: one finding per row. Make words bold in Excel (Ctrl+B) to show them bold on the dashboard.", None),
        ("Highlights: Type = Highlight or LLM Highlight, then title, description, and the screenshot pasted on the same row in column E.", None),
        ("", None),
        ("Rules", Font(bold=True)),
        ("Ranks: type the position number. Use 101 for 'not in top 100'. Leave blank or type - when there is no data.", None),
        ("Screenshots: paste the picture over column E of its row (normal paste, not 'Place in Cell'). Or type the image file name in column F and attach the image in the chat.", None),
        ("Do not rename the sheets or the header row. You can add or remove rows.", None),
    ]
    for i, (t, f) in enumerate(lines, 1):
        ws.cell(row=i, column=1, value=t)
        if f:
            ws.cell(row=i, column=1).font = f
    ws.column_dimensions["A"].width = 150

    meta = (report or {}).get("meta", {})
    kpis = (report or {}).get("kpis", {})
    kr = (report or {}).get("keywordRanking", {})

    # ---------------------------------------------------------------- Overview
    ws = wb.create_sheet("Overview")
    note(ws, "Values in column B. Report month like 'Oct 2026'. Leave 'Report date' blank to use the publishing day.")
    header(ws, 2, ["Field", "Value", "Notes"], [34, 60, 60])
    month_label = ""
    if meta.get("reportMonth"):
        y, m = meta["reportMonth"].split("-")
        month_label = f"{['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][int(m)-1]} {y}"
    base_label = (meta.get("baselineLabel") or "").replace(" (Baseline)", "")
    rows = [
        ("Report month", month_label, "e.g. Oct 2026"),
        ("Baseline month", base_label or "Dec 2025", "Month the comparison starts from"),
        ("Report date", meta.get("reportDate", ""), "Shown at the top of the dashboard. Blank = publishing day"),
        ("URLs tracked", kpis.get("urlsTracked"), ""),
        ("Keywords tracked", kpis.get("keywordsTracked"), ""),
        ("Plan total backlinks", kpis.get("planTotalBacklinks"), "Till the report month"),
        ("Actual total backlinks", kpis.get("totalBacklinks"), "Till the report month"),
        ("Keywords in Top 5 (baseline)", (kr.get("topFive") or {}).get("baseline"), ""),
        ("Keywords in Top 5 (current)", (kr.get("topFive") or {}).get("current"), "Should match the Top 5 rows in Keyword Lists"),
        ("Keywords on Page 1 (baseline)", (kr.get("firstPage") or {}).get("baseline"), ""),
        ("Keywords on Page 1 (current)", (kr.get("firstPage") or {}).get("current"), "Should match the Page 1 rows in Keyword Lists"),
        ("Monthly backlinks sheet link", (report or {}).get("acquisitionSheetUrl", ""), "Google Sheet with the detailed backlinks"),
        ("Dashboard link name (optional)", "", "Blank = splashtop-backlinking-dashboard-<month><year>"),
    ]
    for i, (a, b, c) in enumerate(rows, 3):
        ws.cell(row=i, column=1, value=a).font = Font(bold=True)
        ws.cell(row=i, column=2, value=b)
        ws.cell(row=i, column=3, value=c).font = NOTE_FONT

    # ---------------------------------------------------------------- Business Impact
    ws = wb.create_sheet("Business Impact")
    note(ws, "One row per keyword. Chart = one of the three chart names. Ranks: 101 = not in top 100.")
    header(ws, 2, ["Chart", "Keyword", "Baseline rank", "Current rank"], [38, 40, 16, 16])
    dv = DataValidation(type="list", formula1='"' + ",".join(CHARTS) + '"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add("A3:A200")
    r = 3
    for c in (report or {}).get("businessImpact", []):
        for row in c["rows"]:
            ws.cell(row=r, column=1, value=c["title"].strip())
            ws.cell(row=r, column=2, value=row["keyword"])
            ws.cell(row=r, column=3, value=row["baseline"])
            ws.cell(row=r, column=4, value=row["current"])
            r += 1

    # ---------------------------------------------------------------- Chart Insights
    ws = wb.create_sheet("Chart Insights")
    note(ws, "One key takeaway per chart, shown under that chart.")
    header(ws, 2, ["Chart", "Insight"], [38, 120])
    r = 3
    titles = [c["title"].strip() for c in (report or {}).get("businessImpact", [])] or CHARTS
    insights = {c["title"].strip(): c.get("insight", "") for c in (report or {}).get("businessImpact", [])}
    for t in titles:
        ws.cell(row=r, column=1, value=t)
        ws.cell(row=r, column=2, value=insights.get(t, "")).alignment = WRAP
        r += 1

    # ---------------------------------------------------------------- Referring Domains
    ws = wb.create_sheet("Referring Domains")
    note(ws, "Number of referring domains in each DA range.")
    header(ws, 2, ["DA range", "Referring domains"], [20, 20])
    da = ((report or {}).get("referringDomains") or {}).get("data") or [
        {"name": "DA 71-100", "value": None}, {"name": "DA 41-70", "value": None}, {"name": "DA 25-40", "value": None}]
    for i, d in enumerate(da, 3):
        ws.cell(row=i, column=1, value=d["name"])
        ws.cell(row=i, column=2, value=d["value"])

    # ---------------------------------------------------------------- Monthly Growth
    ws = wb.create_sheet("Monthly Growth")
    note(ws, "Backlinks added each month (not cumulative), oldest first. Month like 'Feb 2026'.")
    header(ws, 2, ["Month", "Backlinks added"], [16, 18])
    growth = (report or {}).get("monthlyBacklinkGrowth") or []
    # report.json keeps 3-letter months; rebuild the year by counting back from the report month
    if growth and meta.get("reportMonth"):
        y, m = map(int, meta["reportMonth"].split("-"))
        labels = []
        mm, yy = m, y
        for _ in growth:
            labels.append(f"{['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][mm-1]} {yy}")
            mm -= 1
            if mm == 0:
                mm, yy = 12, yy - 1
        labels.reverse()
        # if the report skipped a month (e.g. no January), keep the names from report.json
        if [l[:3] for l in labels] != [g["month"] for g in growth]:
            labels = [g["month"] for g in growth]
    else:
        labels = [g["month"] for g in growth]
    for i, (lab, g) in enumerate(zip(labels, growth), 3):
        ws.cell(row=i, column=1, value=lab)
        ws.cell(row=i, column=2, value=g["backlinks"])

    # ---------------------------------------------------------------- Keyword Lists
    ws = wb.create_sheet("Keyword Lists")
    note(ws, "List = Top 5 or Page 1 (current month). URL is optional: if blank it is found from the URL Rankings sheet.")
    header(ws, 2, ["List", "Keyword", "Baseline rank", "Current rank", "URL (optional)"], [12, 40, 16, 16, 70])
    dv2 = DataValidation(type="list", formula1='"Top 5,Page 1"', allow_blank=True)
    ws.add_data_validation(dv2)
    dv2.add("A3:A200")
    r = 3
    for k in (kr.get("topFive") or {}).get("keywords", []):
        for c, v in enumerate(["Top 5", k["keyword"], k.get("baselineRank"), k.get("currentRank"), k.get("url")], 1):
            ws.cell(row=r, column=c, value=v)
        r += 1
    fp = kr.get("firstPage") or {}
    base_map = {x["keyword"].lower(): x for x in fp.get("baselineKeywords", [])}
    seen = set()
    for k in fp.get("currentKeywords", []):
        b = base_map.get(k["keyword"].lower(), {})
        for c, v in enumerate(["Page 1", k["keyword"], b.get("rank"), k.get("rank"), k.get("url")], 1):
            ws.cell(row=r, column=c, value=v)
        seen.add(k["keyword"].lower())
        r += 1
    for k in fp.get("baselineKeywords", []):
        if k["keyword"].lower() not in seen:   # on Page 1 at baseline only
            for c, v in enumerate(["Page 1", k["keyword"], k.get("rank"), None, k.get("url")], 1):
                ws.cell(row=r, column=c, value=v)
            r += 1

    # ---------------------------------------------------------------- URL Rankings
    ws = wb.create_sheet("URL Rankings")
    note(ws, "One block per URL: URL in column A (on the first row of the block is enough), then Total Backlinks, "
             "one row per keyword (its rank each month) and Page Authority. 101 = not in top 100; blank or - = no data.")
    months = (rank_tables or {}).get("months") or ["Dec'25", "Feb'26", "Mar'26"]
    header(ws, 2, ["URL", "Metric"] + months, [62, 40] + [10] * len(months))
    r = 3
    for block in (rank_tables or {}).get("blocks", []):
        first = True
        rows_ = [("Total Backlinks", block["total"])] + [(k["name"], k["ranks"]) for k in block["keywords"]] + \
                [("Page Authority", block["pa"])]
        for name, vals in rows_:
            ws.cell(row=r, column=1, value=block["url"] if first else None)
            ws.cell(row=r, column=2, value=name).font = Font(bold=name in ("Total Backlinks", "Page Authority"))
            for c, v in enumerate(vals or [], 3):
                ws.cell(row=r, column=c, value=v if v is not None else "-")
            first = False
            r += 1
        r += 1  # blank line between URLs

    # ---------------------------------------------------------------- Key Findings
    ws = wb.create_sheet("Key Findings")
    note(ws, "One finding per row. Bold words in Excel (Ctrl+B) are shown bold on the dashboard.")
    header(ws, 2, ["#", "Finding"], [5, 140])
    for i, f in enumerate((report or {}).get("keyFindings", []), 1):
        ws.cell(row=i + 2, column=1, value=i)
        cell = ws.cell(row=i + 2, column=2, value=md_to_rich(f["description"]))
        cell.alignment = WRAP

    # ---------------------------------------------------------------- Highlights
    ws = wb.create_sheet("Highlights")
    note(ws, "Type = Highlight or LLM Highlight. Paste each screenshot over column E of its row "
             "(normal paste, not 'Place in Cell'), or type its file name in column F and attach the image in the chat.")
    header(ws, 2, ["Type", "#", "Title", "Description", "Screenshot (paste here)", "Screenshot file (optional)"],
           [16, 5, 42, 70, 50, 26])
    dv3 = DataValidation(type="list", formula1='"Highlight,LLM Highlight"', allow_blank=True)
    ws.add_data_validation(dv3)
    dv3.add("A3:A100")
    r = 3
    for typ, items in (("Highlight", (report or {}).get("highlights", [])),
                       ("LLM Highlight", (report or {}).get("llmHighlights", []))):
        for n, h in enumerate(items, 1):
            ws.cell(row=r, column=1, value=typ)
            ws.cell(row=r, column=2, value=n)
            ws.cell(row=r, column=3, value=h["title"]).alignment = WRAP
            ws.cell(row=r, column=4, value=h["description"]).alignment = WRAP
            img_path = os.path.join(ROOT, "public", (h.get("image") or "").lstrip("/")) if h.get("image") else None
            if img_path and os.path.exists(img_path):
                img = XLImage(img_path)
                scale = 340 / img.width
                img.width, img.height = 340, int(img.height * scale)
                img.anchor = f"E{r}"
                ws.add_image(img)
                ws.row_dimensions[r].height = min(409, img.height * 0.75 + 6)
            r += 1

    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    wb.save(out)
    print(f"Wrote {out}")


def rank_tables_from_docx(docx):
    import update_dashboard as ud
    url_cfg = json.load(open(os.path.join(ROOT, "data", "url-config.json"), encoding="utf-8"))["urls"]
    from docx_blocks import read_tables
    tables = ud.parse_tables(docx)
    mapping = ud.match_tables(tables, url_cfg)
    months = []
    for rows in read_tables(docx):
        if rows and any(ud.MONTH_YY.search(c or "") for c in rows[0][1:]):
            for c in rows[0][1:]:
                m = ud.MONTH_YY.search(c or "")
                months.append(f"{ud.MONTHS[ud.mi(m.group(1))][:3].title()}'{m.group(2)[-2:]}" if m else c)
            break
    blocks = []
    for ui, u in enumerate(url_cfg):
        if ui in mapping:
            t = mapping[ui]
            blocks.append({"url": u["url"], "total": t["total"], "pa": t["pa"], "keywords": t["keywords"]})
    return {"months": months, "blocks": blocks}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--blank", action="store_true")
    ap.add_argument("--from-report")
    ap.add_argument("--rankings-docx")
    a = ap.parse_args()
    report = None if a.blank else (json.load(open(a.from_report, encoding="utf-8")) if a.from_report else None)
    ranks = rank_tables_from_docx(a.rankings_docx) if (a.rankings_docx and not a.blank) else None
    build(report, ranks, a.out)


if __name__ == "__main__":
    main()
