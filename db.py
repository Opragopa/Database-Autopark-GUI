import configparser
import os
from typing import Optional

import psycopg2

from utils import hash_password


def load_config(filename='config.ini', section='postgresql'):
    parser = configparser.ConfigParser()
    if os.path.exists(filename):
        parser.read(filename)
    else:
        parser.read_string("""
[postgresql]
host = localhost
database = autopark
user = postgres
password = postgres
port = 5432
""")
    return {k: v for k, v in parser.items(section)}

def get_connection() -> Optional[psycopg2.extensions.connection]:
    config = load_config()
    config['client_encoding'] = 'UTF8'
    return psycopg2.connect(**config)

def init_default_users():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM users")
            if cur.fetchone()[0] == 0:
                admin_hash = hash_password("admin123")
                user_hash = hash_password("user123")
                cur.execute(
                    "INSERT INTO users (login, password_hash, role) VALUES (%s, %s, %s), (%s, %s, %s)",
                    ("admin", admin_hash, "admin", "user", user_hash, "user")
                )
                conn.commit()
                print("Created default users: admin / user")
    finally:
        conn.close()