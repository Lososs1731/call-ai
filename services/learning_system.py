"""
Learning System - Učí se z úspěšných hovorů a vylepšuje prompty
"""

import openai
from config import Config, Prompts
from database import CallDB
import json
import os


class LearningSystem:
    """Systém pro učení z úspěšných hovorů"""
    
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.db = CallDB()
        self.learned_prompts_file = 'data/learned_prompts.json'
        self._ensure_file()
    
    def _ensure_file(self):
        """Vytvoří soubor pro learned prompts pokud neexistuje"""
        if not os.path.exists(self.learned_prompts_file):
            os.makedirs(os.path.dirname(self.learned_prompts_file), exist_ok=True)
            with open(self.learned_prompts_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'version': 1,
                    'learned_patterns': [],
                    'successful_phrases': [],
                    'best_practices': []
                }, f, ensure_ascii=False, indent=2)
    
    def learn_from_call(self, call_sid, report):
        """
        Učí se z úspěšného hovoru
        
        Args:
            call_sid: ID hovoru
            report: AI report z call_reporter
        """
        
        print(f"\n{'='*60}")
        print(f"🧠 LEARNING SYSTEM - ANALYZING CALL")
        print(f"{'='*60}")
        print(f"Call SID: {call_sid}")
        print(f"Success rate: {report.get('success_rate', 0)}%")
        
        # Získej konverzaci
        from services import ReceptionistService
        receptionist = ReceptionistService()
        
        if call_sid not in receptionist.ai.conversations:
            print(f"❌ Konverzace nenalezena")
            return
        
        messages = receptionist.ai.conversations[call_sid]
        
        # Sestav přepis (jen assistant zprávy)
        bot_messages = [
            msg['content'] for msg in messages 
            if msg['role'] == 'assistant' and not msg['content'].startswith('CALL_START_TIME')
        ]
        
        if not bot_messages:
            print(f"❌ Žádné bot zprávy")
            return
        
        print(f"📝 Bot zpráv: {len(bot_messages)}")
        
        # AI analýza - co fungovalo
        try:
            analysis = self._analyze_successful_patterns(bot_messages, report)
            
            if analysis:
                print(f"✅ Analýza dokončena")
                
                # Ulož learned patterns
                self._save_patterns(analysis)
                
                print(f"✅ Patterns uloženy")
                print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"❌ Learning error: {e}")
            import traceback
            traceback.print_exc()
    
    def _analyze_successful_patterns(self, bot_messages, report):
        """Analyzuje co fungovalo v úspěšném hovoru"""
        
        print(f"  🤖 Analyzuji úspěšné vzorce...")
        
        prompt = f"""Analyzuj tento ÚSPĚŠNÝ prodejní hovor (úspěšnost {report.get('success_rate')}%).

BOT ZPRÁVY:
{chr(10).join([f"- {msg}" for msg in bot_messages])}

AI FEEDBACK:
{report.get('feedback', 'N/A')}

CO BYLO DOBRÉ:
{chr(10).join([f"- {s}" for s in report.get('strengths', [])])}

ÚKOL:
Identifikuj konkrétní FRÁZE a PŘÍSTUPY které vedly k úspěchu.

Vrať JSON:
{{
    "successful_phrases": ["fráze 1", "fráze 2", ...],
    "effective_approach": "Popis přístupu který fungoval",
    "key_moments": ["moment 1", "moment 2", ...],
    "avoid": ["co nedělat"]
}}

Odpověz POUZE validním JSON!
"""
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Jsi expert na analýzu prodejních hovorů. Odpovídáš POUZE JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        analysis = json.loads(response.choices[0].message.content)
        
        print(f"  ✅ Learned patterns:")
        for phrase in analysis.get('successful_phrases', [])[:3]:
            print(f"     • {phrase}")
        
        return analysis
    
    def _save_patterns(self, analysis):
        """Uloží learned patterns do souboru"""
        
        # Načti existující
        with open(self.learned_prompts_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Přidej nové
        data['learned_patterns'].append({
            'timestamp': os.times().elapsed,
            'analysis': analysis
        })
        
        # Updatuj successful phrases (bez duplikátů)
        for phrase in analysis.get('successful_phrases', []):
            if phrase not in data['successful_phrases']:
                data['successful_phrases'].append(phrase)
        
        # Best practices
        if analysis.get('effective_approach'):
            data['best_practices'].append(analysis['effective_approach'])
        
        # Ulož
        with open(self.learned_prompts_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_optimized_prompt(self, product, contact_name):
        """
        Vrátí optimalizovaný prompt na základě learned patterns
        
        Args:
            product: Produkt z databáze
            contact_name: Jméno kontaktu
            
        Returns:
            str: Optimalizovaný sales prompt
        """
        
        # Načti learned patterns
        try:
            with open(self.learned_prompts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            # Fallback na default
            return Prompts.get_sales_prompt(product, contact_name)
        
        # Pokud nemáme patterns, použij default
        if not data.get('successful_phrases'):
            return Prompts.get_sales_prompt(product, contact_name)
        
        # Jinak vytvoř enhanced prompt
        base_prompt = Prompts.get_sales_prompt(product, contact_name)
        
        # Přidej learned patterns
        enhancement = f"""

⭐ OSVĚDČENÉ PŘÍSTUPY (z úspěšných hovorů):
{chr(10).join([f"- {phrase}" for phrase in data['successful_phrases'][:5]])}

⭐ BEST PRACTICES:
{chr(10).join([f"- {bp}" for bp in data['best_practices'][-3:]])}

DŮLEŽITÉ: Použij tyto osvědčené fráze a přístupy ve svých odpovědích!
"""
        
        return base_prompt + enhancement


if __name__ == "__main__":
    # Test
    learner = LearningSystem()
    
    # Simulace
    fake_report = {
        'success_rate': 85,
        'feedback': 'Bot byl profesionální a aktivní',
        'strengths': ['Jasná komunikace', 'Dobré uzavření'],
        'classification': 'success'
    }
    
    print("Test learning system...")