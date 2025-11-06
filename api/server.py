"""
Flask server pro Twilio webhooky
OPRAVENO: Auto-zavěšení, rychlejší reakce, české skloňování
"""

from flask import Flask, request, Response, send_from_directory
from twilio.twiml.voice_response import VoiceResponse, Gather
import os

from core import TTSEngine
from services import ReceptionistService
from config import Prompts, Config

app = Flask(__name__, static_folder='../static', static_url_path='/static')

receptionist = ReceptionistService()
tts = TTSEngine()


@app.route('/static/<path:filename>')
def serve_static(filename):
    """Servuje staticke soubory"""
    static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
    return send_from_directory(static_dir, filename)


@app.route("/voice", methods=['POST'])
@app.route("/inbound", methods=['POST'])
def inbound_call():
    """Příchozí hovory - OPRAVENO: reset konverzace"""
    call_sid = request.values.get('CallSid')
    caller = request.values.get('From')
    
    print(f"\n{'='*50}")
    print(f"📞 PŘÍCHOZÍ HOVOR")
    print(f"Od: {caller}")
    print(f"CallSid: {call_sid}")
    print(f"{'='*50}")
    
    # ✅ SMAŽ STAROU KONVERZACI (pokud existuje)
    if call_sid in receptionist.ai.conversations:
        print(f"  ⚠️  Mažu starou konverzaci pro {call_sid}")
        del receptionist.ai.conversations[call_sid]
    
    # Získej TEXT pozdravu
    greeting_text = receptionist.handle_call(call_sid, caller)
    
    # Vytvoř TwiML
    response = VoiceResponse()
    
    # Generuj TTS
    try:
        audio_url = tts.generate(greeting_text, use_cache=True)
    except:
        audio_url = None
    
    # ✅ GATHER BĚHEM PLAY (barge-in)
    gather = Gather(
        input='speech',
        action='/process?call_time=0',
        language='cs-CZ',
        speech_timeout='1',  # ✅ ZMĚNĚNO z 'auto' na '1'
        timeout=8,  # ✅ ZKRÁCENO z 10
        speech_model='phone_call',
        barge_in=True,
        actionOnEmptyResult=True,
        profanity_filter=False,
        enhanced=True,
        hints='dobrý den, ahoj, recepce, objednávka, dotaz, ano, ne, moment, prosím, děkuji, halo, slyšíme se'
    )
    
    if audio_url:
        print(f"  ✅ TTS: {audio_url}")
        gather.play(audio_url)  # ✅ PLAY UVNITŘ GATHER
    else:
        print(f"  ⚠️  TTS selhalo")
        gather.say(greeting_text, language='cs-CZ')
    
    response.append(gather)
    response.redirect('/process?call_time=0')
    
    return Response(str(response), mimetype='text/xml')


