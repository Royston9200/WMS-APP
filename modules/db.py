import os
import mysql.connector
from mysql.connector import Error

def get_connection():
    """Return a live MySQL connection using environment variables."""
    cfg = {
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
    }

    
    missing = [k for k, v in cfg.items() if not v]
    if missing:
        raise RuntimeError(f"Missing DB config keys in .env: {missing}")

    try:
        return mysql.connector.connect(**cfg)
    except Error as e:
        redacted = {**cfg, "password": "***"}
        raise RuntimeError(f"MySQL connection failed: {e}; cfg={redacted}") from e


