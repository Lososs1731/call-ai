"""
AI Receptionist - Petra
Telefonní asistentka pro Moravské Weby
NAPOJENO NA SQLite KNOWLEDGE BASE
"""

import os
from openai import OpenAI
from datetime import datetime
import json
from typing import Optional, Dict, List

# KNOWLEDGE BASE INTEGRATION
from database.sqlite_connector import get_knowledge_base
from services.topic_controller import TopicController
from services.response_selector import ResponseSelector

class AIReceptionist:
    """AI Telefonní recepční Petra"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # KNOWLEDGE BASE KOMPONENTY
        self.kb = get_knowledge_base()
        self.topic_controller = TopicController()
        self.response_selector = ResponseSelector()
        
        # Conversation state
        self.conversation_history = []
        self.current_stage = 'intro'  # intro -> discovery -> value -> objection -> closing
        self.customer_name = None
        self.customer_sentiment = 'neutral'  # positive/neutral/negative
        self.meeting_scheduled = False
        
        # Tracking
        self.off_topic_count = 0
        self.last_response_id = None
        
        # System prompt
        self.system_prompt = self._build_system_prompt()
        
        print("🤖 AI Receptionist Petra initialized")
        print(f"   ✅ Knowledge Base loaded")
        print(f"   ✅ Topic Controller active")
        print(f"   ✅ Response Selector ready")
    
    def _build_system_prompt(self) -> str:
        """Vytvoř system prompt pro AI"""
        return """Jsi Petra, telefonní recepční pro Moravské Weby.

OSOBNOST:
- Příjemná, přátelská, ale profesionální
- Mluvíš přirozeně česky (jo, no, jasně, fajn)
- Jsi asertivní - máš cíl (domluvit schůzku)
- Empatie, ale nepřehánět

CÍL HOVORU:
1. Zjistit jestli mají web
2. Ukázat hodnotu (víc zákazníků)
3. DOMLUVIT SCHŮZKU

DŮLEŽITÉ:
- Používej krátké věty
- Přirozený český jazyk
- Reaguj na emoce zákazníka
- Push ke schůzce ale nenátlakově
- Pokud odmítá → nechej kontakt

TAKTIKA:
- Intro: Zaujmout (30 sekund, peníze, zákazníci)
- Discovery: Zjistit situaci (web? funguje? kolik zákazníků?)
- Value: Ukázat benefit (ROI, SEO, 24/7, konkurence)
- Objection: Vyřešit námitky (čas, peníze, zájem)
- Closing: Domluvit schůzku (zítra? pozítří? online?)

