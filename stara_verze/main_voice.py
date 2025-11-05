from openai import OpenAI
from config import Config
from tts import TextToSpeech
from stt_whisper import WhisperSTT  # <-- ZMĚNA: používáme Whisper!
import sys

class VoiceAssistant:
    def __init__(self):
        """Inicializace hlasového asistenta"""
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.conversation_history = [
            {"role": "system", "content": Config.SYSTEM_PROMPT}
        ]
        
        # TTS a STT systémy
        self.tts = TextToSpeech()
        self.stt = WhisperSTT()  # <-- ZMĚNA: používáme Whisper!
        
        print("🤖 Hlasový AI Asistent inicializován!")
        print(f"📱 Model: {Config.OPENAI_MODEL}")
        print("-" * 50)
    
    def chat_voice(self):
        """
        Poslouchá uživatele, zpracuje a odpoví hlasem
        """
        # 1. Poslouchání uživatele
        user_message = self.stt.listen_once(duration=5)
        
        if not user_message:
            return None
        
        # 2. Zpracování ChatGPT
        try:
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=self.conversation_history,
                temperature=0.7,
                max_tokens=150
            )
            
            ai_message = response.choices[0].message.content
            
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_message
            })
            
            # 3. Odpověď hlasem
            print(f"\n🤖 AI: {ai_message}\n")
            self.tts.speak(ai_message)
            
            return ai_message
            
        except Exception as e:
            error_msg = f"Chyba při komunikaci s AI: {str(e)}"
            print(f"❌ {error_msg}")
            self.tts.speak("Omlouváme se, nastala technická chyba.")
            return None
    
    def cleanup(self):
        """Uklidí resources"""
        self.tts.cleanup()


def main():
    """Hlavní funkce - plně hlasová konverzace"""
    print("=" * 50)
    print("🎙️  AI TELEFONNÍ ASISTENT - HLASOVÝ REŽIM")
    print("=" * 50)
    
    # Kontrola API klíčů
    if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == 'sk-your-api-key-here':
        print("❌ CHYBA: Nastavte OPENAI_API_KEY v .env souboru!")
        sys.exit(1)
    
    # Vytvoření asistenta
    assistant = VoiceAssistant()
    
    print("\n🎤 HLASOVÝ REŽIM aktivní!")
    print("   Po každé odpovědi AI můžeš mluvit znovu.")
    print("   Stiskni Ctrl+C pro ukončení.\n")
    
    # Úvodní pozdrav
    assistant.tts.speak("Ahoj, jsem tvůj AI asistent. Jak ti můžu pomoct?")
    
    # Hlavní smyčka
    try:
        while True:
            assistant.chat_voice()
            
    except KeyboardInterrupt:
        print("\n\n👋 Ukončeno uživatelem. Nashledanou!")
        assistant.tts.speak("Nashledanou!")
        
    finally:
        assistant.cleanup()


if __name__ == "__main__":
    main()