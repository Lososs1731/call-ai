"""
Hromadný import kontaktů z CSV
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import CallDB
import csv


def import_contacts_from_csv(csv_file):
    """Importuje kontakty z CSV souboru"""
    
    db = CallDB()
    
    print(f"\n{'='*60}")
    print(f"📥 IMPORT KONTAKTŮ Z CSV")
    print(f"{'='*60}")
    print(f"Soubor: {csv_file}")
    
    imported = 0
    skipped = 0
    errors = 0
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    # Očekávané sloupce: name, phone, email, company
                    name = row.get('name', '').strip()
                    phone = row.get('phone', '').strip()
                    email = row.get('email', '').strip()
                    company = row.get('company', '').strip()
                    
                    # Validace
                    if not name or not phone:
                        print(f"  ⚠️  Přeskakuji řádek (chybí jméno nebo telefon): {row}")
                        skipped += 1
                        continue
                    
                    # Normalizuj telefon (odeber mezery, pomlčky)
                    phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                    
                    # Zkontroluj jestli už existuje
                    existing = db.cursor.execute(
                        "SELECT id FROM contacts WHERE phone = ?", (phone,)
                    ).fetchone()
                    
                    if existing:
                        print(f"  ⚠️  Kontakt už existuje: {phone} ({name})")
                        skipped += 1
                        continue
                    
                    # Přidej kontakt
                    db.add_contact({
                        'name': name,
                        'phone': phone,
                        'email': email,
                        'company': company,
                        'status': 'new'
                    })
                    
                    imported += 1
                    
                    if imported % 10 == 0:
                        print(f"  ✅ Importováno: {imported}")
                    
                except Exception as e:
                    print(f"  ❌ Chyba při importu řádku: {e}")
                    errors += 1
        
        print(f"\n{'='*60}")
        print(f"📊 VÝSLEDKY IMPORTU")
        print(f"{'='*60}")
        print(f"✅ Importováno: {imported}")
        print(f"⚠️  Přeskočeno: {skipped}")
        print(f"❌ Chyby: {errors}")
        print(f"{'='*60}\n")
        
        return imported
        
    except FileNotFoundError:
        print(f"❌ Soubor nenalezen: {csv_file}")
        return 0
    except Exception as e:
        print(f"❌ Chyba při čtení CSV: {e}")
        import traceback
        traceback.print_exc()
        return 0


def create_sample_csv():
    """Vytvoří vzorový CSV soubor"""
    sample_file = 'data/contacts_sample.csv'
    
    with open(sample_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow(['name', 'phone', 'email', 'company'])
        
        # Sample data
        writer.writerow(['Jan Novák', '+420777123456', 'jan@example.com', 'Firma ABC'])
        writer.writerow(['Petra Svobodová', '+420606987654', 'petra@example.com', 'Firma XYZ'])
        writer.writerow(['Ondřej Hýža', '+420735744433', 'ondrej@example.com', 'Rožnovská Střední'])
    
    print(f"✅ Vytvořen vzorový CSV: {sample_file}")
    print(f"\nFormát CSV:")
    print(f"name,phone,email,company")
    print(f"Jan Novák,+420777123456,jan@example.com,Firma ABC")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        import_contacts_from_csv(csv_file)
    else:
        print("Použití: python utils/import_contacts_bulk.py <cesta_k_csv>")
        print("\nNebo vytvoř vzorový CSV:")
        create_sample_csv()