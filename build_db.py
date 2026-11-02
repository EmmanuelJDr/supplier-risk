"""Build a SQLite database from data/metrics.csv so the SQL queries can run."""
import csv
import sqlite3
from pathlib import Path

CSV_FILE = Path("data/metrics.csv")
DB_FILE = Path("data/supplier_risk.db")


def to_int(value):
    return int(value) if value not in ("", None) else None


def main():
    if not CSV_FILE.exists():
        raise SystemExit("data/metrics.csv not found. Run fetch.py first.")

    with CSV_FILE.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if DB_FILE.exists():
        DB_FILE.unlink()

    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE metrics (
            repo TEXT PRIMARY KEY,
            stars INTEGER,
            open_issues INTEGER,
            days_since_push INTEGER,
            archived TEXT,
            days_since_release INTEGER,
            contributors INTEGER,
            fetched_on TEXT
        )
    """)
    conn.executemany(
        "INSERT INTO metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (
                r["repo"],
                int(r["stars"]),
                int(r["open_issues"]),
                to_int(r["days_since_push"]),
                r["archived"],
                to_int(r["days_since_release"]),
                int(r["contributors"]),
                r["fetched_on"],
            )
            for r in rows
        ],
    )
    conn.commit()
    conn.close()
    print(f"Loaded {len(rows)} rows into {DB_FILE}")


if __name__ == "__main__":
    main()