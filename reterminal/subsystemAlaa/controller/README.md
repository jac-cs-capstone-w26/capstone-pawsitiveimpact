# Controller (A1)

Python backend for the reTerminal: device wrappers, FastAPI HTTP API, and `uv`-managed dependencies.

## Setup (developer machine or reTerminal)

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then from this directory:

```bash
uv sync
```

Dependencies are listed in `pyproject.toml`. Add or remove packages with:

```bash
uv add <package>
uv remove <package>
```

## Run the API

```bash
uv run fastapi dev app.py
```

Or production-style (good for Tailscale demos):

```bash
uv run fastapi run app.py --host 0.0.0.0 --port 8000
```

Open `http://<pi-ip>:8000/docs` to try **GET** `/read/{sensor_id}` and **PUT** `/control/{actuator_id}`.

### IDs

| Kind        | ID                   |
|------------|----------------------|
| Temperature | `sensor-temperature` |
| Humidity    | `sensor-humidity`    |
| LED         | `actuator-led`       |
| Fan         | `actuator-fan`       |

**PUT** body JSON: `{ "state": "on" }` or `{ "state": "off" }`.

### Environment (optional)

| Variable        | Default | Meaning        |
|----------------|---------|----------------|
| `LED_GPIO`     | `18`    | LED PWM pin    |
| `FAN_GPIO`     | `17`    | Relay pin      |
| `AHT20_I2C_BUS`| `4`     | Linux I2C bus # |
| `CORS_ORIGINS` | `*`     | Comma-separated origins for the dashboard |

## Test device scripts alone

```bash
uv run python led.py
uv run python fan.py
uv run python aht20.py
```

## I2C bus for AHT20

Add to `/boot/firmware/config.txt`, reboot, then confirm `i2cdetect -y 4` shows `38`:

```text
dtoverlay=i2c-gpio,bus=4,i2c_gpio_delay_us=1,i2c_gpio_sda=27,i2c_gpio_scl=26
```
