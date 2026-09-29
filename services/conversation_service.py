import re


COMMON_GREETINGS = {
    "hi",
    "hello",
    "hey",
    "hii",
    "hiii",
    "good morning",
    "good afternoon",
    "good evening"
}


THANK_YOU_MESSAGES = {
    "thanks",
    "thank you",
    "thanks a lot",
    "thank you so much"
}


def get_conversation_response(text):

    text = text.strip().lower()

    # Greetings
    if text in COMMON_GREETINGS:
        return "Hi! Welcome to MindSolve. How can I help you today?"

    # Thank you
    if text in THANK_YOU_MESSAGES:
        return "You're welcome! I'm here if you need help with anything else."

    # How are you
    if text in {"how are you", "how are you doing"}:
        return "I'm ready to help. What would you like to work on?"

    # Self introduction
    name_match = re.match(
        r"^(my name is|i am|i'm)\s+([a-zA-Z]+)$",
        text
    )

    if name_match:
        name = name_match.group(2).capitalize()
        return f"Nice to meet you, {name}! What would you like help with?"

    return None