Tvoje odpovědi jsou KRÁTKÉ, PŘIROZENÉ a směřují KE SCHŮZCE."""
    
    def generate_response(self, customer_input: str, call_sid: str) -> str:
        """
        Generuj odpověď s pomocí Knowledge Base
        
        FLOW:
        1. Check OFF-TOPIC → redirect
        2. Detect sentiment
        3. Determine stage
        4. Get response from DB
        5. Personalize with AI
        6. Log usage
        7. Return
        """
        
        print(f"\n💬 Customer: {customer_input}")
        
        # ============================================================
        # 1. OFF-TOPIC CHECK
        # ============================================================
        
        is_on_topic, redirect_response = self.topic_controller.check_and_redirect(customer_input)
        
        if not is_on_topic:
            print(f"⚠️  OFF-TOPIC detected! Redirecting...")
            
            if self.topic_controller.should_end_call():
                print("❌ Too many OFF-TOPIC. Ending call.")
                return self.topic_controller.get_end_call_message()
            
            return redirect_response
        
        # ============================================================
        # 2. DETECT SENTIMENT
        # ============================================================
        
        self.customer_sentiment = self._detect_sentiment(customer_input)
        print(f"😊 Sentiment: {self.customer_sentiment}")
        
        # ============================================================
        # 3. DETERMINE STAGE & SUB-CATEGORY
        # ============================================================
        
        stage, sub_category = self._determine_stage_and_subcategory(customer_input)
        self.current_stage = stage
        
        print(f"🎯 Stage: {stage}, Sub: {sub_category}")
        
        # ============================================================
        # 4. GET RESPONSE FROM KB
        # ============================================================
        
        kb_response = self.response_selector.get_response(
            stage=stage,
            sub_category=sub_category,
            customer_sentiment=self.customer_sentiment,
            add_czech_filler=True
        )
        
        self.last_response_id = kb_response['id']
        print(f"📚 KB Response #{kb_response['id']}")
        
        # ============================================================
        # 5. PERSONALIZE WITH AI
        # ============================================================
        
        final_response = self._personalize_with_ai(
            kb_response=kb_response,
            customer_input=customer_input
        )
        
        # ============================================================
        # 6. LOG USAGE
        # ============================================================
        
        is_positive = self.customer_sentiment == 'positive' or any(
            word in customer_input.lower() 
            for word in ['ano', 'zajímá', 'jo', 'dobré', 'super', 'schůzka']
        )
        
        led_to_meeting = any(
            word in customer_input.lower()
            for word in ['schůzka', 'sejdeme', 'zítra', 'pondělí', 'úterý', 'středa']
        )
        
        if led_to_meeting:
            self.meeting_scheduled = True
        
        if self.last_response_id and self.last_response_id > 0:
            self.response_selector.log_response_success(
                response_id=self.last_response_id,
                was_successful=is_positive,
                led_to_meeting=led_to_meeting
            )
        
        # ============================================================
        # 7. RETURN
        # ============================================================
        
        print(f"🤖 Petra: {final_response[:80]}...")
        
        # Add to history
        self.conversation_history.append({
            'role': 'user',
            'content': customer_input
        })
        self.conversation_history.append({
            'role': 'assistant',
            'content': final_response
        })
        
        return final_response
    
    # ============================================================
    # HELPER METHODS
    # ============================================================
    
    def _detect_sentiment(self, text: str) -> str:
        """Rychlá detekce sentimentu z klíčových slov"""
        text_lower = text.lower()
        
        # Pozitivní signály
        positive_words = [
            'ano', 'jo', 'jasně', 'super', 'skvělé', 'zajímá', 'dobré',
            'fajn', 'ok', 'souhlasím', 'chci', 'pojďme', 'dobře'
        ]
        
        # Negativní signály
        negative_words = [
            'ne', 'nechci', 'nezajímá', 'nemám', 'nemůžu', 'nejde',
            'ale', 'problém', 'těžké', 'drahé', 'nechci', 'odmítám'
        ]
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _determine_stage_and_subcategory(self, text: str) -> tuple:
        """
        Urči stage a sub-category podle customer inputu
        
        Returns: (stage, sub_category)
        """
        text_lower = text.lower()
        
        # CLOSING SIGNALS
        if any(word in text_lower for word in [
            'schůzka', 'sejdeme', 'zítra', 'příští', 'pondělí', 'úterý',
            'středa', 'čtvrtek', 'pátek', 'termín', 'kdy'
        ]):
            return 'closing', 'direct_close'
        
        # OBJECTION SIGNALS
        if any(word in text_lower for word in ['nemám čas', 'zaneprázdněný', 'teď ne', 'později']):
            return 'objection', 'no_time'
        
        if any(word in text_lower for word in ['drahé', 'kolik', 'cena', 'rozpočet', 'peníze', 'nemáme peníze']):
            return 'objection', 'no_money'
        
        if any(word in text_lower for word in ['spokojení', 'už máme', 'nechceme']):
            return 'objection', 'have_web_satisfied'
        
        if any(word in text_lower for word in ['musím', 'poradit', 'manžel', 'šéf', 'tým']):
            return 'objection', 'need_consultation'
        
        if any(word in text_lower for word in ['nezajímá', 'nemáme zájem', 'nechci']):
            return 'objection', 'no_interest'
        
        # VALUE SIGNALS (zákazník chce vědět víc)
        if any(word in text_lower for word in [
            'jak', 'proč', 'co to', 'zajímá', 'víc', 'benefit',
            'výhoda', 'pomůže', 'funguje'
        ]):
            # Determine sub-category
            if 'seo' in text_lower or 'google' in text_lower:
                return 'value', 'seo_benefit'
            elif 'roi' in text_lower or 'návrat' in text_lower or 'kolik' in text_lower:
                return 'value', 'roi_benefit'
            elif 'konkurence' in text_lower:
                return 'value', 'competitor_advantage'
            else:
                return 'value', 'seo_benefit'  # default value
        
        # DISCOVERY SIGNALS
        if any(word in text_lower for word in [
            'máme web', 'nemáme web', 'ano máme', 'ne nemáme',
            'mám stránky', 'nemám stránky', 'web máme', 'web nemáme'
        ]):
            if 'nemáme' in text_lower or 'nemám' in text_lower or 'ne ' in text_lower:
                return 'discovery', 'no_web'
            else:
                return 'discovery', 'have_web'
        
        # DEFAULT - podle current stage
        if self.current_stage == 'intro':
            return 'discovery', 'web_check'
        elif self.current_stage == 'discovery':
            return 'value', 'seo_benefit'
        elif self.current_stage == 'value':
            return 'closing', 'direct_close'
        else:
            return self.current_stage, None
    
    def _personalize_with_ai(self, kb_response: Dict, customer_input: str) -> str:
        """
        Personalizuj KB response s pomocí AI
        (Optional - můžeš vypnout pro rychlost)
        """
        
        # Pro rychlost můžeš vrátit rovnou KB response
        # return kb_response['text']
        
        # NEBO personalizuj s AI:
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "system", "content": f"KNOWLEDGE BASE RESPONSE: {kb_response['text']}"},
                {"role": "system", "content": f"Použij tuto response ale udělej ji přirozenější. Zachovej smysl. Max 2 věty."},
                {"role": "user", "content": customer_input}
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Pokud AI response je moc dlouhá, použij KB
            if len(ai_response) > 300:
                return kb_response['text']
            
            return ai_response
            
        except Exception as e:
            print(f"⚠️  AI personalization failed: {e}")
            # Fallback na KB response
            return kb_response['text']
    
    def get_greeting(self) -> str:
        """Získej intro greeting z databáze"""
        intro_response = self.response_selector.get_response(
            stage='intro',
            sub_category='value_first',
            add_czech_filler=False
        )
        return intro_response['text']
    
    def end_call_summary(self) -> Dict:
        """Shrnutí hovoru"""
        return {
            'meeting_scheduled': self.meeting_scheduled,
            'total_messages': len(self.conversation_history),
            'final_stage': self.current_stage,
            'sentiment': self.customer_sentiment,
            'off_topic_count': self.topic_controller.off_topic_count
        }