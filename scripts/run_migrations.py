from app.db import get_connection

def run_migrations():
    conn = get_connection()
    with conn.cursor() as cur:
        with open('migrations/init.sql') as f:
            cur.execute(f.read())
    conn.commit()

if __name__ == '__main__':
    run_migrations()
