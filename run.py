"""
Hlavni spoustec AI Telefonniho Asistenta
"""

import sys
from pyngrok import ngrok
from config import Config
import subprocess


def main():
    print("=" * 60)
    print("   AI TELEFONNI ASISTENT")
    print("   Maturitni projekt - Lososs1731")
    print("=" * 60)
    
    # Kontrola konfigurace
    if not Config.TWILIO_ACCOUNT_SID:
        print("\nCHYBA: Chybi TWILIO_ACCOUNT_SID v .env")
        sys.exit(1)
    
    # Spusteni ngrok
    print("\nSpoustim ngrok tunnel...")
    try:
        public_url = ngrok.connect(Config.SERVER_PORT)
        print(f"✓ Ngrok URL: {public_url}")
        
        print(f"\n{'='*60}")
        print("NASTAVENI TWILIO:")
        print(f"{'='*60}")
        print(f"1. Jdi na:")
        print(f"   https://console.twilio.com/us1/develop/phone-numbers/manage/incoming")
        print(f"\n2. Klikni na sve cislo: {Config.TWILIO_PHONE_NUMBER}")
        print(f"\n3. V 'Voice Configuration' nastav:")
        print(f"   A CALL COMES IN:")
        print(f"     - Webhook")
        print(f"     - {public_url}/inbound")
        print(f"     - HTTP POST")
        print(f"\n4. Klikni 'Save'")
        print(f"\n5. Zavolej na: {Config.TWILIO_PHONE_NUMBER}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"CHYBA ngrok: {e}")
        sys.exit(1)
    
    # Spusteni Flask serveru
    print("Spoustim server...\n")
    try:
        subprocess.run([sys.executable, "-m", "api.server"])
    except KeyboardInterrupt:
        print("\n\nUkonceno")
        ngrok.disconnect(public_url)


if __name__ == "__main__":
    main()