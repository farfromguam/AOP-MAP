# Discovery Notes

Date: 2026-05-20

## Project spinup

The MVP stack is designed to start from `mvp/docker-compose.yml`.

Verified commands:

```bash
cd mvp
docker compose up -d
docker compose ps
```

The running database container is currently `mvp-db-1` on `localhost:5432`.

## Current documented spinup sources

- `README.md`
- `mvp/README.md`
- `brain/flows/cwc.md`

Both root `README.md` and `mvp/README.md` include PostGIS startup instructions and PostGIS connection details.

## Issues discovered

- There is no executable `./cwc` script in the repository root.
- The `.vscode/tasks.json` file exists but is currently empty.
- The `brain/flows/cwc.md` flow references a `~~cwc` invocation and the task label "CWC: Continue MVP work with context," but the working script is missing.

## Relevant current status

- The database container is up and mapped to `localhost:5432`.
- The MVP environment startup appears to have been attempted successfully in previous session commands.
- No `cwc` entrypoint is available to satisfy the VS Code task or the handoff flow semantics.

## Recommended next action

1. Restore or add the missing `cwc` script at repository root, or update the task and docs to point to the correct handoff entrypoint.
2. Keep this note until the missing script/task mismatch is resolved.
3. Continue by verifying `website/data/publish.geojson` against the `publish` views and the `brain/handoff/session_context.md` guidance.
