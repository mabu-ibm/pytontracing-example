# Traced Python Web Application

A simple Flask web application with OpenTelemetry auto-instrumentation that works with **Instana**, **SigNoz**, and any OTLP-compatible backend.

## Features

- Flask REST API with multiple endpoints
- OpenTelemetry auto-instrumentation (no code changes needed)
- Works with Instana, SigNoz, Jaeger, and any OTLP backend
- Kubernetes-ready with health checks
- Configurable via environment variables

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Welcome message with endpoint list |
| `GET /health` | Health check endpoint |
| `GET /api/users` | Returns sample user data |
| `GET /api/orders` | Returns sample order data |
| `GET /api/slow` | Simulates slow response (0.5-2s) |
| `GET /api/error` | Randomly throws errors (50% chance) |

## Quick Start

### 1. Build the Docker Image

```bash
cd traced-webapp
docker build -t traced-webapp:latest .
```

### 2. Run Locally (without tracing)

```bash
docker run -p 8080:8080 traced-webapp:latest
```

### 3. Run Locally with Tracing

```bash
# For SigNoz
docker run -p 8080:8080 \
  -e OTEL_SERVICE_NAME=traced-webapp \
  -e OTEL_EXPORTER_OTLP_ENDPOINT=http://host.docker.internal:4317 \
  traced-webapp:latest

# For Instana
docker run -p 8080:8080 \
  -e OTEL_SERVICE_NAME=traced-webapp \
  -e OTEL_EXPORTER_OTLP_ENDPOINT=http://host.docker.internal:4317 \
  traced-webapp:latest
```

## Kubernetes Deployment

### Option A: Deploy for SigNoz

```bash
# Make sure SigNoz is installed in your cluster
# https://signoz.io/docs/install/kubernetes/

# Deploy the app
kubectl apply -f k8s/namespace.yaml # Instana Autotracing disabled 
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/signoz/deployment-signoz.yaml
```

### Option B: Deploy for Instana

```bash
# Make sure Instana agent is installed in your cluster
# https://www.ibm.com/docs/en/instana-observability/current?topic=agents-installing-host-agent-kubernetes

# Deploy the app
kubectl apply -f k8s/namespace.yaml # Instana Autotracing disabled
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/instana/deployment-instana.yaml
```

### Option C: Deploy with Kustomize

```bash
# Edit k8s/deployment.yaml to set the correct OTLP endpoint
kubectl apply -k k8s/
```

## Configuration

All configuration is done via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `OTEL_SERVICE_NAME` | Service name in traces | `traced-webapp` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP collector endpoint | - |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | Protocol (`grpc` or `http/protobuf`) | `grpc` |
| `OTEL_TRACES_SAMPLER` | Sampling strategy | `parentbased_traceidratio` |
| `OTEL_TRACES_SAMPLER_ARG` | Sampling rate (0.0-1.0) | `1.0` |
| `PORT` | Application port | `8080` |

## OTLP Endpoints

### SigNoz (Kubernetes)
```
http://signoz-otel-collector.signoz.svc.cluster.local:4317
```

### Instana (Kubernetes)
```
http://instana-agent.instana-agent.svc.cluster.local:4317
```

### SigNoz (Docker Compose)
```
http://signoz-otel-collector:4317
```

### Local Development
```
http://localhost:4317
```

## Testing Traces

Generate some traffic to see traces:

```bash
# Get the service URL
kubectl port-forward svc/traced-webapp 8080:80

# Generate requests
curl http://localhost:8080/
curl http://localhost:8080/api/users
curl http://localhost:8080/api/orders
curl http://localhost:8080/api/slow
curl http://localhost:8080/api/error
```

Or use a load generator:

```bash
# Generate 100 requests
for i in {1..100}; do
  curl -s http://localhost:8080/api/users > /dev/null
  curl -s http://localhost:8080/api/orders > /dev/null
done
```

## How Auto-Instrumentation Works

The application uses OpenTelemetry's auto-instrumentation which:

1. **Wraps the application** - The `opentelemetry-instrument` command wraps your Python app
2. **Auto-detects frameworks** - Automatically detects Flask, requests, and other libraries
3. **Creates spans** - Automatically creates spans for HTTP requests, database calls, etc.
4. **Exports traces** - Sends traces to the configured OTLP endpoint

No code changes are required in your application!

## Project Structure

```
traced-webapp/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container image
├── README.md             # This file
└── k8s/
    ├── deployment.yaml   # Generic deployment
    ├── service.yaml      # Kubernetes service
    ├── configmap.yaml    # Configuration
    ├── kustomization.yaml
    ├── signoz/
    │   └── deployment-signoz.yaml
    └── instana/
        └── deployment-instana.yaml
```

## Troubleshooting

### No traces appearing?

1. Check the OTLP endpoint is correct
2. Verify the collector is running: `kubectl get pods -n signoz` or `kubectl get pods -n instana-agent`
3. Check application logs: `kubectl logs -l app=traced-webapp`

### Connection refused errors?

1. Ensure the collector service is accessible from your namespace
2. Check if you need to use HTTP instead of gRPC: set `OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf`

### Traces are incomplete?

1. Ensure sampling rate is 1.0 for testing: `OTEL_TRACES_SAMPLER_ARG=1.0`
2. Check that all services in the call chain are instrumented
