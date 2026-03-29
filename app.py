import os
import json
from flask import Flask, request, jsonify, render_template
from rapidfuzz import fuzz
from textblob import TextBlob
from pymongo import MongoClient
from dotenv import load_dotenv

# 🔐 Load environment variables
load_dotenv()

# 🔗 MongoDB Connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client["mindsolve"]
problems_collection = db["problems"]

# 🔹 Load data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "data.json"), encoding="utf-8") as f:
    knowledge_base = json.load(f)

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


# 🧹 Clean text
def clean_text(text):
    return text.lower().strip()


# 🧠 Autocorrect
def autocorrect_text(text):
    if len(text.split()) < 4:
        return text
    try:
        return str(TextBlob(text).correct())
    except:
        return text


# 🧠 Suggestion logic
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

    if best_score < 40 or not best_match:
        return ["No good match found. Try rephrasing."], []

    return best_match["solutions"], [best_match["problem"]]


# 🧠 Solve + Save
@app.route("/problem", methods=["POST"])
def solve_problem():
    data = request.get_json()
    text = data.get("text", "")

    try:
        if text:
            problems_collection.insert_one({"problem": text})
    except Exception as e:
        print("MongoDB Error:", e)

    suggestions, similar = get_suggestions(text)

    return jsonify({
        "suggestions": suggestions,
        "similar": similar
    })


# 🔍 Search
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

    results = list(set(results))

    return jsonify({"results": results[:5]})


# 📂 Category
@app.route("/category", methods=["POST"])
def get_category():
    data = request.get_json()
    category = data.get("category", "").lower().strip()

    if category not in knowledge_base:
        return jsonify({"problems": []})

    problems = [item["problem"] for item in knowledge_base[category]]

    return jsonify({"problems": problems})


# 🧠 Recent Problems
@app.route("/recent", methods=["GET"])
def get_recent():
    problems = list(problems_collection.find().sort("_id", -1).limit(10))

    return jsonify({
        "problems": [p["problem"] for p in problems]
    })


# 🚀 Run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))