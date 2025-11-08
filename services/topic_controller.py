"""
Topic Controller - Hlídá že hovor je ON-TOPIC
Pokud zákazník odbočí → redirect zpět k tématu
"""

from database.sqlite_connector import get_knowledge_base
from typing import Tuple, Optional
import random

class TopicController:
    """Kontroluje a udržuje hovor ON-TOPIC"""
    
    def __init__(self):
        self.kb = get_knowledge_base()
        self.off_topic_count = 0  # Kolikrát zákazník odbočil
        self.max_off_topic = 3    # Po 3x = ukončit hovor
    
    def check_and_redirect(self, customer_text: str) -> Tuple[bool, Optional[str]]:
        """
        Zkontroluj jestli zákazník je ON-TOPIC
        
        Returns:
            (is_on_topic: bool, redirect_response: Optional[str])
        """
        
        # ✅ Tyto fráze NEJSOU off-topic! (základní konverzační odpovědi)
        context_responses = [
            'slyšíme se', 'haló', 'halo', 'neslyším', 'ano slyším',
            'jo slyším', 'slyším vás', 'dobrý den', 'ahoj', 'prosím',
            'ano', 'jo', 'ne', 'moment', 'pardon'
        ]
        
        # Pokud je to jen krátká kontextová odpověď
        text_lower = customer_text.lower().strip()
        if len(text_lower) < 30:
            if any(phrase in text_lower for phrase in context_responses):
                self.off_topic_count = 0
                return True, None
        
        # Zkontroluj jestli text je ON-TOPIC
        is_on_topic, matched_topic = self.kb.is_on_topic(customer_text)
        
        if is_on_topic:
            # Reset counter
            self.off_topic_count = 0
            return True, None
        
        # OFF-TOPIC!
        self.off_topic_count += 1
        
        # Detekuj typ OFF-TOPIC
        redirect_type = self._detect_redirect_type(customer_text)
        
        # Získej redirect template
        redirect = self.kb.get_redirect(redirect_type)
        
        if not redirect:
            # Fallback
            return False, "Jo. Ale zpátky k byznysu - máte web?"
        
        # Sestav odpověď
        redirect_response = self._build_redirect_response(redirect)
        
        # Log usage
        if 'id' in redirect:
            self.kb.log_redirect_usage(redirect['id'], was_successful=False)
        
        return False, redirect_response
    
    def _detect_redirect_type(self, text: str) -> str:
        """Detekuj typ OFF-TOPIC konverzace"""
        text_lower = text.lower()
        
        # Jednoduchá keyword detekce
        if any(word in text_lower for word in ['počasí', 'prší', 'sníh', 'slunce', 'venku']):
            return 'weather'
        
        if any(word in text_lower for word in ['fotbal', 'hokej', 'sport', 'zápas']):
            return 'sports'
        
        if any(word in text_lower for word in ['politika', 'vláda', 'volby', 'prezident']):
            return 'politics'
        
        if any(word in text_lower for word in ['nemocný', 'zdraví', 'doktor', 'bolí']):
            return 'health'
        
        if any(word in text_lower for word in ['děti', 'rodina', 'manželka', 'dovolená']):
            return 'personal_life'
        
        if any(word in text_lower for word in ['drahé', 'problém', 'těžké']):
            return 'complaint_vent'
        
        if any(word in text_lower for word in ['jak se máte', 'dobrý den', 'počasí']):
            return 'casual_smalltalk'
        
        # Default
        return 'general_offtopic'
    
    def _build_redirect_response(self, redirect: dict) -> str:
        """Sestav redirect odpověď s českými fillery"""
        
        # Acknowledge (jo, chápu, hmm, ...)
        acknowledge = redirect.get('acknowledge_short', 'Jo')
        
        # Redirect
        redirect_text = redirect.get('redirect_direct', '')
        
        # Přidej náhodný filler občas
        if random.random() < 0.3:
            filler = self.kb.get_random_filler()
            if filler:
                acknowledge = filler
        
        return f"{acknowledge}. {redirect_text}"
    
    def should_end_call(self) -> bool:
        """Měl by se hovor ukončit? (příliš OFF-TOPIC)"""
        return self.off_topic_count >= self.max_off_topic
    
    def get_end_call_message(self) -> str:
        """Zdvořilé ukončení když je příliš OFF-TOPIC"""
        return (
            "Rozumím že teď není ten správný čas. "
            "Pošlu vám email s informacemi a můžeme se bavit až budete mít chvilku. "
            "Hezký den!"
        )