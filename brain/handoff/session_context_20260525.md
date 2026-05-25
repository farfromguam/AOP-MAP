# Session Context: Left-rail manilla-tab design

Date: 20260525

This is the CWC dump for the 2026-05-25 left-rail collapse design session.
Design exploration only — no `website/index.html` changes. The artifact still
in progress is the build card at
`brain/tasks/03_event_app/left_rail_collapse_tabs.md`.

## Where we are

Repo: `/Users/christopherfryman/Documents/code/AOP MAP`. Sprint 03.

Five HTML mockup variants of a "manilla tab drawer" for the left rail are
checked in under `website/leftrail_v{1..5}_*.html` with an iframe comparison
page at `website/leftrail_compare.html`. The locked behavior is the unified
drawer with per-card icon toggle, upward absorption, the E1 downward
absorption for the bottom card, and the closed-icon-as-island visual. The
five variants differ only in visual treatment — classic manilla folder, flat
modern, color-coded cabinet, dynamic / motion-led, and a hybrid (v1's
content-aware JS layout + v2's flat skin). Variant pick is the open decision.

The current viewer (`website/index.html`) still uses the pre-collapse vertical
stack of three independent cream cards (`.search-shell`, `.hot-control`,
`.calendar-card`). The collapse work is structural; the Rock Warblers content
rebrand that landed earlier on 2026-05-25 (see `left_sidebar_content_audit.md`)
is content. They overlap on the same `#calendarCard` DOM but don't conflict.

## Work log

**Round 1 — conceptual brainstorm.** Four parallel agents produced ASCII
mockups of distinct collapse models: edge-dock (cards slide off, 44px icon
rail pinned to viewport edge), header-strip accordion (cards shrink in place),
map-room metaphor (binder / dog-ear paper artifact), power-user / activity-bar
(VS-Code-style dense). User picked the edge-dock collapsed shape as the
closest match. The round-one comparison page survives at
`website/leftrail_collapse_mockups.html` as reference.

**Iteration with the user.** Several rounds of ASCII back-and-forth pinned
down the behavior:

1. First swing: per-card 44px icon to the left, each pill independent (the
   `website/leftrail_edge_dock_mockup.html` intermediate).
2. User refinement: the icon and card should be ONE element horizontally, not
   `[icon][card]` floating side by side. Icons should NOT vertically connect
   between rows.
3. Implementation: tighten the row layout to a single shell per row, no gap.
4. User refinement: "go back to the last thought — think dynamic manilla tab
   group on the left." Switched to a unified-drawer model with the
   icon-column-as-spine and the island-cut-out + scoot-up rules.
5. The bottom-card edge case (E1 down-absorb vs E2 L-shape) was resolved to
   E1 — symmetric absorption keeps the drawer rectangular.

**Round 2 — visual variant agents.** Four parallel agents built clickable
HTML mockups, each on the locked behavior with a distinct visual direction:
classic manilla (v1), flat modern (v2), color-coded cabinet (v3), dynamic
motion-led (v4). A fifth variant (v5) was added by user request — v1's
content-aware JS layout engine wearing v2's flat skin. All five carry the
full 8-state behavior matrix (any combination of open/closed per card).

## Files touched / created

```
website/leftrail_v1_classic.html             new
website/leftrail_v2_modern.html              new
website/leftrail_v3_cabinet.html             new
website/leftrail_v4_dynamic.html             new
website/leftrail_v5_hybrid.html              new
website/leftrail_compare.html                new (iframe index of v1-v5)
website/leftrail_edge_dock_mockup.html       new (intermediate)
website/leftrail_collapse_mockups.html       new (round-1 ASCII review)
brain/tasks/03_event_app/left_rail_collapse_tabs.md   new (build card)
brain/handoff/session_context_20260525.md    new (this file)
brain/handoff/session_context.md             updated (pointer + archive index)
brain/tasks/03_event_app/_readme.md          updated (lists the new card)
```

Nothing in `website/index.html`, `mvp/`, or `brain/research/viewer.md`.

## Verification

Design-only. No verifier runs. Each mockup was clicked through the 8
open/closed permutations and the absorption + divider rules confirmed against
the locked behavior. Both the comparison page (`leftrail_compare.html`) and
each variant render against the existing `python3 -m http.server 8000` dev
server.

## Open

- **Variant pick.** v1 / v2 / v3 / v4 / v5. Hybrid v5 is the most likely
  pickup; not committed.
- **Integration into `website/index.html`.** Replaces the three current cream
  shells with the unified drawer; the inside chrome of each card stays
  intact. ID-stability rule from `left_panel_context_tabs.md` carries over —
  verifiers depend on `#searchInput`, `#hotButton`, `#hotTrailButton`,
  `#calendarToggle`, `#calendarBody`.
- **Mobile story (≤760px).** Drawer needs a per-card-still-works adaptation
  inside the existing full-width left-controls override at
  `website/index.html:277`.
- **"Active" vs "open" model.** v2 and v5 promote one open segment to
  "active" with a rust accent. Drop this if the second click target is one
  subtlety too many.
- **Persistence.** One localStorage key per card open/closed state, matching
  the existing `aop_calendar_collapsed_v1` pattern.

## Pickup

Open `website/leftrail_compare.html` against the running viewer server
(`cd website && python3 -m http.server 8000` → `http://localhost:8000/`),
click through the variants, decide one. Then re-open
`brain/tasks/03_event_app/left_rail_collapse_tabs.md` and start the
integration lane.
