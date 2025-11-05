"""
Smart Cold Caller - Production Ready
Error handling, retry, timeout, statistics
"""

from twilio.rest import Client
from datetime import datetime
import time

from core import AIEngine
from config import Config, CallConfig
from database import CallDB


class SmartColdCaller:
    """Inteligentní cold calling"""
    
    def __init__(self, campaign_name, product_name=None):
        self.twilio = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        self.ai = AIEngine()
        self.db = CallDB()
        self.campaign = campaign_name
        
        # Produkt
        if product_name:
            self.product = self.db.get_product_by_name(product_name)
        else:
            self.product = self.db.get_product_by_name("Tvorba webů na míru")
        
        if not self.product:
            raise ValueError(f"Produkt '{product_name}' nenalezen!")
        
        # Statistiky
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'busy': 0,
            'no_answer': 0,
            'errors': []
        }
        
        print(f"\n{'='*60}")
        print(f"🤖 SMART COLD CALLER - PRODUCTION")
        print(f"{'='*60}")
        print(f"Kampaň: {campaign_name}")
        print(f"Produkt: {self.product['name']}")
        print(f"{'='*60}\n")
    
    def call_contact(self, contact, webhook_base_url, retry=0):
        """Zavolá kontakt s error handling"""
        
        max_retries = 2
        
        try:
            print(f"\n{'='*60}")
            print(f"📞 VOLÁM [{self.stats['total'] + 1}]")
            print(f"{'='*60}")
            print(f"Jméno: {contact['name']}")
            print(f"Telefon: {contact['phone']}")
            if contact.get('company'):
                print(f"Firma: {contact['company']}")
            if retry > 0:
                print(f"⚠️  RETRY pokus #{retry}")
            
            # Webhook
            base_url = webhook_base_url.rstrip('/')
            
            import urllib.parse
            params = urllib.parse.urlencode({
                'name': contact['name'],
                'company': contact.get('company', ''),
                'product_id': self.product['id'],
                'campaign': self.campaign
            })
            
            webhook = f"{base_url}/outbound?{params}"
            status_callback = f"{base_url}/call-status"
            
            print(f"📡 Volám Twilio API...")
            
            # ⭐ ZAVOLAT S TIMEOUT!
            call = self.twilio.calls.create(
                to=contact['phone'],
                from_=Config.TWILIO_PHONE_NUMBER,
                url=webhook,
                status_callback=status_callback,
                status_callback_event=['completed', 'failed', 'busy', 'no-answer'],
                record=CallConfig.RECORD_CALLS,
                timeout=30,
                time_limit=300,  # ⭐ MAX 5 MINUT!
                machine_detection='DetectMessageEnd',
                machine_detection_timeout=5
            )
            
            print(f"✅ Hovor zahájen!")
            print(f"   SID: {call.sid}")
            print(f"   Status: {call.status}")
            
            # DB
            self.db.add_call({
                'sid': call.sid,
                'type': 'outbound',
                'direction': 'outbound',
                'phone': contact['phone'],
                'status': call.status
            })
            
            self.db.update_contact(contact['phone'], {
                'last_call': datetime.now().isoformat(),
                'call_count': contact.get('call_count', 0) + 1,
                'status': 'contacted'
            })
            
            self.stats['total'] += 1
            self.stats['success'] += 1
            
            print(f"{'='*60}\n")
            
            return {'success': True, 'sid': call.sid}
            
        except Exception as e:
            error_msg = str(e)
            
            print(f"\n❌ CHYBA: {error_msg}")
            
            # Retry
            if retry < max_retries:
                print(f"⏳ Zkusím znovu za 5s... ({retry + 1}/{max_retries})")
                time.sleep(5)
                return self.call_contact(contact, webhook_base_url, retry + 1)
            else:
                print(f"❌ Selhalo i po {max_retries} pokusech")
                
                self.stats['failed'] += 1
                self.stats['errors'].append({
                    'phone': contact['phone'],
                    'error': error_msg
                })
                
                self.db.update_contact(contact['phone'], {
                    'status': 'failed',
                    'notes': f"Chyba: {error_msg}"
                })
                
                return {'success': False, 'error': error_msg}
    
    def run_campaign(self, webhook_base_url, max_calls=None):
        """Spustí kampaň"""
        
        print(f"\n{'='*80}")
        print(f"🚀 KAMPAŇ: {self.campaign}")
        print(f"{'='*80}")
        
        # Načti kontakty
        contacts = self.db.get_contacts(status='new', limit=max_calls or 10000)
        
        if not contacts:
            print("❌ Žádné nové kontakty")
            return
        
        total_contacts = len(contacts)
        
        print(f"📊 Kontaktů: {total_contacts}")
        print(f"🎯 Produkt: {self.product['name']}")
        print(f"⏰ Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")
        
        # Obvolávání
        for i, contact in enumerate(contacts, 1):
            
            # Kontrola volací doby
            if not self._can_call():
                print(f"\n⏰ MIMO VOLACÍ DOBU - ukončuji")
                break
            
            # Progress
            progress = (i / total_contacts) * 100
            print(f"\n📈 PROGRESS: {i}/{total_contacts} ({progress:.1f}%)")
            
            # Zavolej
            result = self.call_contact(contact, webhook_base_url)
            
            # Pauza
            if i < total_contacts:
                wait_time = 60 / CallConfig.CALLS_PER_MINUTE
                print(f"⏳ Čekám {wait_time:.0f}s...")
                time.sleep(wait_time)
        
        # Report
        self._print_final_report()
    
    def _can_call(self):
        """Kontrola volací doby"""
        now = datetime.now()
        
        if now.weekday() not in CallConfig.WORK_DAYS:
            return False
        
        if not (CallConfig.START_HOUR <= now.hour < CallConfig.END_HOUR):
            return False
        
        return True
    
    def _print_final_report(self):
        """Finální report"""
        
        print(f"\n{'='*80}")
        print(f"📊 FINÁLNÍ REPORT KAMPANĚ")
        print(f"{'='*80}")
        print(f"Kampaň: {self.campaign}")
        print(f"Ukončeno: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n📞 HOVORY:")
        print(f"   Celkem pokusů: {self.stats['total']}")
        print(f"   ✅ Úspěšné: {self.stats['success']}")
        print(f"   ❌ Selhané: {self.stats['failed']}")
        
        if self.stats['total'] > 0:
            success_rate = (self.stats['success'] / self.stats['total']) * 100
            print(f"   📈 Úspěšnost volání: {success_rate:.1f}%")
        
        if self.stats['errors']:
            print(f"\n❌ CHYBY ({len(self.stats['errors'])}):")
            for err in self.stats['errors'][:10]:
                print(f"   • {err['phone']}: {err['error']}")
            
            if len(self.stats['errors']) > 10:
                print(f"   ... a {len(self.stats['errors']) - 10} dalších")
        
        print(f"\n💡 ZOBRAZ AI REPORTY:")
        print(f"   python cli/show_reports.py")
        print(f"{'='*80}\n")