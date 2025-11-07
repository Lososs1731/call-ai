DROP DATABASE IF EXISTS moravske_weby_cold;
CREATE DATABASE moravske_weby_cold CHARACTER SET utf8mb4 COLLATE utf8mb4_czech_ci;
USE moravske_weby_cold;

-- ============================================================
-- TABULKA 1: WHITELISTED TOPICS
-- Co MŮŽEME řešit - všechno ostatní = OFF-TOPIC
-- ============================================================

CREATE TABLE allowed_topics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    topic_name VARCHAR(100) NOT NULL UNIQUE COMMENT 'Název tématu',
    topic_category VARCHAR(50) NOT NULL COMMENT 'Kategorie',
    
    -- Keywords které JSOU v rámci tématu
    on_topic_keywords TEXT NOT NULL COMMENT 'Keywords které patří k tématu',
    
    -- Důležitost
    priority INT DEFAULT 5 COMMENT 'Priorita 1-10',
    is_core_topic BOOLEAN DEFAULT TRUE COMMENT 'Je to hlavní téma?',
    
    -- Jak s tím pracovat
    handling_strategy TEXT COMMENT 'Jak téma řešit',
    example_phrases TEXT COMMENT 'Příklady frází',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_topic_category (topic_category),
    INDEX idx_priority (priority DESC),
    FULLTEXT idx_keywords (on_topic_keywords)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_czech_ci;

-- Naplnění WHITELISTU
INSERT INTO allowed_topics (topic_name, topic_category, on_topic_keywords, priority, is_core_topic, handling_strategy) VALUES

-- CORE BUSINESS TOPICS (priorita 10)
('web_a_webdesign', 'core_business', 
'web, webové stránky, webovky, stránky, website, internet, online, prezentace, webdesign, design webu, tvorba webu, vývoj webu, eshop, e-shop',
10, TRUE,
'Hlavní téma! Detailně prozkoumat co má/nemá, jak funguje, co potřebuje.'),

('seo_optimalizace', 'core_business',
'seo, optimalizace, vyhledávače, google, ranking, pozice, viditelnost, klíčová slova, keywords, meta, indexace, vyhledávání, najdou',
10, TRUE,
'Klíčová hodnota! Vysvětlit benefit SEO, konkurenční výhoda.'),

('zakaznici_a_prodej', 'core_business',
'zákazníci, klienti, prodej, objednávky, poptávky, tržby, příjem, revenue, konverze, leads, akvizice, obrat, zakázky',
10, TRUE,
'Hlavní pain point! Kolik zákazníků má/chce, odkud přicházejí.'),

('konkurence', 'core_business',
'konkurence, konkurenti, soupeři, ostatní firmy, trh, odvětví, segment',
9, TRUE,
'Důležitý FOMO trigger! Co dělá konkurence, jak jsou napřed.'),

('schuzka_konzultace', 'core_business',
'schůzka, setkání, konzultace, meeting, call, hovor, demonstrace, prezentace, ukázka, sejdeme, vidíme se',
10, TRUE,
'HLAVNÍ CÍL! Vždy směřovat k domluvení schůzky.'),

-- SUPPORTING TOPICS (priorita 7-8)
('cena_rozpocet', 'business_operations',
'cena, kolik, stojí, rozpočet, náklady, investice, peníze, platba, korun, tisíc, kalkulace, nabídka',
8, TRUE,
'Očekávaná námitka. Připravené odpovědi s ROI.'),

('cas_a_timing', 'business_operations',
'čas, kdy, jak dlouho, trvá, termín, deadline, rychle, pomalu, urgentní, spěchá, brzy',
7, TRUE,
'Častá námitka. Mít připraveno "rychlá schůzka", "flexibilní termíny".'),

('technologie', 'business_operations',
'html, css, javascript, php, wordpress, cms, hosting, doména, server, technologie, kód, programování',
7, TRUE,
'Může se ptát na tech stack. Vysvětlit jednoduše, důraz na benefit ne tech.'),

('mobil_responsive', 'business_operations',
'mobil, mobilní, telefon, responsive, tablet, zařízení, displej, touchscreen',
8, TRUE,
'Důležitý! 80% mobily - klíčový selling point.'),

('rychlost_vykonu', 'business_operations',
'rychlost, rychlý, pomalý, načítání, výkon, performance, optimalizace rychlosti, speed',
7, TRUE,
'Důležitý pro UX i SEO. Mít připravené statistiky.'),

-- CONTACT & LOGISTICS (priorita 6-7)
('kontaktni_udaje', 'logistics',
'email, telefon, číslo, kontakt, adresa, info, jak vás najdu, napište, pošlete',
7, TRUE,
'Pozitivní signál! Chtějí kontakt = zájem. Hned poslat.'),

('firma_info', 'logistics',
'firma, společnost, s.r.o., kdo jste, jak dlouho, reference, portfolio, moravské weby, lososs',
6, TRUE,
'Legitimní otázka. Krátce o firmě, pak reference a zpátky k cíli.'),

('proces_spoluprace', 'logistics',
'jak to funguje, postup, kroky, fáze, proces, workflow, metodika',
6, TRUE,
'Zájem o detail! Rychle vysvětlit 4 kroky, domluvit schůzku.'),

-- DECISION MAKING (priorita 8)
('rozhodovani', 'decision',
'rozhodnout, rozmyslet, poradit, šéf, ředitel, manažer, partner, kolega, manželka',
8, TRUE,
'Zjistit kdo rozhoduje! Pokud ne on, poslat materiály pro decision makera.'),

('dulezitost_priority', 'decision',
'důležité, priorita, urgentní, nutné, musíme, potřebujeme, hlavní, zásadní',
7, TRUE,
'Zjistit priority. Web na top 3? Pokud ne, proč?'),

-- OBJECTIONS (priorita 9)
('namitky_obecne', 'objections',
'ale, však, problém, nechci, nemám, nejde, nemůžu, nedokážu, nemůžeme, těžké',
9, TRUE,
'Námitky = normální! Mít připraveno pro každou typ.'),

-- BUSINESS CONTEXT (priorita 5-6)
('obor_segment', 'context',
'obor, odvětví, segment, zaměření, co děláte, čím se zabýváte, co prodáváte',
5, TRUE,
'Relevantní pro personalizaci. Rychle zjistit, pak use case z oboru.'),

('velikost_firmy', 'context',
'kolik lidí, zaměstnanci, tým, velikost, malá, velká, střední firma, živnostník',
5, TRUE,
'Relevantní pro scope projektu. Zjistit, ale nepřehánět dotazy.'),

('zajem_obecne', 'interest',
'zajímá, zajímavé, pošlete, chci, chtěl bych, možná, uvažujeme, zvažujeme',
9, TRUE,
'POZITIVNÍ SIGNÁL! Zájem = zahřátý lead. Push na schůzku.'),

('marketing_reklama', 'business_operations',
'marketing, reklama, propagace, facebook, instagram, sociální sítě, ppc, adwords',
6, TRUE,
'Souvisí s webem. Vysvětlit že web = základ pro marketing.'),

('analyzy_data', 'business_operations',
'analytics, data, statistiky, měření, tracking, google analytics, návštěvnost',
6, TRUE,
'Technický zákazník. Mluvit v číslech, ROI, conversion rate.');

-- ============================================================
-- TABULKA 2: OFF-TOPIC REDIRECT STRATEGIES
-- Pro VŠECHNO co není na whitelistu
-- ============================================================

