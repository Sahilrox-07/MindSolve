from rapidfuzz import process
from utils.common_words import COMMON_WORDS
from utils.vocabulary import VOCABULARY
from utils.spelling_map import SPELLING_MAP
import re


def correct_text(text):
    words = re.findall(r"\b\w+\b", text.lower())

    corrected = []

    for word in words:
        clean_word = word

        # Keep common words unchanged
        if clean_word in COMMON_WORDS:
            corrected.append(clean_word)
            continue

        # Direct spelling fixes
        if clean_word in SPELLING_MAP:
            corrected.append(SPELLING_MAP[clean_word])
            continue

        # Skip very short words
        if len(clean_word) <= 3:
            corrected.append(clean_word)
            continue

        # Word already exists in vocabulary
        if clean_word in VOCABULARY:
            corrected.append(clean_word)
            continue

        # RapidFuzz matching
        match = process.extractOne(
            clean_word,
            VOCABULARY,
            score_cutoff=85
        )

        if match:
            matched_word = match[0]
            score = match[1]

            # Apply correction only if confidence is high
            if (
                abs(len(clean_word) - len(matched_word)) <= 2
                and score >= 90
            ):
                corrected.append(matched_word)
            else:
                corrected.append(clean_word)
        else:
            corrected.append(clean_word)

    corrected_text = " ".join(corrected)

    print("ORIGINAL:", text)
    print("CORRECTED:", corrected_text)

    return corrected_text