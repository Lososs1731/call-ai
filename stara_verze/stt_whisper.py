from openai import OpenAI
import pyaudio
import wave
import tempfile
import os
from config import Config

class WhisperSTT:
    """Speech-to-Text pomocí OpenAI Whisper"""
    
    def __init__(self):
        """Inicializace Whisper STT"""
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Audio parametry
        self.rate = 16000
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        
        print("🎤 Speech-to-Text inicializován (OpenAI Whisper)!")
        print(f"🌍 Jazyk: čeština")
    
    def listen_once(self, duration=5):
        """
        Nahraje audio a přepíše ho pomocí Whisper
        
        Args:
            duration (int): Délka nahrávání v sekundách
            
        Returns:
            str: Přepsaný text
        """
        print(f"\n🎤 Poslouchám {duration} sekund... (mluv teď)")
        
        audio_interface = pyaudio.PyAudio()
        
        try:
            # Otevření mikrofonu
            stream = audio_interface.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            # Nahrávání
            frames = []
            for i in range(0, int(self.rate / self.chunk * duration)):
                data = stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)
                
                # Progress indikátor
                if i % 10 == 0:
                    print("🔴", end="", flush=True)
            
            print(" ✅")
            
            # Ukončení nahrávání
            stream.stop_stream()
            stream.close()
            
            # Uložení do dočasného WAV souboru
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_filename = temp_audio.name
                
                wf = wave.open(temp_filename, 'wb')
                wf.setnchannels(self.channels)
                wf.setsampwidth(audio_interface.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(frames))
                wf.close()
            
            # Přepis pomocí Whisper
            print("🔄 Zpracovávám...")
            
            with open(temp_filename, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="cs"  # Čeština
                )
            
            # Smazání dočasného souboru
            os.unlink(temp_filename)
            
            # Získání textu
            text = transcript.text.strip()
            
            if text:
                print(f"✅ Rozpoznáno: {text}")
                return text
            else:
                print("❌ Nic nebylo rozpoznáno")
                return None
                
        except Exception as e:
            print(f"❌ Chyba při rozpoznávání řeči: {str(e)}")
            return None
            
        finally:
            audio_interface.terminate()