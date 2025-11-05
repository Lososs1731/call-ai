"""
Lokalni hlasovy chat (pro testovani)
"""

from core import AIEngine, TTSEngine, STTEngine
from config import Prompts

ai = AIEngine()
tts = TTSEngine()
stt = STTEngine()

session = "local-test"
ai.start_conversation(session, Prompts.RECEPTIONIST)

print("Hlasovy chat (Ctrl+C pro ukonceni)")
print("-" * 40)

# Pozdrav
greeting = "Ahoj, jak ti muzu pomoct?"
print(f"AI: {greeting}")
tts.generate(greeting)

try:
    while True:
        # Poslouchat
        user_input = stt.listen(duration=5)
        
        if not user_input:
            continue
        
        print(f"Ty: {user_input}")
        
        # AI odpoved
        reply = ai.get_response(session, user_input)
        print(f"AI: {reply}")
        
        # TTS
        tts.generate(reply)
        
except KeyboardInterrupt:
    print("\n\nUkonceno")