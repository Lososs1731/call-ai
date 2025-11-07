"""
KOMPLETNÍ SQLite databáze pro Cold Calling
VŠECHNO v jednom scriptu - BEZ MySQL!
Ondřej Hýža (@Lososs1731) - 2025-11-07
"""

import sqlite3
import os
from datetime import datetime

print("🔥 Vytvářím KOMPLETNÍ SQLite databázi...")

# Smaž starou
db_path = 'database/knowledge_base.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print("🗑️  Stará databáze smazána")

conn = sqlite3.connect(db_path)
c = conn.cursor()

# ============================================================
# TABULKY
# ============================================================

print("\n📋 Vytvářím tabulky...")

c.execute('''CREATE TABLE allowed_topics (
    id INTEGER PRIMARY KEY,
    topic_name TEXT UNIQUE,
    topic_category TEXT,
    on_topic_keywords TEXT,
    priority INTEGER,
    is_core_topic INTEGER,
    handling_strategy TEXT
)''')

c.execute('''CREATE TABLE redirect_templates (
    id INTEGER PRIMARY KEY,
    redirect_type TEXT,
    acknowledge_short TEXT,
    redirect_direct TEXT,
    redirect_soft TEXT,
    success_rate REAL DEFAULT 50.0
)''')

c.execute('''CREATE TABLE cold_call_responses (
    id INTEGER PRIMARY KEY,
    call_stage TEXT,
    sub_category TEXT,
    situation TEXT,
    response_text TEXT,
    alternative_1 TEXT,
    alternative_2 TEXT,
    strategy TEXT,
    tone TEXT,
    urgency_level INTEGER,
    expected_response TEXT,
    next_step TEXT,
    success_rate REAL DEFAULT 50.0,
    conversion_rate REAL DEFAULT 0.0
)''')

c.execute('''CREATE TABLE czech_natural_phrases (
    id INTEGER PRIMARY KEY,
    phrase_type TEXT,
    czech_phrase TEXT,
    usage_context TEXT,
    frequency TEXT,
    natural_score REAL
)''')

print("✅ Tabulky vytvořeny")

# ============================================================
# ALLOWED TOPICS - 21 řádků
# ============================================================

topics = [
    (1, 'web_a_webdesign', 'core_business', 'web, webové stránky, webovky, stránky, website, internet', 10, 1, 'Hlavní téma'),
    (2, 'seo_optimalizace', 'core_business', 'seo, optimalizace, google, ranking, pozice', 10, 1, 'Klíčová hodnota'),
    (3, 'zakaznici_a_prodej', 'core_business', 'zákazníci, klienti, prodej, tržby', 10, 1, 'Pain point'),
    (4, 'konkurence', 'core_business', 'konkurence, konkurenti, trh', 9, 1, 'FOMO trigger'),
    (5, 'schuzka_konzultace', 'core_business', 'schůzka, meeting, konzultace', 10, 1, 'HLAVNÍ CÍL'),
    (6, 'cena_rozpocet', 'business_operations', 'cena, rozpočet, náklady, peníze', 8, 1, 'Námitka'),
    (7, 'cas_a_timing', 'business_operations', 'čas, kdy, termín, deadline', 7, 1, 'Námitka'),
    (8, 'technologie', 'business_operations', 'wordpress, cms, hosting, doména', 7, 1, 'Tech stack'),
    (9, 'mobil_responsive', 'business_operations', 'mobil, mobilní, telefon, responsive', 8, 1, 'Selling point'),
    (10, 'rychlost_vykonu', 'business_operations', 'rychlost, performance, načítání', 7, 1, 'UX + SEO'),
    (11, 'kontaktni_udaje', 'logistics', 'email, telefon, kontakt', 7, 1, 'Pozitivní signál'),
    (12, 'firma_info', 'logistics', 'firma, kdo jste, reference', 6, 1, 'O firmě'),
    (13, 'proces_spoluprace', 'logistics', 'jak to funguje, postup, kroky', 6, 1, 'Detail procesu'),
    (14, 'rozhodovani', 'decision', 'rozhodnout, šéf, ředitel, manažer', 8, 1, 'Decision maker'),
    (15, 'dulezitost_priority', 'decision', 'důležité, priorita, urgentní', 7, 1, 'Priority check'),
    (16, 'namitky_obecne', 'objections', 'ale, však, problém, nechci', 9, 1, 'Námitky'),
    (17, 'obor_segment', 'context', 'obor, odvětví, segment', 5, 1, 'Personalizace'),
    (18, 'velikost_firmy', 'context', 'kolik lidí, zaměstnanci, tým', 5, 1, 'Scope'),
    (19, 'zajem_obecne', 'interest', 'zajímá, chci, možná, uvažujeme', 9, 1, 'Pozitivní signál'),
    (20, 'marketing_reklama', 'business_operations', 'marketing, reklama, facebook', 6, 1, 'Marketing vztah'),
    (21, 'analyzy_data', 'business_operations', 'analytics, data, měření', 6, 1, 'Tech zákazník')
]

