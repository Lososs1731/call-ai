"""
Bulk Cold Calling
Rychlé spuštění 200 callů

Použití:
    python bulk_call_kb.py
"""

from twilio.rest import Client
from database import CallDB
import os
from dotenv import load_dotenv
import time
from urllib.parse import urlencode  # ✅ PŘIDÁNO!

load_dotenv()

def main():
    print("=" * 60)
    print("   BULK CALLING")
    print("=" * 60)
    
    # Config
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER]):
        print("\n❌ CHYBA: Chybí Twilio credentials v .env!")
        return
    
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    # Ngrok URL
    ngrok_url = input("\nZadej ngrok URL (https://...): ").strip().rstrip('/')
    
    if not ngrok_url.startswith('https://'):
        print("❌ CHYBA: URL musí začínat https://")
        return
    
    # ✅ TEST dostupnosti
    print(f"\n🔍 Testuji server...")
    import requests
    try:
        response = requests.get(f"{ngrok_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Server běží!")
        else:
            print(f"   ⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Server není dostupný: {e}")
        cont = input("\nPokračovat? (ano/ne): ").strip().lower()
        if cont not in ['ano', 'a', 'yes', 'y']:
            return
    
    # Načti kontakty
    db = CallDB()
    
    max_calls_input = input("\nKolik callů? (1-200): ").strip() or "1"
    
    try:
        max_calls = int(max_calls_input)
        if max_calls < 1 or max_calls > 200:
            raise ValueError()
    except ValueError:
        print("❌ CHYBA: Zadej číslo mezi 1 a 200")
        return
    
    contacts = db.get_contacts(status='new', limit=max_calls)
    
    if not contacts:
        print("\n❌ CHYBA: Žádné kontakty!")
        print("Spusť: python -m utils.import_contacts data/contacts.csv")
        return
    
    print(f"\n📊 Kontaktů: {len(contacts)}")
    print(f"📞 Twilio: {TWILIO_NUMBER}")
    print(f"🌐 Webhook: {ngrok_url}")
    
    # Preview
    print("\nKontakty:")
    for i, c in enumerate(contacts[:5], 1):
        print(f"  {i}. {c['name']} - {c['phone']}")
    if len(contacts) > 5:
        print(f"  ... a dalších {len(contacts) - 5}")
    
    # Potvrzení
    confirm = input(f"\nSpustit {len(contacts)} callů? (ano/ne): ").strip().lower()
    
    if confirm not in ['ano', 'a', 'yes', 'y']:
        print("Zrušeno")
        return
    
    print("\n" + "=" * 60)
    print("📞 SPOUŠTÍM HOVORY...")
    print("=" * 60 + "\n")
    
    success = 0
    failed = 0
    
    for i, contact in enumerate(contacts, 1):
        name = contact['name']
        phone = contact['phone']
        company = contact.get('company', '')
        
        print(f"[{i}/{len(contacts)}] {name} ({phone})...", end=' ', flush=True)
        
        try:
            # URL ENCODING
            params = urlencode({
                'name': name,
                'company': company
            })
            
            webhook_url = f"{ngrok_url}/outbound?{params}"
            
            # Vytvoř hovor
            call = client.calls.create(
                to=phone,
                from_=TWILIO_NUMBER,
                url=webhook_url,  # ✅ URL-encoded!
                method='POST',
                status_callback=f"{ngrok_url}/call-status",
                status_callback_event=['completed'],
                status_callback_method='POST'
            )
            
            print(f"✅ {call.sid[:20]}...")
            success += 1
            
            # Update DB
            try:
                db.cursor.execute("""
                    UPDATE contacts 
                    SET status = 'called', last_called = datetime('now')
                    WHERE id = ?
                """, (contact['id'],))
                db.conn.commit()
            except:
                pass
            
            # Delay
            if i < len(contacts):
                time.sleep(2)
            
        except Exception as e:
            print(f"❌ {str(e)[:50]}...")
            failed += 1
    
    # Výsledky
    print(f"\n{'='*60}")
    print(f"HOTOVO!")
    print(f"{'='*60}")
    print(f"✅ Úspěšné: {success}")
    print(f"❌ Selhané: {failed}")
    print(f"📊 Celkem: {success + failed}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Přerušeno (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ CHYBA: {e}")
        import traceback
        traceback.print_exc()