#!/usr/bin/env python3
"""Create the Splashtop dashboard workbook (.xlsx): one tab per month, like the Word doc's tabs.

Each month tab (named like "Oct 2026") holds every section one under another:
Overview, Business Impact, Chart Insights, Referring Domains, Monthly Growth, Keyword Lists,
URL Rankings, Key Findings, Highlights. scripts/update_from_excel.py reads one month tab.

Usage (from the repo root):
    # the shared all-months workbook, filled from published months
    python3 -B scripts/make_excel_template.py "templates/Splashtop Dashboard Data.xlsx" \\
        --month data/history/2026-08.json "monthly-docs/2026-08 Backlink Performance Dashboard data.docx" \\
        --month data/history/2026-09.json "monthly-docs/2026-09 Backlink Performance Dashboard data.docx" \\
        --month data/report.json          "monthly-docs/2026-10 Backlink Performance Dashboard data.docx"
    # a blank workbook with one empty month tab
    python3 -B scripts/make_excel_template.py "templates/Splashtop Dashboard Data - TEMPLATE.xlsx" --blank
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
SECTION_FILL = PatternFill("solid", fgColor=GREEN)
SECTION_FONT = Font(bold=True, color="FFFFFF", size=12)
HEAD_FILL = PatternFill("solid", fgColor="E8F5E9")
HEAD_FONT = Font(bold=True, color=GREEN)
NOTE_FONT = Font(italic=True, color="666666", size=9)
WRAP = Alignment(wrap_text=True, vertical="top")
TOP = Alignment(vertical="top")
MON3 = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
WIDE_TO = 8          # merged text cells run from their column to column H
PIC_COL = "I"        # screenshots are pasted from column I
CHARTS = ["Remote Access / Support Keywords", "Competitor Comparison Keywords", "AEM & PM keywords"]

# section names: update_from_excel.py finds sections by these exact titles in column A
SECTIONS = ["Overview", "Business Impact", "Chart Insights", "Referring Domains", "Monthly Growth",
            "Keyword Lists", "URL Rankings", "Key Findings", "Highlights"]


def md_to_rich(text):
    """'plain **bold** plain' -> Excel rich text with real bold runs."""
    if "**" not in text:
        return text
    blocks = []
    for p in re.split(r"(\*\*[^*]+\*\*)", text):
        if not p:
            continue
        if p.startswith("**") and p.endswith("**"):
            blocks.append(TextBlock(InlineFont(b=True), p[2:-2]))
        else:
            blocks.append(p)
    return CellRichText(*blocks)


class MonthTab:
    def __init__(self, ws):
        self.ws = ws
        self.r = 1

    def title(self, text, note):
        self.ws.cell(row=1, column=1, value=text).font = Font(bold=True, size=14, color=GREEN)
        self.ws.cell(row=2, column=1, value=note).font = NOTE_FONT
        self.r = 4

    def section(self, name, headers, note=None):
        ws = self.ws
        for c in range(1, 14):
            ws.cell(row=self.r, column=c).fill = SECTION_FILL
        ws.cell(row=self.r, column=1, value=name).font = SECTION_FONT
        if note:
            ws.cell(row=self.r, column=2, value=note).font = Font(italic=True, color="FFFFFF", size=9)
        self.r += 1
        for c, h in enumerate(headers, 1):
            if h is None:
                continue
            cell = ws.cell(row=self.r, column=c, value=h)
            cell.font = HEAD_FONT
            cell.fill = HEAD_FILL
        self.r += 1

    def row(self, values, wide=None, height=None, bold_cols=()):
        """values: list by column. wide: column index (1-based) whose cell is merged to column H and wrapped."""
        ws = self.ws
        for c, v in enumerate(values, 1):
            if v is None:
                continue
            cell = ws.cell(row=self.r, column=c, value=v)
            cell.alignment = WRAP if c == wide else TOP
            if c in bold_cols:
                cell.font = Font(bold=True)
        if wide:
            ws.merge_cells(start_row=self.r, start_column=wide, end_row=self.r, end_column=WIDE_TO)
            ws.cell(row=self.r, column=wide).alignment = WRAP
            if height is None:
                txt = values[wide - 1]
                n = len("".join(b.text if isinstance(b, TextBlock) else str(b) for b in txt)) \
                    if isinstance(txt, CellRichText) else len(str(txt or ""))
                height = max(15, 15 * (n // 95 + 1))
        if height:
            ws.row_dimensions[self.r].height = min(409, height)
        self.r += 1
        return self.r - 1

    def gap(self, n=1):
        self.r += n


def month_label(report_month):
    y, m = report_month.split("-")
    return f"{MON3[int(m) - 1]} {y}"


def growth_labels(report):
    growth = report.get("monthlyBacklinkGrowth") or []
    meta = report.get("meta", {})
    if not growth or not meta.get("reportMonth"):
        return [g["month"] for g in growth]
    y, m = map(int, meta["reportMonth"].split("-"))
    labels = []
    for _ in growth:
        labels.append(f"{MON3[m - 1]} {y}")
        m -= 1
        if m == 0:
            m, y = 12, y - 1
    labels.reverse()
    if [l[:3] for l in labels] != [g["month"] for g in growth]:   # a month was skipped
        return [g["month"] for g in growth]
    return labels


def add_month_tab(wb, report, ranks, blank=False):
    meta = report.get("meta", {})
    kpis = report.get("kpis", {})
    kr = report.get("keywordRanking", {})
    name = month_label(meta["reportMonth"]) if meta.get("reportMonth") else "Mon YYYY"
    ws = wb.create_sheet(name)
    ws.sheet_properties.tabColor = GREEN
    for c, w in enumerate([40, 46] + [11] * 11, 1):
        ws.column_dimensions[get_column_letter(c)].width = w
    t = MonthTab(ws)
    t.title(f"Splashtop dashboard data: {name}",
            "One tab per month. To start a new month: right-click this tab > Duplicate (Move or Copy > Create a copy), "
            "rename it like 'Nov 2026', then update it. Do not rename the green section rows or the header rows.")

    # Overview
    t.section("Overview", ["Field", "Value", "Notes"])
    base_label = (meta.get("baselineLabel") or "").replace(" (Baseline)", "")
    for a, b, c in [
        ("Report month", name if not blank else None, "Same as the tab name, e.g. Oct 2026"),
        ("Baseline month", base_label or "Dec 2025", "Month the comparison starts from"),
        ("Report date", meta.get("reportDate"), "Shown at the top of the dashboard. Blank = publishing day"),
        ("URLs tracked", kpis.get("urlsTracked"), ""),
        ("Keywords tracked", kpis.get("keywordsTracked"), ""),
        ("Plan total backlinks", kpis.get("planTotalBacklinks"), "Till the report month"),
        ("Actual total backlinks", kpis.get("totalBacklinks"), "Till the report month"),
        ("Keywords in Top 5 (baseline)", (kr.get("topFive") or {}).get("baseline"), ""),
        ("Keywords in Top 5 (current)", (kr.get("topFive") or {}).get("current"), "Should match the Top 5 rows in Keyword Lists"),
        ("Keywords on Page 1 (baseline)", (kr.get("firstPage") or {}).get("baseline"), ""),
        ("Keywords on Page 1 (current)", (kr.get("firstPage") or {}).get("current"), "Should match the Page 1 rows in Keyword Lists"),
        ("Monthly backlinks sheet link", report.get("acquisitionSheetUrl"), "Google Sheet with the detailed backlinks"),
        ("Dashboard link name (optional)", None, "Blank = splashtop-backlinking-dashboard-<month><year>"),
    ]:
        r = t.row([a, b], bold_cols=(1,))
        ws.cell(row=r, column=3, value=c).font = NOTE_FONT
    t.gap()

    # Business Impact
    t.section("Business Impact", ["Chart", "Keyword", "Baseline rank", "Current rank"],
              "One row per keyword. 101 = not in top 100")
    first = t.r
    for c in report.get("businessImpact", []):
        for row in c["rows"]:
            t.row([c["title"].strip(), row["keyword"], row["baseline"], row["current"]])
    if blank:
        t.gap(6)
    dv = DataValidation(type="list", formula1='"' + ",".join(CHARTS) + '"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"A{first}:A{max(first, t.r - 1)}")
    t.gap()

    # Chart Insights
    t.section("Chart Insights", ["Chart", "Insight"], "One key takeaway per chart")
    ins = {c["title"].strip(): c.get("insight", "") for c in report.get("businessImpact", [])}
    for title in ([c["title"].strip() for c in report.get("businessImpact", [])] or CHARTS):
        t.row([title, ins.get(title) or None], wide=2)
    t.gap()

    # Referring Domains
    t.section("Referring Domains", ["DA range", "Referring domains"])
    for d in (report.get("referringDomains") or {}).get("data") or [
            {"name": n, "value": None} for n in ("DA 71-100", "DA 41-70", "DA 25-40")]:
        t.row([d["name"], d["value"]])
    t.gap()

    # Monthly Growth
    t.section("Monthly Growth", ["Month", "Backlinks added"], "Backlinks added each month (not cumulative), oldest first")
    for lab, g in zip(growth_labels(report), report.get("monthlyBacklinkGrowth") or []):
        t.row([lab, g["backlinks"]])
    if blank:
        t.gap(3)
    t.gap()

    # Keyword Lists
    t.section("Keyword Lists", ["List", "Keyword", "Baseline rank", "Current rank", "URL (optional)"],
              "List = Top 5 or Page 1 (current month). URL blank = found automatically")
    first = t.r
    for k in (kr.get("topFive") or {}).get("keywords", []):
        t.row(["Top 5", k["keyword"], k.get("baselineRank"), k.get("currentRank")])
    fp = kr.get("firstPage") or {}
    base_map = {x["keyword"].lower(): x for x in fp.get("baselineKeywords", [])}
    seen = set()
    for k in fp.get("currentKeywords", []):
        t.row(["Page 1", k["keyword"], base_map.get(k["keyword"].lower(), {}).get("rank"), k.get("rank")])
        seen.add(k["keyword"].lower())
    for k in fp.get("baselineKeywords", []):
        if k["keyword"].lower() not in seen:
            t.row(["Page 1", k["keyword"], k.get("rank"), None])
    if blank:
        t.gap(6)
    dv2 = DataValidation(type="list", formula1='"Top 5,Page 1"', allow_blank=True)
    ws.add_data_validation(dv2)
    dv2.add(f"A{first}:A{max(first, t.r - 1)}")
    t.gap()

    # URL Rankings
    months = (ranks or {}).get("months") or ["Dec'25", "Feb'26", "Mar'26"]
    t.section("URL Rankings", ["URL", "Metric"] + months,
              "Per URL: Total Backlinks, one row per keyword, Page Authority. 101 = not in top 100; - = no data")
    for block in (ranks or {}).get("blocks", []):
        rows_ = [("Total Backlinks", block["total"])] + [(k["name"], k["ranks"]) for k in block["keywords"]] + \
                [("Page Authority", block["pa"])]
        for i, (metric, vals) in enumerate(rows_):
            t.row([block["url"] if i == 0 else None, metric] + [v if v is not None else "-" for v in (vals or [])],
                  bold_cols=(2,) if metric in ("Total Backlinks", "Page Authority") else ())
        t.gap()
    if blank:
        t.gap(6)

    # Key Findings
    t.section("Key Findings", ["#", "Finding"], "One finding per row. Bold words (Ctrl+B) show bold on the dashboard")
    for i, f in enumerate(report.get("keyFindings", []), 1):
        t.row([i, md_to_rich(f["description"])], wide=2)
    if blank:
        for i in range(1, 6):
            t.row([i, None], wide=2)
    t.gap()

    # Highlights
    t.section("Highlights", ["Type", "Title", "Description", None, None, None, None, None,
                             "Screenshot (paste from here) or file name"],
              "Type = Highlight or LLM Highlight. Paste each screenshot on its own row, starting at column I")
    first = t.r
    for typ, items in (("Highlight", report.get("highlights", [])), ("LLM Highlight", report.get("llmHighlights", []))):
        for h in items:
            img_path = os.path.join(ROOT, "public", h["image"].lstrip("/")) if h.get("image") else None
            img = None
            if img_path and os.path.exists(img_path):
                img = XLImage(img_path)
                scale = 300 / img.width
                img.width, img.height = 300, int(img.height * scale)
            r = t.row([typ, h["title"], h["description"]], wide=3,
                      height=max(60, (img.height * 0.75 + 8) if img else 60))
            ws.cell(row=r, column=2).alignment = WRAP
            if img:
                img.anchor = f"{PIC_COL}{r}"
                ws.add_image(img)
    if blank:
        for typ in ["Highlight"] * 3 + ["LLM Highlight"] * 3:
            r = t.row([typ, None, None], wide=3, height=120)
    dv3 = DataValidation(type="list", formula1='"Highlight,LLM Highlight"', allow_blank=True)
    ws.add_data_validation(dv3)
    dv3.add(f"A{first}:A{max(first, t.r - 1)}")
    ws.freeze_panes = "A4"
    return ws


def add_readme(wb):
    ws = wb.active
    ws.title = "README"
    lines = [
        ("Splashtop Backlink Dashboard: monthly data", Font(bold=True, size=14, color=GREEN)),
        ("One workbook for all months. Each month has its own tab named like 'Oct 2026' (like the tabs in the Word doc).", None),
        ("", None),
        ("Every month", Font(bold=True)),
        ("1. Right-click last month's tab > Duplicate (Excel: Move or Copy > Create a copy). Rename the copy to the new month, e.g. 'Nov 2026'.", None),
        ("2. In the new tab update the numbers, texts and screenshots. Set 'Report month' in Overview to the same month.", None),
        ("3. Attach this workbook in Claude: \"Update the Splashtop dashboard with this sheet\". Claude uses the newest month tab.", None),
        ("   To redo an older month, say which tab: \"Update the Splashtop dashboard with the Sep 2026 tab\".", None),
        ("", None),
        ("Sections in each month tab (green rows; keep their names and the header row under them)", Font(bold=True)),
        ("Overview: month, KPIs, Top 5 / Page 1 counts, sheet link, optional dashboard link name.", None),
        ("Business Impact: one row per keyword in the three charts (baseline vs current rank), in display order.", None),
        ("Chart Insights: one key takeaway per chart.", None),
        ("Referring Domains: the DA split.", None),
        ("Monthly Growth: backlinks added each month, oldest first.", None),
        ("Keyword Lists: keywords in the Top 5 and on Page 1 (current month), with their baseline rank.", None),
        ("URL Rankings: one block per tracked URL (URL in column A on the first row): Total Backlinks, each keyword, Page Authority. Add a month column each month.", None),
        ("Key Findings: one finding per row. Bold words (Ctrl+B) show bold on the dashboard.", None),
        ("Highlights: Type (Highlight / LLM Highlight), Title, Description, and the screenshot pasted on the same row from column I.", None),
        ("", None),
        ("Rules", Font(bold=True)),
        ("Ranks: type the position number. 101 = not in top 100. Blank or - = no data.", None),
        ("Rows can be added or removed inside a section. Leave the green section rows and header rows as they are.", None),
        ("Screenshots: normal paste so the picture floats over the cells (not 'Place in Cell'). Its top-left corner must be on the highlight's row.", None),
        ("Or type the image file name in column I and attach the image in the chat.", None),
    ]
    for i, (t, f) in enumerate(lines, 1):
        ws.cell(row=i, column=1, value=t)
        if f:
            ws.cell(row=i, column=1).font = f
    ws.column_dimensions["A"].width = 150


def rank_tables_from_docx(docx):
    import update_dashboard as ud
    from docx_blocks import read_tables
    url_cfg = json.load(open(os.path.join(ROOT, "data", "url-config.json"), encoding="utf-8"))["urls"]
    mapping = ud.match_tables(ud.parse_tables(docx), url_cfg)
    months = []
    for rows in read_tables(docx):
        if rows and any(ud.MONTH_YY.search(c or "") for c in rows[0][1:]):
            for c in rows[0][1:]:
                m = ud.MONTH_YY.search(c or "")
                months.append(f"{ud.MONTHS[ud.mi(m.group(1))][:3].title()}'{m.group(2)[-2:]}" if m else c)
            break
    blocks = [{"url": u["url"], "total": mapping[i]["total"], "pa": mapping[i]["pa"], "keywords": mapping[i]["keywords"]}
              for i, u in enumerate(url_cfg) if i in mapping]
    return {"months": months, "blocks": blocks}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--blank", action="store_true")
    ap.add_argument("--month", nargs=2, action="append", metavar=("REPORT_JSON", "DOCX"),
                    help="Add a filled month tab from a report.json and the Word doc that holds its ranking tables.")
    a = ap.parse_args()
    wb = Workbook()
    add_readme(wb)
    if a.blank or not a.month:
        add_month_tab(wb, {}, None, blank=True)
    else:
        # newest month first, so it is the first tab after README
        items = [(json.load(open(rj, encoding="utf-8")), dx) for rj, dx in a.month]
        items.sort(key=lambda x: x[0]["meta"]["reportMonth"], reverse=True)
        for report, docx in items:
            add_month_tab(wb, report, rank_tables_from_docx(docx))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    wb.save(a.out)
    print(f"Wrote {a.out}")


if __name__ == "__main__":
    main()
