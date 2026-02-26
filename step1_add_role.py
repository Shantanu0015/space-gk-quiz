import sqlite3

db = sqlite3.connect("quiz.db")

db.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")

db.commit()
db.close()

print("Role column added successfully")