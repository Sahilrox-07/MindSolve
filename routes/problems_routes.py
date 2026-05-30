from flask import Blueprint, request, jsonify
from datetime import datetime, timezone

from services.text_service import (
    is_valid_problem,
    detect_language,
    translate_to_english,
    is_clean,
    is_negative_sentiment
)

from services.matching_service import (
    get_suggestions,
    format_response
)

from utils.database import problems_collection

import logging

problem_bp = Blueprint("problem_bp", __name__)


@problem_bp.route("/problem", methods=["POST"])
def solve_problem():

    data = request.get_json()
    original = data.get("text", "").strip()

    if not original:
        return jsonify({
            "type": "error",
            "suggestions": ["Please enter a problem"],
            "similar": [],
            "history": []
        })

    lines = [l.strip() for l in original.split("\n") if l.strip()][:5]

    if problems_collection is not None:
        try:
            for line in lines:

                lang = detect_language(line)
                text = translate_to_english(line) if lang != "en" else line

                if not is_clean(text):
                    continue

                if is_negative_sentiment(text):
                    continue

                if not is_valid_problem(text):
                    continue

                problems_collection.insert_one({
                    "text": line,
                    "time": datetime.now(timezone.utc)
                })

        except Exception as e:
            logging.error(f"Problem insertion failed: {e}")

    all_suggestions = []
    all_similar = []

    abuse_detected = False
    negative_detected = False

    for line in lines:

        lang = detect_language(line)
        text = translate_to_english(line) if lang != "en" else line

        if not is_clean(text):
            abuse_detected = True
            continue

        if is_negative_sentiment(text):
            negative_detected = True
            continue

        if not is_valid_problem(text):
            continue

        suggestions, similar = get_suggestions(text)
        formatted = format_response(text, suggestions)

        all_suggestions.extend(formatted)
        all_similar.extend(similar)

    history = []

    if problems_collection is not None:
        try:
            recent = problems_collection.find().sort("time", -1).limit(3)
            history = [r.get("text", "") for r in recent]

        except Exception as e:
            logging.error(f"History fetch failed: {e}")

    if abuse_detected:
        return jsonify({
            "type": "abuse",
            "suggestions": [
                "Please avoid offensive language.",
                "Describe your issue clearly."
            ],
            "similar": [],
            "history": history
        })

    if negative_detected and not all_suggestions:
        return jsonify({
            "type": "negative",
            "suggestions": [
                "It seems like you're having a frustrating experience.",
                "Try explaining your problem clearly so we can help."
            ],
            "similar": [],
            "history": history
        })

    if not all_suggestions:
        return jsonify({
            "type": "error",
            "suggestions": [
                "Try describing your problem more clearly."
            ],
            "similar": [],
            "history": history
        })

    return jsonify({
        "type": "normal",
        "suggestions": all_suggestions,
        "similar": list(set(all_similar))[:5],
        "history": history
    })