@app.route("/outbound", methods=['POST'])
def outbound_call():
    """Odchozi hovory - OPRAVENO: český greeting, barge-in"""
    call_sid = request.values.get('CallSid')
    name = request.values.get('name', 'pane')
    company = request.values.get('company', '')
    product_id = request.values.get('product_id', 1)
    campaign = request.values.get('campaign', 'default')
    
    print(f"\n{'='*50}")
    print(f"📞 ODCHOZI HOVOR")
    print(f"Kontakt: {name}")
    print(f"Firma: {company}")
    print(f"Kampaň: {campaign}")
    print(f"CallSid: {call_sid}")
    print(f"{'='*50}")
    
    from database import CallDB
    db = CallDB()
    product = db.get_product_by_name("Tvorba webů na míru")
    
    # ✅ ČESKÝ POZDRAV (ne "Halo?")
    greeting = f"Dobrý den, {name}. Tady Pavel z Lososs."
    
    print(f"  📝 Greeting: '{greeting}'")
    
    # AUTO-LEARNING PROMPT
    try:
        from services.learning_system import LearningSystem
        learner = LearningSystem()
        sales_prompt = learner.get_optimized_prompt(product, name)
        print(f"  🧠 Použit LEARNED prompt!")
    except Exception as e:
        print(f"  ⚠️  Learning nedostupný: {e}")
        sales_prompt = Prompts.get_sales_prompt(product, name)
    
    # Zahaj AI konverzaci
    receptionist.ai.start_conversation(call_sid, sales_prompt)
    
    # Přidej greeting do konverzace
    receptionist.ai.conversations[call_sid].append({
        'role': 'assistant',
        'content': greeting
    })
    
    response = VoiceResponse()
    
    # Generuj TTS
    print(f"  🎤 Generuji ElevenLabs TTS...")
    
    try:
        audio_url = tts.generate(greeting, use_cache=True)
    except Exception as e:
        print(f"  ❌ TTS chyba: {e}")
        audio_url = None
    
    if audio_url:
        print(f"  ✅ Audio: {audio_url}")
        
        # ✅ GATHER BĚHEM PLAY (barge-in)
        gather = Gather(
            input='speech',
            action='/process?call_time=0',
            language='cs-CZ',
            speech_timeout='1',  # ✅ ZMĚNĚNO z 'auto'
            timeout=10,  # ✅ ZKRÁCENO z 15
            speech_model='phone_call',
            barge_in=True,
            actionOnEmptyResult=True,
            profanity_filter=False,
            enhanced=True,
            hints='dobrý den, ahoj, ano, ne, web, děkuji, moment, stop, zájem, email, halo, slyšíme se'
        )
        
        gather.play(audio_url)  # ✅ PLAY UVNITŘ GATHER
        response.append(gather)
        response.redirect('/process?call_time=0')
        
    else:
        print(f"  ❌ TTS selhalo - ukončuji")
        response.say(greeting, language='cs-CZ')
        response.hangup()
    
    return Response(str(response), mimetype='text/xml')