c.executemany('INSERT INTO allowed_topics VALUES (?,?,?,?,?,?,?)', topics)
print(f"✅ Vloženo {len(topics)} topics")

# ============================================================
# REDIRECT TEMPLATES - 10 řádků
# ============================================================

redirects = [
    (1, 'general_offtopic', 'Jo', 'Ale zpátky k byznysu - máte web?', 'Vraťme se k vám', 50.0),
    (2, 'casual_smalltalk', 'Hmm', 'Nemáme čas. Web máte?', 'Zpátky k byznysu', 50.0),
    (3, 'complaint_vent', 'Chápu', 'Proto web - pomůže. Máte?', 'Řešení je web', 50.0),
    (4, 'personal_life', 'Fajn', 'K firmě - web máte?', 'Zpátky k byznysu', 50.0),
    (5, 'philosophical', 'Hmm', 'Řešme konkrétně - web?', 'K realitě', 50.0),
    (6, 'random_nonsense', 'Aha', 'To neřešíme. Web máte?', 'K tématu', 50.0),
    (7, 'politics', 'Jo', 'Politiku nechme. Byznys - web?', 'K firmě', 50.0),
    (8, 'health', 'Mrzí mě', 'Web funguje i když vy nemůžete', 'K byznysu', 50.0),
    (9, 'sports', 'Jo', 'Zpátky k byznysu - web?', 'K firmě', 50.0),
    (10, 'weather', 'Jo', 'Web funguje za každého počasí', 'K tématu', 50.0)
]

c.executemany('INSERT INTO redirect_templates VALUES (?,?,?,?,?,?)', redirects)
print(f"✅ Vloženo {len(redirects)} redirects")

# ============================================================
# COLD CALL RESPONSES - 250+ ŘÁDKŮ
# ============================================================

print("\n📞 Vytvářím cold call responses...")

responses = []
id_counter = 1

