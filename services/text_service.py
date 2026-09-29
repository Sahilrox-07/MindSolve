from rapidfuzz import fuzz
from langdetect import detect
from deep_translator import GoogleTranslator
import re
import logging
import time

def clean_text(text):
    return text.lower().strip()

def is_valid_problem(text):

    if not text:
        return False

    text = text.strip()

    if len(text) < 5 or len(text) > 200:
        return False

    if len(set(text.replace(" ", ""))) <= 2:
        return False

    if not any(char.isalpha() for char in text):
        return False

    return True

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


_translation_cache = {}

def translate_to_english(text):

    if not text:
        return text

    text = text.strip()

    # Return cached translation if we have already translated this text
    if text in _translation_cache:
        return _translation_cache[text]

    try:

        time.sleep(0.25)

        translated = GoogleTranslator(
            source="auto", target="en"
        ).translate(text)

        if translated:
            _translation_cache[text] = translated
            return translated
        
        return text

    except Exception as e:

        logging.error(f"Translation failed: {e}")
        
        return text
    
# =========================
# 🧠 HINGLISH DETECTION
# =========================
def is_hinglish(text):
    hinglish_words = {

    "hai","nahi","kyu","kaise",
    "mujhe","mera","meri","mere",
    "tum","aap","hum","mai",
    "main","padhai","college",
    "dhyan","samajh","problem",
    "pareshan","thak","thaka","thaki",
    "soch","sochna","dimag",
    "paisa","padh","padhta",
    "samasya","madad","karna",
    "kar","raha","rahi",
    "ho","gaya","gayi",
    "nhi","nahin","acha",
    "kharab","bhai","yaar",
    "padhai","padhayi","adhyan",
    "samjh","samajh","samajhna",
    "dhyaan","dhyan","nikal",
    "nikalna","fas","fasa",
    "paisa","likhne","samasya",
    "kamai","naukri","padhti",
    "rozgar","man","mann",
    "dost","ghar","parivaar",
    "family","shaadi","padhne",
    "mushkil","bachpan","jawani"
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
        "useless", "frustrating", "disappointing", "annoying",
        "hopeless","worthless","frustrated","stuck","lost",
        "failure","failing","broken","exhausted",
        "drained","upset","sad","depressed","angry","annoyed",
        "demotivated","burnt out","burned out","overwhelmed"
    }

    text = text.lower()

    return any(word in text for word in negative_words)

