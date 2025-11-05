"""
Hlavni konfigurace aplikace
Obsahuje nastaveni API klicu a globalnich parametru
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Zakladni konfigurace aplikace"""
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    # ElevenLabs
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', 'pFZP5JQG7iQjIQuC4Bku')
    
    # Twilio
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    # Databaze
    DB_PATH = 'data/calls.db'
    
    # Audio cache
    AUDIO_CACHE_DIR = 'static/audio'
    
    # Konverzace
    MAX_HISTORY = 10
    MAX_TOKENS = 60
    TEMPERATURE = 0.7
    
    # Server
    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = 5000
    DEBUG = True

class CallConfig:
    """Konfigurace pro cold calling"""
    
    # Rate limiting
    CALLS_PER_MINUTE = 4  # Změna z 2 na 4 (15s delay místo 30s)
    MAX_CALL_DURATION = 180
    
    # Retry
    RETRY_FAILED = True
    MAX_RETRIES = 2
    RETRY_DELAY = 300
    
    # Volaci hodiny - PRO TESTOVANI
    START_HOUR = 8
    END_HOUR = 23
    WORK_DAYS = [0, 1, 2, 3, 4, 5, 6]
    
    # Recording
    RECORD_CALLS = True
    SAVE_TRANSCRIPTS = True