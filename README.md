# secure-flask-template – *Internal Flask Micro‑service Starter Kit*
A Flask Application Starter Kit for Newbies to OIDC, ABAC, OPA and Pydantic

## 1. Introduction – What Are We Building?

### 1.1 Problem Statement

In modern enterprise systems, applications are increasingly built as a collection of small, independent services (microservices). Each microservice is responsible for a specific business function and communicates over HTTP APIs. However, without a standardized structure, each team may implement:

* Different authentication mechanisms
* Inconsistent authorization checks
* Varying data validation practices
* Divergent deployment pipelines

This inconsistency creates friction in scaling, maintaining, and securing microservices.

### 1.2 Objective

The objective of this project is to provide a comprehensive, production-ready **Flask micro-service starter kit** that:

* Implements **JWT-based authentication** using an OIDC provider (Keycloak).
* Enforces **Attribute-Based Access Control (ABAC)** policies via Open Policy Agent (OPA).
* Exposes RESTful **CRUD APIs** for basic resource management (e.g., Todo items).
* Utilizes **Pydantic** for data validation and serialization.
* Supports **containerization** via Docker and deployment via K3s.
* Leverages **GitOps** for deployment consistency via Flux CD.
* Manages secrets securely using **Vault**.

### 1.3 Target Audience

* Developers with minimal experience in Python, Kubernetes, and Docker who need a ready-to-use template for building secure, scalable Flask microservices.

---

## 2. Detailed Architecture Breakdown

### 2.1 Architectural Overview

```
┌─────────────────────────────────────────┐
│                Client                  │
│  (CLI, Postman, React, etc.)           │
└─────────────────────────────────────────┘
             │  (HTTP + JWT)
             ▼
┌─────────────────────┐      ┌───────────────┐
│     Flask API       │─────▶│ Open Policy   │
│  (Gunicorn + Auth)  │◀─────│ Agent (OPA)   │
│  - JWT verification │      │ - ABAC Rules  │
│  - CRUD logic       │      └───────────────┘
│  - OpenAPI docs     │
└─────────────────────┘
       │
       │ (SQL)
       ▼
┌─────────────┐
│ PostgreSQL  │
└─────────────┘
```

### 2.2 Component Breakdown

| Component      | Role                       | Why We Use It                                                          |
| -------------- | -------------------------- | ---------------------------------------------------------------------- |
| **Flask**      | Web framework              | Simple, lightweight, and well-supported in the Python ecosystem.       |
| **Gunicorn**   | WSGI server                | Production-ready server for handling multiple concurrent requests.     |
| **Authlib**    | OIDC client                | Seamlessly handles JWT verification and key rotation.                  |
| **Pydantic**   | Data validation            | Strong data validation using Python types and JSON schemas.            |
| **OPA**        | Policy engine              | Centralizes authorization logic in a reusable, testable policy engine. |
| **Rego**       | Policy language            | Declarative, logic-based policy definition for OPA.                    |
| **PostgreSQL** | Database                   | ACID-compliant, robust, and highly scalable relational database.       |
| **Vault**      | Secrets manager            | Securely manages DB credentials and JWT keys without hardcoding.       |
| **K3s**        | Kubernetes distro          | Lightweight Kubernetes, ideal for local dev and edge deployments.      |
| **Helm**       | Kubernetes package manager | Deploys services as versioned, reusable templates.                     |
| **Flux CD**    | GitOps controller          | Automatically applies Git changes to the cluster.                      |

---

## 3. Repository Structure and Code Organization

```
{{ cookiecutter.module_name }}/
├── app/
│   ├── __init__.py      # App factory, extension registration
│   ├── api/
│   │   └── v1/
│   │       └── todos.py # CRUD API endpoints
│   ├── auth/
│   │   ├── oidc.py      # JWT verification
│   │   └── opa.py       # OPA client
│   ├── core/
│   │   └── models.py    # SQLAlchemy models
│   ├── db.py            # Database initialization
│   ├── schemas.py       # Pydantic schemas
│   └── services.py      # Business logic layer
├── migrations/          # Alembic migrations
├── policies/            # OPA Rego policies
├── tests/               # Pytest test cases
├── Dockerfile           # Container build file
├── docker-compose.yml   # Local dev stack
├── chart/               # Helm chart for K3s deployment
├── .env.example         # Example environment variables
├── Makefile             # Dev commands (lint, test, build)
└── README.md            # Comprehensive walkthrough
```

---

## 4. Implementation Guide – From Zero to Running

### 4.1 Prerequisite Installation

1. **System Packages:**

```bash
sudo apt update && sudo apt install -y \
  git curl make gnupg lsb-release ca-certificates \
  python3.12 python3.12-venv python3-pip
```

2. **Docker & K3s:**

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --yes --dearmor -o /usr/share/keyrings/docker.gpg
sudo apt update && sudo apt install -y docker-ce docker-ce-cli containerd.io

curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644
```

3. **Copier:**

```bash
python3 -m pip install --user pipx
pipx install copier
```

---

### 4.2 Scaffold the Service with Copier

When you run the Copier command, it will automatically generate the following structure along with code stubs and initial content for each file:

```
{{ cookiecutter.module_name }}/
├── app/
│   ├── __init__.py      # Initializes the Flask app, registers Blueprints and extensions
│   ├── api/
│   │   └── v1/
│   │       └── todos.py # CRUD API endpoints for the Todo resource (GET, POST, PATCH, DELETE)
│   ├── auth/
│   │   ├── oidc.py      # JWT verification via Authlib
│   │   └── opa.py       # Middleware for OPA communication and authorization
│   ├── core/
│   │   └── models.py    # SQLAlchemy models defining the database schema (e.g., Todo model)
│   ├── db.py            # Database initialization and configuration
│   ├── schemas.py       # Pydantic schemas for request/response validation
│   └── services.py      # Business logic layer; contains functions that perform CRUD operations
├── migrations/          # Alembic migrations for database schema changes
├── policies/            # OPA Rego policies, initially includes `allow_all.rego` as a permissive rule
├── tests/               # Pytest test cases for API endpoints and policy checks
├── Dockerfile           # Container build file for Flask API and OPA sidecar
├── docker-compose.yml   # Local development stack: API + Postgres + Keycloak + OPA
├── chart/               # Helm chart for K3s deployment
├── .env.example         # Example environment variables
├── Makefile             # Dev commands (lint, test, build)
└── README.md            # Comprehensive walkthrough
```

### 4.2.1 Command to Scaffold the Service

```bash
copier gh:YOUR-ORG/flask-microservice-template my-todo-svc
cd my-todo-svc
```

Copier will ask you the following questions:

* **service\_name:** A human-readable name for the service (e.g., `todo-svc`)
* **module\_name:** The Python module name (e.g., `todo`)
* **port:** The default port for the service (e.g., `5000`)

After answering these prompts, the specified structure will be generated, with the following key files populated:

* **`todos.py`** – Implements CRUD endpoints using Flask-Smorest Blueprints.
* **`oidc.py`** – Handles JWT validation via Authlib and caches JWKs.
* **`opa.py`** – Communicates with the OPA sidecar, passing method, path, and claims for authorization checks.
* **`models.py`** – Defines the `Todo` model using SQLAlchemy ORM.
* **`db.py`** – Initializes the database connection and session management.
* **`schemas.py`** – Defines input/output schemas using Pydantic for each endpoint.
* **`services.py`** – Implements the core business logic and CRUD operations as isolated functions.

This structure provides a clear separation of concerns:

* **API Layer:** Handles HTTP requests/responses and validation.
* **Auth Layer:** Ensures security via JWT and OPA.
* **Core Layer:** Business logic and data processing.
* **Data Layer:** SQLAlchemy ORM models and migrations.

Now proceed to repository setup.

### 4.3 Create the GitHub Repository

1. **Initialize a new repository:**

```bash
git init my-todo-svc
cd my-todo-svc
git remote add origin https://github.com/YOUR-ORG/my-todo-svc.git
```

2. **Copy the template:**

```bash
copier gh:YOUR-ORG/flask-microservice-template my-todo-svc
```

3. **Set up CI/CD:**

* Add `.gitea-ci.yml` for Drone CI configuration.
* Add `infra/kustomize` for Flux CD deployment manifests.

---

### 4.3 Code Walkthrough

* **app/api/v1/todos.py:** CRUD routes, JWT-protected.
* **app/auth/opa.py:** Middleware that communicates with OPA to enforce Rego policies.
* **app/schemas.py:** Pydantic data models for request validation and response formatting.
* **Dockerfile:** Multi-stage build with dependencies isolated in separate layers.
* **Helm Chart:** Parameterized deployment configuration for K3s.

---

### 4.4 Testing & Running Locally

```bash
docker-compose up --build
```

* Open Keycloak: [http://localhost:8080](http://localhost:8080)
* Access API docs: [http://localhost:5000/openapi.json](http://localhost:5000/openapi.json)

---

### 4.5 Deploy to K3s

```bash
helm install todo-svc chart/ --set image.repository=my-registry/todo-svc --set image.tag=0.1.0
```

### 4.6 Common Errors & Troubleshooting

| Issue              | Cause       | Solution                         |
| ------------------ | ----------- | -------------------------------- |
| `401 Unauthorized` | Invalid JWT | Verify JWT and Keycloak config   |
| `403 Forbidden`    | Rego denial | Update OPA policy in `policies/` |
| `DB connection`    | Vault issue | Check Vault logs                 |

---

### 4.7 Next Steps

* Implement ABAC rules in `policies/`.
* Add automated tests for OPA policies.
* Integrate OpenTelemetry for tracing requests.

Happy building! 🚀
