from app.db import get_connection

def list_todos():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, title, completed FROM todos")
        return cur.fetchall()

def create_todo(data):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO todos (title, completed) VALUES (%s, %s) RETURNING id, title, completed",
            (data['title'], data.get('completed', False))
        )
        return cur.fetchone()

def get_todo(todo_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, title, completed FROM todos WHERE id=%s", (todo_id,))
        return cur.fetchone()

def update_todo(todo_id, data):
    conn = get_connection()
    set_clause = ", ".join(f"{k}=%s" for k in data.keys())
    values = list(data.values()) + [todo_id]
    with conn.cursor() as cur:
        cur.execute(
            f"UPDATE todos SET {set_clause} WHERE id=%s RETURNING id, title, completed",
            values
        )
        return cur.fetchone()

def delete_todo(todo_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM todos WHERE id=%s", (todo_id,))
