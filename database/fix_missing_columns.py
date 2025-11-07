"""
Přidá chybějící sloupce do existující databáze
"""

import sqlite3

db_path = 'database/knowledge_base.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("🔧 Přidávám chybějící sloupce...")

# Zkontroluj jaké sloupce existují
c.execute("PRAGMA table_info(cold_call_responses)")
existing_columns = [row[1] for row in c.fetchall()]
print(f"📋 Existující sloupce: {existing_columns}")

# Přidej chybějící sloupce
columns_to_add = {
    'times_used': 'INTEGER DEFAULT 0',
    'times_led_to_meeting': 'INTEGER DEFAULT 0',
    'last_used': 'TIMESTAMP',
    'avg_response_time': 'REAL'
}

for col_name, col_type in columns_to_add.items():
    if col_name not in existing_columns:
        try:
            c.execute(f"ALTER TABLE cold_call_responses ADD COLUMN {col_name} {col_type}")
            print(f"✅ Přidán sloupec: {col_name}")
        except sqlite3.OperationalError as e:
            print(f"⚠️  {col_name}: {e}")

# Kontrola redirect_templates
c.execute("PRAGMA table_info(redirect_templates)")
existing_columns = [row[1] for row in c.fetchall()]

redirect_columns = {
    'times_used': 'INTEGER DEFAULT 0',
    'times_successful': 'INTEGER DEFAULT 0',
    'success_rate': 'REAL DEFAULT 50.0',
    'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
    'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
}

for col_name, col_type in redirect_columns.items():
    if col_name not in existing_columns:
        try:
            c.execute(f"ALTER TABLE redirect_templates ADD COLUMN {col_name} {col_type}")
            print(f"✅ Přidán sloupec do redirect_templates: {col_name}")
        except sqlite3.OperationalError as e:
            print(f"⚠️  {col_name}: {e}")

# Kontrola allowed_topics
c.execute("PRAGMA table_info(allowed_topics)")
existing_columns = [row[1] for row in c.fetchall()]

if 'created_at' not in existing_columns:
    try:
        c.execute("ALTER TABLE allowed_topics ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        print(f"✅ Přidán sloupec do allowed_topics: created_at")
    except sqlite3.OperationalError as e:
        print(f"⚠️  created_at: {e}")

# Kontrola czech_natural_phrases
c.execute("PRAGMA table_info(czech_natural_phrases)")
existing_columns = [row[1] for row in c.fetchall()]

if 'created_at' not in existing_columns:
    try:
        c.execute("ALTER TABLE czech_natural_phrases ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        print(f"✅ Přidán sloupec do czech_natural_phrases: created_at")
    except sqlite3.OperationalError as e:
        print(f"⚠️  created_at: {e}")

conn.commit()
conn.close()

print("\n✅ Databáze opravena!")

# Ověření
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("\n📋 Finální struktura cold_call_responses:")
c.execute("PRAGMA table_info(cold_call_responses)")
for row in c.fetchall():
    print(f"   • {row[1]} ({row[2]})")

conn.close()