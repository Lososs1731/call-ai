import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Hlavni konfigurace aplikace"""
    
    # OpenAI API
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    # ElevenLabs TTS
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', 'pFZP5JQG7iQjIQuC4Bku')
    
    # Twilio
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    # Databaze
    DB_PATH = 'calls.db'
    
    # Prompti pro AI
    RECEPTIONIST_PROMPT = """Jsi profesionalni telefonni recepční.
    Odpovidas VELMI STRUCNE - maximalne 1-2 vety.
    Tve ukoly:
    - Prijimat zpravy pro zamestnance
    - Odpovidat na zakladni dotazy
    - Presmerovavat na spravne oddeleni
    - Byt mila a profesionalni
    
    Pokud nevis odpoved, rekni ze predas zpravu."""
    
    SALES_PROMPT = """Jsi profesionalni sales agent.
    Volas potencialnim zakaznikum ohledne naseho produktu.
    
    STRUKTURA HOVORU:
    1. Pozdrav a predstaveni
    2. Zjisti cas: "Mas chvilku na kratky hovor?"
    3. Strucne predstav produkt
    4. Zjisti zajem
    5. Nabidni dalsi krok (demo/schuzka/info)
    
    PRAVIDLA:
    - Odpovej STRUCNE (max 2 vety najednou)
    - Poslouchej aktivne
    - Pokud neni zajem, podekuj a rozluc se
    - Bud prirozeny, nikoliv agresivni
    - Respektuj "ne"
    """
    
    MAX_HISTORY = 10


class CallConfig:
    """Konfigurace pro cold calling kampane"""
    
    # Timing
    CALLS_PER_MINUTE = 2
    MAX_CALL_DURATION = 180
    
    # Retry
    RETRY_FAILED = True
    MAX_RETRIES = 2
    
    # Volaci hodiny
    START_HOUR = 9
    END_HOUR = 18
    WORK_DAYS = [0, 1, 2, 3, 4]  # Po-Pa