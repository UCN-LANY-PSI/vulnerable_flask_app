# setup_db_student.py
# Formål: Træn i at oprette en lille testdatabase i SQLite.
# Opgaver (TODO):
#  1) Udfyld USERS_SCHEMA med en korrekt CREATE TABLE for 'users'
#     - Kolonnenavne SKAL være: id, username, email, role
#     - Krav: id = INTEGER PRIMARY KEY AUTOINCREMENT
#             username = TEXT NOT NULL UNIQUE
#             email = TEXT NOT NULL
#             role = TEXT NOT NULL (gerne CHECK på ('user','manager','admin'))
#  2) Tilføj mindst 5 rækker i USERS_ROWS (inkl. mindst én 'admin')
#  3) (Valgfrit) Udfyld USERS_INDEX_SQL for hurtigere opslag på username
#  4) Kør sanity_check: den fejler indtil kravene er opfyldt
#
# Kør:
#   python setup_db_student.py            # opret/overskriv test.db
#   python setup_db_student.py --fresh    # sletter test.db først

from __future__ import annotations
import argparse
import sqlite3
from pathlib import Path
from typing import Iterable, Tuple

DB_PATH = Path("test.db")

# ---------- TODO 1: Skema ----------
USERS_SCHEMA = """
CREATE TABLE users (
    -- TODO: id som INTEGER PRIMARY KEY AUTOINCREMENT
    -- TODO: username som TEXT NOT NULL UNIQUE
    -- TODO: email som TEXT NOT NULL
    -- TODO: role som TEXT NOT NULL  (gerne CHECK role IN ('user','manager','admin'))
);
""".strip()

# ---------- TODO 2: Data ----------
# Tilføj mindst 5 rækker. Behold strukturen (username, email, role).
USERS_ROWS: Iterable[Tuple[str, str, str]] = [
    # Eksempler (må gerne ændres/udvides):
    # ("alice", "alice@example.com", "user"),
    # ("bob",   "bob@example.com",   "user"),
    # ("carol", "carol@example.com", "manager"),
    # ("dave",  "dave@example.com",  "admin"),
    # ("eve",   "eve@example.com",   "user"),
]

# ---------- TODO 3 (valgfri): Indeks ----------
USERS_INDEX_SQL = """
-- TODO (valgfri): fx CREATE INDEX idx_users_username ON users(username);
""".strip()


def get_conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def reset_db():
    if DB_PATH.exists():
        DB_PATH.unlink()


def create_schema(conn: sqlite3.Connection):
    if "TODO" in USERS_SCHEMA:
        raise NotImplementedError("Udfyld USERS_SCHEMA (CREATE TABLE users ...).")
    with conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute(USERS_SCHEMA)
        if USERS_INDEX_SQL and "CREATE INDEX" in USERS_INDEX_SQL.upper():
            conn.execute(USERS_INDEX_SQL)


def seed_users(conn: sqlite3.Connection):
    rows = list(USERS_ROWS)
    if not rows or len(rows) < 5:
        raise AssertionError("Tilføj mindst 5 rækker i USERS_ROWS (inkl. mindst én 'admin').")
    with conn:
        conn.executemany(
            "INSERT INTO users (username, email, role) VALUES (?, ?, ?);",
            rows,
        )


def sanity_check(conn: sqlite3.Connection):
    cur = conn.cursor()

    # 1) Tjek kolonner
    cur.execute("PRAGMA table_info('users');")
    cols = {row[1] for row in cur.fetchall()}  # row[1]=name
    required = {"id", "username", "email", "role"}
    missing = required - cols
    if missing:
        raise AssertionError(f"Mangler kolonner i 'users': {', '.join(sorted(missing))}")

    # 2) Tjek PK/autoincrement indirekte (id skal vokse, og være integer)
    cur.execute("SELECT typeof(id) FROM users LIMIT 1;")
    t = cur.fetchone()
    if not t or t[0] != "integer":
        raise AssertionError("Kolonnen 'id' skal være INTEGER (PK AUTOINCREMENT).")

    # 3) Mindst 5 rækker
    cur.execute("SELECT COUNT(*) FROM users;")
    count = cur.fetchone()[0]
    if count < 5:
        raise AssertionError("Der skal være mindst 5 rækker i 'users'.")

    # 4) Mindst én admin
    cur.execute("SELECT COUNT(*) FROM users WHERE role='admin';")
    admins = cur.fetchone()[0]
    if admins < 1:
        raise AssertionError("Tilføj mindst én række med role='admin'.")

    # 5) Unikke usernames (detekter dubletter)
    cur.execute("""
        SELECT username, COUNT(*) c FROM users
        GROUP BY username HAVING c > 1;
    """)
    dups = cur.fetchall()
    if dups:
        raise AssertionError(f"Dublerede usernames fundet: {dups}")

    print("Sanity check: OK")


def main():
    parser = argparse.ArgumentParser(description="Opret lille testdatabase (SQLite) til SQLi-øvelse.")
    parser.add_argument("--fresh", action="store_true", help="Slet eksisterende test.db først")
    args = parser.parse_args()

    if args.fresh:
        reset_db()

    conn = get_conn()
    try:
        create_schema(conn)
        seed_users(conn)
        sanity_check(conn)
    finally:
        conn.close()

    print(f"OK: {DB_PATH} klar.")


if __name__ == "__main__":
    main()
