"""Smaže všechny kontakty a začne nanovo"""
from database import CallDB
import sqlite3

print("=" * 60)
print("   RESET KONTAKTŮ")
print("=" * 60)

# Přímé připojení k databázi
conn = sqlite3.connect('data/calls.db')
cursor = conn.cursor()

# Zobraz kolik jich je teď
cursor.execute("SELECT * FROM contacts")
current = cursor.fetchall()

print(f"\nAktuálně v DB: {len(current)} kontaktů")

if current:
    print("\nKontakty ke smazání:")
    for c in current:
        print(f"  - {c[1]} ({c[2]})")  # c[1]=name, c[2]=phone

# Potvrzení
confirm = input("\nOpravdu smazat všechny kontakty? (ano/ne): ")

if confirm.lower() == 'ano':
    # Smaž všechny kontakty
    cursor.execute("DELETE FROM contacts")
    conn.commit()
    
    print("\n✓ Všechny kontakty smazány!")
    
    # Reset auto-increment
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='contacts'")
    conn.commit()
    
    # Ověř
    cursor.execute("SELECT COUNT(*) FROM contacts")
    remaining = cursor.fetchone()[0]
    print(f"✓ Zbývá: {remaining} kontaktů")
    
    print("\n" + "=" * 60)
    print("Nyní můžeš přidat nové kontakty:")
    print("  python add_my_contact.py")
    print("=" * 60)
else:
    print("\n⊘ Reset zrušen")

conn.close()