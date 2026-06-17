"""Apply pending SQL migrations from the migrations/ directory.

Run:  python -m dublin_jobs.db.migrate

Each *.sql file runs once, in filename order, inside its own transaction, and is
recorded in the schema_migrations table. Re-running applies only what's new.
"""

from pathlib import Path

import psycopg

from dublin_jobs.config import settings

MIGRATIONS_DIR = Path(__file__).resolve().parents[3] / "migrations"


def main() -> None:
    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            " version TEXT PRIMARY KEY,"
            " applied_at TIMESTAMPTZ NOT NULL DEFAULT now())"
        )
        applied = {row[0] for row in conn.execute("SELECT version FROM schema_migrations")}
        pending = [p for p in sorted(MIGRATIONS_DIR.glob("*.sql")) if p.name not in applied]

        if not pending:
            print("up to date — no pending migrations")
            return

        for path in pending:
            with conn.transaction():
                conn.execute(path.read_text())
                conn.execute(
                    "INSERT INTO schema_migrations (version) VALUES (%s)", (path.name,)
                )
            print(f"applied {path.name}")


if __name__ == "__main__":
    main()
