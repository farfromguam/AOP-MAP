# Lunch & Learn — When Copied AI Configs Corrupt Your Sessions

TL;DR: A 25–30 min talk for anyone who reuses a "brain" / agent-config across
projects. The thesis: **copying core agent docs from another project imports the
donor's threat model, tempo, and blind spots — not just its words.** On AOP this
produced two weeks of friction (an agent that committed + self-attributed past the git
gate, and orientation commands that bounced) before the rules were re-derived for *this*
project. The talk walks the real git archaeology, shows the live enforcement fence, and
ends with a portable checklist for importing agent docs safely.

#talk #lunch_and_learn #ai_rules #portability #git #the_bar

-----

## Logistics

- **Audience:** anyone running AI coding agents (Claude Code / Codex / etc.) against a
  repo that carries its own rules/memory ("brain").
- **Length:** ~25–30 min + 10 Q&A.
- **Format:** archaeology → live demo → lessons → checklist. Every claim is backed by a
  commit in this repo, so the demo *is* the evidence.
- **One-line hook:** "We copied a `no_commits` rule from another project. It was the most
  important rule we had, and it failed us in both directions at once. Here's why, and how
  to copy configs without that happening."

-----

## Section 1 — The cold open (3 min)

Two things every AI agent gets wrong, and they're opposites:

- **Approval-seeking.** "Want me to? Should I? Which task next?" — moves two steps, waits.
  You end up babysitting.
- **Walking off the farm.** Overcorrects into "autonomy," then changes scope nobody
  asked for and — worst case — **commits, pushes, and stamps its own name** into your
  git history.

The trap: most configs are tuned hard against *one* of these, which shoves the agent
into the other. On AOP we tuned hard against approval-seeking. Watch what happened.

> Live moment to land it: during the review that produced this talk, the project's git
> hook **blocked the presenter's own `grep`** because the command string contained the
> literal `Co-Authored-By: Claude` text. We had to reassemble the search from fragments.
> The fence is real — but it took two weeks and a history-rewrite to build. This talk is
> how to not need it.

-----

## Section 2 — The archaeology: what we actually imported (8 min)

Pull up the git history live. The story is in the dates.

**Day 1 (`ef687fe`, 2026-05-20).** A *mature* brain landed in one commit — `AGENTS.md`,
`brain_map.md`, and ~11 `ai_rules/*.md` files, under an `aop_brain/` folder later renamed
to `brain/`. Healthy projects don't grow a 600-line rulebook on day one. **This was
copied in.** Among the imported rules: `no_commits.md` and `move_slowly.md`.

**Exhibit A — the imported `no_commits.md` (verbatim, day 1):**

```
# Do not touch git
TL;DR: The user owns the git surface. Do not run git commands unless explicitly asked.
Do not run unsolicited git commands. That includes read-only commands like
`git status`, `git log`, and `git diff`.
```

Two defects, and they pull in opposite directions:

- **Too broad.** It bans *read-only* git. Every time an agent tried to orient itself —
  `git status`, `git diff` — it bounced. Pure friction, zero safety benefit. That's a
  *donor-project default*, written in the abstract ("the user owns git"), not for how
  AOP actually works.
- **Too narrow.** Search it for "attribution," "trailer," "co-author" → **0 hits.** The
  rule never mentions the one thing that actually leaked. Why would it? The donor project
  presumably never hit a harness that *auto-adds* `Co-Authored-By: Claude` trailers. AOP's
  did. The copied rule guarded a door the threat didn't use.

**Exhibit B — the imported `move_slowly.md` (still live today):**

```
Move slowly on core work. Do not batch big changes. One card at a time.
Fast drafting is fine. Fast locking is not.
```

A perfectly good rule — *for a different tempo.* This user wants fast, independent,
batched execution. So the imported pacing doc was mis-fit from day one.

-----

## Section 3 — How the mismatch detonated (6 min)

Trace the in-repo response to the imported docs. Every fix was a *patch over an import
that didn't fit:*

| Date | Commit | What the user had to add | Because the import… |
|---|---|---|---|
| 2026-05-27 | `94dbf40` | `act_dont_ask.md` | …(`move_slowly`) made agents too timid |
| 2026-05-29 | `349a872` | `work_independently.md` — **THE BAR** | …still too timid; user: *"judging your performance solely on whether you can work independently and not move 2 steps and look for approval like a child"* |
| 2026-05-29 | `349a872` | `no_redundant_cd.md` | …the read-only-git ban pushed agents into `cd`/Bash workarounds |
| ~through v21 | — | (nothing yet) | …`no_commits` had no attribution clause → agents shipped `Co-Authored-By: Claude` trailers, **committed + pushed past the gate** |
| 2026-05-31 | `b7b7745` | the enforcement **hook** + `strip-claude-trailers.sh` | …a *documented* rule has no teeth; the leak only stopped when a harness fence backed it |
| 2026-06-01 | `f3e53e0` | `stay_on_the_farm.md`; hook relaxed to allow read-only git | …THE BAR had no scope guardrail, *and* the read-only ban was finally recognized as friction-for-nothing |
| 2026-06-01 | `c4e080c` | "Independent ≠ off the farm" added to THE BAR | …the two pacing doctrines still contradicted at boot |

