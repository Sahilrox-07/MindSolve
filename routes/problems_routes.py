from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
import logging

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

from services.recommendation_service import build_local_recommendation

from services.conversation_service import get_conversation_response

from utils.database import problems_collection

problem_bp = Blueprint("problem_bp", __name__)


@problem_bp.route("/problem", methods=["POST"])
def solve_problem():

    data = request.get_json() or {}
    original = data.get("text", "").strip()

    # =========================
    # EMPTY INPUT
    # =========================

    if not original:
        return jsonify({
            "type": "error",
            "suggestions": ["Please enter a problem"],
            "similar": [],
            "history": []
        })

    # Process maximum 5 lines
    lines = [
        line.strip()
        for line in original.split("\n")
        if line.strip()
    ][:5]

    all_suggestions = []
    all_similar = []

    analyses = []

    abuse_detected = False
    negative_detected = False

    # =========================
    # PROCESS EACH PROBLEM
    # =========================

    for line in lines:

                # =========================
        # CONVERSATIONAL MESSAGE
        # =========================

        conversation_response = get_conversation_response(line)

        if conversation_response:
            all_suggestions.append(conversation_response)
            continue

        # =========================
        # LANGUAGE DETECTION
        # =========================

        lang = detect_language(line)

        text = (
            translate_to_english(line)
            if lang != "en"
            else line
        )

        # =========================
        # SPELL CORRECTION
        # =========================

        text = correct_text(text)

        # =========================
        # ABUSE FILTER
        # =========================

        if not is_clean(text):
            abuse_detected = True
            continue

        # =========================
        # NEGATIVE SENTIMENT
        # =========================

        if is_negative_sentiment(text):
            negative_detected = True
            continue

        # =========================
        # VALIDATION
        # =========================

        if not is_valid_problem(text):
            continue

        # =========================
        # CATEGORY
        # =========================

        category_result = classify_problem(text)

        category = category_result["category"]
        category_confidence = category_result["confidence"]
        category_matches = category_result["matched_words"]

        # =========================
        # CAUSE
        # =========================

        cause_result = detect_cause(text)

        cause = cause_result["cause"]
        cause_confidence = cause_result["confidence"]
        cause_matches = cause_result["matched_words"]

        # =========================
        # MATCHING
        # =========================
        # Matching must happen BEFORE
        # match_score and match are used.

        match_result = get_suggestions(
            text,
            category
        )

        suggestions = match_result["solutions"]
        similar = match_result["similar"]
        match = match_result["match"]
        match_score = match_result["score"]

        # =========================
        # SCORE-BASED SOLUTIONS
        # =========================

        match = match_result["match"]
        match_score = match_result["score"]
        
        # =========================
        # LOCAL RECOMMENDATION
        # =========================

        recommendation = build_local_recommendation(
            match=match,
            match_score=match_score,
            cause=cause
        )

        if recommendation["solutions"]:
            suggestions = recommendation["solutions"]

        # =========================
        # ANALYSIS
        # =========================

        analyses.append({

            "category": category,

            "category_confidence": category_confidence,

            "category_matches": category_matches,

            "cause": cause,

            "cause_confidence": cause_confidence,

            "cause_matches": cause_matches,

            "match_score": match_score,

            "matched_problem": (
                match.get("problem")
                if match
                else None
            ),

            "recommendation_source": recommendation["source"],
        })

        # =========================
        # SAVE TO MONGODB
        # =========================

        if problems_collection is not None:

            try:

                problems_collection.insert_one({

                    "original_text": line,

                    "text": text,

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

        # =========================
        # DEBUG INFORMATION
        # =========================

        print("\n" + "=" * 70)

        print(f"TEXT: {text}")

        print(f"CATEGORY: {category}")

        print(
            f"CATEGORY SCORE: "
            f"{category_confidence}"
        )

        print(
            f"CATEGORY MATCHES: "
            f"{category_matches}"
        )

        print(f"CAUSE: {cause}")

        print(
            f"CAUSE SCORE: "
            f"{cause_confidence}"
        )

        print(
            f"CAUSE MATCHES: "
            f"{cause_matches}"
        )

        print(
            f"MATCH SCORE: "
            f"{match_score}"
        )

        print(
            "MATCHED PROBLEM: "
            f"{match.get('problem') if match else 'None'}"
        )

        print(
            f"RECOMMENDATION SOURCE: "
            f"{recommendation['source']}"
        )

        print("=" * 70 + "\n")

        # =========================
        # FORMAT RESPONSE
        # =========================

        formatted = format_response(
            text,
            suggestions
        )

        all_suggestions.extend(formatted)
        all_similar.extend(similar)

    # =========================
    # RECENT HISTORY
    # =========================

    history = []

    if problems_collection is not None:

        try:

            recent = (
                problems_collection
                .find()
                .sort("created_at", -1)
                .limit(3)
            )

            history = [
                r.get("text", "")
                for r in recent
            ]

        except Exception as e:

            logging.error(
                f"History fetch failed: {e}"
            )

    # =========================
    # ABUSE RESPONSE
    # =========================

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

    # =========================
    # NEGATIVE SENTIMENT RESPONSE
    # =========================

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

    # =========================
    # NO VALID SUGGESTIONS
    # =========================

    if not all_suggestions:

        return jsonify({

            "type": "error",

            "suggestions": [
                "Try describing your problem more clearly."
            ],

            "similar": [],

            "history": history

        })

    # =========================
    # FINAL RESPONSE
    # =========================

    return jsonify({

        "type": "normal",

        "suggestions": all_suggestions,

        "similar": list(set(all_similar))[:5],

        "history": history,

        "analysis": analyses

    })