@app.route("/process", methods=['POST'])
def process_speech():
    """Zpracování řeči - OPRAVENO: auto-zavěšení, rychlejší reakce"""
    call_sid = request.values.get('CallSid')
    user_input = request.values.get('SpeechResult', '')
    confidence = request.values.get('Confidence', 0)
    retry_count = request.values.get('retry', '0')
    call_time = request.values.get('call_time', '0')
    
    try:
        retry_count = int(retry_count)
        call_time = int(call_time)
        confidence = float(confidence) if confidence else 0.0
    except:
        retry_count = 0
        call_time = 0
        confidence = 0.0
    
    print(f"\n{'='*50}")
    print(f"🎤 ZÁKAZNÍK MLUVÍ")
    print(f"{'='*50}")
    print(f"Text: '{user_input}'")
    print(f"Confidence: {confidence}")
    print(f"Délka: {len(user_input)} znaků")
    print(f"Retry: {retry_count}")
    print(f"Call time: {call_time}s")
    
    response = VoiceResponse()
    
    # ⏰ TIMEOUT CHECK (5 MINUT)
    if call_time >= 270:
        print(f"  ⏰ TIMEOUT - ukončuji")
        
        timeout_msg = "Musím ukončit hovor. Hezký den!"
        
        try:
            audio_url = tts.generate(timeout_msg, use_cache=True)
            if audio_url:
                response.play(audio_url)
        except:
            pass
        
        response.hangup()
        return Response(str(response), mimetype='text/xml')
    
    # ⭐ DETEKCE ODMÍTNUTÍ - ROZŠÍŘENO
    # ⭐ DETEKCE ODMÍTNUTÍ - POUZE TVRDÁ ODMÍTNUTÍ!
    hard_rejection_keywords = [
        'nemám zájem a nebudu', 'nevolejte', 'smažte', 'přestaňte',
        'neotravujte', 'odhlásit', 'nechci', 'už podruhé ne',
        'říkám ne', 'konec', 'stop'
    ]

    # ✅ SOFT ODMÍTNUTÍ = NÁMITKA (pokračuj!)
    soft_rejection = [
        'nemám čas', 'nemám minutku', 'teď ne', 'později',
        'musím jít', 'spěchám'
    ]

    # ✅ PŘÍLEŽITOST (rozhodně ne odmítnutí!)
    opportunities = [
        'nemáme web', 'nemáme stránky', 'nemáme', 'nemám web',
        'starý web', 'nefunguje', 'špatný', 'zastaralý'
    ]

    user_input_lower = user_input.lower()

    # 1. Zkontroluj příležitosti PRVNÍ
    is_opportunity = any(phrase in user_input_lower for phrase in opportunities)
    if is_opportunity:
        print(f"  🎯 PŘÍLEŽITOST detekována - pokračuji agresivně!")
        # Pokračuj normálně s AI - není to odmítnutí!
        is_rejection = False

    # 2. Soft rejection = jen poznámka, ale pokračuj
    elif any(phrase in user_input_lower for phrase in soft_rejection):
        print(f"  ⚠️  SOFT odmítnutí - zkusím obejít!")
        is_rejection = False  # Nech AI to vyřešit!

    # 3. Jen HARD rejection = skutečně zavěs
    else:
        is_rejection = any(keyword in user_input_lower for keyword in hard_rejection_keywords)

    if is_rejection:
        print(f"  ❌ HARD ODMÍTNUTÍ - ukončuji")
        
        goodbye = "Rozumím, díky za čas. Hezký den."
        
        try:
            audio_url = tts.generate(goodbye, use_cache=True)
            if audio_url:
                response.play(audio_url)
        except:
            pass
        
        try:
            receptionist.end_call(call_sid, call_time)
        except:
            pass
        
        response.pause(length=1)
        response.hangup()
        return Response(str(response), mimetype='text/xml')
    
    # ⭐ PRÁZDNÝ VSTUP
    if not user_input or len(user_input.strip()) == 0:
        print(f"  ⚠️  PRÁZDNÝ vstup")
        
        if retry_count >= 2:
            print(f"  ❌ 2 pokusy - ukončuji")
            
            sorry_msg = "Omlouvám se, nerozumím. Hezký den."
            
            try:
                audio_url = tts.generate(sorry_msg, use_cache=True)
                if audio_url:
                    response.play(audio_url)
            except:
                pass
            
            response.pause(length=1)
            response.hangup()
            return Response(str(response), mimetype='text/xml')
        
        sorry_msg = "Neslyším vás. Mluvte prosím hlasitěji."
        
        try:
            audio_url = tts.generate(sorry_msg, use_cache=True)
        except:
            audio_url = None
        
        gather = Gather(
            input='speech',
            action=f'/process?retry={retry_count + 1}&call_time={call_time + 8}',
            language='cs-CZ',
            speech_timeout='1',  # ✅ ZMĚNĚNO z 'auto'
            timeout=8,
            speech_model='phone_call',
            barge_in=True,
            actionOnEmptyResult=True,
            profanity_filter=False,
            enhanced=True
        )
        
        if audio_url:
            gather.play(audio_url)
        else:
            gather.say(sorry_msg, language='cs-CZ')
        
        response.append(gather)
        response.redirect(f'/process?retry={retry_count + 1}&call_time={call_time + 8}')
        return Response(str(response), mimetype='text/xml')
    
    # ⭐ PŘÍLIŠ KRÁTKÝ (< 2 znaky)
    if len(user_input.strip()) < 2:
        print(f"  ⚠️  PŘÍLIŠ KRÁTKÝ")
        
        if retry_count >= 2:
            response.say("Omlouvám se, nerozumím. Hezký den.", language='cs-CZ')
            response.pause(length=1)
            response.hangup()
            return Response(str(response), mimetype='text/xml')
        
        sorry_msg = "Nerozuměl jsem. Zopakujte prosím."
        
        try:
            audio_url = tts.generate(sorry_msg, use_cache=True)
        except:
            audio_url = None
        
        gather = Gather(
            input='speech',
            action=f'/process?retry={retry_count + 1}&call_time={call_time + 8}',
            language='cs-CZ',
            speech_timeout='1',  # ✅ ZMĚNĚNO
            timeout=8,
            speech_model='phone_call',
            barge_in=True,
            actionOnEmptyResult=True,
            profanity_filter=False,
            enhanced=True
        )
        
        if audio_url:
            gather.play(audio_url)
        else:
            gather.say(sorry_msg, language='cs-CZ')
        
        response.append(gather)
        response.redirect(f'/process?retry={retry_count + 1}&call_time={call_time + 8}')
        return Response(str(response), mimetype='text/xml')
    
    # ✅ ZPRACOVÁNÍ AI
    print(f"  🤖 Zpracovávám AI odpověď...")
    
    try:
        ai_reply = receptionist.process_message(call_sid, user_input)
        
        print(f"  AI: {ai_reply[:100]}...")
        
        # ✅ DETEKUJ ROZLOUČENÍ V AI ODPOVĚDI
        goodbye_phrases = [
            'hezký den', 'nashledanou', 'na shledanou',
            'měj se', 'zatím ahoj', 'díky za čas',
            'už musím', 'musím jít', 'rozumím, díky'
        ]
        
        ai_reply_lower = ai_reply.lower()
        is_goodbye = any(phrase in ai_reply_lower for phrase in goodbye_phrases)
        
        # Zkrať dlouhé odpovědi
        if len(ai_reply) > 250 or ai_reply.count('.') > 2:
            sentences = ai_reply.split('.')
            ai_reply = '. '.join(sentences[:2]) + '.'
            print(f"  ✂️  Zkráceno")
        
        # Generuj TTS
        print(f"  🎤 Generuji TTS...")
        try:
            audio_url = tts.generate(ai_reply, use_cache=True)
        except:
            audio_url = None
        
        # ✅ POKUD ROZLOUČENÍ → PŘEHRAJ A ZAVĚS!
        if is_goodbye:
            print(f"  👋 DETEKOVÁNO ROZLOUČENÍ - zavěšuji po přehrání")
            
            if audio_url:
                response.play(audio_url)
            else:
                response.say(ai_reply, language='cs-CZ')
            
            response.pause(length=1)
            response.hangup()
            
            # Ulož do DB
            try:
                receptionist.end_call(call_sid, call_time + 10)
            except:
                pass
            
            return Response(str(response), mimetype='text/xml')
        
        # ✅ NORMÁLNÍ ODPOVĚĎ S GATHER
        new_call_time = call_time + 15
        
        gather = Gather(
            input='speech',
            action=f'/process?retry=0&call_time={new_call_time}',
            language='cs-CZ',
            speech_timeout='1',  # ✅ ZMĚNĚNO z 'auto'
            timeout=8,  # ✅ ZKRÁCENO z 15
            speech_model='phone_call',
            barge_in=True,
            actionOnEmptyResult=True,
            profanity_filter=False,
            enhanced=True,
            hints='ano, ne, dobrý den, ahoj, děkuji, web, email, telefon, moment, stop, prosím, halo, slyšíme se'
        )
        
        if audio_url:
            print(f"  ✅ Přehrávám s barge-in: {audio_url}")
            gather.play(audio_url)
        else:
            print(f"  ⚠️  TTS selhalo, použiji say")
            gather.say(ai_reply, language='cs-CZ')
        
        response.append(gather)
        response.redirect(f'/process?retry=0&call_time={new_call_time}')
        
        return Response(str(response), mimetype='text/xml')
            
    except Exception as e:
        print(f"  ❌ AI chyba: {e}")
        import traceback
        traceback.print_exc()
        
        sorry_msg = "Omlouvám se, nastala chyba. Zkuste znovu."
        
        try:
            audio_url = tts.generate(sorry_msg, use_cache=True)
        except:
            audio_url = None
        
        gather = Gather(
            input='speech',
            action=f'/process?retry=0&call_time={call_time + 8}',
            language='cs-CZ',
            speech_timeout='1',
            timeout=8,
            speech_model='phone_call',
            barge_in=True,
            actionOnEmptyResult=True,
            profanity_filter=False,
            enhanced=True
        )
        
        if audio_url:
            gather.play(audio_url)
        else:
            gather.say(sorry_msg, language='cs-CZ')
        
        response.append(gather)
        response.redirect(f'/process?retry=0&call_time={call_time + 8}')
        
        return Response(str(response), mimetype='text/xml')


