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

The database container is available as `mvp-db-1` and is exposed on
`localhost:55432` by default. It still listens on `5432` inside the container.

## Documented startup resources

Existing documentation includes:

- `README.md`
- `mvp/README.md`
- `brain/spinup/mvp_runbook.md`
- `brain/flows/cwc.md`

These files describe Docker/PostGIS startup, QGIS connection settings, the CWC
flow, and the durable troubleshooting path.

## Discovered issues

- `brain/flows/cwc.md` references the `~~cwc` conversation flow. A root
  `./cwc` helper and VS Code task now exist for a non-mutating local continuation
  check, but the brain flow remains the source of truth.

## Current status

- Docker and the MVP PostGIS database have been started successfully.
- The container `mvp-db-1` is running and mapped to `localhost:55432` by default.

## 2026-05-20 CWC update

Local Postgres can already be listening on `localhost:5432`, which makes QGIS
or host `psql` connections hit the wrong database even while Docker shows the
MVP container running. The Compose host port now defaults to `55432`; use
`AOP_DB_HOST_PORT` to override it.

The durable runbook for this is `brain/spinup/mvp_runbook.md`. Check it before
changing Docker volumes or assuming the database is corrupt.
- The app viewer data export path `website/data/publish.geojson` is present in the workspace.

## Recommended next steps

1. Run `./cwc` from the repo root when a local continuation check is useful.
2. Verify the `publish` views in the database and refresh `website/data/publish.geojson` from the live views.
3. Use `brain/handoff/session_context.md` and `brain/northstar/validation_loop.md` as the current session guidance.
