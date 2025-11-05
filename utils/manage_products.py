"""
Sprava produktu v databazi

Pouziti:
    python -m utils.manage_products
"""

from database import CallDB
import sys


def list_products(db):
    """Vypise vsechny produkty"""
    products = db.get_all_products()
    
    if not products:
        print("Zadne produkty v databazi")
        return
    
    print("\n" + "=" * 60)
    print("PRODUKTY V DATABAZI")
    print("=" * 60)
    
    for i, product in enumerate(products, 1):
        print(f"\n{i}. {product['name']}")
        print(f"   {product['description']}")
        print(f"   Pitch: {product['pitch'][:100]}...")


def add_product(db):
    """Prida novy produkt"""
    print("\n" + "=" * 60)
    print("PRIDANI NOVEHO PRODUKTU")
    print("=" * 60)
    
    name = input("\nNazev produktu: ").strip()
    if not name:
        print("CHYBA: Nazev je povinny")
        return
    
    description = input("Strucny popis (1 veta): ").strip()
    
    print("\nSales pitch (vice radku, ukonci prazdnym radkem):")
    pitch_lines = []
    while True:
        line = input()
        if not line:
            break
        pitch_lines.append(line)
    
    pitch = '\n'.join(pitch_lines)
    
    benefits = input("\nBenefity (oddelene carkou): ").strip()
    target = input("Cilova skupina: ").strip()
    
    price_from = input("Cena od (Kc, enter = preskocit): ").strip()
    price_to = input("Cena do (Kc, enter = preskocit): ").strip()
    
    # Ulozeni
    data = {
        'name': name,
        'description': description,
        'pitch': pitch,
        'benefits': benefits,
        'target_audience': target,
        'price_from': int(price_from) if price_from else None,
        'price_to': int(price_to) if price_to else None
    }
    
    if db.add_product(data):
        print(f"\n✓ Produkt '{name}' pridan")
    else:
        print(f"\n✗ Produkt '{name}' uz existuje")


def main():
    db = CallDB()
    
    while True:
        print("\n" + "=" * 60)
        print("SPRAVA PRODUKTU")
        print("=" * 60)
        print("1. Vypsat produkty")
        print("2. Pridat produkt")
        print("3. Ukoncit")
        
        choice = input("\nVolba: ").strip()
        
        if choice == '1':
            list_products(db)
        elif choice == '2':
            add_product(db)
        elif choice == '3':
            break
        else:
            print("Neplatna volba")


if __name__ == "__main__":
    main()