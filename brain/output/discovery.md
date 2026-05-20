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

The running database container is currently `mvp-db-1` and should be exposed on
`localhost:55432` by default.

## Current documented spinup sources

- `README.md`
- `mvp/README.md`
- `brain/flows/cwc.md`

Both root `README.md` and `mvp/README.md` include PostGIS startup instructions and PostGIS connection details.

## Issues discovered

- The `brain/flows/cwc.md` flow references a `~~cwc` invocation and the task label
  "CWC: Continue MVP work with context." A root `./cwc` helper and VS Code task
  now exist for a non-mutating local continuation check.

## Relevant current status

- The database container is up and should be mapped to `localhost:55432`.
- The MVP environment startup appears to have been attempted successfully in previous session commands.
- The root `./cwc` helper is available for a non-mutating continuation check.

## Recommended next action

1. Run `./cwc` from the repo root when a local continuation check is useful.
2. Keep this note until the task/helper shape has been validated in normal use.
3. Continue by verifying `website/data/publish.geojson` against the `publish` views and the `brain/handoff/session_context.md` guidance.
