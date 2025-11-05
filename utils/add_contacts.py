"""Přidá Ondřeje do databáze"""
from database import CallDB

db = CallDB()

my_contact = {
    'name': 'Ondřej Hýža',
    'phone': '+420735744433',
    'company': 'Rožnovská Střední',
    'email': 'ondrej@hyza.cz'
}

print("Přidávám kontakt...")
print(f"Jméno: {my_contact['name']}")
print(f"Telefon: {my_contact['phone']}")

if db.add_contact(my_contact):
    print("\n✓ Kontakt úspěšně přidán!")
else:
    print("\n⊘ Kontakt už existuje (duplikát)")

# Zobraz všechny kontakty
contacts = db.get_contacts()
print(f"\nCelkem v databázi: {len(contacts)} kontaktů")

for c in contacts:
    print(f"  - {c['name']} ({c['phone']})")