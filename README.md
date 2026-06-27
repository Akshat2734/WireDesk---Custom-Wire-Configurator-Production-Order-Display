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

# 🗄️ Entity Relationship

``` mermaid
erDiagram
User ||--o{ Orders : creates
Orders ||--|| Analytics : has
Orders ||--o{ Outbox : emits

User{
int id PK
string username
string email
}

Orders{
string order_id PK
string status
float length
}

Analytics{
float cost_per_meter
float pvc_weight
}

Outbox{
string event_id
string status
}
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
