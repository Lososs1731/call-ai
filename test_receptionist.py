"""
Test AI Receptionist s databází
"""

from services.receptionist import AIReceptionist

print("🧪 Testuju AI Receptionist...\n")

petra = AIReceptionist()

print("\n" + "="*60)
print("TEST CONVERSATION")
print("="*60 + "\n")

# Test 1: Greeting
greeting = petra.get_greeting()
print(f"Petra: {greeting}\n")

# Test 2: Discovery
response = petra.generate_response("Ne, nemáme web.", "test_call_001")
print(f"Petra: {response}\n")

# Test 3: Objection
response = petra.generate_response("To je asi drahé ne?", "test_call_001")
print(f"Petra: {response}\n")

# Test 4: Closing
response = petra.generate_response("Jo zajímá mě to. Kdy se můžeme sejít?", "test_call_001")
print(f"Petra: {response}\n")

# Test 5: OFF-TOPIC
response = petra.generate_response("Dneska hezky prší ne?", "test_call_001")
print(f"Petra: {response}\n")

# Summary
summary = petra.end_call_summary()
print("\n" + "="*60)
print("CALL SUMMARY")
print("="*60)
for key, value in summary.items():
    print(f"{key}: {value}")