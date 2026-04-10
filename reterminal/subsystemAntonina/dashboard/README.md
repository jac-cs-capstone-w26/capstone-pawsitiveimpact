# Dashboard (React + TypeScript + Bun)

Prototype dashboard for controlling actuators and visualizing live AHT20 readings.

## Requirements

- Bun installed
- Backend controller running from `a1/controller`

## Install

```bash
bun install
```

## Run (dev)

Make sure you are in right directory: a1/dashboard

```bash
bun run dev
```

Default dashboard URL: `http://127.0.0.1:5173`

## Configure API base URL

The frontend uses `VITE_API_BASE_URL` (defaults to `http://127.0.0.1:8000`).

Create `.env` if needed:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Features

- Toggle fan (`fan-1`) on/off via `PUT /control/fan-1?state=...`
- Toggle LED (`led-1`) on/off via `PUT /control/led-1?state=...`
- Poll temperature (`temperature-1`) and humidity (`humidity-1`) every 2 seconds
- Render a live line chart over time

## Build

```bash
bun run build
```