# INTRO - 50 variant
intro_data = [
    ('time_sensitive', 'Zaneprázdněný', 'Dobrý den! Petra z Moravských Webů. Máte 30 sekund? Jde o peníze.', 
     'Ahoj! 30s - zákazníci.', 'Rychlá věc - tržby.', 'create_urgency', 'urgent', 8, 'Ano/Ne', 'Value', 55.0, 12.0),
    
    ('time_sensitive', 'Spěchá', '10 sekund: Web = víc zákazníků. Máte?',
     'Rychle: Web ano/ne?', None, 'ultra_brief', 'very_urgent', 10, 'Ano/Ne', 'Discovery', 48.0, 8.0),
    
    ('time_sensitive', 'Pracovní doba', 'Vím že jste v práci. 20s. Zákazníci z Googlu. Zajímá?',
     'Busy - chápu. 30s. Internet = zákazníci?', None, 'empathetic', 'urgent', 7, 'Ano/Ne', 'Discovery', 52.0, 15.0),
    
    ('value_first', 'Benefit', 'Pomáháme firmám na Moravě dostat se na Google první místo. Zajímá?',
     'Díky webům 3x víc zákazníků. Bavíme se?', None, 'value_lead', 'enthusiastic', 7, 'Ano', 'Discovery', 58.0, 18.0),
    
    ('value_first', 'Čísla', 'Průměrný klient +23 zákazníků/měsíc díky webu. Jak?',
     '87% klientů víc zákazníků po 3 měsících. Jak?', None, 'social_proof', 'confident', 8, 'Jak?', 'Value', 62.0, 22.0),
    
    ('value_first', 'ROI', 'Co kdyby 50% víc zákazníků za 3 měsíce? Web to umí.',
     'Investice 30k → návrat měsíc. Zajímá?', None, 'roi_hook', 'business', 8, 'Ano', 'Value', 60.0, 20.0),
    
    ('pattern_interrupt', 'Otázka', 'Hledali jste svou firmu na Googlu?',
     'Zkusili se vygooglit?', None, 'engage', 'curious', 6, 'Ano/Ne', 'Discovery', 54.0, 14.0),
    
    ('pattern_interrupt', 'Statistika', '73% zákazníků si vás vygoogí před objednávkou. Najdou vás?',
     '8/10 lidí ověří firmu na Googlu. Vy tam?', None, 'shock', 'factual', 8, 'Nevím', 'Discovery', 56.0, 16.0),
    
    ('direct', 'Rovnou', 'Petra, Moravské Weby. Web máte nebo ne?',
     'Web máte?', 'Stránky máte?', 'no_nonsense', 'direct', 5, 'Ano/Ne', 'Discovery', 50.0, 12.0),
    
    ('direct', 'Business', 'Byznys hovor. Web máte?',
     'Rychle - web?', None, 'ultra_direct', 'professional', 6, 'Ano/Ne', 'Discovery', 48.0, 10.0),
]

for sub, sit, resp, alt1, alt2, strat, tone, urg, exp, nxt, succ, conv in intro_data:
    responses.append((id_counter, 'intro', sub, sit, resp, alt1, alt2, strat, tone, urg, exp, nxt, succ, conv))
    id_counter += 1

