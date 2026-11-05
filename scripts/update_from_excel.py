#!/usr/bin/env python3
"""Splashtop dashboard workbook (.xlsx, one tab per month) -> data/report.json + screenshots.

Same output and the same calculation rules as update_dashboard.py (the Word-doc version);
only the input is different. Layout of the workbook: see scripts/make_excel_template.py
and MONTHLY_UPDATE.md ("Excel workbook").

Usage (from the repo root):
    python3 -B scripts/update_from_excel.py "monthly-data/Splashtop Dashboard Data.xlsx" [--month "Oct 2026"] --dry-run
    python3 -B scripts/update_from_excel.py "<file>.xlsx" [--month "Oct 2026"] [--report-date "November 4, 2026"] [--images-dir <folder>]

--month: which month tab to use. Default: the newest tab named like "Oct 2026".
--images-dir: folder with screenshots named in the Highlights section (column I)
(used when a picture is not pasted into the tab).
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import update_dashboard as ud  # noqa: E402  (reuses MONTHS, slugify, summary_row, keyword_url)

try:
    import openpyxl
    from openpyxl.cell.rich_text import CellRichText, TextBlock
except ImportError:  # pragma: no cover
    print("openpyxl is needed: pip install openpyxl")
    sys.exit(2)

DATA, PUBLIC = ud.DATA, ud.PUBLIC
MONTHS = ud.MONTHS
problems, warnings, notes = ud.problems, ud.warnings, ud.notes
MON_RE = re.compile(r"^\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*[\'’‘`,]?\s*(\d{4}|\d{2})?\s*$", re.I)
DA_COLORS = ["#14b8a6", "#3b82f6", "#22c55e", "#f59e0b"]
NO_DATA = ("", "-", "–", "—", "n/a", "na", "none")


def report():
    print("=" * 70)
    for n in notes:
        print("OK  ", n)
    if warnings:
        print("\nWARNINGS (check these, publishing is allowed):")
        for w in warnings:
            print("  -", w)
    if problems:
        print("\nPROBLEMS (fix the Excel sheet and run again before publishing):")
        for p in problems:
            print("  -", p)
    if not warnings and not problems:
        print("No warnings.")
    print("=" * 70)


# ------------------------------------------------------------------ cell helpers
def text(v):
    if v is None:
        return ""
    if isinstance(v, CellRichText):
        return ud.norm("".join(b.text if isinstance(b, TextBlock) else str(b) for b in v))
    if isinstance(v, (dt.date, dt.datetime)):
        return v.strftime("%Y-%m-%d")
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return ud.norm(str(v))


def md(v):
    """Cell text with Excel bold runs as **bold** (same as the Word parser)."""
    if not isinstance(v, CellRichText):
        return text(v)
    out = ""
    for b in v:
        if isinstance(b, TextBlock):
            t = b.text
            if b.font is not None and b.font.b and t.strip():
                lead, core, trail = re.match(r"^(\s*)(.*?)(\s*)$", t, re.S).groups()
                out += f"{lead}**{core}**{trail}"
            else:
                out += t
        else:
            out += str(b)
    out = re.sub(r"\*\*\s*\*\*", "", out)          # merge touching bold runs
    return ud.norm(out)


def number(v, where, allow_none=True):
    """Whole number from a cell; None for blank or '-'. Records a PROBLEM for anything else."""
    if v is None or (isinstance(v, str) and v.strip().lower() in NO_DATA):
        if not allow_none:
            problems.append(f"{where}: value is missing.")
        return None
    if isinstance(v, bool):
        problems.append(f"{where}: '{v}' is not a number.")
        return None
    if isinstance(v, (int, float)):
        if float(v).is_integer():
            return int(v)
        problems.append(f"{where}: '{v}' should be a whole number.")
        return None
    s = text(v).replace(",", "")
    m = re.fullmatch(r"[#]?\s*(\d+)(?:\+|st|nd|rd|th)?", s, re.I)
    if m:
        return int(m.group(1))
    if re.fullmatch(r">\s*100|100\+|not in top 100|nr|not ranking", s, re.I):
        return 101
    problems.append(f"{where}: '{text(v)}' is not a number.")
    return None


def parse_month(v):
    """'Oct 2026', "Oct'26", 'October 2026' or an Excel date -> (month index, 4-digit year)."""
    if isinstance(v, (dt.date, dt.datetime)):
        return v.month - 1, v.year
    m = MON_RE.match(text(v))
    if not m or not m.group(2):
        return None
    y = int(m.group(2))
    return ud.mi(m.group(1)), (2000 + y if y < 100 else y)


def col(vals, i):
    return vals[i] if i < len(vals) else None


SECTION_NAMES = ["overview", "business impact", "chart insights", "referring domains", "monthly growth",
                 "keyword lists", "url rankings", "key findings", "highlights"]


def month_tabs(wb):
    out = []
    for ws in wb.worksheets:
        m = parse_month(ws.title)
        if m:
            out.append((m, ws))
    return out


def read_sections(ws):
    """Green section rows (exact names in column A) split the month tab. The next non-blank row is the
    header; everything after it until the next section is data. -> {name: {"header": vals, "rows": [(r, vals)]}}"""
    secs, cur = {}, None
    width = ws.max_column
    for r in range(1, ws.max_row + 1):
        vals = [ws.cell(row=r, column=c).value for c in range(1, width + 1)]
        a = text(vals[0]).lower() if vals else ""
        if a in SECTION_NAMES and all(text(v) == "" or i == 1 for i, v in enumerate(vals) if i > 0) \
                and (a not in secs):
            cur = {"header": None, "rows": [], "start": r}
            secs[a] = cur
            continue
        if cur is None or all(text(v) == "" for v in vals):
            continue
        if cur["header"] is None:
            cur["header"] = vals
            continue
        cur["rows"].append((r, vals))
    for n in SECTION_NAMES:
        if n not in secs:
            problems.append(f"Section '{n.title()}' is missing from the tab '{ws.title}' (keep the green section rows).")
    return secs


# ------------------------------------------------------------------ sections
def read_sections_quiet(ws):
    before = len(problems)
    out = read_sections(ws)
    del problems[before:]
    return out


def parse_overview(rows):
    fields = {}
    for r, v in rows:
        key = text(col(v, 0)).lower()
        if key:
            fields[key] = col(v, 1)

    def get(label_re):
        for k, val in fields.items():
            if re.match(label_re, k):
                return val
        return None
    return get


def parse_highlight_images(ws):
    """Pictures floating over the month tab -> {excel_row: (bytes, ext)}."""
    out = {}
    for img in getattr(ws, "_images", []):
        try:
            row = img.anchor._from.row + 1  # 0-based -> Excel row
        except AttributeError:
            continue
        data = img._data()
        fmt = (getattr(img, "format", None) or "png").lower()
        ext = ".jpg" if fmt in ("jpeg", "jpg") else f".{fmt}"
        if row in out:
            warnings.append(f"Row {row} has more than one picture; using the first one.")
            continue
        out[row] = (data, ext)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("xlsx")
    ap.add_argument("--report-date", help='Date shown at the top, e.g. "November 4, 2026". Default: the sheet, else today.')
    ap.add_argument("--link-name", help="Optional custom Vercel link name (overrides the sheet).")
    ap.add_argument("--month", help='Month tab to use, e.g. "Oct 2026". Default: the newest month tab.')
    ap.add_argument("--images-dir", help="Folder with screenshots named in the Highlights section.")
    ap.add_argument("--dry-run", action="store_true", help="Validate only; write nothing.")
    args = ap.parse_args()

    site = json.load(open(os.path.join(DATA, "site-config.json"), encoding="utf-8"))
    url_cfg = json.load(open(os.path.join(DATA, "url-config.json"), encoding="utf-8"))["urls"]
    cat_cfg = json.load(open(os.path.join(DATA, "business-impact.json"), encoding="utf-8"))["categories"]

    try:
        wb = openpyxl.load_workbook(args.xlsx, data_only=True, rich_text=True)
    except Exception as e:  # noqa: BLE001
        problems.append(f"Could not open the workbook ({e}). Save it as .xlsx and attach it again.")
        report()
        sys.exit(2)

    # ---- pick the month tab
    tabs = month_tabs(wb)
    if not tabs:
        problems.append("No month tab found. Name each month's tab like 'Oct 2026' (rename the template's 'Mon YYYY' tab).")
        report()
        sys.exit(2)
    if args.month:
        want = parse_month(args.month)
        pick = [ws for m, ws in tabs if m == want]
        if not want or not pick:
            problems.append(f"No tab for '{args.month}'. Month tabs in the workbook: " + ", ".join(ws.title for _, ws in tabs) + ".")
            report()
            sys.exit(2)
        ws_month = pick[0]
    else:
        dup = {}
        for m, ws in tabs:
            dup.setdefault(m, []).append(ws.title)
        for m, names in dup.items():
            if len(names) > 1:
                problems.append("Two tabs are for the same month: " + ", ".join(f"'{n}'" for n in names) + ". Rename or delete one.")
        ws_month = max(tabs, key=lambda x: (x[0][1], x[0][0]))[1]
    tab_month = parse_month(ws_month.title)
    notes.append(f"Using the tab '{ws_month.title}' (month tabs: " + ", ".join(ws.title for _, ws in tabs) + ")")
    secs = read_sections(ws_month)

    def sec_rows(name):
        return (secs.get(name) or {}).get("rows", [])

    def where(name, r):
        return f"{ws_month.title} tab, {name} (row {r})"

    # ---- overview
    get = parse_overview(sec_rows("overview"))
    rm = parse_month(get(r"^report month"))
    if rm and rm != tab_month:
        problems.append(f"Overview 'Report month' says {text(get(r'^report month'))} but the tab is '{ws_month.title}'. Make them the same.")
    m_idx, year = tab_month
    month_key = f"{year}-{m_idx + 1:02d}"
    bm = parse_month(get(r"^baseline month"))
    if not bm:
        problems.append("Overview: 'Baseline month' must look like 'Dec 2025'.")
    img_dir = os.path.join(PUBLIC, "reports", month_key)

    kpis = {
        "urlsTracked": number(get(r"^urls tracked"), "Overview: URLs tracked", False),
        "keywordsTracked": number(get(r"^keywords tracked"), "Overview: Keywords tracked", False),
        "planTotalBacklinks": number(get(r"^plan total"), "Overview: Plan total backlinks", False),
        "totalBacklinks": number(get(r"^actual total"), "Overview: Actual total backlinks", False),
    }

    # a duplicated tab that was never updated would publish last month's numbers again
    older = [(m, ws) for m, ws in tabs if (m[1], m[0]) < (year, m_idx)]
    if older:
        pm, pws = max(older, key=lambda x: (x[0][1], x[0][0]))
        pget = parse_overview(read_sections_quiet(pws).get("overview", {}).get("rows", []))
        same = [lab for lab, rx in (("Actual total backlinks", r"^actual total"), ("Plan total backlinks", r"^plan total"))
                if text(pget(rx)) and text(pget(rx)) == text(get(rx))]
        if len(same) == 2:
            warnings.append(f"Plan and actual total backlinks are the same as in the '{pws.title}' tab. "
                            "Check the tab was updated for the new month.")

    # ---- business impact
    bi_rows = []
    for r, v in sec_rows("business impact"):
        chart, kw = text(col(v, 0)), text(col(v, 1))
        if not kw:
            continue
        bi_rows.append((chart, kw, number(col(v, 2), where("Business Impact", r) + " baseline rank"),
                        number(col(v, 3), where("Business Impact", r) + " current rank")))
    ins = {}
    for r, v in sec_rows("chart insights"):
        if text(col(v, 0)):
            ins[text(col(v, 0)).lower()] = text(col(v, 1))

    def chart_key(s):
        return re.sub(r"[^a-z0-9]", "", s.lower())
    categories = []
    for c in cat_cfg:
        key = chart_key(c["title"])
        rows = [{"keyword": kw, "baseline": b, "current": cur} for ch, kw, b, cur in bi_rows if chart_key(ch) == key]
        insight = next((t for k, t in ins.items() if chart_key(k) == key), "")
        if not rows:
            warnings.append(f"Business Impact: no keywords for the '{c['title'].strip()}' chart.")
        if not insight:
            warnings.append(f"No key takeaway found for the '{c['title'].strip()}' chart (Chart Insights section).")
        for x in rows:
            if x["baseline"] is None or x["current"] is None:
                warnings.append(f"Business impact keyword '{x['keyword']}' is missing a baseline or current rank.")
        categories.append({"title": c["title"], "rows": rows, "insight": insight})
    known = {chart_key(c["title"]) for c in cat_cfg}
    for ch, kw, _, _ in bi_rows:
        if chart_key(ch) not in known:
            problems.append(f"Business Impact: keyword '{kw}' has chart '{ch or '(blank)'}'; use one of: "
                            + ", ".join(c["title"].strip() for c in cat_cfg) + ".")

    # ---- referring domains
    da = []
    for r, v in sec_rows("referring domains"):
        name = text(col(v, 0))
        if not name:
            continue
        m = re.search(r"(\d+)\s*[-–—to]+\s*(\d+)", name)
        if not m:
            problems.append(where("Referring Domains", r) + f": DA range '{name}' should look like 'DA 41-70'.")
            continue
        da.append({"name": f"DA {m.group(1)}-{m.group(2)}", "value": number(col(v, 1), where("Referring Domains", r), False) or 0,
                   "color": DA_COLORS[len(da) % len(DA_COLORS)]})
    total_da = sum(d["value"] for d in da)
    high = sum(d["value"] for d in da if int(re.search(r"DA (\d+)", d["name"]).group(1)) >= 41)
    pct = round(100 * high / total_da) if total_da else 0
    quality = (f"Approximately {pct}% of referring domains fall within the DA 41–100 range, reflecting a strong and "
               "credible backlink profile supported by a substantial number of high-quality, authoritative referring websites.")

    # ---- monthly growth
    growth = []
    for r, v in sec_rows("monthly growth"):
        mv = col(v, 0)
        pm = parse_month(mv)
        mm = MON_RE.match(text(mv)) if not pm else None
        if not pm and not mm:
            problems.append(where("Monthly Growth", r) + f": month '{text(mv)}' should look like 'Feb 2026'.")
            continue
        idx = pm[0] if pm else ud.mi(mm.group(1))
        growth.append({"month": MONTHS[idx][:3].title(), "backlinks": number(col(v, 1), where("Monthly Growth", r))})
    if growth and growth[-1]["month"] != MONTHS[m_idx][:3].title():
        warnings.append(f"Monthly Growth ends at {growth[-1]['month']}, not the report month ({MONTHS[m_idx][:3].title()}).")

    # ---- keyword lists
    t5, p1 = [], []
    for r, v in sec_rows("keyword lists"):
        lst, kw = text(col(v, 0)).lower().replace(" ", ""), text(col(v, 1))
        if not kw:
            continue
        item = {"keyword": kw, "base": number(col(v, 2), where("Keyword Lists", r) + " baseline rank"),
                "cur": number(col(v, 3), where("Keyword Lists", r) + " current rank"), "url": text(col(v, 4))}
        if lst in ("top5",):
            t5.append(item)
        elif lst in ("page1", "firstpage"):
            p1.append(item)
        else:
            problems.append(where("Keyword Lists", r) + f": List must be 'Top 5' or 'Page 1' (found '{text(col(v, 0))}').")

    def url_for(item):
        if item["url"]:
            return item["url"]
        u = ud.keyword_url(item["keyword"], url_cfg)
        if not u:
            warnings.append(f"Keyword '{item['keyword']}' is not linked to any URL in data/url-config.json.")
        return u or ""

    t5_cur = [x for x in t5 if x["cur"] is not None]
    p1_cur = [x for x in p1 if x["cur"] is not None]
    p1_base = [x for x in p1 if x["base"] is not None]
    for x in p1:
        if x["cur"] is not None and x["cur"] > 10:
            warnings.append(f"Page 1 keyword '{x['keyword']}' has current rank {x['cur']} (page 1 is rank 1 to 10).")
    for x in t5_cur:
        if x["cur"] > 5:
            warnings.append(f"Top 5 keyword '{x['keyword']}' has current rank {x['cur']} (Top 5 is rank 1 to 5).")
    keyword_ranking = {
        "topFive": {"baseline": number(get(r"^keywords in top 5 \(baseline"), "Overview: Top 5 (baseline)"),
                    "current": number(get(r"^keywords in top 5 \(current"), "Overview: Top 5 (current)"),
                    "keywords": [{"keyword": x["keyword"], "url": url_for(x), "baselineRank": x["base"],
                                  "currentRank": x["cur"]} for x in t5_cur]},
        "firstPage": {"baseline": number(get(r"^keywords on page 1 \(baseline"), "Overview: Page 1 (baseline)"),
                      "current": number(get(r"^keywords on page 1 \(current"), "Overview: Page 1 (current)"),
                      "baselineKeywords": [{"keyword": x["keyword"], "url": url_for(x), "rank": x["base"]} for x in p1_base],
                      "currentKeywords": [{"keyword": x["keyword"], "url": url_for(x), "rank": x["cur"]} for x in p1_cur]},
    }
    for key, lst, label in (("topFive", t5_cur, "Top 5"), ("firstPage", p1_cur, "Page 1")):
        n = keyword_ranking[key]["current"]
        if n is not None and n != len(lst):
            warnings.append(f"Keywords in {label}: Overview says {n} but Keyword Lists has {len(lst)} current keywords.")

    # ---- URL rankings -> performance summary
    blocks, cur = [], None
    month_cols = []
    hdr = (secs.get("url rankings") or {}).get("header")
    if hdr:
        month_cols = [i for i, h in enumerate(hdr) if i >= 2 and text(h)]
        last = parse_month(hdr[month_cols[-1]]) if month_cols else None
        if month_cols and last and last != (m_idx, year):
            warnings.append(f"URL Rankings: last month column is '{text(hdr[month_cols[-1]])}', not the report month.")
        for r, v in sec_rows("url rankings"):
            u, metric = text(col(v, 0)), text(col(v, 1))
            if u:
                cur = {"url": u, "total": None, "pa": None, "keywords": [], "row": r}
                blocks.append(cur)
            if not metric:
                continue
            if cur is None:
                problems.append(where("URL Rankings", r) + f": '{metric}' has no URL above it in column A.")
                continue
            vals = [number(col(v, i), where("URL Rankings", r) + f" ({metric})") for i in month_cols]
            low = metric.lower()
            if low.startswith("total backlinks"):
                cur["total"] = vals
            elif low.startswith("page authority"):
                cur["pa"] = vals
            else:
                cur["keywords"].append({"name": metric, "ranks": vals})
    by_url = {b["url"].rstrip("/").lower(): b for b in blocks}
    summary = []
    for u in url_cfg:
        b = by_url.get(u["url"].rstrip("/").lower())
        if not b:
            problems.append(f"URL Rankings: no block for {u['url']}.")
            continue
        summary.append(ud.summary_row(u["url"], b))
        sheet_kws = {k["name"].lower() for k in b["keywords"]}
        miss = [k for k in u["keywords"] if k.lower() not in sheet_kws]
        if miss:
            warnings.append(f"URL Rankings: {u['url']} has no row for " + ", ".join(f"'{k}'" for k in miss) + ".")
    cfg_urls = {u["url"].rstrip("/").lower() for u in url_cfg}
    for b in blocks:
        if b["url"].rstrip("/").lower() not in cfg_urls:
            warnings.append(f"URL Rankings: {b['url']} is not in data/url-config.json; add it (with its keywords) to show it.")
    if kpis["urlsTracked"] is not None and kpis["urlsTracked"] != len(blocks):
        warnings.append(f"URLs tracked: Overview says {kpis['urlsTracked']}, URL Rankings has {len(blocks)} URLs.")

    # ---- key findings
    key_findings = []
    for r, v in sec_rows("key findings"):
        t = md(col(v, 1)) or (md(col(v, 0)) if not isinstance(col(v, 0), (int, float)) else "")
        if t:
            key_findings.append({"description": t})

    # ---- highlights (+ screenshots)
    pics = parse_highlight_images(ws_month)
    hl_rows = sec_rows("highlights")
    hl_start = (secs.get("highlights") or {}).get("start", 10 ** 9)
    import zipfile
    with zipfile.ZipFile(args.xlsx) as z:
        if any(n.startswith("xl/richData/") for n in z.namelist()):
            warnings.append("Some pictures were added with 'Place in Cell'; those cannot be read. Paste them so they float "
                            "over the cells instead (Excel: right-click the picture > Place over Cells).")
    extracted = []  # (bytes or source path, file name)
    highlights, llm = [], []
    counters = {"highlight": 0, "llm": 0}
    for r, v in hl_rows:
        typ, title, desc = text(col(v, 0)).lower(), text(col(v, 1)), text(col(v, 2))
        fname = text(col(v, 8))
        if not title and not desc:
            if r in pics:
                warnings.append(where("Highlights", r) + f" has a picture but no title or description; ignored.")
            continue
        kind = "llm" if typ.startswith("llm") else ("highlight" if typ.startswith("highlight") else None)
        if not kind:
            problems.append(where("Highlights", r) + f": Type must be 'Highlight' or 'LLM Highlight' (found '{text(col(v, 0))}').")
            continue
        counters[kind] += 1
        n = counters[kind]
        label = "LLM highlight" if kind == "llm" else "Highlight"
        base = f"{kind}-{n}-{ud.slugify(title, 30)}"
        image = None
        if r in pics:
            data, ext = pics[r]
            extracted.append((data, base + ext))
            image = f"/reports/{month_key}/{base}{ext}"
        elif fname:
            src = os.path.join(args.images_dir, fname) if args.images_dir else None
            if src and os.path.exists(src):
                ext = os.path.splitext(fname)[1].lower() or ".png"
                extracted.append((src, base + ext))
                image = f"/reports/{month_key}/{base}{ext}"
            else:
                problems.append(f"{label} {n} ('{title}'): screenshot file '{fname}' was not attached.")
        else:
            warnings.append(f"{label} {n} ('{title}') has no screenshot (paste it on row {r} of the Highlights section, from column I).")
        if not title:
            warnings.append(f"{label} {n} has no title.")
        if not desc:
            warnings.append(f"{label} {n} ('{title}') has no description.")
        (llm if kind == "llm" else highlights).append({"title": title, "description": desc, "image": image})
    stray = sorted(set(pics) - {r for r, _ in hl_rows})
    for r in stray:
        where_ = "in the Highlights section" if r > hl_start else "above the Highlights section"
        warnings.append(f"A picture sits on row {r} ({where_}) where there is no highlight; it is ignored.")
    if not highlights:
        warnings.append("No highlights found in the Highlights section.")

    sheet_url = text(get(r"^monthly backlinks sheet")) or None
    out_path = os.path.join(DATA, "report.json")
    if not sheet_url:
        warnings.append("No monthly backlinks sheet link in Overview; keeping the previous one.")
        if os.path.exists(out_path):
            sheet_url = json.load(open(out_path, encoding="utf-8")).get("acquisitionSheetUrl")

    # ---- link name and report date
    default_link = f"{site['linkPrefix']}-{MONTHS[m_idx]}{year}"
    link_name = default_link
    wanted = args.link_name or text(get(r"^dashboard link name"))
    if wanted:
        raw = re.sub(r"\.vercel\.app$", "", re.sub(r"^https?://", "", wanted.strip().lower()).split("/")[0])
        clean = re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9-]", "-", raw)).strip("-")[:63].strip("-")
        if not clean:
            problems.append(f"Link name '{wanted}' has no usable characters.")
        else:
            if clean != raw:
                warnings.append(f"Link name changed to '{clean}' (web addresses can only use a-z, 0-9 and '-').")
            link_name = clean
    rd = get(r"^report date")
    if args.report_date:
        report_date = args.report_date
    elif isinstance(rd, (dt.date, dt.datetime)):
        report_date = f"{rd:%B} {rd.day}, {rd.year}"
    elif text(rd):
        report_date = text(rd)
    else:
        d = dt.date.today()
        report_date = f"{d:%B} {d.day}, {d.year}"

    meta = {
        "client": site["client"],
        "reportMonth": month_key,
        "reportDate": report_date,
        "reportTitle": site["reportTitle"],
        "reportSubtitle": site["reportSubtitle"],
        "baselineLabel": f"{MONTHS[bm[0]][:3].title()} {bm[1]} (Baseline)" if bm else "Baseline",
        "currentLabel": f"{MONTHS[m_idx].title()} {year}",
        "currentMonthName": MONTHS[m_idx].title(),
        "currentMonthAbbr": MONTHS[m_idx][:3].title(),
        "linkName": link_name,
        "sourceFile": os.path.basename(args.xlsx),
        "generatedAt": dt.datetime.now().isoformat(timespec="seconds"),
    }
    report_json = {
        "meta": meta,
        "kpis": kpis,
        "businessImpact": categories,
        "referringDomains": {"data": da, "qualityStatement": quality},
        "monthlyBacklinkGrowth": growth,
        "keywordRanking": keyword_ranking,
        "performanceSummary": summary,
        "acquisitionSheetUrl": sheet_url,
        "keyFindings": key_findings,
        "highlights": highlights,
        "llmHighlights": llm,
    }

    # ---- cross checks
    if kpis.get("totalBacklinks") and total_da and total_da != kpis["totalBacklinks"]:
        warnings.append(f"DA split adds up to {total_da} but actual total backlinks is {kpis['totalBacklinks']}.")
    if growth and kpis.get("totalBacklinks"):
        s_growth = sum(g["backlinks"] or 0 for g in growth)
        if s_growth != kpis["totalBacklinks"]:
            notes.append(f"Monthly growth adds up to {s_growth} (actual total backlinks {kpis['totalBacklinks']}; "
                         "the difference is backlinks from before the first month shown).")
    if not key_findings:
        warnings.append("No key findings in the Key Findings sheet.")

    if not args.dry_run and not problems:
        if os.path.exists(out_path):
            prev = json.load(open(out_path, encoding="utf-8"))
            pm = prev.get("meta", {}).get("reportMonth")
            if pm and pm != month_key:
                os.makedirs(os.path.join(DATA, "history"), exist_ok=True)
                shutil.copy(out_path, os.path.join(DATA, "history", f"{pm}.json"))
                notes.append(f"Archived previous report to data/history/{pm}.json")
        if os.path.isdir(img_dir):
            shutil.rmtree(img_dir)   # this month's screenshots come only from this workbook
        os.makedirs(img_dir, exist_ok=True)
        for src, fname in extracted:
            dest = os.path.join(img_dir, fname)
            if isinstance(src, (bytes, bytearray)):
                with open(dest, "wb") as f:
                    f.write(src)
            else:
                shutil.copy(src, dest)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report_json, f, ensure_ascii=False, indent=2)
            f.write("\n")
        notes.append(f"Wrote data/report.json and {len(extracted)} images to public/reports/{month_key}/")
    elif not args.dry_run:
        notes.append("Nothing written because of the problems below.")

    notes.insert(0, f"Link: https://{link_name}.vercel.app")
    notes.insert(0, f"Report month: {meta['currentLabel']} | URLs: {len(summary)} | Top 5: "
                    f"{keyword_ranking['topFive']['current']} | Page 1: {keyword_ranking['firstPage']['current']} | "
                    f"highlights: {len(highlights)} | LLM highlights: {len(llm)} | images: {len(extracted)}")
    report()
    sys.exit(2 if problems else 0)


if __name__ == "__main__":
    main()
