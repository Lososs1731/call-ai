"""
AI Telefonni Asistent - Server
Zpracovava prichozi i odchozi hovory pres Twilio
"""

from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from openai import OpenAI
from config import Config
try:
    from database import CallDB
except ImportError:
    # Fallback - server bez databáze (jen pro test)
    print("VAROVÁNÍ: Databáze není dostupná, běží bez ukládání")
    class CallDB:
        def __init__(self): pass
        def add_call(self, data): pass
        def update_call(self, sid, updates): pass
        def add_contact(self, data): return True
        def get_contacts(self, status='new', limit=100): return []
        def update_contact(self, phone, updates): pass
        def get_stats(self): return {}
from datetime import datetime
import os
import time

app = Flask(__name__)

# Globalni konverzacni historie pro aktivni hovory
conversations = {}

# Inicializace klientu
openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
twilio_client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
db = CallDB()


@app.route("/inbound", methods=['POST'])
def inbound_call():
    """Webhook pro prichozi hovory (recepcni rezim)"""
    call_sid = request.values.get('CallSid')
    caller_number = request.values.get('From')
    
    print(f"\nPrichozi hovor: {caller_number}")
    
    # Ulozeni hovoru do databaze
    db.add_call({
        'sid': call_sid,
        'type': 'inbound',
        'direction': 'inbound',
        'phone': caller_number
    })
    
    # Inicializace konverzace
    if call_sid not in conversations:
        conversations[call_sid] = [
            {"role": "system", "content": Config.RECEPTIONIST_PROMPT}
        ]
    
    response = VoiceResponse()
    greeting = "Ahoj, jak ti muzu pomoct?"
    
    # Generovani TTS
    audio_url = generate_tts(greeting)
    
    if audio_url:
        response.play(audio_url)
    else:
        response.say(greeting, language='cs-CZ', voice='woman')
    
    # Gather pro nasledujici vstup
    gather = Gather(
        input='speech',
        action='/process',
        language='cs-CZ',
        speech_timeout='auto',
        timeout=3
    )
    
    response.append(gather)
    response.redirect('/inbound')
    
    return Response(str(response), mimetype='text/xml')


@app.route("/outbound", methods=['POST'])
def outbound_call():
    """Webhook pro odchozi hovory (cold calling rezim)"""
    call_sid = request.values.get('CallSid')
    contact_name = request.values.get('name', 'pane')
    company = request.values.get('company', '')
    
    print(f"\nOdchozi hovor: {contact_name}")
    
    # Personalizovany pozdrav
    if company:
        greeting = f"Dobry den, {contact_name} z {company}, volam z AI Assistents."
    else:
        greeting = f"Dobry den, {contact_name}, volam z AI Assistents."
    
    # Inicializace sales konverzace
    if call_sid not in conversations:
        conversations[call_sid] = [
            {"role": "system", "content": Config.SALES_PROMPT},
            {"role": "assistant", "content": greeting}
        ]
    
    response = VoiceResponse()
    
    audio_url = generate_tts(greeting)
    
    if audio_url:
        response.play(audio_url)
    else:
        response.say(greeting, language='cs-CZ', voice='woman')
    
    gather = Gather(
        input='speech',
        action='/process',
        language='cs-CZ',
        speech_timeout='auto',
        timeout=3
    )
    
    response.append(gather)
    
    return Response(str(response), mimetype='text/xml')


@app.route("/process", methods=['POST'])
def process_speech():
    """Zpracovani reci od uzivatele (spolecne pro oba rezimy)"""
    call_sid = request.values.get('CallSid')
    user_input = request.values.get('SpeechResult', '')
    
    print(f"Uzivatel: {user_input}")
    
    response = VoiceResponse()
    
    if not user_input:
        response.say("Nerozumel jsem, zkus to znovu.", language='cs-CZ', voice='woman')
        response.redirect('/inbound')
        return Response(str(response), mimetype='text/xml')
    
    # Ziskani AI odpovedi
    start = time.time()
    ai_reply = get_ai_response(call_sid, user_input)
    ai_time = time.time() - start
    
    print(f"AI ({ai_time:.2f}s): {ai_reply}")
    
    # Generovani TTS
    tts_start = time.time()
    audio_url = generate_tts(ai_reply)
    tts_time = time.time() - tts_start
    
    print(f"TTS ({tts_time:.2f}s)")
    print(f"Celkem: {time.time() - start:.2f}s\n")
    
    if audio_url:
        response.play(audio_url)
    else:
        response.say(ai_reply, language='cs-CZ', voice='woman')
    
    # Dalsi gather
    gather = Gather(
        input='speech',
        action='/process',
        language='cs-CZ',
        speech_timeout='auto',
        timeout=3
    )
    
    response.append(gather)
    
    # Fallback podle typu hovoru
    if call_sid in conversations:
        first_msg = conversations[call_sid][0]['content']
        if 'sales' in first_msg.lower():
            response.redirect('/outbound')
        else:
            response.redirect('/inbound')
    
    return Response(str(response), mimetype='text/xml')