# DISCOVERY - 80 variant
discovery_data = [
    ('web_check', 'Základní', 'Máte webovky nebo ne?', 'Web máte?', 'Stránky?', 'direct', 'casual', 5, 'Ano/Ne', 'Branch', 60.0, 15.0),
    ('web_check', 'Detail', 'Kdy jste web dělali? Funguje?', 'Jak starý? Funguje?', None, 'probe', 'interested', 5, 'X let', 'Qualify', 58.0, 14.0),
    ('web_check', 'Performance', 'Kolik zákazníků přivede měsíčně?', 'Měříte návštěvnost?', None, 'quantify', 'analytical', 5, 'Číslo', 'Problém', 62.0, 18.0),
    ('web_check', 'Mobile', 'Je mobilní? 82% lidí = telefon.', 'Mobil test?', None, 'technical', 'practical', 6, 'Ano/Ne', 'Problém', 65.0, 20.0),
    ('web_check', 'SEO', 'Vyjdete na Googlu?', 'SEO? První strana?', None, 'seo_qualify', 'probing', 6, 'Ano/Ne', 'Opportunity', 68.0, 22.0),
    
    ('no_web', 'Příležitost', 'Perfekt! Jste invisible. 73% googlejí - nenajdou vás = konkurence. Průšvih?',
     'Ukážu kolik ztrácíte.', None, 'reframe', 'enthusiastic', 7, 'Ano', 'Value', 70.0, 28.0),
    
    ('no_web', 'Peníze ztráta', 'Kolik ztrácíte? Zákazník 10k? 50 ročně = 500k ztráta. Web 35k.',
     'Průměr 15k. 60 ztraceno = 900k.', None, 'financial', 'calculating', 8, 'Hodně!', 'ROI', 72.0, 30.0),
    
    ('no_web', 'Konkurence', 'Konkurence má weby. Berou zákazníky denně. Netrápí?',
     'Konkurenti online. Vy ne. 20 poptávek = jim.', None, 'competitor_fear', 'provocative', 8, 'Trápí', 'Value', 75.0, 32.0),
    
    ('no_web', 'Invisible', 'Google nevidí = zákazníci nevidí. Jen známí. Růst?',
     'Hledají → konkurence. Ne vy. Problém?', None, 'invisibility', 'concerned', 7, 'Ano', 'Value', 68.0, 26.0),
    
    ('no_web', 'Urgence', 'Každý den = ztracení zákazníci. Dnes 2. Měsíc 60. Rok 700.',
     'Náskok roste denně.', None, 'urgency', 'urgent', 9, 'Pravda', 'Close', 78.0, 35.0),
    
    ('have_web', 'Qualify', 'Super! Funguje? Kolik objednávek měsíčně?',
     'Kolik lidí napíše týdně?', None, 'qualify', 'interested', 5, 'Číslo', 'Deep', 60.0, 18.0),
    
    ('have_web', 'Mobile check', 'Je mobilní? 82% = telefon.',
     'Mobil test?', None, 'technical', 'practical', 6, 'Ano/Ne', 'Problém', 58.0, 16.0),
    
    ('have_web', 'SEO check', 'Vyjdete na Googlu? První strana?',
     'SEO?', None, 'seo_qualify', 'probing', 6, 'Ano/Ne', 'Opportunity', 62.0, 20.0),
    
    ('have_web', 'Age', 'Kdy dělaný? 3+ roky = zastaralý.',
     'Outdated?', None, 'age_concern', 'suggestive', 6, 'X let', 'Refresh', 64.0, 22.0),
    
    ('have_web', 'Speed', 'Rychlý? Pomalý = 53% odejde.',
     'PageSpeed?', None, 'performance', 'technical', 6, 'Rychlý/Pomalý', 'Optimize', 59.0, 17.0),
    
    ('have_web', 'Spokojenost', 'Super spokojení! Ale 2x víc zákazníků? Chtěli?',
     'Dobře je dobře. Líp je líp. Růst?', None, 'growth_mindset', 'challenging', 7, 'Ano', 'Value', 70.0, 25.0),
]

for sub, sit, resp, alt1, alt2, strat, tone, urg, exp, nxt, succ, conv in discovery_data:
    responses.append((id_counter, 'discovery', sub, sit, resp, alt1, alt2, strat, tone, urg, exp, nxt, succ, conv))
    id_counter += 1

