# Splashtop Backlink Dashboard: how the monthly update works

Repo: **https://github.com/sandhika-leadwalnut/splashtop_backlink_dashboard** (one repo for every month)

## The flow

1. **Attach the month's Word doc** in a new Claude chat and type: *Update the Splashtop dashboard with this doc*.
2. **Claude checks the doc** and builds the data and the screenshots (3 highlights + 5 LLM charts in September). You get a short summary plus anything to double-check.
3. **Claude shows you the dashboard in the chat** as a private preview page, exactly as it will look when published (charts, tables, screenshots, links). Nothing is public yet.
4. **Ask for corrections, if any.** Tell Claude what to change, e.g. *"key finding 3 should say 6 keywords"*, *"typo in the TeamViewer highlight"*, *"use this screenshot for LLM highlight 2"* (attach it). Claude applies the changes and refreshes the same preview. Repeat until it looks right.
   For number changes, also fix the Word doc so the records match.
5. **Claude asks for a link name (optional).**
   - Type a name, e.g. `splashtop-backlinking-dashboard-september2026-copy`, or
   - say **skip** to use the default monthly link: `splashtop-backlinking-dashboard-<month><year>`, e.g. `...-october2026`.
6. **Say "yes" to publish.** Claude pushes to GitHub itself. GitHub Actions deploys to Vercel and attaches the link.
7. **Claude waits for the deploy (about 1 to 2 minutes) and gives you the final link in the chat**:
   `https://<link name>.vercel.app`

The preview page is private to the person who ran the update. To let a colleague review it before publishing, use the page's **Share** menu.

Each deployment is a frozen copy. Publishing October never changes September's link. Re-publishing the same month with the same link name replaces only that link (use this for corrections).

Link name rules: lowercase letters, numbers and `-` only (no `_` or spaces), up to 63 characters. Claude fixes small mistakes and warns you if the name looks like another month's link, because publishing would replace that month.

---

## One-time setup

| Step | Status |
|---|---|
| Repo created, code and automation pushed | Done |
| Claude GitHub App has access to this repo | Check: Sandhika may need to add `splashtop_backlink_dashboard` to the Claude app (github.com/apps/claude > Configure > Repository access). |
| Vercel project for this repo | To do: Vercel > Leadwalnut team > **Add New** > **Project** > import `sandhika-leadwalnut/splashtop_backlink_dashboard`, framework **Vite**. The first deploy fails (no month's data yet); ignore it. |
| GitHub secrets `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` | To do: repo **Settings** > **Secrets and variables** > **Actions** > **Secrets**. The token must be **team-scoped (Leadwalnut)**, not project-scoped, or attaching the link fails with "User not found". The same team token as Fortinet works. `VERCEL_PROJECT_ID` is the new Splashtop project's ID. |
| Public access to the links | Vercel project **Settings** > **Deployment Protection** > turn **Vercel Authentication** off, otherwise the links ask for a Vercel login. |
| Each person who runs updates | Needs GitHub linked in Claude (**Settings** > **Connectors** > **GitHub**) and Write access to the repo (repo **Settings** > **Collaborators**). |
| Repo visibility | Recommended: private (repo **Settings** > General > Danger Zone). |

The repo's `vercel.json` switches off Vercel's own deploy-on-push. GitHub Actions does the deploying.

---

## Test it with the September doc

1. Save the `splashtop-dashboard-monthly-update` skill (from the card in the chat).
2. Open a **new** Claude chat, attach the September 2026 doc, and type *Update the Splashtop dashboard with this doc*.
3. Check the preview Claude shows you. Ask for a small correction to try it (you can change it back).
4. When Claude asks for the link name, type a test name such as **`splashtop-backlinking-dashboard-september2026-copy`** (or skip, if `...-september2026` is not already used by the old Splashtop dashboard).
5. Say **yes** to publish.
6. Claude replies with the link, e.g. `https://splashtop-backlinking-dashboard-september2026-copy.vercel.app`
7. Open it next to the current Splashtop dashboard and check:

- [ ] Header: "October 8, 2026" (or the date you gave), "Backlink Performance Summary Report"
- [ ] KPI cards: 15 URLs / 35 keywords / 455 planned / 421 actual, titled "(Till Sep)"
- [ ] Business impact: 3 charts (6 + 6 + 3 keywords), Dec 2025 vs September 2026, each with its insight
- [ ] DA split: 62 / 317 / 42, "Approximately 90%..." statement
- [ ] Monthly growth: Feb to Sep, 50 / 25 / 48 / 83 / 32 / 108 / 35 / 40
- [ ] Keyword ranking: Top 5 = 6 (from 0), Page 1 = 8 (from 4), both keyword lists
- [ ] Performance summary: 15 rows
- [ ] Key findings: 4 points, with the bold phrases
- [ ] Highlights: 3, and LLM Highlights: 5, each with its screenshot

Known differences (the new version follows the Word doc):

| Where | Current site | New version |
|---|---|---|
| LLM highlight 5 screenshot | Repeats the image of LLM highlight 3 | Its own screenshot from the doc |
| DA quality statement | Shows literal `**` marks | Plain text, percentage calculated from the DA split |
| Growth chart month labels | Feb, Mar, ... June, July, August, September | Feb, Mar, ... Jun, Jul, Aug, Sep |

---

## Troubleshooting

| What you see | What to do |
|---|---|
| Claude says it cannot push / "no GitHub access" | Link GitHub in Claude, be a collaborator with Write access, and check the Claude GitHub App includes this repo. |
| Claude reports "No ranking table in the doc for <URL>" | Each URL's table is recognised by its keywords (`data/url-config.json`). If a URL's keywords changed, tell Claude the new keywords for that URL. |
| Deploy fails at **Deploy to Vercel** | A Vercel secret is wrong or missing. |
| Deploy fails at **Attach the monthly link**: "User not found" | `VERCEL_TOKEN` is project-scoped. Create a token with scope **Leadwalnut** (team) and replace the secret. |
| Deploy fails at **Attach the monthly link**: domain in use | That link name belongs to another Vercel project. Publish again with a different link name. |
| Deploy fails at **Check the build works** | Tell Claude; it will re-check the doc and say what to fix. |
| A month's link shows wrong data | Send Claude the corrected doc and use the same link name. Only that link changes. |
| Need an old month's data | `data/history/<YYYY-MM>.json` and `monthly-docs/` in the repo keep every month. |

Manual fallback (no Claude): GitHub > **Actions** > **Deploy monthly dashboard** > **Run workflow**, optionally with a link name. This redeploys whatever month is currently in the repo.
