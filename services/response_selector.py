"""
Response Selector - Vybírá nejlepší odpověď z databáze
Inteligentní výběr podle kontext, historie, success rate
"""

from database.sqlite_connector import get_knowledge_base
from typing import Optional, Dict, List
import random

class ResponseSelector:
    """Inteligentní výběr responses z knowledge base"""
    
    def __init__(self):
        self.kb = get_knowledge_base()
        self.used_responses = []  # Historie použitých responses
        self.max_history = 10     # Kolik pamatovat
    
    def get_response(
        self,
        stage: str,
        sub_category: Optional[str] = None,
        customer_sentiment: str = 'neutral',  # positive/neutral/negative
        add_czech_filler: bool = True
    ) -> Dict:
        """
        Získej nejlepší response pro situaci
        
        Args:
            stage: intro/discovery/value/objection/closing
            sub_category: upřesnění (time_sensitive, no_money, ...)
            customer_sentiment: nálada zákazníka
            add_czech_filler: přidat české fillery?
        
        Returns:
            Dict s response_text, alternatives, metadata
        """
        
        # Získej top candidates
        candidates = self.kb.get_best_response(
            stage=stage,
            sub_category=sub_category,
            limit=5
        )
        
        if not candidates:
            # Fallback - jakýkoliv z daného stage
            candidates = self.kb.get_response_by_stage(stage, limit=5)
        
        if not candidates:
            return self._fallback_response(stage)
        
        # Vyfiltruj nedávno použité (variabilita)
        candidates = self._filter_recent(candidates)
        
        # Vyber podle sentimentu
        selected = self._select_by_sentiment(candidates, customer_sentiment)
        
        # Přidej do historie
        self.used_responses.append(selected['id'])
        if len(self.used_responses) > self.max_history:
            self.used_responses.pop(0)
        
        # Sestav finální response
        final_response = self._build_response(selected, add_czech_filler)
        
        return final_response
    
    def _filter_recent(self, candidates: List[Dict]) -> List[Dict]:
        """Odfiltruj nedávno použité responses (variabilita)"""
        filtered = [c for c in candidates if c['id'] not in self.used_responses[-3:]]
        return filtered if filtered else candidates
    
    def _select_by_sentiment(self, candidates: List[Dict], sentiment: str) -> Dict:
        """Vyber response podle sentimentu zákazníka"""
        
        if sentiment == 'negative':
            # Preferuj empathetic tone
            empathetic = [c for c in candidates if c.get('tone') in ['empathetic', 'understanding', 'calm']]
            if empathetic:
                return empathetic[0]
        
        elif sentiment == 'positive':
            # Preferuj enthusiastic/confident
            positive = [c for c in candidates if c.get('tone') in ['enthusiastic', 'confident', 'exciting']]
            if positive:
                return positive[0]
        
        # Default - nejvyšší success rate
        return candidates[0]
    
    def _build_response(self, response: Dict, add_filler: bool) -> Dict:
        """Sestav finální response s českými fillery"""
        
        text = response['response_text']
        
        # Přidej český filler občas
        if add_filler and random.random() < 0.4:
            filler = self.kb.get_random_filler()
            if filler and not text.startswith(filler):
                text = f"{filler}, {text[0].lower()}{text[1:]}"
        
        return {
            'id': response['id'],
            'text': text,
            'alternative_1': response.get('alternative_1'),
            'alternative_2': response.get('alternative_2'),
            'tone': response.get('tone', 'friendly'),
            'expected_response': response.get('expected_response'),
            'next_step': response.get('next_step'),
            'strategy': response.get('strategy'),
        }
    
    def _fallback_response(self, stage: str) -> Dict:
        """Fallback pokud nic nenajdeme"""
        fallbacks = {
            'intro': "Dobrý den! Petra z Moravských Webů. Máte chvilku?",
            'discovery': "Řekněte mi - máte webové stránky?",
            'value': "Web vám přivede víc zákazníků automaticky. Zajímá vás jak?",
            'objection': "Chápu váš pohled. Můžeme se sejít a ukážu vám konkrétní příklady?",
            'closing': "Pojďme se sejít. Zítra nebo pozítří vám vyhovuje?"
        }
        
        return {
            'id': -1,
            'text': fallbacks.get(stage, "Zajímá vás víc informací o našich službách?"),
            'alternative_1': None,
            'alternative_2': None,
            'tone': 'friendly',
            'expected_response': None,
            'next_step': 'Continue conversation',
            'strategy': 'fallback'
        }
    
    def log_response_success(
        self,
        response_id: int,
        was_successful: bool = False,
        led_to_meeting: bool = False
    ):
        """Zaloguj jak response fungovala"""
        if response_id > 0:  # Skip fallbacks
            self.kb.log_response_usage(
                response_id=response_id,
                was_successful=was_successful,
                led_to_meeting=led_to_meeting
            )