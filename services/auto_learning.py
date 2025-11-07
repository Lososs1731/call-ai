"""
AUTO-LEARNING SYSTEM - učí se z každého hovoru
"""

import mysql.connector
from typing import Dict, List
import json
from datetime import datetime
from openai import OpenAI
from config import Config


class AutoLearningSystem:
    """Automatické učení z hovorů"""
    
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # ✅ ZMĚŇ!
            database='ai_calling',
            charset='utf8mb4'
        )
        self.cursor = self.conn.cursor(dictionary=True)
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def learn_from_call(self, call_data: Dict):
        """Uč se z hovoru - OKAMŽITĚ PO KAŽDÉM HOVORU!"""
        
        print(f"\n{'='*60}")
        print(f"🧠 AUTO-LEARNING ZAČÍNÁ")
        print(f"{'='*60}")
        
        call_sid = call_data.get('call_sid')
        outcome = call_data.get('outcome')
        score = call_data.get('sales_score', 0)
        conversation = call_data.get('conversation', [])
        
        print(f"  Call SID: {call_sid}")
        print(f"  Outcome: {outcome}")
        print(f"  Score: {score}/100")
        
        # 1. ANALÝZA CO FUNGOVALO
        if score >= 70:
            print(f"  ✅ ÚSPĚŠNÝ HOVOR - učím se co fungovalo...")
            self._learn_success_patterns(call_data)
        
        # 2. ANALÝZA CO SELHALO
        elif score < 40:
            print(f"  ❌ NEÚSPĚŠNÝ HOVOR - učím se z chyb...")
            self._learn_failure_patterns(call_data)
        
        # 3. AKTUALIZUJ SUCCESS RATES
        print(f"  📊 Aktualizuji success rates...")
        self._update_success_rates(call_data)
        
        # 4. DETEKUJ NOVÉ VZORY
        print(f"  🔍 Hledám nové vzory...")
        self._detect_new_patterns(call_data)
        
        print(f"  ✅ Learning dokončen!")
        print(f"{'='*60}\n")
    
    def _learn_success_patterns(self, call_data: Dict):
        """Uč se z úspěšného hovoru"""
        
        conversation = call_data.get('conversation', [])
        what_worked = call_data.get('what_worked', '')
        
        # AI analýza co přesně fungovalo
        analysis_prompt = f"""
Analyzuj tento ÚSPĚŠNÝ hovor a zjisti CO PŘESNĚ fungovalo:

KONVERZACE:
{json.dumps(conversation, ensure_ascii=False, indent=2)}

CO FUNGOVALO (podle AI analýzy):
{what_worked}

Odpověz ve formátu JSON:
{{
    "successful_phrases": ["fráze 1", "fráze 2", ...],
    "successful_strategies": ["strategie 1", "strategie 2", ...],
    "key_moments": ["moment 1", "moment 2", ...],
    "objection_handling": {{"námitka": "úspěšná odpověď"}},
    "recommendation": "Co použít příště"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Ulož úspěšné fráze do databáze
            for phrase in result.get('successful_phrases', []):
                self.cursor.execute("""
                    INSERT INTO successful_phrases (phrase_type, phrase_text, success_rate, conversions)
                    VALUES ('learned', %s, 100, 1)
                    ON DUPLICATE KEY UPDATE
                        times_used = times_used + 1,
                        conversions = conversions + 1,
                        success_rate = (conversions * 100.0 / times_used)
                """, (phrase,))
            
            # Ulož strategie
            for strategy in result.get('successful_strategies', []):
                self.cursor.execute("""
                    INSERT INTO learning_insights (
                        insight_type, situation, what_worked, recommendation, confidence_score
                    ) VALUES ('success_strategy', %s, %s, %s, %s)
                """, (
                    'Úspěšný hovor',
                    strategy,
                    result.get('recommendation', ''),
                    call_data.get('sales_score', 0) / 100.0
                ))
            
            self.conn.commit()
            print(f"    ✅ Naučeno {len(result.get('successful_phrases', []))} frází")
            
        except Exception as e:
            print(f"    ❌ Chyba při učení: {e}")
    
    def _learn_failure_patterns(self, call_data: Dict):
        """Uč se z neúspěšného hovoru"""
        
        conversation = call_data.get('conversation', [])
        what_failed = call_data.get('what_failed', '')
        recommendations = call_data.get('ai_recommendations', '')
        
        # AI analýza co selhalo
        analysis_prompt = f"""
Analyzuj tento NEÚSPĚŠNÝ hovor a zjisti CO SELHALO:

