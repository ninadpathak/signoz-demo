# SigNoz Demo: Order Service

This repository contains a small Flask “order service” that emits dummy telemetry so you can inspect traces and metrics inside [SigNoz](https://signoz.io/). The service does **not** talk to a real database or inventory system. It generates random data that is suitable for dashboards. The instructions below cover streaming telemetry to SigNoz Cloud.

## Prerequisites

- macOS/Linux with **Python 3.8+** (tested on Python 3.13)
- Git
- An existing SigNoz Cloud account
- SigNoz Cloud ingestion key

## 1. Clone the Repository

```bash
git clone <your-github-repo-url> signoz-demo
cd signoz-demo
```

## 2. Set Up and Install Python Dependencies

Create an isolated environment and install the packages required by the order service:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# install auto-instrumentation entry points
opentelemetry-bootstrap --action=install
```

The requirements include:
- `flask` for the API
- `opentelemetry-distro` & `opentelemetry-exporter-otlp` for tracing/metrics
- `opentelemetry-instrumentation-flask` so Flask gets hooked automatically

## 3. Configure SigNoz Cloud Environment Variables

In the same terminal with the virtual environment activated, export the variables that tell OpenTelemetry where to send data:

```bash
export OTEL_RESOURCE_ATTRIBUTES=service.name=order-service
export OTEL_EXPORTER_OTLP_ENDPOINT=https://ingest.<region>.signoz.cloud:443
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc             # use http/protobuf for the HTTP exporter
export OTEL_EXPORTER_OTLP_HEADERS="signoz-ingestion-key=<your-ingestion-key>"
```

Replace each placeholder as follows:
- `<region>` is the region shown in your SigNoz Cloud account (for example `us`, `in`, or `eu`)
- `<your-ingestion-key>` is the ingestion key generated in the SigNoz UI

> **Note:** The ingestion endpoint (`4317` for gRPC or `4318` for HTTP) is not a user interface. It only accepts telemetry. Open the SigNoz Cloud dashboard to view the traces.

## 4. Run the Order Service with Auto-Instrumentation

Start the Flask service through the OpenTelemetry launcher so instrumentation is applied automatically:

```bash
opentelemetry-instrument python app.py
```

The service listens on `http://localhost:5001`. It prints a few helper messages and runs without hot reload. Debugging reloaders break instrumentation, so leave them disabled.

## 5. Generate Dummy Traffic

Open a second terminal, move into the project, activate the same virtual environment, and execute the test script:

```bash
cd <path-to-clone>/signoz-demo
source venv/bin/activate
python test.py
```

The script alternates between hitting `/createOrder` and `/checkInventory`. It emits fake orders and inventory checks, prints responses, and reports errors. The application does not execute any business logic.

Within a minute the spans and metrics appear in SigNoz Cloud under the `order-service` name.
## 6. Viewing Data

- Log in at [signoz.io](https://signoz.io/). Locate the `order-service` entry in the Services list.

Because the service produces random values, the charts do not reflect a real workload. The spans, attributes, events, and metrics still exercise the telemetry pipeline in a realistic way.

## Troubleshooting Tips

- **“Port 5001 is in use”**: Another instance of the service is running. Stop it with `Ctrl+C` or find the process with `lsof -i :5001`.
- **`StatusCode.UNAUTHENTICATED` errors**: The ingestion key header is missing or invalid. Double-check the `OTEL_EXPORTER_OTLP_HEADERS` variable and confirm that you export it in the same terminal that launches the service.
- **`pkg_resources is deprecated` warning**: The OpenTelemetry launcher still imports `pkg_resources`. You can ignore the warning or pin `setuptools<81` until a newer distro is released.

## Repository Layout

```
app.py             # Flask API emitting spans/metrics
test.py            # Simple traffic generator
requirements.txt   # Python dependencies
README.md
```

Enjoy experimenting with the demo. Use it to focus on wiring observability rather than business logic. Replace the dummy application with your own service once you are comfortable sending data to SigNoz Cloud.
