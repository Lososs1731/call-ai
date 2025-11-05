"""
Import kontaktu z CSV
"""

import csv
import sys
from database import CallDB


def import_csv(filename):
    """Importuje kontakty z CSV"""
    db = CallDB()
    imported = 0
    skipped = 0
    
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            data = {
                'name': row.get('name', row.get('jmeno', '')),
                'phone': row.get('phone', row.get('telefon', '')),
                'company': row.get('company', row.get('firma', '')),
                'email': row.get('email', '')
            }
            
            if db.add_contact(data):
                imported += 1
                print(f"✓ {data['name']}")
            else:
                skipped += 1
                print(f"⊘ {data['name']} (duplicita)")
    
    print(f"\nImportovano: {imported}")
    print(f"Preskoceno: {skipped}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Pouziti: python -m utils.import_contacts data/contacts.csv")
        sys.exit(1)
    
    import_csv(sys.argv[1])