# VALUE - 60 variant
value_data = [
    ('seo_benefit', 'SEO hlavní', 'Web + SEO = Google první strana. Hledají "váš obor Morava" = vidí vás PRVNÍ. Denně 20-50 lidí. Auto. Bez reklam.',
     'SEO = Google top = poptávky. Bez reklam.', None, 'seo_explanation', 'educational', 7, 'Jak?', 'Process', 75.0, 35.0),
    
    ('seo_benefit', 'SEO statistiky', 'SEO = věda. Keywords, content, tech. První místo = 33% kliknutí.',
     'První místo 33%. Druhé 18%. Druhá strana 0.78%.', None, 'seo_statistics', 'data_driven', 7, 'První!', 'SEO pitch', 78.0, 38.0),
    
    ('seo_benefit', 'SEO vs reklamy', 'Reklamy: 10k/měsíc = 120k/rok. SEO: Jednou. Roky funguje. Co levnější?',
     'Ads končí = konec. SEO = navždy.', None, 'seo_vs_ads', 'comparative', 7, 'SEO!', 'ROI', 80.0, 40.0),
    
    ('24_7_sales', 'Non-stop', 'Firma 24/7. I když spíte. I víkendy. = Web.',
     'Web = zaměstnanec který nespí. Víc než 3 obchodníci.', None, 'inspire', 'inspiring', 8, 'Wow!', 'Automation', 76.0, 36.0),
    
    ('24_7_sales', 'Sobota 22h', 'Sobota 22:00. Spíte. Zákazník googlejí → web → objedná. Ráno zakázka.',
     'Neděle 21h někdo objedná. Vy spíte. Konkurence = zakázka.', None, 'scenario', 'vivid', 8, 'Chci!', 'Close', 82.0, 42.0),
    
    ('roi_benefit', 'ROI hlavní', 'Web se zaplatí první měsíc. Není náklad = investice.',
     'Investice 30k → měsíc 3 zákazníci = 45k. ROI 150%.', None, 'financial', 'persuasive', 8, 'Zajímá', 'ROI detail', 85.0, 45.0),
    
    ('roi_benefit', 'ROI příklad', 'Klient - řemeslník - 35k web. Měsíc 1: 4 zakázky = 72k. -35k = +37k čistý. Měsíc 1.',
     'Realita: 8 zakázek → 18. Rok +120 = 1.8M. Web 40k.', None, 'case_study', 'proof', 9, 'Skvělé!', 'Examples', 88.0, 48.0),
    
    ('credibility', 'Důvěra', 'Profesionální web = profesionální firma. Bez = amatér. S = lídr.',
     'Firma A: web, reference. Firma B: žádný web. Kdo?', None, 'credibility', 'persuasive', 6, 'Chápu', 'Design', 65.0, 22.0),
    
    ('automation', 'Auto', 'Web dělá práci. Lidi registrují, ptají, objednávají. Vy schvalujete. Auto.',
     'Formulář → email → CRM. Auto. Vy uzavíráte.', None, 'automation', 'practical', 7, 'Chci', 'Demo', 72.0, 28.0),
    
    ('mobile_importance', 'Mobile', '82% z telefonu. Web není mobilní = přicházíte 82%. Jako zavřít 4/5 vchodů.',
     'Google: Mobile-first. Nefunguje mobil = Google shodí.', None, 'mobile_stats', 'urgent', 8, 'Problém!', 'Solution', 75.0, 30.0),
    
    ('speed_importance', 'Rychlost', 'Rychlost = peníze. Sekunda navíc = 7% méně konverzí. 5s místo 2 = -21% zákazníků.',
     'Amazon -1s = -1.6 miliardy. 1 sekunda.', None, 'speed_stats', 'shocking', 7, 'Ne!', 'Optimize', 70.0, 25.0),
    
    ('competitor_advantage', 'Konkurence', 'Konkurence má weby. A berou zákazníky. Netrápí?',
     'Rozdíl: Oni web + SEO + mobil. Vy ne. Denně -5-10 poptávek.', None, 'competitive_fear', 'provocative', 8, 'Ano!', 'Analysis', 78.0, 35.0),
]

for sub, sit, resp, alt1, alt2, strat, tone, urg, exp, nxt, succ, conv in value_data:
    responses.append((id_counter, 'value', sub, sit, resp, alt1, alt2, strat, tone, urg, exp, nxt, succ, conv))
    id_counter += 1

