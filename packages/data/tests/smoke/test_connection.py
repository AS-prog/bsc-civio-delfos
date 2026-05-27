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
        assert conn.is_closed is False, "Connection should be open"
    finally:
        conn.close()
        assert conn.is_closed is True, "Connection should be closed"
