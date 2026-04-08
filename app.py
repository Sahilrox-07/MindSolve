import os
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
from rapidfuzz import fuzz
from textblob import TextBlob
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# =========================
# 🔗 MONGODB
# =========================
problems_collection = None

try:
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    client.admin.command("ping")

    db = client["mindsolve"]
    problems_collection = db["problems"]

    print("✅ MongoDB Connected")
except Exception as e:
    print("❌ MongoDB Error:", e)


# =========================
# 📂 LOAD DATA
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "data.json"), encoding="utf-8") as f:
    knowledge_base = json.load(f)


# =========================
# 🧹 UTILITIES
# =========================
def clean_text(text):
    return text.lower().strip()


def autocorrect_text(text):
    try:
        corrected = str(TextBlob(text).correct())
        if abs(len(corrected) - len(text)) > 5:
            return text
        return corrected
    except:
        return text


def is_valid_problem(text):
    if not text or len(text) < 5 or len(text) > 200:
        return False
    if len(set(text)) <= 2:
        return False
    if not any(c.isalpha() for c in text):
        return False
    return True


# =========================
# 🧠 INTENT DETECTION
# =========================
def detect_intent(text):
    text = text.lower()
    greetings = ["hello", "hi", "hey", "what is this", "who are you"]

    if any(g in text for g in greetings):
        return "basic"

    return "problem"


# =========================
# 🤖 BASIC RESPONSE
# =========================
def basic_response():
    return [
        "I'm MindSolve — a system designed to help you solve real-life problems.",
        "You can describe any issue you're facing and I'll guide you with practical solutions.",
        "Try something like: 'I can't focus while studying'"
    ]


# =========================
# 🧠 CATEGORY DETECTION (IMPROVED)
# =========================
def detect_category(text):
    text = text.lower()

    categories = {
        "study": ["study", "exam", "focus", "learn", "revision"],
        "career": ["job", "career", "interview", "resume"],
        "productivity": ["lazy", "time", "habit", "procrastinate"],
        "health": ["stress", "sleep", "anxiety", "tired"]
    }

    scores = {}

    for cat, keywords in categories.items():
        scores[cat] = sum(1 for word in keywords if word in text)

    best = max(scores, key=scores.get)

    return best if scores[best] > 0 else None


# =========================
# 🧠 SUGGESTION ENGINE (STRICT)
# =========================
def get_suggestions(problem_text):
    problem_text = clean_text(problem_text)
    corrected = autocorrect_text(problem_text)

    best_match = None
    best_score = 0

    for category in knowledge_base:
        for item in knowledge_base[category]:

            db_problem = clean_text(item["problem"])

            score = fuzz.token_set_ratio(corrected, db_problem)

            if score > best_score:
                best_score = score
                best_match = item

    if best_score < 70 or not best_match:
        return [], []

    return best_match["solutions"], [best_match["problem"]]


# =========================
# 🧠 RICH RESPONSE FORMAT
# =========================
def format_response(problem, solutions):

    if not solutions:
        return [
            f"I couldn't find an exact solution for '{problem}'.",
            "Try rephrasing your problem more clearly."
        ]

    explanation = (
        f"It looks like you're facing: '{problem}'. "
        "This usually happens due to lack of structure, distractions, or unclear direction."
    )

    steps = "Here’s what you can do:\n"
    for i, s in enumerate(solutions, 1):
        steps += f"{i}. {s.capitalize()}.\n"

    plan = (
        "\nStart with one step today. Keep it simple and stay consistent. "
        "Improvement comes from repetition, not perfection."
    )

    return [explanation, steps.strip(), plan]


# =========================
# 🌐 ROUTES
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# 🔥 MAIN
# =========================
@app.route("/problem", methods=["POST"])
def solve_problem():
    data = request.get_json()
    text = data.get("text", "").strip()

    if not is_valid_problem(text):
        return jsonify({"suggestions": ["Invalid or spam input"], "similar": []})

    intent = detect_intent(text)

    if intent == "basic":
        return jsonify({"suggestions": basic_response(), "similar": []})

    # SAVE (NO BOOL ERROR FIX)
    if problems_collection is not None:
        if not problems_collection.find_one({"problem": text}):
            problems_collection.insert_one({
                "problem": text,
                "timestamp": datetime.utcnow()
            })

    suggestions, similar = get_suggestions(text)

    response = format_response(text, suggestions)

    # LIGHT MEMORY
    history = []
    if problems_collection is not None:
        recent = problems_collection.find().sort("timestamp", -1).limit(3)
        history = [r["problem"] for r in recent]

    return jsonify({
        "suggestions": response,
        "similar": similar,
        "history": history
    })


# =========================
# 🔍 SEARCH (DATASET ONLY)
# =========================
@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = clean_text(data.get("query", ""))

    results = []

    for category in knowledge_base:
        for item in knowledge_base[category]:
            score = fuzz.token_set_ratio(query, clean_text(item["problem"]))
            if score > 70:
                results.append(item["problem"])

    return jsonify({"results": list(set(results))[:5]})


# =========================
# 🧠 RECENT
# =========================
@app.route("/recent")
def recent():
    if problems_collection is None:
        return jsonify({"problems": []})

    data = problems_collection.find().sort("timestamp", -1).limit(5)

    return jsonify({
        "problems": [d["problem"] for d in data]
    })


# =========================
# 📈 TRENDING
# =========================
@app.route("/trending")
def trending():
    if problems_collection is None:
        return jsonify({"trending": []})

    last_week = datetime.utcnow() - timedelta(days=7)

    pipeline = [
        {"$match": {"timestamp": {"$gte": last_week}}},
        {"$group": {"_id": "$problem", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]

    results = list(problems_collection.aggregate(pipeline))

    return jsonify({
        "trending": [r["_id"] for r in results]
    })


# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)