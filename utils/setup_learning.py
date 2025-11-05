"""
Nastavení Auto-Learning systému
"""

import os
import json


def setup_learning():
    """Vytvoří potřebné soubory a složky pro learning"""
    
    print("🔧 Nastavuji Auto-Learning systém...\n")
    
    # Vytvoř data složku
    os.makedirs('data', exist_ok=True)
    print("✅ Složka data/ vytvořena")
    
    # Vytvoř learned_prompts.json
    learned_file = 'data/learned_prompts.json'
    
    if not os.path.exists(learned_file):
        initial_data = {
            'version': 1,
            'learned_patterns': [],
            'successful_phrases': [
                # Základní fráze které fungují
                "Dobrý den, volám ohledně možnosti vytvořit vám moderní webové stránky.",
                "Můžu vám poslat cenovou nabídku emailem?",
                "Kdy by vám vyhovovalo si o tom více popovídat?",
                "Máme speciální nabídku pro nové zákazníky.",
                "Reference našich klientů najdete na našem webu."
            ],
            'best_practices': [
                "Být konkrétní a stručný",
                "Nabídnout email nebo schůzku",
                "Reagovat na námitky pozitivně",
                "Ukončit s jasným dalším krokem"
            ],
            'stats': {
                'total_learned_calls': 0,
                'last_learning': None
            }
        }
        
        with open(learned_file, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Soubor {learned_file} vytvořen s výchozími daty")
    else:
        print(f"⚠️  Soubor {learned_file} už existuje - ponechán")
    
    # Zkontroluj permissions
    try:
        with open(learned_file, 'r') as f:
            data = json.load(f)
        print(f"✅ Soubor je čitelný")
        
        with open(learned_file, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Soubor je zapisovatelný")
        
    except Exception as e:
        print(f"❌ Chyba permissions: {e}")
        return False
    
    print("\n✅ Auto-Learning systém READY!")
    print(f"\nSoubor: {os.path.abspath(learned_file)}")
    print(f"Výchozích frází: {len(initial_data['successful_phrases'])}")
    
    return True


if __name__ == "__main__":
    setup_learning()