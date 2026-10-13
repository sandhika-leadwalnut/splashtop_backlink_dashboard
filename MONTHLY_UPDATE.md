# Monthly dashboard update (Splashtop)

Every monthly number, text and screenshot on the dashboard comes from `data/report.json`, generated from the monthly Word doc. Nobody edits components or `data/mockdata.ts` by hand. The Claude skill `splashtop-dashboard-monthly-update` runs all of this, including preview, publish and the final link (see `SETUP_AND_TEST.md`).

## Commands (from the repo root)

```
python3 scripts/update_dashboard.py "monthly-docs/2026-10 Backlink Performance Dashboard data.docx" --report-date "November 6, 2026" [--dry-run]
python3 scripts/set_link_name.py <name> | --default
python3 scripts/make_preview.py      # portable preview in preview/ (what Claude shows in the chat)
npm run build
```

`update_dashboard.py` prints a report: **PROBLEMS** must be fixed in the Word doc before publishing; **WARNINGS** should be checked.

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