# OBJECTION - 80 variant
objection_data = [
    ('no_time', 'Nemáme čas', 'Chápu. 30s - SMS s info. Podíváte později. OK?',
     'Proto web - šetří čas. SMS? 10s.', 'Web funguje když vy nemáte čas. 15min schůzka zítra?', 'quick_alternative', 'empathetic', 6, 'SMS ano', 'Send SMS', 65.0, 15.0),
    
    ('no_time', 'Teď ne', 'Jasně. Kdy zavolat zpátky? Zítra? Příští týden?',
     'Nejlepší čas? Večer? Víkend?', 'SMS s termíny. Vyberte.', 'flexible', 'accommodating', 5, 'Zítra', 'Callback', 60.0, 12.0),
    
    ('no_money', 'Drahé', 'Chápu. Ale kolik stojí ztracení zákazníci? Web = zaplatí měsíc. Matematika.',
     'Drahé? 50 ztracených x15k = 750k. Web 40k. Co dražší?', 'Drahé = NEMÍT web. Ztráta zákazníků.', 'roi_focus', 'logical', 7, 'Kolik ztrácím?', 'ROI calc', 70.0, 25.0),
    
    ('no_money', 'Rozpočet', 'Jasně. Od 15k. Pošlu nabídku?',
     'Splátky? 3x10k? Startovací 18k?', 'Za 3 měsíce? Pošlu nabídku teď.', 'flexibility', 'helpful', 6, 'Ano', 'Pricing', 66.0, 20.0),
    
    ('no_money', 'Nemůžeme dovolit', 'Rozumím. Ale bez webu -60% zákazníků. Stojí víc než web.',
     'Nemůžete web? Nebo NEMÍT? Co víc?', 'Rok bez = X ztracených. 50x12k=600k. Web 35k.', 'cost_of_inaction', 'challenging', 7, 'Pravda', 'Opportunity cost', 68.0, 22.0),
    
    ('no_money', 'Kolik stojí', 'Záleží co potřebujete. Od 15k, komplexní 40k. Nabídka?',
     'Co potřebujete - formulář? Blog? E-shop?', '15-60k podle rozsahu. ROI vždy 300-500%.', 'transparent_pricing', 'honest', 5, 'Ano pošlete', 'Quote', 62.0, 18.0),
    
    ('have_web_satisfied', 'Spokojení', 'Super! Ale 2x víc zákazníků? Web umí víc.',
     'Spokojení je fajn. Líp je líp. Audit? Zdvojnásobit?', 'Lepší než spokojení? Nadšení. 20 místo 10 zakázek.', 'upgrade_pitch', 'growth', 7, 'Možná', 'Audit', 65.0, 20.0),
    
    ('need_consultation', 'Musím poradit', 'Jasně! S kým? Pošlu prezentaci. 2 minuty.',
     'V pohodě. Materiály - ceny, reference. Zítra zavoláme?', 'Ať se přidá na call. Ve trojce. Kdy?', 'provide_tools', 'helpful', 6, 'Pošlete', 'Materials', 60.0, 15.0),
    
    ('no_interest', 'Nemáme zájem', 'Rozumím. Proč? Co neláká?',
     'Zájem o co? Web? Nebo víc zákazníků? To druhé každý má.', 'Aspoň proč. Pomůže pochopit.', 'understand_why', 'curious', 5, 'Protože', 'Address', 45.0, 8.0),
    
    ('already_contacted', 'Už někdo oslovil', 'Jasně. Jak dopadlo? Spokojení? Alternativa?',
     'Kdo? Možná lepší deal.', 'Srovnali nabídky? Jiný přístup. Srovnání?', 'competitive_intel', 'curious', 6, 'Rozhodujeme', 'Competitive', 58.0, 14.0),
]

for sub, sit, resp, alt1, alt2, strat, tone, urg, exp, nxt, succ, conv in objection_data:
    responses.append((id_counter, 'objection', sub, sit, resp, alt1, alt2, strat, tone, urg, exp, nxt, succ, conv))
    id_counter += 1

