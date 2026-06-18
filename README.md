# WireDesk: Distributed Production Management Architecture

## 1. System Topology & Request Lifecycle

The architecture routes HTTP REST traffic and persistent WebSocket connections through a unified NGINX gateway, balancing loads across isolated stateless application nodes while protecting physical storage layers via proxy pooling. The system is designed to decouple edge client state from backend application memory.

### Architectural Flow
When a request enters the system, it follows a strict topology designed for high availability and process isolation:

1. **Edge Gateway (NGINX):** All client traffic (both PyQt6 Manager ordering apps and live Factory Displays) terminates at the NGINX reverse proxy. NGINX handles round-robin load balancing across the API cluster and maintains the HTTP `Upgrade` and `Connection` headers necessary to keep long-lived WebSocket tunnels alive.
2. **Application Cluster (Flask / Gunicorn / Eventlet):** Stateless API nodes process the core business logic and database mapping. By utilizing Eventlet, the Gunicorn workers can handle concurrent WebSocket connections asynchronously without blocking the main execution threads.
3. **Real-Time Backplane (Redis):** Because API nodes are horizontally scaled, client WebSocket connections are fragmented across the cluster. Redis acts as a Pub/Sub message broker. When a state mutation occurs on Node A, it is published to Redis, which instantaneously pushes the event to Node B so all connected edge displays remain synchronized regardless of which node they are attached to.
4. **Connection Pooling (PgBouncer):** Application nodes do not connect directly to the primary database. Write traffic is routed through PgBouncer operating in `transaction` mode. This multiplexes thousands of lightweight application virtual connections through a strictly limited pool of heavy physical PostgreSQL connections, preventing database Out-Of-Memory (OOM) failures under extreme load.
5. **Storage Tier (PostgreSQL Primary/Replica):** The physical storage layer is separated into a Primary node for ACID state mutations and a Replica node for read-only queries, synchronized asynchronously via Write-Ahead Logging (WAL).


## Repository Architecture

To enforce strict Separation of Concerns and ensure microservice-readiness, the codebase is decoupled into completely independent `client` and `server` environments. The infrastructure and orchestration configurations sit at the repository root.

```text
wiredesk/
├── .github/
│   └── workflows/
│       └── ci.yml                 # Automated pipeline for Flake8 linting and pytest
├── client/                        # The Edge Client (PyQt6 Desktop Apps)
│   ├── app.py                     # Entry point for the Manager's Configuration App
│   ├── display_app.py             # Entry point for the live Factory Floor Display
│   ├── network_sync.py            # Socket.IO client bridging PyQt6 to cloud WebSockets
│   ├── components/                # Reusable UI classes (Card, Overlay, Dashboard)
│   ├── assets/                    # Static UI resources (images, icons)
│   ├── data/                      # JSON schemas for dynamic configuration forms
│   └── lookup_table/              # Local manufacturing constants (tolerances, weights)
├── server/                        # The Application Cluster (Flask/Gunicorn)
│   ├── app.py                     # WSGI entry point and Application Factory
│   ├── requirements.txt           # Python dependencies for the Docker build
│   ├── api/                       # Flask Blueprints (HTTP routes & Socket.IO events)
│   ├── controllers/               # Core Business Logic (Math Engine & Transactional Outbox)
│   ├── models/                    # SQLAlchemy ORM definitions (PostgreSQL schema mapping)
│   ├── extensions/                # Infrastructure wiring (SQLAlchemy, SocketIO, JWT)
│   ├── utils/                     # Custom RBAC decorators and middleware
│   ├── metrics.py                 # Prometheus telemetry (Counters, Histograms)
│   └── tests/                     # Automated unit and integration testing suite
├── compose.yaml                   # Docker Compose orchestrator for the distributed stack
├── Dockerfile                     # Multi-stage containerization script for API nodes
├── nginx.conf                     # Reverse Proxy config (Load Balancing + WebSockets)
├── prometheus.yml                 # Scraper configuration mapping to API metric endpoints
└── alerts.yml                     # Alertmanager rules for triggering automated alarms
```