@app.route("/call-status", methods=['POST'])
def call_status():
    """Status callback - AI REPORT + AUTO-LEARNING + DATABÁZE"""
    call_sid = request.values.get('CallSid')
    status = request.values.get('CallStatus')
    duration = request.values.get('CallDuration', 0)
    caller = request.values.get('From', '')
    
    print(f"\n{'='*50}")
    print(f"📊 STATUS UPDATE")
    print(f"CallSid: {call_sid}")
    print(f"Status: {status}")
    print(f"Duration: {duration}s")
    print(f"{'='*50}")
    
    try:
        # ✅ ZÍSKEJ KONVERZACI PŘED end_call!
        conversation = []
        if call_sid in receptionist.ai.conversations:
            conversation = receptionist.ai.conversations[call_sid].copy()
            print(f"  ✅ Konverzace nalezena ({len(conversation)} zpráv)")
        else:
            print(f"  ⚠️  Konverzace už byla smazána!")
        
        # Teprve TEĎ zavolej end_call (nesmaže konverzaci)
        # receptionist.end_call(call_sid, int(duration))
        
        # AI REPORT - POUZE pokud máme konverzaci!
        if status == 'completed' and int(duration) >= 10 and len(conversation) > 2:
            print(f"\n{'='*60}")
            print(f"🤖 SPOUŠTÍM AI VYHODNOCENÍ")
            print(f"{'='*60}")
            
            try:
                from services.call_reporter import CallReporter
                from database.call_analytics import CallAnalytics
                
                reporter = CallReporter()
                analytics = CallAnalytics()
                
                # ✅ POŠLI KONVERZACI DO REPORTERU!
                result = reporter.analyze_call(call_sid, conversation)
                
                if 'error' not in result:
                    print(f"\n✅ AI REPORT VYGENEROVÁN!")
                    print(f"   Výsledek: {result.get('outcome', 'N/A')}")
                    print(f"   Skóre: {result.get('sales_score', 0)}/100")
                    print(f"   Shrnutí: {result.get('ai_summary', 'N/A')[:100]}...")
                    
                    # ✅ ULOŽ DO DATABÁZE
                    call_data = {
                        'call_sid': call_sid,
                        'contact_phone': caller,
                        'duration': int(duration),
                        'conversation': conversation,
                        'started_at': None,  # TODO: track start time
                        'ended_at': None,
                        **result
                    }
                    
                    analytics.save_call(call_data)
                    print(f"   ✅ Uloženo do databáze!")
                    
                    # ✅ AI LEARNING - pokud úspěšný!
                    success_rate = result.get('sales_score', 0)
                    
                    if success_rate >= 70:
                        print(f"\n🧠 SPOUŠTÍM AUTO-LEARNING (úspěšný hovor {success_rate}%)...")
                        
                        try:
                            from services.learning_system import LearningSystem
                            learner = LearningSystem()
                            learner.learn_from_call(call_sid, result)
                            print(f"   ✅ Learning dokončen - prompt vylepšen!")
                        except Exception as e:
                            print(f"   ⚠️  Learning error: {e}")
                    
                    elif success_rate < 40:
                        print(f"\n📚 Ukládám FAILED hovor pro learning ({success_rate}%)...")
                        # TODO: Learn from failures
                    
                else:
                    print(f"\n❌ Report error: {result['error']}")
                    
            except Exception as e:
                print(f"\n❌ Report failed: {e}")
                import traceback
                traceback.print_exc()
        
        elif len(conversation) <= 2:
            print(f"  ⚠️  Hovor příliš krátký ({len(conversation)} zpráv) - přeskakuji AI report")
        
        else:
            print(f"  ⚠️  Status={status}, duration={duration}s - přeskakuji")
        
    except Exception as e:
        print(f"  ❌ Chyba: {e}")
        import traceback
        traceback.print_exc()
    
    return Response('OK', mimetype='text/plain')


@app.route("/health", methods=['GET'])
def health():
    """Health check"""
    return {'status': 'ok', 'service': 'AI Phone Assistant'}


if __name__ == "__main__":
    print("=" * 60)
    print("   AI TELEFONNÍ ASISTENT - PRODUCTION")
    print("=" * 60)
    print(f"Server: http://localhost:{Config.SERVER_PORT}")
    print(f"Číslo: {Config.TWILIO_PHONE_NUMBER}")
    print("\n✅ OPRAVY:")
    print("  🎤 Český greeting (ne 'Halo?')")
    print("  🔊 Barge-in: gather.play() místo response.play()")
    print("  🧠 Reset konverzace při novém hovoru")
    print("  👋 Auto-zavěšení při rozloučení")
    print("  ⚡ Rychlejší reakce: speech_timeout='1'")
    print("  ⏱️  Kratší timeout: 8s místo 15s")
    print("=" * 60)
    
    app.run(
        host=Config.SERVER_HOST,
        port=Config.SERVER_PORT,
        debug=Config.DEBUG
    )