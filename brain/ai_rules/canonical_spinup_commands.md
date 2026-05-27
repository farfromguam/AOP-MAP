# Canonical spinup commands

TL;DR: The AOP MAP spinup commands and ports are already pinned. Do not invent variants. Do not ask the user to pick a port. Do not drift.

#ai_rules #spinup #ports

-----

The durable spec lives in `brain/spinup/mvp_runbook.md` and the repo `README.md`. This rule exists because the assistant kept giving slightly different commands and changing ports between sessions, which made the system impossible for the user to diagnose.

## The four commands

```bash
# Database (PostGIS in Docker) — only when QGIS, imports, or DB queries are needed
cd mvp && docker compose up -d

# User's manual viewer — port 8000 is reserved for the user
cd website && python3 -m http.server 8000
# → http://localhost:8000/

# Assistant's Playwright / automation viewer — port 8001 is the assistant's lane
cd website && python3 -m http.server 8001
# → http://localhost:8001/

# Non-mutating continuation check from repo root
./cwc
```

## Port discipline

- `8000` belongs to the user. The assistant does not start a server on it, does not test against it, and does not suggest changing it.
- `8001` is the assistant's. Playwright verifiers in `mvp/scripts/playwright_verify_*.py` default to `http://localhost:8001/` via `playwright_base.py`. If `8001` is busy, identify the listener with `lsof -nP -iTCP:8001 -sTCP:LISTEN`, kill it only if it is a recognized stale viewer/test server, and reuse `8001`. Do not drift to `8002`, `8010`, or any other port.
- `55432` is the host port for the PostGIS container. Override only through `AOP_DB_HOST_PORT`, never by editing the compose file ad hoc.

## How to apply

- When the user asks how to run the app, give the four commands above verbatim. Do not paraphrase, reorder, or add alternatives.
- Do not ask "which port should I use?" The rule answers that.
- When something deviates (e.g. a task card says to use a different port for a one-off test), call the deviation out explicitly and link back to this file.

See also: `brain/spinup/mvp_runbook.md` (full runbook), `cwc` (root helper), `verify_by_observation.md` (why observing the running system matters).
