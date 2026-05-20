# App Spinup Discovery

Date: 2026-05-20

## Summary

This document captures the discovery findings for the AOP MAP MVP app spinup and current workspace status.

## Spinup path

The MVP stack launches from the `mvp` directory using Docker Compose.

Verified startup commands:

```bash
cd mvp
docker compose up -d
docker compose ps
```

The database container is available as `mvp-db-1` and listens on `localhost:5432`.

## Documented startup resources

Existing documentation includes:

- `README.md`
- `mvp/README.md`
- `brain/flows/cwc.md`

These files describe Docker/PostGIS startup, QGIS connection settings, and the CWC flow.

## Discovered issues

- The repository does not contain a `./cwc` executable entrypoint at the root.
- `.vscode/tasks.json` exists but is currently empty.
- `brain/flows/cwc.md` references the `~~cwc` flow and the task "CWC: Continue MVP work with context," but no runnable script exists to satisfy that flow.

## Current status

- Docker and the MVP PostGIS database have been started successfully.
- The container `mvp-db-1` is running and mapped to `localhost:5432`.
- The app viewer data export path `website/data/publish.geojson` is present in the workspace.

## Recommended next steps

1. Add or restore the missing `cwc` script at the repository root, or update the task/docs to point to the actual spinup command.
2. Verify the `publish` views in the database and refresh `website/data/publish.geojson` from the live views.
3. Use `brain/handoff/session_context.md` and `brain/northstar/validation_loop.md` as the current session guidance.
