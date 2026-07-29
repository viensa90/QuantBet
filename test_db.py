import sys
sys.path.append('.')
from src.storage.database import DatabaseManager
from src.storage.repository import Repository

db = DatabaseManager("quantbet_test.db")
repo = Repository(db)

# Verificar que las tablas se crearon
conn = db.get_connection()
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tablas creadas:", [t[0] for t in tables])
db.close()