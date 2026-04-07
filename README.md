<div align="center">

# JFT SDP MVP Storyboard

**Interactive Prototype for the WGU Skills Development Platform**

[![Live Demo](https://img.shields.io/badge/Live_Demo-GitHub_Pages-0070F0?style=for-the-badge&logo=github)](https://brady-wgu.github.io/JFT_SDP_MVP/)
[![Presentation](https://img.shields.io/badge/Presentation-Light-001730?style=for-the-badge)](https://brady-wgu.github.io/JFT_SDP_MVP/presentation.html)
[![Presentation Dark](https://img.shields.io/badge/Presentation-Dark-0E2841?style=for-the-badge)](https://brady-wgu.github.io/JFT_SDP_MVP/presentation_dark.html)
[![Version](https://img.shields.io/badge/Version-3.1-46B1EF?style=for-the-badge)]()
[![Screens](https://img.shields.io/badge/Screens-34-001730?style=for-the-badge)]()
[![WCAG](https://img.shields.io/badge/WCAG_2.2-AA-2E7D32?style=for-the-badge)]()

---

*A medium-fidelity HTML storyboard for the JFT SDP Coding Coach MVP release.*
*Built on the [SDP Design System v1.2](https://github.com/openedx/paragon) (Paragon / Open edX) with WGU FY26 brand tokens.*

</div>

---

## Overview

This storyboard is the authoritative UX reference for the **JFT Skills Development Platform (SDP) MVP** -- an AI-powered Python coding coach for WGU students. It covers all four MVP user scenarios defined in the JFT SDP MVP Scenario Catalog v1.1.

The prototype consists of three self-contained HTML files that work offline, require no build step, and render in any modern browser. Developers should use them as the pixel-level reference for all student-facing screens in the MVP.

### Pages

| Page | URL | Description |
|:-----|:----|:------------|
| **Interactive Storyboard** | [`index.html`](https://brady-wgu.github.io/JFT_SDP_MVP/) | 34-screen interactive prototype with dark mode toggle, keyboard navigation, and admin bar |
| **Scenario Catalog (Light)** | [`presentation.html`](https://brady-wgu.github.io/JFT_SDP_MVP/presentation.html) | Scrollable presentation with all scenario steps, descriptions, and light-mode screenshots |
| **Scenario Catalog (Dark)** | [`presentation_dark.html`](https://brady-wgu.github.io/JFT_SDP_MVP/presentation_dark.html) | Same presentation with dark-mode screenshots |

---

## Scenarios

| Scenario | Flow | Screens | Description |
|:---------|:-----|:-------:|:------------|
| **SC-MVP-01** | Basic | 8 | First launch of the Coding Coach. New student with no Python knowledge completes diagnostic, views progress map, begins first coaching task, saves session. |
| **SC-MVP-02** | Advanced | 11 | Progressive coaching with targeted feedback. Student with partial Python knowledge completes diagnostic, receives foundational coaching, encounters incorrect answer with specific error feedback, verifies gap resolution, advances difficulty. |
| **SC-MVP-03** | Professional | 9 | Experienced developer fast-tracks through the coaching baseline. Diagnostic demonstrates mastery across all sub-sections. One verification task required for Functions & Modular Programming. |
| **SC-MVP-04** | Returning | 6 | Student returns after a multi-week break. Prior progress preserved. Re-assessment verifies retention before resuming coaching at prior difficulty level. |

---

## Design System

The storyboard implements the **SDP Design System v1.2**, which is a brand theme layer on top of [Paragon](https://github.com/openedx/paragon) (Open edX's open-source design system).

| Layer | Purpose |
|:------|:--------|
| **Paragon** | Component structure, accessibility, base CSS (`@openedx/paragon`) |
| **WGU Brand Tokens** | Color, typography, spacing overrides (`--pgn-*` CSS custom properties) |
| **SDP Product** | Page composition, content structure, learning interactions |

### Color Palette (WGU FY26 — Authoritative)

| Token | Hex | Role |
|:------|:----|:-----|
| Deep Navy | `#001730` | Primary dark background, navbar, headers |
| Dark Navy | `#002855` | Deep accent, logo gradient |
| Bright Blue | `#0070F0` | Primary actions, CTAs, links |
| Sky Blue | `#46B1EF` | Secondary blue, accents, progress |
| Ice Blue | `#EEF6F9` | Light surface backgrounds |
| Accent Red | `#C13232` | Error states, emphasis |
| Amber | `#FBAE40` | Warnings, section accents |

All colors aligned to the WGU FY26 Design System Specification. Where FY26 and SDP Figma tokens conflict, FY26 values take precedence.

### Typography

- **Headings:** Sora Bold (H1: 40px, H2: 32px, H3: 28px, H4: 24px, H5: 20px)
- **Body:** Lato Regular 16px / 1.5 line-height
- **Type scale:** 12, 14, 16, 18, 20, 24, 28, 32, 40, 48px (strict — no off-scale sizes)
- **Code blocks:** Lato 14px — light mode: white background with SDP palette syntax colors; dark mode: `#0d1117` background with high-contrast syntax colors

### Spacing

All padding, margin, and gap values follow an **8-point grid** (multiples of 8px: 8, 16, 24, 32, 40, 48px).

---

## Features

- **34 interactive screens** across 4 self-contained scenario flows
- **zyBooks landing page** — every scenario starts from a realistic zyBooks course page with "Coding Coach" CTA button positioned next to the Competencies section
- **Dark mode toggle** (moon/sun icon in header) with localStorage persistence
- **Light-mode-aware code blocks** — white background with SDP palette syntax highlighting in light mode, dark theme in dark mode
- **Official WGU Corporation logos** embedded as base64 PNG
- **Keyboard navigation** (arrow keys between screens)
- **Admin bar** with 3-column layout: scenario ID, description, numbered screen buttons
- **Presentation pages** — scrollable scenario catalogs with annotated screenshots (light and dark variants)
- **WCAG 2.2 AA** compliant: semantic HTML, ARIA landmarks, skip navigation, focus indicators, heading hierarchy, table scope attributes, contrast-verified color pairs, touch target sizing, responsive breakpoints
- **FY26 brand compliance** — all colors, typography, and spacing validated against the WGU FY26 Design System Specification
- **Fully offline** -- self-contained HTML files, no external dependencies beyond Google Fonts
- **Paragon-compatible CSS** class names (`--pgn-*` tokens, `.btn-primary`, `.pgn__card`, etc.)

---

## How to Use

### Online

| Page | URL |
|:-----|:----|
| Interactive Storyboard | **[brady-wgu.github.io/JFT_SDP_MVP](https://brady-wgu.github.io/JFT_SDP_MVP/)** |
| Scenario Catalog (Light) | **[brady-wgu.github.io/JFT_SDP_MVP/presentation.html](https://brady-wgu.github.io/JFT_SDP_MVP/presentation.html)** |
| Scenario Catalog (Dark) | **[brady-wgu.github.io/JFT_SDP_MVP/presentation_dark.html](https://brady-wgu.github.io/JFT_SDP_MVP/presentation_dark.html)** |

### Offline
Download the HTML files and the `screenshots/` / `screenshots_dark/` directories. Open in any browser. No server required.

### Navigation (Interactive Storyboard)
- Use the **admin bar** at the bottom to jump between scenarios and screens
- Use **arrow keys** (left/right) to step through screens sequentially
- Click interactive elements (Coding Coach CTA on zyBooks page, Submit buttons) to follow the scenario flow
- Toggle **dark mode** with the moon/sun icon in the upper-right corner

---

## Changelog (v3.1)

Changes applied since v3.0 (30 Mar 2026):

- **zyBooks landing page** — replaced mock WGU Student Portal LMS page (Screen 01) across all four scenarios with a realistic zyBooks course page; "Coding Coach" CTA button placed next to the Competencies section as the new entry point
- **Sequential screen numbering** — renumbered all 34 screens sequentially (01–08 SC-MVP-01, 09–19 SC-MVP-02, 20–28 SC-MVP-03, 29–34 SC-MVP-04); admin bar now displays true screen numbers instead of restarting at 01 per scenario
- **Presentation text sync** — fully aligned presentation.html and presentation_dark.html narrative text, Notes for JFT, and Document Control with the v1.2 Scenario Catalog (07 Apr 2026), including expanded LRPS descriptions per WGU LRPS team review
- **Design system audit** — 271 fixes across index.html and presentation.html covering WCAG 2.2 AA compliance, FY26 color palette alignment, typography scale enforcement, and 8-point spacing grid
- **FY26 palette reconciliation** — `--pgn-*` tokens updated from SDP Figma values to FY26 authoritative values (`#001730`, `#0070F0`, `#46B1EF`)
- **Light-mode code blocks** — white background with SDP palette syntax highlighting; dark mode retains `#0d1117` theme
- **Screen-footer removal** — removed "Screen X of Y" navigation bar from all screens
- **Heading focus outline fix** — suppressed `:focus-visible` outline on headings after programmatic focus
- **Dark mode presentation** — added `presentation_dark.html` with all 34 dark-theme screenshots
- **WCAG improvements** — skip navigation links, `<main>` landmark, contentinfo footer, heading hierarchy fixes, table scope attributes, aria-labels, focus indicators, responsive breakpoints, touch target sizing, contrast ratio fixes
- **Screenshot recapture** — all 68 screenshots (34 light + 34 dark) recaptured at 1440×900 with sequential filenames matching new screen IDs

---

## Source Documents

This storyboard is grounded in the following WGU Program Development deliverables:

| Document | Version | Date |
|:---------|:--------|:-----|
| JFT SDP MVP Scenario Catalog | v1.2 | 07 Apr 2026 |
| JFT SDP User Profiles | v1.2 | 30 Mar 2026 |
| SDP Design System Specification | v1.2 | 30 Mar 2026 |
| WGU FY26 Design System Specification | v1.0 | 25 Mar 2025 |

Upstream design system: [@openedx/paragon](https://github.com/openedx/paragon) (release-23.x, v23.19.1)

---

## For Developers

This storyboard is a **design reference**, not production code. When implementing:

1. Install Paragon: `npm install @openedx/paragon`
2. Apply WGU brand tokens via the brand package override mechanism
3. Use Paragon React components -- do not rebuild them
4. The CSS custom properties in this file (`--pgn-*`) map directly to the Paragon token schema
5. All screen layouts, component patterns, and interaction flows shown here are the implementation target

---

<div align="center">

**Western Governors University** | Program Development | JFT SDP

*WGU confidential/proprietary. Do not redistribute without authorization.*

</div>
