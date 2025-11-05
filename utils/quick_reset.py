"""Reset databáze pro opakované testování"""
import sqlite3
import os

db_path = 'data/calls.db'

print("=" * 60)
print("   RESET DATABÁZE PRO TESTOVÁNÍ")
print("=" * 60)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Zobraz co tam je
cursor.execute("SELECT * FROM contacts")
contacts = cursor.fetchall()
print(f"\n📊 Aktuální kontakty: {len(contacts)}")
for c in contacts:
    print(f"  - {c[1]} ({c[2]}) - Status: {c[5]}, Volání: {c[6]}")

cursor.execute("SELECT * FROM calls")
calls = cursor.fetchall()
print(f"\n📞 Aktuální hovory: {len(calls)}")

# 2. Potvrzení
confirm = input("\nSmazat všechny hovory a resetovat kontakty? (ano/ne): ")

if confirm.lower() == 'ano':
    # Smaž hovory
    cursor.execute("DELETE FROM calls")
    print("✓ Hovory smazány")
    
    # Reset kontaktů na 'new'
    cursor.execute("UPDATE contacts SET status = 'new', call_count = 0, last_called = NULL")
    print("✓ Kontakty resetovány")
    
    conn.commit()
    
    # Ověř
    cursor.execute("SELECT COUNT(*) FROM calls")
    remaining_calls = cursor.fetchone()[0]
    
    cursor.execute("SELECT * FROM contacts WHERE status = 'new'")
    new_contacts = cursor.fetchall()
    
    print(f"\n✅ RESET DOKONČEN")
    print(f"  Hovory: {remaining_calls}")
    print(f"  Kontakty 'new': {len(new_contacts)}")
    
    for c in new_contacts:
        print(f"    - {c[1]} ({c[2]})")
    
    print("\n🚀 Můžeš znovu spustit kampaň!")
else:
    print("\n⊘ Reset zrušen")

conn.close()