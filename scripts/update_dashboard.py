#!/usr/bin/env python3
"""Turn the monthly Splashtop "Backlink Performance Dashboard data" Word doc into data/report.json.

Usage (run from the dashboard folder):
    python3 scripts/update_dashboard.py "monthly-docs/<file>.docx" [--report-date "October 8, 2026"] [--link-name <name>] [--dry-run]

What it does:
  1. Reads the Word doc (standard library only, nothing to install), including its tables and bold text.
  2. Pulls every number and text the dashboard shows and calculates the derived values
     (PA change, best/worst keyword move, overall status, DA quality statement).
  3. Extracts the highlight screenshots embedded in the doc into public/reports/<YYYY-MM>/.
  4. Archives the previous data/report.json into data/history/ and writes the new one.
  5. Prints a validation report. Anything under "PROBLEMS" must be fixed before publishing.

Exit code 0 = no problems, 2 = problems found.
Config files it reads: data/site-config.json, data/url-config.json, data/business-impact.json.
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx_blocks import read_blocks, read_media, read_tables  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
PUBLIC = os.path.join(ROOT, "public")

MONTHS = ["january", "february", "march", "april", "may", "june", "july",
          "august", "september", "october", "november", "december"]
MON = r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*"
# "Sep’26", "Sep' 26", "Dec‘25", "Sep,26", "Sep 2026"
MONTH_YY = re.compile(MON + r"\s*[\'’‘`,]?\s*(\d{4}|\d{2})\b", re.I)
DASH = r"\s*[-–—:]\s*"

problems, warnings, notes = [], [], []


def mi(token):
    return [m[:3] for m in MONTHS].index(token[:3].lower())


def norm(s):
    return re.sub(r"\s+", " ", (s or "").replace(" ", " ")).strip()


def num(s):
    s = (s or "").strip().replace(",", "")
    return int(s) if re.fullmatch(r"-?\d+", s) else None


def slugify(s, n=40):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:n].strip("-") or "image"


def lines_of(blocks):
    """Flatten blocks into (line, block_index) pairs, splitting on line breaks."""
    out = []
    for i, b in enumerate(blocks):
        for ln in b["text"].split("\n"):
            t = norm(ln)
            if t:
                out.append((t, i))
    return out


def find_block(blocks, pred, start=0):
    for i in range(start, len(blocks)):
        if pred(norm(blocks[i]["text"]).lower()):
            return i
    return -1


def month_label(line):
    """'Sep’26' alone on a line -> (month_idx, yy); else None."""
    m = re.fullmatch(MON + r"\s*[\'’‘`,]?\s*(\d{2}|\d{4})", line.strip(), re.I)
    if m:
        return mi(m.group(1)), m.group(2)[-2:]
    return None


def month_count(line):
    """'Dec’25 - 0' -> (month_idx, yy, 0); else None."""
    m = re.fullmatch(MON + r"\s*[\'’‘`,]?\s*(\d{2}|\d{4})" + DASH + r"(\d+)", line.strip(), re.I)
    if m:
        return mi(m.group(1)), m.group(2)[-2:], int(m.group(3))
    return None


def kw_item(line):
    m = re.fullmatch(r"(.+?)" + DASH + r"(\d+)", line.strip())
    if m and not month_label(m.group(1)):
        return norm(m.group(1)), int(m.group(2))
    return None


# ------------------------------------------------------------------ sections

def parse_report_month(blocks):
    for b in blocks[:6]:
        m = MONTH_YY.search(b["text"])
        if m:
            return mi(m.group(1)), int(("20" + m.group(2)) if len(m.group(2)) == 2 else m.group(2))
    problems.append("Could not find the report month at the top of the doc "
                    "(expected a title like 'Backlink Performance Analysis (Sep’ 26)').")
    return None, None


def number_after(lines, label_re):
    for k, (t, _) in enumerate(lines):
        m = re.search(label_re, t, re.I)
        if m:
            rest = t[m.end():]
            n = re.search(r"\d[\d,]*", rest)
            if n:
                return num(n.group(0))
            for t2, _ in lines[k + 1:k + 3]:
                n = re.fullmatch(r"[\d,]+", t2)
                if n:
                    return num(t2)
            return None
    return None


def parse_kpis(lines):
    pats = {"urlsTracked": r"^urls tracked", "keywordsTracked": r"^keywords tracked",
            "planTotalBacklinks": r"^plan total backlinks[^)]*\)?", "totalBacklinks": r"^actual total backlinks[^)]*\)?"}
    out = {}
    for key, pat in pats.items():
        v = number_after(lines, pat)
        if v is None:
            problems.append(f"KPI missing in doc: {key}")
        out[key] = v
    return out


def section_lines(lines, start_re, end_re):
    s = next((k for k, (t, _) in enumerate(lines) if re.search(start_re, t, re.I)), None)
    if s is None:
        return []
    e = next((k for k in range(s + 1, len(lines)) if re.search(end_re, lines[k][0], re.I)), len(lines))
    return lines[s + 1:e]


def month_lists(sec):
    """Collect 'keyword - N' lists grouped under month labels, plus 'Month'yy - N' counts."""
    lists, counts, cur = {}, {}, None
    for t, _ in sec:
        c = month_count(t)
        if c:
            counts[(c[0], c[1])] = c[2]
            continue
        # a line may start with a month label followed by an item on the same line
        m = re.match(MON + r"\s*[\'’‘`,]?\s*(\d{2})\s*$", t, re.I)
        if m:
            cur = (mi(m.group(1)), m.group(2))
            lists.setdefault(cur, [])
            continue
        it = kw_item(t)
        if it and cur is not None:
            lists[cur].append(it)
    return lists, counts


