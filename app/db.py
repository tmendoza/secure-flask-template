import os
import psycopg                       # psycopg 3
from psycopg.rows import dict_row

def get_connection():
    # psycopg 3: use row_factory=dict_row so cursor.fetchall() returns dicts
    return psycopg.connect(
        os.getenv("DATABASE_URL"),
        row_factory=dict_row
    )
