# Help & Resources — shared surface

[← Back to root README](../README.md) · [Live surface](https://brady-wgu.github.io/SkillProof/help/)

## What this is

A shared support surface for SkillProof. Single page, two sections:

1. **Submit a support request** — Zendesk-styled form (name, email, request type, subject, description, attachments). Anchor `id="submit-request"` is the link target used by every portal's Help button.
2. **Help docs** — flat list of 15 documentation entries grouped by persona role tag (Student / Instructor / School Admin / Super Admin / All admin roles).

Closes Appendix A §16.4 #9.14 (Self-service support portal).

## Persona

Shared. Reachable from every portal's navbar Help link, and from the root portal selector.

## Scope

- Zendesk-style ticket submission with 5 request types (Permission, LRPS reissue/revoke, Bug, Feature, Other).
- Flat documentation list. No search, no video, no card grid.
- Form is faux-functional: `onsubmit` shows a success toast and resets the fields. Production wires this to a real Zendesk endpoint.
- All docs-list `href="#"` are stubs. Production builds out the actual article pages.

## SOW references

§16.4 #9.14 (Self-service support portal); supporting: §9.1 (Support Plan), §9.4 (Support channels), §9.11 (Comprehensive documentation and user training materials).

**Not covered by this surface in v1.2:** §16.4 #9.15 (Video training resources). The earlier video gallery was removed in the v4.81 rewrite; videos are deferred per WGU direction (2026-05-21).

## Files

- [`index.html`](index.html) — single-page surface (navbar + Zendesk form + sidebar + docs list + footer)
- `screenshots/` — light-theme PNG (capture via `capture_screens.py`)
- `screenshots_dark/` — dark-theme PNG (same)

## Components

- **`.support-grid`** — 2-column layout (form left, "Suggested articles" sidebar right); collapses to 1 column under 880px.
- **`.support-form-card`** — Zendesk-style form container with name / email / request type / subject / description / attachments.
- **`.sidebar-card`** — "Suggested articles" rail with 4 jump links anchored to `#docs`.
- **`.docs-list`** — bordered flat list; each row is a docs-title + role chip + chevron wrapped in a stub `<a href="#">`.

## Notes

- Container max-width 1080px (slightly narrower than the 1192px admin portals — by design for readability on a help/docs page).
- Theme toggle persists via `localStorage` (`skillproof-theme` key).
- All copy is illustrative; production article titles and ticket form copy come from the WGU/JFT content library.

## Future enhancements (post-v4.115)

- Form submit is a stub — production wires to the Zendesk API.
- Docs-list articles are `href="#"` placeholders — production builds the article pages.
- No search. If the docs list grows past one screen, consider a search bar or per-role filter.