def split_base_current(d, cur_key, what):
    """d: {(m,yy): value}. Return (baseline, current) by matching the report month."""
    if cur_key not in d:
        problems.append(f"{what}: no data for the report month.")
        return None, None
    others = [k for k in d if k != cur_key]
    if len(others) != 1:
        problems.append(f"{what}: expected exactly one baseline month besides the report month, found {len(others)}.")
        return None, d[cur_key]
    return d[others[0]], d[cur_key]


def parse_da(blocks):
    found = []
    for b in blocks:
        for m in re.finditer(r"DA\s*(\d+)\s*[-–]\s*(\d+)" + DASH + r"(\d+)", b["text"]):
            found.append((int(m.group(1)), int(m.group(2)), int(m.group(3))))
    if not found:
        problems.append("Referring domain DA split not found (expected lines like 'DA 41-70 - 317').")
    colors = ["#14b8a6", "#3b82f6", "#22c55e", "#f59e0b"]
    found.sort(key=lambda x: -x[0])
    return [{"name": f"DA {lo}-{hi}", "value": v, "color": colors[i % len(colors)]}
            for i, (lo, hi, v) in enumerate(found)]


def parse_growth(blocks):
    i = find_block(blocks, lambda t: t.startswith("monthly backlink growth"))
    if i < 0:
        problems.append("'Monthly Backlink Growth' section not found.")
        return []
    months, values = [], []
    for b in blocks[i + 1:i + 6]:
        t = b["text"]
        if not months:
            ms = re.findall(MON, t, re.I)
            if len(ms) >= 2:
                months = [mi(x) for x in ms]
                continue
        if "total backlinks" in t.lower():
            values = [num(x) for x in re.findall(r"\b\d+\b", t.lower().split("total backlinks", 1)[1])]
            break
    if not months or not values:
        problems.append("Monthly backlink growth: could not read the months and the 'Total Backlinks' numbers.")
        return []
    if len(months) != len(values):
        problems.append(f"Monthly backlink growth: {len(months)} months but {len(values)} values.")
    return [{"month": MONTHS[m][:3].title(), "backlinks": v} for m, v in zip(months, values)]


def parse_urls(lines):
    sec = section_lines(lines, r"^tracked urls", r"^performance summary")
    return [t.split()[0] for t, _ in sec if re.match(r"https?://", t)]


def parse_tables(path):
    out = []
    for rows in read_tables(path):
        if not rows or len(rows) < 2:
            continue
        header = rows[0]
        if not any(MONTH_YY.search(c or "") for c in header[1:]):
            continue
        tbl = {"total": None, "pa": None, "keywords": []}
        for r in rows[1:]:
            if not r:
                continue
            name = norm(r[0])
            vals = [None if (c or "").strip() in ("", "-", "–", "—", "N/A") else num(c) for c in r[1:]]
            low = name.lower()
            if low.startswith("total backlinks"):
                tbl["total"] = vals
            elif low.startswith("page authority"):
                tbl["pa"] = vals
            elif name:
                tbl["keywords"].append({"name": name, "ranks": vals})
        out.append(tbl)
    return out


