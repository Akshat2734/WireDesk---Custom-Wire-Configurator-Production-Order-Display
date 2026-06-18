# metrics.py
import time
from flask import request
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# 1. Define the Metrics
# Labels allow us to filter by HTTP method, endpoint, and HTTP status code
REQUEST_COUNT = Counter(
    'http_requests_total', 'Total HTTP Requests',
    ['method', 'endpoint', 'http_status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 'HTTP Request Latency',
    ['method', 'endpoint']
)

# A Gauge goes up and down (perfect for live connections)
ACTIVE_CONNECTIONS = Gauge(
    'websocket_active_connections', 'Current live factory displays'
)

def setup_metrics(app, socketio):
    # 2. Flask Middleware: Triggered before and after every request
    @app.before_request
    def before_request():
        request.start_time = time.time()

    @app.after_request
    def after_request(response):
        # Calculate latency
        latency = time.time() - request.start_time
        
        # We don't want to track the /metrics endpoint itself
        if request.path != '/metrics':
            REQUEST_COUNT.labels(
                request.method, request.path, response.status_code
            ).inc()
            
            REQUEST_LATENCY.labels(
                request.method, request.path
            ).observe(latency)
            
        return response

    # 3. Expose the /metrics endpoint for Prometheus to scrape
    @app.route('/metrics')
    def metrics():
        return generate_latest(), 200, {'Content-Type': 'text/plain; version=0.0.4'}

    # 4. Instrument Socket.IO Connections
    @socketio.on('connect')
    def handle_connect():
        ACTIVE_CONNECTIONS.inc()

    @socketio.on('disconnect')
    def handle_disconnect():
        ACTIVE_CONNECTIONS.dec()