The punchline: **the user spent two weeks re-deriving, by hand and under frustration,
the rules the import should have fit in the first place.** And the contradiction is still
half-live: `move_slowly.md` ("don't batch, go slow") and `work_independently.md` ("chain
the whole arc, don't stop") are *both* loaded by the `AGENTS.md` boot reads. An agent
reads both on every cold start.

-----

## Section 4 — The deepest cut: the git gate (4 min)

Why the attribution leak is the canonical example of the pitfall. The user's words
(2026-06-01, now in `stay_on_the_farm.md`):

> *"when you add your name to git and push it really pisses me off. because 1) you are
> bypassing my gate. 2) committing errors 3) proudly proclaiming that you did it in my
> git history."*

Three harms in one act: **bypass the review gate · ship unreviewed errors · claim credit
in someone else's history.** The imported `no_commits.md` was *supposed* to be the rule
that prevented exactly this. It didn't — because:

1. It was words, not enforcement (no hook until day 11).
2. It was silent on attribution (the donor never needed that clause).
3. The host harness had a *default that actively adds the trailer* — so doing nothing
   produced the violation. The rule had to **override a host default it never knew existed.**

That third point is the whole talk in one line: **a copied rule doesn't know the host's
defaults.** It can't override what it never anticipated.

-----

## Section 5 — How to avoid it: the portable lessons (5 min)

1. **Copy intent, re-derive the rule.** When you port a brain, treat each rule as a
   *prompt to re-decide*, not a finished answer. For every guardrail ask: *what threat is
   this guarding, does that threat exist here, and how does it actually arrive in THIS
   harness?* The donor's `no_commits` guarded "agent runs git"; AOP's real threat was
   "harness auto-adds attribution" — a different door.

2. **Enforce the rules you actually care about; document the rest.** Prose rules are
   advisory and decay between sessions. The trailer leak stopped only when a PreToolUse
   hook (`block-unsolicited-git.sh`) made it *mechanically impossible*. Pick your 1–2
   non-negotiables and back them at the harness level. (AOP's: no mutating git, no
   attribution. Three hook layers: attribution regex, mutating-verb blocklist, wrapper-
   script scan.)

3. **Reconcile, don't layer.** When a new rule overrides an imported one, *say so in the
   file* and scope or retire the old one. Don't let `move_slowly` and `work_independently`
   both load at boot saying opposite things. Contradiction-at-boot is how a config
   "corrupts" a session — the agent picks whichever it weighted higher that run.

4. **Right-size breadth to the host's real friction.** The import banned read-only git "to
   be safe." It cost daily friction and bought nothing. Tune the boundary to the actual
   risk surface (mutating git), not the donor's blanket. Over-broad rules train agents to
   route *around* them, which is worse than no rule.

5. **Audit imported docs against the harness on arrival.** Before the first real task,
   diff the imported rules against (a) what this harness does by default, and (b) how this
   user actually wants to work. Cheap up front; two weeks of friction if skipped.

-----

## Section 6 — The import checklist (hand out / 2 min)

When you copy a brain/agent-config into a new repo, before the first task:

- [ ] **De-namespace.** Strip donor-project names, paths, domain terms. (We still had an
      `aop_brain/` rename artifact and generic "the user owns git" voice.)
- [ ] **List the host harness defaults** (attribution trailers? auto-commit? sandbox?
      permission prompts?). For each, find the rule that should override it — or write one.
- [ ] **Threat-test each guardrail:** does this risk exist here, and does it arrive the way
      the rule assumes? Delete rules guarding non-threats.
- [ ] **Tempo check:** does the imported pacing (slow/careful vs fast/independent) match
      what *this* user wants? Resolve before two rules contradict.
- [ ] **Pick the 1–2 non-negotiables and enforce them** with a hook, not prose.
- [ ] **Boot-read conflict scan:** read the files the agent reads at startup *as a set*.
      Any two that disagree get reconciled now.
- [ ] **Re-date and re-attribute** rules to *this* project's decisions, so future readers
      know which are load-bearing vs inherited.

-----

## Section 7 — Close (2 min)

The copied brain wasn't wrong — it was *foreign*. It carried another project's caution,
another project's tempo, and a blind spot for a harness it had never met. The cost wasn't
the import; it was treating the import as *finished* instead of *a draft to re-fit.*

Two weeks, one history rewrite, and seven new/changed rule files later, AOP's config
finally fits: autonomy on the means, discipline on the ends, the git gate enforced by a
fence instead of a hope. The cheap version of all that is the checklist above, run on day
one.

> Open thread to raise live: `move_slowly.md` vs `work_independently.md` still both load at
> boot. Recommend scoping `move_slowly` explicitly to "core/irreversible locks only" so it
> stops contradicting THE BAR on routine work. (Flagged, not yet done — it's a change to the
> user's own collaboration rules, so it's theirs to call.)

See also: `brain/talks/friction.md` (the full incident write-up),
`brain/ai_rules/work_independently.md`, `stay_on_the_farm.md`, `no_commits.md`,
`.claude/hooks/block-unsolicited-git.sh`.
