import mysql.connector
from werkzeug.security import generate_password_hash

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="jouw_mysql_wachtwoord",
    database="wms_db"
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role VARCHAR(20) DEFAULT 'scanner'
)
""")


gebruikers = [
    ("admin", "test@1234", "admin"),
    ("Roy", "test@1234", "admin"),
    ("Stefan", "test@1234", "admin"),
    ("Rocky", "test@1234", "admin"),
    ("Farhan", "test@1234", "scanner"),
    ("Olivier", "test@1234", "scanner"),
    ("Kenneth", "test@1234", "scanner"),
    ("Jens", "test@1234", "scanner"),
    ("Abdullah", "test@1234", "scanner"),
    ("Bilal", "test@1234", "scanner"),
    ("Peter", "test@1234", "scanner"),
    ("Fréderic", "test@1234", "scanner"),
    ("Robbe", "test@1234", "scanner"),
    ("Matthias", "test@1234", "scanner"),
    ("Sven", "test@1234", "scanner"),
    ("Magomed", "test@1234", "scanner"),
    ("Enrique", "test@1234", "scanner"),
    ("Tom", "test@1234", "scanner"),
    ("Nelson", "test@1234", "scanner"),
    ("Interim1", "test@1234", "scanner"),
    ("Gabriël", "test@1234", "scanner"),
    ("Dragos", "test@1234", "scanner"),
    ("Thomas", "test@1234", "scanner")
]

for username, password, role in gebruikers:
    try:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            (username, generate_password_hash(password), role)
        )
    except mysql.connector.errors.IntegrityError:
        print(f"{username} bestaat al – wordt overgeslagen.")

conn.commit()
print("Gebruikers toegevoegd!")
conn.close()
