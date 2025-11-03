from dotenv import load_dotenv
from pathlib import Path
from modules.db import get_connection
import traceback


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

try:
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    
    cur.execute("SELECT 1 AS ok")
    print("ping:", cur.fetchone()["ok"])

    
    cur.execute("SELECT COUNT(*) AS n FROM sec_users WHERE active = 1")
    print("active users:", cur.fetchone()["n"])

    
    cur.execute("DESCRIBE sec_users")
    print("sec_users columns:", [r["Field"] for r in cur.fetchall()])

    
    cur.execute("SELECT username FROM sec_users LIMIT 5")
    print("example users:", [r["username"] for r in cur.fetchall()])

    conn.close()

except Exception as e:
    print("❌ Database connection failed!")
    traceback.print_exc()