def match_tables(tables, url_cfg):
    """Assign each ranking table to a URL by overlap of keyword names."""
    cfg_sets = [{k.lower() for k in u["keywords"]} for u in url_cfg]
    scored = []
    for ti, t in enumerate(tables):
        kws = {k["name"].lower() for k in t["keywords"]}
        for ui, s in enumerate(cfg_sets):
            ov = len(kws & s)
            if ov:
                scored.append((ov / max(len(kws | s), 1), ov, ti, ui))
    scored.sort(reverse=True)
    t2u, used_u = {}, set()
    for _, _, ti, ui in scored:
        if ti in t2u or ui in used_u:
            continue
        t2u[ti] = ui
        used_u.add(ui)
    for ti, t in enumerate(tables):
        if ti not in t2u:
            warnings.append("A ranking table with keywords " + ", ".join(k["name"] for k in t["keywords"]) +
                            " does not match any tracked URL in data/url-config.json, so it is not shown.")
    return {ui: tables[ti] for ti, ui in t2u.items()}


def moves(tbl):
    out = []
    for k in tbl["keywords"]:
        first, last = k["ranks"][0] if k["ranks"] else None, k["ranks"][-1] if k["ranks"] else None
        if first is None or last is None:
            continue
        out.append({"keyword": k["name"], "change": first - last})
    return out


def summary_row(url, tbl):
    """Best = biggest improvement (+N), worst = biggest drop (-N); keywords without a
    baseline or current rank are skipped. Status: Positive if anything improved,
    Negative if only drops, Stable if nothing moved."""
    mv = moves(tbl)
    ups = [m for m in mv if m["change"] > 0]
    downs = [m for m in mv if m["change"] < 0]
    best = max(ups, key=lambda m: m["change"]) if ups else None
    worst = min(downs, key=lambda m: m["change"]) if downs else None
    pa = [v for v in (tbl["pa"] or []) if v is not None]
    status = "Positive" if best else ("Negative" if worst else "Stable")
    return {
        "url": url,
        "paChange": (pa[-1] - pa[0]) if len(pa) >= 2 else 0,
        "bestKeywordMove": {"keyword": best["keyword"].lower(), "change": f"+{best['change']}"} if best else None,
        "worstKeywordMove": {"keyword": worst["keyword"].lower(), "change": str(worst["change"])} if worst else None,
        "overallStatus": status,
    }


def keyword_url(keyword, url_cfg):
    k = keyword.lower()
    for u in url_cfg:
        if u["keywords"] and u["keywords"][0].lower() == k:
            return u["url"]
    for u in url_cfg:
        if k in (x.lower() for x in u["keywords"]):
            return u["url"]
    return None


def paragraphs_between(blocks, start_pred, end_pred):
    s = find_block(blocks, start_pred)
    if s < 0:
        return [], -1
    e = find_block(blocks, end_pred, s + 1)
    return blocks[s + 1:(e if e >= 0 else len(blocks))], s


def parse_key_findings(blocks):
    sec, s = paragraphs_between(blocks, lambda t: t == "key findings", lambda t: t.startswith("llm highlights")
                                or t == "highlights")
    if s < 0:
        problems.append("'Key Findings' section not found.")
        return []
    items = []
    for b in sec:
        t, md = norm(b["text"]), b.get("md", b["text"]).strip()
        if not t:
            continue
        # a paragraph split in the middle of a word or sentence continues the previous one
        if items and (not re.search(r"[.!?]\s*\**\s*$", items[-1]["text"]) or t[0].islower()):
            joiner = "" if (re.search(r"[A-Za-z]\**$", items[-1]["md"]) and t[0].islower()
                            and not items[-1]["text"].endswith(" ")) else " "
            items[-1]["md"] = (items[-1]["md"] + joiner + md)
            items[-1]["text"] += joiner + t
            continue
        items.append({"text": t, "md": md})
    out = []
    for it in items:
        md = re.sub(r"\*\*\*\*", "", it["md"])          # merge **a****b** -> **ab**
        md = re.sub(r"\*\*\s+\*\*", " ", md)
        md = re.sub(r"(\S)\s+\*\*(?=\s|$)", r"\1** ", md)  # keep spaces outside bold
        md = re.sub(r"([,;:])\*\*", r"**\1", md)          # "pages,**" -> "pages**,"
        md = re.sub(r"\s{2,}", " ", md).strip()
        out.append({"description": md})
    if not out:
        problems.append("No key findings found under 'Key Findings'.")
    return out


