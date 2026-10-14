import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent / ".env"

if not ENV_PATH.exists():
    raise RuntimeError(
        f".env file not found at {ENV_PATH}. "
        "Run 'python setup_db.py' in the backend folder to create it."
    )

load_dotenv(ENV_PATH)


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "research_portal"),
    )
