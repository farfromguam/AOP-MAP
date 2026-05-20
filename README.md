# AOP MAP MVP

This repository contains the Adventure Off Road Park map brain and a minimal MVP scaffold for the first PostGIS/QGIS/MapLibre build.

## Current progress

- [X] Scaffold PostGIS container and init SQL
- [X] Add static MapLibre viewer skeleton
- [X] Add root README and website README
- [ ] Confirm Docker container startup
- [ ] Connect QGIS and verify schema

## Spinup instructions

### 1. Start Docker Desktop

Make sure Docker is installed and the Docker daemon is running.
On macOS this typically means opening Docker Desktop and waiting for it to become ready.

### 2. Start the PostGIS database

From the repository root:

```bash
cd mvp
docker compose up -d
```

This will launch a PostGIS container with the following settings:
- Host: `localhost`
- Port: `5432`
- Database: `aop_map`
- Username: `aop`
- Password: `aop`

### 3. Verify the container

Run:

```bash
docker compose ps
```

If the container is running, you should see the `db` service listed.

### 4. Connect QGIS

In QGIS, create a new PostGIS connection using:
- Host: `localhost`
- Port: `5432`
- Database: `aop_map`
- Username: `aop`
- Password: `aop`

Then inspect these schemas:
- `source_register`
- `core`
- `publish`

### 5. Preview the viewer

Open `website/index.html` in a browser, or use a simple local web server from the repository root:

```bash
cd website
python3 -m http.server 8000
```

Then browse to `http://localhost:8000`.

## Troubleshooting

- If `docker compose up -d` fails with `Cannot connect to the Docker daemon`, the Docker daemon is not running.
- On macOS, open Docker Desktop and wait until it indicates it is ready.
- If the compose service fails to start, run:

```bash
cd mvp
docker compose logs db
```

- If the database port is already in use, either stop the conflicting service or edit `mvp/docker-compose.yml`.

## What is included

- `mvp/docker-compose.yml` — PostGIS container definition
- `mvp/init_db.sql` — initial database schema for sources, park boundaries, parcels, trails, observations, hazards, trailheads, and publish views
- `website/index.html` — static MapLibre viewer skeleton
- `website/data/publish.geojson` — placeholder publish layer data