def get_ai_response(call_sid, user_message):
    """Ziska odpoved od ChatGPT"""
    try:
        if call_sid not in conversations:
            conversations[call_sid] = [
                {"role": "system", "content": Config.RECEPTIONIST_PROMPT}
            ]
        
        conversations[call_sid].append({
            "role": "user",
            "content": user_message
        })
        
        response = openai_client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=conversations[call_sid],
            temperature=0.7,
            max_tokens=60
        )
        
        ai_message = response.choices[0].message.content.strip()
        
        # Oriznutie dlouhych odpovedi
        if len(ai_message) > 200:
            last_dot = ai_message[:200].rfind('.')
            if last_dot > 0:
                ai_message = ai_message[:last_dot + 1]
        
        conversations[call_sid].append({
            "role": "assistant",
            "content": ai_message
        })
        
        # Omezeni historie
        if len(conversations[call_sid]) > Config.MAX_HISTORY + 1:
            conversations[call_sid] = [
                conversations[call_sid][0]
            ] + conversations[call_sid][-Config.MAX_HISTORY:]
        
        return ai_message
        
    except Exception as e:
        print(f"Chyba AI: {e}")
        return "Omlouvam se, nastala chyba."


def generate_tts(text):
    """Generuje TTS pomoci ElevenLabs"""
    try:
        from elevenlabs.client import ElevenLabs
        from elevenlabs import VoiceSettings
        
        # Cache pro opakujici se fraze
        cache_file = f"static/cache_{abs(hash(text))}.mp3"
        if os.path.exists(cache_file):
            return f"/static/{os.path.basename(cache_file)}"
        
        client = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)
        
        audio_gen = client.text_to_speech.convert(
            voice_id=Config.ELEVENLABS_VOICE_ID,
            optimize_streaming_latency="4",
            output_format="mp3_22050_32",
            text=text,
            model_id="eleven_turbo_v2_5",
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.0,
                use_speaker_boost=True,
            ),
        )
        
        audio_bytes = b"".join(audio_gen)
        os.makedirs('static', exist_ok=True)
        
        with open(cache_file, 'wb') as f:
            f.write(audio_bytes)
        
        return f"/static/{os.path.basename(cache_file)}"
        
    except Exception as e:
        print(f"TTS chyba: {e}")
        return None


@app.route("/call-status", methods=['POST'])
def call_status():
    """Callback pro aktualizaci statusu hovoru"""
    call_sid = request.values.get('CallSid')
    status = request.values.get('CallStatus')
    duration = request.values.get('CallDuration', 0)
    
    print(f"Hovor {call_sid}: {status} ({duration}s)")
    
    # Aktualizace databaze
    db.update_call(call_sid, {
        'status': status,
        'duration': int(duration),
        'end_time': datetime.now().isoformat()
    })
    
    # Smazani konverzace z pameti
    if call_sid in conversations:
        # Ulozeni transkriptu do databaze
        db.update_call(call_sid, {
            'transcript': str(conversations[call_sid])
        })
        del conversations[call_sid]
    
    return Response('OK', mimetype='text/plain')


if __name__ == "__main__":
    print("=" * 50)
    print("AI TELEFONNI ASISTENT - SERVER")
    print("=" * 50)
    print(f"Server: http://localhost:5000")
    print(f"Cislo: {Config.TWILIO_PHONE_NUMBER}")
    print("\nWebhooky:")
    print("  Prichozi: /inbound")
    print("  Odchozi: /outbound")
    print("  Status: /call-status")
    print("=" * 50)
    
    app.run(debug=True, port=5000)