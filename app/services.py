# app/services.py

from app.db import get_connection

def list_todos():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, title, completed FROM todos")
        return cur.fetchall()

def create_todo(data):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO todos (title, completed) VALUES (%s, %s) RETURNING id, title, completed",
                (data['title'], data.get('completed', False))
            )
            row = cur.fetchone()
        conn.commit()    # ← commit the insert
        return row
    finally:
        conn.close()

def get_todo(todo_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, completed FROM todos WHERE id = %s", (todo_id,))
            return cur.fetchone()
    finally:
        conn.close()

def update_todo(todo_id, data):
    conn = get_connection()
    try:
        set_clause = ", ".join(f"{k} = %s" for k in data.keys())
        values = list(data.values()) + [todo_id]
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE todos SET {set_clause} WHERE id = %s RETURNING id, title, completed",
                values
            )
            row = cur.fetchone()
        conn.commit()    # ← commit the update
        return row
    finally:
        conn.close()

def delete_todo(todo_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
        conn.commit()    # ← commit the delete
    finally:
        conn.close()
