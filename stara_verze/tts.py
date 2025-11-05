from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from config import Config
import pygame
import io
import sys

class TextToSpeech:
    def __init__(self):
        """Inicializace TTS systému"""
        if not Config.ELEVENLABS_API_KEY or Config.ELEVENLABS_API_KEY == 'your-elevenlabs-api-key-here':
            print("❌ CHYBA: Nastavte ELEVENLABS_API_KEY v .env souboru!")
            print("   Získejte klíč na: https://elevenlabs.io/app/settings/api-keys")
            sys.exit(1)
            
        self.client = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)
        
        # Inicializace pygame pro přehrávání audia
        pygame.mixer.init()
        
        print("🔊 Text-to-Speech inicializován!")
        print(f"🎙️ Voice ID: {Config.ELEVENLABS_VOICE_ID}")
    
    def speak(self, text):
        """
        Převede text na řeč a přehraje ho
        
        Args:
            text (str): Text k převedení na řeč
        """
        try:
            print(f"🔊 Generuji řeč: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            
            # Generování řeči přes ElevenLabs API
            audio_generator = self.client.text_to_speech.convert(
                voice_id=Config.ELEVENLABS_VOICE_ID,
                optimize_streaming_latency="0",
                output_format="mp3_22050_32",
                text=text,
                model_id="eleven_multilingual_v2",  # Podporuje češtinu!
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.8,
                    style=0.0,
                    use_speaker_boost=True,
                ),
            )
            
            # Převedení generátoru na bytes
            audio_bytes = b"".join(audio_generator)
            
            # Přehrání audia
            self._play_audio(audio_bytes)
            
            print("✅ Řeč přehrána")
            
        except Exception as e:
            print(f"❌ Chyba při generování řeči: {str(e)}")
    
    def _play_audio(self, audio_bytes):
        """
        Přehraje audio z bytes
        
        Args:
            audio_bytes (bytes): Audio data v MP3 formátu
        """
        try:
            # Vytvoření in-memory souboru
            audio_io = io.BytesIO(audio_bytes)
            
            # Načtení a přehrání
            pygame.mixer.music.load(audio_io)
            pygame.mixer.music.play()
            
            # Čekání na dokončení přehrávání
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
        except Exception as e:
            print(f"❌ Chyba při přehrávání audia: {str(e)}")
    
    def cleanup(self):
        """Uklidí resources"""
        pygame.mixer.quit()