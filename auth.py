from db import get_connection
from utils import verify_password

from typing import Optional

def authenticate(login: str, password: str) -> Optional[str]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT password_hash, role FROM users WHERE login = %s", (login,))
            row = cur.fetchone()
            if row and verify_password(password, row[0]):
                return row[1]  # 'admin' or 'user'
    finally:
        conn.close()
    return None