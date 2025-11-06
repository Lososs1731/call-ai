"""
Konfigurace aplikace
OPTIMALIZOVÁNO: Rychlejší AI odpovědi + opravený AUDIO_CACHE_DIR + WORK_DAYS
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Hlavni konfigurace"""
    
    # Twilio
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = 'gpt-4o-mini'  # ✅ Rychlejší model
    TEMPERATURE = 0.7
    MAX_TOKENS = 100  # ✅ Kratší odpovědi
    MAX_HISTORY = 8
    
    # ElevenLabs
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', 'EXAVITQu4vr4xnSDxMaL')  # Sarah
    
    # Server
    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = 5000
    DEBUG = True
    
    # Database
    DB_PATH = 'data/calls.db'
    
    # Audio cache
    AUDIO_CACHE_DIR = 'static/audio'
    AUDIO_CACHE_ENABLED = True


class CallConfig:
    """Konfigurace pro volání"""
    
    RECORD_CALLS = True
    MAX_CALL_DURATION = 300  # 5 minut
    SPEECH_TIMEOUT = 'auto'
    GATHER_TIMEOUT = 8
    MIN_CONFIDENCE = 0.1
    
    # ✅ PŘIDÁNO: Pracovní doba pro cold calling
    WORK_DAYS = [0, 1, 2, 3, 4]  # ✅ Pondělí-Pátek (0=Po, 4=Pá)
    WORK_HOURS_START = 1  # ✅ Od 9:00
    WORK_HOURS_END = 23   # ✅ Do 17:00
    DELAY_BETWEEN_CALLS = 5  # ✅ 5s pauza mezi hovory


# Export
from .prompts import Prompts

__all__ = ['Config', 'CallConfig', 'Prompts']