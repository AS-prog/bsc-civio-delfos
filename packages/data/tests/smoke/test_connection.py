"""Smoke test: verify Python service can connect to PostgreSQL."""

import os
import psycopg


def test_postgres_connection():
    """Verify data service can reach PostgreSQL via Docker DNS."""
    host = "postgres"
    port = int(os.environ["POSTGRES_PORT"])
    dbname = os.environ["POSTGRES_DB"]
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]

    conn = psycopg.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
    )
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        assert cursor.fetchone() == (1,), "Expected SELECT 1 to return (1,)"
    finally:
        conn.close()