KONVERZACE:
{json.dumps(conversation, ensure_ascii=False, indent=2)}

CO SELHALO:
{what_failed}

DOPORUČENÍ:
{recommendations}

Odpověz ve formátu JSON:
{{
    "failed_approaches": ["přístup 1", "přístup 2", ...],
    "missed_opportunities": ["příležitost 1", "příležitost 2", ...],
    "better_responses": {{"špatná odpověď": "lepší odpověď"}},
    "what_to_avoid": ["co nedělat 1", "co nedělat 2", ...],
    "what_to_do_instead": ["co dělat místo toho 1", "co dělat místo toho 2", ...]
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Ulož learning insights
            for failed_approach in result.get('failed_approaches', []):
                self.cursor.execute("""
                    INSERT INTO learning_insights (
                        insight_type, situation, what_failed, recommendation, confidence_score
                    ) VALUES ('failure_pattern', %s, %s, %s, %s)
                """, (
                    'Neúspěšný hovor',
                    failed_approach,
                    ', '.join(result.get('what_to_do_instead', [])),
                    0.8
                ))
            
            # Aktualizuj objection responses pokud selhaly
            for old_response, better_response in result.get('better_responses', {}).items():
                # Najdi původní odpověď a sniž její success rate
                self.cursor.execute("""
                    UPDATE objection_responses
                    SET success_rate = success_rate * 0.9
                    WHERE bot_response LIKE %s
                    LIMIT 1
                """, (f"%{old_response[:50]}%",))
                
                # Přidej lepší odpověď
                self.cursor.execute("""
                    INSERT INTO objection_responses (
                        objection_type, customer_phrase, bot_response, success_rate
                    ) VALUES ('learned', %s, %s, 50.0)
                """, (old_response[:100], better_response))
            
            self.conn.commit()
            print(f"    ✅ Naučeno {len(result.get('failed_approaches', []))} chyb k vyhnutí")
            
        except Exception as e:
            print(f"    ❌ Chyba při učení: {e}")
    
    def _update_success_rates(self, call_data: Dict):
        """Aktualizuj success rates podle výsledku hovoru"""
        
        conversation = call_data.get('conversation', [])
        success = call_data.get('sales_score', 0) >= 70
        
        # Projdi všechny odpovědi bota
        for msg in conversation:
            if msg.get('role') == 'assistant':
                text = msg.get('content', '')
                
                if len(text) > 10:
                    # Najdi podobné fráze v databázi a aktualizuj
                    self.cursor.execute("""
                        SELECT id FROM knowledge_base
                        WHERE answer LIKE %s
                        LIMIT 1
                    """, (f"%{text[:30]}%",))
                    
                    result = self.cursor.fetchone()
                    
                    if result:
                        kb_id = result['id']
                        
                        # Aktualizuj metriky
                        self.cursor.execute("""
                            UPDATE knowledge_base
                            SET 
                                times_used = times_used + 1,
                                times_successful = times_successful + %s,
                                success_rate = (times_successful * 100.0 / times_used),
                                last_used = NOW()
                            WHERE id = %s
                        """, (1 if success else 0, kb_id))
        
        self.conn.commit()
    
    def _detect_new_patterns(self, call_data: Dict):
        """Detekuj nové vzory v konverzaci"""
        
        conversation = call_data.get('conversation', [])
        
        # Hledej opakující se vzory
        customer_phrases = [
            msg.get('content') for msg in conversation 
            if msg.get('role') == 'user'
        ]
        
        # Pokud zákazník řekl něco nového, co není v databázi
        for phrase in customer_phrases:
            if len(phrase) > 5:
                # Zkontroluj jestli existuje
                self.cursor.execute("""
                    SELECT COUNT(*) as count FROM objection_responses
                    WHERE customer_phrase LIKE %s
                """, (f"%{phrase[:20]}%",))
                
                result = self.cursor.fetchone()
                
                if result['count'] == 0:
                    print(f"    🆕 Nová fráze: '{phrase[:50]}...'")
                    # TODO: AI navrhne odpověď
    
    def get_best_practices(self) -> List[Dict]:
        """Získej nejlepší praktiky z učení"""
        
        self.cursor.execute("""
            SELECT *
            FROM learning_insights
            WHERE confidence_score > 0.7
            ORDER BY confidence_score DESC
            LIMIT 20
        """)
        
        return self.cursor.fetchall()
    
    def close(self):
        """Zavři spojení"""
        self.cursor.close()
        self.conn.close()