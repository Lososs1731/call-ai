"""
Testovaci rezim kampane - simuluje volani bez skutecneho hovoru

Pouziti:
    python -m cli.dry_run_campaign
"""

from services import ColdCallerService
from database import CallDB
from config import Prompts
import sys


def main():
    print("=" * 60)
    print("   DRY RUN - TESTOVACI KAMPAN")
    print("=" * 60)
    
    db = CallDB()
    
    # Vyber produktu
    products = db.get_all_products()
    
    if not products:
        print("\nŽádné produkty v databázi!")
        print("Spusť nejdřív: python -m utils.init_db")
        sys.exit(1)
    
    print("\nDostupné produkty:")
    for i, p in enumerate(products, 1):
        print(f"  {i}. {p['name']}")
    
    choice = int(input("\nVyber produkt (číslo): ")) - 1
    product = products[choice]
    
    # Ziskej kontakty
    contacts = db.get_contacts(status='new', limit=100)
    
    if not contacts:
        print("\nŽádné kontakty!")
        print("Spusť nejdřív: python -m utils.add_contacts")
        sys.exit(1)
    
    print(f"\n✓ Nalezeno {len(contacts)} kontaktů")
    
    # Simulace
    print("\n" + "=" * 60)
    print("SIMULACE HOVORŮ (bez skutečného volání)")
    print("=" * 60)
    
    for i, contact in enumerate(contacts[:5], 1):  # Prvnich 5
        print(f"\n[{i}] SIMULACE: {contact['name']} ({contact['phone']})")
        
        # Vygeneruj sales pitch
        sales_prompt = Prompts.get_sales_prompt(product, contact['name'])
        
        # Ukaz co AI rekne
        if contact.get('company'):
            greeting = f"Dobrý den, {contact['name']} z {contact['company']}, volám z Lososs Web Development."
        else:
            greeting = f"Dobrý den, {contact['name']}, volám z Lososs Web Development."
        
        print(f"\n  📞 AI POZDRAV:")
        print(f"  {greeting}")
        
        print(f"\n  🎯 SALES PITCH:")
        pitch_preview = product['pitch'][:200] + "..." if len(product['pitch']) > 200 else product['pitch']
        print(f"  {pitch_preview}")
        
        print(f"\n  🎯 CÍL: Zjistit zájem o {product['name']}")
        
        answer = input("\n  [Enter pro další / 'q' pro ukončení]: ")
        if answer.lower() == 'q':
            break
    
    print("\n" + "=" * 60)
    print("DRY RUN DOKONČEN")
    print("=" * 60)
    print("\nPokud je vše OK, spusť skutečnou kampaň:")
    print("  python -m cli.run_campaign")


if __name__ == "__main__":
    main()