def parse_cards(blocks, start_pred, end_pred, label, images_out, prefix):
    """Title / screenshot / description cards (Highlights and LLM Highlights)."""
    sec, s = paragraphs_between(blocks, start_pred, end_pred)
    if s < 0:
        warnings.append(f"'{label}' section not found; it will be empty.")
        return []
    cards, pending_imgs = [], []
    for b in sec:
        for img in b["images"]:
            if cards and cards[-1]["image"] is None and not cards[-1]["description"]:
                cards[-1]["image"] = img
            elif cards and cards[-1]["image"] is None:
                cards[-1]["image"] = img
            else:
                pending_imgs.append(img)
        for ln in b["text"].split("\n"):
            t = norm(ln)
            if not t:
                continue
            is_title = (len(t) <= 110 and not re.search(r"[.!?]$", t)) or not cards or (
                cards[-1]["description"] and len(t) <= 110)
            if is_title and not (cards and not cards[-1]["description"] and len(t) > 110):
                cards.append({"title": t.rstrip(":"), "description": "",
                              "image": pending_imgs.pop(0) if pending_imgs else None})
            else:
                cards[-1]["description"] = (cards[-1]["description"] + " " + t).strip()
    for n, c in enumerate(cards, 1):
        if c["image"] is None:
            problems.append(f"{label} '{c['title']}' has no screenshot.")
        if not c["description"]:
            warnings.append(f"{label} '{c['title']}' has no description.")
        c["image"] = images_out(c["image"], f"{prefix}-{n}-" + slugify(c["title"], 30))
    return cards


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docx")
    ap.add_argument("--report-date", help='Date shown at the top, e.g. "October 8, 2026". Default: today.')
    ap.add_argument("--link-name", help="Optional custom Vercel link name. Default: <linkPrefix>-<month><year>.")
    ap.add_argument("--dry-run", action="store_true", help="Validate only; write nothing.")
    args = ap.parse_args()

    site = json.load(open(os.path.join(DATA, "site-config.json"), encoding="utf-8"))
    url_cfg = json.load(open(os.path.join(DATA, "url-config.json"), encoding="utf-8"))["urls"]
    cat_cfg = json.load(open(os.path.join(DATA, "business-impact.json"), encoding="utf-8"))["categories"]

    blocks = read_blocks(args.docx)
    lines = lines_of(blocks)
    m_idx, year = parse_report_month(blocks)
    if m_idx is None:
        report()
        sys.exit(2)
    yy = str(year)[2:]
    cur_key = (m_idx, yy)
    month_key = f"{year}-{m_idx + 1:02d}"
    img_dir = os.path.join(PUBLIC, "reports", month_key)
    extracted = []

    def images_out(member, name):
        if not member:
            return None
        ext = os.path.splitext(member)[1].lower() or ".png"
        extracted.append((member, f"{name}{ext}"))
        return f"/reports/{month_key}/{name}{ext}"

    kpis = parse_kpis(lines)

    # ---- business impact (keyword lists for two months + 3 takeaways)
    bi_sec = section_lines(lines, r"^business impact of backlinks", r"^add this key ?takeaway|^referring domains")
    bi_lists, _ = month_lists(bi_sec)
    base_list, cur_list = split_base_current(bi_lists, cur_key, "Business impact keyword lists")
    base_map = {k.lower(): v for k, v in (base_list or [])}
    cur_map = {k.lower(): v for k, v in (cur_list or [])}
    takeaways = [norm(t) for t, _ in section_lines(lines, r"^add this key ?takeaway", r"^referring domains")]
    categories = []
    used = set()
    for c in cat_cfg:
        rows = []
        for k in c["keywords"]:
            kl = k.lower()
            if kl in cur_map or kl in base_map:
                rows.append({"keyword": k, "baseline": base_map.get(kl), "current": cur_map.get(kl)})
                used.add(kl)
            else:
                warnings.append(f"Business impact keyword '{k}' is not in the doc; it is left out of its chart.")
        categories.append({"title": c["title"], "rows": rows, "insight": ""})
    extra = [k for k, _ in (cur_list or []) if k.lower() not in used]
    for k in extra:
        warnings.append(f"Business impact keyword '{k}' is not in data/business-impact.json; added to the last chart.")
        categories[-1]["rows"].append({"keyword": k, "baseline": base_map.get(k.lower()), "current": cur_map.get(k.lower())})
    for i, c in enumerate(categories):
        c["insight"] = takeaways[i] if i < len(takeaways) else ""
        if not c["insight"]:
            warnings.append(f"No key takeaway found for the '{c['title'].strip()}' chart.")
        for r in c["rows"]:
            if r["baseline"] is None or r["current"] is None:
                warnings.append(f"Business impact keyword '{r['keyword']}' is missing a baseline or current rank.")
    if len(takeaways) > len(categories):
        warnings.append(f"{len(takeaways)} key takeaways for {len(categories)} charts; extra ones are ignored.")

    # ---- referring domains
    da = parse_da(blocks)
    total_da = sum(d["value"] for d in da)
    high = sum(d["value"] for d in da if int(re.search(r"DA (\d+)", d["name"]).group(1)) >= 41)
    pct = round(100 * high / total_da) if total_da else 0
    quality = (f"Approximately {pct}% of referring domains fall within the DA 41–100 range, reflecting a strong and "
               "credible backlink profile supported by a substantial number of high-quality, authoritative referring websites.")

    growth = parse_growth(blocks)

    # ---- keyword ranking performance (Top 5 and Page 1)
    t5_sec = section_lines(lines, r"^keywords in top 5", r"^keywords on first page")
    p1_sec = section_lines(lines, r"^keywords on first page", r"^tracked urls")
    # the "Keywords on First Page" heading line may carry the baseline count on the next lines
    t5_lists, t5_counts = month_lists(t5_sec)
    p1_head = next((t for t, _ in lines if re.match(r"^keywords on first page", t, re.I)), "")
    p1_lists, p1_counts = month_lists([(p1_head, -1)] + p1_sec)
    t5_base_n, t5_cur_n = split_base_current(t5_counts, cur_key, "Keywords in Top 5 counts")
    p1_base_n, p1_cur_n = split_base_current(p1_counts, cur_key, "Keywords on First Page counts")
    t5_base, t5_cur = split_base_current(t5_lists, cur_key, "Keywords in Top 5 lists")
    p1_base, p1_cur = split_base_current(p1_lists, cur_key, "Keywords on First Page lists")

    def with_url(items):
        out = []
        for k, r in items or []:
            u = keyword_url(k, url_cfg)
            if not u:
                warnings.append(f"Keyword '{k}' is not linked to any URL in data/url-config.json.")
            out.append({"keyword": k, "url": u or "", "rank": r})
        return out

    t5_base_map = {k.lower(): r for k, r in (t5_base or [])}
    keyword_ranking = {
        "topFive": {"baseline": t5_base_n, "current": t5_cur_n,
                    "keywords": [{"keyword": x["keyword"], "url": x["url"],
                                  "baselineRank": t5_base_map.get(x["keyword"].lower()), "currentRank": x["rank"]}
                                 for x in with_url(t5_cur)]},
        "firstPage": {"baseline": p1_base_n, "current": p1_cur_n,
                      "baselineKeywords": with_url(p1_base), "currentKeywords": with_url(p1_cur)},
    }
    if t5_cur_n is not None and len(t5_cur or []) != t5_cur_n:
        warnings.append(f"Keywords in Top 5: doc says {t5_cur_n} but lists {len(t5_cur or [])} keywords.")
    if p1_cur_n is not None and len(p1_cur or []) != p1_cur_n:
        warnings.append(f"Keywords on First Page: doc says {p1_cur_n} but lists {len(p1_cur or [])} keywords.")

    # ---- per-URL tables -> performance summary
    doc_urls = parse_urls(lines)
    tables = parse_tables(args.docx)
    mapping = match_tables(tables, url_cfg)
    summary = []
    for ui, u in enumerate(url_cfg):
        if ui not in mapping:
            problems.append(f"No ranking table in the doc for {u['url']} (matched by its keywords in data/url-config.json).")
            continue
        summary.append(summary_row(u["url"], mapping[ui]))
    cfg_urls = {u["url"].rstrip("/") for u in url_cfg}
    for u in doc_urls:
        if u.rstrip("/") not in cfg_urls:
            warnings.append(f"Tracked URL {u} is not in data/url-config.json; add it (with its keywords) to show it.")
    if kpis.get("urlsTracked") is not None and kpis["urlsTracked"] != len(doc_urls):
        warnings.append(f"URLs tracked: doc says {kpis['urlsTracked']}, the Tracked URLs list has {len(doc_urls)}.")

    # ---- sheet link, key findings, highlights
    sheet = None
    s = find_block(blocks, lambda t: t.startswith("implementation details"))
    for b in blocks[s + 1:s + 4] if s >= 0 else []:
        if b["links"]:
            sheet = b["links"][0]["url"]
            break
    if not sheet:
        warnings.append("No sheet link under 'Implementation Details'; keeping the previous one.")
    key_findings = parse_key_findings(blocks)
    llm = parse_cards(blocks, lambda t: t.startswith("llm highlights"), lambda t: t == "highlights",
                      "LLM highlight", images_out, "llm")
    highlights = parse_cards(blocks, lambda t: t == "highlights", lambda t: t.startswith("llm highlights"),
                             "Highlight", images_out, "highlight")

    # ---- link name
    default_link = f"{site['linkPrefix']}-{MONTHS[m_idx]}{year}"
    link_name = default_link
    if args.link_name:
        raw = re.sub(r"\.vercel\.app$", "", re.sub(r"^https?://", "", args.link_name.strip().lower()).split("/")[0])
        clean = re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9-]", "-", raw)).strip("-")[:63].strip("-")
        if not clean:
            problems.append(f"Link name '{args.link_name}' has no usable characters.")
        else:
            if clean != raw:
                warnings.append(f"Link name changed to '{clean}' (web addresses can only use a-z, 0-9 and '-').")
            link_name = clean

    base_m = next((k for k in t5_counts if k != cur_key), None)
    meta = {
        "client": site["client"],
        "reportMonth": month_key,
        "reportDate": args.report_date or (lambda d: f"{d:%B} {d.day}, {d.year}")(dt.date.today()),
        "reportTitle": site["reportTitle"],
        "reportSubtitle": site["reportSubtitle"],
        "baselineLabel": f"{MONTHS[base_m[0]][:3].title()} 20{base_m[1]} (Baseline)" if base_m else "Baseline",
        "currentLabel": f"{MONTHS[m_idx].title()} {year}",
        "currentMonthName": MONTHS[m_idx].title(),
        "currentMonthAbbr": MONTHS[m_idx][:3].title(),
        "linkName": link_name,
        "sourceFile": os.path.basename(args.docx),
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
        "acquisitionSheetUrl": sheet,
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

    out_path = os.path.join(DATA, "report.json")
    if sheet is None and os.path.exists(out_path):
        report_json["acquisitionSheetUrl"] = json.load(open(out_path, encoding="utf-8")).get("acquisitionSheetUrl")

    if not args.dry_run:
        if os.path.exists(out_path):
            prev = json.load(open(out_path, encoding="utf-8"))
            pm = prev.get("meta", {}).get("reportMonth")
            if pm and pm != month_key:
                os.makedirs(os.path.join(DATA, "history"), exist_ok=True)
                shutil.copy(out_path, os.path.join(DATA, "history", f"{pm}.json"))
                notes.append(f"Archived previous report to data/history/{pm}.json")
        os.makedirs(img_dir, exist_ok=True)
        for member, fname in extracted:
            with open(os.path.join(img_dir, fname), "wb") as f:
                f.write(read_media(args.docx, member))
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report_json, f, ensure_ascii=False, indent=2)
            f.write("\n")
        notes.append(f"Wrote data/report.json and {len(extracted)} images to public/reports/{month_key}/")

    notes.insert(0, f"Link: https://{link_name}.vercel.app")
    notes.insert(0, f"Report month: {meta['currentLabel']} | URLs: {len(summary)} | Top 5: {t5_cur_n} | "
                    f"Page 1: {p1_cur_n} | highlights: {len(highlights)} | LLM highlights: {len(llm)} | "
                    f"images: {len(extracted)}")
    report()
    sys.exit(2 if problems else 0)


def report():
    print("=" * 70)
    for n in notes:
        print("OK  ", n)
    if warnings:
        print("\nWARNINGS (check these, publishing is allowed):")
        for w in warnings:
            print("  -", w)
    if problems:
        print("\nPROBLEMS (fix the Word doc and run again before publishing):")
        for p in problems:
            print("  -", p)
    if not warnings and not problems:
        print("No warnings.")
    print("=" * 70)


if __name__ == "__main__":
    main()
