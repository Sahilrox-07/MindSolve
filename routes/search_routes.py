from flask import Blueprint, request, jsonify

from rapidfuzz import fuzz

from services.text_service import (
    clean_text,
    detect_language,
    translate_to_english
)

from utils.data_loader import knowledge_base

search_bp = Blueprint("search_bp", __name__)

# =========================
# 🔍 SEARCH
# =========================
@search_bp.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    original_query = data.get("query","").strip()

    lang = detect_language(original_query)
    query = translate_to_english(original_query) if lang != "en" else original_query

    if not query or len(query) < 2:
        return jsonify({"results":[]})

    query = clean_text(query)

    results = []
    for category in knowledge_base:
        for item in knowledge_base[category]:
            db_problem = clean_text(item["problem"])
            score = fuzz.token_set_ratio(query, db_problem)

            if score > 50:
                results.append((score, item["problem"]))

    results.sort(key=lambda x:x[0], reverse=True)

    final = []
    seen = set()

    for _,p in results:
        if p not in seen:
            seen.add(p)
            final.append(p)

    return jsonify({"results": final[:5]})


# =========================
# 📂 CATEGORY
# =========================
@search_bp.route("/category", methods=["POST"])
def category():
    data = request.get_json()
    category = data.get("category","").lower()

    if category not in knowledge_base:
        return jsonify({"problems":[]})

    return jsonify({
        "problems":[item["problem"] for item in knowledge_base[category]][:5]
    })
