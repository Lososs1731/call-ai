from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from openai import OpenAI
from config import Config
import os
import time
import threading

app = Flask(__name__)

conversations = {}
openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
twilio_client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)


@app.route("/voice", methods=['POST'])
def voice():
    """Příjem příchozího hovoru"""
    call_sid = request.values.get('CallSid')
    
    if call_sid not in conversations:
        conversations[call_sid] = [
            {"role": "system", "content": Config.SYSTEM_PROMPT}
        ]
    
    response = VoiceResponse()
    welcome_text = "Ahoj, jak ti můžu pomoct?"
    
    audio_url = generate_tts(welcome_text)
    
    if audio_url:
        response.play(audio_url)
    else:
        response.say(welcome_text, language='cs-CZ', voice='woman')
    
    gather = Gather(
        input='speech',
        action='/process-speech',
        language='cs-CZ',
        speech_timeout='auto',  # ⚡ AUTO = inteligentní detekce
        timeout=3,
        profanity_filter=False  # Rychlejší zpracování
    )
    
    response.append(gather)
    response.redirect('/voice')
    
    return Response(str(response), mimetype='text/xml')


@app.route("/process-speech", methods=['POST'])
def process_speech():
    """Zpracování řeči od uživatele"""
    call_sid = request.values.get('CallSid')
    speech_result = request.values.get('SpeechResult', '')
    
    print(f"\n👤 Uživatel: {speech_result}")
    
    response = VoiceResponse()
    
    if not speech_result:
        response.say("Nerozuměl jsem.", language='cs-CZ', voice='woman')
        response.redirect('/voice')
        return Response(str(response), mimetype='text/xml')
    
    start_time = time.time()
    
    # Získání odpovědi
    ai_response = get_ai_response(call_sid, speech_result)
    
    ai_time = time.time() - start_time
    print(f"🤖 AI ({ai_time:.2f}s): {ai_response}")
    
    # TTS
    tts_start = time.time()
    audio_url = generate_tts(ai_response)
    tts_time = time.time() - tts_start
    
    print(f"🔊 TTS ({tts_time:.2f}s)")
    print(f"⏱️ Celkem: {time.time() - start_time:.2f}s\n")
    
    if audio_url:
        response.play(audio_url)
    else:
        response.say(ai_response, language='cs-CZ', voice='woman')
    
    gather = Gather(
        input='speech',
        action='/process-speech',
        language='cs-CZ',
        speech_timeout='auto',
        timeout=3,
        profanity_filter=False
    )
    
    response.append(gather)
    response.redirect('/voice')
    
    return Response(str(response), mimetype='text/xml')


def get_ai_response(call_sid, user_message):
    """Získá odpověď od ChatGPT - OPTIMALIZOVÁNO"""
    try:
        if call_sid not in conversations:
            conversations[call_sid] = [
                {"role": "system", "content": Config.SYSTEM_PROMPT}
            ]
        
        conversations[call_sid].append({
            "role": "user",
            "content": user_message
        })
        
        # ⚡ Streaming pro rychlejší TTFB (Time To First Byte)
        stream = openai_client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=conversations[call_sid],
            temperature=0.7,
            max_tokens=60,  # O trochu víc pro přirozenější odpovědi
            presence_penalty=0.6,
            frequency_penalty=0.6,
            stream=False  # Pro telefonní hovory je celá odpověď lepší
        )
        
        ai_message = stream.choices[0].message.content.strip()
        
        # Oříznutí příliš dlouhých odpovědí
        if len(ai_message) > 200:
            # Najdi konec věty
            last_period = ai_message[:200].rfind('.')
            if last_period > 0:
                ai_message = ai_message[:last_period + 1]
        
        conversations[call_sid].append({
            "role": "assistant",
            "content": ai_message
        })
        
        # Omezení historie
        if len(conversations[call_sid]) > Config.MAX_CONVERSATION_HISTORY + 1:
            conversations[call_sid] = [
                conversations[call_sid][0]
            ] + conversations[call_sid][-(Config.MAX_CONVERSATION_HISTORY):]
        
        return ai_message
        
    except Exception as e:
        print(f"❌ Chyba AI: {e}")
        return "Omlouvám se, nastala chyba."


def generate_tts(text):
    """TTS s caching pro opakované fráze"""
    try:
        from elevenlabs.client import ElevenLabs
        from elevenlabs import VoiceSettings
        
        # ⚡ Cache pro časté fráze
        cache_filename = f"static/cache_{abs(hash(text))}.mp3"
        if os.path.exists(cache_filename):
            print("🔄 Použit cache")
            return f"/static/{os.path.basename(cache_filename)}"
        
        client = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)
        
        audio_generator = client.text_to_speech.convert(
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
        
        audio_bytes = b"".join(audio_generator)
        os.makedirs('static', exist_ok=True)
        
        with open(cache_filename, 'wb') as f:
            f.write(audio_bytes)
        
        return f"/static/{os.path.basename(cache_filename)}"
        
    except Exception as e:
        print(f"❌ TTS chyba: {e}")
        return None


@app.route("/make-call", methods=['POST'])
def make_call():
    """Odchozí hovor"""
    to_number = request.json.get('to')
    
    if not to_number:
        return {"error": "Missing 'to' parameter"}, 400
    
    try:
        call = twilio_client.calls.create(
            to=to_number,
            from_=Config.TWILIO_PHONE_NUMBER,
            url=request.url_root + 'voice'
        )
        
        return {"success": True, "call_sid": call.sid}
        
    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    print("=" * 50)
    print("📞 TWILIO SERVER - ULTRA OPTIMALIZACE")
    print("=" * 50)
    print(f"🔊 Server: http://localhost:5000")
    print(f"📱 Číslo: {Config.TWILIO_PHONE_NUMBER}")
    print("⚡ Vylepšení:")
    print("  - Auto speech detection")
    print("  - TTS caching")
    print("  - Oříznutí dlouhých odpovědí")
    print("=" * 50)
    
    app.run(debug=True, port=5000)