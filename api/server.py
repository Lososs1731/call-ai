"""
Flask server pro Twilio webhooky
PRODUCTION READY - timeout, odmítnutí, zesílení, auto-learning
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
    """Prichozi hovory"""
    call_sid = request.values.get('CallSid')
    caller = request.values.get('From')
    
    print(f"\n{'='*50}")
    print(f"📞 PRICHOZI HOVOR")
    print(f"Od: {caller}")
    print(f"CallSid: {call_sid}")
    print(f"{'='*50}")
    
    greeting = receptionist.handle_call(call_sid, caller)
    
    response = VoiceResponse()
    
    try:
        audio_url = tts.generate(greeting, use_cache=True)
        if audio_url:
            print(f"  ✅ TTS: {audio_url}")
            response.play(audio_url)
        else:
            print(f"  ⚠️  TTS selhalo - pauza")
            response.pause(length=1)
    except Exception as e:
        print(f"  ❌ TTS chyba: {e}")
        response.pause(length=1)
    
    # GATHER
    gather = Gather(
        input='speech',
        action='/process?call_time=0',  # ⭐ Přidán timeout tracking
        language='cs-CZ',
        speech_timeout='1',
        timeout=20,
        speech_model='experimental_conversations',
        barge_in=True,
        hints='recepce, objednávka, dotaz, informace, ano, ne, moment, ale, počkej, prosím, děkuji, dobrý den, ahoj, web, telefon, email',
        profanity_filter=False,
        enhanced=True,
    )
    
    response.append(gather)
    response.redirect('/voice')
    
    return Response(str(response), mimetype='text/xml')


@app.route("/outbound", methods=['POST'])
def outbound_call():
    """Odchozi hovory - ULTRA CITLIVÝ STT"""
    call_sid = request.values.get('CallSid')
    name = request.values.get('name', 'pane')
    company = request.values.get('company', '')
    product_id = request.values.get('product_id', 1)
    campaign = request.values.get('campaign', 'default')  # ⭐ NOVÉ
    
    print(f"\n{'='*50}")
    print(f"📞 ODCHOZI HOVOR")
    print(f"Kontakt: {name}")
    print(f"Firma: {company}")
    print(f"Kampaň: {campaign}")  # ⭐ NOVÉ
    print(f"CallSid: {call_sid}")
    print(f"{'='*50}")
    
    from database import CallDB
    db = CallDB()
    product = db.get_product_by_name("Tvorba webů na míru")
    
    greeting = "Halo?"
    
    print(f"  📝 Greeting: '{greeting}'")
    
    # ⭐ NOVÉ: AUTO-LEARNING PROMPT
    try:
        from services.learning_system import LearningSystem
        learner = LearningSystem()
        sales_prompt = learner.get_optimized_prompt(product, name)
        print(f"  🧠 Použit LEARNED prompt!")
    except Exception as e:
        print(f"  ⚠️  Learning nedostupný, použit default: {e}")
        sales_prompt = Prompts.get_sales_prompt(product, name)
    
    # Zahaj AI konverzaci
    receptionist.ai.start_conversation(call_sid, sales_prompt)
    
    receptionist.ai.conversations[call_sid].append({
        'role': 'assistant',
        'content': greeting
    })
    
    response = VoiceResponse()
    
    # Generuj TTS
    print(f"  🎤 Generuji ElevenLabs TTS...")
    
    try:
        audio_url = tts.generate(greeting, use_cache=True)
        
        if audio_url:
            import os
            audio_path = audio_url.replace('/static/', 'static/').replace('/', os.sep)
            
            if os.path.exists(audio_path):
                file_size = os.path.getsize(audio_path)
                print(f"  ✅ Audio: {audio_url} ({file_size} bytes)")
                response.play(audio_url)
            else:
                print(f"  ❌ Soubor neexistuje, generuji znovu...")
                audio_url_new = tts.generate(greeting, use_cache=False)
                if audio_url_new:
                    response.play(audio_url_new)
                else:
                    response.pause(length=2)
        else:
            print(f"  ❌ TTS vrátilo None")
            audio_url_new = tts.generate(greeting, use_cache=False)
            if audio_url_new:
                response.play(audio_url_new)
            else:
                response.pause(length=2)
            
    except Exception as e:
        print(f"  ❌ TTS chyba: {e}")
        import traceback
        traceback.print_exc()
        response.pause(length=2)
    
    # GATHER
    gather = Gather(
        input='speech',
        action='/process?call_time=0',  # ⭐ Timeout tracking
        language='cs-CZ',
        speech_timeout='1',
        timeout=20,
        speech_model='experimental_conversations',
        barge_in=True,
        hints='web, webové stránky, website, ano, ne, děkuji, zajem, zájem, cena, kolik, email, telefon, moment, ale, však, počkej, stop, prosím, dobrý den, ahoj, nashledanou',
        profanity_filter=False,
        enhanced=True
    )
    
    response.append(gather)
    response.redirect('/voice')
    
    return Response(str(response), mimetype='text/xml')


@app.route("/process", methods=['POST'])
def process_speech():
    """Zpracovani reci - s detekcí odmítnutí, retry, timeout, zesílením"""
    call_sid = request.values.get('CallSid')
    user_input = request.values.get('SpeechResult', '')
    confidence = request.values.get('Confidence', 0)
    retry_count = request.values.get('retry', '0')
    call_time = request.values.get('call_time', '0')  # ⭐ NOVÉ
    
    try:
        retry_count = int(retry_count)
        call_time = int(call_time)
    except:
        retry_count = 0
        call_time = 0
    
    print(f"\n{'='*50}")
    print(f"🎤 ZÁKAZNÍK MLUVÍ")
    print(f"{'='*50}")
    print(f"Text: '{user_input}'")
    print(f"Confidence: {confidence}")
    print(f"Délka: {len(user_input)} znaků")
    print(f"Retry: {retry_count}")
    print(f"Call time: {call_time}s")  # ⭐ NOVÉ
    
    response = VoiceResponse()
    
    # ⏰ TIMEOUT CHECK (5 MINUT = 300s)
    if call_time >= 270:  # 4:30 - varování před ukončením
        print(f"  ⏰ TIMEOUT - ukončuji hovor (5 minut)")
        
        timeout_msg = "Musím bohužel ukončit hovor. Ozveme se vám brzy s dalšími informacemi. Děkuji za váš čas, hezký den!"
        
        try:
            audio_url = tts.generate(timeout_msg, use_cache=True)
            if audio_url:
                response.play(audio_url)
        except:
            pass
        
        response.pause(length=5)
        response.hangup()
        return Response(str(response), mimetype='text/xml')
    
    # ⭐ 1. DETEKCE ODMÍTNUTÍ
    rejection_keywords = [
        'nemám zájem', 'nezajímá', 'nechci', 'ne děkuji', 'neděkuji',
        'nemám čas', 'nezavolávejte', 'smazat', 'odhlásit', 'nepotřebuji',
        'nevolat', 'neotravuj', 'nezajímá mě', 'nemá smysl', 'nedělám',
        'nemám peníze', 'příliš drahé', 'už mám', 'mám jiného'
    ]
    
    is_rejection = any(keyword in user_input.lower() for keyword in rejection_keywords)
    
    if is_rejection:
        print(f"  ⚠️  DETEKOVÁNO ODMÍTNUTÍ - ukončuji OKAMŽITĚ")
        
        goodbye = "Rozumím, děkuji za váš čas. Hezký den."
        
        try:
            audio_url = tts.generate(goodbye, use_cache=True)
            if audio_url:
                response.play(audio_url)
            else:
                response.pause(length=1)
        except:
            response.pause(length=1)
        
        # Ulož do DB
        try:
            receptionist.end_call(call_sid, call_time)
            
            from database import CallDB
            db = CallDB()
            db.cursor.execute("""
                UPDATE calls 
                SET classification = 'no_interest', 
                    summary = 'Zákazník odmítl nabídku - auto-ukončeno',
                    ai_score = 0
                WHERE sid = ?
            """, (call_sid,))
            db.conn.commit()
        except Exception as e:
            print(f"  ⚠️  DB error: {e}")
        
        response.hangup()
        return Response(str(response), mimetype='text/xml')
    
    # ⭐ 2. PRÁZDNÝ VSTUP - RETRY + ZESÍLENÍ
    if not user_input or len(user_input.strip()) == 0:
        print(f"  ⚠️  PRÁZDNÝ vstup")
        
        if retry_count >= 2:
            print(f"  ❌ 2 pokusy selhaly - ukončuji po 15s")
            
            sorry_msg = "Omlouvám se, bohužel vám nerozumím. Zavoláme jindy. Hezký den."
            
            try:
                audio_url = tts.generate(sorry_msg, use_cache=True)
                if audio_url:
                    response.play(audio_url)
            except:
                pass
            
            response.pause(length=15)
            response.hangup()
            return Response(str(response), mimetype='text/xml')
        
        else:
            print(f"  🔄 Retry #{retry_count + 1} + ZESÍLENÍ")
            
            # ⭐ ZESÍLENÍ - žádá HLASITĚJŠÍ řeč
            if retry_count == 0:
                sorry_msg = "Nerozuměl jsem, můžete to prosím zopakovat HLASITĚJI?"
            else:
                sorry_msg = "Stále vám špatně rozumím. Prosím mluvte HLASNĚ a POMALU."
            
            try:
                audio_url = tts.generate(sorry_msg, use_cache=True)
                if audio_url:
                    response.play(audio_url)
                else:
                    response.pause(length=1)
            except:
                response.pause(length=1)
            
            gather = Gather(
                input='speech',
                action=f'/process?retry={retry_count + 1}&call_time={call_time + 15}',
                language='cs-CZ',
                speech_timeout='1',
                timeout=15,
                speech_model='experimental_conversations',
                barge_in=True,
                profanity_filter=False,
                enhanced=True
            )
            response.append(gather)
            response.redirect('/voice')
            return Response(str(response), mimetype='text/xml')
    
    # ⭐ 3. PŘÍLIŠ KRÁTKÝ (< 3 znaky)
    if len(user_input.strip()) < 3:
        print(f"  ⚠️  PŘÍLIŠ KRÁTKÝ ({len(user_input)} znaků)")
        
        if retry_count >= 2:
            print(f"  ❌ 2 pokusy - ukončuji")
            
            sorry_msg = "Omlouvám se, nerozumím vám. Hezký den."
            
            try:
                audio_url = tts.generate(sorry_msg, use_cache=True)
                if audio_url:
                    response.play(audio_url)
            except:
                pass
            
            response.pause(length=15)
            response.hangup()
            return Response(str(response), mimetype='text/xml')
        
        else:
            # ⭐ ZESÍLENÍ
            if retry_count == 0:
                sorry_msg = "Nerozuměl jsem, prosím mluvte JASNĚJI a HLASITĚJI."
            else:
                sorry_msg = "Stále nerozumím. Mluvte prosím POMALU a HLASNĚ."
            
            try:
                audio_url = tts.generate(sorry_msg, use_cache=True)
                if audio_url:
                    response.play(audio_url)
                else:
                    response.pause(length=1)
            except:
                response.pause(length=1)
            
            gather = Gather(
                input='speech',
                action=f'/process?retry={retry_count + 1}&call_time={call_time + 15}',
                language='cs-CZ',
                speech_timeout='1',
                timeout=15,
                speech_model='experimental_conversations',
                barge_in=True,
                profanity_filter=False,
                enhanced=True
            )
            response.append(gather)
            response.redirect('/voice')
            return Response(str(response), mimetype='text/xml')
    
    # ⭐ 4. VELMI NÍZKÁ CONFIDENCE (< 0.3)
    if float(confidence) < 0.3:
        print(f"  ⚠️  VELMI NÍZKÁ confidence ({confidence})")
        
        if retry_count >= 2:
            print(f"  ❌ 2 pokusy - ukončuji")
            
            sorry_msg = "Omlouvám se, špatné spojení. Zavoláme jindy. Nashledanou."
            
            try:
                audio_url = tts.generate(sorry_msg, use_cache=True)
                if audio_url:
                    response.play(audio_url)
            except:
                pass
            
            response.pause(length=15)
            response.hangup()
            return Response(str(response), mimetype='text/xml')
        
        else:
            sorry_msg = "Špatně vám rozumím. Prosím zopakujte HLASNĚJI."
            
            try:
                audio_url = tts.generate(sorry_msg, use_cache=True)
                if audio_url:
                    response.play(audio_url)
                else:
                    response.pause(length=1)
            except:
                response.pause(length=1)
            
            gather = Gather(
                input='speech',
                action=f'/process?retry={retry_count + 1}&call_time={call_time + 15}',
                language='cs-CZ',
                speech_timeout='1',
                timeout=15,
                speech_model='experimental_conversations',
                barge_in=True,
                profanity_filter=False,
                enhanced=True
            )
            response.append(gather)
            response.redirect('/voice')
            return Response(str(response), mimetype='text/xml')
    
    # ⚠️ NÍZKÁ CONFIDENCE (0.3-0.5)
    if float(confidence) < 0.5:
        print(f"  ⚠️  Nízká confidence ({confidence}) - ale zpracuji")
    
    # ⭐ 5. ZPRACOVÁNÍ AI ODPOVĚDI
    try:
        print(f"  🤖 Zpracovávám AI odpověď...")
        ai_reply = receptionist.process_message(call_sid, user_input)
        
        print(f"  AI: {ai_reply[:100]}...")
        
        # ⭐ ZKRAŤ ZDLOUHAVÉ ODPOVĚDI
        if len(ai_reply) > 300 or ai_reply.count('.') > 3:
            sentences = ai_reply.split('.')
            ai_reply = '. '.join(sentences[:2]) + '.'
            print(f"  ✂️  Zkráceno (bylo příliš dlouhé)")
        
        # Generuj TTS
        print(f"  🎤 Generuji TTS...")
        audio_url = tts.generate(ai_reply, use_cache=True)
        
        if audio_url:
            print(f"  ✅ Přehrávám: {audio_url}")
            response.play(audio_url)
        else:
            print(f"  ⚠️  TTS selhalo - pauza")
            response.pause(length=1)
            
    except Exception as e:
        print(f"  ❌ AI chyba: {e}")
        import traceback
        traceback.print_exc()
        
        sorry_msg = "Omlouvám se, nastala chyba. Zkuste prosím znovu."
        try:
            audio_url = tts.generate(sorry_msg, use_cache=True)
            if audio_url:
                response.play(audio_url)
            else:
                response.pause(length=1)
        except:
            response.pause(length=1)
    
    # ⭐ 6. DALŠÍ GATHER (increment call_time, reset retry)
    new_call_time = call_time + 30  # Přidej ~30s
    
    gather = Gather(
        input='speech',
        action=f'/process?retry=0&call_time={new_call_time}',  # ⭐ NOVÉ
        language='cs-CZ',
        speech_timeout='1',
        timeout=20,
        speech_model='experimental_conversations',
        barge_in=True,
        hints='web, ano, ne, děkuji, zajem, email, telefon, kolik, cena, moment, ale, však, počkej, stop, prosím, nerozumím',
        profanity_filter=False,
        enhanced=True
    )
    
    response.append(gather)
    response.redirect('/voice')
    
    return Response(str(response), mimetype='text/xml')


@app.route("/call-status", methods=['POST'])
def call_status():
    """Status callback - AI REPORT + AUTO-LEARNING"""
    call_sid = request.values.get('CallSid')
    status = request.values.get('CallStatus')
    duration = request.values.get('CallDuration', 0)
    
    print(f"\n{'='*50}")
    print(f"📊 STATUS UPDATE")
    print(f"CallSid: {call_sid}")
    print(f"Status: {status}")
    print(f"Duration: {duration}s")
    
    # ⏰ Timeout check
    if int(duration) >= 290:
        print(f"  ⏰ TIMEOUT hovor (5 minut)!")
    
    print(f"{'='*50}")
    
    try:
        receptionist.end_call(call_sid, int(duration))
        
        # ⭐ AI REPORT
        if status == 'completed' and int(duration) >= 10:
            print(f"\n{'='*60}")
            print(f"🤖 SPOUŠTÍM AI VYHODNOCENÍ HOVORU")
            print(f"{'='*60}")
            
            try:
                from services.call_reporter import CallReporter
                reporter = CallReporter()
                
                report = reporter.analyze_call(call_sid)
                
                if 'error' not in report:
                    success_rate = report.get('success_rate', 0)
                    classification = report.get('classification', 'N/A')
                    
                    print(f"\n{'='*60}")
                    print(f"✅ AI REPORT VYGENEROVÁN!")
                    print(f"{'='*60}")
                    print(f"🎯 Úspěšnost: {success_rate}%")
                    print(f"📌 Klasifikace: {classification.upper()}")
                    print(f"💬 Feedback: {report.get('feedback', 'N/A')[:100]}...")
                    print(f"{'='*60}\n")
                    
                    # ⭐ AUTO-LEARNING (pokud úspěšný!)
                    if success_rate >= 70:
                        print(f"🧠 Spouštím AUTO-LEARNING (úspěšný hovor)...")
                        
                        try:
                            from services.learning_system import LearningSystem
                            learner = LearningSystem()
                            learner.learn_from_call(call_sid, report)
                            print(f"✅ Learning dokončen - prompt vylepšen!")
                        except Exception as e:
                            print(f"⚠️  Learning error: {e}")
                else:
                    print(f"\n❌ Chyba při generování reportu: {report['error']}")
                    
            except Exception as e:
                print(f"\n❌ Nepodařilo se vygenerovat AI report: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"  ⚠️  Hovor příliš krátký ({duration}s) - přeskakuji AI report")
        
    except Exception as e:
        print(f"  ❌ Chyba: {e}")
    
    return Response('OK', mimetype='text/plain')


@app.route("/health", methods=['GET'])
def health():
    """Health check"""
    return {'status': 'ok', 'service': 'AI Phone Assistant PRODUCTION'}


if __name__ == "__main__":
    print("=" * 60)
    print("   AI TELEFONNI ASISTENT - PRODUCTION SERVER")
    print("=" * 60)
    print(f"Server: http://localhost:{Config.SERVER_PORT}")
    print(f"Cislo: {Config.TWILIO_PHONE_NUMBER}")
    print(f"Static: {app.static_folder}")
    print("\nEndpointy:")
    print("  /voice       - Prichozi hovory")
    print("  /inbound     - Prichozi hovory")
    print("  /outbound    - Odchozi hovory")
    print("  /process     - Zpracovani reci")
    print("  /call-status - Status callback + AI Report + Learning")
    print("  /health      - Health check")
    print("  /static/*    - Audio soubory")
    print("\nFunkce:")
    print("  ⏰ Timeout: 5 minut (auto-ukončení)")
    print("  ❌ Odmítnutí: Auto-detekce → zavěsí")
    print("  🔊 Zesílení: Žádá HLASITĚJI při problémech")
    print("  🔄 Retry: 2x pokus, pak zavěsí po 15s")
    print("  🤖 AI Report: Automaticky po hovoru")
    print("  🧠 Auto-Learning: Z úspěšných hovorů (≥70%)")
    print("  ⚡ Barge-in: ZAPNUTO")
    print("  🔊 STT: MAXIMÁLNÍ citlivost (1s)")
    print("  🎤 TTS: ElevenLabs")
    print("=" * 60)
    
    app.run(
        host=Config.SERVER_HOST,
        port=Config.SERVER_PORT,
        debug=Config.DEBUG
    )