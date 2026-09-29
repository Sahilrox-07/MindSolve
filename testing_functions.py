from services.text_service import translate_to_english

tests = [
    "padhai me man nahi lagta",
    "mujhe padhai me focus nahi lagta",
    "mera phone bahut distract karta hai",
]

for text in tests:
    print(f"Original: {text}")
    print("English:", translate_to_english(text))