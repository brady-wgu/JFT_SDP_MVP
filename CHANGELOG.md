# Changelog

All notable changes to the SkillProof storyboard. Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

The repo's storyboard version (`Storyboard vN.M`) tracks the visual prototype, not the underlying SkillProof product version that JFT is building. The SkillProof product follows the user scenario catalog versions (v1.2 MVP, v1.3 Additional, etc.).

This is a prototype repo — entries below run from the active JFT meeting follow-up phases (v4.69) through the current release. Earlier history exists in git but isn't tracked here.

---

## v4.171 — 13 Aug 2026 — The status demo deck now opens in the browser

The landing page linked the raw `.pptx`, which meant "view the deck" was really "download 41 MB, wait, open PowerPoint". **No browser renders PowerPoint natively**, so the deck is now converted to something a browser can paint: a viewer at [`/deck/`](https://brady-wgu.github.io/SkillProof/deck/).

**Not** the Microsoft Office Online viewer (`view.officeapps.live.com/op/embed.aspx`), which fails here on three counts: it caps at 10 MB against a 41 MB deck, it would not play the embedded video anyway, and it would hand a WGU URL to a third party to fetch on every page load. Everything below is self-hosted.

- **`render_deck.py`** exports the 7 slides to PNG at 2560×1440 via PowerPoint COM (no LibreOffice or `pdftoppm` on this machine). All 7 slides total **1.6 MB**.
- **`build_deck_viewer.py`** generates `deck/index.html`. Arrow-key / Home / End paging, a slide counter, dot rail, full-screen, per-slide deep links (`/deck/#4`), and the original `.pptx` one click away on the toolbar.
- **The video is not duplicated.** Slide 6 is 39.56 of the deck's 41 MB — one embedded MP4 that is **byte-identical (sha256)** to `assets/video/skillproof-walkthrough-2k.mp4` already in the repo. So a real `<video>` is overlaid on the slide's own video region and pointed at the existing asset. `preload="none"` keeps 40 MB from being fetched by anyone who never reaches slide 6, and the poster is cropped from the slide's own render so the region looks identical until you press play. The player pauses when you page away.
- **The deck's hyperlinks survive.** Slide 6's "Launch the live STU101 coach" button and slide 7's two links to this site are real `<a>` elements overlaid on the exact regions the shapes occupy. A button authored as three stacked shapes carrying the same link merges into one anchor. Links on hidden slides are pulled out of the tab order.
- **Overlay geometry is read from the slide XML**, not eyeballed — EMU offsets over slide size, expressed in percentages, the same technique the persona walkthrough hotspots use. Verified against the rendered page: the video lands at 28.03% / 0.12% / 71.90% / 99.76% against the XML's 28 / 0 / 72 / 100.
- **Run-level link widths are measured, not trusted.** A hyperlink on a text *run* reports its whole containing text box. Slide 7's URL line sits in a 45%-wide box while the visible text covers about 16%, so the box verbatim would leave a huge invisible click target over blank slide. The width is measured from the rendered PNG's ink — and the measurement stops at the first gap wider than 1.5% of the slide, because a first pass took leftmost-to-rightmost ink, swept into the screenshot panel that starts at 43% of that slide, and produced a **39.8%-wide** hotspot. It is now **15.8%**, matching the text.
- New `verify-deck.js` in the QA tools asserts all of the above plus no JS errors, every slide decoding, 16:9 with no overflow at 1024–2560px, and that the 40 MB video is not requested on load.

---

## v4.170 — 13 Aug 2026 — Real owl favicon, and the status demo deck added to the landing page

**Favicon rebuilt.** The old icon was invisible against a dark browser tab strip. Root cause: `assets/wgu-favicon.png` was never a favicon — it was the **2000×910 WGU wordmark** in Deep Navy on a transparent background. A 2.2:1 wordmark squashed into a 16×16 slot is an illegible blob, and navy-on-transparent has nothing to sit against once the tab strip goes dark.

Replaced with the **owl mark**, cropped from the official FY26 Full Color Reverse lockup (where the owl is already white) and centred on an **opaque** Deep Navy `#001730` square. Opacity is the fix: the icon now carries its own background, so it reads identically on light and dark chrome instead of inheriting either.

- New files: `favicon.ico` (16 + 32 + 48), `assets/wgu-owl-favicon.png` (512), `assets/apple-touch-icon.png` (180)
- Each `.ico` frame is rendered at its **own** size, with per-size padding and a small stroke dilation measured in target pixels. A single LANCZOS downscale of a 465px **outline** mark to 16px averaged the hairlines with the navy behind them and produced mid-grey mush; the 16px frame now resolves as an owl with visible eyes and ear tufts. Pillow's built-in ICO writer downscales every frame from one image, so the container is packed by hand as embedded PNGs to preserve the per-size rendering.
- Generated by the new `make_favicon.py`. The art is only cropped and scaled, never redrawn.
- Wired into all 8 live pages: `index.html`, `pitch/`, `help/`, and the 4 persona pages via the `PAGE` template in `build_prototypes.py` (regenerated — favicon links are the only change to those files; no screenshots re-captured).
- **New filenames on purpose.** Favicons cache hard; overwriting `wgu-favicon.png` would have left the old blob in place for anyone who had already loaded the site. That file stays on disk because the 4 `_archive/` mockups still reference it, and those are intentionally frozen.

**Status demo deck linked.** Brady's live demo deck (`skillproof-status-demo_v1-1_30JUL2026.pptx`, 7 slides, 41 MB, mostly embedded video) is now the third **About SkillProof** sidebar link, below Full Walkthrough (2K). Marked `download` since a 41 MB `.pptx` cannot preview in-browser.

---

## v4.169 — 13 Aug 2026 — 2K full walkthrough added as a second landing-page link

The 2K walkthrough capture (`skillproof-stu101-walkthrough_2K_30JUL2026.mp4`) is now linked from the landing page rather than replacing anything: **2560×2000, 4 min 19 s, 40 MB**.

- Landed as **`assets/video/skillproof-walkthrough-2k.mp4`** — a site-level asset, since it is reached from the landing page and is not pitch-page media.
- New sidebar link **Full Walkthrough (2K)** directly under *One-Slide Pitch* in the About SkillProof section. It points at the file and opens in a new tab, so the native player gets the full window and the landing page is not lost. `title` carries the resolution, duration and size.
- **`pitch/index.html` is unchanged.** It keeps its own shorter embedded clip (1280×1000, 38 s), so the pitch slide still reads as a single tight slide while the long-form walkthrough lives one click away on the landing page.
- Landing hero images regenerated, because the sidebar gained a visible row.

Verified in-browser: the link resolves to the 2K file, `videoWidth`/`videoHeight` report 2560×2000, duration 259 s, playback advances, and no request fails (the `net::ERR_ABORTED` on the media request is a cancelled range request after buffering, not a load failure).

### Files
`index.html`, `assets/video/skillproof-walkthrough-2k.mp4`, `assets/landing/{light,dark}.png`, `README.md`, this file.

---

## v4.168 — 13 Aug 2026 — Demo rebuilt on STU101 with the AI interaction loop

The persona walkthroughs were unusable as a stand-in for a live demo: the frames were letterboxed cards rather than full-width app windows, no screen showed the AI interaction the platform exists for, and the student flow had silently moved off STU101 onto Introduction to Python. This release fixes all three and makes the failure modes structurally impossible to repeat.

**Full-browser-width frames.** `.shot` was pinned at `min(1440px, 100%)` with a 900px height cap, centred on a grey backdrop, so it read as a floating screenshot rather than the app. It is now `width: 100%` / `height: calc(100vh - bar)`, edge-to-edge, and the frame owns the only scrollbar. Captures vary from 1,080px to 6,139px tall; the internal scroll keeps every screen the same shape. `.stage` changed from flex to block — a flex row let a second `.active` screen shrink both children and produced phantom width readings.

**The AI interaction loop, on all three sides.** Previously absent entirely; the July 2026 storyboard had two such screens and the 12 Aug rebuild had dropped them.
- Student **AI diagnostic**: a model-generated assessment prompt, then its evaluation — narrative feedback, a per-Learning-Objective score table, and a next-focus line.
- Student **AI coaching**: a coaching prompt for the recommended Topic, then the same per-objective evaluation.
- Instructor **Skill Preview**: the staff-side view of the same loop, marked "Preview only — no data is saved". The 11 Aug site map had recorded this grading step as unverified because the Claude-browser permission classifier blocked the submit.
- School Admin **New Skill wizard step 3** now shows the model choice, the fallback chain, the prompt configuration fields *filled in*, and the resulting compiled system prompt. The Preview grades against exactly the Learning Objectives entered in step 2, which demonstrates the authoring config reaching the model.

**One course across all four roles.** Everything course-scoped points at `STU101 · Time Management & Study Skills` inside course folder `B002 · Brady's SoT Course` — 17 enrolled learners, so the heatmaps and learner profiles are populated with real data. A student session is pinned to one course by its LTI launch (the JWT carries `activeCourseId`; the app ignores `?course=`), so the launch link *is* the course selection: `provision/576572714`, not `568442570`.

**Access + data created to make the capture possible.**
- Granted the instructor account course folder B002 via Super Admin → Access Control → Add Course. Before that the app answered "You do not have access to this course folder". The grant is checked server-side and applied to the already-open session with no LTI re-launch.
- Created staging Skill `STU101-PREV · Weekly Planning Basics` in B002 (1 Topic, 2 Learning Objectives, gpt-4o-mini) so Skill Preview has something to run. Staging means students cannot launch it, and only staging Skills appear in the Preview list.

**Screen counts:** Student 4 → 8, Instructor 7 → 8, School Admin 8 → 10, Super Admin 6. **32 screens · 39 hotspots**, every capture 1920px wide (was a mix of 745/1329/1440), all four personas light-mode only.

**Capture harness (`skillproof-qa-tools`, versioned in `brady-browser-kit`).**
- Captures at 1920 wide so screens are 1:1 on a 1080p share instead of upscaled by the full-bleed frame.
- `order` lets capture order differ from display order. Diagnostic Results needs a COMPLETED diagnostic while the diagnostic question screen needs one IN PROGRESS, so results is captured first and the retake that destroys it runs last.
- **Content-readiness gate.** Three student screens shipped as grey loading skeletons with every wait reporting success, because the app's skeleton reuses the real class names — `waitSelector` proved presence, never readiness. Capture now blocks until no skeleton/spinner is present and re-asserts it at the shutter. Two traps: loading markers must be counted *raw*, since a skeleton wrapper measures 0×0 while its bars still paint (a visibility filter made the gate pass instantly); and `[role=progressbar]` must NOT count as a spinner, because the Super Admin cost bar legitimately carries that role and is always present.
- New `select` step (`locator.fill()` cannot drive the wizard's required Course dropdown), optional per-step `timeout`, and `readyTimeout` for model-generated screens.
- Fixed a real hotspot bug: resolving the dashboard's B002 target by text matched `DIV.tap__course-grid` — the entire 16-course grid at 60.8% width — so clicking anywhere in it navigated.
- `demo-seed-diagnostic.js` now finishes any part-finished attempt before retaking; continuing a partial attempt answered only leftover questions and deleted the "Mastered Topics" group from the results screen.
- `verify-demo.js` derives expected width per persona instead of hardcoding 1440, and launches its own browser rather than borrowing an SSO-authenticated profile.

**Redaction.** Student surnames masked, first names and all staff names visible. Added masking to the Instructor dashboard's 68-learner cross-course table, which held real names and had never been redacted. Access Control masks Student rows only — staff keep names and emails.

**Cache-buster.** Screenshots were re-captured several times while `v` stayed put, so the `?v=` query never changed and browsers kept serving the cached skeleton images — a shipped fix looked undeployed. All personas bumped to `v=7`, and the rule is now recorded in every flow file and the README.

**Documentation.** Full README refresh against the current state: repointed five broken links to per-persona READMEs that moved to `_archive/` in v4.167; retargeted the "Python coding coach" framing to the course-agnostic platform the demo now shows; corrected the repo-layout PNG counts (4/5/4/4 → 8/8/10/6) and noted the personas are light-mode only; replaced the "Regenerate screenshots" instructions, which only covered the archived mockups, with the real five-step live pipeline plus what the tooling does and does not guarantee; scoped the Design System palette extensions and the shared persona/course reference to `_archive/`; added a **Live demo canon** table of the real STAGE ids; and fixed the changelog pointer, which claimed v4.160 while the badge read v4.167.

### Files
`README.md`, `CHANGELOG.md`, `index.html`, `build_prototypes.py`, `{student,instructor,tenant_admin,super_admin}/{index.html,flow.json,screenshots/}`, and in `skillproof-qa-tools` / `brady-browser-kit`: `demo-capture.js`, `verify-demo.js`, `verify-frame-width.js`, `demo-reauth.js`, `demo-seed-diagnostic.js`, `demo-complete-diagnostic.js`, `flow-{student,instructor,schooladmin,superadmin}.json`.

---

## v4.167 — 23 Jul 2026 — Persona portals rebuilt as live-app screenshot walkthroughs

SkillProof is now in **beta** on the live app (`wgu.teamjft.com`), so the four hand-built persona storyboards were replaced with **click-through walkthroughs built from real screenshots of the working app** — a login-free backup for when the live app is unavailable. The original mockups are **preserved, not deleted**.

- **Archived the 4 hand-built mockups** to `_archive/{student,instructor,tenant_admin,super_admin}/` via `git mv` (history preserved); unlinked from the landing page but still reachable by direct URL. Their relative paths were re-based one level deeper (`../assets/` → `../../assets/`, `../help/` → `../../help/`, `href="../"` → `href="../../"`) so they still render.
- **New `build_prototypes.py`** generator: emits each persona `index.html` from a per-persona `flow.json` (screens + hotspot wiring). Screenshots are full-page live-app captures; transparent percentage-positioned hotspots overlay the advancing buttons and call the reused `goToScreen()` switcher — flow-nav, `?screen=N` deep-link, arrow-key nav, and the collapsible meta-bar are all retained. Light theme only for v1 (toggle gated on a complete `screenshots_dark/` set).
- **Captured via** a new `capture-screen.js` helper (in the `skillproof-qa-tools` Playwright toolkit) driving real Chrome over CDP, one authenticated session per persona (WGU SSO). Screen counts: Student 4 (STU101 · Time Management), Instructor 5, School Admin 4, Super Admin 4 = **17**.
- **School Admin tenant was empty**, so a demo course (`DEMO101 · Sample Course (SkillProof Walkthrough)`) with two staging Skills was created in-app (School of Business) to populate the Dashboard, Course Detail, and Analytics screens — avoiding empty pages. Flow: Dashboard → Course Detail → Analytics → Help & Support.
- **Landing page:** the "Prototype Storyboards" section is relabeled **"Live-App Walkthroughs · Screenshot Backup (no login)"**; the 4 rows' dates → 23 Jul 2026 and aria-labels reworded; meta-bar quick-launch links de-personalized (dropped Sally/Charlie/Alice/Bob → role labels only).
- `<title>` → `v4.167`; README overview note, Surfaces table, and Repo layout updated.

### Files
`index.html`, `README.md`, `build_prototypes.py`, `{student,instructor,tenant_admin,super_admin}/{index.html,flow.json,screenshots/}`, `_archive/**`, this file.

---

## v4.166 — 16 Jul 2026 — Added 24 E010/D522 skill-level LRPS links

Per the 16 Jul 2026 link-list update: E010 and D522 were broken out from a single course-level LRPS link each into their constituent Topics, for granular skill-level testing.

- **Added 10 E010 rows** (`E010-01` through `E010-10`) under a new "E010 · Foundations of Programming — Skill-Level (Live)" divider, and **14 D522 rows** (`D522-01B` through `D522-14`) under a new "D522 · Python for IT Automation — Skill-Level (Live)" divider — both placed after the existing Student Skills section, before Staff Links.
- Noted `D522-13`'s course slug (`building-small-pro`) still reflects an earlier renaming test; the link and label are both correct, only the slug is cosmetic.
- `count-info` updated `19` → `43` providers; `<title>` → `v4.166`.
- `README.md` Live Skills section gained matching E010 and D522 skill-level tables.

### Files
`index.html`, `README.md`, this file.

---

## v4.165 — 08 Jul 2026 — Removed pagination: one real, complete page now

Per Brady: "We only need this one page of real links from now on." With v4.164 having stripped every decorative filler row, the "huge simulated institution-wide table, viewing a page of it" framing (First/Prev/Next/Last, page-number input, rows-per-page select, "View 1–200 of N") no longer matched what the page actually is — a short, complete, real list.

- **Removed the entire `.pager` control** (First/Previous/Next/Last page buttons, page-number input, rows-per-page `<select>`) and its now-dead CSS (`.pager`, `.pager-input`, `.pager-select`).
- **`count-info` replaced** with an honest, accurate `Showing all 19 providers` (was the fictional `View 1–200 of 13,553`).
- `table-actions` (Refresh / Add new provider / Save icon buttons) left as-is — not pagination, out of scope for this change.
- `<title>` → `v4.165`.

### Files
`index.html`, `README.md`, this file.

---

## v4.164 — 08 Jul 2026 — Removed all decorative filler rows; added real DEV links

Per Brady, the Links table should exactly mirror his own `skillproof-link-list_<DATE>.md` environment tracker — every real link present, nothing fake taking up space.

- **Removed 10 decorative filler rows** that never went anywhere: SkillProof REST API Provider, Cicada PoC v1.1 and v1.0, OEX Studio, Panopto, MyMathLab, ProctorU, Welcome & Roster Sync, Coursera Programs Bridge, Instructional Designer Review.
- **Added the 4 real DEV links** from the tracker (Python, Instructor Portal, School Admin, Super Admin), folded into the existing Student Skills / Staff Links sections rather than a new section — each marked with a new **amber "Broken" status pill** (`.dot.amber`, already defined in CSS) since DEV's LRPS provisioning is confirmed non-functional as of 08 Jul 2026, pending a JFT fix. Still clickable (opens in new tab) so the real URL is inspectable, just honestly labeled.
- **tbody now contains only real content**: Student Skills (9, 1 broken DEV) → Staff Links (6, 3 broken DEV) → Prototypes (4, local storyboard links) — zero decorative rows.
- `count-info` adjusted to `13,553` (net −6: −10 filler, +4 DEV); `<title>` → `v4.164`.

### Files
`index.html`, `README.md`, this file.

---

## v4.163 — 08 Jul 2026 — STU101 added; reconciled README with D522's earlier untracked landing-page addition

Brady built and deployed a new, deliberately non-technical Skill — **STU101, Time Management & Study Skills for College Success** (Course B002 · Brady's SoT Course) — to demonstrate SkillProof's range beyond coding subjects for an executive audience. 4 atomic Topics (Time Management / Avoiding Procrastination / Effective Study Habits / Exam Preparation), 1 Learning Objective each, each answerable in 1-2 sentences by design.

- **New Student Skills row:** `[Skill]STU101 — Time Management & Study Skills` → `lrps.wgu.edu/provision/576572714`.
- **Reconciliation:** D522 (`lrps.wgu.edu/provision/575242504`) was added to `index.html`'s landing table in an earlier untracked edit (commits `54a4d80`/`a9e9375`) but never made it into `README.md`'s Live Skills table or a CHANGELOG entry. Backfilled here alongside STU101.
- `count-info` bumped to `13,559`; `<title>` → `v4.163`.

### Files
`index.html`, `README.md`, this file.

---

## v4.162 — 18 Jun 2026 — Segmented table: Student Skills / Staff Links / Prototypes

Added 3 real Staff LRPS links (Instructor Portal, Tenant Admin, Super Admin) and organized all live rows into three labelled sections with subtle divider rows.

- **New CSS: `tr.section-divider`** — full-width label row with icon, light/dark themed, non-interactive (`pointer-events: none`). Uses `--pgn-color-primary-tint` in light mode and `#0D1E35` in dark.
- **Three `tr.live` Staff rows** (`[Staff]` name-tag) linking to real `lrps.wgu.edu` provision URLs; open in a new tab via the existing absolute-URL handler.
- **tbody order:** Student Skills (6) → Staff Links (3) → Prototypes (4) → filler rows.
- Icons: `school` (Student Skills), `badge` (Staff Links), `science` (Prototypes).

### Files
`index.html`; docs (`README.md`, this file). Landing screenshot regenerated.

---

## v4.161 — 15 Jun 2026 — Live Skills launcher: 6 deployed LRPS skills wired into the landing table

Brady deployed six real skills in LRPS. Added them as live rows at the top of the landing Links table so the shared GitHub Pages URL doubles as a launch hub.

- **Six `tr.live` skill rows** (Python, Professionalism, Applied UX, E010, Calc, Teaching Engineering) at the top of the Links `<tbody>`, each linking to its real `lrps.wgu.edu/provision/<id>` URL. Name + Launch only, `[Skill]` name-tag, `Created By` Brady, provision id in the Id column.
- **Launch in a new tab:** the row-click/keyboard handler now opens absolute `http(s)` `data-launch` targets via `window.open(..., '_blank', 'noopener')`; the four relative persona-portal rows keep their same-tab behavior.
- Cosmetic: count-info `13,549` → `13,555`; stale `<title>` `v4.91` → `v4.161`.

### Files
`index.html`; docs (`README.md`, this file). Landing screenshot regenerated if Playwright is available.

---

## v4.160 — 2 Jun 2026 — Unified export: one "Export ▾" dropdown on every filtered table, format by data nature

The per-section export buttons were hand-built and had drifted — inconsistent placement/alignment (a stray `margin-left:16px`, off-indent), and all four formats offered everywhere. Replaced with a single shared component.

- **One control, module-injected:** `assets/table-controls.js` now injects a consistent **"Export ▾" dropdown** into every filtered table's control bar (and heatmaps), so placement + alignment are identical site-wide. Removed all **20 hand-built standalone export rows** (TA 8 / SA 9 / instructor 3) via a verified script.
- **On every filtered table:** rosters, dashboards, School Management, analytics, logs — anywhere with filters now offers export (previously only analytics + drill screens did).
- **Format by audience:** **PDF + CSV** for human-read data (default); **MD + JSON** for machine-ingested data (logs / audit / webhooks), via `data-export="machine"`. A heatmap exports PDF/CSV; a server log exports MD/JSON.
- **"Reports & exports" section:** per-row report downloads trimmed to **PDF + CSV** (human reports); the table itself marked `data-no-export` (per-row download is the export there).
- Exactly one confirmation toast per export; the SA Logs export uses a `data-export-here` hook on its bespoke filter row. Verified: SA 14 dropdowns (11 human / 3 machine), TA 7 (6/1), Instructor 3 (all human), 0 legacy rows, no console errors, light + dark.

### Assets
Shared `table-controls.{css,js}` → `?v=13`.

### Files
`instructor/index.html`, `tenant_admin/index.html`, `super_admin/index.html`, `assets/table-controls.{css,js}`; docs (`README.md`, this file). Screenshots regenerated.

---

## v4.159 — 2 Jun 2026 — Post-audit refinements (logs de-dup, logo home, dashboard subtitles)

A holistic site audit confirmed the prototype is otherwise clean (no broken markup / images, no placeholder text, no console errors, consistent components, dark mode solid). Three small refinements came out of it:

- **Logs de-dup:** the SA Logs (S11) and TA Activity Log (S11) each rendered **two stacked filter bars** — a purpose-built one plus the generic auto-injected one (duplicate search box). Suppressed the auto bar on both (`data-no-controls`), keeping the purpose-built School / time / search filter on Logs and the action-type chips on the Activity Log.
- **Logo = home:** the WGU navbar logo (previously a dead `href="#"`) now returns to the dashboard (`goToScreen(1)`) across all three admin portals.
- **Dashboard subtitles:** added a one-line descriptive subtitle under the Super Admin and School Admin dashboard titles to match the Instructor dashboard's treatment.

### Files
`instructor/index.html`, `tenant_admin/index.html`, `super_admin/index.html`; docs (`README.md`, this file). Screenshots regenerated.

---

## v4.158 — 2 Jun 2026 — Filter/sort placement audit + remove the logs "Result" column (JFT standup)

Two cleanups from the JFT morning standup.

**1. Controls only where there's something to sort/filter.** The site-wide auto-injector had added filter chips / search / sort to tables that don't warrant them. Suppressed each via a reversible `data-no-controls` flag — **no JS change**:
- **TA S7** Topics & Learning Objectives editors (×4) — editable objective lists, not data to sort.
- **TA S8** the LLM / model list.
- **Root / LRPS** "Links" table — LRPS isn't a JFT deliverable, and it already shows its own native sort icons.
- **SA S1** "Where the spend is going" (3-row top-consumers).
- **Student** S5 / S6 / S10 coaching-feedback tables + S11 "Welcome back" (per direction to clear all Student screens).

Kept (they genuinely need it): SA & TA analytics (incl. Reports & exports + Audit trail), SA Logs, Access Control People / Skills, SA Webhooks, TA Archived Skills, Instructor at-risk list + heatmap search.

**2. A log has no pass/fail.** Removed the always-"Success" **Result** column from the TA Activity Log — a log records events that happened, not success/failure states.

### Files
`index.html`, `super_admin/index.html`, `tenant_admin/index.html`, `student/index.html`; docs (`README.md`, this file). Screenshots regenerated.

---

## v4.157 — 2 Jun 2026 — Remove the "AA contrast" chip (assumed standard, not for end-user display)

Per Brady: WCAG 2.2 AA is an assumed, contractual standard — surfacing it as a UI label adds noise without informing the viewer (same rationale as not labeling TLS/FERPA on-screen). Removed the **"WCAG 2.2 AA contrast" chip** from the three analytics / heatmap headers (Instructor, School Admin, Super Admin), reverting those headers to the plain eyebrow, and dropped the WCAG phrasing from the **Visualization-key** note (kept the functional point: each chart pairs a color with its numeric value). No other v4.156 work changed. Dev-only CSS comments referencing the focus-ring fix are untouched (not user-facing).

### Files
`instructor/index.html`, `tenant_admin/index.html`, `super_admin/index.html`; docs (`README.md`, per-portal READMEs, this file).

---

## v4.156 — 2 Jun 2026 — Design-system polish pass: consistency + leadership-facing enhancements (3 admin portals)

A focused UI/UX pass over the three new admin flows (Instructor, School Admin, Super Admin) ahead of the leadership review, grounded in the **SkillProof Design System v1.3 (13 May 2026)**. The brand tokens, Sora/Lato typefaces, and the 8-pt spacing scale were already correctly wired — this pass *enforced* them where inline overrides had escaped, then added a few high-visibility, contract-aligned enhancements. **No new screens; `?screen=N` deep links and screen counts (5 / 12 / 11) unchanged.**

### Tier 1 — design-system consistency
- **8-pt grid:** emphasis badges → a sanctioned `.badge-lg` (8×16); skill-list buttons unified to 8×16 across Instructor + School Admin (were 8×12 / 10×14); modal head/body/foot padding + gaps normalized (were 22 / 8 / 12px, `gap:12px`).
- **Token compliance / dark-mode fixes:** Super Admin GraphQL block → `--code-bg` / `--code-text` (was hardcoded, value-drifted `#0d1117` / `#c9d1d9`); School Admin API-card code color tokenized; Super Admin **new-school review box** `#f2f4f8` / `#e4e7eb` → tokens so it adapts in dark mode.
- **Component drift:** the 8 Super Admin role selectors were `.badge`-styled `<button>`s with duplicated inline styles and no focus ring → a single `.role-pill` class (keeps the role color-coding, adds hover + a visible focus outline).
- **Copy:** removed `[Demo]` from the Instructor empty state.

### Tier 2 — leadership-facing enhancements
- **§7.14 — Export feels real:** a shared, accessible toast (`role=status` / `aria-live`, success-styled, ~3 s) confirms every PDF / CSV / JSON export. One delegated handler in `assets/table-controls.js`; no per-button wiring.
- **§7.9 — Live institutional branding:** Super Admin → School Management gains a primary-color picker + a live learner-header preview; switching Schools re-themes it (each School carries its own brand color), and the preview auto-selects a readable text color (luminance test) so it stays AA-legible.

### Tier 3 — flourishes
- **§7.3 — Accessibility made visible:** an honest "WCAG 2.2 AA — color contrast verified" chip (tooltip notes the full keyboard/SR audit is in progress) on the analytics + heatmap headers whose color system was unified in v4.152.
- **§7.13 — Visualization key:** a collapsible legend atop both analytics screens covering every viz type (heatmap cells, mastery/cost bars, KPI gauges, score pills, status dots, exports) on the unified heat scale.
- **§7.2 / §7.7 — Responsiveness made visible:** a "Works on every device" card on the Super Admin dashboard with a phone-frame preview of the dashboard reflowed to a single column (the phone screen respects dark mode too).

### Assets
- Shared `assets/table-controls.{css,js}` → `?v=12` (cache-bust so deployed clients pick up the toast + export wiring).

### Files
`instructor/index.html`, `tenant_admin/index.html`, `super_admin/index.html`, `assets/table-controls.css`, `assets/table-controls.js`; docs (`README.md`, per-portal READMEs, this file).

---

## v4.155 — 2 Jun 2026 — Screenshots regenerated against the post-review storyboard

The committed screenshot set had drifted badly through the v4.152 / v4.153 / v4.154 changes — student/screenshots had 34 PNGs each theme (correct count is now 18), super_admin had 26 (now 11), tenant_admin had 15 (now 12), instructor had 8 (now 5). **140 stale + 166 orphan PNGs** in total.

### Naming convention change
Switched from `{scenario}_step{NN}_screen{NN}.png` (e.g., `sc-mvp-01_step02_screen02.png`) to a simple `screen-NN.png` per portal, 1:1 with on-page screen IDs and the new `?screen=N` deep-link URLs. The User Scenario Catalog narrative-step grouping (34 steps across 18 student screens, etc.) lives in the per-portal README scenario tables — keeping it out of filenames eliminates the renumber churn.

### Pipeline updates
- `capture_screens.py` PORTALS table rewritten to the current screen counts (18 / 5 / 12 / 11 / 1 help / 1 root landing).
- Server port standardized to `8000` (was `63417`).
- Filenames `screen-01.png`..`screen-NN.png`; `help.png` for help; `assets/landing/{light,dark}.png` for the LRPS root.

### Counts after regen
| Portal | Screens (each theme) | Filenames |
|:------|:--------------------:|:----------|
| student/ | 18 | `screen-01.png` … `screen-18.png` |
| instructor/ | 5 | `screen-01.png` … `screen-05.png` |
| tenant_admin/ | 12 | `screen-01.png` … `screen-12.png` |
| super_admin/ | 11 | `screen-01.png` … `screen-11.png` |
| help/ | 1 | `help.png` |
| (root LRPS) | 1 | `assets/landing/{light,dark}.png` |
| **Total** | **47 × 2 themes + 2 landing = 96 PNGs** | |

### Docs refresh
- Root README screenshot regen instructions: port 8000, 96-PNG total, new filename convention; stale-warning removed.
- Per-portal README "Files" sections + hero `<img>` refs updated to `screenshots/screen-NN.png`.
- Repo-layout PNG counts corrected (instructor 9 → 5, TA 21 → 12, SA 14 → 11).

### Files
- `capture_screens.py` (rewritten); root `README.md`; `student/README.md`; `instructor/README.md`; `tenant_admin/README.md`; `super_admin/README.md`; all PNGs under `student/screenshots*/`, `instructor/screenshots*/`, `tenant_admin/screenshots*/`, `super_admin/screenshots*/`, `help/screenshots*/`, `assets/landing/`.

---

## v4.153 / v4.154 — 2 Jun 2026 — Deep-link support + dark mode working across the site

### v4.153 — `?screen=N` deep-links
Each portal (`student/`, `instructor/`, `tenant_admin/`, `super_admin/`) now parses `?screen=N` on load and calls `goToScreen(N)`, enabling URL-based deep-linking to specific screens. Used by the Coda Contract Requirements tracker — each tracker row links to the exact screen evidencing that requirement (e.g., `?screen=2` → Access Control, `?screen=11` → Analytics). No effect if the parameter is missing or out of range. ~5 lines of JS per portal.

### v4.154 — Dark mode fixes
Three concrete bugs that the v4.152 light-only review missed:
- **`.tc-sort`** (shared module): the descendant selector `.table-controls .tc-sort` didn't match chip-bar sorts that `addChipBarSort` injects into hand-coded chip bars (e.g., SA S2 Access Control People/Skills/Schools). Changed to bare `.tc-sort` for universal coverage. Added `appearance: none` + a URL-encoded SVG caret so Chrome respects our `background-color` on native `<select>` (without `appearance: none` Chrome paints the OS default white).
- **3 SA inline modals** (`#role-modal`, `#new-school-modal`, `#remove-modal`): hardcoded `background:#fff` on dialog divs left them white-with-gray-text (unreadable) in dark mode. Changed to `var(--pgn-color-white)` which dark-flips to `#0D1A2E`.
- **`[data-theme="dark"]` defensive overrides** added for `.tc-chip`, `.tc-search input`, `.tc-sort`, `.tc-chip-search input`, `.an-tab`, `.an-tabs`.

Verified in dark mode across all 6 surfaces (LRPS root · Student · Instructor · Tenant Admin · Super Admin · Help) — zero light-bg suspects on any audited screen. Light mode preserved.

Asset version: `?v=11`.

### Coda Contract Requirements tracker — 92 rows updated
With the prototype evidence on `main@ce0f20f`, the SkillProof Project Tracker was updated for the first time end-to-end. Final tally: **34 Met** (UI surface depicted in storyboard with `?screen=N` deep-link), 2 In Progress (§7.2 mobile, §7.3 WCAG — Pass-B pending), 2 Deferred Post-MVP (§6.12 LaTeX, §7.7 PWA), 54 N/A (production-only infra; JFT-owned). Last Verified Date = 2 Jun 2026 on every row. Of 38 reqs with a UI surface, 34 are Met (89%); the 54 N/As are pure infra (TLS, AES, scaling, SLAs, certifications) that a storyboard can't structurally show.

---

## v4.152 — 1 Jun 2026 — Storyboard review: shared controls, modals & heat-scale unification (Instructor / Tenant Admin / Super Admin)

Cross-portal Pass-A review with targeted UX fixes. A shared controls module was introduced, status colors were unified, and create/delete/remove flows moved to modals. Admin screen counts settled: **Tenant Admin 13 → 12, Super Admin 13 → 11** (Instructor 5, Student 18 unchanged).

### New shared module — `assets/table-controls.{js,css}`
- Auto-injects **filter chips + search + sort** on every data table site-wide — including tables that already carry a bespoke chip bar; `Actions`/`Controls` columns are excluded from the sort options.
- **Sticky scroll-spy section nav** for long analytics pages (pinned beneath the page title; smooth-scroll + active-section highlight).
- Loaded by all five surfaces; asset version `?v=7`.

### Cross-cutting
- **Status colors unified to the heat scale** (`--heat-1..9`) across heatmaps, score pills, badges, status dots, and threshold/budget bars (instructor / tenant_admin / super_admin) — one red → amber → green language.
- **WCAG 2.2 AA contrast fixes**: warning text darkened to `#8A5A00` (was `#B5710B`, 3.94:1).
- `no-cache` meta tags added to all five surfaces.

### Tenant Admin (now 12 screens)
- Analytics: mastery bars recolored to the heat scale; per-section headers consolidated (one icon + title each); sticky section nav placed below the page title.
- **New Course → modal** from the dashboard (form → confirm → success); the standalone New Course screen was removed.
- **Archived Skills**: "Permanently delete" → confirmation modal.

### Super Admin (now 11 screens)
- Analytics parity with TA (heat bars, consolidated headers, sticky nav — 5 levels).
- **Access Control**: removing any assignment now opens a **confirm modal**; duplicate top search removed; **sort added to all three tabs** (People / Skills / Schools — fixed a Schools column mismatch that had also broken its search + filter).
- **Create a School → modal** from S4 School Management; the standalone Create-a-School screen was removed (S6–S12 renumbered to S5–S11).
- Dashboard quick-links: **dropped "Cost & Usage"**, **added "Data Hub"** (→ Data & Integrations Hub).
- **De-overlap**: S9 renamed "External Tooling & Integrations" → **"External Tooling"** (operational dashboards); "Integrations" now lives solely in the Data & Integrations Hub.

### Known follow-ups
- Screenshot sets are **stale** (captured against older, larger screen counts) — pending a `capture_screens.py` regen.
- External-tool launchers (S9 + S10) use placeholder `#` hrefs; production needs real URLs + `target="_blank" rel="noopener"`.

### Files
- `assets/table-controls.{js,css}` (new); `index.html` + `student/` + `instructor/` + `tenant_admin/` + `super_admin/` `index.html`.

---

## SA v4.150 — 28–29 May 2026 — Super Admin walkthrough (S1–S13) + cost consolidation

Full Super Admin re-walk against the Coda Contract Requirements. Screen count 15 → 13 (S11 + S12 folded into S1).

### Screen-by-screen
- **S1 Dashboard** is now the cost hub: platform cost gauges + a Per-School table where selecting a School reveals its cost/usage detail in-place (S4-style). The flagged School shows the cost-spike trend + top-Skills + likely cause; others show a "stable, within budget" note. Toolbar "Platform Settings" → "Cost & Usage".
- **S11 (Platform Settings) + S12 (Cost spike) removed** — consolidated into S1. Rate-limits block dropped (nothing to set).
- **S2 Access Control**: min-2-Super-Admin guard restored on the role-change modal (disables downgrade + dialog a11y: Escape-close / focus management); Skills renamed to a clear Skill/Course distinction; filter-chip counts = role totals; top-down ordering applied.
- **S3 Access Denied**: headline now states the real reason (expired/revoked link); "Logged ·" + time-of-day dropped (date + event-id kept).
- **S4 School Management**: rows click to reveal per-School Settings in-place; New School button left-aligned; trimmed (removed Primary color, conversation-log retention, Reset).
- **S5 Create a School**: dropped the browser alert + SOW cite; naming standardized to "School Management"; roster + ID-prefix fixes.
- **S6 Analytics**: rebuilt to 5 levels (Platform → School → Course → Skill → Topic); Per-Topic filter chip-highlight fixed; activity log re-sorted chronologically + chip counts corrected.
- **S7–S10 drill-chain**: ported the missing `.heatmap-*` + `--heat` ramp, `.score-pill`, and `.section-card`/`.section-stat` CSS plus `filterHeatmap` from School Admin so the inherited screens render correctly; S8 → S9 link wired.
- **S13 External Tools**: Global configuration section removed.

### Platform-wide
- **Keyboard a11y**: Enter/Space now activates `role="button"` rows/cards (super_admin + instructor + tenant_admin).
- **`tenant_` ID prefix removed** site-wide (School IDs → `school_*`; TA branding map).
- **Cost data canonical** (Tech = high-cost spike): $4,287 platform total; Tech $2,415 / Business $1,000 / Education $330 / Health $542 — reconciled across S1, S4, S6.
- Roster aligned to Alice / Miguel / Renee / Theo on the walked screens.

### Files
- `super_admin/index.html` — major (title stamp v4.141 → v4.150)
- `tenant_admin/index.html` + `instructor/index.html` — keyboard-a11y helper; `tenant_` prefix removal (TA)

---

## TA v4.138 — 24 May 2026 — TA walkthrough complete: redesign, terminology lock, 4-level Analytics

The Tenant Admin (now **School Admin**) portal was walked end-to-end and overhauled in a single session. The portal is now 15 screens (S1–S15), down from 26 in v4.119. Scope was sharpened to **Courses + Skills management only** — at-risk learner tracking, help-desk 2-way communication, and School Settings all moved to other personas (Instructor / Super Admin) per Brady's directive.

### Scope cuts (TA only manages Courses + Skills)

- **At-risk learner tracking removed** from S1 dashboard. The at-risk roster, "X learners at risk" badges, and "View at-risk learners" buttons were stripped. Drill-down through the heatmap (S3 → S4 At-risk filter → S5 Learner profile) remains accessible for diagnostic, but is not the TA's primary surface.
- **Incident response flow removed**. Per Brady's directive ("there won't be any 2-way communication between the help desk and SkillProof"), the 8-screen incident response chain (former S16–S23: degradation alert → notification → P1 ticket → CSM thread → restore → SLA) was deleted entirely. Help is now a one-way link out to Zendesk via the help icon in the navbar. The "Incidents Open" KPI gauge was also removed.
- **School Settings moved to Super Admin**. The former S24 (School Settings — branding, thresholds, retention) was deleted from TA and rebuilt inside the Super Admin's S12 (Schools & Settings) screen as expandable per-School panels. SA owns platform-wide tenant configuration.
- **Skill Lifecycle moved into Course detail page**. The former standalone S25 (Active / Archived Skills) is now accessed via the Course view (S2) where each Skill card has Edit / Archive affordances inline.
- **Activity Log folded into Analytics**. The former standalone S27 is now Section 6 of the consolidated Analytics screen (S15).

### New architecture (15 screens)

| # | Screen | Purpose |
|:---:|:---|:---|
| S1 | School Dashboard | KPI rollup (4 Courses · 7 Skills · 680 Sessions/wk · 90 Learners) + toolbar (New Skill / Analytics) + 4 Course cards with Skills folded in as inline action buttons + filter chips + sort dropdown + text-search |
| S2 | Course view | Skills inside a Course (Edit primary, Archive, Open Heatmap) — TA's primary maintenance surface |
| S3 | Skill heatmap | Topic × Learner mastery grid (Instructor-mirror; diagnostic drill-in) |
| S4 | At-risk filter | Learner rows filtered by AI-mastery threshold (diagnostic) |
| S5 | Learner profile | Per-Topic mastery + session history (diagnostic) |
| S6 | Conversation logs | Session log per learner (diagnostic) |
| S7 | Session transcript | Full chat thread with objective miss markers (diagnostic) |
| S8 | Audit Trail | Event log for a learner's sessions (diagnostic) |
| S9 | Access Denied | Deny path (write to non-owned Skill, cross-School write attempt) |
| S10 | New Skill (wizard 1/5) | Course Number + Course Title combobox typeahead with add-new + Skill code + Skill name + description |
| S11 | Topics & Learning Objectives (2/5) | Topic expanders with per-LO % thresholds (0–100% scale for TA-entered passing thresholds; AI-scored values stay 0.00–1.00) |
| S12 | Model & Prompt (3/5) | Model picker + AI coaching prompt config (Coaching style removed; A/B test + LaTeX badges removed) |
| S13 | Review & Deploy (4/5) | Full Skill summary + Deploy to Staging / Deploy to Live (lifecycle terminology lock) |
| S14 | Deploy success (5/5) | OOP Skill build succeeded + LRPS provisioning ticket + Back to Dashboard / Create another Skill |
| S15 | Analytics & Activity Log | **4-level zoom**: School Rollup → Per-Course → Per-Skill → Per-Topic; each section has PDF / CSV / MD / JSON download; Program Reports + Activity Log embedded |

### Terminology and copy locks

- **"Tenant Admin" → "School Admin"** across all chrome, breadcrumbs, copy, and persona references.
- **Persona chip**: `School Admin · School of Technology` (role + scope qualifier).
- **Lifecycle states**: Draft / Staging / **Live** (not "Production" or "In production").
- **Score scales** (refined platform rule, F42):
    - AI-scored values (heatmap, session scores, KPI mastery averages): `0.00–1.00`
    - TA-entered passing thresholds (Skill setup, Deploy review): `0–100%`
- **"audit-logged" copy removed** platform-wide — it's expected and assumed, not something to surface to the user.
- **No real names, real emails, real $-amounts (contract values only)**. Operational $-amounts (token costs, billing data) are fine per Brady's refined hygiene rule.
- **Never abbreviate "Learning Objective" to "LO"** anywhere in copy.
- **"Course Number" + "Course Title"** terminology for Course identifiers on the New Skill wizard (replaces "Parent Course"). Both are typeable combobox inputs (HTML5 `<datalist>`) that support add-new.

### New S1 dashboard layout (Brady's progressive refinement across the session)

- 4 KPI gauges: Courses (4) · Skills (7) · Sessions This Week (680) · Learners (90)
- Toolbar (replaces former Quick Actions cards): `+ New Skill` (primary) · `Analytics` (outline-primary)
- 4 Course cards (E010 Foundations / E075 Intermediate / E135 OOP / E120 Data Structures) with Skills folded in as full-width inline button rows inside each card
- Filter chips: All Courses (4) / Has Live Skill (3) / Has Staging Skill (1) / Has Draft Skill (1) / I own at least one Skill (3)
- Sort dropdown: Course code / Most active learners / Highest avg score / Recently active
- Text-search input with magnifying-glass icon (matches against Course Number AND Course Title, case-insensitive)
- Filter + search + sort all combine with AND logic

### New S15 Analytics architecture (4-level zoom)

```
Level 1 — School Rollup    : 4 KPI gauges + 30d active-learners line chart + 7d submissions bar chart
Level 2 — Per-Course        : 4-row table + Mastery h-bar comparison + Cost h-bar comparison
Level 3 — Per-Skill         : 7-row table with lifecycle badges (Live/Staging/Draft) + Skill mastery comparison
Level 4 — Per-Topic         : 20-row table filterable by Course; spot expensive/underused Topics (Skill prompt bugs)
+ Program Reports           : Pre-built reports w/ filters (date range, Skill, Topic)
+ Activity Log              : 11 events paginated, filter chips (Create / Edit / Deploy / Role changes)
```

Each section has `PDF / CSV / MD / JSON` download. Demo data math reconciles fully (E010 $172+$35=$207 · E075 $45+$60=$105 · E120 $0 · E135 $45+$30=$75 · Total $387 MTD).

### Files changed

- `tenant_admin/index.html` — ~4,500 line net change across v4.120–v4.138 (significant restructure + S15 redesign)
- Title stamp: `Storyboard v4.119` → `Storyboard v4.138`

---

## SA v4.118 — 24 May 2026 — SA Phase 1 + drill-chain expansion

The Super Admin portal was walked S1, renumbered to start at S1, expanded to 26 screens by inheriting TA's full drill-chain + wizard + Analytics, and polished. Persona "Bob" is the generic stand-in for the initial WGU Super Admins (names kept out of the public repo per data-hygiene policy).

### Phase 1 — renumber + terminology lock + School Settings (v4.114)

- **Renumbered S2–S14 → S1–S13** so SA starts at S1, matching TA + Instructor. Old S1 (SSO landing, removed in v4.85) gap closed. All `id="screen-N"`, `id="sN-heading"`, `id="main-N"`, `aria-labelledby`, `goToScreen(N)` calls updated via placeholder substitution.
- **"Tenant Admin" → "School Admin"** rename across 19 spots (5 plural + 14 singular).
- **Navbar chip**: `Super Admin Portal` → `Super Admin` (role-only, parallel to TA's role+scope chip pattern).
- **H1 + breadcrumb root**: `Super Admin Portal` → `Super Admin Dashboard` (matches TA's "School Admin Dashboard" pattern).
- **De-personalized SA-level copy**: removed "Sally" name from active-alerts (S1) and cost-spike narrative (S3). SA cares about systemic patterns, not individual learner names — that's Instructor's domain.
- **School Settings added to S12 (Schools & Settings)** — 4 new "Settings" buttons (one per School row) + wireframe Settings panel below the table with Branding (logo + primary color) + Default Thresholds (passing % + monthly token budget $) + Data Retention (conversation logs + audit log) sections. Replaces the old TA School Settings that was removed from TA in v4.124.

### Phase 2 — dashboard polish (v4.115, v4.116)

- Quick Links cards: 8 large icon-cards (col-3 4×2) → 10 compact horizontal icon+title cards (col-3 4+4+2), descriptions dropped
- Status legend dropped from S1 header (gauge dots self-describe)
- Intro paragraph below H1 removed (eyebrow + H1 self-describe)
- KPI gauges made clickable drill-ins: SCHOOLS→S12 · ACTIVE LEARNERS→S26 · TOKEN SPEND→S2 · RATE LIMIT HEADROOM→S4
- Meta-bar restructured from single flow group → 5 flow groups (A: Platform Ops · B: Compliance & Audit · C: Access & People · D: External Tools & Data · E: Deny Path)

### Phase 3 — drill-chain expansion (v4.117)

The Super Admin can drill into all the same data a Tenant Admin or Instructor can see. 13 new screens copied from TA, transformed (navbar swapped to WGU corporate logo + Super Admin chip + Bob/B user; breadcrumb root rewritten; goToScreen targets remapped per TA→SA mapping table; section IDs renumbered).

| New SA # | Source (TA #) | Screen |
|:---:|:---:|:---|
| S14 | TA S2 | Course view (Skills inside a Course) |
| S15 | TA S3 | Skill heatmap (Topic × Learner) |
| S16 | TA S4 | At-risk filter |
| S17 | TA S5 | Learner profile |
| S18 | TA S6 | Conversation logs |
| S19 | TA S7 | Session transcript |
| S20 | TA S8 | Audit Trail |
| S21 | TA S10 | New Skill — Course Number + Title + Skill details |
| S22 | TA S11 | Topics & Learning Objectives |
| S23 | TA S12 | Model & Prompt |
| S24 | TA S13 | Review & Deploy |
| S25 | TA S14 | Deploy success |
| S26 | TA S15 | Analytics & Activity Log (4-level zoom) |

TA S9 (Access Denied) skipped — SA's S13 covers the deny path with broader scope. Meta-bar gained 3 new flow groups: F (Drill-Down) · G (Skill Creation Wizard) · H (Analytics).

### Phase 4 — S1 review (v4.118)

- Quick Links reordered into a clean narrative: **Row 1 — Drill + Analytics + Governance** (Course Drill-Down · Analytics · Schools & Settings · User Management) · **Row 2 — Platform Operations** (Token Usage · Rate Limits · Compliance · Geo-Redundancy) · **Row 3 — People + Tools** (Instructor Roster · External Tooling)
- 12 stale `<!-- Screen N: -->` HTML comments fixed throughout the file (pre-renumber stale dev-comments)
- Status legend dropped; gauges remain self-describing

### Files changed

- `super_admin/index.html` — ~2,300 line net additions across v4.114–v4.118 (drill-chain mirror)
- Title stamp: `Storyboard v4.113` → `Storyboard v4.118`

---

## v4.119 — 24 May 2026 — TA renumber S1..S26 + JS leak fix

Per Brady's directive: TA portal should start at Screen 01 (consistent with Instructor portal numbering). Plus a stray `</body></html>` block was interrupting the script tag mid-file, causing the trailing theme-restore / toggle / radio-card JS to render as plain text on every page instead of executing.

### Changes

- **TA renumber S2..S27 → S1..S26** (uniform -1 offset). New S1 is the School Dashboard (default active). All `id="screen-N"`, `id="sN-heading"`, `id="main-N"`, `aria-labelledby`, `goToScreen(N)` calls, and JS `'#screen-N'` selectors updated via placeholder substitution to avoid double-replacement (e.g., `screen-2` inside `screen-20`). Meta-bar rewritten with new numbering.
- **JS leak fix**: removed an orphan `</script>` + `</body>` + `</html>` block at line ~4747 that was splitting the script tag. The `// Restore theme on load` IIFE + `// Toggle switches` + `// Radio cards` event listeners (~40 lines) were previously rendering as visible text below the page footer because they were positioned after the broken `</body></html>` and lacked a wrapping `<script>` tag. Now stitched back into a single contiguous script block.
- **TOTAL_SCREENS**: 27 → 26.
- **Title stamp**: `Storyboard v4.118` → `Storyboard v4.119`.

### Files changed

- `tenant_admin/index.html` — ~50 line net change (orphan block removed); all 26 screens renumbered; meta-bar rewritten

---

## v4.118 — 24 May 2026 — Tenant Admin redesign + cross-portal visual unification

Major redesign of the Tenant Admin portal architecture, plus Phase 1 visual unification across all three portals (instructor / tenant_admin / super_admin). Per Brady's directive 23 May 2026 mid-walkthrough: "Update both admin prototypes to match the style of the Instructor we've just finalized... base your screens on the Instructor displays from the bottom up, then add in the higher level details and abilities of the Tenant Admin."

### Why

After landing F21–F25 on TA S2 + S3 during the walkthrough, the original TA architecture ("Quick Actions" cards + flat Skills list) was visibly mismatched with the Instructor portal's drill-down model. Brady redirected the engagement scope: rather than continue per-screen walkthrough fixes, the TA portal should be rebuilt to mirror Instructor's screens and add Tenant-Admin-specific layers (create + modify Courses + Skills, manage School Settings, monitor SLA + handle incidents, view Tenant-scope Analytics + Activity Log). Same audit also surfaced cross-portal CSS drift: super_admin was missing the `.chip-filter` definition entirely (chips rendered as unstyled buttons); tenant_admin used icon+text Help link while instructor + super_admin used icon-only.

### Decisions locked (Brady verdicts 23 May 2026)

| Decision | Verdict |
|---|---|
| Help link direction | Icon-only across all 3 portals (supersedes F22:A) |
| TA screen numbering | Clean renumber S2–S27 (Instructor mirror first, then TA-only) |
| Skill lifecycle states | Three: Draft / Staging / Live (rename "In production" → "Live") |
| Read-only Skills | Hide Edit affordance; Read-only badge stays |
| KPI tile count on new TA S2 | Four gauges (SKILLS LIVE / DEPLOYS · LAST 30 DAYS / ACTIVE LEARNERS / INCIDENTS · OPEN) |
| At-risk roster on S2 | **Removed entirely (24 May 2026)** — at-risk learner identification is an Instructor-level function; School Admin is one level higher (Course/Skill/Settings/SLA scope). Drill-down to at-risk filter (S5) remains available via Course-card at-risk badge if Alice wants the detail. |

### Changes — Phase 1 unification (cross-portal chrome)

- **F22 reversed**: tenant_admin's `.navbar-help-link` CSS removed (main block + light/dark overrides); 19 HTML instances converted to icon-only `.btn-theme-toggle` pattern. All 3 portals now consistent.
- **super_admin gets `.chip-filter` CSS** (16 lines): chip-filter HTML existed but had no styling — rendered as raw browser buttons. Now styled as pill chips with brand-blue active state.
- **super_admin `.gauge-number` font-size**: 40px → 64px to match instructor + tenant_admin density.
- **`.row-card.at-risk` + `.row-card.flagged` defined in all 3 portals**: previously each portal had only one (instructor=at-risk, super_admin=flagged, tenant_admin=neither). Now additive so both classes work everywhere.
- **`tenant_admin/index.html` chip-filter CSS imported** (16 lines): audit found TA's HTML used `.chip-filter` but the CSS was never defined — chips were unstyled. Imported from instructor.

### Changes — Phase 2 TA redesign (new architecture)

Goes from 19 screens (S2–S5, S7–S21) to **26 screens (S2–S27, no gaps)**. New numbering:

| New # | Purpose | Source |
|---|---|---|
| S2 | School Dashboard (replaces "Quick Actions" surface) | Built fresh: mirrors Instructor S1 structurally but at School Admin scope (one level higher than Instructor). 4 KPI gauges + toolbar (`+ New Skill` / `School Settings` / `Skill Lifecycle` / `Analytics` / `Activity Log` / `System Status`) + 4 Course cards (E010 / E075 / E135 / E120) with aggregate at-risk badges that drill to the at-risk filter (S5). No individual-learner roster on the dashboard — that's the Instructor's surface. |
| S3 | Course view | Mirror Instructor S2 + `+ New Skill in this Course` button |
| S4 | Skill heatmap | Mirror Instructor S3 (Python Skill heatmap, 15 learners × 13 Topics, chip filters, Export) |
| S5 | At-risk filter | Mirror Instructor S4 |
| S6 | Learner profile | Mirror Instructor S5 (Sally + Per-Topic table) |
| S7 | Conversation logs | Mirror Instructor S6 (9 sessions) |
| S8 | Transcript | Mirror Instructor S7 (chat thread + Objective miss markers) |
| S9 | Audit trail | Mirror Instructor S8 (event log, 10 of 47) |
| S10 | Access Denied | Mirror Instructor S9 + TA-specific deny scenarios (write to non-owned Skill, cross-School write) |
| S11–S15 | Skill creation wizard (5 steps) | Renumbered from current S3–S5, S7, S8 |
| S16–S23 | Incident response flow (8 screens) | Renumbered from current S9–S16 |
| S24 | School Settings | Renumbered from current S17 |
| S25 | Skill Lifecycle | Renumbered from current S18 |
| S26 | Analytics & Reporting | Renumbered from current S19 |
| S27 | Activity Log | Renumbered from current S20 |

Current S21 (Access Denied) deleted — absorbed by new S10 mirror.

### CSS / JS imported from Instructor v4.117 (canonical baseline)

- `.section-card` + `.section-card.recommended` + `.section-stat*` (cards + inline stat tiles)
- `.heatmap-*` block (~140 lines: grid, card, scroll-container, corner, col-label, row-label, cell.h1-h9, legend, scroll-hint)
- `.score-pill.low/.med/.high`
- Heatmap CSS variables `--heat-1..--heat-9` + `--heat-text-dark` for both light and dark modes
- Dark-mode `.heatmap-card` selector added to existing card chain
- JS: `hydrateOneHeatmap`, `hydrateHeatmap`, `filterAtRiskRoster`, `filterHeatmap`, `filterPerTopicTable`, `filterSessions`, `filterTranscript`, `filterAuditEvents`, `setupHeatmapScrollState` (~220 lines). All `#screen-N` references renumbered for TA's new architecture (instructor screen-N → TA screen-(N+1)); `goToScreen(5)` inside heatmap hydration renumbered to `goToScreen(6)` (drill to learner profile).

### Renumbering details

- Current TA S3-S5 → New S11-S13 (offset +8; closes the S6 gap)
- Current TA S7-S20 → New S14-S27 (offset +7)
- Current TA S21 (Access Denied) → DELETED (new S10 absorbs)
- All `id="screen-N"`, `id="sN-heading"`, `id="main-N"`, `aria-labelledby="sN-heading"`, and `goToScreen(N)` calls bounded to the post-S10 zone got renumbered consistently.
- `enforceLoMinimum` + `addTopic` JS selectors updated `#screen-4` → `#screen-12` (Topics & Learning Objectives renumbered).
- `TOTAL_SCREENS` constant bumped 21 → 27.

### Meta-bar restructure

Old: 2 flows (A: Skill Configuration, B: Critical Incident Response & SLA). New: 4 flows matching the new architecture:
- **Flow A — Cross-Course Drill** (S2 School Dashboard → S10 Access Denied; mirrors Instructor portal): 9 chips
- **Flow B — Skill Creation** (S11–S15): 5 chips
- **Flow C — Critical Incident Response & SLA** (S16–S23): 8 chips
- **Flow D — Settings & Reporting** (S24–S27): 4 chips

### Other findings landed in this version

- **F21** (P1): "SUBJECTS LIVE" KPI label → "SKILLS LIVE" (terminology — Subject is not a platform hierarchy term)
- **F23** (P2): Activity Log Quick Action card got a second CTA ("Export Activity Log") — then superseded by S2 wholesale replacement
- **F24** (P2): TA "Your Skills" rows renamed to actual Skill names (Python Skill / OOP Skill / Python Intermediate Skill / Data Structures Skill) with Course code in row-sub line — then superseded by new S2 structure
- **F25** (P3): S11 (was S3) breadcrumb "Skills" hop wired to `goToScreen(2)`
- **F26** (P1, carry-over): 10 per-LO Threshold inputs on new S12 (was S4 Topics & LOs) normalized from 0-100% scale to 0.00-1.00 with `step="0.01"`. Strict source-of-truth alignment with Brady's score scale rule.
- **F27, F28** (carry-over): deferred to walkthrough resumption
- **F29-F34** (S2 deep re-review findings): superseded by S2 wholesale replacement

### Lifecycle terminology rename

`>In production<` and `>In staging<` badge text patterns replaced with `>Live<` and `>Staging<` respectively. Only remaining "In production" string in the file is a CSS install code comment (non-user-facing).

### Files changed

- `tenant_admin/index.html` — major rewrite; 3,395 → 4,885 lines (+1,490, +44%); 142 KB → 305 KB
- `instructor/index.html` — Phase 1 unification only (`.row-card.flagged` added)
- `super_admin/index.html` — Phase 1 unification (`.chip-filter` block imported, gauge font 40px → 64px, `.row-card.at-risk` added)
- Title stamp `Storyboard v4.114` → `Storyboard v4.118` in `tenant_admin/index.html`

### Walkthrough resumption

The TA walkthrough (Task 3) now resumes against the new S2–S27 architecture. Findings F21–F26 are landed on their renumbered equivalents (F26 on new S12, not on current S4). F29–F34 from the S2 deep re-review are superseded by structural redesign. Task 4 (Super Admin) and Task 5 (cross-portal hygiene) proceed unchanged.

---

## v4.117 — 23 May 2026 — Instructor S2–S9 re-review — export pattern platform-wide, source-level affordance, terminology + content-clarity fixes

Continues the instructor S1–S9 re-review against the freshly-finalized Coda canonical sources (Scenarios v1.4, User-Profiles v1.3, Access-Control v1.2 — all dated 23 May 2026). Eight screens, fifteen findings landed across F5–F19 per Brady's per-finding verdicts. F8 (Topic taxonomy reconciliation) and F20 (em-dash terminology) intentionally deferred. S9 (Access Denied) had no findings requiring action — it was the strongest contract-anchored screen in the portal (Access-Control v1.2 §3.2 all 4 requirements satisfied at v4.113).

### Why

The S1 walkthrough (v4.116) surfaced a class of patterns that recurred across S2–S9: missing or partial `Export [Context Name]` patterns relative to Brady's PDF / CSV / MD / JSON platform rule; source HTML that depended on runtime patches (`hydrateOneHeatmap` adding click affordance) where JFT would build verbatim from source; visual layout regressions when expanding inline header rows; terminology drift between "AI evaluation misses" (S7 subtitle, S8 stat label) and the canonical "Objective miss" event term from Access-Control v1.2; one persona-name leak ("set by Alice"); and a real content-clarity bug on S7 where Sally's code samples rendered as single-line proportional font due to a wrong `font-family` declaration.

### Changes

- **F5 (S2) — Git Skill card → S3 Python heatmap routing** [verdict D, deferred]: Storyboard limitation acknowledged. S3 will continue to show Python content regardless of which Skill card navigated to it; JFT understands this is illustrative wireframing.
- **F6 (S2) — Export `E010 Course Report` added** [A]: Full PDF / CSV / MD / JSON pattern in a dedicated row below the H1 row. Header restructured to avoid H1 wrap (consistent dedicated-row pattern adopted across S2/S3/S5/S6/S7).
- **F7 (S3) — Export `Python Skill Report` expanded** [A]: MD + JSON buttons added (had PDF + CSV only); header restructured to dedicated-row pattern.
- **F8 (S3) — Topic taxonomy reconciliation** [skip]: Scenarios v1.4 §1.3 documents 4 MVP "coached competency areas"; storyboard shows 13 post-MVP Python Topics. Reconciliation deferred — not in scope for this re-review.
- **F9 (S3 + S4) — Heatmap row-label status dots removed** [Brady directive — remove entirely, not re-color]: 19 `<span class="dot ...">` instances removed from `.heatmap-row-label` elements. Status discrimination remains via chip filter and cell-color bands. S1 status legend retained (it explains badge colors in the at-risk roster table, not row-label dots).
- **F10 (S4) — Source-level click affordance on 4 at-risk row labels** [A]: Added `onclick="goToScreen(5)"`, `role="rowheader"`, `tabindex="0"`, `aria-label`, and `title` attributes directly to source HTML for Sally / B.F. / C.S. / H.D. row labels. Runtime `hydrateOneHeatmap` continues to add these defensively; source-level alignment matches the F2:B precedent (JFT builds verbatim from prototype).
- **F11 (S4) — At-risk threshold disclosed as School-Admin-configurable** [A]: Subtitle updated from `"Filter narrowed to AI-scored Topic mastery < 0.60 across two or more Topics."` → `"Filter narrowed to the at-risk threshold set by your School Admin (AI-scored Topic mastery < 0.60 across two or more Topics)."` — mirrors the "Mastery threshold: 0.80 (set by ...)" pattern already on this screen.
- **F12 (S4) — Persona-name leak fix** [A]: `"0.80 (set by Alice)"` → `"0.80 (set by School Admin)"`. Role-only label per Access-Control v1.2 §1 NOTE (UI label is "School Admin"; "Tenant Admin" is the contract role name).
- **F13 (S5) — Export `Sally's Topic Mastery Report` added** [A]: Full PDF / CSV / MD / JSON pattern in a dedicated row.
- **F14 (S5) — Long "Stuck on Topic" cell** [B, no change]: Accepted as-is. Topic name "Data Structures: Lists, Tuples, Sets, Dictionaries" wraps acceptably in the narrow profile card.
- **F15 (S6) — Export `Sally's Conversation Log` expanded** [A]: MD + JSON buttons added (had PDF + CSV only); header restructured to dedicated-row pattern.
- **F16 (S7) — Export `Session 09 Transcript` expanded** [A]: CSV + JSON buttons added (had PDF + MD only); header restructured to dedicated-row pattern.
- **F17 (S7) — Code block content-clarity bug fixed** [A]: Two `<div class="chat-text">` elements in Sally's bubbles used `style="font-family: 'Lato', monospace; font-size: 13px;"` — Lato is sans-serif, so the browser used Lato as primary font; combined with default whitespace collapsing, multi-line code rendered as a single proportional-font line and was unreadable. Fix: `font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace; font-size: 13px; white-space: pre-wrap;` — code now renders as proper indented multi-line monospace.
- **F18 (S7 + S8) — Terminology normalized to canonical "Objective miss"** [A]: S7 subtitle `"3 AI evaluation misses"` → `"3 Objective misses"`; S8 stat label `"AI evaluation misses"` → `"Objective misses"`. Aligns with Access-Control v1.2 callout naming the canonical event term.
- **F19 (S8) — Export `Session 09 Audit Log` expanded** [A]: PDF + CSV + MD buttons added (had JSON only). Inline layout retained per Brady's explicit option choice; cosmetic side-effect is H1 "All 47 messages logged" wrapping to 2 lines as the feedback panel compresses — accepted.
- **F20 (S9) — "School Admin - School of Technology" hyphen vs em-dash** [C, deferred]: Access-Control v1.2 §1 NOTE specifies em-dash format `"School Admin — [School Name]"`; storyboard currently uses hyphen-minus. Queued for platform-wide audit in the cross-portal hygiene task (where tenant_admin + super_admin may have the same pattern).
- **`instructor/index.html` title stamp** — `Storyboard v4.116` → `Storyboard v4.117`.

### Contract tracker follow-up

- The chip-filter coverage table from v4.114 was already corrected in v4.116 (S1 row). v4.117 confirms S3 / S4 / S6 / S7 / S8 chip filters were already wired correctly in prior versions; no further coverage-table edits needed.
- F20 (em-dash terminology) is the one finding that crosses portals; will be addressed in the cross-portal hygiene task after all three portal walkthroughs complete.
- F8 (Topic taxonomy: 4 MVP competencies vs 13 storyboard Topics) remains an open reconciliation item between Coda Scenarios v1.4 §1.3 and the storyboard. Not contractually blocking for the post-MVP SC-ADD-03 framing.

### Files changed

- `instructor/index.html` — 8 screen edits, dedicated-row export pattern adopted on S2/S3/S5/S6/S7, 19 row-label dots removed, 4 source-level row-affordance additions, 2 code-block CSS fixes, 2 terminology fixes, 1 persona-name fix, 1 threshold-disclosure rewrite, title stamp.

---

## v4.116 — 23 May 2026 — Instructor S1 walkthrough — chip filters wired, source scores normalized, Course-card affordance unified

First screen of the instructor S1–S9 re-review against the freshly-finalized Coda canonical sources (Scenarios v1.4, User-Profiles v1.3, Access-Control v1.2 — all dated 23 May 2026). Three findings landed per Brady's per-finding verdicts: F1:A, F2:B, F3:A. F4 confirmed no-op (S1 intentionally export-free; §7.14 covered by S2/S3 exports).

### Why

The v4.114 chip-filter rollout coverage table marked `Instructor S1 Cross-Course Roster | Status | ✅`, but DOM inspection during the re-review showed the 5 chips had neither `onclick` nor `data-filter-status` — they were decorative. The same walkthrough surfaced legacy `XX%` percent literals in `.section-stat-num` and bare-integer score literals in `.score-pill` + `.heatmap-cell` that were being patched at runtime by `standardizeScoresTo0to1()` (added in v4.107). JFT builds verbatim from prototype, so the runtime patch was a contract risk: JFT would either replicate the patch (preserving legacy source values) or build from source and render `76%` — violating the 0.00–1.00 platform rule. Finally, the E010 "Recommended next" Course card was clickable as a whole while E075 + E135 cards were visually identical but non-interactive.

### Changes

- **F1 — `instructor/index.html` S1 at-risk-roster chip filters wired**: added `data-filter-status` + `onclick="filterAtRiskRoster(...)"` to all 5 chips (All / Mastery / On track / Watch list / At risk). Tagged the 4 visible at-risk rows with `data-row-status="at-risk"`. Added a `.no-matches-row` placeholder that displays "[Demo] No sample learners in this filter — open the Skill heatmap for the full roster." when the active filter has 0 matches. New `filterAtRiskRoster(status)` function mirrors S3's `filterHeatmap` pattern (chip active-state toggle + row hide/show + placeholder visibility).
- **F2 — `instructor/index.html` strict source score normalization**: replaced all legacy `XX%` and bare-integer score literals with 0.00–1.00 equivalents directly in source. Removed `standardizeScoresTo0to1()` function and its invocation. JFT now builds verbatim from already-correct source. Totals: 5 `.section-stat-num` percent → 0.XX, 22 `.score-pill` bare-integer → 0.XX, 247 `.heatmap-cell` bare-integer → 0.XX (274 total). Side benefit: heatmap tooltip `Score N (of 1.00)` now reads coherently (was previously contradictory with values like `Score 62 (of 1.00)`).
- **F3 — `instructor/index.html` S1 Course-card affordance unified**: E075 + E135 outer `.section-card` divs now have `onclick="goToScreen(2)"`, `cursor:pointer`, `role="button"`, `tabindex="0"`, and `aria-label="Open <code> Course details"` — uniform with E010's interactive pattern.
- **`instructor/index.html` title stamp** — `Storyboard v4.113` → `Storyboard v4.116`.

### F4 — no-op (confirmed intentional)

S1 has no `Export [Context Name]` affordance, and Brady confirmed this is intentional. §7.14 (Export capabilities for all reports) is satisfied at S2 (Course detail) and S3 (Skill heatmap), where the standard export pattern (`Export Python Skill Report` + PDF/CSV buttons) already exists. S1 is a roll-up dashboard, not a report surface.

### Contract tracker follow-up

The v4.114 chip-filter coverage table over-claimed Instructor S1. As of v4.116 the claim is accurate. Coda Contract Requirements rows anchored to S1 (§7.10 engagement tracking, §7.11 learning analytics dashboard, §7.13 data visualization tools, §7.14 export — see F4 above) remain `Not Started` in the tracker because Storyboard Location URLs aren't yet populated; that bulk update is queued for cross-portal hygiene at end of engagement.

### Files changed

- `instructor/index.html` — 5 chips wired, 4 rows tagged, 1 placeholder row added, `filterAtRiskRoster` function injected, `standardizeScoresTo0to1` block removed, 274 score-literal normalizations, E075 + E135 card affordances, title stamp.

---

## v4.115 — 21 May 2026 — Help portal README sync + version stamp

Quick hygiene pass on the help portal during its critical walkthrough.

### Why

The help portal page was rewritten end-to-end in v4.81 (823 → ~330 lines, search bar / 3-card grid / updates feed / video gallery / floating Contact FAB all removed in favor of a flat Zendesk form + docs list). The README was never updated, so it still narrated all the removed features and still claimed §16.4 #9.15 (Video training resources) coverage that the page no longer provides.

### Changes

- **`help/README.md`** — full rewrite to describe the actual current surface. Removed references to search bar, 3-card grid, updates feed, video gallery, floating Contact FAB, role-filter chips, featured callout, and video tiles. Reduced SOW references to the items the page actually delivers (§16.4 #9.14, supporting §9.1 / §9.4 / §9.11). Added an explicit "Not covered by this surface in v1.2" line for §16.4 #9.15 — videos deferred per WGU direction.
- **`help/index.html`** — title stamp `Storyboard v4.91` → `Storyboard v4.115` to align with the rest of the platform.

### Contract tracker follow-up

§16.4 #9.15 (Video training resources) is now uncovered by the help portal in v1.2. The Coda Contract Requirements tracker should reflect this as `Deferred` (or equivalent) with a 2026-05-21 last-verified date. No re-add to the prototype is planned.

### Files changed

- `help/index.html` (1 line)
- `help/README.md` (full rewrite)

---

## v4.114 — 21 May 2026 — Chip-filter rollout (continued): Tenant Admin S2 "Your Skills" row-list

Continues the chip-filter rollout. Demonstrates the v4.113 `rowSelector` param working for non-table row layouts.

### Tenant Admin S2 Portal Home — "Your Skills"

Added chip filter above the 4-card list of Alice's Skills. **This list uses `.row-card` elements (not `<table>` rows), so the filter passes `'#your-skills-list .row-card'` as the row selector** — proves the helper extension from v4.113 works for non-table layouts too.

Chip filter:
- All Skills (4)
- In production (2) — E010, E135
- In staging (1) — E075
- Draft (1) — E120
- Owned by me (3) — E135, E075, E120 (E010 is read-only because Alice didn't create it)

Each card has `data-yourskill-cat` with space-separated tags (e.g., E135 = `"live owner"`, E120 = `"draft owner"`). The Owned-by-me filter matches against multiple primary statuses, so it correctly counts 3 cards.

### Live verification

- Filter "In production" → 2 cards visible (E010, E135) ✓
- Filter "Owned by me" → 3 cards visible (E135, E075, E120) ✓
- Filter "Draft" → 1 card visible (E120) ✓

### Coverage summary across chip-filter rollout (v4.96 → v4.114)

| Portal | Screen / Surface | Filter type | Status |
|---|---|---|---|
| Instructor | S1 Cross-Course Roster | Status | ✅ |
| Instructor | S3 Skill heatmap | Status | ✅ |
| Instructor | S4 At-risk mini-heatmap | Status | ✅ |
| Instructor | S5 Per-Topic table | Coaching activity | ✅ |
| Instructor | S6 Sessions list | Session type | ✅ |
| Instructor | S7 Transcript | Message type | ✅ |
| Instructor | S8 Audit events | Event category | ✅ |
| Super Admin | S9 People tab | Role | ✅ |
| Super Admin | S9 Skills tab | School + owner status | ✅ |
| Tenant Admin | S2 Your Skills | Production/staging/draft + owner | ✅ |
| Tenant Admin | S16 Recent Incidents | Auto-resolved / JFT engaged | ✅ |
| Tenant Admin | S18 Skill Lifecycle (Active) | Live / Ramping | ✅ |
| Tenant Admin | S20 Activity Log | Action type | ✅ |
| **Total** | **13 tables/lists across 3 portals** | | |

### Still deferred

| Surface | Reason |
|---|---|
| Super Admin S9 Schools tab (4 rows) | Too few rows |
| Super Admin S4 Per-school cost breakdown (4 rows) | Too few rows |
| Super Admin S10–S13 operational tables | Re-evaluate per screen |
| Tenant Admin S4 lo-topic-tables (×4) | Already grouped by Topic |
| Tenant Admin S9/S10 Services tables | Operational health views |
| Tenant Admin S18 Archived Skills (2 rows) | Too few rows |
| Student Progress Map | Re-evaluate after student walkthrough |

### Storyboard stamp

v4.114 tenant_admin portal. Instructor + super_admin stay at v4.113.

---

## v4.113 — 21 May 2026 — Chip-filter rollout (continued): Tenant Admin S16 Incidents + S18 Skill Lifecycle + multi-table helper

Continues the chip-filter rollout from v4.112. Two more tenant_admin tables wired up.

### Helper extended (cross-portal)

`chipFilterTable()` got an optional 5th param `rowSelector` (instructor + super_admin + tenant_admin all updated). When a screen has multiple `<table>` elements, the row selector can target a specific table (e.g., `'#active-skills-table tbody tr'`) so the chip only filters the intended table — the other tables on the screen are unaffected.

### Tenant Admin S16 SLA history — Recent Incidents

Added chip filter above the 4-row incidents table:
- All (4)
- Auto-resolved (3) — Auto-fallback, Self-healed, Auto-scale events
- JFT engaged (1) — danger-tinted chip; matches the warning-badge visual signal

`data-incident-cat` on each row; new `filterIncidents()` JS function. Targets `#incidents-table tbody tr` so the helper doesn't touch any other table on S16.

### Tenant Admin S18 Skill Lifecycle — Active Skills

Added chip filter above the 3-row Active Skills table:
- All (3)
- Live (2) — E010, E075
- Ramping (1) — E135, freshly deployed

`data-lifecycle-cat` on each row; new `filterSkillLifecycle()` JS function. Targets `#active-skills-table tbody tr` so the Archived Skills table below is not filtered.

> Note: "Ramping" is a third lifecycle state distinct from the platform-wide "Testing / Live" convention introduced in v4.95. Where Testing means "pre-deploy verification by admins" and Live means "deployed to students", Ramping signals "newly deployed and being monitored for early uptake metrics." Worth a follow-up conversation on whether Ramping is a real state or should collapse into Live.

### Live verification

- **S16** filter "JFT engaged" → 1 visible (Auth provider rate-limit anomaly) ✓
- **S18** filter "Live" → 2 visible (E010, E075) ✓
- **S18** filter "Ramping" → 1 visible (E135) ✓
- **S18** Archived Skills table unaffected by filters (2 rows always visible) ✓

### Still deferred (next pass)

| Surface | Reason |
|---|---|
| Super Admin Schools tab (4 rows) | Too few rows |
| Super Admin S4 Per-school cost breakdown (4 rows) | Too few rows |
| Super Admin S10–S13 operational tables | Need per-screen judgment |
| Tenant Admin S2 "Your Skills" row-list | Uses `.row-card` not `<table>` — helper would need extension to support |
| Tenant Admin S4 lo-topic-tables (×4) | Already grouped by Topic — chip filter redundant |
| Tenant Admin S9/S10 Services tables | Operational health views — re-evaluate |
| Student Progress Map | Re-evaluate after student portal walkthrough |

### Storyboard stamp

v4.113 across instructor + super_admin + tenant_admin portals.

---

## v4.112 — 21 May 2026 — Chip-filter rollout (continued): Super Admin Skills tab + Tenant Admin Activity Log

Continues the global chip-filter rollout started in v4.109. Brady (21 May 2026): *"Add filter chips to all tables globally."*

### What changed

**Super Admin S9 Access Control · Skills tab** — added chip filter:
- All (6 of 31)
- Technology (3) · Business (1) · Education (2) · Health (1)
- No owner (1) — danger-tinted chip, matches the warning-row visual signal

Each Skill row gets a `data-skill-cat` attribute with space-separated category tags (e.g., `data-skill-cat="tech education"` for a Skill deployed in both schools). New JS function `filterSkillsTable()` calls the generic `chipFilterTable()` helper.

**Tenant Admin S20 Activity Log** — replaced the decorative-only badge row (All actions / Create / Edit / Delete / Deploy / Last 30 days / All actors) with a functional chip-filter:
- All actions (11)
- Create (2) · Edit (3) · Deploy (3) · Role changes (3)

Each row gets `data-activity-cat` matching its action type. New JS function `filterActivityLog()` + new `chipFilterTable()` helper added to tenant_admin's JS block.

### Helper extension — multi-category rows

The `chipFilterTable()` helper in all three portals (instructor, super_admin, tenant_admin) was extended to support **space-separated multi-category values** in the data attribute:

```js
// Before: cat === filterValue
// After:  cats.split(/\s+/).indexOf(filterValue) !== -1
```

This lets a row belong to multiple chip categories simultaneously (e.g., a Skill deployed in both Technology and Education schools matches both filters).

### Live verification (cross-portal)

- **Super Admin Skills tab** filter "Technology" → 3 visible (E010, E075, E135) ✓
- **Super Admin Skills tab** filter "No owner" → 1 visible (H320 Health Informatics) ✓
- **Tenant Admin Activity Log** filter "Deploy" → 3 visible (E135 prod, E075 staging, E010 prod) ✓
- **Tenant Admin Activity Log** filter "Role changes" → 3 visible (Bob's role elevations + instructor assignment) ✓

### Still deferred (next chip-filter commit)

| Surface | Reason |
|---|---|
| Super Admin Schools tab (4 rows) | Too few rows to filter |
| Super Admin S4 Per-school cost breakdown (4 rows) | Too few rows |
| Super Admin S10–S13 operational tables | Need per-screen judgment |
| Tenant Admin S2 "Your Skills" row-list (4 rows) | Uses `.row-card` not `<table>`; helper needs row-selector parameter to support |
| Tenant Admin S16 Recent incidents | Worth doing in a follow-up |
| Tenant Admin S18 Skill Lifecycle | Worth doing in a follow-up |
| Tenant Admin S4 lo-topic-tables (×4) | Already grouped by Topic — chip filter would be redundant |
| Student Progress Map | Re-evaluate after student walkthrough |

### Storyboard stamp

v4.112 instructor + super_admin + tenant_admin portals.

---

## v4.111 — 21 May 2026 — S9 Access Denied walkthrough complete — instructor portal walkthrough done

Resolves S9-01 through S9-05 per Brady's verdicts. Closes the instructor portal walkthrough (S1-S9 all complete).

### What changed

- **S9-01** Added scope to the required-role row: "This page requires: School Admin" → **"This page requires: School Admin - School of Technology"**. Satisfies RBAC §4.2 Figure 6 requirement to name the role AND scope.
- **S9-02** Used the full UI-label form **"School Admin - School of Technology"** per the canonical RBAC doc convention ("School Admin - <School Name>" with hyphen).
- **S9-03** Reframed the audit disclosure from muted footer text to a small explicit notice with `info` icon: *"ⓘ This access attempt has been recorded in the audit log (evt_b1d5e342 · 18 May 2026)."* — still subtle but communicates the policy intent more directly.
- **S9-04** Moved the "Open the correct LRPS link" explanation into a hover **tooltip** on the button: *"Returns you to the WGU LRPS portal where your role-correct deep links are listed."* Brady's directive: minimize all on-screen text outside of tooltips at all times.
- **S9-05** **Removed the navbar chip** ("Instructor Dashboard") on S9 only — the chip was misleading on a deny screen where the user has just been told they can't access where they tried to go.
- **S9-06** Skipped — security best practice is to NOT reveal what specific resource was attempted past the deny boundary. Current behavior is correct.

### New UI principle (from Brady, 21 May 2026)

> *"I want to minimize all text displayed to the user on the screen outside of a hover tooltip at all times."*

This becomes a global guideline for future passes: any explanatory text that can live in a tooltip (`title` attribute) should — keep the visible UI clean.

### Instructor portal walkthrough — STATUS: COMPLETE

All 9 instructor screens walked, critiqued, and resolved over the multi-session pass:

| Screen | Status |
|---|---|
| S1 Instructor Dashboard | ✅ Closed |
| S2 Course view | ✅ Closed |
| S3 Skill heatmap | ✅ Closed |
| S4 At-risk filter | ✅ Closed |
| S5 Sally drill-down | ✅ Closed |
| S6 Conversation logs | ✅ Closed |
| S7 Conversation transcript | ✅ Closed |
| S8 Audit Trail | ✅ Closed |
| S9 Access Denied | ✅ Closed (this commit) |

### Storyboard stamp

v4.111 instructor portal.

---

## v4.110 — 21 May 2026 — S8 audit log: drop Payload + Hash columns

Per Brady: "Let's remove the Payload column from this page as well. I don't think it's helpful, along with the Hash column."

### What changed

S8 Audit Trail event log table now has **4 columns** (was 6):
- `#` · `Date` · `Event type` · `Source`

Removed:
- `Payload` — byte counts (128 B, 412 B, 2.1 KB, etc.) — forensic noise; doesn't help an instructor decide anything
- `Hash (sha256, first 8)` — first 8 chars of sha256 hash per event — useful for cryptographic chain-of-custody verification, but not actionable for an instructor's read

### Production note for JFT

The underlying §10.4 audit data model in production must still capture payload size + cryptographic hash per event (immutable chain-of-custody is a hard contract requirement). The instructor-facing display drops these for clarity. They remain available via the JSON export (the "Export Session 09 Audit Log" → JSON button at top-right) and visible only to Super Admin in the cross-tenant audit log.

### Storyboard stamp

v4.110 instructor portal.

---

## v4.109 — 21 May 2026 — S8 Audit Trail walkthrough + cross-platform chip-filter rollout + "no LO-aggregate data" rule + "Capture integrity" removal

Three threads landed:

### Thread 1: S8 Audit Trail walkthrough (S8-01 through S8-06)

- **S8-01** Removed "Sample design only" banner.
- **S8-02** Expanded breadcrumb to **`Dashboard › E010 › Python Skill › Sally › Session 09 › Audit Trail`** (6 levels, full Course + Skill context — matches the S7 expansion).
- **S8-03** Renamed column header **"Timestamp (UTC)" → "Date"** (values were already date-only since v4.99 — header was lying to the user).
- **S8-04** Stat tile label **"Learning Objective misses" → "AI evaluation misses"** (Brady's "no LO-aggregate-data" principle).
- **S8-05** Moved bottom buttons into the in-flow `.floating-actions` block (consistent with S2/S3/S5/S6/S7).
- **S8-06** Standardized **Source column** to `[Actor type]: [Identifier]` — e.g., `AI: SkillProof Coach`, `Learner: Sally (198.51.x.x)`, `Model: Anthropic Claude Sonnet 4.5`, `Guardrail: SkillProof Coach`.

### Thread 2: "No Learning Objective-level data in aggregate" — new global rule

Brady (21 May 2026): *"No learning-objective-level data. Stop suggesting we keep that level of detail because most students will never have data across all learning objectives, only across topics consistently."*

- **S8 stat tile** renamed "Learning Objective misses" → "AI evaluation misses".
- **S7 description** updated: "3 Learning Objective misses" → **"3 AI evaluation misses"**.
- The per-message **"Feedback · objective miss"** badge inside the actual transcript chat thread (S7) **stays** — it's event-level AI evaluation feedback at the moment the AI judged a turn, not aggregate LO data.

### Thread 3: "Capture integrity" removal (platform-wide)

Brady (21 May 2026): *"I have no idea what that means at all or what that tells the instructor. Remove 'Capture Integrity' entirely from all UIs across the platform."*

- **S8** stat tile "1.00 Capture integrity" — removed.
- Cross-platform grep confirmed no other instances of "Capture integrity" across student, instructor, tenant_admin, super_admin, help portals.

### Thread 4: Chip-filter rollout — multi-portal pass (partial)

Brady (21 May 2026): *"Add filter chips to all tables globally. This works well on the screens we have already reviewed, so apply them to the entire platform for all tables."*

New filters added in this pass:

| Surface | Filter chips | Categories |
|---|---|---|
| **Instructor S5** Sally Per-Topic table | All Topics (13) · Coached since diagnostic (5) · Diagnostic only (8) | `data-topic-cat` |
| **Instructor S6** Coaching sessions | All sessions (9) · Diagnostic (1) · Coaching (8) | `data-session-cat` |
| **Instructor S8** Audit event log | All events (47) · AI events (12) · Learner submissions (18) · Model invocations (9) · Guardrails (8) | `data-event-cat` |
| **Super Admin S9** Access Control · People tab | All (8 of 187) · Super Admin (2) · Tenant Admin (2) · Instructor (2) · Student (2) | `data-user-cat` |

Existing chip-filtered tables (unchanged):
- Instructor S1 cross-Course at-risk roster (v4.96)
- Instructor S3 Topic mastery heatmap (v4.97)
- Instructor S4 At-risk mini-heatmap (v4.98)
- Instructor S7 Transcript message filter (v4.108)

New reusable helper added: `chipFilterTable(scopeSelector, filterValue, dataAttr, chipAttr)` in both instructor and super_admin portals — factors out the duplicated logic across screen-specific wrapper functions. JFT can reuse this for production tables.

**Deferred to follow-up commit** — partial pass only:

| Portal | Tables not yet filtered | Reason |
|---|---|---|
| Super Admin S9 | Skills tab (31 rows), Schools tab (4 rows) | Skills tab worth doing next; Schools tab is only 4 rows so chip-filter has low value |
| Super Admin S4 | Per-school cost breakdown (4 rows) | Only 4 rows; chip filter would have 1-2 items per chip |
| Super Admin S10, S11, S12, S13 | Various operational/Skill-management tables | Need per-screen judgment on chip categories |
| Tenant Admin | Skill builder LO tables (×4), Skill lifecycle, activity log, Settings tables | Each table needs context-specific chip categories |
| Student portal | Progress Map detail rows | Re-evaluate after student walkthrough |

All deferred tables documented as the natural next pass; they're not skipped permanently.

### Live verification

- **S5** filter "Coached since diagnostic" → 5 visible ✓
- **S6** filter "Diagnostic" → 1 visible ✓
- **S8** filter "Learner submissions" → 3 visible ✓
- **S8** stats: 4 tiles (47 Messages · 3 AI evaluation misses · 5 AI escalations · 0 Events dropped) — Capture integrity removed ✓
- **S8** breadcrumb: 5 links + current page (6 levels) ✓
- **S8** column header: "Date" (was Timestamp UTC) ✓
- **S8** Source: "AI: SkillProof Coach" / "Learner: Sally (198.51.x.x)" / "Model: Anthropic Claude Sonnet 4.5" / "Guardrail: SkillProof Coach" ✓

### Storyboard stamp

v4.109 instructor + super_admin portals. Tenant admin + student portals stay at v4.107.

---

## v4.108 — 21 May 2026 — S7 Conversation Transcript walkthrough complete

Resolves S7-01 through S7-07 per Brady's verdicts.

### What changed

- **S7-01** Removed "Sample design only" banner.
- **S7-02** Added in-flow `.floating-actions` block at the bottom-right: **"Back to Conversation logs"** → S6.
- **S7-03** Expanded breadcrumb from `Dashboard › Sally › Logs › Session 09` to **`Dashboard › E010 › Python Skill › Sally › Session 09`** (5 levels, full Course + Skill context). Removed the "Logs" intermediate — the Back button covers immediate-parent navigation.
- **S7-04** Trimmed description: dropped redundant "AI feedback panels shown inline" (already in description) → **"All 47 messages captured by the Audit Trail. AI score 0.15 · 5 feedback panels · 3 Learning Objective misses."**
- **S7-05** Reorganized eyebrow: removed counts (5 feedback panels, 3 Learning Objective misses) → moved into description. Eyebrow now reads **"Session 09 · 06 May 2026 · Data Structures: Lists, Tuples, Sets, Dictionaries"** (Topic-level context only).
- **S7-06** Replaced LO reference "Lists & comprehensions" with the canonical Topic name **"Data Structures: Lists, Tuples, Sets, Dictionaries"** in the eyebrow. Brady's directive: *"Topics are what we show the Instructor in detail, not the learning objectives."*
- **S7-07** Added a chip-filter bar above the chat thread:
  - **All messages (47)** — default active
  - **AI feedback only (5)** — hides learner-side bubbles; shows AI prompts/feedback/reframes
  - **Objective misses only (3)** — shows only AI feedback bubbles with the "objective miss" badge
  - Each chat-row now has `data-msg-type` attribute: `prompt`, `learner`, `feedback-miss`, `reframe`
  - New JS function `filterTranscript(filter)` toggles row visibility and chip active state

### Live verification

- Filter "Objective misses only" → 2 visible bubbles (matches the 2 feedback-miss data-msg-type rows; 1 more lives in the hidden 36 messages)
- Filter "AI feedback only" → 4 visible (3 AI feedback/reframe/prompt rows on the AI side)
- Filter "All" → 7 visible (all rows restored)
- Back button label: "Back to Conversation logs" ✓

### Note for JFT

The chat-row filter currently hides learner-side messages when "AI feedback only" is selected — this strips conversational context. Production may want a different pattern (e.g., scroll-to-next-miss with highlight, or a "show in context" toggle that keeps the surrounding turn visible). This is a prototype demo of the filter UX.

### Storyboard stamp

v4.108 instructor portal.

---

## v4.107 — 21 May 2026 — S6 Conversation Logs rewrite + platform-wide 0-1 scoring standardization

Two threads landed together: the S6 walkthrough verdicts (most of S6-01 through S6-09) and a cross-platform scoring scale change.

### Phase 1: S6 Coaching Sessions List rewrite

Resolves S6-01 through S6-09 per Brady's verdicts:

- **S6-01** Removed "Sample design only" banner.
- **S6-02** **All 9 rows clickable → S7** (was only session 09). `cursor: pointer` + onclick.
- **S6-03** Added in-flow **Back to Sally's profile** button → S5.
- **S6-04** Eyebrow "AI Coaching · Conversation logs" → **"Python Skill · Conversation logs"**.
- **S6-05** Removed the Audit column (every row was an identical "Captured" badge). Replaced with a footer note: *"All 9 sessions captured to the Audit Trail. View full event log on the Audit Trail screen."* (clickable → S8).
- **S6-06** Added upper-right Export group: **"Export Sally's Conversation Log"** + [PDF] + [CSV] following the v4.105 pattern.
- **S6-07** (modified per Brady) Removed the Outcome column entirely. AI score column carries the signal alone.
- **S6-08** Description trimmed: *"Most recent first. Click any row to read the full transcript."*
- **S6-09** (modified per Brady) Removed the Learning Objective column entirely. *"Too much information. The transcript is what tells the story to the instructor because not all Learning Objectives will be answered by the student unless they spend a lot of time using the Skill."*

Final table is 4 columns: Session · Date · Topic · AI score.

### Phase 2: Platform-wide 0-1 scoring standardization

Per Brady (21 May 2026): "The actual scoring by the LLM is zero-to-one scale, I believe. JFT knows how the code works, so they are already doing this point-to-percent translation somewhere, but my prototype UI needs to display this consistently at all levels and to all users."

**The new convention:** All scores display as 0.00–1.00 decimals (2 decimal places). Eliminates the 0-100 percent translation step JFT's UI was doing on top of the 0-1 data model.

**Implementation — instructor portal:**

- **New `standardizeScoresTo0to1()` JS function** runs on page load before `hydrateHeatmap()`. Targets:
  - `.score-pill` (S5 Per-Topic table = 13 cells, S6 sessions list = 9 cells)
  - `.heatmap-cell` (S3 = 195 cells, S4 = 52 cells)
  - `.section-stat-num` with `^\d+%$` pattern (S1 Course-card avg, S2 Skill-card avg)
  - Pure-integer guard so re-running doesn't double-transform
- **Hydrated heatmap cell tooltips** updated from "Score X/100" → "Score X.XX (of 1.00)".
- **S1 inline Skill rows** (6 instances across E010/E075/E135) — source edits: e.g., "76% avg Topic mastery" → "0.76 avg Topic mastery".
- **S3 description**: "AI-scored Topic mastery (0–100)" → **"(0.00–1.00)"**.
- **S3 legend bar** numbers: "0 25 50 75 100" → **"0.00 0.25 0.50 0.75 1.00"**.
- **S4 filter description**: "Topic mastery < 60" → **"< 0.60"**.
- **S4 summary card** rows: "Avg score (at-risk): 42.4" → **"0.42"**; "Mastery threshold: 80%" → **"0.80 (set by Alice)"**.
- **S7 description**: "AI score 15" → **"AI score 0.15"**.

**Implementation — student portal:**
- Baseline result header: "Overall 12%" → **"Overall 0.12"**.
- result-skill-score cells: "100%" → **"1.00"**, "0%" (×3) → **"0.00"**.
- pm-card-sub: "Completed · Score 100%" → **"1.00"**, "Score 0%" (×2) → **"0.00"**.

**Implementation — tenant_admin portal:**
- Form input "Overall Skill passing threshold": `min="0" max="100" value="70"` with `%` suffix → `min="0" max="1" step="0.01" value="0.70"` with "(0.00–1.00 scale)" hint. Default text "Defaults to 70%." → "Defaults to 0.70."
- Detail-table row "70%" → **"0.70"**.
- Skill-detail intro text now reads: *"Set the overall Skill passing threshold on the 0.00–1.00 scale..."*

**Sample verification (live runtime):**
- S1 E010 Avg Skill Score: `0.76` ✓
- S3 first heatmap cell (A.J. on Basic Syntax): `0.98` ✓
- S4 first heatmap cell (Sally on Basic Syntax): `0.62` ✓
- S4 Mastery threshold: `0.80 (set by Alice)` ✓
- S5 Sally first row (Basic Syntax & Data Types): `0.62` ✓
- S6 session 09 row: `0.15` ✓

### Note for JFT

The prototype source HTML now uses 0-1 displayed values directly (matching the underlying LLM data model). Where the JS hydrates from integer 0-100 stored in the markup, it's documented as a temporary prototype-time transformation; production should serialize 0-1 floats end-to-end and skip the conversion entirely.

### Storyboard stamp

v4.107 across instructor, student, and tenant_admin portals. Super admin + help unchanged (no scoring surfaces).

---

## v4.106 — 21 May 2026 — S6 Coaching Sessions List rewrite (Phase 1 of v4.107)

Folded into v4.107.

---

## v4.105 — 21 May 2026 — Platform-wide data-export button pattern: "Export [Context]" + format-only buttons in upper-right

Per Brady: "The label should say 'Export Python Skill Report' and then the 2 buttons are 'PDF' and 'CSV'. You should be able to derive this pattern and execute it across the platform in a similar manner so all these 'data export' features are displayed in a similar fashion across the platform, in the upper, right corner of the screen."

### The standardized pattern

```
<div class="d-flex justify-content-between align-items-start mb-3">
  <div><!-- eyebrow + h1 + description --></div>
  <div class="d-flex gap-2 align-items-center" style="flex-shrink:0; flex-wrap:nowrap; white-space:nowrap;">
    <span class="text-muted small">Export [Context Name]</span>
    <button class="btn btn-outline-primary btn-sm" aria-label="Export [Context] as PDF">
      <span class="material-icons-outlined">picture_as_pdf</span>PDF
    </button>
    <!-- one button per format: PDF · CSV · MD · JSON -->
  </div>
</div>
```

Rules:
- Label communicates **what's being exported** (e.g., "Export Python Skill Report", "Export Session 09 Transcript", "Export Session 09 Audit Log").
- Buttons are **format-only**: PDF, CSV, MD, JSON. Each has its own format-appropriate Material icon (picture_as_pdf, table_view, description, data_object).
- Every button gets a descriptive `aria-label` (e.g., "Export Python Skill Report as PDF") so screen readers hear the full intent.
- Group lives in the **upper-right of the screen**, inline with the H1 and eyebrow. Locked together via `flex-shrink:0` + `flex-wrap:nowrap` + `white-space:nowrap`.

### Applied to (instructor portal)

**S3 Skill heatmap**
- Old: "Export:" + button "Python Skill report (PDF)" + button "CSV"
- New: "Export Python Skill Report" + [PDF] + [CSV]

**S7 Conversation transcript**
- Old: 2 export buttons at the bottom alongside "View Audit Trail" — full label inside the button text ("Export transcript (PDF)")
- New: upper-right "Export Session 09 Transcript" + [PDF] + [MD]
- Old upper-right badges (47 messages captured, AI score: 15) folded into the description line: "All 47 messages captured by the Audit Trail · AI score 15 · AI feedback panels shown inline."
- Bottom row simplified to just "View Audit Trail"

**S8 Audit Trail**
- Old: 1 export button at the bottom ("Export full log (JSON)") between two navigation buttons
- New: upper-right "Export Session 09 Audit Log" + [JSON]
- Feedback-panel restructured into a flex-justify-between row with the panel on left and the Export group on right
- Bottom row simplified to just navigation (Back to transcript, Back to dashboard)

### Not changed in this pass

- **`super_admin` inline "Export" buttons** in tables (lines ~1019, 1594) — these are per-row inline actions, not screen-level exports. Different UX context.
- **`tenant_admin` "Export Reports" + "Export incident report (CSV)" buttons** — these are CTAs inside content cards, also inline rather than screen-level. Pattern doesn't fit directly. Flagged for a future pass if Brady wants in-card export buttons standardized.

### Storyboard stamp

v4.105 instructor portal.

---

## v4.104 — 21 May 2026 — S3 header: shorten description, keep PDF + CSV co-located

Per Brady: "This line is awkward on S3: '[the description text]' with the CSV button next to it. Reduce this descriptive text by 50% and update the placement of the CSV download button to be co-located with the Python Skill report button."

### What changed (S3 only)

- **Description text shortened ~50%**: was "Each cell shows a learner's AI-scored Topic mastery (0–100) for the Python Skill in E010. Topics refresh after every coaching session." (130 chars). Now: **"AI-scored Topic mastery (0–100) per learner. Updates after each coaching session."** (81 chars). Information density preserved; Skill+Course context is already in the eyebrow + breadcrumb above.
- **PDF + CSV buttons now lock together on one line**: the right-side Export container had `flex-wrap: wrap` which let the CSV button drop to a new row when the parent row got tight. Changed to `flex-wrap: nowrap` + `white-space: nowrap` + `flex-shrink: 0` so the Export label + PDF button + CSV button stay co-located as a single horizontal group regardless of the left-side text length.

### Storyboard stamp

v4.104 instructor portal.

---

## v4.103 — 21 May 2026 — Horizontal scroll discoverability: fade + scrollbar + hint label

Per Brady: "I like the scroll, but let's make it a little more obvious and clear that there is more to see. I don't want the user thinking there is nothing else to look at to the right of this viewport."

### Three complementary cues added to S3 + S4 heatmaps

1. **Right-edge fade gradient** — `.heatmap-scroll-container::after` pseudo-element renders a 56px-wide white→transparent gradient on the right edge. Signals visually that content is cut off. Fades out (`opacity:0`) when the user has scrolled to the right edge via JS-toggled `.at-end` class.
2. **Prominent brand-blue scrollbar** — `.heatmap-card::-webkit-scrollbar` styled 12px tall with `--pgn-color-brand-base` thumb. `scrollbar-color` set for Firefox. Visible affordance even when no scrolling has happened.
3. **Italic hint label below the heatmap** — pill-style block with `swap_horiz` icon, brand-blue text on brand-tint background: *"Scroll horizontally to see all 13 Topics — try the scrollbar below, shift + mouse wheel, or trackpad swipe"*. Educates users on the available scroll methods. Dims to 50% opacity when scrolled to right end.

### Wiring

- Wrapped both heatmaps in `<div class="heatmap-scroll-container">` (was `.heatmap-card` directly).
- Added `<div class="heatmap-scroll-hint" role="note">` as sibling below each `.heatmap-card`.
- New JS function `setupHeatmapScrollState(screenSelector)` listens for `scroll`, window `resize`, and uses `ResizeObserver` to recalculate when the heatmap first becomes visible (handles the display:none → visible transition when user navigates to S3 or S4). Toggles `.at-end` class on the container when `scrollLeft >= scrollWidth - clientWidth - 4`.

### Behavior

- On page load: fade gradient + hint at full opacity → signals "more to the right"
- User scrolls right: fade gradient stays visible until reaching the end
- Scrolled to right edge: fade gradient opacity goes to 0, hint dims to 50% → signals "you've seen everything"
- Viewport wider than 1580px (no scroll needed): `.at-end` is automatically added, so fade + dim are applied

### Storyboard stamp

v4.103 instructor portal.

---

## v4.102 — 21 May 2026 — S3/S4 heatmaps + S6 sessions expanded to 13 canonical Topics

Per Brady (21 May 2026): "Let's see what happens when you have many more topics. I would expect this to naturally maximize at ~20 topics, so 13 is a great average to visualize. Update those related heatmaps and session information now."

### CSS

`.heatmap-grid` grid-template-columns expanded from 4 to **13 columns**:
```css
grid-template-columns: 160px repeat(13, minmax(108px, 1fr));
min-width: 1580px;
```
Container's `overflow-x: auto` kicks in on smaller viewports for horizontal scroll. Designed to scale up to ~20 Topics per Brady's expected ceiling.

### S3 (Skill heatmap)

- Column headers: 4 action-statement labels → **13 canonical Topic names** matching the student portal taxonomy (Basic Syntax & Data Types · Control Flow & Logic · Functions & Modular Programming · Data Structures: Lists, Tuples, Sets, Dictionaries · Working with Files & I/O · Error Handling & Debugging · Object-Oriented Programming (OOP) · Python Libraries & Modules · Advanced Data Handling · Regular Expressions & String Manipulation · Working with Databases · Introduction to Automation · Introduction to Machine Learning).
- All 15 visible learner rows now have **13 cells each** (195 cells total). Score distributions per learner status:
  - Mastery (A.J., K.L., M.K., D.W.): scores 84–98 (h7–h9 darker greens)
  - On-track (P.A., J.T., R.M., E.G., N.B., L.O.): scores 63–82 (h5–h7 light greens)
  - Watch (T.V.): scores 54–68 (h3–h5 amber/transitional)
  - At-risk (Sally, B.F., C.S., H.D.): scores 15–62 (h1–h3 reds), with Sally's exact 13 values matching her S5 Per-Topic table

### S4 (At-risk mini-heatmap)

- Same column expansion: 4 → 13 canonical Topic names.
- 4 at-risk rows × 13 cells (52 cells total).
- Right-side summary card "Lowest Topic score" value updated from "Manipulates Data Structures" → **"Data Structures: Lists, Tuples, Sets, Dictionaries"** (canonical name).

### S6 (Coaching sessions list)

Topic column values updated from action-statement labels to canonical Topic names. Mapping based on each session's LO context:

| Session | Old Topic | New Topic |
|---|---|---|
| 09 | Manipulates Data Structures | Data Structures: Lists, Tuples, Sets, Dictionaries |
| 08 | Manipulates Data Structures | Data Structures: Lists, Tuples, Sets, Dictionaries |
| 07 | Identifies Python Constructs | Control Flow & Logic |
| 06 | Executes Python Code | Error Handling & Debugging |
| 05 | Creates Functional Programs | Functions & Modular Programming |
| 04 | Creates Functional Programs | Functions & Modular Programming |
| 03 | Executes Python Code | Basic Syntax & Data Types |
| 02 | Identifies Python Constructs | Basic Syntax & Data Types |
| 01 | Diagnostic | Diagnostic (all 13 Topics) |

LO column values (Lists & comprehensions, Define variables & types, etc.) stay unchanged — those were already LO-level and remain accurate within their canonical Topic.

### Canonical Topic taxonomy now consistent across

| Surface | Status |
|---|---|
| Student portal sidebar/snapshot | ✅ 13 Topics (canonical source) |
| S1 Dashboard (no Topic surface) | n/a |
| S2 Course view Skill cards | shows count "4 Topics" / "3 Topics" — count only, no names |
| **S3 heatmap (this commit)** | ✅ 13 canonical Topics |
| **S4 mini-heatmap (this commit)** | ✅ 13 canonical Topics |
| S5 Sally Per-Topic table | ✅ 13 canonical Topics (from v4.101) |
| **S6 sessions Topic column (this commit)** | ✅ Canonical Topic names |
| S7 transcript eyebrow | "Lists & comprehensions" — LO-level reference, accurate |

### Storyboard stamp

v4.102 instructor portal.

---

## v4.101 — 21 May 2026 — S5 Topic naming aligned to student-portal canonical taxonomy; all 13 Topics scored

Per Brady (21 May 2026): "It says the diagnostic assessment was completed, so all 13 topics should have scores and last attempts. Do not leave those rows blank. Also, use the actual topic names, you have those in the student storyboard view, those are not mysteries or in need of random generation."

### What changed (S5 only)

**Replaced all 13 Topic rows with the canonical student-portal Topic taxonomy**, and gave Sally a diagnostic-baseline score on every Topic. Diagnostic-only Topics show "30 Apr 2026" (diagnostic date); coached Topics show their last-coaching-session date.

| # | Topic | Score | Last attempt |
|---|---|---|---|
| 1 | Basic Syntax & Data Types | 62 | 01 May 2026 |
| 2 | Control Flow & Logic | 28 | 05 May 2026 |
| 3 | Functions & Modular Programming | 44 | 04 May 2026 |
| 4 | Data Structures: Lists, Tuples, Sets, Dictionaries | 22 | 06 May 2026 |
| 5 | Working with Files & I/O | 38 | 30 Apr 2026 |
| 6 | Error Handling & Debugging | 33 | 05 May 2026 |
| 7 | Object-Oriented Programming (OOP) | 41 | 30 Apr 2026 |
| 8 | Python Libraries & Modules | 25 | 30 Apr 2026 |
| 9 | Advanced Data Handling | 18 | 30 Apr 2026 |
| 10 | Regular Expressions & String Manipulation | 22 | 30 Apr 2026 |
| 11 | Working with Databases | 30 | 30 Apr 2026 |
| 12 | Introduction to Automation | 19 | 30 Apr 2026 |
| 13 | Introduction to Machine Learning | 15 | 30 Apr 2026 |

- Every Topic has a real score (no em-dashes, no "Not yet attempted") — consistent with "Diagnostic Complete: Yes" in the Profile card.
- Topics with continued coaching (#1, 2, 3, 4, 6) have last-attempt dates after diagnostic (30 Apr); the other 8 are at diagnostic baseline.
- **Profile card "Stuck on Topic"** updated from "Manipulates Data Structures" → **"Data Structures: Lists, Tuples, Sets, Dictionaries"** (matches table row #4, the canonical student-portal Topic name).

### Cross-screen alignment status (after v4.101)

| Screen | Topic naming convention | Reconciled to student-portal taxonomy? |
|---|---|---|
| **Student portal** (sidebar, progress map, snapshot) | Basic Syntax & Data Types, Control Flow & Logic, ... | ✅ Canonical source |
| **S5 instructor profile** (this commit) | Same as student portal | ✅ Aligned |
| **S3 instructor heatmap** | Identifies Python Constructs, Executes Python Code, Manipulates Data Structures, Creates Functional Programs | ❌ Still uses old 4 action-statement labels |
| **S4 at-risk mini-heatmap** | Same 4 action-statement labels as S3 | ❌ Still uses old labels |
| **S6 coaching sessions list** | Topic column shows 4 action-statement labels | ❌ Still uses old labels |

### Open follow-up — explicit

**S3-06 / S5-09 reconciliation still pending.** S3 heatmap columns, S4 mini-heatmap columns, and S6 "Topic" column values all reference the 4 old action-statement labels. With S5 + student portal now using the 13 canonical Topic names, the heatmaps need to either expand to 13 columns OR be restructured around the canonical taxonomy. This is the next coordinated cross-screen pass.

### Storyboard stamp

v4.101 instructor portal.

---

## v4.100 — 21 May 2026 — S5 Per-Topic table populated to all 13 Python Skill Topics

Per Brady: "Populate the rest of the per-topic scores table with the other Python topic areas so JFT doesn't think I only listed 4 on purpose."

### What changed

Extended S5's Per-Topic scores table from 4 rows to **all 13 Topics** of the Python Skill, matching the canonical taxonomy:

| # | Topic | Sally's score | Last attempt |
|---|---|---|---|
| 1 | Identifies Python Constructs | 42 | 05 May 2026 |
| 2 | Executes Python Code | 55 | 06 May 2026 |
| 3 | Manipulates Data Structures | 28 | 06 May 2026 |
| 4 | Creates Functional Programs | 38 | 04 May 2026 |
| 5 | Working with Files & I/O | 44 | 02 May 2026 |
| 6 | Error Handling & Debugging | 33 | 30 Apr 2026 |
| 7 | Object-Oriented Programming (OOP) | — | Not yet attempted |
| 8 | Python Libraries & Modules | — | Not yet attempted |
| 9 | Advanced Data Handling | — | Not yet attempted |
| 10 | Regular Expressions & String Manipulation | — | Not yet attempted |
| 11 | Working with Databases | — | Not yet attempted |
| 12 | Introduction to Automation | — | Not yet attempted |
| 13 | Introduction to Machine Learning | — | Not yet attempted |

- Sally's profile reflects an at-risk learner: scores on 6 of 13 Topics (all low/med), 7 Topics not yet attempted.
- All 13 rows clickable → S6 conversation logs (consistent affordance). Unstarted Topics will show empty-state in production per JFT implementation.
- "0 of 13 Topics mastered" in the Profile card now reads correctly against the table.

### Known follow-up (reiterated)

Rows 1–4 (action-statement names like "Identifies Python Constructs") and rows 5–13 (student-portal Topic names like "Working with Files & I/O") use **two different naming conventions** within the same table. The S3 heatmap and rows 1–4 of this S5 table use the original action-statement labels; rows 5–13 + the student portal use the descriptive Topic-name convention. Hierarchical content reconciliation — picking ONE convention and applying it everywhere — remains the open S3-06 / S5-09 follow-up.

### Storyboard stamp

v4.100 instructor portal.

---

## v4.99 — 21 May 2026 — S5 Sally Profile rewrite + global no-"LO"-abbreviation + global date-only display

Three threads landed in this commit per Brady's S5 walkthrough verdicts + two cross-portal global directives.

### S5 Sally Profile — rewrite to Topic-level only

- **Removed** the "Sample design only" banner.
- **Eyebrow** "AT-RISK LEARNER PROFILE" → **"LEARNER PROFILE"** (generic; every learner row on S1's cross-Course roster routes here regardless of status).
- **Removed** the "Anonymized identifier `lnr_4a3b2c1d` · E010 · 28 active learners (rolling enrollment)" subtitle entirely — H1 "Sally" stands alone.
- **Profile card simplifications:**
  - LAST ACTIVE: "06 May 2026 17:54 UTC" → **"06 May 2026"** (date only)
  - STUCK ON: "Lists & comprehensions (Learning Objective 3.1)" → **STUCK ON TOPIC: "Manipulates Data Structures"** (Topic-level only)
  - **Removed** the "Learning Objective misses (last 9 sessions): 14" row — instructor reviews specific LO data via S6/S7 logs and transcript
  - MASTERY ACHIEVED "0 of 4" → **TOPICS MASTERED "0 of 13"** (aligned to the 13 Topics that make up the Python Skill)
- **Right card rebuilt as Per-Topic scores:**
  - Eyebrow "PER-LEARNING OBJECTIVE SCORES" → **"PER-TOPIC SCORES"**
  - Removed `Learning Objective` and `Pattern` columns
  - Removed all 8 LO rows; replaced with 4 Topic rows (Sally's per-Topic averages: Identifies Python Constructs 42 · Executes Python Code 55 · Manipulates Data Structures 28 · Creates Functional Programs 38)
  - Every row clickable → S6 (Conversation logs for that Topic)
  - Caption added: "Click any row to open Sally's conversation logs for that Topic."
- **Back button** label: "Back" → **"Back to At-risk filter"** (consistent with other screens)

### Global directive 1 — no "LO" abbreviation anywhere

Per Brady (21 May 2026): never shorten "Learning Objective" to "LO" in any user-facing surface.

- **tenant_admin/index.html**: 3 instances replaced
  - Production section copy: "(rename, threshold change, add LO)" → "(rename, threshold change, add Learning Objective)"
  - Meta-bar button label: "04 Topics & LOs" → "04 Topics & Learning Objectives"
  - JS tooltip in `enforceLoMinimum()`: "Add another LO before removing..." → "Add another Learning Objective..."
- **Coda RBAC canonical hierarchy callout**: removed the previous sanction of "LO" as acceptable shorthand. Now reads: *"'Learning Objective' is the correct term for each individual LLM coaching target. Never abbreviate to 'LO' anywhere in UI copy, code, docs, or communication (Brady's directive, 2026-05-21)."*
- "objective miss" event-term shorthand in badges is **still allowed** (Brady didn't ban that specific shorthand).

### Global directive 2 — date-only display in student + instructor views

Per Brady: no time-of-day timestamps in student or instructor views. Apply globally.

- **instructor/index.html** — stripped times from:
  - S1 cross-Course at-risk roster (4 rows: e.g., "06 May 17:54" → "06 May 2026")
  - S6 Coaching sessions list (9 rows: e.g., "06 May 18:21 UTC" → "06 May 2026")
  - S7 Conversation transcript chat-meta (7 spans removed: e.g., `<span>18:21:04</span>` deleted; conversation date stays in S7 eyebrow)
  - S8 Audit Trail event log (10 rows: e.g., "2026-05-06 18:21:00" → "06 May 2026")
  - S9 Access Denied footer: "Logged · 18 May 2026 14:22:07 UTC · evt_b1d5e342" → "Logged · 18 May 2026 · evt_b1d5e342"
- **student/index.html** — no changes needed (already date-only).
- **Note for §10.4 forensic audit logging**: S8 displays date-only per Brady's directive; the underlying audit-log data model in production must still retain full timestamps for forensic value. Display ≠ storage.

### Known follow-up

**S5-09 (new):** the Python Skill heatmap on S3 currently shows 4 Topic columns, but the canonical truth (per Brady) is 13 Topics in the Python Skill (matching the student-portal Topic taxonomy). S5 now displays "0 of 13 Topics mastered" while S3 displays 4 columns. Hierarchical content reconciliation is a separate pass — flagged earlier as S3-06 and now reinforced.

### Storyboard stamp

v4.99 instructor + tenant_admin portals. Other 4 portals unchanged.

---

## v4.98 — 20 May 2026 — S4 At-risk filter: extend v4.97 patterns + breadcrumb + summary card relabel

Extends the v4.97 S3 hydration to S4 (At-risk filter) and applies the same cleanup playbook.

### Behavior changes

- **Generalized `hydrateHeatmap()`** — now hydrates both `#screen-3` (15 visible learners) and `#screen-4` (4 at-risk learners) with the same ARIA grid + tooltips + clickable rows pattern. Status maps per screen so the row-level data-row-status is correct on both.
- **S4 row labels now clickable** → S5 (all 4 at-risk rows: Sally, B.F., C.S., H.D.) — was only Sally before.
- **S4 cells get hover tooltips**: `"Sally · Identifies Python Constructs · Score 42/100"` etc.
- **Filter chips on S4 wired** — All/Mastery/On track/Watch now navigate to S3 AND apply that filter (using `goToScreen(3); filterHeatmap('xxx');`). The At risk chip remains the active state.

### Copy and layout

- **Removed "Sample design only" banner** from S4 (matches S3 removal)
- **Fixed breadcrumb formatting**: was "Heatmap · At risk" as a single span; now properly split into "Heatmap" (clickable to S3) + chevron + "At risk" (current page)
- **Removed Sally's inconsistent arrow icon** + her bespoke onclick handlers on row+cells — Sally now renders identically to the other 3 at-risk learners, all hydrated by the JS
- **Right summary card eyebrow** "Course summary" → **"Python Skill summary"** (Skill-level naming per the metric ladder)

### Storyboard stamp

v4.98 instructor portal. Other 5 portals unchanged.

---

## v4.97 — 20 May 2026 — S3 Skill heatmap: filter wiring, ARIA grid, hover tooltips, back button, copy fixes

Resolves S3 (Python Skill heatmap) walkthrough findings S3-01 through S3-10.

### Behavior changes (S3-02, S3-03, S3-04, S3-10)

Added a v4.97 hydration block to the JS that runs on initial S3 setup:
- **`hydrateHeatmap()`** — converts the heatmap into a proper ARIA grid:
  - `role="grid"`, `aria-readonly="true"`, `aria-label` describing the grid dimensions
  - Each column header gets `role="columnheader"` + `aria-colindex`
  - Each row label gets `role="rowheader"` + `aria-rowindex` + `data-row-status` (mastery/on-track/watch/at-risk based on the 15 visible learners)
  - Each cell gets `role="gridcell"` + `aria-rowindex` + `aria-colindex`
  - Each cell gets a `title` tooltip: `"Sally · Manipulates Data Structures · Score 28/100"`
  - Each row label is now clickable → S5 (Sally profile placeholder) with cursor:pointer + hover effect + aria-label
- **`filterHeatmap(status)`** — actually filters the heatmap:
  - Hides/shows rows based on `data-row-status` attribute
  - Updates the active chip styling
  - Updates the "Showing X of N learners" footer dynamically
  - Wired to chip onclicks via `data-filter-status` attribute

### Copy and layout changes

- **S3-01** — Renamed export button "Course report (PDF)" → **"Python Skill report (PDF)"** (Skill-level naming per the metric ladder)
- **S3-05** — Added the in-flow Back button block: **"Back to Course view"** → S2 (was missing entirely)
- **S3-07** — Removed `.heatmap-row-label.sally` CSS rule (red tinting + bold) — Sally's row now renders in default plaintext; heatmap-cell colors carry the at-risk cue
- **S3-08** — Removed the bottom alert "4 learners at risk. Sally lowest on Manipulates Data Structures" — heatmap colors and the red-dot status make the same point
- **S3-09** — Renamed eyebrow "Python Skill · Class heatmap" → **"Python Skill · Heatmap"** (no "class"; rolling enrollment, no fixed cohort)
- Removed the "Sample design only" banner from S3 (per Brady's directive)

### Known follow-up (S3-06)

The 4 heatmap column names ("Identifies Python Constructs", "Executes Python Code", "Manipulates Data Structures", "Creates Functional Programs") roll up Sally's 8 Learning Objectives — that satisfies the "Topic rolling up LOs" rule per Brady's exception. But the **13 Topics on the student portal don't match the 4 Topics in the instructor heatmap.** Hierarchical content reconciliation is a separate pass.

### S3-11 deferred

Cell-click drill-down to per-Topic Learning Objective breakdown — nice-to-have, not blocking.

### Storyboard stamp

v4.97 instructor portal. Other 5 portals unchanged.

---

## v4.96 — 20 May 2026 — Relocate Course Roster from S2 to S1 (cross-Course at-risk view)

Per Brady's second-pass feedback: the "Course Roster" on S2 (Course Detail) was conceptually misplaced — S2 should hold only Skill-specific data per the metric ladder. The roster data belonged on S1 (cross-Course view) or S3 (per-Skill view; the heatmap already serves that role).

### What changed (instructor portal only)

**S2 — Removed the entire Course Roster section:**
- "COURSE ROSTER" eyebrow + "Learners in E010" H2 — gone
- "Open Python Skill heatmap" standalone button — gone (each Skill card already has its own "Open Heatmap" button)
- Chip-filter bar (All / Mastery / On track / Watch list / At risk) — gone
- Roster table with per-Skill score columns — gone
- "—" footnote — gone

**S2 is now focused on Skill-level data only:** breadcrumb → header → 2 Skill cards → Back to Dashboard. Clean and on-spec.

**S1 — Added cross-Course "Learners needing attention" section** below the 3 Course cards:
- "ACROSS ALL YOUR COURSES" eyebrow
- H2: "Learners needing attention"
- Chip-filter bar with cross-Course totals: All (68) · Mastery (7) · On track (56) · Watch list (1) · At risk (4) [active]
- 4-row table: Learner | Course | Status | Last active | View profile
- All 4 at-risk learners currently in E010 (placeholder data); Course column shows which Course they're at-risk in
- Each row → S5 (Sally profile); "View profile" buttons → S5

### Conceptual model after v4.96

| Screen | Data scope | What's there |
|---|---|---|
| **S1 Dashboard** | Multi-Course + cross-Course roster | 3 Course cards + at-risk roster across all Courses |
| **S2 Course Detail** | Per-Skill within one Course | Skills (2 active) + Skill KPIs |
| **S3 Skill View** | Per-Topic within one Skill (the heatmap) | Topic × Learner grid |
| **S4 At-risk Filter** | Per-Skill at-risk subset | Filtered heatmap |
| **S5 Sally Profile** | Individual learner | Per-Learning-Objective scores |

### Storyboard stamp

v4.96 across the instructor portal. Other 5 portals stay at v4.91 (or v4.95 for tenant_admin / super_admin which got the floating-actions fix).

---

## v4.95 — 20 May 2026 — S2 second-pass refinements + cross-portal floating-actions accessibility fix

Resolves S2-13 through S2-19 from the S2 (Course view) second-pass walkthrough, plus a cross-portal layout fix to remove the floating-overlay button.

### S2 Course view refinements (instructor portal)

- **S2-13 — Python Skill card "4 learners at risk" badge now clickable** → routes to S4 At-risk filter (matches the S1 E010 card pattern). Uses `event.stopPropagation()` so it doesn't bubble up to the card-level S3 navigation.
- **S2-14 — Skill cards on S2 now have full a11y attributes:** `role="button"`, `tabindex="0"`, `aria-label` ("Open Python Skill heatmap" / "Open Git & Version Control Skill heatmap"). Matches the S1 E010 card a11y pattern.
- **S2-15 — Replaced uninformative "Active" eyebrow with a "Live" status badge** inline with the Skill title. Cross-platform status terminology proposed: **Testing** (amber/warning) for Skills under verification by admins/instructors, and **Live** (green/success) for Skills deployed to students with Topics locked. Recommended for ALL 4 user types (Student, Instructor, Tenant Admin, Super Admin) — "Testing" is clearer than "Test", "Live" is less technical than "Production"/"Prod".
- **S2-16 — Renamed "View full roster (heatmap)" button** to **"Open Python Skill heatmap"** — specific to which Skill's heatmap opens (was ambiguous with 2 Skills now in E010).
- **S2-18 — Removed `<strong>` bold from Sally's name in Roster table.** All learner names now render in default plaintext (matches default font styling site-wide).
- **S2-19 — Added chip-filter bar to Course Roster:** All (28) · Mastery (7) · On track (17) · Watch list (1) · At risk (4) [active]. Same pattern as the S3 heatmap filter.
- **Bonus:** Renamed roster heading from "Learners needing attention (4 of 28)" to **"Learners in E010"** — the filter chip below now communicates which subset is shown, no need to bake "4 of 28" into the heading.
- **Bonus:** All 4 at-risk row "View profile" buttons now route to **S5 Sally profile** (was S4 for non-Sally rows). Matches Brady's "clicking this row goes to Screen 05" verdict — JFT will parameterize per-learner profile in production.

### S2-17 — Cross-portal floating-actions accessibility fix (3 admin portals)

The old `.floating-actions` CSS used `position: fixed; bottom: 200px; right: 32px;` to overlay the page — caused overlap with content (e.g., the roster table on S2) and broke keyboard/screen-reader flow.

**New `.floating-actions` rule** (applied to instructor, super_admin, and tenant_admin portals):
```css
.floating-actions {
  display: flex; gap: var(--pgn-spacing-2);
  justify-content: flex-end;
  margin-top: var(--pgn-spacing-5);
  padding: var(--pgn-spacing-3) 0;
}
```

- Removed: `position: fixed`, `bottom`, `right`, `background`, `backdrop-filter`, `padding`, `border-radius`, `border`, `box-shadow`, `z-index`
- Added: in-flow flex layout, right-aligned, vertical spacing above the footer
- Removed associated dark-mode override (no overlay → no background to override)
- Net effect: the Back/return button now renders at the bottom-right of the page content, just above the footer — matches the student portal's `.pm-bottom-actions` pattern

### Storyboard stamp

v4.95 across instructor, super_admin, tenant_admin. Student and help portals stay at v4.91.

---

## v4.94 — 20 May 2026 — Instructor S1 Dashboard: full E010 card clickable, regional click routing

Follow-up to v4.93 per Brady's directive: the big E010 Course card on the Dashboard needs more clickable regions, not just the title link and "Open Course details" button.

### What changed (instructor portal only)

- **Entire E010 Course card now clickable** → routes to **S2 Course view**.
  - `<div class="section-card recommended">` gained `onclick="goToScreen(2)"`, `cursor:pointer`, `role="button"`, `tabindex="0"`, and `aria-label="Open E010 Course details"`.
  - The course-title `<a>` link was simplified (still readable as a course title, no longer needs its own onclick — the parent card handles navigation).
- **Skill region clicks now route to S3** correctly via `event.stopPropagation()`.
  - Python Skill nested card and Git Skill nested card both got `event.stopPropagation(); goToScreen(3);` on their onclick, so clicks inside the Skills region don't bubble up to the parent E010 card.
- **"4 at risk" header badge is now a clickable link** → routes to **S4 At-risk filter** (consistent with the same badge on S2). Uses `event.stopPropagation()` to prevent bubbling to the parent E010 card.

### Click-region map verified (functional test)

| Clicked region | Lands on |
|---|---|
| E010 card body (KPIs, eyebrow, title, subtitle) | **S2** Course view |
| `4 at risk` header badge | **S4** At-risk filter |
| Python Skill nested card | **S3** Skill view (heatmap) |
| Git Skill nested card | **S3** Skill view (heatmap) |
| Either "Open Heatmap" button inside Skill cards | **S3** Skill view (heatmap) |

### Storyboard stamp

v4.94 across the instructor portal. Other 5 portals stay at v4.91.

---

## v4.93 — 20 May 2026 — Instructor S2 Course view refined: Skill-level metrics only, second Skill added, learner roster surfaced

Resolves the S2 (Course view) walkthrough findings S2-07 through S2-12 per Brady's verdicts.

### What changed (instructor portal only)

- **Removed** the "Course aggregate metrics" card (`Across all Skills in this Course` with 6 KPI tiles) — duplicated S1 Dashboard E010 KPIs and violated the "Skill-level perspective" rule for S2.
- **Removed** the "Sample design only" disclaimer banner from S2.
- **Renamed** section heading `Coaching modules (1 active)` → `Skills (2 active)` (terminology enforcement — "module" is on the banned-terms list per the RBAC canonical hierarchy callout).
- **Made the header badge `4 learners at risk` a real link** — now routes to S4 At-risk filter (was non-clickable static badge).
- **Dropped redundant "Skill" from card eyebrows** — eyebrow now reads `Active` instead of `Skill · Active` (the card title `Python Skill` already names the entity).
- **Added a second Skill — Git & Version Control Skill** — appears on S2 (full card with KPIs + Open Heatmap CTA) and on S1 Dashboard's E010 card (compact row). Course E010 now shows `SKILLS IN THIS COURSE (2 active)` instead of `(1 active)`. Sample data: 22 learners practicing, 68% avg Topic mastery, 3 Topics, 0 at risk.
- **Added a Course Roster section to S2** — `Learners needing attention (4 of 28)` compact table showing the 4 at-risk learners (Sally, B.F., C.S., H.D.) with per-Skill scores across both Python Skill and Git Skill. "—" indicates learner has not started practicing that Skill yet. Each row links to the at-risk filter or Sally's profile.
- **NO time-related metrics anywhere** — per Brady's directive: no "time-on-platform", no "average session length", no "time-since-last-active" beyond the human-readable "last active" timestamp.

### Followed Brady's framing of the metric ladder

| Screen | Granularity | Example KPIs |
|---|---|---|
| **S1 Dashboard** | per-Course | 28 active learners · 76% Avg Skill score · 4 at risk |
| **S2 Course view** | per-Skill | Python Skill: 28 practicing, 76% avg Topic mastery; Git Skill: 22 practicing, 68% |
| **S3 Skill view (heatmap)** | per-Topic | Cell = learner × Topic mastery within one Skill |

### Storyboard stamp

v4.93 across the instructor portal. Other 5 portals stay at v4.91.

---

## v4.92 — 20 May 2026 — Instructor portal: Course view inserted as Screen 02, screens renumbered 01-09, S2 findings cleared

Resumes the S2 critical walkthrough by acting on Brady's verdict on S2-01 through S2-06 (per session findings). Major architectural change to the instructor flow.

### What changed

- **Screen renumbering: all 8 instructor screens renumbered 01-09 starting at Screen 01 (Dashboard)** — the original Screen 01 (SSO splash) was removed in v4.85; this pass closes that gap. New navigation hierarchy:
  - **Screen 01** — Instructor Dashboard (Course list with Skills nested in each Course card)
  - **Screen 02** — Course view (NEW — aggregate Course metrics + Skills deployed in the Course)
  - **Screen 03** — Skill view (Python Skill heatmap, was old Screen 03 reframed as Skill-level)
  - **Screen 04** — At-risk filter applied
  - **Screen 05** — Sally drill-down
  - **Screen 06** — Coaching sessions
  - **Screen 07** — Session transcript
  - **Screen 08** — Audit trail
  - **Screen 09** — Access denied
- **Screen 01 Dashboard restructure** — Each Course card now shows its Skills nested inline. E010 card shows the Python Skill with mastery stats + Open Heatmap CTA. E075 and E135 show their Skills (Python Intermediate, Libraries, OOP, Design Patterns) as compact rows.
- **Screen 02 Course view (new)** — Opens when instructor clicks `E010 · Foundations of Programming (Python)` from Dashboard, or via the "Open Course details" link. Shows Course aggregate metrics, Skills deployed in the Course, and per-Skill drill-down CTAs.
- **Screen 03 Skill view (relabeling)** — Heatmap now framed as a Skill-level view. Header reads `Python Skill — Topic mastery`, breadcrumb now reads `Instructor Dashboard › E010 › Python Skill › Heatmap` (Skill node added).
- **Breadcrumbs across S3-S8** — `goToScreen(2)` (Dashboard) updated to `goToScreen(1)` everywhere; E010 link in S4/S5/S6 breadcrumbs now routes to Course view (S2) instead of Heatmap (S3).
- **Floating "Back to dashboard" actions on S8 and S9** — updated to `goToScreen(1)`.
- **Meta-bar** — 9 buttons starting at "01 Dashboard home" with new "02 Course view" and "03 Skill view" labels.
- **TOTAL_SCREENS comment** updated to note v4.92 renumbering.

### S2 walkthrough findings resolved (S2-01 through S2-06)

- **S2-01 + S2-03** (dead E075/E135 cards + E010-only drill-down) — Resolved by the new Course view + Skills-nested-in-Course pattern. Course cards no longer have dead `cursor:pointer`; all Skill drill-downs are explicit clickable elements.
- **S2-04** (redundant alert "4 learners flagged at-risk in E010 today") — Removed entirely.
- **S2-05** (degenerate single-item breadcrumb on entry screen) — Removed.
- **S2-06** ("Diagnostic in flight" on E135) — Removed. E135 now shows real KPIs (18 learners, 71% Avg Skill score, 0 at risk).

### Known follow-ups

- Screenshots in `instructor/screenshots/` and `instructor/screenshots_dark/` are still numbered against the old 02-09 sequence. Regeneration deferred until the storyboard fully stabilizes.
- S7 and S8 breadcrumbs still skip the Course + Python Skill layers (`Dashboard › Sally › ...`) — pragmatic shortcut for the deeper screens; can be revisited.

### Storyboard stamp

v4.92 across the instructor portal. Other 5 portals stay at v4.91 (no changes).

---

## v4.91 — 20 May 2026 — Correct hierarchy terminology: Topic / Learning Objective (replaces v4.90 mislabeling)

Mid-session correction after Brady clarified the full 6-level platform hierarchy. v4.90 had renamed Topics as Skills in the student portal — wrong granularity. v4.91 corrects to the canonical hierarchy: **Platform > School > Course > Skill > Topic > Learning Objective**.

### What changed (corrections to v4.90)

- **Student portal** — "13 Skills" / "sub-sections" → **"13 Topics"** (8 instances: sidebar card label, aria-label, footer note, progress map stats, welcome-back table rows, session snapshot rows)
- **Help portal** — reverted the v4.90 meaning-change bug: "Retiring a Skill from production" → **"Retiring a Topic from a production Skill"** (the original intent was Topic-level lifecycle, not Skill-level)

### What changed (new in v4.91)

- **Instructor portal (all 8 screens)** — "competency" / "Competency" / "objective" / "Objective" replaced in user-facing copy:
  - S2 stat tile: "Avg competency" → "Avg Skill score"
  - S3 heading + cell labels: "competency mastery" + "Competency →" → "Topic mastery" + "Topic →"
  - S4 filter description + summary: "Lowest competency" → "Lowest Topic score"
  - S5 badge: "AI-scored competency: Low" → "AI-scored Skill mastery: Low"
  - S5 table headers: "Competency" → "Topic", "Objective" → "Learning Objective"
  - S5 profile: "(Objective 3.1)" → "(Learning Objective 3.1)", "objective misses" → "Learning Objective misses"
  - S5 eyebrow: "Per-objective scores" → "Per-Learning Objective scores"
  - S6 table header: "Objective" → "Learning Objective"
  - S7 eyebrow: "3 objective misses" → "3 Learning Objective misses"
  - S8 stat tile: "objective misses" → "Learning Objective misses"
- **READMEs** — terminology fixes in `README.md`, `instructor/README.md`, `student/README.md`, `tenant_admin/README.md` (8 instances across "sub-sections", "competency", "Program Subject")
- **Coda RBAC doc** — replaced v4.90 4-level callout with corrected 6-level Canonical Terminology block (Platform → School → Course → Skill → Topic → Learning Objective) plus enforced terminology rules

### What is NOT changed

- "objective miss" badges in instructor S6 / S7 (e.g., `objective miss × 3`) — retained as established SkillProof event-term shorthand, sanctioned in the RBAC callout
- CSS class names like `.practice-areas-card` — internal selectors retained for v4.91; rename deferred to a follow-up commit
- CHANGELOG historical entries (e.g., v4.73 "Program Subject" note) — immutable history

### Storyboard stamp

v4.91 across the 6 portals.

---

## v4.90 — 20 May 2026 — Standardize Skill/Course/School/Platform hierarchy terminology site-wide (initial pass, superseded by v4.91)

Initial hierarchy standardization based on Brady's 4-level model (Platform / School / Course / Skill). Subsequently corrected by v4.91 after Brady clarified the full 6-level model adds Topic and Learning Objective beneath Skill. See v4.91 for the canonical hierarchy.

### What changed

- Student portal — "Practice Areas" / "sub-sections" → "Skills" (later corrected to "Topics" in v4.91)
- Student portal — added `E010` Course node to all 6 coaching breadcrumbs (retained in v4.91)
- Super Admin portal — "Coaching module" → "Skill" (5 instances; retained)
- Tenant Admin portal — "Program Subject" → "Course" (2 instances; retained)
- Help portal — "Retiring a topic from a production Skill" → "Retiring a Skill from production" (reverted in v4.91 as meaning-change)
- Coda RBAC doc — added hierarchy callout (later replaced with 6-level version in v4.91); fixed §4.1 Instructor-assigned-to-Course error (retained)

### Storyboard stamp

v4.90 (superseded by v4.91 same day).

---

## v4.89 — 19 May 2026 — Strip superfluous labels (LRPS demo shortcut + Not for student use + build stamp) and passive governance banners

Two cleanup passes per Brady's directive.

### What changed

- **LRPS landing** (`index.html`) — removed three label families:
  - `demo shortcut` badges on the Tenant Admin + Super Admin rows (×2 elements)
  - `(demo shortcut)` suffix trimmed from the two corresponding `aria-label`s
  - `Not for student use` badges on the Instructor, Tenant Admin, Super Admin rows (×3 elements)
  - Footer build stamp paragraph `Build: 20260507 · LRPS v3.4.2 · SkillProof-styled storyboard recreation`
  - Associated CSS: `.no-student-badge` rule block + the comment + `max-width / overflow / text-overflow` overrides in `.pgn__data-table tr.live .lrps-name` that existed solely to accommodate the badge
- **Tenant Admin Screen 4** (`tenant_admin/index.html`) — removed both passive informational alert banners:
  - "This Skill is in Production. Topics cannot be removed once a Skill is live…"
  - "Every topic must have at least one Learning Objective…"
  - These rules are now enforced exclusively by action-triggered UI (disabled `Remove topic` buttons with `title=` tooltip + `enforceLoMinimum()` JS) — the same enforcement that was already in place. Rules themselves migrate to user instruction docs.

### Storyboard stamp

v4.89 across the 6 portals.

---

## v4.88 — 19 May 2026 — Strip 'SkillProof Design System v1.2' from HTML comments

Follow-up to v4.87 — Brady's directive was "anywhere," so the phrase was also stripped from the developer comments at the top of each portal file. Each occurrence of `SkillProof Design System v1.2` replaced with `design tokens` so the surrounding comment text still reads.

### Storyboard stamp

v4.88 across the 6 portals.

---

## v4.87 — 19 May 2026 — Strip 'SkillProof Design System v1.2' meta-bar text + remove unrequested 'Technical contact' footer link

Two clean-up passes per Brady's directive.

### What changed

- **Meta-bar header** in 4 portals (root LRPS, instructor, tenant_admin, super_admin) — removed the `· SkillProof Design System v1.2 ·` segment. Now reads `DEMO ONLY · [Portal name] · Persona: [Name]`.
- **Footer** in all 6 portals (root, student, instructor, tenant_admin, super_admin, help) — removed the `| Technical contact: Vivek` `mailto:vivek@wgu.edu` link I had added in v4.78 without explicit ask. Footer now ends at Honor Code.
- **Screen 17 identity card** in tenant_admin — removed the `Contact Vivek for changes` mention; now reads `Tenant ID tenant_school_tech · managed centrally by WGU.` and stops there.

### Storyboard stamp

v4.87 across the 6 portals.

---

## v4.86 — 19 May 2026 — Apply student-style storyboard shortcut bar to all 3 admin portals

Brady: *"I like the update you did to the student flow shortcut bar at the bottom of the page with the 'back' button in the upper right corner of the shortcut bar that goes back to the LRPS page. I also like that you added a short description along with the screen numbering in that bar. Apply all of those updates to all the other prototype screens in the other 3 user scenarios."*

### What changed

For each of `super_admin/`, `tenant_admin/`, `instructor/`:

1. **`← Storyboard Index` link** added to the upper-right of the meta-bar-header, pointing back to the LRPS root (`../`). Uses the new `.meta-link` CSS rule (mirrors student's pattern).
2. **Short descriptions** appended to every step-btn label so you can see what each screen is at a glance:
   - super_admin: `02 Portal home` · `03 Token usage` · `04 Cost spike` · `05 Rate limits` · `06 Compliance` · `07 Geo-redundancy` · `08 Audit log` · `09 Access Control` · `10 External Tooling` · `11 Data Hub` · `12 Instructor Roster` · `13 School Mgmt` · `14 Access Denied`
   - tenant_admin Flow A: `02 Portal home` · `03 New Skill` · `04 Topics & LOs` · `05 Model & Coaching` · `07 Deploy review` · `08 Deploy success` · `17 School Settings` · `18 Skill Lifecycle` · `19 Analytics` · `20 Activity Log` · `21 Access Denied`
   - tenant_admin Flow B: `09 All systems OK` · `10 LLM down` · `11 Notification` · `12 P1 ticket` · `13 Ticket submitted` · `14 CSM response` · `15 Service restored` · `16 SLA dashboard`
   - instructor: `02 Dashboard home` · `03 Class heatmap` · `04 At-risk filter` · `05 Sally profile` · `06 Conversation logs` · `07 Session transcript` · `08 Audit Trail` · `09 Access Denied`

### Storyboard stamp

v4.86 across the 6 portals.

---

## v4.85 — 19 May 2026 — Remove Screen 01 (SSO landing) from admin portals

Brady: *"Let's remove Screen 01 from the instructor, tenant admin, and super admin. Those are informational only and should have been removed a long time ago when I directed that we only include the screens and features for JFT to implement. No extra features or text or buttons or anything else that is outside of the requirements of the contract language."*

The SSO landing screens were illustrative — they showed the authentication handshake (LRPS deep link verified · WGU SSO complete · LTI role + elevation) but nothing for JFT to build. Auth is contractually LTI 1.3 + WGU SSO; the prototype shouldn't depict the auth ceremony at all.

### What was removed

- `super_admin/index.html` — Screen 1 (~50 lines): "Welcome to the Super Admin Portal" SSO splash + Continue button + meta-bar `01` step-btn
- `tenant_admin/index.html` — Screen 1 (~45 lines): "Welcome to the School Admin Portal" SSO splash + Continue button + meta-bar `01` step-btn
- `instructor/index.html` — Screen 1 (~45 lines): "Welcome to the Instructor Dashboard" SSO splash + Continue button + meta-bar `01` step-btn

In each portal, screen-2 (the actual portal home) is now marked `class="screen active"` so it's the default screen on load. The meta-bar's `02` step-btn carries the `active` class.

### What is NOT changed

- `student/` Screen 1 (the Coding Coach intro / Begin Diagnostic landing) stays. It's a legitimate first screen of the student flow, not an SSO splash.
- LRPS landing (root `index.html`) stays — it's the entry point that distributes to each persona portal.
- TOTAL_SCREENS counter and arrow-key navigation already had fall-through for missing screen IDs (since v4.74 / v4.85 introduced the screen-1 + screen-6 gaps in admin portals).
- `goToScreen(2)` references unchanged — that's now the entry point.

### Storyboard stamp

v4.85 across the 6 portals.

---

## v4.84 — 19 May 2026 — Larger school logos in navbar (so 'School of X' text reads)

Brady: *"Now increase the school-level logo in the upper-left corner to the larger size you did with the standard WGU logo. Right now, it's so small I can't read the lettering for 'School of XXX'."*

The school logos have a stacked WGU + horizontal line + school-name layout, so at the 40px shared height set in v4.80 the school-name text portion was only ~13px tall — illegible. Bumped to **64px** specifically for school logos via the `[data-school-logo]` attribute selector, leaving the WGU corporate logos at 40px:

```css
.navbar-brand-logo { height: 40px; width: auto; }
.navbar-brand-logo[data-school-logo] { height: 64px; }
```

Applied to all 6 portals (only the school-logo navbars in `tenant_admin/`, `student/`, `instructor/` actually pick up the override; the others have WGU corporate logos without the data attribute).

### Storyboard stamp

v4.84 across the 6 portals.

---

## v4.83 — 19 May 2026 — Dark-mode footer theming (deep navy + white text, all 6 portals)

Brady's directive: *"The dark mode footer needs to have the dark navy background and white text like the header does so it's legible and accessible in dark mode. All you did in the footer was update the logo file. Apply the other dark mode theming and make sure that's also deployed across every page of the prototype."*

The footer markup uses hardcoded inline styles (`background: #F5F7FA`, `color: #002855`, etc.) that don't respond to `[data-theme="dark"]`. Added a CSS override block to each of the 6 portals that targets `footer[role="contentinfo"]` with `!important` to win over the inline styles:

```css
[data-theme="dark"] footer[role="contentinfo"] {
  background: var(--color-deep-navy) !important;
  border-top-color: rgba(255,255,255,0.1) !important;
}
[data-theme="dark"] footer[role="contentinfo"] > div {
  border-bottom-color: rgba(255,255,255,0.1) !important;
}
[data-theme="dark"] footer[role="contentinfo"] a { color: #fff !important; }
[data-theme="dark"] footer[role="contentinfo"] span { color: rgba(255,255,255,0.7) !important; }
```

Applied identically to root `index.html`, `student/`, `instructor/`, `tenant_admin/`, `super_admin/`, and `help/`.

Light-mode header + footer were already consistent across all 6 portals; no light-mode changes needed.

### Verification

- Toggle dark mode on any portal → footer flips to deep-navy background with white link text, semi-transparent white copyright + divider pipe colors
- All 6 portals respond identically
- Light mode unchanged

### Storyboard stamp

v4.83 across the 6 portals.

---

## v4.82 — 19 May 2026 — Help button in every navbar

Brady's directive: *"The help button should be in the header across ALL pages on the site, no matter what."*

The LRPS landing root (`index.html`) had no Help button. Added one next to the theme toggle (matches the `.btn-theme-toggle` icon pattern used by other admin portals, links to `help/index.html#submit-request`).

The help page itself (`help/index.html`) also got a Help icon button in its navbar — it re-anchors to the form on the same page (`#submit-request`).

All 6 portals now carry a Help icon in their navbar:

| Portal | Pattern | Target |
|---|---|---|
| `/` (LRPS landing) | `.btn-theme-toggle` icon link | `help/index.html#submit-request` |
| `student/` | `.btn-theme-toggle` icon link | `../help/index.html#submit-request` |
| `instructor/` | `.btn-theme-toggle` icon link | `../help/index.html#submit-request` |
| `tenant_admin/` | `.navbar-help-link` pill (existing) | `../help/index.html#submit-request` |
| `super_admin/` | `.btn-theme-toggle` icon link | `../help/index.html#submit-request` |
| `help/` | `.btn-theme-toggle` icon link | `#submit-request` (re-anchor) |

### Storyboard stamp

v4.82 across the 6 portals.

---

## v4.81 — 19 May 2026 — Help page rewrite + remove floating support pill + CHANGELOG prune

Four-item batch from the second audit follow-up.

### What changed

- **`help/index.html` rewritten end-to-end** to match the rest of the site's chrome (Paragon-aligned tokens, WGU corporate navbar with theme toggle + Help & Support chip + 40px logo, standard WGU footer with Vivek link). 823-line page collapsed to ~330 lines.
- **Page content trimmed to two sections only**:
  1. The Zendesk-style support form (`id="submit-request"` anchor preserved, so existing portal Help-button anchor links still work)
  2. A flat help-docs list — 15 role-tagged article links (Student / Instructor / Tenant Admin / Super Admin / All admin roles). No cards, no videos, no external links.
- **Removed** from the help page: the floating "Contact JFT Support" pill, the 4-card Self-service support grid, the Recent updates feed, the entire Video training resources section (role-chip filter, featured callout, video tiles), and the custom-styled brand-logo gradient block.
- **CHANGELOG pruned** — pre-v4.69 entries (v4.0–v4.68, ~3,300 lines) replaced with a one-line "history exists in git" note. Per Brady's directive: this is a prototype; incremental change documentation isn't important. Pre-v4.69 references to deleted files (`presentation.html`, `presentation_dark.html`, `_contract_tracking/`) cleared in the same pass.
- **Storyboard stamp** v4.80 → v4.81 across all 6 portals.

### Why

Brady's audit response:
- *"Remove the support pill. We don't need it."*
- *"That help page is terrible. It needs a complete rewrite to come into compliance with the header/footer/styling we've implemented across the site. I also only want the help form and help docs. No videos and external links. This page is much too complicated right now."*
- *"I don't care much about the changelog. This is a prototype, so incremental change documentation is not very important."*

### Verification

- `https://brady-wgu.github.io/SkillProof/help/` → standard WGU navbar at top (matches admin portals); standard WGU footer at bottom with Vivek link; Zendesk-styled support form; below the form, the flat docs list; no floating Contact JFT pill; no video tiles; no Recent updates feed; no external links other than the WGU policy URLs in the footer.
- Help button on every portal still anchors to `help/index.html#submit-request` and lands on the form.

---

## v4.80 — 19 May 2026 — Audit follow-ups (School identity trim · bigger logos · Zendesk-styled help · student Help link)

Follow-up batch after the v4.79 review. Five-item delivery:

### 1. Screen 17 School identity card simplified

The 6-row info table (Tenant ID, Parent Org, Operated by, LRPS launch URL, Assigned JFT CSM, Your role scope) was redundant — none of those fields are user-modifiable, so the School Admin couldn't act on any of it. Replaced the whole table with a single sentence:

> Tenant ID `tenant_school_tech` · managed centrally by WGU. Contact Vivek for changes.

The school name (h2) stays for context; the Tenant ID stays in a `<code>` for support-ticket reference. Brady's directive: *"Remove almost everything in that box because they are not things the School Admin can change or modify in any way."*

### 2. Header + footer logos enlarged

Bumped logo height from `28px` → `40px` across all 6 portals — both the navbar (`.navbar-brand-logo { height: 40px; }`) and footer image inline styles. Brady's directive: *"The sizes of these in our prototype are WAY too small, so they need to be made much larger to be the same height as the other buttons and labels on the header and footer rows."*

Student portal's old `.navbar-brand-logo { width: 36px; height: 36px; }` rule (which was sized for a square text-mark) was simplified to `height: 40px; width: auto;` to fit the v4.72 school-logo image swap.

### 3. Help form refined to mimic a real Zendesk page

Replaced the bare form with a 2-column Zendesk-style layout on `help/index.html`:

- **Left column**: "WGU Support · powered by Zendesk" badge + h2 + form card with Subject + Description + LRPS-reissue request type + drag-drop Attachments area + Submit / Cancel buttons + success-state with request-ID copy
- **Right column**: "Suggested articles" aside with 5 article links + response-time note ("usually within 1 business day; P1 paged immediately")
- Form wrapper carries `id="submit-request"` so Help-button links anchor directly to it
- Required-field asterisks throughout

### 4. Help buttons across the site route to the form

Every Help button now uses `#submit-request` anchor so clicking lands the user directly on the support form:

- super_admin · tenant_admin · instructor — existing `<a class="navbar-help-link" href="../help/index.html#submit-request">` (or `btn-theme-toggle` variant)
- **student/** — added a Help icon button (previously had none); now matches admin portals

### 5. Version increment

v4.79 → v4.80 across the 6 portals. Future: every commit/push that ships UI changes should bump this version so Brady can spot when GitHub gets out of sync with local pushes.

### Companion external document

Started `OneDrive\_SkillProof\c_Deliverables\_From Brady to JFT\g_User Documentation\SkillProof_User_Documentation_Outline_v0_1_19MAY2026.md` — a bulleted outline organizing what to include in the eventual user-instruction docs for Tenant Admins, Instructors, Students, and Super Admins. Lives in OneDrive (not the public repo), per Brady's separation of prototype vs. supporting docs.

### Verification

- Screen 17 identity card → reads "School of Technology" + the one-line tenant ID sentence; no other rows
- Hard-refresh `https://brady-wgu.github.io/SkillProof/` → header WGU logo + each portal navbar logo + footer WGU logo all render at the new 40px height
- `help/index.html#submit-request` → lands at the form; the Zendesk styling is visible (powered-by badge, sidebar, attachments box)
- student/ navbar shows a Help icon next to the theme toggle
- v4.80 title stamp on all 6 portals

---

## v4.79 — 19 May 2026 — Analytics page iteration (no more timing things)

Phase K — the final phase of the original JFT meeting follow-ups. Per Brady's note *"Iterate on the analytics page. No more timing things,"* the arbitrary time-on-task metric is gone, replaced with a more meaningful active-learners trend.

### What changed (tenant_admin/index.html · Screen 19 Analytics & Reporting)

- **Engagement section, left panel** rebuilt:
  - Eyebrow: "Time on task · last 30 days" → "Active learners · last 30 days"
  - Subhead: "Median 18 min · per session" → "178 active learners · +14% vs prior 30 days"
  - Aria-label: "Time-on-task trend chart..." → "Active learners trend chart..."
  - Icon: `schedule` → `groups`
  - The existing SVG line chart stays (visually a learner-growth trend); only the framing changes from time-duration to learner-count.

The Submissions chart (right side), Class Insights table, Billing & Usage gauges, Cost by Skill table, and Program Reports section all stay as-is — none used arbitrary timing data.

### What stays as contractually-required SLA timings

Incident Response screens (SC-ADD-06, Screens 14–16) keep their SLA timings — 6-min first response, 60–90 min ETA — because those are signed in SOW §9.5 (P1 SLA = 2-hour response). Those are contractual, not arbitrary.

### Storyboard stamp

v4.79 across the 6 portals.

---

## v4.78 — 19 May 2026 — Help / Support flows + Vivek footer link

Phase J. Wires up the Submit LRPS Ticket button to a real `mailto:` action, refreshes the help page with an LRPS deep-link distribution note, and adds the Vivek technical-contact footer link across all 6 portals.

### What changed

- **tenant_admin Screen 8 (Deploy success)** — Submit LRPS ticket button is now an `<a>` with a `mailto:wgu-lrps-support@wgu.edu` link, pre-filled subject `LRPS Ticket — E135 OOP Python (School of Technology)` and a multi-line body including Tenant Admin, Skill, Build, Destination URL, and a Justification stub.
- **help/index.html** — added an "LRPS deep links" tile to the self-service card grid explaining WGU IT distributes the URL out-of-band. *(Tile was later removed in v4.81's help-page rewrite.)*
- **Footer — Vivek technical contact** added to all 6 portal footers (`super_admin/`, `tenant_admin/`, `instructor/`, `student/`, `help/`, root `index.html`). Pipe-separated next to Honor Code, `mailto:vivek@wgu.edu` placeholder.

### Storyboard stamp

v4.78 across the 6 portals.

---

## v4.77 — 19 May 2026 — Super Admin demotion tooltips + Instructor Downgrade affordance

Phase H. Brady's JFT note: *"Demotion to lower levels is also important to remember."* The v4.68 Access Control screen already had Downgrade buttons for Tenant Admins and Super Admin. This release adds context-specific tooltips explaining what each demotion does to scope assignments, and surfaces the missing Instructor → Student demotion affordance.

### What changed (super_admin/index.html · Screen 9 Access Control · People tab)

- **Jordan (Super Admin, disabled Downgrade)** — title tooltip: *"Demoting to Tenant Admin requires assignment to at least one School afterward. Currently blocked: minimum 2 Super Admins required at all times."*
- **Alice + Miguel (Tenant Admin Downgrade)** — title tooltip: *"Demoting to Instructor removes all School assignments and reverts to baseline read-only access on assigned Skills."*
- **Charlie + Priya (Instructor)** — added a third button "Downgrade" with title tooltip: *"Demoting to Student removes all Skill assignments and reverts to learner-only access."*
- Sally + Devon (Student) — stay as-is (Student is the baseline; no lower role to demote to).

### Storyboard stamp

v4.77 across the 6 portals.

---

## v4.76 — 19 May 2026 — School Settings rebuild (Screen 17)

Phase G. Tenant Settings renamed and simplified per Brady's JFT direction.

### What changed (tenant_admin/index.html · Screen 17)

- **Renamed to "School Settings"** across the surface — breadcrumb, eyebrow, h1, identity card eyebrow ("School identity"), branding h2 ("School logo"). The architectural identifier "Tenant ID" stays as the underlying tech name (matches the SOW).
- **Removed the accent color box** + the standalone "Accent color" form group.
- **"Parent organization" → "Parent Org"**.
- **Logo upload helper text added**: *"Max 2 MB · PNG or SVG · recommended 400 × 120 px"* directly under the School logo heading.
- **Logo preview images** swapped to the active school's logo with `data-school-logo` markers so they update on Switch School.
- **Cross-screen label sweep** — every other "Tenant Settings" user-visible reference now reads "School Settings" / "Skill Lifecycle".

*(In v4.80, the identity-card info table was further trimmed to a one-line sentence.)*

### Storyboard stamp

v4.76 across the 6 portals.

---

## v4.75 — 19 May 2026 — Skill Production Governance (topic remove + LO≥1 + deploy stages)

Phase F. Surface the production-Skill rules in the UI so JFT builds the right affordances. When a Skill is in Production, topics cannot be removed and the UI shows that constraint explicitly. Learning Objectives have a `≥ 1 per topic` floor enforced via UI state.

### What changed (tenant_admin/index.html)

**Screen 4 (Topics & Learning Objectives):**

- **Production-status banner** (alert-warning) above the topic list explaining production constraints
- **LO ≥ 1 banner** (alert-info) explaining the per-topic floor
- **All 4 "Remove topic" buttons disabled** with tooltip
- **New `enforceLoMinimum()` JS**: scans every topic on load + after `addTopic()`. If a topic has only 1 LO, that LO's delete button is disabled + tooltip

**Screen 7 (Review & Deploy):**

- **Bare 2-button deploy row replaced** with two explanatory cards side-by-side (Staging vs Production) with access-scope copy.
- **Step 3 summary table** updated to reflect the v4.74 wizard rebuild
- **Step 4 summary table** removed (no longer a separate wizard step).

### Storyboard stamp

v4.75 across the 6 portals.

---

## v4.74 — 19 May 2026 — Skill Creation Wizard rebuild (combined Screens 5+6)

Phase E. The wizard's "Model & Coaching" (Screen 5) and "AI Coaching Prompt" (Screen 6) merge into a single Screen 5; preset prompt fields replaced with free-text inputs; jailbreak + sandbox boxes removed (enforced globally per JFT); default model changed to gpt-4o-mini with OpenAI top-3 + OpenRouter browse-all; "Add topic" button wired to insert a new row; MD upload + download flow added.

### What changed (tenant_admin/index.html)

- **Screen 5 rebuilt end-to-end** as Step 3 of 4:
  - Model picker defaults to **gpt-4o-mini** (Recommended); top-3 alternatives are **gpt-4o** + **gpt-4-turbo** (all OpenAI). 1M / 1M token callout.
  - **"Browse all OpenRouter models"** `<details>` block expands to a 6-row table (Claude / Gemini / Llama / Mistral).
  - **Fallback chain** alert updated to OpenAI siblings.
  - **"Global coaching style"** → **"Coaching style"**. The 3 radio options (Socratic / Direct / Adaptive) stay.
  - **NEW inline "AI coaching prompt" section** below the coaching style:
    - **MD upload + download buttons** — preferred format `.md`. Upload disables the three text inputs.
    - **3 free-text inputs** with example placeholders (Student profile / Examples should be / Other), blank by default.
    - **Compiled prompt preview** column showing the assembled prompt.
- **Screen 6 deleted entirely.** Stub comment left in markup. `TOTAL_SCREENS` stays at 21 (max ID); arrow-key navigation has fall-through.
- **Step counter** on the remaining wizard screens: "of 5" → "of 4".
- **Meta-bar step-btn 06** removed from Flow A nav.
- **"Add Topic" button** on Screen 4 now wired to `addTopic()` — clones the last topic block, clears values, opens it, scrolls into view.

### Storyboard stamp

v4.74 across the 6 portals.

---

## v4.73 — 19 May 2026 — Subject → Skill terminology sweep

Brady's JFT direction: *"Make sure everything is 'topics' and 'learning objectives' for a 'skill'."* The prototype previously used "Subject" as the top-level concept; aligned to "Skill" across the user-visible UI and the persona READMEs. Topics + Learning Objectives stay as the canonical sub-units.

### What changed (user-visible)

**`tenant_admin/index.html`** (the heaviest target — ~40 unique strings):

- Section + heading: "Your Subjects" → "Your Skills", "Subject Lifecycle & Archival" → "Skill Lifecycle & Archival"
- Wizard steps: "Create a new Subject" / "Step 1 of 5 · Subject Details" / "Subject summary" → Skill variants
- Buttons + CTAs: "New Subject" / "Configure another Subject" / "Deactivate Subject" / "Create subject" → Skill variants
- Form labels: "Subject code" / "Subject title" / "Subject-domain limits" → Skill variants
- Identifier copy: "Subject ID" → "Skill ID"; Breadcrumb hub "Subjects" → "Skills"
- Analytics filter label + select id: `rep-subject` → `rep-skill`, "All subjects" → "All Skills"
- Table headers + counters + aria-labels — all swept
- "Course Configuration" → "Skill Configuration"

**`super_admin/index.html`** (Cost-spike screen + audit feed):

- "Top consuming subjects" → "Top consuming Skills"
- `<th>Subject</th>` → `<th>Skill</th>`
- Rate-limit + cap + JSON keys + audit event `subject.deploy` → `skill.deploy`
- Form ID `f-subject` → `f-skill`

**Root `index.html`** (LRPS landing illustrative URL): `lti/launch?subject=e010` → `lti/launch?skill=e010`

### What is NOT changed

- **"Program Subject"** form-field label — refers to the WGU program/course field that HOSTS a Skill, not the SkillProof internal entity.
- **"course code"** literal — preserved for URL-generation consistency.
- **"data subject rights"** in the GDPR compliance row — GDPR legal term, not the SkillProof concept.

### Storyboard stamp

v4.73 across the 6 portals.

---

## v4.72 — 19 May 2026 — Per-school branding (4 WGU School logos + Switch School)

Brady's JFT note: *"Add the custom branding for each of the 4 schools."* Each WGU School (Technology / Business / Education / Leavitt Health) now has its own logo swapped into the navbar based on the active tenant context. The Switch School menu in the Tenant Admin user profile expands from 2 to all 4 schools.

### What changed

- **8 new logo assets** copied from OneDrive `WGU FY26 Design System / School Logos`:
  - `assets/school-tech-{light,dark}.png`
  - `assets/school-business-{light,dark}.png`
  - `assets/school-education-{light,dark}.png`
  - `assets/school-health-{light,dark}.png`
- **tenant_admin navbar logos** → default to `school-tech-*` with `data-school-logo` markers
- **student/ + instructor/ navbars** → swap to school-tech default
- **super_admin, help, root** → stay WGU corporate (cross-tenant / utility surfaces)
- **Switch School menu** expanded from 2 schools to all 4
- **`switchSchool(name)` JS extended** with school slug map, tenant ID map, `applySchoolLogos()` helper, `localStorage` persistence under key `skillproof-active-school`, on-load restore
- **Tenant identity card** wired with `data-tenant-name`, `data-tenant-id`, `data-tenant-scope` attributes

### Storyboard stamp

v4.72 across the 6 portals.

---

## v4.71 — 19 May 2026 — Delete scenario-catalog pages and contract-tracking docs

Brady's direction: this repo is for the SkillProof UI prototypes only. Supporting docs (scenario catalogs, contract trackers) are no longer maintained in the public repo. They live in Coda.io now.

### What was deleted

- The 2 scenario-catalog HTML pages (light + dark variants)
- `_contract_tracking/CONTRACT_TRACKER.md`
- `_contract_tracking/SCREEN_JUSTIFICATIONS.md`
- `_contract_tracking/D3A_BUILD_PLAN.md`
- `_contract_tracking/README.md`
- All in-repo references to the above (badges, surface table rows, repo-layout tree, per-persona README "Catalog" links)

Note: git history still contains these files at older commits. No history rewrite was performed.

### What stays

The 6 UI surfaces (4 persona portals + LRPS root + Help) are now the entire repo deliverable. All future phases ship UI changes only.

### Storyboard stamp

v4.71 across all 6 portals.

---

## v4.70 — 19 May 2026 — Site-wide UI polish (help icon, footer logo, sign-out, timing copy)

Phase B of the JFT meeting follow-up sweep. Fixes UI bugs that have accumulated since v4.62 plus a copy cleanup.

### What changed

- **Light-mode help icon visibility** — the navbar help icon (and theme-toggle icon) was visually faint in light mode because the icon glyph color was inheriting from a dark-navbar context. Added explicit `color: var(--color-deep-navy)` + `font-weight: 500` for `.btn-theme-toggle .material-icons-outlined` in light mode, with `#fff` override for dark mode. Applied across all portal navbars.
- **Removed the Sign out button** from the Tenant Admin user-profile menu — Brady's JFT note: *"I don't think we need the sign out button."* Authentication is LRPS / SSO-managed.
- **"No more timing things"** — removed arbitrary duration copy that wasn't tied to a contractual SLA:
  - Student onboarding "Takes about 5–8 minutes" hint on the diagnostic CTA
  - Student session-snapshot "Session duration · 14 min" row
  - Analytics-page Median 18 min · per session deferred to Phase K (v4.79)
  - All SLA references preserved as contractual.

### Storyboard stamp

v4.70 across all 6 portals.

---

## v4.69 — 19 May 2026 — URGENT: LRPS landing reframed to Sally (Student) for leadership preview

Brady is sharing the storyboard URL with leadership for EOD review. The LRPS landing root was framed as Alice's (Tenant Admin's) view since v4.65, since Alice's role per User Profile Catalog v1.3 explicitly includes managing LRPS deep links. For the leadership preview, the framing reverts to Sally (Student) so the entry point matches what an end-learner actually sees when launching the Coding Coach from their LMS course module.

### What changed

- **`index.html`** meta-bar persona line: `Persona: Alice (Tenant Admin · manages SkillProof LRPS links per User Profile Catalog v1.3)` → `Persona: Sally (Student · this is the LRPS view a learner sees when launching the Coding Coach from their LMS course module)`.
- **`README.md`** LRPS Landing section "Persona:" line reverted to a Sally-centered description.
- **Storyboard stamps** → v4.69 across all 6 portals.

### Why

Direct quote from Brady's JFT meeting notes: *"LRPS link directing to /tenant-admin — Put this back to the /student view so I can send to leadership tomorrow at EOD."*

---

## Pre-v4.69 history

Earlier release entries (v4.0 – v4.68) are no longer tracked in this file. This is a prototype repo and incremental change documentation isn't a priority. Full commit history with file-level diffs is in git (`git log --all`).
