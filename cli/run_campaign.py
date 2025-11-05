"""
Spusteni cold calling kampane z prikazove radky

Pouziti:
    python -m cli.run_campaign
"""

from services import ColdCallerService
from database import CallDB
import sys


def main():
    print("=" * 60)
    print("   COLD CALLING - SPUSTENI KAMPANE")
    print("=" * 60)
    
    # Inicializace DB
    db = CallDB()
    
    # 1. Vyber produktu
    print("\nDostupne produkty:")
    products = db.get_all_products()
    
    if not products:
        print("CHYBA: Zadne produkty v databazi!")
        print("Vytvaram defaultni produkt...")
        db._init_default_product()
        products = db.get_all_products()
    
    for i, product in enumerate(products, 1):
        print(f"  {i}. {product['name']}")
        print(f"     {product['description']}")
    
    product_choice = input(f"\nVyber produkt (1-{len(products)}): ").strip()
    
    try:
        product_idx = int(product_choice) - 1
        selected_product = products[product_idx]['name']
    except (ValueError, IndexError):
        print("CHYBA: Neplatna volba")
        sys.exit(1)
    
    print(f"\n✓ Vybran produkt: {selected_product}")
    
    # 2. Ziskani ngrok URL
    print("\n" + "=" * 60)
    print("NASTAVENI WEBHOOku")
    print("=" * 60)
    print("1. Ujisti se, ze mas spusteny server (python run.py)")
    print("2. Zkopiruj ngrok URL z terminu serveru")
    
    ngrok_url = input("\nZadej ngrok URL (https://...): ").strip()
    
    if not ngrok_url.startswith('https://'):
        print("CHYBA: URL musi zacinat https://")
        sys.exit(1)
    
    # 3. Kontrola kontaktu
    contacts = db.get_contacts(status='new', limit=100)
    
    if not contacts:
        print("\n" + "=" * 60)
        print("CHYBA: Zadne kontakty v databazi!")
        print("=" * 60)
        print("\nSpust nejprve:")
        print("  python -m utils.import_contacts data/contacts.csv")
        print("\nNebo vytvor soubor data/contacts.csv s obsahem:")
        print("  name,phone,company,email")
        print("  Jan Novak,+420777111222,Firma s.r.o.,jan@email.cz")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("KONTAKTY K ZAVOLANI")
    print("=" * 60)
    print(f"\nNalezeno {len(contacts)} kontaktu:")
    for i, contact in enumerate(contacts[:5], 1):
        print(f"  {i}. {contact['name']} - {contact['phone']}")
        if contact.get('company'):
            print(f"     {contact['company']}")
    if len(contacts) > 5:
        print(f"  ... a dalsich {len(contacts) - 5}")
    
    # 4. Kolik hovoru
    max_calls = input(f"\nKolik hovoru chces uskutecnit? (max {len(contacts)}): ").strip()
    
    try:
        max_calls = int(max_calls)
        if max_calls < 1 or max_calls > len(contacts):
            raise ValueError()
    except ValueError:
        print("CHYBA: Zadej cislo mezi 1 a", len(contacts))
        sys.exit(1)
    
    # 5. Potvrzeni
    print("\n" + "=" * 60)
    print("POTVRZENI")
    print("=" * 60)
    print(f"Produkt: {selected_product}")
    print(f"Pocet hovoru: {max_calls}")
    print(f"Kontakty: {', '.join([c['name'] for c in contacts[:max_calls]])}")
    
    confirm = input(f"\nOpravdu spustit kampan? (ano/ne): ").strip().lower()
    
    if confirm not in ['ano', 'a', 'yes', 'y']:
        print("Zruseno")
        sys.exit(0)
    
    # 6. Nazev kampane
    campaign_name = input("\nNazev kampane: ").strip() or f"Kampan {selected_product}"
    
    # 7. Vytvoreni a spusteni kampane
    print("\n" + "=" * 60)
    print("SPOUSTIM KAMPAN...")
    print("=" * 60)
    
    try:
        caller = ColdCallerService(
            campaign_name=campaign_name,
            product_name=selected_product
        )
        
        caller.run_campaign(
            webhook_base_url=ngrok_url,
            max_calls=max_calls
        )
        
    except Exception as e:
        print(f"\nCHYBA: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # 8. Vysledky
    print("\n" + "=" * 60)
    print("KAMPAN DOKONCENA!")
    print("=" * 60)
    
    # Statistiky
    stats = db.get_stats()
    print(f"\nCelkove statistiky:")
    print(f"  Prichozi hovory: {stats.get('inbound', 0)}")
    print(f"  Odchozi hovory: {stats.get('outbound', 0)}")
    print(f"  Celkem: {sum(stats.values())}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nKampan prerusena uzivatelem")
        sys.exit(0)
    except Exception as e:
        print(f"\nNEOCEKAVANA CHYBA: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)