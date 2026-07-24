import re

from utils.categories import CATEGORIES
from utils.causes import CAUSES


def classify_problem(text):

    words = re.findall(r"\b\w+\b", text.lower())

    scores = {}
    category_matches = {}

    for category, keywords in CATEGORIES.items():

        matched_words = [
            word for word in keywords
            if word in words
        ]

        score = len(matched_words)

        scores[category] = score
        category_matches[category] = matched_words

    best_category = max(scores, key=scores.get)

    if scores[best_category] == 0:
        return {
            "category": "general",
            "confidence": 0,
            "matched_words": []
        }

    return {
        "category": best_category,
        "confidence": scores[best_category],
        "matched_words": category_matches[best_category]
    }


def detect_cause(text):

    words = re.findall(r"\b\w+\b", text.lower())

    best_cause = "unknown"
    best_score = 0
    best_matches = []

    for cause, keywords in CAUSES.items():

        matched_words = [
            word for word in keywords
            if word in words
        ]

        score = len(matched_words)

        if score > best_score:
            best_score = score
            best_cause = cause
            best_matches = matched_words

    return {
        "cause": best_cause,
        "confidence": best_score,
        "matched_words": best_matches
    }