"""
Text-to-Speech engine
Prevadi text na rec pomoci ElevenLabs
"""

import os
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from config import Config


class TTSEngine:
    """Engine pro generovani reci z textu"""
    
    def __init__(self):
        print("Inicializuji TTSEngine...")
        try:
            self.client = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)
            self._ensure_cache_dir()
            print("  ✓ TTSEngine OK")
        except Exception as e:
            print(f"  ✗ TTSEngine chyba: {e}")
            raise
    
    def generate(self, text, use_cache=True):
        """Vygeneruje audio z textu"""
        print(f"\n[TTSEngine] generate('{text[:50]}...')")
        
        try:
            cache_file = self._get_cache_path(text)
            
            if use_cache and os.path.exists(cache_file):
                print(f"  ✓ Cache hit: {cache_file}")
                return self._get_url_from_path(cache_file)
            
            print("  Generuji audio...")
            
            # OPTIMALIZACE: Nizsi latence
            audio_gen = self.client.text_to_speech.convert(
                voice_id=Config.ELEVENLABS_VOICE_ID,
                optimize_streaming_latency="3",  # Zmena z 4 na 3 (rychlejsi)

                text=text,
                model_id="eleven_turbo_v2_5",  # Turbo je nejrychlejsi
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.0,
                    use_speaker_boost=True,
                ),
                
            )
            
            audio_bytes = b"".join(audio_gen)
            
            with open(cache_file, 'wb') as f:
                f.write(audio_bytes)
            
            print(f"  ✓ Audio ulozeno: {cache_file} ({len(audio_bytes)} bytes)")
            
            url = self._get_url_from_path(cache_file)
            print(f"  URL: {url}")
            return url
        
        except Exception as e:
            print(f"  ✗ TTS chyba: {e}")
            return None
    
    def _ensure_cache_dir(self):
        """Vytvori slozku pro cache"""
        os.makedirs(Config.AUDIO_CACHE_DIR, exist_ok=True)
        print(f"  Cache dir: {Config.AUDIO_CACHE_DIR}")
    
    def _get_cache_path(self, text):
        """Vrati cestu k cache souboru"""
        filename = f"tts_{abs(hash(text))}.mp3"
        return os.path.join(Config.AUDIO_CACHE_DIR, filename)
    
    def _get_url_from_path(self, path):
        """Prevede filepath na URL"""
        # OPRAV: Normalizuj cestu pro URL (pouzij forward slash)
        # Odeber prvni "static/" a pridej zpet s forward slash
        path_parts = path.replace(os.sep, '/').split('/')
        
        # Najdi 'static' a vezmi vse za nim
        if 'static' in path_parts:
            static_index = path_parts.index('static')
            relative_path = '/'.join(path_parts[static_index+1:])
            url = f"/static/{relative_path}"
        else:
            # Fallback
            url = f"/{path.replace(os.sep, '/')}"
        
        return url