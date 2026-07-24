from flask import Blueprint, request, jsonify
from datetime import datetime, timezone

from services.text_service import (
    is_valid_problem,
    detect_language,
    translate_to_english,
    is_clean,
    is_negative_sentiment
)

from services.spell_service import correct_text

from services.classification_service import (
    classify_problem, 
    detect_cause
)

from services.matching_service import (
    get_suggestions,
    format_response
)

from services.recommendation_service import get_cause_solutions


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

    all_suggestions = []
    all_similar = []

    analyses = []

    abuse_detected = False
    negative_detected = False

    for line in lines:

        lang = detect_language(line)
        text = translate_to_english(line) if lang != "en" else line

        text = correct_text(text)

        if not is_clean(text):
            abuse_detected = True
            continue

        if is_negative_sentiment(text):
            negative_detected = True
            continue

        if not is_valid_problem(text):
            continue

        category_result = classify_problem(text)

        cause_result = detect_cause(text)

        category = category_result["category"]
        category_confidence = category_result["confidence"]
        category_matches = category_result["matched_words"]
        

        cause = cause_result["cause"]
        cause_confidence = cause_result["confidence"]
        cause_matches = cause_result["matched_words"]

        analyses.append({

            "category": category,

            "category_confidence": category_confidence,

            "category_matches": category_matches,

            "cause": cause,

            "cause_confidence": cause_confidence,

            "cause_matches": cause_matches

        })

        if problems_collection is not None:
            try:

                problems_collection.insert_one({

                "text": line,

                "processed_text": text,

                "language": lang,

                "category": category,

                "category_confidence": category_confidence,

                "cause": cause,

                "cause_confidence": cause_confidence,

                "created_at": datetime.now(timezone.utc)

            })

            except Exception as e:

                logging.error(
                    f"Problem insertion failed: {e}"
        )

        print("\n" + "=" * 70)
        print(f"TEXT: {text}")
        print(f"CATEGORY: {category}")
        print(f"CATEGORY SCORE: {category_confidence}")
        print(f"CATEGORY MATCHES: {category_matches}")
        print(f"CAUSE: {cause}")
        print(f"CAUSE SCORE: {cause_confidence}")
        print(f"CAUSE MATCHES: {cause_matches}")
        print("=" * 70 + "\n")
                
        suggestions, similar = get_suggestions(
            text,
            category
        )

        cause_suggestions = get_cause_solutions(cause)

        if cause_suggestions:
            suggestions = cause_suggestions
            
        formatted = format_response(text, suggestions)

        all_suggestions.extend(formatted)
        all_similar.extend(similar)

    history = []

    if problems_collection is not None:
        try:
            recent = problems_collection.find().sort("created_at", -1).limit(3)
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

        "history": history,

        "analysis": analyses
    })