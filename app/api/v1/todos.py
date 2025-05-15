from flask_smorest import Blueprint, abort
from flask.views import MethodView
from app.schemas import TodoSchema
from app.services import list_todos, create_todo, get_todo, update_todo, delete_todo
from app.auth.opa import opa_guard

blp = Blueprint("todos", "todos", description="Todo CRUD operations")

@blp.route("/")
class TodoList(MethodView):
    @opa_guard
    @blp.response(200, TodoSchema(many=True))
    def get(self):
        return list_todos()

    @opa_guard
    @blp.arguments(TodoSchema)
    @blp.response(201, TodoSchema)
    def post(self, new_data):
        return create_todo(new_data)

@blp.route("/<int:todo_id>")
class TodoItem(MethodView):
    @opa_guard
    @blp.response(200, TodoSchema)
    def get(self, todo_id):
        todo = get_todo(todo_id) or abort(404)
        return todo

    @opa_guard
    @blp.arguments(TodoSchema(partial=True))
    @blp.response(200, TodoSchema)
    def patch(self, update_data, todo_id):
        return update_todo(todo_id, update_data)

    @opa_guard
    @blp.response(204)
    def delete(self, todo_id):
        delete_todo(todo_id)
        return ""
