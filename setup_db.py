import sqlite3
import json

# Connect DB (creates file automatically)
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# 🔧 Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    problem TEXT,
    solutions TEXT
)
""")

# 📂 Load JSON
with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

# 📥 Insert data
for category in data:
    for item in data[category]:
        cursor.execute(
            "INSERT INTO problems (category, problem, solutions) VALUES (?, ?, ?)",
            (
                category,
                item["problem"],
                json.dumps(item["solutions"])
            )
        )

conn.commit()
conn.close()

print("✅ Database setup complete")