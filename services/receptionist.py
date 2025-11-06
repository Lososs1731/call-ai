"""
Receptionist Service - Hlavní AI asistent pro příchozí hovory
OPRAVENO: TwiML vs Text, process_speech místo process_message
"""

from twilio.twiml.voice_response import VoiceResponse, Gather
from core import AIEngine, TTSEngine
from database import CallDB
from config import Config, Prompts
import time
from datetime import datetime


class ReceptionistService:
    """AI Receptionist pro zpracování příchozích hovorů"""
    
    def __init__(self):
        self.ai = AIEngine()
        self.tts = TTSEngine()
        self.db = CallDB()
        
        print("✅ ReceptionistService inicializován")
    
    def handle_call(self, call_sid, from_number):
        """
        Zpracuje příchozí hovor
        
        Args:
            call_sid: Twilio Call SID
            from_number: Telefonní číslo volajícího
            
        Returns:
            str: TEXT (ne TwiML!) pro TTS
        """
        
        print(f"\n{'='*50}")
        print(f"PŘÍCHOZÍ HOVOR")
        print(f"Od: {from_number}")
        print(f"CallSid: {call_sid}")
        print(f"{'='*50}\n")
        
        # Ulož do databáze
        print(f"[ReceptionistService] handle_call({call_sid})")
        print(f"  Ukládám do DB...")
        
        self.db.add_call({
            'sid': call_sid,
            'phone': from_number,
            'direction': 'inbound',
            'status': 'in-progress',
            'type': 'inbound'
        })
        
        print(f"  ✓ Uloženo do DB")
        
        # Zahaj konverzaci
        print(f"  Zahajuji konverzaci...")
        
        self.ai.start_conversation(
            session_id=call_sid,
            system_prompt=Prompts.RECEPTIONIST
        )
        
        greeting = self.ai.get_response(
            session_id=call_sid,
            user_message="Zákazník zvedl telefon."
        )
        
        print(f"  ✓ Konverzace zahájena")
        print(f"  Vracím pozdrav: {greeting}\n")
        
        # ✅ VRAŤ JEN TEXT, NE TwiML!
        return greeting
    
    def process_speech(self, call_sid, speech_result):
        """
        Zpracuje řeč uživatele a vygeneruje odpověď
        
        Args:
            call_sid: Call SID
            speech_result: Text od Twilio STT
            
        Returns:
            str: AI odpověď (text)
        """
        
        print(f"\n[ReceptionistService] process_speech({call_sid})")
        print(f"  Uživatel řekl: '{speech_result}'")
        
        # Pokud je prázdné
        if not speech_result or speech_result.strip() == "":
            print(f"  ⚠️  Prázdný vstup")
            return "Nerozuměl jsem. Můžete to zopakovat?"
        
        # AI odpověď
        print(f"  Generuji AI odpověď...")
        
        ai_response = self.ai.get_response(
            session_id=call_sid,
            user_message=speech_result
        )
        
        print(f"  AI odpověď: {ai_response}")
        
        return ai_response
    
    def process_message(self, call_sid, user_input):
        """
        Alias pro process_speech (kvůli kompatibilitě s api/server.py)
        """
        return self.process_speech(call_sid, user_input)
    
    def end_call(self, call_sid, duration):
        """
        Ukončí hovor a aktualizuje databázi
        
        Args:
            call_sid: Call SID
            duration: Délka hovoru v sekundách
        """
        
        print(f"\n[ReceptionistService] end_call({call_sid}, {duration}s)")
        
        # Ukončit konverzaci
        history = self.ai.end_conversation(call_sid)
        messages_count = len(history) if history else 0
        
        print(f"  Konverzace ukončena ({messages_count} zpráv)")
        
        # Aktualizovat DB
        try:
            self.db.cursor.execute("""
                UPDATE calls 
                SET status = ?, duration = ?
                WHERE sid = ?
            """, ('completed', duration, call_sid))
            self.db.conn.commit()
            print(f"  ✓ DB aktualizována")
        except Exception as e:
            print(f"  ⚠️  DB error: {e}")