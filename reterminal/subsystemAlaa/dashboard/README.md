# Dashboard (A1)

TypeScript + React (Vite) UI for the controller API. Use **bun** to install and run.

## Setup

From this directory:

```bash
bun install
```

If `bun install` ever leaves `react-dom` missing on your machine, delete `node_modules` and run `bun install` again (or run `bun run build` after a fresh install).

## Run (development)

1. Start the FastAPI backend (see `../controller/README.md`).
2. Start the dashboard:

```bash
bun run dev
```

By default the UI calls `http://127.0.0.1:8000`. On another machine or over Tailscale, set:

```bash
# .env.local (Vite)
VITE_API_BASE=http://100.x.y.z:8000
```

## Build

```bash
bun run build
bun run preview
```

## Features

- Toggles for **LED** and **Fan** → `PUT /control/{actuator_id}` with `{ "state": "on"|"off" }`
- Live **temperature** and **humidity** text → `GET /read/{sensor_id}` every ~1.5s
- **Line chart** (Recharts) fed from the same polling loop
