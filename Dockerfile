FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install OpenTelemetry auto-instrumentation packages
RUN opentelemetry-bootstrap -a install

# Verify the executable exists
RUN which opentelemetry-instrument

# Copy application code
COPY app.py .

# Expose the application port
EXPOSE 8080

# Set default environment variables for OpenTelemetry
ENV OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
ENV OTEL_TRACES_EXPORTER=otlp
ENV OTEL_METRICS_EXPORTER=otlp
ENV OTEL_LOGS_EXPORTER=otlp
ENV OTEL_EXPORTER_OTLP_PROTOCOL=grpc
ENV PATH="/usr/local/bin:$PATH"

# Run with OpenTelemetry auto-instrumentation
CMD ["opentelemetry-instrument", "gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app:app"]
