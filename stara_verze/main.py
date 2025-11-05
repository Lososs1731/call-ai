from openai import OpenAI
from config import Config
from tts import TextToSpeech
import sys

class AIAssistant:
    def __init__(self, enable_tts=True):
        """
        Inicializace AI asistenta
        
        Args:
            enable_tts (bool): Zapnout/vypnout TTS
        """
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.conversation_history = [
            {"role": "system", "content": Config.SYSTEM_PROMPT}
        ]
        
        # TTS systém
        self.enable_tts = enable_tts
        if self.enable_tts:
            self.tts = TextToSpeech()
        
        print("🤖 AI Asistent inicializován!")
        print(f"📱 Model: {Config.OPENAI_MODEL}")
        print(f"🔊 TTS: {'Zapnuto' if enable_tts else 'Vypnuto'}")
        print("-" * 50)
    
    def chat(self, user_message, speak=True):
        """
        Pošle zprávu AI a vrátí odpověď
        
        Args:
            user_message (str): Zpráva od uživatele
            speak (bool): Přehrát odpověď pomocí TTS
            
        Returns:
            str: Odpověď od AI
        """
        try:
            # Přidání uživatelské zprávy do historie
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Volání ChatGPT API
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=self.conversation_history,
                temperature=0.7,
                max_tokens=150
            )
            
            # Získání odpovědi
            ai_message = response.choices[0].message.content
            
            # Přidání AI odpovědi do historie
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_message
            })
            
            # Omezení délky historie
            self._trim_history()
            
            # Přehrání odpovědi pomocí TTS
            if speak and self.enable_tts:
                self.tts.speak(ai_message)
            
            return ai_message
            
        except Exception as e:
            error_msg = f"Chyba při komunikaci s AI: {str(e)}"
            print(f"❌ {error_msg}")
            return "Omlouváme se, nastala technická chyba."
    
    def _trim_history(self):
        """Omezí délku historie konverzace"""
        if len(self.conversation_history) > Config.MAX_CONVERSATION_HISTORY + 1:
            self.conversation_history = [
                self.conversation_history[0]
            ] + self.conversation_history[-(Config.MAX_CONVERSATION_HISTORY):]
    
    def reset_conversation(self):
        """Resetuje konverzaci na začátek"""
        self.conversation_history = [
            {"role": "system", "content": Config.SYSTEM_PROMPT}
        ]
        print("🔄 Konverzace resetována")
    
    def cleanup(self):
        """Uklidí resources"""
        if self.enable_tts:
            self.tts.cleanup()


def main():
    """Hlavní funkce - interaktivní chat s TTS"""
    print("=" * 50)
    print("🎙️  AI TELEFONNÍ ASISTENT - TTS REŽIM")
    print("=" * 50)
    
    # Kontrola API klíčů
    if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == 'sk-your-api-key-here':
        print("❌ CHYBA: Nastavte OPENAI_API_KEY v .env souboru!")
        sys.exit(1)
    
    # Vytvoření asistenta s TTS
    assistant = AIAssistant(enable_tts=True)
    
    print("\n💬 Můžete začít chatovat! AI vám bude odpovídat HLASEM!")
    print("   Příkazy:")
    print("   - 'reset' - nová konverzace")
    print("   - 'tts off' - vypnout hlas")
    print("   - 'tts on' - zapnout hlas")
    print("   - 'quit' - ukončit\n")
    
    # Hlavní chat smyčka
    try:
        while True:
            try:
                # Vstup od uživatele
                user_input = input("VY: ").strip()
                
                # Prázdný vstup
                if not user_input:
                    continue
                
                # Příkazy
                if user_input.lower() == 'quit':
                    print("👋 Nashledanou!")
                    break
                
                if user_input.lower() == 'reset':
                    assistant.reset_conversation()
                    continue
                
                if user_input.lower() == 'tts off':
                    assistant.enable_tts = False
                    print("🔇 TTS vypnuto")
                    continue
                
                if user_input.lower() == 'tts on':
                    assistant.enable_tts = True
                    print("🔊 TTS zapnuto")
                    continue
                
                # Odeslání zprávy AI
                print("AI: ", end="", flush=True)
                response = assistant.chat(user_input)
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\n\n👋 Přerušeno uživatelem. Nashledanou!")
                break
                
    finally:
        # Cleanup
        assistant.cleanup()


if __name__ == "__main__":
    main()