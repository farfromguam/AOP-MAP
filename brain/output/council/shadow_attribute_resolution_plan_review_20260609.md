# Council plan-review — shadow-attribute resolution (ralph-loop plan) (2026-06-09)

**Reviewed:** `brain/tasks/09_editor_maturity/shadow_attribute_resolution.md` — the resolution plan that
sequences the 45-finding catalog ([[shadow_attributes_audit]]) into Path A loop slices (A1–A5) + a HELD
Path B (gold slice 6) + out-of-scope (events) + deferred-low. **Diff:** brain-only, uncommitted (HEAD
`4c168b2`). **Tier:** FULL SIX (the cut+migrate touches publish-zone served data + the bake; the plan runs
unattended in a loop). **Chair:** Steward.

## Verdicts

| Seat | Verdict | One-line |
|---|---|---|
| Quartermaster | **clear** | Extends the ONE crosswalk (`rebake_canonical.py` + `_schema.json`) + the ONE registry (A5 = R10/R12 spec fields), deletes runtime joins rather than adding parallel ones; Path B held + tagged, not duplicated; findings referenced by id, not re-listed; C1/C2/C6 greps hold. |
| Mason | **clear** (+ note, folded) | C5 binding propagated; no slice invites a reject/drop/throw; migration shape minimal/idiomatic. Note: A1 must write canonical `status` as a NEW derived field with the original key preserved — folded into the Standing-conditions binding + A1's acceptance (assert original key present). |
| Warden | **clear** | Brain-only diff, git gate untouched (HEAD `4c168b2`, no bump/commit/mutation); plan is sequencing-only (no slice executed); loop STOPS at the Path A/B boundary; Path B listed-and-deferred (no `- [ ]`, no un-hold). |
| Witness | **clear** (after andon → fold → re-review) | See below. |
| Scribe | **clear** (after andon → fold → re-review) | See below. |

## The two andons — folded and re-cleared

**Witness andon (verification design):** four defects — (1) A1's acceptance needed net-new join machinery
(the re-bake reads one file at a time, no cross-file join; sidecars not in `raw/`/`CONFIG`) dressed as a
config tweak; (2) A2/A3/A4 "left==right==map label" named no tool and could be satisfied by re-derivation
(the exact trap the seat exists to refute); (3) A5's acceptance was pure narration; (4) inverting the
re-bake's deliberate `name=None` will spawn map labels — undisclosed.
**Fold:** A1 gained a **BUILD** paragraph (join primitive + sidecars as deterministic `raw/` inputs, named
as net-new) + a **SIDE EFFECT** paragraph (label paint disclosed) + acceptance asserting a label-count
delta and the original key preserved; the Standing-conditions **Witness** bullet + A2/A3/A4 now mandate a
**live-DOM Playwright verifier on `mvp/scripts/playwright_base.py`** (rendered row text + right-panel Name
input *value* + map-label feature `name`, assert agreement, attach output) and **forbid closing by tracing
the read site**; A5 names the `editorPois` create path + a before/after DOM read, carving structural-only
sub-changes to grep + `node --check`. **Re-review: clear** — all four anchored to real artifacts.

**Scribe andon (record/traceability):** the plan cited self-minted slugs but the audit catalog had no id
field (bold-title prose) → "traceable by id" was false; and three findings were orphaned
(`event-overlay-two-divergent-resolvers`, `publish-kind-taxonomy-fork`, `hotspot-twin-id-collision-offvocab-sort`).
**Fold:** the audit card's FINDINGS catalog was **re-emitted id-tagged** (45 bullets each leading with a
backticked canonical `id`); the plan's `Closes:` lines now cite those ids **verbatim** (grep-resolves); a
**Coverage accounting** line (22 Path A + 20 Path B + 2 out-of-scope + 1 deferred-low = 45) was added and
all three orphans homed under named buckets. **Re-review: clear** — 5/5 spot-checked ids resolve; a
mechanical check confirms all 45 catalog ids appear in the plan exactly once.

## Steward synthesis

**Outcome: FULL SIX CLEAR.** The plan is accepted as **ralph-loop-ready**. It sequences every one of the 45
findings into exactly one home, each Path A slice carries a live-observation acceptance (no re-derivation)
and an `id`-traceable `Closes:` line, the controlled-vocab targets are bound additive (no limiting-code
drift), the loop stops cleanly at the Path A/B boundary, and gold slice 6 stays HELD for the user's pull.

**Gates remaining (the user's, not the council's):**
- **Commit-pause** — commit this brain-only plan + the id-tagged catalog (the cadence's commit gate).
- **Run the loop in a fresh session** — feed the verbatim loop prompt; this producing session is
  context-heavy and the council's own principle is a fresh executor + fresh verification.
- The `vNN` bump (one per Path A batch) + the commit of any slice's diff stay the user's git gate; the loop
  reports owed, never performs.
