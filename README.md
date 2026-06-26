
# WireDesk - Production Order Management System

WireDesk is a full-stack, distributed production management application designed for custom wire manufacturing. It features a PyQt6-based desktop application that interfaces with a highly scalable Flask REST API. The system enforces strict role-based access control, real-time factory floor synchronization via WebSockets, and a robust infrastructure designed to handle high-throughput manufacturing data.

---

# 🚀 Key Features

## Frontend (Desktop Client)

- **Role-Based UIs:** Distinct, native PyQt6 interfaces for Admin Configurator and Viewer Factory Display.
- **Dynamic Configuration Engine:** Auto-generates UI forms based on complex JSON product definitions and remote lookup tables.
- **Real-Time Dashboard:** Factory floor viewers receive instant, live UI updates of order statuses without manual refreshing.
- **Interactive Data Visualization:** Displays comprehensive analytics (e.g., copper rate, PVC weight, cost per meter) alongside standard order details.

## Backend (REST API & WebSockets)

- **Role-Based Access Control (RBAC):** JWT-based authentication enforcing strict read/write permissions at the route level.
- **Idempotent Operations:** Utilizes `X-Idempotency-Key` headers on order creation to prevent duplicate manufacturing runs during network retries.
- **Real-Time Event Broadcasting:** Socket.IO integration pushes state changes to connected clients instantly.
- **Transactional Outbox Pattern:** Ensures dual-write consistency between the SQL database and the WebSocket message broker.

## Infrastructure & Scalability

- **CQRS-Style Read/Write Splitting:** Write-heavy operations route to the Primary PostgreSQL database, while read-heavy dashboard views route to a read-only replica.
- **Distributed Caching:** Redis caches `/view_orders` endpoints, utilizing targeted invalidation when new orders are created or updated.
- **Connection Pooling:** Integrates PgBouncer to prevent database connection exhaustion during traffic spikes.
- **System Observability:** Prometheus integration continuously scrapes Node, API, and DB metrics for Grafana dashboard visualization.

---

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

# 🏗️ System Design & Architecture

The architecture of WireDesk is designed to prioritize high availability, strict data consistency, and real-time responsiveness.

## 1. High-Level System Architecture

```mermaid
graph TD
    classDef frontend fill:#232937,stroke:#4da3ff,stroke-width:2px,color:#fff;
    classDef backend fill:#17c3b2,stroke:#000,stroke-width:1px,color:#000;
    classDef database fill:#f4d35e,stroke:#000,stroke-width:1px,color:#000;
    classDef cache fill:#ff6b6b,stroke:#000,stroke-width:1px,color:#fff;

    subgraph Client-Side
        AdminUI[Admin Configurator UI<br/>PyQt6]:::frontend
        ViewUI[Factory Display UI<br/>PyQt6]:::frontend
    end

    API[Flask REST API<br/>JWT Auth]:::backend
    WebSocket[Socket.IO Server<br/>Event Broadcaster]:::backend

    Redis[(Redis Cache<br/>orders:v1)]:::cache

    subgraph Data Tier
        DB_Primary[(Primary DB<br/>SQLModel)]:::database
        DB_Replica[(Failover Replica<br/>Read-Only)]:::database
    end

    AdminUI -- POST /create_order --> API
    AdminUI & ViewUI -- GET /view_orders --> API
    AdminUI & ViewUI -- WS Connection --> WebSocket

    API -- Read/Write --> DB_Primary
    DB_Primary -. Replication .-> DB_Replica
    API -- Read Failover --> DB_Replica

    API -- Invalidate/Update --> Redis
    API -- Read (Cache Hit) --> Redis

    API -- Publish Event --> WebSocket
    WebSocket -- Broadcast 'orders_updated' --> AdminUI & ViewUI
```

**Architectural Note:** Notice how the API gateway routes cached GET requests to Redis while real-time updates rely on a transactional outbox pattern to ensure reliable WebSocket delivery.

