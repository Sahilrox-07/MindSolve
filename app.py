import os
import json
from flask import Flask, request, jsonify, render_template
from rapidfuzz import fuzz
from textblob import TextBlob

# 🔹 Load data safely
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "data.json"), encoding="utf-8") as f:
    knowledge_base = json.load(f)

app = Flask(__name__)



@app.route("/")
def home():
    return render_template("index.html")


# 🧹 Clean text (normalize input)
def clean_text(text):
    return text.lower().strip()


# 🧠 Autocorrect (safe usage)
def autocorrect_text(text):
    if len(text.split()) < 3:
        return text
    try:
        return str(TextBlob(text).correct())
    except:
        return text


# 🧠 Suggestion logic (fuzzy + autocorrect)
def get_suggestions(problem_text):

    problem_text = clean_text(problem_text)
    corrected_text = autocorrect_text(problem_text)

    best_match = None
    best_score = 0

    for category in knowledge_base:
        for item in knowledge_base[category]:

            db_problem = clean_text(item["problem"])

            score = max(
                fuzz.ratio(corrected_text, db_problem),
                fuzz.partial_ratio(corrected_text, db_problem)
            )

            if score > best_score:
                best_score = score
                best_match = item

    # 🛑 Safe fallback
    if best_score < 40 or not best_match:
        return ["No good match found. Try rephrasing."], []

    return best_match["solutions"], [best_match["problem"]]


# 🧠 Solve problem endpoint
@app.route("/problem", methods=["POST"])
def solve_problem():
    data = request.get_json()
    text = data.get("text", "")

    suggestions, similar = get_suggestions(text)

    return jsonify({
        "suggestions": suggestions,
        "similar": similar
    })


# 🔍 Smart search endpoint
@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = clean_text(data.get("query", ""))

    corrected_query = autocorrect_text(query)

    results = []

    for category in knowledge_base:
        for item in knowledge_base[category]:

            db_problem = clean_text(item["problem"])

            score = fuzz.partial_ratio(corrected_query, db_problem)

            if score > 40:
                results.append(item["problem"])

    # ❗ Remove duplicates
    results = list(set(results))

    return jsonify({"results": results[:5]})


# 📂 Category loader endpoint
@app.route("/category", methods=["POST"])
def get_category():
    data = request.get_json()
    category = data.get("category", "").lower().strip()

    if category not in knowledge_base:
        print(f"⚠️ Unknown category received: {category}")
        return jsonify({"problems": []})

    problems = [item["problem"] for item in knowledge_base[category]]

    return jsonify({"problems": problems})


# 🚀 Run server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))