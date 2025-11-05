"""
Cold Calling Engine
Automaticke odchozi hovory na kontakty z databaze
"""

from twilio.rest import Client
from config import Config, CallConfig
from database import CallDB
from datetime import datetime
import time

class ColdCaller:
    """System pro cold calling kampane"""
    
    def __init__(self, campaign_name, product_name):
        self.twilio = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        self.db = CallDB()
        self.campaign = campaign_name
        self.product = product_name
        
        print(f"Cold Caller pripraven")
        print(f"Kampan: {campaign_name}")
        print(f"Produkt: {product_name}")
    
    def call_contact(self, contact):
        """Zavola jeden kontakt"""
        try:
            print(f"\nVolam: {contact['name']} ({contact['phone']})")
            
            # POZOR: Tady zmen URL na tvou ngrok URL!
            base_url = "https://your-ngrok-url.ngrok-free.app"
            webhook = f"{base_url}/outbound?name={contact['name']}&company={contact.get('company', '')}"
            
            # Uskutecneni hovoru
            call = self.twilio.calls.create(
                to=contact['phone'],
                from_=Config.TWILIO_PHONE_NUMBER,
                url=webhook,
                status_callback=f"{base_url}/call-status",
                status_callback_event=['completed'],
                record=True,
                timeout=30
            )
            
            # Ulozeni do DB
            self.db.add_call({
                'sid': call.sid,
                'type': 'outbound',
                'direction': 'outbound',
                'phone': contact['phone']
            })
            
            # Update kontaktu
            self.db.update_contact(contact['phone'], {
                'last_call': datetime.now().isoformat(),
                'call_count': contact.get('call_count', 0) + 1,
                'status': 'contacted'
            })
            
            print(f"Hovor zahajen: {call.sid}")
            return {'success': True, 'sid': call.sid}
            
        except Exception as e:
            print(f"Chyba: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_campaign(self, max_calls=None):
        """Spusti kampan"""
        print(f"\nSpoustim kampan: {self.campaign}")
        print("=" * 50)
        
        contacts = self.db.get_contacts(status='new', limit=max_calls or 1000)
        
        if not contacts:
            print("Zadne kontakty")
            return
        
        print(f"Kontaktu: {len(contacts)}")
        
        made = 0
        success = 0
        
        for contact in contacts:
            if not self._can_call():
                print("Mimo volaci dobu")
                break
            
            result = self.call_contact(contact)
            
            if result['success']:
                made += 1
                success += 1
            
            # Pauza mezi hovory
            if made < len(contacts):
                wait = 60 / CallConfig.CALLS_PER_MINUTE
                print(f"Cekam {wait:.0f}s...")
                time.sleep(wait)
        
        print("\n" + "=" * 50)
        print(f"Kampan ukoncena")
        print(f"Hovoru: {made}")
        print(f"Uspesnych: {success}")
    
    def _can_call(self):
        """Kontrola volaci doby"""
        now = datetime.now()
        
        if now.weekday() not in CallConfig.WORK_DAYS:
            return False
        
        if not (CallConfig.START_HOUR <= now.hour < CallConfig.END_HOUR):
            return False
        
        return True


if __name__ == "__main__":
    # Priklad pouziti
    caller = ColdCaller(
        campaign_name="Demo Kampan",
        product_name="AI Assistant"
    )
    
    caller.run_campaign(max_calls=3)