---

## 2. Database Schema (Entity Relationship)

```mermaid
erDiagram
    User ||--o{ OrdersDB : creates
    User ||--o{ AnalyticsDB : generates
    User ||--o{ OutboxDB : triggers
    OrdersDB ||--|| AnalyticsDB : "1:1 tied by order_id"

    User {
        int id PK
        string username UK
        string email UK
        string password
    }

    OrdersDB {
        int id PK
        string order_id UK
        int user_id FK
        string idempotency_key UK
        datetime timestamp
        string wire_type
        float length_meters
        string status
    }

    AnalyticsDB {
        int id PK
        string order_id UK
        int user_id FK
        float total_cost
        float cost_per_meter
        float copper_rate_per_kg
        float pvc_weight_kg
        string status
    }

    OutboxDB {
        int id PK
        string event_id UK
        string order_id
        int user_id FK
        string event_type
        json payload
        string status
    }
```

---

## 3. Scalable Infrastructure Topology

```mermaid
graph TD
    classDef proxy fill:#232937,stroke:#4da3ff,stroke-width:2px,color:#fff;
    classDef backend fill:#17c3b2,stroke:#000,stroke-width:1px,color:#000;
    classDef database fill:#f4d35e,stroke:#000,stroke-width:1px,color:#000;
    classDef cache fill:#ff6b6b,stroke:#000,stroke-width:1px,color:#fff;
    classDef monitor fill:#9b59b6,stroke:#000,stroke-width:1px,color:#fff;

    Client([Client Devices]):::proxy

    subgraph Edge Layer
        Nginx[Nginx]
    end

    subgraph Application Layer
        API1[Flask API Node 1]
        API2[Flask API Node 2]
    end

    subgraph Database Layer
        PgBouncer[PgBouncer]
        DB_Main[(PostgreSQL Main)]
        DB_Replica[(PostgreSQL Replica)]
    end

    subgraph Observability
        Prometheus((Prometheus))
        Grafana[Grafana]
    end

    Client --> Nginx
    Nginx --> API1
    Nginx --> API2

    API1 --> PgBouncer
    API2 --> PgBouncer

    PgBouncer --> DB_Main
    PgBouncer --> DB_Replica

    Prometheus -.-> API1
    Prometheus -.-> PgBouncer
    Grafana -.-> Prometheus
```
**Architectural Note:** PgBouncer pools PostgreSQL connections to prevent connection exhaustion, while Prometheus continuously scrapes metrics for Grafana dashboards.

---

## 4. Request Lifecycle

```mermaid
sequenceDiagram
    autonumber

    actor Client
    participant Nginx
    participant API
    participant Redis
    participant PgBouncer
    participant Main
    participant Replica

    rect rgb(35,41,55)
        Note over Client,Replica: Viewing Orders

        Client->>Nginx: GET /view_orders
        Nginx->>API: Route request
        API->>Redis: Check Cache

        alt Cache Miss
            Redis-->>API: Null
            API->>PgBouncer: SELECT
            PgBouncer->>Replica: Execute Query
            Replica-->>PgBouncer: Data
            PgBouncer-->>API: Response
            API->>Redis: Cache Response
        else Cache Hit
            Redis-->>API: Cached JSON
        end

        API-->>Client: Orders
    end

    rect rgb(45,53,69)
        Note over Client,Replica: Creating Order

        Client->>Nginx: POST /create_order
        Nginx->>API: Route request
        API->>PgBouncer: BEGIN
        PgBouncer->>Main: INSERT
        Main-->>PgBouncer: COMMIT
        PgBouncer-->>API: Success
        Main-)Replica: WAL Replication
        API->>Redis: Invalidate Cache
        API-->>Client: 201 Created
    end
```

**Architectural Note:** Read-heavy traffic is served from Redis or the PostgreSQL replica, while write operations are committed only to the primary database before cache invalidation.








