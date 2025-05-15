# Todo-Svc – Internal Flask Microservice Starter Kit

[![Build Status](https://img.shields.io/github/actions/workflow/status/your-org/todo-svc/ci.yml)](https://github.com/your-org/todo-svc/actions)
[![Tests Coverage](https://img.shields.io/codecov/c/github/your-org/todo-svc)](https://codecov.io/gh/your-org/todo-svc)
[![License](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)
[![Docker Pulls](https://img.shields.io/docker/pulls/your-org/todo-svc)](https://hub.docker.com/r/your-org/todo-svc)

---

## 🚀 Quick Start

```bash
git clone https://github.com/your-org/todo-svc.git
cd todo-svc
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker-compose up --build
docker-compose exec api python scripts/run_migrations.py
````

* Health check: `curl http://localhost:5000/health`
* API docs: `http://localhost:5000/openapi.json`
* CRUD: `http://localhost:5000/v1/todos/`

---

## 📝 Table of Contents

- [Todo-Svc – Internal Flask Microservice Starter Kit](#todo-svc--internal-flask-microservice-starter-kit)
  - [🚀 Quick Start](#-quick-start)
  - [📝 Table of Contents](#-table-of-contents)
  - [📖 Introduction](#-introduction)
  - [🛠️ Prerequisites](#️-prerequisites)
    - [Software](#software)
    - [Accounts (for production)](#accounts-for-production)
  - [📥 Getting Started](#-getting-started)
  - [🏗️ Project Structure](#️-project-structure)
  - [🔍 Core Concepts \& Architecture](#-core-concepts--architecture)
    - [What this Application Is \& How It Works](#what-this-application-is--how-it-works)
    - [Component Breakdown](#component-breakdown)
  - [📚 Dependencies \& Tools](#-dependencies--tools)
    - [Python Packages](#python-packages)
    - [Dev Tools](#dev-tools)
    - [CI/CD](#cicd)
  - [🏃‍♂️ Usage \& Features](#️-usage--features)
    - [Endpoints](#endpoints)
    - [Example](#example)
  - [✅ Testing](#-testing)
  - [🐳 Docker \& Containerization](#-docker--containerization)
  - [☁️ Deployment](#️-deployment)
    - [Docker \& Docker COmpose](#docker--docker-compose)
    - [Helm + K3s](#helm--k3s)
    - [GitOps (Flux CD)](#gitops-flux-cd)
  - [🔧 Logging \& Monitoring](#-logging--monitoring)
  - [⚙️ CI/CD Pipeline](#️-cicd-pipeline)
  - [📈 Extending the Starter Kit](#-extending-the-starter-kit)
  - [🙋 Frequently Asked Questions](#-frequently-asked-questions)
  - [🤝 Contributing](#-contributing)
  - [📜 License](#-license)
  - [🎉 Acknowledgements \& Resources](#-acknowledgements--resources)
  - [🧾 Changelog](#-changelog)

---

## 📖 Introduction

**What is this?**
A Flask-based, Docker-ready microservice template for building secure, production-grade CRUD APIs.

**Why use it?**

* Consistent folder layout & best practices
* JWT/OIDC authentication via Keycloak
* ABAC authorization via OPA/Rego
* JSON validation with Pydantic & OpenAPI docs
* PostgreSQL persistence using **psycopg2**
* One-command local dev (Docker Compose)
* GitOps deploy to K3s (Helm + Flux CD)
* Built-in testing & CI pipeline

**Who is this for?**
Developers new to Python microservices or returning after a hiatus.

**What you’ll learn**
Flask fundamentals, REST APIs, Docker, database migrations, GitOps, and more.

---

## 🛠️ Prerequisites

### Software

* **Python 3.12+** (with `venv`)
* **pip** or **pipx**
* **Docker & Docker Compose** (optional but recommended)
* **Git**

### Accounts (for production)

* Docker Hub (or private registry)
* Kubernetes cluster credentials (optional)

---

## 📥 Getting Started

1. **Clone the repo**

   ```bash
   git clone https://github.com/your-org/todo-svc.git
   cd todo-svc
   ```
2. **Create & activate virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```
4. **Environment configuration**

   ```bash
   cp .env.example .env
   # edit .env: FLASK_ENV, DATABASE_URL, OIDC_ISSUER, OPA_URL
   ```
5. **Run locally**

   ```bash
   docker-compose up --build
   docker-compose exec api python scripts/run_migrations.py
   ```
6. **Verify**

   * Health: `curl http://localhost:5000/health`
   * API docs: `http://localhost:5000/openapi.json`
   * CRUD: see [Usage & Features](#🏃‍♂️-usage--features)

---

## 🏗️ Project Structure

```
.
├── app/
│   ├── __init__.py         # Flask app factory
│   ├── api/v1/todos.py     # CRUD endpoints & Flask-Smorest
│   ├── auth/              
│   │   ├── oidc.py         # Authlib JWT/OIDC setup
│   │   └── opa.py          # OPA guard decorator
│   ├── core/models.py      # DB models
│   ├── db.py               # psycopg2 connection helper
│   ├── schemas.py          # Marshmallow schemas (TodoSchema)
│   └── services.py         # Business logic (CRUD functions)
├── migrations/             # SQL migration scripts
├── policies/               # OPA policies (allow_all.rego)
├── scripts/                # Helpers (run_migrations.py)
├── tests/                  # pytest tests
├── Dockerfile              # Multi-stage build
├── docker-compose.yml      # Dev stack (api, db, keycloak, opa)
├── chart/                  # Helm chart for K3s
├── .env.example            # Example environment variables
├── Makefile                # lint, test, run, migrations
├── requirements.txt        # Python deps
└── README.md               # This file
```

---

## 🔍 Core Concepts & Architecture

### What this Application Is & How It Works

This **Todo-Svc** is a “to-do list” microservice: authenticated users can **create**, **read**, **update**, and **delete** todo items stored in PostgreSQL. Each request must present a valid JWT (issued by Keycloak), then the app calls OPA (sidecar) to authorize the action. Incoming data is validated by Pydantic; outgoing responses are serialized via Marshmallow. You can run locally with Docker Compose or deploy to K3s via Helm + Flux CD.

### Component Breakdown

| Component                   | Role in App                    | Why Chosen & How It Functions                                                                                                       |
| --------------------------- | ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| **Flask**                   | Core web framework             | - **Why:** Minimalistic, easy to learn<br>- **How:** Defines routes/blueprints for `/v1/todos/` and `/health` endpoint              |
| **Gunicorn**                | WSGI server                    | - **Why:** Production-ready concurrency<br>- **How:** Launches multiple worker processes to serve the Flask app                     |
| **Authlib**                 | OIDC/JWT validation            | - **Why:** Simplifies token verification<br>- **How:** Fetches JWKs from Keycloak, decodes tokens, and checks claims                |
| **Flask-Smorest**           | OpenAPI spec & request parsing | - **Why:** Auto-generates documentation<br>- **How:** Decorators produce `/openapi.json` and handle payload parsing                 |
| **Pydantic**                | Request validation             | - **Why:** Type-driven, clear errors<br>- **How:** Defines `TodoIn` model; rejects invalid JSON payloads                            |
| **Marshmallow**             | Response serialization         | - **Why:** Compatible with Flask-Smorest responses<br>- **How:** Defines `TodoSchema` for serializing output                        |
| **OPA (Open Policy Agent)** | Authorization engine           | - **Why:** Externalizes policy from code<br>- **How:** Sidecar receives method, path, and claims; returns allow/deny                |
| **Rego**                    | Policy language                | - **Why:** Declarative and testable policies<br>- **How:** `.rego` files evaluated by OPA                                           |
| **PostgreSQL**              | Persistent data store          | - **Why:** ACID compliance, reliability<br>- **How:** Stores `todos` table; accessed via `psycopg2`                                 |
| **psycopg2**                | PostgreSQL driver              | - **Why:** Direct SQL control<br>- **How:** `db.py` opens connections using the `DATABASE_URL` environment variable                 |
| **Alembic**                 | Database migrations            | - **Why:** Versioned schema changes<br>- **How:** `scripts/run_migrations.py` applies `migrations/*.sql`                            |
| **Vault**                   | Secrets management             | - **Why:** Keeps credentials out of code<br>- **How:** Sidecar injects secrets as environment variables or mounted files            |
| **Docker & Compose**        | Local orchestration            | - **Why:** Reproducible development stack<br>- **How:** `docker-compose.yml` spins up `api`, `db`, `keycloak`, and `opa`            |
| **K3s**                     | Lightweight Kubernetes         | - **Why:** Easy local/edge cluster<br>- **How:** Runs the same Docker images via Helm charts                                        |
| **Helm**                    | Kubernetes package manager     | - **Why:** Templated, versioned deployments<br>- **How:** `chart/` directory defines Kubernetes manifests and ConfigMaps            |
| **Flux CD**                 | GitOps controller              | - **Why:** Git as single source of truth<br>- **How:** Watches the chart repo (or an infra repo) and syncs changes into the cluster |

---

## 📚 Dependencies & Tools

### Python Packages

* Flask
* Flask-Smorest
* Authlib
* httpx
* cachetools
* psycopg2-binary
* Pydantic
* Marshmallow
* Alembic
* gunicorn
* pytest

### Dev Tools

* Black, isort, Flake8 (pre-commit)
* Docker, docker-compose

### CI/CD

* GitHub Actions or Drone CI config in `.github/workflows/ci.yml`

---

## 🏃‍♂️ Usage & Features

### Endpoints

| Method | Path             | Description       |
| ------ | ---------------- | ----------------- |
| GET    | `/v1/todos/`     | List all todos    |
| POST   | `/v1/todos/`     | Create a new todo |
| GET    | `/v1/todos/{id}` | Get a todo by ID  |
| PATCH  | `/v1/todos/{id}` | Update a todo     |
| DELETE | `/v1/todos/{id}` | Delete a todo     |

### Example

```bash
export TOKEN=...
curl -X POST http://localhost:5000/v1/todos/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk"}'
```

---

## ✅ Testing

```bash
pytest --cov=app
```

* Unit vs integration tests
* Coverage reports via Codecov

---

## 🐳 Docker & Containerization

* **Dockerfile:** Multi-stage, slim image
* **docker-compose.yml:** Services: api, db, keycloak, opa
* Health endpoint at `/health`

---

## ☁️ Deployment

### Docker & Docker COmpose
```bash
docker-compose up --build
docker-compose exec api python scripts/run_migrations.py
```
### Helm + K3s

```bash
docker build -t your-org/todo-svc:0.1.0 .
docker push your-org/todo-svc:0.1.0

helm upgrade --install todo-svc chart/ \
  --set image.repository=your-org/todo-svc \
  --set image.tag=0.1.0
```

### GitOps (Flux CD)

Configure Flux to watch this repo or a sibling infra repo.

---

## 🔧 Logging & Monitoring

* Python `logging` configured in `create_app()`
* Optional Prometheus metrics via `/metrics`

---

## ⚙️ CI/CD Pipeline

Example (GitHub Actions):

```yaml
on: [push]
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with: python-version: 3.12
      - run: pip install -r requirements.txt
      - run: pytest --cov=app
      - run: docker build . -t your-org/todo-svc:latest
```

---

## 📈 Extending the Starter Kit

* **Add endpoint:** blueprint → service → test
* **Background jobs:** Celery or RQ
* **Caching:** Redis + `flask-caching`

---

## 🙋 Frequently Asked Questions

**Why psycopg2 over ORM?**
Direct control, fewer abstractions—easier to see raw SQL.

---

## 🤝 Contributing

Read `CODE_OF_CONDUCT.md`. Fork → feature branch → PR.

---

## 📜 License

MIT © Your Company

---

## 🎉 Acknowledgements & Resources

* [Flask Docs](https://flask.palletsprojects.com)
* [Open Policy Agent](https://www.openpolicyagent.org/)
* [Keycloak](https://www.keycloak.org/)

---

## 🧾 Changelog

See `CHANGELOG.md`.

