# app/__init__.py

import os
import logging
from flask import Flask, jsonify, request
from flask_smorest import Api
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from app.auth.oidc import configure_oidc
from app.api.v1.todos import blp as todos_blp

# Prometheus counters
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Count of HTTP requests",
    ["method", "endpoint", "http_status"]
)

def create_app():
    app = Flask(__name__)
    app.config.update(
        API_TITLE="todo-svc",
        API_VERSION="1.0.0",
        OPENAPI_VERSION="3.1.0",
        DATABASE_URL=os.getenv("DATABASE_URL"),
        OIDC_ISSUER=os.getenv("OIDC_ISSUER"),
        OPA_URL=os.getenv("OPA_URL"),
    )

    # -------- Logging --------
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '{"time":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}'
    ))
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    # -------- Metrics endpoint --------
    @app.route("/metrics")
    def metrics():
        return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

    # -------- Error handling --------
    api = Api(app)

    @app.errorhandler(Exception)
    def handle_all_errors(e):
        code = getattr(e, "code", 500)
        message = getattr(e, "description", str(e))
        app.logger.error(f"{code} - {message}")
        return jsonify({"code": code, "message": message}), code

    # -------- After-request hook for metrics --------
    @app.after_request
    def after_request(response):
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.path,
            http_status=response.status_code
        ).inc()
        return response

    # -------- Register blueprints & auth --------
    api.register_blueprint(todos_blp, url_prefix="/v1/todos")
    configure_oidc(app)

    return app