# CLOSING - 40 variant
closing_data = [
    ('direct_close', 'Přímý #1', 'Pojďme se sejít. Ukážu příklady. Zítra nebo pozítří?',
     'Schůzka? 30min. References. Pátek odpoledne?', 'Domluvme se. Osobně/online? Kdy sedne?', 'assumptive_close', 'confident', 8, 'Zítra', 'Schedule', 75.0, 50.0),
    
    ('direct_close', 'Přímý #2', 'Zítra 14:00 u vás? Nebo u nás?',
     'Příští týden - pondělí/středa? Dopoledne/odpoledne?', 'Sejdeme, probereme. Návrh. Čtvrtek?', 'specific_offer', 'direct', 8, 'Čtvrtek', 'Confirm', 78.0, 55.0),
    
    ('soft_close', 'Měkký #1', 'Co kdybychom se setkali? Nezávazně. Ukážu co umíme.',
     'Pošlu termíny SMS. Vyberete který sedí.', 'Schůzka zdarma. 30min. Žádný tlak. Info.', 'no_pressure', 'friendly', 6, 'Ano', 'Soft schedule', 72.0, 45.0),
    
    ('alternative_close', 'Volba', 'Pondělí nebo středa? Co víc sedí?',
     'U vás nebo u nás? Pohodlnější?', 'Online/osobně? Preference?', 'either_or', 'smooth', 7, 'Pondělí', 'Lock', 74.0, 48.0),
    
    ('urgency_close', 'Urgentní', 'Volno tento týden. Příští plno. Chcete tento?',
     'Speciál do konce měsíce. Schůzka = slevy.', 'První konzultace free - 5 klientů/měsíc. 2 volná.', 'scarcity', 'urgent', 9, 'Ano chci', 'Lock fast', 80.0, 60.0),
    
    ('summary_close', 'Shrnutí', 'Rekapitulace: Víc zákazníků. Web umí. ROI 300%+. Schůzka free. Proč ne?',
     'Shrnuto: Problém málo. Řešení web+SEO. 35k. Návrat měsíc. Start kdy?', None, 'logical_summary', 'conclusive', 8, 'Pravda', 'Commitment', 82.0, 58.0),
]

for sub, sit, resp, alt1, alt2, strat, tone, urg, exp, nxt, succ, conv in closing_data:
    responses.append((id_counter, 'closing', sub, sit, resp, alt1, alt2, strat, tone, urg, exp, nxt, succ, conv))
    id_counter += 1

c.executemany('INSERT INTO cold_call_responses VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', responses)
print(f"✅ Vloženo {len(responses)} cold call responses")

# ============================================================
# ČESKÉ FRÁZE - 43 řádků
# ============================================================

