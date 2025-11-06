"""
Learning System - Učí se z úspěšných hovorů
PRODUCTION READY - s detailním loggingem
OPRAVENO: f-string backslash error
"""

import openai
from config import Config, Prompts
from database import CallDB
import json
import os
from datetime import datetime


class LearningSystem:
    """Systém pro učení z úspěšných hovorů"""
    
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.db = CallDB()
        self.learned_prompts_file = 'data/learned_prompts.json'
        self._ensure_file()
    
    def _ensure_file(self):
        """Vytvoří soubor pro learned prompts"""
        
        # Vytvoř složku
        os.makedirs('data', exist_ok=True)
        
        if not os.path.exists(self.learned_prompts_file):
            print(f"⚠️  Learned prompts soubor neexistuje - vytvářím...")
            
            initial_data = {
                'version': 1,
                'learned_patterns': [],
                'successful_phrases': [
                    "Dobrý den, volám ohledně možnosti vytvořit vám moderní webové stránky.",
                    "Můžu vám poslat cenovou nabídku emailem?",
                    "Kdy by vám vyhovovalo si o tom více popovídat?",
                    "Máme speciální nabídku pro nové zákazníky."
                ],
                'best_practices': [
                    "Být konkrétní a stručný",
                    "Nabídnout email nebo schůzku",
                    "Ukončit s jasným dalším krokem"
                ],
                'stats': {
                    'total_learned_calls': 0,
                    'last_learning': None,
                    'avg_success_rate': 0
                }
            }
            
            try:
                with open(self.learned_prompts_file, 'w', encoding='utf-8') as f:
                    json.dump(initial_data, f, ensure_ascii=False, indent=2)
                
                print(f"✅ Learned prompts soubor vytvořen: {self.learned_prompts_file}")
                
            except Exception as e:
                print(f"❌ Nepodařilo se vytvořit soubor: {e}")
                raise
    
    def learn_from_call(self, call_sid, report):
        """
        Učí se z úspěšného hovoru
        
        Args:
            call_sid: ID hovoru
            report: AI report
        """
        
        print(f"\n{'='*60}")
        print(f"🧠 AUTO-LEARNING SYSTEM")
        print(f"{'='*60}")
        print(f"Call SID: {call_sid}")
        print(f"Success rate: {report.get('success_rate', 0)}%")
        print(f"Classification: {report.get('classification', 'N/A')}")
        
        # Získej konverzaci
        from services import ReceptionistService
        receptionist = ReceptionistService()
        
        if call_sid not in receptionist.ai.conversations:
            print(f"❌ Konverzace nenalezena v paměti")
            return False
        
        messages = receptionist.ai.conversations[call_sid]
        
        # Bot zprávy
        bot_messages = [
            msg['content'] for msg in messages 
            if msg['role'] == 'assistant' 
            and not msg['content'].startswith('CALL_START_TIME')
            and len(msg['content']) > 5
        ]
        
        if not bot_messages:
            print(f"❌ Žádné bot zprávy k analýze")
            return False
        
        print(f"📝 Bot zpráv k analýze: {len(bot_messages)}")
        
        # AI analýza
        try:
            print(f"🤖 Analyzuji úspěšné vzorce...")
            
            analysis = self._analyze_successful_patterns(bot_messages, report)
            
            if not analysis:
                print(f"❌ Analýza selhala")
                return False
            
            print(f"✅ Analýza dokončena")
            
            # Ulož patterns
            saved = self._save_patterns(analysis, report.get('success_rate', 0))
            
            if saved:
                print(f"✅ Patterns uloženy do {self.learned_prompts_file}")
                print(f"🎓 Nově naučených frází: {len(analysis.get('successful_phrases', []))}")
            else:
                print(f"❌ Nepodařilo se uložit patterns")
                return False
            
            print(f"{'='*60}\n")
            return True
            
        except Exception as e:
            print(f"❌ Learning error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _analyze_successful_patterns(self, bot_messages, report):
        """Analyzuje úspěšné vzorce pomocí AI"""
        
        # ✅ OPRAVA: chr(10) MIMO f-string
        nl = '\n'
        
        prompt = f"""Analyzuj tento ÚSPĚŠNÝ prodejní hovor (úspěšnost {report.get('success_rate')}%).

BOT ZPRÁVY ({len(bot_messages)} zpráv):
{nl.join([f"{i+1}. {msg}" for i, msg in enumerate(bot_messages)])}

AI FEEDBACK:
{report.get('feedback', 'N/A')}

CO BYLO DOBRÉ:
{nl.join([f"- {s}" for s in report.get('strengths', [])])}

CO ZLEPŠIT:
{nl.join([f"- {w}" for w in report.get('weaknesses', [])])}

ÚKOL:
Identifikuj KONKRÉTNÍ FRÁZE a PŘÍSTUPY které vedly k úspěchu.

Vrať JSON:
{{
    "successful_phrases": [
        "přesná fráze 1 kterou bot řekl",
        "přesná fráze 2 kterou bot řekl",
        ...max 5 nejlepších
    ],
    "effective_approach": "Popis přístupu který fungoval",
    "key_moments": [
        "moment kdy bot udělal dobře věc 1",
        "moment 2",
        ...max 3
    ],
    "avoid": [
        "co nedělat 1",
        "co nedělat 2"
    ],
    "recommended_structure": "Jak strukturovat další hovory"
}}

DŮLEŽITÉ:
- successful_phrases musí být PŘESNÉ citace z bot zpráv výše
- Vyber jen ty nejefektivnější fráze
- Zaměř se na to co OPRAVDU fungovalo

Odpověz POUZE validním JSON!
"""
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": "Jsi expert na analýzu prodejních hovorů. Identifikuješ přesné fráze které vedou k úspěchu. Odpovídáš POUZE JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            # Debug output
            print(f"\n  📊 Analyzované vzorce:")
            print(f"     Úspěšných frází: {len(analysis.get('successful_phrases', []))}")
            
            for i, phrase in enumerate(analysis.get('successful_phrases', [])[:3], 1):
                print(f"     {i}. \"{phrase[:60]}...\"")
            
            return analysis
            
        except Exception as e:
            print(f"  ❌ OpenAI error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _save_patterns(self, analysis, success_rate):
        """Uloží learned patterns"""
        
        try:
            # Načti existující
            with open(self.learned_prompts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Přidej nový pattern
            data['learned_patterns'].append({
                'timestamp': datetime.now().isoformat(),
                'success_rate': success_rate,
                'analysis': analysis
            })
            
            # Updatuj successful phrases (bez duplikátů, max 20)
            for phrase in analysis.get('successful_phrases', []):
                if phrase and phrase not in data['successful_phrases']:
                    data['successful_phrases'].append(phrase)
            
            # Omez na 20 nejnovějších
            data['successful_phrases'] = data['successful_phrases'][-20:]
            
            # Best practices (max 10)
            if analysis.get('effective_approach'):
                if analysis['effective_approach'] not in data['best_practices']:
                    data['best_practices'].append(analysis['effective_approach'])
            
            data['best_practices'] = data['best_practices'][-10:]
            
            # Statistiky
            data['stats']['total_learned_calls'] = data['stats'].get('total_learned_calls', 0) + 1
            data['stats']['last_learning'] = datetime.now().isoformat()
            
            # Průměrná úspěšnost
            all_rates = [p.get('success_rate', 0) for p in data['learned_patterns'][-10:]]
            data['stats']['avg_success_rate'] = sum(all_rates) / len(all_rates) if all_rates else 0
            
            # Ulož
            with open(self.learned_prompts_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"\n  💾 Uloženo:")
            print(f"     Celkem learned hovorů: {data['stats']['total_learned_calls']}")
            print(f"     Celkem frází: {len(data['successful_phrases'])}")
            print(f"     Průměrná úspěšnost: {data['stats']['avg_success_rate']:.1f}%")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Save error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_optimized_prompt(self, product, contact_name):
        """Vrátí optimalizovaný prompt s learned patterns"""
        
        # Načti learned patterns
        try:
            with open(self.learned_prompts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"⚠️  Nepodařilo se načíst learned prompts: {e}")
            return Prompts.get_sales_prompt(product, contact_name)
        
        # Pokud nemáme data, použij default
        if not data.get('successful_phrases'):
            print(f"⚠️  Žádné learned patterns - použit default prompt")
            return Prompts.get_sales_prompt(product, contact_name)
        
        # Jinak vytvoř enhanced prompt
        base_prompt = Prompts.get_sales_prompt(product, contact_name)
        
        # ✅ OPRAVA: \n MIMO f-string
        nl = '\n'
        separator = '=' * 60
        
        # Přidej learned patterns
        enhancement = f"""

{separator}
🧠 OSVĚDČENÉ PŘÍSTUPY (naučeno z {data['stats']['total_learned_calls']} úspěšných hovorů):
{separator}

📝 ÚSPĚŠNÉ FRÁZE (použij podobné):
{nl.join([f"   • \"{phrase}\"" for phrase in data['successful_phrases'][-8:]])}

🎯 BEST PRACTICES:
{nl.join([f"   • {bp}" for bp in data['best_practices'][-5:]])}

⭐ DŮLEŽITÉ:
- Inspiruj se těmito frázemi a přístupy
- Udržuj stručnost a konkrétnost
- Vždy nabídni jasný další krok (email, schůzka, callback)
- Reaguj pozitivně na námitky

{separator}
"""
        
        print(f"🧠 Použit LEARNED prompt (průměrná úspěšnost: {data['stats']['avg_success_rate']:.1f}%)")
        
        return base_prompt + enhancement


if __name__ == "__main__":
    # Test
    print("🧪 Test Learning System\n")
    
    learner = LearningSystem()
    
    print(f"✅ Learning system inicializován")
    print(f"📁 Soubor: {learner.learned_prompts_file}")
    
    # Zkus načíst data
    try:
        with open(learner.learned_prompts_file, 'r') as f:
            data = json.load(f)
        
        print(f"\n📊 Aktuální stav:")
        print(f"   Naučených hovorů: {data['stats']['total_learned_calls']}")
        print(f"   Úspěšných frází: {len(data['successful_phrases'])}")
        print(f"   Best practices: {len(data['best_practices'])}")
        
    except Exception as e:
        print(f"❌ Chyba: {e}")