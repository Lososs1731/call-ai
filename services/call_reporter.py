"""
AI Call Reporter - vyhodnocení hovorů
"""

from openai import OpenAI
from config import Config
import json


class CallReporter:
    """AI vyhodnocení hovorů"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def analyze_call(self, call_sid: str, conversation: list) -> dict:
        """Vyhodnoť hovor pomocí AI"""
        
        print(f"\n[CallReporter] analyze_call({call_sid})")
        print(f"  Konverzace: {len(conversation)} zpráv")
        
        if len(conversation) < 2:
            return {'error': 'Conversation too short'}
        
        # Vytvoř transcript
        transcript = "\n".join([
            f"{'BOT' if msg['role'] == 'assistant' else 'ZÁKAZNÍK'}: {msg['content']}"
            for msg in conversation if msg['role'] in ['user', 'assistant']
        ])
        
        print(f"  Transcript délka: {len(transcript)} znaků")
        
        # AI analýza
        prompt = f"""Analyzuj tento prodejní hovor a vyhodnoť ho:

TRANSCRIPT:
{transcript}

Odpověz VE FORMÁTU JSON (pouze JSON, žádný další text!):
{{
    "outcome": "success/no_interest/callback/no_answer",
    "sales_score": 0-100,
    "got_email": true/false,
    "got_phone": true/false,
    "scheduled_callback": true/false,
    "objections_count": 0,
    "positive_signals": 0,
    "ai_summary": "Stručné shrnutí co se stalo",
    "ai_recommendations": "Co zlepšit příště",
    "what_worked": "Co fungovalo dobře",
    "what_failed": "Co selhalo nebo se dalo udělat lépe"
}}

PRAVIDLA:
- "success" = získán email/telefon NEBO domluvena schůzka
- "callback" = zákazník chce být kontaktován později
- "no_interest" = jasné odmítnutí
- sales_score: 0-100 (100 = perfektní prodej)
- objections_count = kolikrát zákazník řekl námitku
- positive_signals = pozitivní fráze ("ano", "zajímá mě", "pošlete")
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            print(f"  ✅ AI analýza dokončena:")
            print(f"     Outcome: {result.get('outcome')}")
            print(f"     Score: {result.get('sales_score')}/100")
            
            return result
            
        except Exception as e:
            print(f"  ❌ AI analýza selhala: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}