# ACIT3855 – Smartwatch Telemetry Microservices

This project implements a microservices-based architecture for collecting, storing, processing, and auditing smartwatch telemetry data.

## 🧱 Architecture Overview

The system is composed of five independently running microservices:

- **Receiver Service**: Accepts telemetry data (e.g., step count, weight) via REST API.
- **Storage Service**: Stores raw telemetry data and processed summaries in a MySQL database.
- **Processing Service**: Subscribes to telemetry data, calculates statistics, and forwards results to the Storage service.
- **Audit Log Service**: Receives and stores log entries related to all service activity.
- **Health Service**: Provides health and performance metrics for monitoring purposes.

Each service runs in its own container and communicates using HTTP. A React-based frontend dashboard is included to visualize and interact with the data.

## 🚀 Features

- Fully containerized microservices using Docker and Docker Compose
- REST APIs built with Flask for each service
- PostgreSQL/MySQL integration via SQLAlchemy
- OpenAPI (Swagger) specifications for API documentation
- Centralized structured logging via YAML-configured loggers
- React frontend to view real-time and historical telemetry data
- CI/CD readiness with modular service structure

## 🧰 Tech Stack

**Backend**
- Python 3.x
- Flask
- SQLAlchemy
- MySQL / SQLite (for local testing)
- Docker, Docker Compose
- OpenAPI (Swagger) Specs
- Logging: Python `logging` + YAML config

**Frontend**
- React.js
- Axios
- HTML/CSS

**Tools**
- Git & GitHub
- VS Code
- Postman (for API testing)

## 📁 Project Structure

```
.
├── receiver/             # Accepts telemetry data
├── processing/           # Computes summaries/statistics
├── storage/              # Stores telemetry and summaries
├── audit_log/            # Tracks system activity
├── health/               # Reports health and performance
├── dashboard/            # React frontend app
├── nginx/                # Reverse proxy configuration
├── config/
│   ├── receiver/         # Receiver service config (e.g., app_conf.yml)
│   ├── processing/       # Processing service config
│   ├── storage/          # Storage service config
│   ├── audit_log/        # Audit log service config
│   └── health/           # Health service config
└── deployment/docker-compose.yml    # Orchestration file

```

## ⚙️ Configuration Files

Each microservice includes:
- `app_conf.yml`: Service-specific configurations like ports, host URLs, and database credentials.
- `log_conf.yml`: Defines structured logging formats, handlers, and levels for consistent logging across services.

The `nginx/` folder contains `nginx.conf`, which routes API requests to the appropriate services using path-based rules.

## 📡 API Endpoints

Each microservice exposes the following endpoints:

### 🔌 Receiver Service
- `POST /read/steps` – Receives a JSON payload containing a timestamp and step count.
- `POST /read/weight` – Receives a JSON payload containing a timestamp and weight.
- `GET /health` – Returns receiver service health info.

### 🧮 Processing Service
- `GET /stats` – Returns the latest statistics regarding weight and steps.
- `GET /health` – Returns processing service health info.

### 💾 Storage Service
- `GET /read/steps` – Retrieves step count records between a starting and ending timestamp from the database.
- `GET /read/weight` – Retrieves weight records between a starting and ending timestamp from the database.
- `GET /health` – Returns storage service health info.

### 🧾 Audit Log Service
- `GET /step` – Returns a step reading at a specified index from the service.
- `GET /weight` – Returns a weight reading at a specified index from the service.
- `GET /health` – Returns audit log service health info.

### ❤️ Health Service
- `GET /health` – Aggregates and returns the health status of all microservices.
