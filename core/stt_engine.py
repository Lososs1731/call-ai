"""
Speech-to-Text engine
Prevadi rec na text pomoci OpenAI Whisper
"""

import tempfile
import wave
import pyaudio
from openai import OpenAI
from config import Config


class STTEngine:
    """Engine pro rozpoznavani reci"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.rate = 16000
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
    
    def listen(self, duration=5):
        """
        Nahraje audio a prevede na text
        
        Args:
            duration: Delka nahravani v sekundach
            
        Returns:
            str: Rozpoznany text
        """
        print(f"Posloucham {duration}s...")
        
        audio_interface = pyaudio.PyAudio()
        
        try:
            # Nahravani
            stream = audio_interface.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            frames = []
            for i in range(0, int(self.rate / self.chunk * duration)):
                data = stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)
                
                if i % 10 == 0:
                    print(".", end="", flush=True)
            
            print(" OK")
            
            stream.stop_stream()
            stream.close()
            
            # Ulozeni do docasneho souboru
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
                temp_path = temp.name
                
                wf = wave.open(temp_path, 'wb')
                wf.setnchannels(self.channels)
                wf.setsampwidth(audio_interface.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(frames))
                wf.close()
            
            # Prepis pomoci Whisper
            print("Zpracovavam...")
            
            with open(temp_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="cs"
                )
            
            # Smazani docasneho souboru
            import os
            os.unlink(temp_path)
            
            text = transcript.text.strip()
            print(f"Rozpoznano: {text}")
            
            return text if text else None
            
        except Exception as e:
            print(f"Chyba STT: {e}")
            return None
            
        finally:
            audio_interface.terminate()