"""
ChatGPT integrace
OPTIMALIZOVÁNO: Rychlejší odpovědi, timeout
"""

from openai import OpenAI
from config import Config


class AIEngine:
    """Engine pro komunikaci s ChatGPT"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=Config.OPENAI_API_KEY,
            timeout=5.0  # ✅ NOVÉ: 5s timeout (standardně 60s!)
        )
        self.conversations = {}
    
    def start_conversation(self, session_id, system_prompt):
        """
        Zahaji novou konverzaci
        
        Args:
            session_id: Unikatni ID konverzace (napr. call_sid)
            system_prompt: Systemovy prompt definujici chovani AI
        """
        self.conversations[session_id] = [
            {"role": "system", "content": system_prompt}
        ]
    
    def get_response(self, session_id, user_message):
        """
        Ziska odpoved od AI
        OPTIMALIZOVÁNO: Rychlejší s timeout
        
        Args:
            session_id: ID konverzace
            user_message: Zprava od uzivatele
            
        Returns:
            str: Odpoved od AI
        """
        if session_id not in self.conversations:
            raise ValueError(f"Konverzace {session_id} neexistuje")
        
        # Pridani user zpravy
        self.conversations[session_id].append({
            "role": "user",
            "content": user_message
        })
        
        # ⚡ OPTIMALIZOVANÉ VOLÁNÍ API
        try:
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=self.conversations[session_id],
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS,
                timeout=5.0,  # ✅ NOVÉ: 5s timeout
                stream=False  # ✅ NOVÉ: vypnuto streaming (rychlejší pro krátké odpovědi)
            )
            
            ai_message = response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"⚠️  OpenAI timeout/error: {e}")
            # Fallback odpověď
            ai_message = "Promiňte, momentálně mám technické potíže. Můžete to zkusit znovu?"
        
        # Oriznutie prilis dlouhych odpovedi
        if len(ai_message) > 200:
            last_dot = ai_message[:200].rfind('.')
            if last_dot > 0:
                ai_message = ai_message[:last_dot + 1]
        
        # Pridani AI odpovedi do historie
        self.conversations[session_id].append({
            "role": "assistant",
            "content": ai_message
        })
        
        # Omezeni velikosti historie
        self._trim_history(session_id)
        
        return ai_message
    
    def end_conversation(self, session_id):
        """
        Ukonci konverzaci a vrati jeji historii
        
        Returns:
            list: Historie konverzace
        """
        if session_id in self.conversations:
            history = self.conversations[session_id]
            del self.conversations[session_id]
            return history
        return []
    
    def _trim_history(self, session_id):
        """Orizne historii na maximalni delku"""
        if len(self.conversations[session_id]) > Config.MAX_HISTORY + 1:
            # Zachovej system prompt + poslednich N zprav
            self.conversations[session_id] = [
                self.conversations[session_id][0]
            ] + self.conversations[session_id][-Config.MAX_HISTORY:]