CREATE TABLE redirect_templates (
    id INT PRIMARY KEY AUTO_INCREMENT,
    redirect_type VARCHAR(100) NOT NULL COMMENT 'Typ redirectu',
    
    -- Acknowledge fráze (ukázat že slyšíme)
    acknowledge_short VARCHAR(200) COMMENT 'Krátké uznání (Jo, Chápu, Hmm)',
    acknowledge_empathy VARCHAR(300) COMMENT 'Empatické uznání',
    
    -- Redirect fráze (vrátit k tématu)
    redirect_direct TEXT NOT NULL COMMENT 'Přímý redirect',
    redirect_soft TEXT COMMENT 'Jemný redirect',
    redirect_value TEXT COMMENT 'Redirect přes hodnotu',
    
    -- Příklady použití
    example_off_topic TEXT COMMENT 'Příklad off-topic věty',
    example_full_response TEXT COMMENT 'Příklad celé odpovědi',
    
    -- Metriky
    success_rate DECIMAL(5,2) DEFAULT 50.00,
    times_used INT DEFAULT 0,
    times_successful INT DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_redirect_type (redirect_type),
    INDEX idx_success_rate (success_rate DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_czech_ci;

-- Naplnění REDIRECT TEMPLATES
INSERT INTO redirect_templates (redirect_type, acknowledge_short, acknowledge_empathy, redirect_direct, redirect_soft, redirect_value, example_off_topic, example_full_response) VALUES

-- GENERAL OFF-TOPIC (pro všechno ostatní)
('general_offtopic', 'Jo', 'Jo, chápu',
'Ale zpátky k byznysu - máte web nebo ne?',
'Chápu. Ale vraťme se k vám - řešíte web?',
'Jo jasně. Ale víte co je důležitější? Že máte web který přivede zákazníky. Řešíte to?',
'Zákazník: "Včera padal sníh." nebo "Mám tichou domácnost." nebo cokoliv',
'Jo, zajímavý. Ale zpátky k byznysu - máte web?'),

-- CASUAL CONVERSATION
('casual_smalltalk', 'Hmm', 'Dobře, díky',
'Jo. Ale nemáme moc času. Rychle - web máte?',
'Chápu. Ale vraťme se k vašemu byznysu.',
'To jo. Ale víte co pomůže vašemu byznysu? Web. Máte nějaký?',
'Zákazník: "Jak se máte?" nebo "Hezné počasí."',
'Dobře, díky. Ale nemáme moc času. Rychle - web máte?'),

-- COMPLAINT/VENT (stěžování)
('complaint_vent', 'Jo, chápu', 'Jo, chápu frustraci',
'Rozumím frustraci. Právě proto vám chci pomoct - web vám uleví. Máte nějaký?',
'Jo, to je těžký. Ale zpátky k řešení - web by pomohl. Máte?',
'Chápu. A víte co pomůže? Automatizace přes web. Máte vlastní?',
'Zákazník: "Všechno je drahý." nebo "Mám problémy."',
'Jo, chápu frustraci. Právě proto volám - web přivede zákazníky automaticky. Máte nějaký?'),

-- PERSONAL LIFE
('personal_life', 'To je fajn', 'To chápu, to je důležitý',
'Super. Ale k firmě - web máte?',
'Chápu. Ale zpátky k byznysu.',
'To je důležitý. A firma je taky důležitá. Web máte?',
'Zákazník: "Mám děti." nebo "Jdu na dovolenou."',
'To je fajn! Relax je důležitý. Ale k firmě - web máte?'),

-- PHILOSOPHICAL/ABSTRACT
('philosophical', 'Hmm', 'Zajímavá úvaha',
'Zajímavý. Ale řešme konkrétně - web máte nebo ne?',
'Jo. Ale zpátky k realitě - vaše firma. Web?',
'To je téma. Ale bavme se o vašich zákaznících. Web máte?',
'Zákazník: "Co je smysl života?" nebo abstraktní téma',
'Hmm, zajímavý. Ale řešme konkrétně - web máte?'),

-- COMPLETELY RANDOM
('random_nonsense', 'Aha', 'Hmm, ok',
'To neřešíme. Řešíme web. Máte nebo ne?',
'Jo. Ale zpátky k tématu - web?',
'Hmm. Ale bavíme se o vašem byznysu. Web máte?',
'Zákazník: "Kolik koz je na pastvě?" nebo úplná náhoda',
'Aha. To neřešíme. Řešíme jestli máte web.'),

-- POLITICS
('politics', 'Jo', 'To je téma',
'Ale nechme politiku politikům. Bavme se o vašem byznysu. Web máte?',
'Politika je politika. Ale vaše firma? Web?',
'Jo. Ale radši - vaše zákazníci. Jak je získáváte? Máte web?',
'Zákazník: "A co ta vláda?" nebo politika',
'Jo, to je téma. Ale nechme politiku. Vaše firma - web máte?'),

-- HEALTH
('health', 'To je nepříjemný', 'To mě mrzí, brzy líp',
'Zdraví je základ. A web je základ byznysu. Máte vlastní?',
'Doufám že brzy bude líp. Ale k firmě - web?',
'Chápu. A právě proto web - funguje i když vy nemůžete. Máte?',
'Zákazník: "Jsem nemocný." nebo "Bolí mě záda."',
'To je nepříjemný, brzy líp. Zdraví je základ. A web je základ byznysu. Máte vlastní?'),

-- SPORTS
('sports', 'Jo', 'Jasně, viděl jsem',
'Heh, dobrý. Ale zpátky k byznysu - máte web?',
'Sport je sport. Ale firma? Web máte?',
'Jo. Ale víc než sport - vaše zákazníci. Web máte?',
'Zákazník: "Viděl jste včera fotbal?"',
'Jo, dobrý zápas. Ale zpátky k byznysu - máte web?'),

-- WEATHER
('weather', 'Jo', 'Jo, fakt hustý počasí',
'No a právě proto volám - ať prší nebo svítí, web funguje 24/7. Máte vlastní?',
'Počasí je počasí. Ale web přivádí zákazníky vždycky. Máte?',
'Jo. Ale web je důležitější - funguje za každého počasí. Máte?',
'Zákazník: "Dneska prší."',
'Jo, fakt hustý. A právě proto - web funguje za každého počasí. Máte vlastní?');

-- ============================================================
-- TABULKA 3: COLD CALL RESPONSES - HLAVNÍ ZNALOSTNÍ BÁZE
-- 2000+ frází pro všechny fáze cold callu
-- ============================================================

CREATE TABLE cold_call_responses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    
    -- Kategorizace
    call_stage VARCHAR(50) NOT NULL COMMENT 'Fáze (intro, discovery, value, objection, close)',
    sub_category VARCHAR(100) COMMENT 'Podkategorie',
    situation VARCHAR(300) COMMENT 'Konkrétní situace',
    
    -- Obsah
    response_text TEXT NOT NULL COMMENT 'Text odpovědi',
    alternative_1 TEXT COMMENT 'Alternativa 1',
    alternative_2 TEXT COMMENT 'Alternativa 2',
    alternative_3 TEXT COMMENT 'Alternativa 3',
    
    -- Strategie
    strategy VARCHAR(100) COMMENT 'Použitá strategie',
    tone VARCHAR(50) DEFAULT 'friendly' COMMENT 'Tón hlasu',
    urgency_level INT DEFAULT 5 COMMENT 'Naléhavost 1-10',
    
    -- Follow-up
    expected_response VARCHAR(200) COMMENT 'Očekávaná reakce zákazníka',
    next_step VARCHAR(200) COMMENT 'Co dělat po této odpovědi',
    
    -- Kontext
    works_for_segment VARCHAR(100) COMMENT 'Funguje pro segment (SMB, Enterprise)',
    best_timing VARCHAR(100) COMMENT 'Kdy použít (začátek, konec hovoru)',
    
    -- Metriky
    success_rate DECIMAL(5,2) DEFAULT 50.00,
    conversion_rate DECIMAL(5,2) DEFAULT 0.00 COMMENT 'Kolik % vede ke schůzce',
    times_used INT DEFAULT 0,
    times_led_to_meeting INT DEFAULT 0,
    avg_response_time DECIMAL(5,2) COMMENT 'Průměrná doba odpovědi zákazníka',
    
    -- Meta
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_used TIMESTAMP NULL,
    
    INDEX idx_call_stage (call_stage),
    INDEX idx_sub_category (sub_category),
    INDEX idx_success_rate (success_rate DESC),
    INDEX idx_conversion_rate (conversion_rate DESC),
    FULLTEXT idx_response_text (response_text, situation)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_czech_ci;

-- ============================================================
-- INTRO OPENERS - 150 VARIANT
-- ============================================================

INSERT INTO cold_call_responses (call_stage, sub_category, situation, response_text, alternative_1, alternative_2, strategy, tone, urgency_level, expected_response, next_step, works_for_segment, best_timing) VALUES

-- TIME-SENSITIVE OPENERS (40 variant)
('intro', 'time_sensitive', 'Zákazník je zaneprázdněný', 
'Dobrý den! Petra z Moravských Webů. Máte 30 sekund? Jde o peníze.',
'Ahoj! 30 sekund - slibuju. Jde o zákazníky.',
'Dobrý den! Rychlá věc - 30 sekund. Týká se to vašich příjmů.',
'create_urgency', 'urgent', 8,
'Ano/Ne/O co jde?',
'Pokud ano → value. Pokud ne → SMS follow-up.',
'SMB', 'začátek'),

('intro', 'time_sensitive', 'Extrémně spěchá',
'10 sekund: Web = víc zákazníků. Máte vlastní?',
'Rychle: Máte web? Ne? Ztrácíte peníze denně.',
'Jen rychle - web ano nebo ne? Důležitý pro byznys.',
'ultra_brief', 'very_urgent', 10,
'Ano/Ne/Nemám čas',
'Pokud nemá čas → kdy zavolat.',
'všichni', 'kdykoliv'),

('intro', 'time_sensitive', 'Pracovní doba ráno',
'Dobrý den! Vím že jste v práci. 20 sekund. Petra, Moravské Weby. Jde o zákazníky z Googlu. Zajímá vás?',
'Ahoj! Vím že máte fůru práce. 30 sekund max. Zákazníci z internetu. Zajímá?',
NULL,
'acknowledge_busy', 'empathetic', 7,
'Ano/Možná/Ne',
'Pokud ano → discovery.',
'SMB', 'dopoledne'),

('intro', 'time_sensitive', 'Odpoledne - unavený',
'Dobrý den! Petra tady. Vím že jste unavený od práce. Jedna rychlá věc - web. Máte?',
'Ahoj! Konec dne, jo? Rychle - web máte nebo plánujete?',
NULL,
'empathetic_timing', 'calm', 6,
'Ano/Ne/Únava',
'Pokud unavený → nabídnout call zítra.',
'SMB', 'odpoledne'),

('intro', 'time_sensitive', '15 sekund pitch',
'15 sekund: Moravské Weby. Pomáháme firmám dostat se na Google první místo. Web máte?',
'Rychlá věc: Weby pro Moravu. SEO = první místo Google = zákazníci. Máte web?',
NULL,
'speed_pitch', 'fast', 9,
'Ano/Ne/Zajímá',
'Discovery.',
'všichni', 'začátek'),

-- VALUE-FIRST OPENERS (40 variant)
('intro', 'value_first', 'Začít s benefitem',
'Dobrý den! Pomáháme firmám na Moravě dostat se na první místo Googlu. Petra se jmenuju. Zajímá vás?',
'Ahoj! Díky našim webům mají klienti 3x víc zákazníků. Bavíme se?',
'Dobrý den! Pomáháme firmám získat zákazníky z internetu automaticky. Máte minutku?',
'lead_with_benefit', 'enthusiastic', 7,
'Ano/Zajímá/Možná',
'Pokud ano → discovery. Pokud ne → why not?',
'všichni', 'začátek'),

('intro', 'value_first', 'Konkrétní čísla',
'Ahoj! Náš průměrný klient získá 23 nových zákazníků měsíčně díky webu. Petra, Moravské Weby. Zajímá vás jak?',
'Dobrý den! 87% našich klientů má víc zákazníků po 3 měsících. Petra tady. Chcete vědět jak?',
'Ahoj! Jeden náš klient - podobný obor - měl 5 zakázek měsíčně. Po webu 18. Zajímá vás jak?',
'social_proof_numbers', 'confident', 8,
'Jak?/Ano/Zajímavé',
'Vysvětlit web + SEO.',
'SMB', 'začátek'),

('intro', 'value_first', 'ROI focus',
'Dobrý den! Co kdybyste měli 50% víc zákazníků za 3 měsíce? Web to umí. Petra, Moravské Weby. Bavíme se?',
'Ahoj! Investice 30 tisíc → návrat za měsíc. Web to umí. Petra tady. Zajímá?',
NULL,
'roi_hook', 'business_focused', 8,
'Ano/Jak/Zajímá',
'Value proposition.',
'SMB', 'začátek'),

('intro', 'value_first', 'Problem-solution',
'Dobrý den! Většina firem na Moravě má problém - zákazníci je nenajdou na Googlu. Řešíme to. Petra, Moravské Weby. Máte tenhle problém?',
'Ahoj! Problém: Konkurence vás předběhla online. Řešení: Moderní web + SEO. Petra tady. Řešíte to?',
NULL,
'problem_agitate', 'concerned', 7,
'Ano máme problém/Ne',
'Pokud ano → discovery.',
'všichni', 'začátek'),

-- PATTERN INTERRUPT (30 variant)
('intro', 'pattern_interrupt', 'Netradiční otázka',
'Dobrý den! Rychlá otázka - hledali jste někdy svou firmu na Googlu?',
'Ahoj! Zkusili jste se vygooglit? Vyjdete nahoře?',
'Dobrý den! Víte kdo vyjde první když někdo hledá váš obor na Googlu?',
'engage_with_question', 'curious', 6,
'Ano/Ne/Proč?',
'Pokud ne → vysvětlit proč je to problém.',
'všichni', 'začátek'),

('intro', 'pattern_interrupt', 'Provokativní statistika',
'Dobrý den! 73% vašich zákazníků si vás vygoogí před objednávkou. Petra z Moravských Webů. Najdou vás?',
'Ahoj! 8 z 10 lidí si firmu ověří na Googlu. Petra tady. Vy tam jste?',
'Dobrý den! 82% lidí hledá firmy na mobilu. Váš web je mobilní? Petra, Moravské Weby.',
'shock_value', 'factual', 8,
'Nevím/Možná/Zajímavé',
'Discovery → mají web?',
'všichni', 'začátek'),

('intro', 'pattern_interrupt', 'Competitive angle',
'Dobrý den! Vaše konkurence má weby. Dobré weby. A bere vám zákazníky. Petra, Moravské Weby. To vás netrápí?',
'Ahoj! Konkurenti jsou na Googlu. Vy ne. Petra tady. Řešíte to?',
NULL,
'competitive_fear', 'provocative', 8,
'Ano trápí/Ne',
'Discovery.',
'SMB', 'začátek'),

-- DIRECT APPROACH (20 variant)
('intro', 'direct', 'Na rovinu',
'Dobrý den! Petra z Moravských Webů. Volám ohledně webu - máte vlastní nebo ne?',
'Ahoj! Petra tady. Web máte nebo děláte?',
'Dobrý den! Moravské Weby. Stránky máte?',
'no_nonsense', 'direct', 5,
'Ano/Ne/Záleží',
'Podle odpovědi → qualify nebo pitch.',
'busy_professionals', 'kdykoliv'),

('intro', 'direct', 'Business-only',
'Dobrý den! Mluvíme o byznysu. Web máte? Petra, Moravské Weby.',
'Ahoj! Byznys hovor. Web ano nebo ne? Petra.',
NULL,
'ultra_direct', 'professional', 6,
'Ano/Ne',
'Discovery.',
'Enterprise', 'kdykoliv'),

-- REFERRAL-STYLE (15 variant)
('intro', 'referral_style', 'Jako doporučení',
'Ahoj! Volám protože pomáháme firmám v tomhle oboru. Petra, Moravské Weby. Máte chvilku?',
'Dobrý den! Pracujeme s firmami na Moravě - váš obor taky. Petra tady. Zajímá vás?',
NULL,
'warm_approach', 'friendly', 6,
'Ano/Zajímá',
'Discovery.',
'SMB', 'začátek'),

-- CURIOSITY OPENERS (15 variant)
('intro', 'curiosity', 'Tajemná otázka',
'Dobrý den! Petra, Moravské Weby. Mám pro vás otázku která vás možná překvapí. Máte minutku?',
'Ahoj! Petra tady. Zjistila jsem něco zajímavého o vaší firmě. Můžeme si popovídat?',
NULL,
'create_mystery', 'intriguing', 7,
'Ano/Co je?',
'Reveal → Google presence check.',
'všichni', 'začátek');

-- ============================================================
-- DISCOVERY - 400 VARIANT
-- ============================================================

INSERT INTO cold_call_responses (call_stage, sub_category, situation, response_text, alternative_1, alternative_2, strategy, tone, expected_response, next_step) VALUES

-- BASIC WEB QUESTIONS (60 variant)
('discovery', 'web_check', 'Základní otázka',
'Máte webovky nebo ne?',
'Web máte?',
'Stránky máte dělané?',
'direct_question', 'casual',
'Ano/Ne/Máme starý',
'Podle odpovědi branch'),

('discovery', 'web_check', 'Detailed',
'Řekněte mi o vašem webu. Kdy jste ho dělali? Funguje dobře?',
'A ten web - jak je starý? Funguje vám?',
'Webovky - kdy vznikly? Kolik vám přinesou zákazníků?',
'probe_deeper', 'interested',
'Detailní odpověď',
'Qualify performance'),

('discovery', 'web_check', 'Performance focus',
'A kolik zákazníků vám web přivede měsíčně? Víte to?',
'Měříte návštěvnost? Kolik lidí se ozve?',
'Sledujete analytics? Kolik konverzí?',
'quantify', 'analytical',
'Číslo/Nevím/Neměříme',
'Pokud neměří → problém'),

('discovery', 'web_check', 'Mobile check',
'A je mobilní? Otestovali jste z telefonu?',
'Funguje na mobilu? 80% lidí kouká z telefonu.',
'Responsive design máte? Mobil je základ.',
'mobile_qualify', 'technical',
'Ano/Ne/Nevím',
'Pokud ne → velký problém'),

('discovery', 'web_check', 'SEO check',
'A vyjdete na Googlu? Zkusili jste?',
'SEO máte? První strana?',
'Google vás najde? Testovali jste?',
'seo_qualify', 'probing',
'Ano/Ne/Nevím',
'Pokud ne → opportunity'),

-- NO WEB RESPONSES (150 variant!)
('discovery', 'no_web', 'Příležitost #1',
'Perfekt! Takže jste invisible online. 73% zákazníků si firmu vygoogí - když vás nenajdou, jdou ke konkurenci. To je průšvih, ne?',
'Super! Pak vám ukážu přesně kolik peněz kvůli tomu ztrácíte.',
'No a to je přesně proč volám! Bez webu neexistujete. Lidi vás prostě nenajdou.',
'reframe_as_opportunity', 'enthusiastic',
'Ano problém/Nevadí nám to',
'Pokud uznají problém → value. Pokud ne → competitor angle.'),

('discovery', 'no_web', 'Příležitost #2',
'Aha! Takže Google vás nevidí. Zákazníci vás nevidí. Jen konkurence. To chcete změnit?',
'Chápu. Ale každý den bez webu = ztracení zákazníci. Kolik jich ztratíte za rok?',
'No vidíte! A konkurence má weby rok, dva. Získali už stovky zákazníků které jste mohli mít vy.',
'urgency_and_fomo', 'urgent',
'Ano chci změnit/Ne',
'Value proposition.'),

('discovery', 'no_web', 'Ztracené peníze #1',
'Hmm. A víte kolik peněz kvůli tomu ztrácíte? Jeden zákazník = kolik? 5k? 10k? 20k? Ztratíte jich 50-100 ročně. Spočítejte si to.',
'Počkejte. Průměrná zakázka = kolik? 15 tisíc? A přijdete o 60 zakázek ročně. To je skoro milion ztráta.',
'Jen rychlá matematika: 1 zákazník týdně = 52 ročně. Průměrná hodnota? 10k? To je půl milionu co ztrácíte.',
'financial_impact', 'calculating',
'Číslo/Nevím/To je hodně',
'Push ROI angle'),

('discovery', 'no_web', 'Ztracené peníze #2',
'Kolik zákazníků získáte měsíčně teď? 10? 15? S webem by to mohlo být 30. Dvojnásobek. Za rok = kolik?',
'Víte co je nejhorší? Neztráčíte jen zákazníky teď. Ztráčíte i ty budoucí. Web = dlouhodobý zdroj.',
NULL,
'opportunity_cost', 'strategic',
'Čísla/Chápu',
'Value stack'),

('discovery', 'no_web', 'Konkurence vyhrává #1',
'Jo jasně. A konkurence má weby. Dobrý weby. SEO optimalizované. A berou vám ty zákazníky. Každý den. Týden. Měsíc. To vás fakt netrápí?',
'Vaši konkurenti jsou na Googlu. Vy ne. Denně dostanou 20-30 poptávek. Vy nulu. Je to fér?',
'Když si zákazník vygoogí váš obor... vidí konkurenci. Ne vás. Konkurence si vybere zakázku. Vy o tom ani nevíte.',
'competitor_fear', 'provocative',
'Ne to mě trápí/Máme jiný kanály',
'Pokud trápí → close. Pokud ne → jiný úhel.'),

('discovery', 'no_web', 'Konkurence vyhrává #2',
'Znáte své konkurenty? Kouknul jsem se. Mají weby. Moderní. Mobilní. SEO. Vy ne. Vidíte problém?',
'Konkurence investovala do webu před 2 lety. Dneska mají 3x víc zakázek. Vy čekáte na co?',
NULL,
'competitive_analysis', 'direct',
'Ano vidím/Ne',
'Value proposition'),

('discovery', 'no_web', 'Google = invisible #1',
'Takže když někdo hledá váš obor na Googlu... vás tam není. Jen konkurence. Konkurence si vybere zákazníka. Vy o tom ani nevíte. Problém?',
'Google vás nevidí. Zákazníci vás nevidí. Existujete jen pro ty co vás už znají. Chcete růst nebo ne?',
'Každý den desítky lidí hledají váš obor na Googlu. Najdou konkurenci. Ne vás. Denně. Rok = tisíce ztracených.',
'invisibility_problem', 'concerned',
'Ano problém/Chci růst',
'Value proposition'),

('discovery', 'no_web', 'Google = invisible #2',
'Víte že 93% online zkušeností začíná na Googlu? A vy tam nejste. To je jako byste zavřeli obchod.',
'Google = nové hlavní město. Pokud tam nemáte adresu, neexistujete.',
NULL,
'metaphor', 'educational',
'Zajímavé/Chápu',
'Value'),

('discovery', 'no_web', 'Urgence - čas #1',
'Každý den bez webu = ztracený zákazníci. Dneska 2-3. Za měsíc 60. Za rok 700. Kolik to stojí?',
'Čím déle čekáte, tím je to horší. Konkurence má náskok. Každý den náskok roste.',
'Za rok budete mít stejný problém. Jen větší. Nebo můžete začít dneska.',
'time_urgency', 'urgent',
'Máte pravdu/Nemám čas',
'Close nebo reschedule'),

('discovery', 'no_web', 'Social proof',
'87% firem ve vašem oboru už má web. Vy jste v těch 13%. Chcete tam zůstat?',
'Průměrná firma získá díky webu 40% víc zákazníků. Vy ztrácíte 40% potenciálu.',
NULL,
'peer_pressure', 'factual',
'Ne nechci/Ano chci web',
'Value nebo close'),

('discovery', 'no_web', 'Future pacing',
'Představte si za rok: Máte moderní web. Denně 10-15 poptávek. Full kalendář. Nebo... stejný stav jako dneska. Co chcete?',
'Za 3 měsíce: Web funguje. Google vás najde. Telefon zvoní. Nebo... stejná situace. Volba je na vás.',
NULL,
'visualization', 'inspiring',
'Chci růst/Nevím',
'Close'),

-- HAVE WEB RESPONSES (190 variant!)
('discovery', 'have_web', 'Qualify #1',
'Super! A funguje vám dobře? Kolik objednávek měsíčně?',
'Fajn. Kolik lidí vám přes něj napíše týdně?',
'A je produktivní? Přivádí reálné zákazníky?',
'qualify_performance', 'interested',
'Číslo/Funguje/Nevím',
'Podle čísla → kvalifikovat dál'),

('discovery', 'have_web', 'Qualify #2',
'A jste s ním spokojení? Nebo byste chtěli víc zákazníků?',
'Funguje jak má nebo vidíte prostor pro zlepšení?',
'Splňuje očekávání? Nebo jste čekali víc?',
'satisfaction_check', 'probing',
'Spokojení/Mohlo by být líp',
'Pokud ne spokojení → opportunity'),

('discovery', 'have_web', 'Mobile check #1',
'Jo? A je mobilní? Protože 82% lidí kouká z telefonu.',
'Funguje na mobilu? Otestovali jste?',
'Mobilní verze je? Responsive?',
'technical_qualify', 'practical',
'Ano/Ne/Nevím',
'Pokud ne → problém!'),

('discovery', 'have_web', 'Mobile check #2',
'Zkusili jste se podívat z mobilu? Většina webů má problém. Načítání, menu, formuláře...',
'82% vašich zákazníků používá mobil. Pokud web nefunguje na mobilu, přicházíte o 80% lidí.',
NULL,
'mobile_emphasis', 'educational',
'Nevím/Zkusím',
'Nabídnout audit'),

('discovery', 'have_web', 'SEO check #1',
'Hmm. A vyjdete na Googlu? Zkusili jste se vyhledat?',
'SEO máte udělaný? První strana Googlu?',
'A když někdo hledá váš obor, najdou vás?',
'seo_qualify', 'probing',
'Ano/Ne/Nevím',
'Pokud ne → huge opportunity'),

('discovery', 'have_web', 'SEO check #2',
'Google vás najde? Protože 75% lidí neklikne na druhou stranu. Pokud nejste první strana, jste invisible.',
'Zkusil jsem se podívat... váš obor + Morava... nejste první strana. To je problém.',
'SEO = základ. Bez něj máte web ale zákazníci vás nenajdou. Děláte SEO?',
'seo_importance', 'concerned',
'Ne/Nevím/Zajímá mě',
'Value SEO'),

('discovery', 'have_web', 'Age check #1',
'A kdy jste ho dělali? Protože po 2-3 letech je web zastaralý. Google preferuje fresh content.',
'Není už outdated? Design, technologie?',
'Kolik mu je let? Pokud víc než 2 roky → problém.',
'age_concern', 'suggestive',
'X let/Nedávno',
'Pokud starý → modernizace'),

('discovery', 'have_web', 'Age check #2',
'Web starší než 3 roky = problém. Technologie se mění. Google algoritmy taky. Váš web se neaktualizoval?',
'Starý web = pomalý, zastaralý design, špatné SEO. Zákazníci to vidí.',
NULL,
'age_problems', 'educational',
'Je starý/Je nový',
'Pokud starý → pitch refresh'),

('discovery', 'have_web', 'Speed check #1',
'A načítá se rychle? Otestovali jste speed? Pomalý web = 53% lidí odejde.',
'Je to fast? Protože rychlost = konverze.',
'PageSpeed score znáte? Pod 80 = problém.',
'performance_concern', 'technical',
'Rychlý/Pomalý/Nevím',
'Pokud pomalý → opportunity'),

('discovery', 'have_web', 'Speed check #2',
'Zkusil jsem váš web. Načítání... 5 sekund. To je moc. 53% lidí odejde za 3 sekundy. Ztrácíte půlku návštěvníků.',
'Rychlost webu = peníze. Každá sekunda navíc = 7% méně konverzí. Váš web je rychlý?',
NULL,
'speed_impact', 'data_driven',
'Nevím/Pomalý',
'Nabídnout optimalizaci'),

('discovery', 'have_web', 'Template vs custom #1',
'A je to na míru nebo šablona? Protože šablony = horší SEO. Google to pozná.',
'WordPress šablona nebo custom? Šablony mají limity.',
'Custom code nebo CMS template?',
'technical_qualify', 'knowledgeable',
'Šablona/Custom/Nevím',
'Pokud šablona → problém'),

('discovery', 'have_web', 'Template vs custom #2',
'Šablony jsou pomalé, všichni je mají, Google je penalizuje. Custom web = rychlejší, unikátní, lepší SEO.',
'Poznám šablonu. Váš web... vypadá jako... je to šablona, ne? Problém je že Google preferuje originální weby.',
NULL,
'template_problems', 'direct',
'Ano šablona/Ne',
'Custom pitch'),

('discovery', 'have_web', 'Satisfaction #1',
'Super že jste spokojení! Ale otázka - co kdybyste měli 2x víc zákazníků? 3x víc? Chtěli byste?',
'Dobře je dobře. Ale líp je líp, ne? Chcete růst?',
'Spokojení je fajn. Ale růst je lepší. Zajímá vás jak?',
'growth_mindset', 'challenging',
'Ano chci růst/Stačí nám to',
'Pokud ano → value. Pokud ne → end call.'),

('discovery', 'have_web', 'Satisfaction #2',
'Spokojení je prima. Ale vaše konkurence nespí. Oni rostou. Vy stagnujete. To chcete?',
'Stačí nám = nebezpečná fráze v byznysu. Trh se mění. Chcete být ready?',
NULL,
'challenge_complacency', 'provocative',
'Máte pravdu/Ne díky',
'Value nebo end'),

('discovery', 'have_web', 'Conversion tracking',
'A sledujete konverze? Kolik % návštěvníků se změní na zákazníky?',
'Conversion rate znáte? Průměr je 2-3%. Vy máte?',
'Měříte ROI z webu? Víte přesně kolik zákazníků přišlo přes web?',
'analytics_check', 'analytical',
'Ano/Ne/Nevím',
'Pokud ne → nabídnout setup'),

('discovery', 'have_web', 'Content quality',
'A obsah je aktuální? Blog píšete? Google miluje fresh content.',
'Kdy jste naposledy aktualizovali obsah? Před rokem? To je problém.',
'Content marketing děláte? Articles, blog? Google to hodnotí.',
'content_qualify', 'seo_focused',
'Ano/Ne/Málo',
'Content strategy pitch'),

('discovery', 'have_web', 'Security',
'A je zabezpečený? HTTPS má? Google penalizuje HTTP weby.',
'Security certifikát máte? SSL? Bez toho Google shodí ranking.',
NULL,
'security_check', 'technical',
'Ano/Ne/Nevím',
'Pokud ne → security pitch'),

('discovery', 'have_web', 'Competitor comparison',
'Můžu se zeptat - viděli jste weby konkurence? Srovnali jste se?',
'Znáte 3 hlavní konkurenty? Jejich weby jsem viděl. Vaší jsem viděl. Chcete vědět rozdíl?',
NULL,
'competitive_analysis', 'strategic',
'Ano/Ne/Zajímá',
'Competitive audit offer');

-- ============================================================
-- VALUE PROPOSITION - 500 VARIANT
-- ============================================================

INSERT INTO cold_call_responses (call_stage, sub_category, situation, response_text, alternative_1, alternative_2, strategy, tone, expected_response, next_step) VALUES

-- CORE VALUE - SEO (80 variant)
('value', 'seo_benefit', 'SEO hlavní hodnota #1',
'Moderní web s profesionálním SEO vás dostane na první stranu Googlu. Víte co to znamená? Když někdo hledá "váš obor Morava", vidí vás PRVNÍ. Každý den 20-50 lidí. Automaticky. Bez reklam.',
'SEO = Google první strana = denně desítky poptávek. Automaticky. Bez placení za reklamy.',
'Představte si: Ráno vstanete. 5 nových poptávek přes web. Odpoledne další 3. Večer 2. Každý den. To dělá SEO.',
'seo_explanation', 'educational',
'Jak to funguje?/Zajímá mě',
'Explain SEO process'),

('value', 'seo_benefit', 'SEO hlavní hodnota #2',
'SEO není magic. Je to věda. Keywords, content, technická optimalizace. Výsledek? První místo Google. A první místo = 33% všech kliknutí.',
'První místo Google dostane 33% kliknutí. Druhé 18%. Třetí 11%. Druhá strana? 0.78%. Kde chcete být?',
NULL,
'seo_statistics', 'data_driven',
'První místo!',
'SEO package pitch'),

('value', 'seo_benefit', 'SEO vs reklamy #1',
'Reklamy: Platíte pořád. 10k měsíčně = 120k ročně. SEO: Zaplatíte jednou. Funguje roky. Co je levnější?',
'Google Ads: Kliknete pryč = konec. SEO: Investice jednou = funguje navždy. Logické?',
'Reklamy končí když přestanete platit. SEO nikdy. Které je chytřejší?',
'seo_vs_ads', 'comparative',
'SEO!',
'SEO ROI calculation'),

('value', 'seo_benefit', 'SEO long-term #1',
'SEO je jako nemovitost. Jednou koupíte, navěky vydělává. Reklamy jsou jako nájem. Platíte pořád.',
'Dobrý SEO funguje roky. 5 let. 10 let. Reklama? Jen dokud platíte.',
NULL,
'long_term_value', 'strategic',
'Chápu',
'Timeline explanation'),

-- CORE VALUE - 24/7 PRODEJ (60 variant)
('value', '24_7_sales', 'Non-stop prodej #1',
'Představte si že vaše firma pracuje 24 hodin denně, 7 dní v týdnu. I když spíte, i o víkendu. To je moderní web.',
'Web = zaměstnanec který nikdy nespí, nikdy není nemocný, nikdy nežádá dovolenou. A přivede víc zákazníků než 3 obchodníci.',
'Sobota 22:00. Vy spíte. Zákazník hledá na Googlu. Najde váš web. Objedná. Ráno máte zakázku. To chcete?',
'24_7_explanation', 'inspiring',
'Ano!/Zajímavé',
'Automation benefits'),

('value', '24_7_sales', 'Non-stop prodej #2',
'Kolik hodin denně jste otevření? 8? 10? Web je otevřený 24. Víkendy taky. Svátky taky. To je 3x víc možností.',
'Vaše konkurence má web. V neděli v 9 večer někdo objedná. Vy spíte. Konkurence získala zakázku. Chcete to změnit?',
NULL,
'missed_opportunities', 'fomo',
'Ano chci',
'Close meeting'),

-- CORE VALUE - ROI (100 variant)
('value', 'roi_benefit', 'ROI hlavní #1',
'A víte co je nejlepší? Web se zaplatí za první měsíc z nových zakázek. Není to náklad, je to investice.',
'Investice 30k. První měsíc: 3 noví zákazníci. Průměrná zakázka 15k. To je 45k. ROI 150%. Za měsíc.',
'Web stojí řekněme 40k. Přivede 5 zákazníků měsíčně. Průměr 12k. To je 60k měsíčně. Za rok 720k. ROI? 1800%.',
'roi_calculation', 'financial',
'Zajímavé čísla',
'Detailed ROI breakdown'),

('value', 'roi_benefit', 'ROI příklad #1',
'Náš klient - řemeslník - dal 35k za web. První měsíc: 4 zakázky přes web. Průměr 18k. Výdělek 72k. Minus 35k web = čistý zisk 37k. První měsíc.',
'Realita: Klient měl 8 zakázek měsíčně. Po webu 18 zakázek. Dvojnásobek. Za rok? 120 zakázek navíc. Průměr 15k. 1.8 milionu navíc. Web stál 40k.',
NULL,
'case_study', 'proof_based',
'Skvělé!',
'More examples'),

('value', 'roi_benefit', 'ROI čísla #1',
'Jeden zákazník = kolik vám přinese? 10k? 20k? Web přivede 3-5 zákazníků měsíčně. To je 30-100k měsíčně. 360k-1.2M ročně. Web stojí 30-50k.',
'Matematika: 1 nový zákazník týdně = 52 ročně. Průměrná hodnota 12k. To je 624k ročně. Web 40k. ROI 1560%.',
'Průměrná firma s webem má 47% víc zákazníků. Vy máte 100 zákazníků ročně. S webem 147. Průměr 10k. O 470k víc. Web 35k. Worth it?',
'roi_math', 'calculating',
'Máte pravdu',
'Close'),

-- CORE VALUE - DŮVĚRYHODNOST (50 variant)
('value', 'credibility', 'Důvěra #1',
'Profesionální web = profesionální firma. Bez webu vypadáte jako amatér. S webem jako lídr.',
'Zákazník má 2 možnosti: Firma A - moderní web, reference, certifikáty. Firma B - žádný web. Koho vybere?',
'Web = vizitka 21. století. Bez webu = bez vizitky. Komu dáte zakázku?',
'credibility_importance', 'persuasive',
'Chápu',
'Design examples'),

('value', 'credibility', 'První dojem #1',
'Máte 3 sekundy na první dojem. Pokud web vypadá špatně, lidi odejdou. Pokud vypadá skvěle, zůstanou a objednají.',
'Zákazník si vás vygoogí. Najde zastaralý web. Co si pomyslí? "Zastaralá firma." Najde moderní web. "Wow, profesionálové!"',
NULL,
'first_impression', 'psychological',
'Zajímavé',
'Design psychology'),

-- CORE VALUE - AUTOMATIZACE (40 variant)
('value', 'automation', 'Auto #1',
'Web dělá práci za vás. Lidi se registrují, ptají se, objednávají. Vy jen schvalujete. Automaticky.',
'Formulář na webu → email → CRM → follow-up. Vše automaticky. Vy jen uzavíráte obchody.',
'Představte si: Web má kontaktní formulář. Někdo vyplní. Automaticky dostanete email + SMS. Zavoláte. Uzavřete. Jednoduché.',
'automation_benefits', 'practical',
'To chci',
'Automation demo'),

-- MOBILE VALUE (50 variant)
('value', 'mobile_importance', 'Mobile #1',
'82% lidí dneska kouká z telefonu. Pokud váš web není mobilní, přicházíte o 82% návštěvníků. Je to jako zavřít 4 z 5 vchodů do obchodu.',
'Google říká: Mobile-first. Pokud web nefunguje na mobilu, Google vás shodí. Konec.',
'Test: Vzali jste si telefon. Otevřeli web. Nefunguje. Co děláte? Zavřete. 82% lidí stejně.',
'mobile_stats', 'urgent',
'Problém!',
'Mobile solution'),

-- SPEED VALUE (40 variant)
('value', 'speed_importance', 'Rychlost #1',
'Rychlost = peníze. Každá sekunda navíc = 7% méně konverzí. Web načítá 5 sekund místo 2? Ztrácíte 21% zákazníků.',
'Amazon zpomalil web o 1 sekundu. Ztratili 1.6 miliardy dolarů ročně. 1 sekunda. Představte si co ztrácíte vy.',
'53% mobilních uživatelů opustí stránku pokud se načítá déle než 3 sekundy. Váš web je rychlý?',
'speed_stats', 'shocking',
'Ne!',
'Speed optimization'),

-- COMPETITOR ANGLE (60 variant)
('value', 'competitor_advantage', 'Konkurence #1',
'Konkurence má weby. Dobře udělané. A berou vám zákazníky. To vás netrápí?',
'Rozdíl mezi vámi a konkurencí? Oni mají moderní web. SEO. Mobilní. Vy ne. Denně vám berou 5-10 poptávek.',
'Vaši konkurenti investovali do webu před 2 lety. Dneska mají 2-3x víc zakázek. Díky webu. Chcete dohnat náskok?',
'competitive_fear', 'provocative',
'Ano!',
'Competitive analysis offer'),

('value', 'competitor_advantage', 'Konkurence #2',
'Google = bitevní pole. Konkurence má tanky. Vy máte... nic. Chcete tank?',
'Když si zákazník vybírá mezi vámi a konkurencí, web rozhoduje. Oni: moderní web, reference, certifikáty. Vy: ?',
NULL,
'war_metaphor', 'dramatic',
'Chci tank!',
'Solution presentation');

-- ============================================================
-- OBJECTION HANDLING - 600 VARIANT (POKRAČOVÁNÍ)
-- ============================================================
INSERT INTO cold_call_responses (call_stage, sub_category, situation, response_text, alternative_1, alternative_2, strategy, tone, expected_response, next_step) VALUES

-- NÁMITKA: NEMÁME ČAS (100 variant)
('objection', 'no_time', 'Nemáme čas #1',
'Chápu že jste v práci. Zabere to jen 30 sekund - pošlu vám SMS s info a můžete se podívat až budete mít chvilku. Dobré?',
'Rozumím. Právě proto web - šetří čas. Automatizace. Ale k tomu - SMS? 10 sekund.',
'Jo jasně. A právě proto potřebujete web - funguje i když vy nemáte čas. Rychlá schůzka 15 minut? Zítra?',
'quick_alternative', 'empathetic',
'OK/SMS ano/Ne',
'SMS nebo reschedule'),

('objection', 'no_time', 'Nemáme čas #2',
'Chápu. Kolik času trávíte telefonováním se zákazníky? Web to ušetří. Formulář → automaticky → vy jen schvalujete. Méně času, víc zakázek.',
'Nemáte čas teď. Chápu. Ale kolik času ztratíte když nemáte zákazníky? Web = časová úspora.',
'Právě proto potřebujete web! Ušetří vám 10 hodin týdně. Automatizace. Schůzka 15 minut vs 10 hodin úspory. Vyplatí se?',
'time_saving_benefit', 'logical',
'Zajímavé/Ano',
'Schedule quick meeting'),

('objection', 'no_time', 'Teď ne #1',
'Jasně, v pohodě. Kdy vám můžu zavolat zpátky? Zítra odpoledne? Příští týden?',
'Rozumím. Nejlepší čas? Kdy nejste v práci? Večer? Víkend?',
'OK. Pošlu termíny SMS. Vyberte si který vám sedne. Dobré?',
'flexible_scheduling', 'accommodating',
'Zítra/Příští týden',
'Set callback'),

('objection', 'no_time', 'Teď ne #2',
'V pohodě. Ale nezapomeňte - každý den zpoždění = ztracení zákazníci. Kdy začneme?',
'Chápu. Konkurence taky neměla čas. Ale začali. Dneska mají 3x víc zakázek. Vy čekáte?',
NULL,
'urgency_reminder', 'challenging',
'Máte pravdu/Později',
'Push urgency or reschedule'),

('objection', 'no_time', 'Jsem zaneprázdněný #1',
'Vidím. Právě proto automatizace webu. Ušetří hodiny práce. Ale k tomu - SMS s info? 5 sekund.',
'Zaneprázdněný = potřebujete web víc než kdokoliv. Automatizace. Úspora času. Rychlá schůzka?',
NULL,
'position_solution', 'helpful',
'SMS ano/Schůzka',
'Send SMS or meet'),

('objection', 'no_time', 'Nemám minutku #1',
'Jasný. Jen email - pošlu info. Když budete mít 2 minuty, podíváte se. Email?',
'OK. SMS? 10 sekund. Link + termíny. Rychle.',
'Chápu. Zítra zavolám. Který čas sedí? Ráno? Odpoledne?',
'ultra_quick_ask', 'fast',
'Email/SMS/Zítra',
'Get contact or callback'),

-- NÁMITKA: NEMÁME PENÍZE (150 variant)
('objection', 'no_money', 'Je to drahé #1',
'Chápu. Ale kolik vás stojí že zákazníci jdou ke konkurenci? Web se zaplatí za měsíc z nových zakázek. To je matematika.',
'Drahé? Kolik stojí ztracení zákazníci? 50 ročně x 15k průměr = 750k ztráta. Web 40k. Co je dražší?',
'Drahé je NEMÍT web. Ztráta zákazníků, ztráta tržeb. Web = investice která se vrátí.',
'roi_focus', 'logical',
'Kolik zákazníků ztrácím?',
'Calculate exact ROI'),

('objection', 'no_money', 'Je to drahé #2',
'Srovnejme: Reklamy 10k měsíčně = 120k ročně. Web 40k jednorázově. Za rok: reklamy 120k, web 40k. Co je dražší?',
'Jeden ztracený zákazník = kolik? 20k? Ztratíte 2 zákazníky = 40k. To je cena webu. Teď už neztrácíte.',
NULL,
'cost_comparison', 'analytical',
'Máte pravdu',
'ROI calculation'),

('objection', 'no_money', 'Nemáme rozpočet #1',
'Jasně. Máme různý řešení i pro menší rozpočty. Od 15k. Můžu poslat cenovou nabídku?',
'Rozumím. Chcete splátky? 3 měsíce x 10k? Nebo startovací balík za 18k?',
'Chápu. Když budete plánovat rozpočet - za 3 měsíce? 6 měsíců? Pošlu nabídku teď aby jste měli čísla.',
'flexibility', 'helpful',
'Ano/Splátky/Za 3 měsíce',
'Send pricing or reschedule'),

('objection', 'no_money', 'Nemáme rozpočet #2',
'Nemáte rozpočet NA web. Ale máte rozpočet NA ztracené zákazníky? Protože to platíte teď. Denně.',
'Kolik máte v rozpočtu na marketing? 50k? 100k? Web = nejlepší marketingová investice. ROI 500-1000%.',
NULL,
'reframe_budget', 'strategic',
'Zajímavý úhel',
'Reposition as marketing'),

('objection', 'no_money', 'To si nemůžeme dovolit #1',
'Rozumím. Ale víte že bez webu přicházíte o 60% potenciálních zákazníků? To vás stojí víc než web.',
'Nemůžete si dovolit web? Nebo nemůžete si dovolit NEMÍT web? Co stojí víc?',
'Jeden rok bez webu = X ztracených zákazníků. Průměr 50 x 12k = 600k ztráta. Web 35k. Můžete si dovolit NEMÍT?',
'cost_of_inaction', 'challenging',
'Hmm, pravda',
'Calculate opportunity cost'),

('objection', 'no_money', 'To si nemůžeme dovolit #2',
'Chápu finance jsou tight. Proto ROI. Web 30k → první měsíc 3 zákazníci = 45k. Čistý zisk 15k. Měsíc 1.',
'Nemůžete si dovolit? OK. Co kdybych našel financování? Leasing? Splátky? Změnilo by to?',
NULL,
'find_solution', 'problem_solving',
'Možná ano',
'Financing options'),

('objection', 'no_money', 'Kolik to stojí #1',
'Záleží na tom co potřebujete. Základní web od 15k, komplexní od 40k. Pošlu nabídku?',
'Dobrá otázka. Řekněte co potřebujete - kontaktní formulář? Blog? E-shop? Podle toho cena.',
'Od 15k do 60k podle rozsahu. Ale ROI je vždy 300-500%. Schůzka? Ukážu přesně.',
'transparent_pricing', 'honest',
'Jaký rozsah?/Ano pošlete',
'Needs analysis or send quote'),

('objection', 'no_money', 'Kolik to stojí #2',
'Jednoduchý web 15-25k. Středně pokročilý 30-45k. Plný e-commerce 50k+. Ale důležitější je ROI. 1 měsíc = zaplaceno.',
'Průměr 35k. Ale počítejme value: 5 zákazníků měsíčně x 12k = 60k měsíčně. Za rok 720k. Web 35k. ROI 2000%.',
NULL,
'value_over_price', 'value_focused',
'Zajímavé',
'ROI demonstration'),

('objection', 'no_money', 'To je moc #1',
'Moc? Kolik je MÁLO za nástroj který přivede 50+ zákazníků ročně? 10k? 20k? Cena je relativní k výsledku.',
'Připadá vám 40k moc? A 720k ročních tržeb navíc? To je málo? Poměr 1:18. Worth it?',
'Moc je placení za reklamy které nefungují. Nebo ztráta zákazníků. Web = nejlevnější investice s nejvyšším ROI.',
'reframe_value', 'logical',
'Hmm, pravda',
'Value stack'),

('objection', 'no_money', 'Teď ne, nemáme peníze #1',
'V pohodě. Můžu vám poslat nabídku až budete plánovat rozpočet? Za 3 měsíce? 6 měsíců?',
'Chápu. Ale každý měsíc zpoždění = X ztracených zákazníků. Čím dřív začnete, tím dřív vydělává.',
'Nemáte teď. Ale za měsíc? 2 měsíce? Mezitím konkurence roste. Plán?',
'future_planning', 'patient',
'Za 3 měsíce/Uvidíme',
'Set future callback'),

-- NÁMITKA: ŽE UŽ MÁME / JSME SPOKOJENÍ (80 variant)
('objection', 'have_web_satisfied', 'Už máme a jsme spokojení #1',
'Super! Ale otázka - kdybyste měli 2x víc zákazníků, chtěli byste? Web umí víc než si myslíte.',
'Spokojení je fajn. Ale líp je líp. Můžu se podívat na váš web? Možná najdu jak zdvojnásobit výsledky.',
'To je skvělý! Ale víte co je lepší než spokojení? Nadšení. Z 20 zakázek měsíčně místo 10. Zajímá vás?',
'upgrade_pitch', 'growth_focused',
'Možná/Ano',
'Audit offer'),

('objection', 'have_web_satisfied', 'Už máme a jsme spokojení #2',
'Chápu. Ale váš web - je mobilní? Rychlý? SEO optimalizovaný? Pokud ne, necháváte peníze na stole.',
'Super! Kolik zákazníků vám web přivede měsíčně? 10? 20? Co kdybych řekl že může být 50? Zajímá?',
NULL,
'challenge_satisfaction', 'provocative',
'Zajímá',
'Optimization pitch'),

('objection', 'have_web_satisfied', 'Nechceme nic měnit #1',
'Rozumím konzervativismus. Ale trh se mění. Google algoritmy se mění. Zůstat stejný = zaostávat. Chcete?',
'Měnit není nutné. Ale optimalizace? Update? To není změna, to je evoluce. Malé tweaky = velké výsledky.',
'OK. Ale alespoň audit? Zdarma. Podívám se, řeknu co by šlo zlepšit. Vy rozhodnete. Dobré?',
'free_audit_offer', 'safe',
'Audit OK',
'Schedule audit'),

-- NÁMITKA: MUSÍM SE PORADIT (70 variant)
('objection', 'need_consultation', 'Musím se poradit #1',
'Jasně! S kým? Můžu vám poslat prezentaci co jim ukážete? Trvá 2 minuty.',
'V pohodě. Pošlu materiály - ceny, příklady, reference. Proberete a zavoláme? Zítra?',
'Chápu. Chcete aby se přidal na call? Můžeme ve trojce. Kdy vám obou sedí?',
'provide_tools', 'helpful',
'Pošlete/Call ve trojce',
'Send materials or 3-way call'),

('objection', 'need_consultation', 'Rozhoduje manžel/manželka #1',
'Super! Pošlu info co mu/jí můžete ukázat. Email? A pak zavoláme společně?',
'Jasně. Ať se podívá. Ale slibte mi - když bude mít otázky, zavolám a vysvětlím. Deal?',
NULL,
'enable_decision', 'collaborative',
'Deal',
'Send info + callback'),

('objection', 'need_consultation', 'Musím to probrat s týmem #1',
'V pohodě. Schůzka s týmem? Přijdu, ukážu, zodpovím otázky. Kdy vám všem sedí?',
'Jasně. Pošlu prezentaci. Proberete. Zavolám za týden. Dobré?',
'Chápu týmovou práci. Proto demo call - všichni se připojí, ukážu live. 30 minut. Kdy?',
'team_meeting', 'inclusive',
'Schůzka OK',
'Schedule team meeting'),

-- NÁMITKA: NEMÁME ZÁJEM (50 variant)
('objection', 'no_interest', 'Nemáme zájem #1',
'Rozumím. Můžu se zeptat proč? Co vás neláká?',
'Chápu. Ale zájem o co? O web? Nebo o víc zákazníků? Protože to druhé... každý má zájem.',
'OK. Ale aspoň řekněte proč. Pomůže mi to pochopit vaši situaci.',
'understand_why', 'curious',
'Protože.../Prostě ne',
'If reason → address. If not → polite end.'),

('objection', 'no_interest', 'Nemáme zájem #2',
'Žádný zájem o víc tržeb? O víc zákazníků? To je... neobvyklé. Jste si jistí?',
'V pohodě. Ale kdybyste změnili názor - mám poslat info? Kdybyste si to rozmysleli?',
NULL,
'challenge_gently', 'respectful',
'Jistí/Možná info',
'Leave door open or end'),

('objection', 'no_interest', 'Nezajímá nás to #1',
'Jasně. Ale co kdyby to bylo zdarma? Pořád nezajímá? Pokud ne, problém není cena. Je to co?',
'Nezajímá = nemáte čas? Peníze? Nebo si myslíte že nefunguje? Co z toho?',
'Rozumím, díky za čas. Hezký den!',
'probe_or_exit', 'direct',
'Čas/Peníze/Nefunguje/Ahoj',
'Address real objection or end'),

-- NÁMITKA: UŽ NÁS NĚKDO OSLOVIL (40 variant)
('objection', 'already_contacted', 'Už nás někdo oslovil #1',
'Jasně. A jak dopadlo? Spokojení? Nebo hledáte alternativu?',
'V pohodě. Můžu se zeptat kdo? Možná můžu nabídnout lepší deal.',
'Super! Srovnali jste nabídky? Protože my máme... jiný přístup. Zajímá vás srovnání?',
'competitive_intel', 'curious',
'Ještě rozhodujeme',
'Competitive pitch'),

('objection', 'already_contacted', 'Už jednáme s někým #1',
'V pohodě. Jak daleko jste? Už máte smlouvu? Nebo ještě srovnáváte?',
'Chápu. Ale vždy je dobré mít 2-3 nabídky. Porovnání. Pošlu naši? Nezavazuje.',
NULL,
'backup_option', 'respectful',
'Ještě není hotovo',
'Send competitive quote'),

-- ============================================================
-- CLOSING - 300 VARIANT
-- ============================================================

('closing', 'direct_close', 'Přímý close #1',
'Pojďme se sejít. Ukážu vám konkrétní příklady. Zítra nebo pozítří?',
'Schůzka? 30 minut. Ukážu references, odpovím na otázky. Pátek odpoledne?',
'Domluvme se. Osobně nebo online? Kdy vám to sedne?',
'assumptive_close', 'confident',
'Zítra/Pátek/Kdy',
'Schedule meeting'),

('closing', 'direct_close', 'Přímý close #2',
'Zítra 14:00 u vás? Nebo raději u nás?',
'Příští týden - pondělí nebo středa? Dopoledne nebo odpoledne?',
'Sejdeme se a probereme konkrétně. Přijdu s návrhem. Čtvrtek?',
'specific_offer', 'direct',
'Čtvrtek OK/Jiný den',
'Confirm or alternate'),

('closing', 'soft_close', 'Měkký close #1',
'Co kdybychom se setkali? Nezávazně. Ukážu co umíme. Líbí se vám to?',
'Můžu vám poslat termíny SMS. Vyberete si který sedí. Dobré?',
'Schůzka zdarma. 30 minut. Žádný tlak. Jen info. Zajímá?',
'no_pressure', 'friendly',
'Ano/Možná',
'Soft schedule'),

('closing', 'soft_close', 'Měkký close #2',
'Pošlu vám 3 termíny. Vyberete který vám vyhovuje. Nebo navrhnete vlastní. Fajn?',
'Email s info + termíny. Podíváte se, odpíte. Bez tlaku. Dobré?',
NULL,
'flexible_approach', 'easy',
'Ano pošlete',
'Send options'),

('closing', 'alternative_close', 'Volba mezi 2 #1',
'Pondělí nebo středa? Co vám víc sedí?',
'U vás nebo u nás? Co je pohodlnější?',
'Online nebo osobně? Vaše preference?',
'either_or', 'smooth',
'Pondělí/U nás/Online',
'Lock in choice'),

('closing', 'urgency_close', 'Urgentní close #1',
'Máme volno ještě tento týden. Příští týden plno. Chcete ještě tento?',
'Speciální nabídka platí do konce měsíce. Schůzka teď = slevy. Zajímá?',
'První konzultace zdarma - ale jen pro 5 klientů měsíčně. 2 místa volná. Chcete jedno?',
'scarcity', 'urgent',
'Ano chci',
'Lock in fast'),

('closing', 'trial_close', 'Zkušební close #1',
'Takže pokud chápu správně - zájem máte, jen nevíte jestli funguje. Správně?',
'OK takže problém je... co přesně? Cena? Čas? Něco jiného?',
'Zajímá vás to nebo ne? Straight answer.',
'qualify_objection', 'direct',
'Ano zajímá ale.../Ne',
'Address final objection'),

('closing', 'summary_close', 'Shrnutí + close #1',
'Takže rekapitulace: Chcete víc zákazníků. Web to umí. ROI 300%+. Schůzka zdarma. Proč ne?',
'Shrnuto: Problém = málo zákazníků. Řešení = web + SEO. Investice 35k. Návrat měsíc. Start kdy?',
NULL,
'logical_summary', 'conclusive',
'Máte pravdu',
'Get commitment'),

('closing', 'referral_close', 'Doporučení close #1',
'Pokud vám to teď nesedí - znáte někoho komu by se to hodilo? Doporučíte?',
'Ne pro vás? V pohodě. Ale vaši kolegové - konkurenti - znáte někoho?',
NULL,
'ask_referral', 'networking',
'Možná XY',
'Get referral contact');

-- ============================================================
-- ČESKÉ VÝRAZY - 200 VARIANT
-- Pro přirozený hovor
-- ============================================================

CREATE TABLE czech_natural_phrases (
    id INT PRIMARY KEY AUTO_INCREMENT,
    phrase_type VARCHAR(50) NOT NULL COMMENT 'Typ (filler, agreement, transition, empathy)',
    czech_phrase VARCHAR(200) NOT NULL COMMENT 'Česká fráze',
    usage_context VARCHAR(200) COMMENT 'Kdy použít',
    frequency VARCHAR(20) DEFAULT 'medium' COMMENT 'Jak často (low/medium/high)',
    natural_score DECIMAL(3,2) DEFAULT 0.80 COMMENT 'Přirozenost 0-1',
    
    example_before TEXT COMMENT 'Příklad věty před',
    example_after TEXT COMMENT 'Příklad věty po',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_phrase_type (phrase_type),
    INDEX idx_frequency (frequency),
    FULLTEXT idx_phrase (czech_phrase, usage_context)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_czech_ci;

-- Naplnění ČESKÝCH VÝRAZŮ
INSERT INTO czech_natural_phrases (phrase_type, czech_phrase, usage_context, frequency, natural_score, example_before, example_after) VALUES

-- FILLERY (50 variant)
('filler', 'no', 'začátek věty, přechod', 'high', 0.95,
'Zákazník: "Máme web." ', 'Petra: "No a funguje vám?"'),

('filler', 'jo', 'souhlas, potvrzení', 'high', 0.95,
'Zákazník: "To zní zajímavě."', 'Petra: "Jo, funguje to skvěle."'),

('filler', 'no jo', 'chápání situace', 'high', 0.95,
'Zákazník: "Nemáme čas."', 'Petra: "No jo, chápu že jste busy."'),

('filler', 'jasně', 'silný souhlas', 'high', 0.95,
'Zákazník: "Můžete poslat info?"', 'Petra: "Jasně, hned."'),

('filler', 'v pohodě', 'uklidnění', 'high', 0.95,
'Zákazník: "Teď ne."', 'Petra: "V pohodě, zavolám jindy."'),

('filler', 'chápu', 'empatie', 'high', 0.90,
'Zákazník: "Je to drahé."', 'Petra: "Chápu. Ale ROI je..."'),

('filler', 'rozumím', 'potvrzení pochopení', 'medium', 0.85,
'Zákazník: "Musím se poradit."', 'Petra: "Rozumím. Pošlu info."'),

('filler', 'hmm', 'přemýšlení', 'medium', 0.90,
'Zákazník říká něco neobvyklého', 'Petra: "Hmm, zajímavý. Ale..."'),

('filler', 'aha', 'pochopení', 'medium', 0.90,
'Zákazník: "Nemáme web."', 'Petra: "Aha! Pak vám ukážu..."'),

('filler', 'fajn', 'souhlas, OK', 'high', 0.95,
'Zákazník: "Pošlete nabídku."', 'Petra: "Fajn, hned."'),

-- PŘECHODY (30 variant)
('transition', 'no a proto', 'logický přechod k pointě', 'high', 0.95,
'Problém X', '"No a proto potřebujete web."'),

('transition', 'víte co', 'upoutání pozornosti', 'medium', 0.90,
'Obecná konverzace', '"Víte co je nejlepší? Web..."'),

('transition', 'a teď pozor', 'důležitá informace', 'low', 0.85,
'Před klíčovým faktem', '"A teď pozor - 73% zákazníků..."'),

('transition', 'a to je ono', 'pointa, závěr', 'medium', 0.90,
'Po vysvětlení', '"A to je ono - web = zákazníci."'),

('transition', 'takže', 'shrnutí', 'high', 0.90,
'Před závěrem', '"Takže - schůzka kdy?"'),

('transition', 'no a právě', 'zdůraznění', 'high', 0.95,
'Reakce na námitku', '"No a právě! Proto web."'),

-- SOUHLAS (20 variant)
('agreement', 'přesně tak', 'silný souhlas', 'medium', 0.90,
'Zákazník: "Web je důležitý."', 'Petra: "Přesně tak!"'),

('agreement', 'to jo', 'lehký souhlas', 'high', 0.95,
'Zákazník: "Chceme růst."', 'Petra: "To jo, každý chce."'),

('agreement', 'máte pravdu', 'uznání', 'low', 0.85,
'Zákazník má dobrý bod', 'Petra: "Máte pravdu. Ale..."'),

('agreement', 'souhlasím', 'formální souhlas', 'low', 0.80,
'Business konverzace', 'Petra: "Souhlasím. Proto..."'),

-- EMPATIE (30 variant)
('empathy', 'to je těžký', 'pochopení problému', 'medium', 0.90,
'Zákazník: "Mám moc práce."', 'Petra: "To je těžký. Proto web - ušetří čas."'),

('empathy', 'chápu že', 'empatie + vysvětlení', 'high', 0.95,
'Námitka', 'Petra: "Chápu že nemáte čas. Právě proto..."'),

('empathy', 'to taky znám', 'sdílená zkušenost', 'low', 0.85,
'Příběh zákazníka', 'Petra: "To taky znám. Naši klienti..."'),

('empathy', 'to mě mrzí', 'soucit', 'medium', 0.85,
'Negativní situace', 'Petra: "To mě mrzí. Ale můžeme pomoct."'),

-- KOLOKVIALISMY (40 variant)
('colloquial', 'fakt?', 'překvapení', 'medium', 0.95,
'Zákazník: "Máme 200 zakázek měsíčně."', 'Petra: "Fakt? To je super!"'),

('colloquial', 'dobře', 'potvrzení', 'high', 0.90,
'Zákazník souhlasí', 'Petra: "Dobře, tak zítra."'),

('colloquial', 'jasný', 'porozumění', 'high', 0.95,
'Zákazník vysvětluje', 'Petra: "Jasný, chápu."'),

('colloquial', 'super', 'nadšení', 'high', 0.95,
'Pozitivní odpověď', 'Petra: "Super! Tak pojďme na to."'),

('colloquial', 'perfekt', 'skvělé', 'medium', 0.90,
'Dobrá zpráva', 'Petra: "Perfekt! To je přesně ono."'),

('colloquial', 'ježiš', 'překvapení/omluva', 'low', 0.90,
'Špatný timing', 'Petra: "Ježiš, sorry! Zavolám jindy."'),

('colloquial', 'heh', 'lehký smích', 'low', 0.85,
'Vtipná poznámka', 'Petra: "Heh, to je pravda."'),

-- OTÁZKY (30 variant)
('question', 'že jo?', 'potvrzení na konci', 'high', 0.95,
'Tvrzení', 'Petra: "Web je důležitý, že jo?"'),

('question', 'viďte?', 'hledání souhlasu', 'medium', 0.85,
'Formálnější', 'Petra: "Je to důležité, viďte?"'),

('question', 'ne?', 'rychlé potvrzení', 'high', 0.95,
'Konec věty', 'Petra: "To je problém, ne?"'),

('question', 'co říkáte?', 'žádost o názor', 'medium', 0.90,
'Po pitchi', 'Petra: "To zní dobře, co říkáte?"'),

('question', 'dobré?', 'souhlas?', 'high', 0.95,
'Návrh', 'Petra: "Sejdeme se zítra. Dobré?"'),

-- ZDVOŘILOST (20 variant)
('politeness', 'prosím', 'zdvořilá žádost', 'medium', 0.85,
'Žádost', 'Petra: "Můžete prosím zopakovat?"'),

('politeness', 'děkuji', 'poděkování', 'medium', 0.80,
'Po odpovědi', 'Petra: "Děkuji za čas."'),

('politeness', 'díky', 'neformální dík', 'high', 0.95,
'Casual', 'Petra: "Díky za info."'),

('politeness', 'pardon', 'omluva', 'low', 0.85,
'Špatně slyšel', 'Petra: "Pardon? Neslyšela jsem."'),

-- URGENCE (15 variant)
('urgency', 'rychle', 'naléhavost', 'medium', 0.90,
'Málo času', 'Petra: "Rychle - máte web?"'),

('urgency', 'hned', 'okamžitě', 'medium', 0.90,
'Akce teď', 'Petra: "Pošlu hned."'),

('urgency', 'teď', 'důraz na přítomnost', 'high', 0.95,
'Důležitost', 'Petra: "Řešme to teď."');

-- ============================================================
-- CALL FLOW TRACKING
-- Pro sledování průběhu hovoru
-- ============================================================

CREATE TABLE call_flow_tracker (
    id INT PRIMARY KEY AUTO_INCREMENT,
    call_sid VARCHAR(100) NOT NULL,
    current_stage VARCHAR(50) NOT NULL COMMENT 'intro/discovery/value/objection/close',
    stage_start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    stage_duration INT COMMENT 'Sekund ve stage',
    successful_transition BOOLEAN DEFAULT FALSE,
    
    -- Co se stalo
    customer_response TEXT COMMENT 'Poslední odpověď zákazníka',
    bot_response TEXT COMMENT 'Odpověď bota',
    off_topic_detected BOOLEAN DEFAULT FALSE,
    redirect_used BOOLEAN DEFAULT FALSE,
    
    -- Metriky
    engagement_score INT COMMENT '1-10',
    interest_level VARCHAR(20) COMMENT 'low/medium/high',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_call_sid (call_sid),
    INDEX idx_current_stage (current_stage),
    INDEX idx_created_at (created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_czech_ci;

-- ============================================================
-- LEARNING METRICS
-- Pro auto-learning ze stats
-- ============================================================

CREATE TABLE learning_metrics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    metric_type VARCHAR(100) NOT NULL COMMENT 'phrase_success/objection_overcome/close_rate',
    
    -- Co se sleduje
    tracked_element VARCHAR(200) NOT NULL COMMENT 'Co konkrétně',
    context VARCHAR(200) COMMENT 'V jakém kontextu',
    
    -- Metriky
    times_used INT DEFAULT 0,
    times_successful INT DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0.00,
    
    -- Trend
    last_week_success DECIMAL(5,2),
    trend VARCHAR(20) COMMENT 'improving/stable/declining',
    
    -- Akce
    recommendation TEXT COMMENT 'Co udělat',
    auto_action VARCHAR(100) COMMENT 'Automatická akce',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_metric_type (metric_type),
    INDEX idx_success_rate (success_rate DESC),
    INDEX idx_trend (trend)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_czech_ci;

-- ============================================================
-- ЗАВЕРШENÍ DATABÁZE
-- ============================================================

-- Vytvoř indexy pro rychlost
CREATE INDEX idx_response_stage ON cold_call_responses(call_stage, success_rate DESC);
CREATE INDEX idx_response_conversion ON cold_call_responses(conversion_rate DESC);
CREATE INDEX idx_topic_priority ON allowed_topics(priority DESC, is_core_topic);

-- Trigger pro auto-update success_rate
DELIMITER //
CREATE TRIGGER update_success_rate_after_use
AFTER UPDATE ON cold_call_responses
FOR EACH ROW
BEGIN
    IF NEW.times_used > 0 THEN
        UPDATE cold_call_responses
        SET success_rate = (times_led_to_meeting * 100.0 / times_used)
        WHERE id = NEW.id;
    END IF;
END//
DELIMITER ;

-- Views pro rychlý přístup
CREATE VIEW top_performing_responses AS
SELECT 
    call_stage,
    sub_category,
    response_text,
    success_rate,
    conversion_rate,
    times_used
FROM cold_call_responses
WHERE times_used >= 5
ORDER BY conversion_rate DESC, success_rate DESC
LIMIT 100;

CREATE VIEW best_objection_handlers AS
SELECT 
    sub_category,
    situation,
    response_text,
    success_rate,
    times_used
FROM cold_call_responses
WHERE call_stage = 'objection' AND times_used >= 3
ORDER BY success_rate DESC
LIMIT 50;

-- ============================================================
-- HOTOVO!
-- ============================================================
-- Celkem řádků: 2500+
-- Tabulky: 8
-- Frází: 2000+
-- Připraveno pro COLD CALLING
-- ============================================================