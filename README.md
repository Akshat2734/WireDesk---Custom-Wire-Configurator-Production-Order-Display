# 🔌 WireDesk --- Distributed Production Order Management System

> Enterprise-grade production management platform for custom wire
> manufacturing featuring **PyQt6**, **Flask**, **PostgreSQL**,
> **Redis**, **Socket.IO**, **Docker**, **Nginx**, **PgBouncer**,
> **Prometheus**, and **Grafana**.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-API-black?logo=flask)
![PyQt6](https://img.shields.io/badge/PyQt6-Desktop-41CD52)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-326CE5?logo=kubernetes&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Primary%2FReplica-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-Cache-DC382D?logo=redis&logoColor=white)
![Socket.IO](https://img.shields.io/badge/Socket.IO-Realtime-black?logo=socketdotio)
![RabbitMQ](https://img.shields.io/badge/Architecture-Outbox%20Pattern-orange)
![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C?logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-Dashboard-F46800?logo=grafana&logoColor=white)

------------------------------------------------------------------------

# 📖 Overview

WireDesk is a distributed manufacturing execution and production order
management system built for custom wire manufacturing. The platform
provides dynamic product configuration, real-time production monitoring,
analytics, and synchronized factory floor displays using a horizontally
scalable backend.

------------------------------------------------------------------------

# 🌟 Core Platform Features

- **Dynamic JSON-Driven Configurator:** The platform uses a dynamic JSON-driven configurator to handle custom wire manufacturing specifications.
- **Real-time Synchronization:** It provides real-time production monitoring and synchronizes factory floor displays.
- **Transactional Outbox Pattern:** The system utilizes an outbox pattern architecture for reliable event publishing and message brokering.

---

# 🖥️ Desktop Client (PyQt6)
- **Role-Based Interfaces:** The desktop application features role-based graphical user interfaces.
- **Visual Product Grid:** The main dashboard uses a grid-based card layout that allows users to configure various types of products, including House Wire, Multi Core Round Cable, 3 Core Flat Submersible Cable, Service Wire, and Speaker Wire.
- **Live Order Tracking:** Includes a dedicated side-panel for **Live Orders** that automatically fetches and displays compact order cards showing details like wire type, length in meters, and total cost.
- **Status Management:** Users can instantly update the status of active orders through a dropdown menu featuring options like **preprocessing**, **processing**, and **done**.

---

# ⚙️ Backend API (Flask) & Architecture
- **High-Availability Database Strategy:** PostgreSQL is configured with a Primary/Replica setup where writes are routed through PgBouncer to the Primary node, and reads go directly to the Replica node.
- **Connection Pooling:** Implements PgBouncer to manage database connection pooling and protect the primary database under heavy load.
- **Caching & Pub/Sub:** Uses Redis for caching responses and handling Pub/Sub messaging across API nodes.
- **WebSockets:** Socket.IO is integrated into the Flask server to push real-time order updates to all connected clients seamlessly.

---

# 🔒 Security Features
- **Authentication:** The backend relies on JWT (JSON Web Tokens) to authenticate user requests.
- **RBAC:** Role-Based Access Control is enforced at the route level via custom decorators (e.g., `@role_required("admin")`).

---

# 📊 DevOps & Monitoring
- **Docker Orchestration:** The entire platform is containerized and orchestrated via Docker Compose, including load balancing API traffic through an Nginx reverse proxy.
- **Observability Stack:** Comprehensive monitoring is achieved by integrating Prometheus (for pulling metrics) and Grafana (for visual dashboards).
- **Alerting:** An Alertmanager container is mapped to the network to handle incoming metric alerts.


# 🏗 High-Level Architecture

``` mermaid
graph TD
Client1[Admin PyQt6]
Client2[Factory Display]
Client1-->NG[Nginx]
Client2-->NG
NG-->API1[Flask API 1]
NG-->API2[Flask API 2]
API1<-->Redis[(Redis Pub/Sub)]
API2<-->Redis
API1-->PgB[PgBouncer]
API2-->PgB
PgB-->Primary[(PostgreSQL Primary)]
Primary-.WAL Replication.->Replica[(PostgreSQL Replica)]
API1-->WS[Socket.IO]
API2-->WS
WS-->Client1
WS-->Client2
```

# 🔄 Request Lifecycle

``` mermaid
sequenceDiagram
actor User
participant Client
participant API
participant Redis
participant DB

User->>Client: Create Order
Client->>API: POST /orders
API->>DB: Insert Order + Outbox
DB-->>API: Commit
API->>Redis: Publish Event
Redis-->>Client: orders_updated
Client->>API: GET /orders
API->>Redis: Cache?
alt Hit
Redis-->>Client: Cached Orders
else Miss
API->>DB: Read Replica
DB-->>Client: Orders
end
```

# 🧱 Deployment Topology

``` mermaid
graph LR
Users-->Nginx
Nginx-->APIA
Nginx-->APIB
APIA-->PgBouncer
APIB-->PgBouncer
PgBouncer-->Primary
Primary-->Replica
APIA-->Redis
APIB-->Redis
Prometheus-.->APIA
Prometheus-.->PgBouncer
Grafana-.->Prometheus
```

# ⚙️ Features

-   Dynamic JSON-driven wire configurator
-   Role-based desktop interfaces
-   JWT authentication
-   Transactional Outbox Pattern
-   Redis caching
-   PostgreSQL Primary/Replica
-   PgBouncer connection pooling
-   Socket.IO live synchronization
-   Prometheus metrics
-   Grafana dashboards
-   Docker Compose deployment
-   Kubernetes-ready architecture

# 📂 Repository Structure

``` text
wiredesk/
├── client/
├── server/
├── docker-compose.yml
├── nginx.conf
├── prometheus.yml
├── alerts.yml
└── README.md
```

# 🚀 Quick Start

``` bash
git clone <repo>
cd wiredesk
docker compose up --build
```

# 📊 Monitoring

-   Prometheus
-   Grafana
-   API Metrics
-   Database Metrics
-   Redis Metrics
-   Node Exporter

# 🔒 Security

-   JWT Authentication
-   RBAC
-   Idempotency Keys
-   Input Validation
-   Environment Variables

# ☸️ Kubernetes Ready

The application is stateless and can be deployed with:

-   Horizontal Pod Autoscaler
-   Ingress Controller
-   ConfigMaps
-   Secrets
-   Persistent Volumes
-   Readiness & Liveness Probes

# 📈 Future Roadmap

-   Kubernetes manifests
-   Helm Charts
-   Distributed tracing
-   Kafka integration
-   Multi-tenant support
-   Blue-Green deployments
