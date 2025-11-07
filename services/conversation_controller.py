"""
CONVERSATION FLOW CONTROLLER
Řídí tok hovoru a vrací zákazníka k tématu
"""

import mysql.connector
from typing import Dict, Optional
import re


class ConversationController:
    """Kontroluje flow konverzace a vrací k cíli"""
    
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='ai_calling',
            charset='utf8mb4'
        )
        self.cursor = self.conn.cursor(dictionary=True)
        
        # Track current stage
        self.current_stage = 'intro'
        self.stage_attempts = 0
        self.stage_start_time = None
    
    def process_customer_input(self, customer_text: str, conversation_history: list) -> Dict:
        """
        Zpracuj vstup zákazníka a rozhodní co dál
        
        Returns:
            {
                'is_on_topic': bool,
                'detected_off_topic': str or None,
                'redirect_needed': bool,
                'redirect_phrase': str or None,
                'next_stage': str,
                'suggested_response': str
            }
        """
        
        print(f"\n[ConversationController] Zpracovávám: '{customer_text}'")
        
        # 1. Detekuj jestli je ON-TOPIC
        is_on_topic = self._is_on_topic(customer_text)
        
        if not is_on_topic:
            # OFF-TOPIC detekováno
            off_topic_type = self._detect_off_topic_type(customer_text)
            redirect = self._get_redirect_phrase(off_topic_type)
            
            print(f"  ⚠️  OFF-TOPIC detekováno: {off_topic_type}")
            print(f"  🔄 Redirect: {redirect[:50]}...")
            
            return {
                'is_on_topic': False,
                'detected_off_topic': off_topic_type,
                'redirect_needed': True,
                'redirect_phrase': redirect,
                'next_stage': self.current_stage,  # Zůstáváme v stejné fázi
                'suggested_response': redirect
            }
        
        # 2. ON-TOPIC - pokračuj podle flow
        print(f"  ✅ ON-TOPIC")
        
        # Analyzuj odpověď zákazníka
        analysis = self._analyze_customer_response(customer_text)
        
        # Rozhodní next stage
        next_stage = self._determine_next_stage(analysis)
        
        # Získej suggested response
        suggested_response = self._get_stage_response(next_stage, analysis)
        
        print(f"  📍 Current stage: {self.current_stage}")
        print(f"  ➡️  Next stage: {next_stage}")
        
        self.current_stage = next_stage
        
        return {
            'is_on_topic': True,
            'detected_off_topic': None,
            'redirect_needed': False,
            'redirect_phrase': None,
            'next_stage': next_stage,
            'suggested_response': suggested_response
        }
    
    def _is_on_topic(self, text: str) -> bool:
        """Detekuj jestli je zákazník ON-TOPIC"""
        
        # ON-TOPIC keywords
        on_topic_keywords = [
            'web', 'stránk', 'internet', 'google', 'seo',
            'zákazník', 'obchodník', 'reklam', 'marketing',
            'schůzka', 'setkání', 'konzultace', 'nabídka',
            'cena', 'kolik', 'ano', 'ne', 'zajímá', 'nezajímá',
            'email', 'telefon', 'kontakt', 'pošl',
            'můžu', 'můžete', 'kdy', 'jak', 'co',
            'mám', 'nemám', 'máme', 'nemáme',
            'chci', 'nechci', 'chtěl', 'potřebuju'
        ]
        
        text_lower = text.lower()
        
        # Pokud obsahuje business keywords = ON-TOPIC
        if any(keyword in text_lower for keyword in on_topic_keywords):
            return True
        
        # Krátké odpovědi (ano, ne, jo, jasně) = ON-TOPIC
        if len(text.split()) <= 3:
            return True
        
        return False
    
    def _detect_off_topic_type(self, text: str) -> str:
        """Detekuj typ OFF-TOPIC odbočení"""
        
        self.cursor.execute("""
            SELECT off_topic_type, detected_keywords
            FROM off_topic_handlers
        """)
        
        handlers = self.cursor.fetchall()
        
        text_lower = text.lower()
        
        for handler in handlers:
            keywords = handler['detected_keywords'].split(', ')
            if any(keyword in text_lower for keyword in keywords):
                return handler['off_topic_type']
        
        return 'random_otázka'  # Default
    
    def _get_redirect_phrase(self, off_topic_type: str) -> str:
        """Získej redirect frázi pro návrat k tématu"""
        
        self.cursor.execute("""
            SELECT acknowledgment, redirect_phrase
            FROM off_topic_handlers
            WHERE off_topic_type = %s
            LIMIT 1
        """, (off_topic_type,))
        
        result = self.cursor.fetchone()
        
        if result:
            # Update stats
            self.cursor.execute("""
                UPDATE off_topic_handlers
                SET times_encountered = times_encountered + 1
                WHERE off_topic_type = %s
            """, (off_topic_type,))
            self.conn.commit()
            
            # Combine acknowledgment + redirect
            return f"{result['acknowledgment']} {result['redirect_phrase']}"
        
        # Fallback
        return "Chápu. Ale zpátky k byznysu - máte web nebo ne?"
    
    def _analyze_customer_response(self, text: str) -> Dict:
        """Analyzuj odpověď zákazníka"""
        
        text_lower = text.lower()
        
        analysis = {
            'has_web': False,
            'interested': None,  # True/False/None
            'objection_detected': None,
            'positive_signal': False,
            'ready_to_meet': False,
            'sentiment': 'neutral'
        }
        
        # Detekce webu
        if any(phrase in text_lower for phrase in ['mám web', 'máme web', 'máme stránky', 'už máme']):
            analysis['has_web'] = True
        elif any(phrase in text_lower for phrase in ['nemám web', 'nemáme web', 'nemáme stránky', 'zatím ne']):
            analysis['has_web'] = False
        
        # Detekce zájmu
        if any(phrase in text_lower for phrase in ['ano', 'jo', 'jasně', 'zajímá', 'určitě', 'dobrý', 'super']):
            analysis['interested'] = True
            analysis['positive_signal'] = True
        elif any(phrase in text_lower for phrase in ['ne', 'nezajímá', 'nechci', 'nemám zájem']):
            analysis['interested'] = False
        
        # Detekce schůzky
        if any(phrase in text_lower for phrase in ['schůzka', 'setkání', 'sejdeme', 'konzultace', 'můžeme', 'zítra', 'příští týden']):
            analysis['ready_to_meet'] = True
            analysis['positive_signal'] = True
        
        # Detekce námitek
        if 'čas' in text_lower and 'nemám' in text_lower:
            analysis['objection_detected'] = 'no_time'
        elif any(phrase in text_lower for phrase in ['drahé', 'peníze', 'rozpočet']):
            analysis['objection_detected'] = 'no_money'
        
        # Sentiment
        if analysis['positive_signal']:
            analysis['sentiment'] = 'positive'
        elif analysis['interested'] == False:
            analysis['sentiment'] = 'negative'
        
        return analysis
    
    def _determine_next_stage(self, analysis: Dict) -> str:
        """Rozhodní další stage podle analýzy"""
        
        current = self.current_stage
        
        # Flow logic
        if current == 'intro':
            if analysis['interested'] == True:
                return 'discovery'
            elif analysis['interested'] == False:
                return 'retry_intro'
            else:
                return 'discovery'  # Zkusíme discovery i tak
        
        elif current == 'discovery':
            if analysis['has_web'] == False:
                return 'value_proposition'  # Příležitost!
            elif analysis['has_web'] == True:
                return 'qualification'  # Zjistit víc
            else:
                return 'discovery'  # Opakuj otázku
        
        elif current == 'value_proposition':
            if analysis['interested'] == True:
                return 'closing'  # Jedeme rovnou na schůzku
            elif analysis['objection_detected']:
                return 'handle_objections'
            else:
                return 'value_proposition'  # Ještě value
        
        elif current == 'handle_objections':
            if analysis['positive_signal']:
                return 'closing'
            else:
                return 'handle_objections'  # Další pokus
        
        elif current == 'closing':
            if analysis['ready_to_meet']:
                return 'confirm_meeting'
            else:
                return 'closing'  # Opakuj close
        
        return current  # Default - zůstaň
    
    def _get_stage_response(self, stage: str, analysis: Dict) -> str:
        """Získej response pro daný stage"""
        
        # Query database pro stage-specific response
        self.cursor.execute("""
            SELECT answer
            FROM knowledge_base
            WHERE category = %s
            ORDER BY success_rate DESC
            LIMIT 1
        """, (stage,))
        
        result = self.cursor.fetchone()
        
        if result:
            return result['answer']
        
        # Fallback responses
        fallbacks = {
            'discovery': 'Takže - máte web nebo ne?',
            'value_proposition': 'Web vám přivede zákazníky 24/7. Bez webu přicházíte o desítky zákazníků měsíčně.',
            'closing': 'Pojďme se sejít. Ukážu vám konkrétní příklady. Zítra nebo pozítří?',
            'confirm_meeting': 'Super! Takže pátek odpoledne? Pošlu email s potvrzením.'
        }
        
        return fallbacks.get(stage, 'Máte minutku se o tom pobavit?')
    
    def get_current_goal(self) -> str:
        """Vrať aktuální cíl konverzace"""
        
        self.cursor.execute("""
            SELECT stage_goal
            FROM conversation_flow
            WHERE flow_stage = %s
        """, (self.current_stage,))
        
        result = self.cursor.fetchone()
        return result['stage_goal'] if result else 'Domluvit schůzku'
    
    def close(self):
        self.cursor.close()
        self.conn.close()