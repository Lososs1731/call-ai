"""
Cold Caller s Knowledge Base
Wrapper kolem ReceptionistService který přidává KB responses
"""

from services.receptionist import ReceptionistService
from database.sqlite_connector import get_knowledge_base
from services.topic_controller import TopicController
from services.response_selector import ResponseSelector


class ColdCallerKB:
    """
    Cold Caller s Knowledge Base
    
    Používá:
    - Tvůj stávající ReceptionistService (funguje!)
    - + Knowledge Base responses (54 variant)
    - + Auto-learning
    - + OFF-TOPIC handling
    """
    
    def __init__(self):
        # Tvůj původní receptionist (funguje!)
        self.receptionist = ReceptionistService()
        
        # Knowledge Base komponenty
        self.kb = get_knowledge_base()
        self.topic_controller = TopicController()
        self.response_selector = ResponseSelector()
        
        # Tracking
        self.current_stage = 'intro'
        self.customer_name = None
        self.company_name = None
        self.has_web = None
        self.last_response_id = None
        
        print("✅ ColdCallerKB inicializován (Receptionist + Knowledge Base)")
    
    def handle_outbound_call(self, call_sid, name, company=''):
        """
        Zahájí outbound cold call
        
        Args:
            call_sid: Call SID
            name: Jméno kontaktu
            company: Název firmy
            
        Returns:
            str: Opening greeting
        """
        
        print(f"\n🔥 COLD CALL s Knowledge Base")
        print(f"   Kontakt: {name}")
        print(f"   Firma: {company}")
        
        # Ulož info
        self.customer_name = name
        self.company_name = company
        self.current_stage = 'intro'
        
        # Získej INTRO z Knowledge Base
        intro_response = self.response_selector.get_response(
            stage='intro',
            sub_category='value_first',  # Použij value-first approach
            add_czech_filler=True
        )
        
        self.last_response_id = intro_response['id']
        
        # Personalizuj s jménem
        greeting = intro_response['text']
        
        # Přidej jméno
        greeting = f"Dobrý den, {name}. " + greeting
        
        # Pokud známe firmu
        if company:
            greeting = greeting.replace("firmám", f"firmě {company}")
        
        print(f"   📚 KB Response #{intro_response['id']}")
        print(f"   💬 Greeting: {greeting}")
        
        return greeting
    
    def process_customer_response(self, call_sid, user_input):
        """
        Zpracuj odpověď zákazníka S Knowledge Base
        
        Args:
            call_sid: Call SID
            user_input: Co zákazník řekl
            
        Returns:
            str: AI odpověď
        """
        
        print(f"\n💬 Zákazník: {user_input}")
        
        # ============================================================
        # 1. OFF-TOPIC CHECK
        # ============================================================
        
        is_on_topic, redirect = self.topic_controller.check_and_redirect(user_input)
        
        if not is_on_topic:
            print(f"   ⚠️  OFF-TOPIC → redirect")
            
            # V cold callingu - max 2 off-topics pak politely end
            if self.topic_controller.off_topic_count >= 2:
                return "Rozumím. Pošlu vám email s informacemi. Hezký den!"
            
            return redirect
        
        # ============================================================
        # 2. UPDATE STATE
        # ============================================================
        
        user_lower = user_input.lower()
        
        # Detekuj jestli mají web
        if 'máme web' in user_lower or 'ano máme' in user_lower:
            self.has_web = True
        elif 'nemáme web' in user_lower or 'ne nemáme' in user_lower:
            self.has_web = False
        
        # ============================================================
        # 3. DETERMINE STAGE
        # ============================================================
        
        next_stage, sub_category = self._determine_stage(user_input)
        self.current_stage = next_stage
        
        print(f"   🎯 Stage: {next_stage}")
        print(f"   📂 Sub: {sub_category}")
        
        # ============================================================
        # 4. GET KB RESPONSE
        # ============================================================
        
        kb_response = self.response_selector.get_response(
            stage=next_stage,
            sub_category=sub_category,
            customer_sentiment=self._detect_sentiment(user_input),
            add_czech_filler=True
        )
        
        self.last_response_id = kb_response['id']
        
        print(f"   📚 KB #{kb_response['id']}: {kb_response['text'][:60]}...")
        
        # ============================================================
        # 5. ENHANCE s AI (optional)
        # ============================================================
        
        # Můžeš použít tvůj AI engine pro personalizaci
        # NEBO vrátit rovnou KB response
        
        # VARIANTA A - Rovnou KB (rychlejší):
        final_response = kb_response['text']
        
        # VARIANTA B - AI enhance (personalizovanější):
        # try:
        #     final_response = self.receptionist.process_message(call_sid, user_input)
        # except:
        #     final_response = kb_response['text']
        
        # ============================================================
        # 6. LOG USAGE
        # ============================================================
        
        # Detekuj úspěch
        is_positive = 'ano' in user_lower or 'zajímá' in user_lower or 'jo' in user_lower
        led_to_meeting = 'schůzka' in user_lower or 'sejdeme' in user_lower
        
        if self.last_response_id and self.last_response_id > 0:
            self.response_selector.log_response_success(
                response_id=self.last_response_id,
                was_successful=is_positive,
                led_to_meeting=led_to_meeting
            )
        
        print(f"   🤖 Odpověď: {final_response[:80]}...")
        
        return final_response
    
    def _determine_stage(self, user_input):
        """Urči stage a sub-category"""
        
        user_lower = user_input.lower()
        
        # CLOSING
        if any(w in user_lower for w in ['schůzka', 'sejdeme', 'zítra', 'příští']):
            return 'closing', 'direct_close'
        
        # OBJECTIONS
        if 'nemám čas' in user_lower or 'zaneprázdněný' in user_lower:
            return 'objection', 'no_time'
        
        if 'drahé' in user_lower or 'kolik' in user_lower or 'cena' in user_lower:
            return 'objection', 'no_money'
        
        if 'spokojení' in user_lower or 'už máme' in user_lower:
            return 'objection', 'have_web_satisfied'
        
        if 'nezajímá' in user_lower or 'nechci' in user_lower:
            return 'objection', 'no_interest'
        
        # VALUE (když se ptají)
        if any(w in user_lower for w in ['jak', 'proč', 'co', 'zajímá']):
            return 'value', 'seo_benefit'
        
        # DISCOVERY
        if self.current_stage == 'intro':
            return 'discovery', 'web_check'
        
        # DEFAULT PROGRESSION
        if self.current_stage == 'discovery':
            if self.has_web == False:
                return 'value', 'seo_benefit'
            else:
                return 'value', 'competitor_advantage'
        
        if self.current_stage == 'value':
            return 'closing', 'soft_close'
        
        return self.current_stage, None
    
    def _detect_sentiment(self, text):
        """Detekuj sentiment"""
        text_lower = text.lower()
        
        positive = ['ano', 'jo', 'jasně', 'super', 'zajímá', 'dobré', 'fajn']
        negative = ['ne', 'nechci', 'nezajímá', 'nemám', 'ale', 'problém']
        
        pos = sum(1 for w in positive if w in text_lower)
        neg = sum(1 for w in negative if w in text_lower)
        
        if pos > neg:
            return 'positive'
        elif neg > pos:
            return 'negative'
        else:
            return 'neutral'
    
    def get_call_summary(self):
        """Shrnutí hovoru"""
        return {
            'customer_name': self.customer_name,
            'company_name': self.company_name,
            'has_web': self.has_web,
            'final_stage': self.current_stage,
            'off_topic_count': self.topic_controller.off_topic_count
        }