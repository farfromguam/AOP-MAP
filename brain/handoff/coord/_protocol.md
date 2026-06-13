# Coordination board — live multi-session claims

TL;DR: When more than one session is live at once, each gets its own file in this folder and posts what it is touching. Read the folder before you claim. Advisory, not a lock. Drains to the handoff on finish.

#coord #handoff #concurrency #sessions

-----

## Why this exists

`handoff/session_context.md` is one file written by one session at a time — safe *because* sessions are assumed serial (A ends → writes → B starts). Two sessions live at once both appending to it race, and clobber each other. This board solves concurrency a different way: **one file per session.** Single writer each → no write race, no merge conflict. The "board" is just the folder; the at-a-glance view is reading it.

This is the CONCURRENCY axis. The TIME axis (settled history) stays in the handoff; the DEPTH axis (one goal across windows) is the card cursor. See `ai_rules/coordination_axes.md` for the whole frame.

## The protocol

1. **Claim.** Starting live work while another session may be running? Copy `_template.md` to `<session-slug>.md`. You own that file; nobody else writes it.
2. **Read before you claim.** Read the other files here first. If a session already claims your area or card, take something else or coordinate through the user.
3. **Keep it current.** Update your file as you go — status, and what you are touching.
4. **Drain on finish.** Write the durable note to `handoff/session_context.md` (and the card), then set your file to `status: done` with a `next:` pointer, or delete it. The board holds *live* state; the handoff holds *settled* history. Nothing here is permanent until it lands in the handoff.

## Honest limits

- **Advisory, not a lock.** There is no atomic claim here — two sessions *could* grab the same area in the same instant. At this scale (a handful of sessions) read-before-claim plus convention is enough. Do not build a mutex; it would be brittle for no payoff.
- **Visible, not a doorbell.** A finished session leaving a `next:` does not wake anyone. A waiting session only follows up if it is polling (a `/loop`) or the user relays. The file cannot ring a bell.

See also: `_template.md` (the per-session file), `ai_rules/coordination_axes.md` (the three-axis frame), `flows/cwc.md` (checks here before claiming a card).