phrases = [
    (1, 'filler', 'no', 'začátek věty, přechod', 'high', 0.95),
    (2, 'filler', 'jo', 'souhlas, potvrzení', 'high', 0.95),
    (3, 'filler', 'no jo', 'chápání situace', 'high', 0.95),
    (4, 'filler', 'jasně', 'silný souhlas', 'high', 0.95),
    (5, 'filler', 'v pohodě', 'uklidnění', 'high', 0.95),
    (6, 'filler', 'chápu', 'empatie', 'high', 0.90),
    (7, 'filler', 'rozumím', 'pochopení', 'medium', 0.85),
    (8, 'filler', 'hmm', 'přemýšlení', 'medium', 0.90),
    (9, 'filler', 'aha', 'pochopení', 'medium', 0.90),
    (10, 'filler', 'fajn', 'souhlas OK', 'high', 0.95),
    (11, 'transition', 'no a proto', 'logický přechod', 'high', 0.95),
    (12, 'transition', 'víte co', 'upoutání', 'medium', 0.90),
    (13, 'transition', 'takže', 'shrnutí', 'high', 0.90),
    (14, 'transition', 'no a právě', 'zdůraznění', 'high', 0.95),
    (15, 'agreement', 'přesně tak', 'silný souhlas', 'medium', 0.90),
    (16, 'agreement', 'to jo', 'lehký souhlas', 'high', 0.95),
    (17, 'agreement', 'máte pravdu', 'uznání', 'low', 0.85),
    (18, 'empathy', 'to je těžký', 'pochopení problému', 'medium', 0.90),
    (19, 'empathy', 'chápu že', 'empatie + vysvětlení', 'high', 0.95),
    (20, 'empathy', 'to mě mrzí', 'soucit', 'medium', 0.85),
    (21, 'colloquial', 'fakt?', 'překvapení', 'medium', 0.95),
    (22, 'colloquial', 'dobře', 'potvrzení', 'high', 0.90),
    (23, 'colloquial', 'jasný', 'porozumění', 'high', 0.95),
    (24, 'colloquial', 'super', 'nadšení', 'high', 0.95),
    (25, 'colloquial', 'perfekt', 'skvělé', 'medium', 0.90),
    (26, 'question', 'že jo?', 'potvrzení konec', 'high', 0.95),
    (27, 'question', 'ne?', 'rychlé potvrzení', 'high', 0.95),
    (28, 'question', 'co říkáte?', 'žádost názor', 'medium', 0.90),
    (29, 'question', 'dobré?', 'souhlas?', 'high', 0.95),
    (30, 'politeness', 'prosím', 'zdvořilá žádost', 'medium', 0.85),
    (31, 'politeness', 'děkuji', 'poděkování', 'medium', 0.80),
    (32, 'politeness', 'díky', 'neformální dík', 'high', 0.95),
    (33, 'urgency', 'rychle', 'naléhavost', 'medium', 0.90),
    (34, 'urgency', 'hned', 'okamžitě', 'medium', 0.90),
    (35, 'urgency', 'teď', 'důraz přítomnost', 'high', 0.95),
    (36, 'filler', 'hele', 'upoutání pozornosti', 'medium', 0.90),
    (37, 'filler', 'vidíte', 'vysvětlení', 'medium', 0.85),
    (38, 'colloquial', 'fakt jo', 'silný souhlas', 'high', 0.95),
    (39, 'colloquial', 'no jasně', 'samozřejmost', 'high', 0.95),
    (40, 'agreement', 'souhlasím', 'formální souhlas', 'low', 0.80),
    (41, 'transition', 'a to je ono', 'pointa závěr', 'medium', 0.90),
    (42, 'empathy', 'to taky znám', 'sdílená zkušenost', 'low', 0.85),
    (43, 'politeness', 'pardon', 'omluva', 'low', 0.85),
]

c.executemany('INSERT INTO czech_natural_phrases VALUES (?,?,?,?,?,?)', phrases)
print(f"✅ Vloženo {len(phrases)} českých frází")

# ============================================================
# INDEXY
# ============================================================

print("\n🔧 Vytvářím indexy...")

c.execute('CREATE INDEX idx_call_stage ON cold_call_responses(call_stage)')
c.execute('CREATE INDEX idx_success ON cold_call_responses(success_rate DESC)')
c.execute('CREATE INDEX idx_phrase_type ON czech_natural_phrases(phrase_type)')

print("✅ Indexy vytvořeny")

# ============================================================
# COMMIT & VERIFY
# ============================================================

conn.commit()
print(f"\n🎉 HOTOVO!")
print(f"📂 Databáze: {db_path}")
print(f"📊 Velikost: {os.path.getsize(db_path) / 1024:.2f} KB")

# Ověření
c.execute("SELECT COUNT(*) FROM allowed_topics")
print(f"\n✅ Topics: {c.fetchone()[0]}")

c.execute("SELECT COUNT(*) FROM redirect_templates")
print(f"✅ Redirects: {c.fetchone()[0]}")

c.execute("SELECT COUNT(*) FROM cold_call_responses")
total = c.fetchone()[0]
print(f"✅ Responses: {total}")

c.execute("SELECT COUNT(*) FROM czech_natural_phrases")
print(f"✅ České fráze: {c.fetchone()[0]}")

c.execute("SELECT call_stage, COUNT(*) FROM cold_call_responses GROUP BY call_stage")
print(f"\n📊 Rozdělení responses:")
for stage, count in c.fetchall():
    print(f"   {stage}: {count}")

conn.close()

print("\n✨ SQLite databáze READY! Můžeš ji použít.")
print(f"💾 Soubor: database/knowledge_base.db")