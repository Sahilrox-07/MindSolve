from rapidfuzz import fuzz


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


def is_fuzzy_greeting(text):

    text = text.lower().strip()

    for greeting in COMMON_GREETINGS:

        if fuzz.ratio(text, greeting) >= 85:
            return True

    return False

def extract_name_from_introduction(text):

    words = text.lower().strip().split()

    # "my name is <name>"
    for i in range(len(words) - 3):

        phrase = " ".join(words[i:i + 3])

        if fuzz.ratio(phrase, "my name is") >= 75:

            name = words[i + 3]

            if name.isalpha():
                return name.capitalize()


    # "i am <name>"
    for i in range(len(words) - 2):

        phrase = " ".join(words[i:i + 2])

        if fuzz.ratio(phrase, "i am") >= 75:

            name = words[i + 2]

            if name.isalpha():
                return name.capitalize()


    # "i'm <name>"
    for i in range(len(words) - 1):

        if words[i] == "i'm":

            name = words[i + 1]

            if name.isalpha():
                return name.capitalize()


    return None

def get_conversation_response(text):

    text = text.strip().lower()

    # Greetings
    if is_fuzzy_greeting(text):

        return "Hi! Welcome to MindSolve. How can I help you today?"

    # Thank you
    if text in THANK_YOU_MESSAGES:

        return "You're welcome! I'm here if you need help with anything else."

    # How are you
    if text in {"how are you", "how are you doing"}:

        return "I'm ready to help. What would you like to work on?"

        # Self introduction

    name = extract_name_from_introduction(text)

    if name:

        greeting_found = False

        for greeting in COMMON_GREETINGS:

            if greeting in text:

                greeting_found = True
                break

        if greeting_found:

            return (
                f"Hi {name}! Welcome to MindSolve. "
                "How can I help you today?"
            )

        return (
            f"Nice to meet you, {name}! "
            "What would you like help with?"
        )