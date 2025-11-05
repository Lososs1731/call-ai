"""
AI Call Reporter - vyhodnocuje úspěšnost hovorů
"""

import openai
from config import Config
from database import CallDB
import json


class CallReporter:
    """Generuje AI report z hovoru"""
    
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.db = CallDB()
    
    def analyze_call(self, call_sid):
        """Analyzuje hovor a vrací report"""
        
        print(f"\n{'='*60}")
        print(f"🤖 AI CALL REPORTER")
        print(f"{'='*60}")
        print(f"Call SID: {call_sid}")
        
        # Získej konverzaci
        from services import ReceptionistService
        receptionist = ReceptionistService()
        
        if call_sid not in receptionist.ai.conversations:
            print(f"❌ Konverzace nenalezena")
            return {'error': 'Conversation not found'}
        
        messages = receptionist.ai.conversations[call_sid]
        
        # Přepis
        transcript_parts = []
        
        for msg in messages:
            if msg['role'] == 'system':
                continue
            
            role = "🤖 BOT" if msg['role'] == 'assistant' else "👤 ZÁKAZNÍK"
            transcript_parts.append(f"{role}: {msg['content']}")
        
        transcript = "\n".join(transcript_parts)
        
        if not transcript:
            print(f"❌ Prázdný přepis")
            return {'error': 'Empty transcript'}
        
        print(f"\n📝 Přepis ({len(transcript)} znaků)")
        
        # AI prompt
        prompt = f"""Jsi expert na vyhodnocování prodejních hovorů.

Analyzuj tento telefonní hovor a vyhodnoť jeho úspěšnost.

PŘEPIS HOVORU:
{transcript}

ÚKOL:
Vygeneruj JSON report:

{{
    "success_rate": 0-100,
    "classification": "success" | "lead" | "no_interest" | "unclear",
    "summary": "Stručný souhrn v 2-3 větách",
    "feedback": "Konstruktivní zpětná vazba",
    "key_points": ["Bod 1", "Bod 2"],
    "next_action": "Doporučený další krok",
    "objections": ["Námitka 1"],
    "mood": "positive" | "neutral" | "negative",
    "will_buy": "yes" | "maybe" | "no",
    "strengths": ["Síla 1", "Síla 2"],
    "weaknesses": ["Slabost 1"]
}}

KRITÉRIA:
- 80-100%: Konkrétní zájem, schůzka/email/callback
- 60-79%: Potenciální zájem, follow-up
- 40-59%: Nejasný zájem
- 20-39%: Slabý zájem
- 0-19%: Odmítnutí

KLASIFIKACE:
- success: Dohodnutá schůzka, email, termín
- lead: Potenciální zájem, follow-up
- no_interest: Odmítnutí
- unclear: Nelze určit

Odpověz POUZE validním JSON!
"""
        
        try:
            print(f"\n🤖 Volám OpenAI API...")
            
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Jsi expert na analýzu prodejních hovorů. Odpovídáš POUZE JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            print(f"\n✅ AI analýza dokončena")
            
            # Ulož do DB
            self._save_report(call_sid, result, transcript)
            
            # Vytiskni report
            self._print_report(result)
            
            return result
            
        except Exception as e:
            print(f"\n❌ Chyba při AI analýze: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}
    
    def _save_report(self, call_sid, report, transcript):
        """Uloží report do databáze"""
        try:
            # Přidej sloupce pokud neexistují
            try:
                self.db.cursor.execute("""
                    UPDATE calls 
                    SET 
                        classification = ?,
                        summary = ?,
                        ai_score = ?,
                        success = ?,
                        metadata = ?,
                        transcript = ?
                    WHERE sid = ?
                """, (
                    report.get('classification'),
                    report.get('summary'),
                    report.get('success_rate'),
                    1 if report.get('success_rate', 0) >= 60 else 0,
                    json.dumps(report, ensure_ascii=False),
                    transcript,
                    call_sid
                ))
                self.db.conn.commit()
                
                print(f"✅ Report uložen do databáze")
                
            except Exception as e:
                print(f"⚠️  DB update error (možná chybí sloupce): {e}")
            
        except Exception as e:
            print(f"⚠️  Nepodařilo se uložit report: {e}")
    
    def _print_report(self, report):
        """Vytiskne formátovaný report"""
        print(f"\n{'='*60}")
        print(f"📊 VYHODNOCENÍ HOVORU")
        print(f"{'='*60}")
        
        # Success rate
        success = report.get('success_rate', 0)
        bar_length = 40
        filled = int(bar_length * success / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f"\n🎯 ÚSPĚŠNOST: {success}%")
        print(f"   [{bar}]")
        
        print(f"\n📌 KLASIFIKACE: {report.get('classification', 'N/A').upper()}")
        print(f"🎭 NÁLADA: {report.get('mood', 'N/A')}")
        print(f"💰 KOUPÍ?: {report.get('will_buy', 'N/A')}")
        
        print(f"\n📝 SOUHRN:")
        print(f"   {report.get('summary', 'N/A')}")
        
        if report.get('key_points'):
            print(f"\n🔑 KLÍČOVÉ BODY:")
            for point in report['key_points']:
                print(f"   • {point}")
        
        if report.get('objections'):
            print(f"\n⚠️  NÁMITKY:")
            for obj in report['objections']:
                print(f"   • {obj}")
        
        if report.get('strengths'):
            print(f"\n✅ CO BYLO DOBRÉ:")
            for strength in report['strengths']:
                print(f"   • {strength}")
        
        if report.get('weaknesses'):
            print(f"\n⚡ CO ZLEPŠIT:")
            for weakness in report['weaknesses']:
                print(f"   • {weakness}")
        
        print(f"\n💬 FEEDBACK:")
        print(f"   {report.get('feedback', 'N/A')}")
        
        print(f"\n👉 DALŠÍ KROK:")
        print(f"   {report.get('next_action', 'N/A')}")
        
        print(f"\n{'='*60}\n")