
FROM python:3.10-slim as builder

WORKDIR /app

# Install system dependencies required to build Python packages (like psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev

# Install Python dependencies into a dedicated folder
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.10-slim

WORKDIR /app

# Install ONLY the runtime libraries for Postgres, not the heavy compilers
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy the installed python packages from the builder stage
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Expose the port and run via Eventlet for WebSockets
EXPOSE 5000
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "-b", "0.0.0.0:5000", "app:create_app()"]