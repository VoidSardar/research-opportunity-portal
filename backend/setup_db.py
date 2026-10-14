"""
One-time setup: asks for your MySQL root password, writes backend/.env,
then creates the research_portal database and opportunities table.

Run from the backend folder (venv active):  python setup_db.py
"""
import getpass
from pathlib import Path

import mysql.connector

BASE = Path(__file__).resolve().parent
ENV_PATH = BASE / ".env"
SCHEMA_PATH = BASE.parent / "database" / "schema.sql"

print("=== Research Portal database setup ===")
host = input("MySQL host [localhost]: ").strip() or "localhost"
port = input("MySQL port [3306]: ").strip() or "3306"
user = input("MySQL user [root]: ").strip() or "root"
password = getpass.getpass(f"MySQL password for '{user}' (typing is hidden): ")

# 1. Test the login before writing anything
try:
    conn = mysql.connector.connect(host=host, port=int(port), user=user, password=password)
except mysql.connector.Error as e:
    print("\nCould not log in to MySQL:", e)
    if e.errno == 1045:
        print("-> Wrong username or password. Use the root password you set in MySQL Installer.")
    elif e.errno == 2003:
        print("-> MySQL server is not running. Start the MySQL80 service (services.msc).")
    raise SystemExit(1)

# 2. Create the database and table from schema.sql
sql = SCHEMA_PATH.read_text(encoding="utf-8")
cur = conn.cursor()
for statement in [s.strip() for s in sql.split(";") if s.strip()]:
    cur.execute(statement)
conn.commit()
cur.execute("SHOW TABLES FROM research_portal")
tables = [row[0] for row in cur.fetchall()]
conn.close()
print("Database ready. Tables:", tables)

# 3. Write .env so the backend can connect
ENV_PATH.write_text(
    f"DB_HOST={host}\nDB_PORT={port}\nDB_USER={user}\n"
    f"DB_PASSWORD={password}\nDB_NAME=research_portal\n",
    encoding="utf-8",
)
print(f"Wrote {ENV_PATH}")
print("\nDone! Now start the backend with:  uvicorn main:app --reload")
