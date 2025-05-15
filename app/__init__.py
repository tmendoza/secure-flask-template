from flask import Flask
from flask_smorest import Api
from app.api.v1.todos import blp as todos_blp
from app.auth.oidc import configure_oidc

def create_app():
    app = Flask(__name__)
    app.config.update(
        API_TITLE="todo-svc",
        API_VERSION="1.0.0",
        OPENAPI_VERSION="3.1.0",
        DATABASE_URL="postgresql://postgres:postgres@db:5432/todo"
    )
    api = Api(app)
    api.register_blueprint(todos_blp, url_prefix="/v1/todos")
    configure_oidc(app)
    return app
