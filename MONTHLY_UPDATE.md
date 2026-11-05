# Monthly dashboard update (Splashtop)

Every monthly number, text and screenshot on the dashboard comes from `data/report.json`, generated from the monthly **Excel workbook** (preferred) or the monthly Word doc. Both give the same `report.json`. Nobody edits components or `data/mockdata.ts` by hand. The Claude skill `splashtop-dashboard-monthly-update` runs all of this, including preview, publish and the final link (see `SETUP_AND_TEST.md`).

## Commands (from the repo root)

```
python3 scripts/update_from_excel.py "monthly-data/2026-10 Splashtop Dashboard Data.xlsx" --report-date "November 6, 2026" [--images-dir <folder>] [--dry-run]
python3 scripts/update_dashboard.py "monthly-docs/2026-10 Backlink Performance Dashboard data.docx" --report-date "November 6, 2026" [--dry-run]
python3 scripts/set_link_name.py <name> | --default
python3 scripts/make_preview.py      # portable preview in preview/ (what Claude shows in the chat)
npm run build
```

Both scripts print a report: **PROBLEMS** must be fixed in the Excel sheet / Word doc before publishing; **WARNINGS** should be checked.

## Config files (change rarely)

| File | What it holds |
|---|---|
| `data/site-config.json` | Client name, report title/subtitle, link prefix (`splashtop-backlinking-dashboard`) |
| `data/url-config.json` | Tracked URLs in the order of the Performance Summary table, and each URL's keywords. The doc's per-URL tables have no URL in them, so each table is matched to a URL by its keywords. |
| `data/business-impact.json` | The three Business Impact charts (title + keywords in display order) |

## Calculation rules

- **PA change** = Page Authority in the last month minus the first (baseline) month.
- **Best keyword move** = the keyword with the biggest improvement (baseline rank minus current rank), shown as `(+N)`. `N/A` if nothing improved.
- **Worst keyword move** = the keyword with the biggest drop, shown as `(-N)`. `-` if nothing dropped.
- Keywords with no baseline or no current rank (`-` in the table) are skipped.
- **Overall status**: Good if any keyword improved, Negative if keywords only dropped, Stable if nothing moved.
- **DA quality statement**: share of referring domains with DA 41 or higher, rounded.

## What the script reads from the Word doc

Keep the layout of the September 2026 doc:

| Section | What it needs |
|---|---|
| Title | `Backlink Performance Analysis (Sep’ 26)` (gives the report month) |
| KPIs | `URLs Tracked` 15, `Keywords Tracked` 35, `Plan Total Backlinks (Till Sep)` 455, `Actual Total Backlinks (Till Sep)` 421 |
| Business Impact | Under `Business Impact of Backlinks`: a list for the current month (`Sep’26`, then `keyword - rank` lines) and one for the baseline (`Dec’25`). Then `Add this KeyTakeaway:` with one paragraph per chart, in chart order. |
| DA split | `DA 71 - 100 - 62`, `DA 41-70 - 317`, `DA 25 -40 - 42` |
| Monthly growth | `Monthly Backlink Growth`, a line of months, then `Total Backlinks` with one number per month |
| Keywords in Top 5 | `Dec’25 - 0` / `Sep’26 - 6` counts, then the Dec and Sep keyword lists |
| Keywords on First Page | Same pattern (`Dec‘25 - 4`, `Sep’26 - 8`, then the two lists) |
| Tracked URLs | One URL per line |
| Per-URL tables | One Word table per URL: header row of months, then `Total Backlinks`, one row per keyword, `Page Authority`. `-` means no data. |
| Implementation Details | A hyperlink to the monthly backlinks sheet |
| Key Findings | One paragraph per finding; **bold** text in Word stays bold on the dashboard |
| LLM Highlights | Per item: title line, screenshot, description |
| Highlights | Per item: title line, screenshot, description |

## Excel workbook (replaces the Word doc)

One workbook for all months, like the Word doc's tabs: **one tab per month**, named like `Oct 2026`. `templates/Splashtop Dashboard Data.xlsx` has Aug, Sep and Oct 2026 filled in (each tab rebuilds that month's published dashboard exactly). `templates/Splashtop Dashboard Data - TEMPLATE.xlsx` is blank (one `Mon YYYY` tab to rename). Rebuild both with `scripts/make_excel_template.py` (see its header).

Each month: duplicate last month's tab, rename it (`Nov 2026`), update it, attach the whole workbook. `update_from_excel.py` uses the newest month tab, or the one given with `--month "Sep 2026"` (to redo an older month). In the repo the workbook is kept as `monthly-data/Splashtop Dashboard Data.xlsx` (git history keeps every version).

Inside a month tab the sections sit one under another. Each starts with a green row whose column A is exactly the section name, then a header row, then the data. Keep the green rows and header rows; rows can be added or removed inside a section. Ranks are whole numbers (`12` or `12th`); `101` = not in top 100; blank or `-` = no data.

| Section | Columns | Becomes |
|---|---|---|
| Overview | Field / Value: Report month (same as the tab name), Baseline month, Report date (blank = publishing day), URLs tracked, Keywords tracked, Plan total backlinks, Actual total backlinks, Top 5 baseline/current, Page 1 baseline/current, Monthly backlinks sheet link, Dashboard link name (optional) | KPI cards, header, keyword counts, sheet link, link name |
| Business Impact | Chart, Keyword, Baseline rank, Current rank | The three charts. Chart must be one of the titles in `data/business-impact.json`; rows show in this order |
| Chart Insights | Chart, Insight | Key takeaway under each chart |
| Referring Domains | DA range (`DA 41-70`), Referring domains | DA split + quality statement (% in DA 41-100) |
| Monthly Growth | Month (`Feb 2026`), Backlinks added | Monthly growth chart |
| Keyword Lists | List (`Top 5` / `Page 1`), Keyword, Baseline rank, Current rank, URL (optional) | Keyword ranking lists. Blank URL = found from `data/url-config.json` |
| URL Rankings | URL (first row of each block), Metric (`Total Backlinks`, each keyword, `Page Authority`), one column per month from baseline to current | Performance Summary (PA change, best/worst move, status, same rules as above). URLs must match `data/url-config.json` |
| Key Findings | #, Finding | Key findings; Excel bold is kept as bold |
| Highlights | Type (`Highlight` / `LLM Highlight`), Title, Description, screenshot pasted on the same row from column I (or its file name in column I) | Highlights and LLM highlights with their screenshots (`public/reports/<YYYY-MM>/`) |

Screenshots: a picture belongs to the row its top-left corner sits on. Pictures added with Excel's **Place in Cell** cannot be read; use a normal paste (floating picture). If a picture is not in the tab, put its file name in column I and pass the attached images with `--images-dir`.

Checks: the Overview "Report month" must match the tab name; two tabs for the same month is a problem; if plan and actual totals equal the previous month's tab, the script warns that the tab may not have been updated.
