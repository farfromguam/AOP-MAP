# MVP Runbook

TL;DR:
- Use `./cwc` from the repo root for the default continuation check.
- QGIS and host tools should connect to `localhost:55432`, not `localhost:5432`.
- `5432` is still the Postgres port inside the Docker container.

#aop #mvp #spinup #postgis #qgis #cwc

-----

## Normal continuation check

From the repo root:

```bash
./cwc
```

This is non-mutating. It checks:
- Docker Compose status for `mvp-db-1`
- host Postgres connectivity to `localhost:55432`
- counts for the source, raw, core, and publish tables/views
- the current `website/data/publish.geojson` feature count by layer

Use this before assuming the MVP stack is broken.

## Database ports

The Docker service maps the database like this by default:

```text
host localhost:55432 -> container 5432
```

Why: local Postgres may already own `localhost:5432`. On 2026-05-20, that
happened on this machine. Docker showed `mvp-db-1` running, but host `psql` and
QGIS pointed at the local Postgres instance instead of the AOP container.

Expected QGIS connection:

```text
Host: localhost
Port: 55432
Database: aop_map
Username: aop
Password: aop
```

Expected host `psql` check:

```bash
psql postgresql://aop:aop@localhost:55432/aop_map -At -c "select current_user, current_database();"
```

Expected output:

```text
aop|aop_map
```

If a different host port is needed:

```bash
cd mvp
AOP_DB_HOST_PORT=55433 docker compose up -d
```

Then use the same port in QGIS, `psql`, and `PGPORT`.

## Port-collision symptoms

These are signs that the host is talking to the wrong Postgres:

- `psql postgresql://aop:aop@localhost:5432/aop_map` says role `aop` does not exist.
- QGIS connects but does not show the expected `raw`, `core`, `publish`, and `source_register` schemas.
- `docker compose ps` says `mvp-db-1` is running, but host tools see a different database.

Check listeners:

```bash
lsof -nP -iTCP:5432 -iTCP:55432 -sTCP:LISTEN
```

Expected current shape:

```text
local Postgres may listen on 127.0.0.1:5432
Docker should listen on *:55432
```

## Script behavior

Most MVP scripts run SQL through Docker Compose, so they use the container's
internal port and do not care about the host port:

```bash
cd mvp
./scripts/import_aop_parcel_boundary.sh
./scripts/run_validation_loop_smoke.sh
./scripts/export_publish_geojson.sh
```

`mvp/scripts/import_geojson.sh` uses a host connection because GDAL runs on the
host. It defaults to `PGPORT=55432` and can be overridden with:

```bash
PGHOST=localhost PGPORT=55433 PGUSER=aop PGDATABASE=aop_map PGPASSWORD=aop ./scripts/import_geojson.sh file.geojson schema.table
```

## Publish export check

Refresh the web export:

```bash
cd mvp
./scripts/export_publish_geojson.sh
```

Validate the file:

```bash
node -e 'const fs=require("fs"); const d=JSON.parse(fs.readFileSync("website/data/publish.geojson","utf8")); console.log(d.type, d.features.length);'
```

The current source-backed state should export one publishable
`park_boundaries` feature until real trails or trailheads are promoted.

## Static viewer

Serve the viewer from `website/`:

```bash
cd website
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000/
```

The viewer reads `website/data/publish.geojson`. If port `8000` is already in
use, pick another port and document the current one in
`brain/handoff/session_context.md`.

## Do not lose local data

Do not delete or reset `mvp/db-data` just because Postgres does not connect from
the host. First check the port mapping and run `./cwc`.

Only move, remove, or recreate `mvp/db-data` when intentionally rebuilding the
database and after recording what will be lost.
