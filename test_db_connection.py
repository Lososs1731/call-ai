"""
Test SQLite připojení a knowledge base
"""

from database.sqlite_connector import get_knowledge_base

print("🧪 Testuju SQLite knowledge base...\n")

kb = get_knowledge_base()

print("\n1️⃣ Test: Získej intro responses")
intros = kb.get_best_response('intro', limit=3)
for i, resp in enumerate(intros, 1):
    print(f"   {i}. [{resp['sub_category']}] {resp['response_text'][:60]}...")

print("\n2️⃣ Test: Získej objection responses")
objections = kb.get_best_response('objection', sub_category='no_money', limit=2)
for i, resp in enumerate(objections, 1):
    print(f"   {i}. {resp['response_text'][:80]}...")

print("\n3️⃣ Test: České fráze")
fillers = kb.get_czech_phrases('filler', 'high')
print(f"   Fillers: {', '.join([p['czech_phrase'] for p in fillers[:10]])}")

print("\n4️⃣ Test: OFF-TOPIC detection")
test_texts = [
    "Máte webové stránky?",
    "Včera pršelo.",
    "Kolik to stojí?",
    "Viděl jste fotbal?"
]
for text in test_texts:
    is_on, topic = kb.is_on_topic(text)
    print(f"   '{text}' → {'✅ ON-TOPIC' if is_on else '❌ OFF-TOPIC'} ({topic})")

print("\n5️⃣ Test: Redirect")
redirect = kb.get_redirect('weather')
print(f"   Weather redirect: {redirect['redirect_direct']}")

print("\n6️⃣ Test: Stage stats")
stats = kb.get_stage_stats()
for stage, count in stats.items():
    print(f"   {stage}: {count} responses")

print("\n✅ Všechny testy OK! Knowledge base funguje.")