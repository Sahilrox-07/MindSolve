from rapidfuzz import fuzz
from langdetect import detect
from deep_translator import GoogleTranslator
import re
import logging

def clean_text(text):
    return text.lower().strip()


def is_valid_problem(text):
    return (
        text
        and 5 <= len(text) <= 200
        and len(set(text)) > 2
        and any(c.isalpha() for c in text)
    )

# =========================
# 🌐 LANGUAGE CONTROL
# =========================
def detect_language(text):
    try:
        if is_hinglish(text):
            return "hi"

        detected = detect(text)
        return detected if detected in ["en", "hi"] else "en"

    except Exception as e:
        logging.error(f"Language detection failed: {e}")
        return "en"


def translate_to_english(text):
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except Exception as e:
        logging.error(f"Translation failed: {e}")
        return text

# =========================
# 🧠 HINGLISH DETECTION
# =========================
def is_hinglish(text):
    hinglish_words = {
        "hai","nahi","kyu","kaise","bekar","acha","kharab",
        "jarurat","mujhe","tum","ye","wo","kya","kar",
        "raha","rahi","mai","hum","aap","samajh",
        "bhai","sahi","kaam"
    }

    words = text.lower().split()
    score = sum(1 for w in words if w in hinglish_words)
    return score >= 2  # FIXED


# =========================
# 🚫 ABUSE FILTER
# =========================
BAD_WORDS = [
    "madarchod","behenchod","bhosdike","chutiya","gandu",
    "loda","randi","harami","kaminey","mc","bc","bkl","bsdk"
]

def is_clean(text):
    text = text.lower()
    text = text.replace("1","i").replace("5","s").replace("0","o")
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    for bad in BAD_WORDS:
        if bad in text:
            return False

    words = re.findall(r'[a-zA-Z]+', text)

    for w in words:
        for bad in BAD_WORDS:
            if fuzz.ratio(w, bad) > 85:
                return False

    return True


# =========================
# 😐 SENTIMENT
# =========================
def is_negative_sentiment(text):
    
    negative_words = {
        "sucks", "bad", "terrible", "awful", "worst", "hate",
        "useless", "frustrating", "disappointing", "annoying"
    }

    text = text.lower()

    return any(word in text for word in negative_words)

