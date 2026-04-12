import os
import json
import re
from datetime import datetime, timedelta, timezone
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

    if mongo_uri:
        client = MongoClient(mongo_uri)
        client.admin.command("ping")

        db = client["mindsolve"]
        problems_collection = db["problems"]
        feedback_collection = db["feedback"]

        print("✅ MongoDB Connected")
    else:
        print("⚠️ MONGO_URI not found")

except Exception as e:
    print("❌ MongoDB Error:", e)


# =========================
# 📂 LOAD DATA
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
knowledge_base = {}

try:
    with open(os.path.join(BASE_DIR, "data.json"), encoding="utf-8") as f:
        knowledge_base = json.load(f)
except FileNotFoundError:
    print("❌ data.json not found")


# =========================
# 🧹 UTILITIES
# =========================
def clean_text(text):
    return text.lower().strip()


def autocorrect_text(text):
    try:
        if len(text) < 6:
            return text

        corrected = str(TextBlob(text).correct())

        if fuzz.ratio(text, corrected) < 70:
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
# 🚫 ABUSE FILTER
# =========================
BAD_WORDS = [
    "hate", "stupid", "idiot", "dumb", "kill", "useless",
    "madarchod", "behenchod", "bhosdike", "chutiya", "gandu",
    "loda", "randi", "harami", "kaminey", "mc", "bc", "bkl", "bsdk",
    "mutthi maroge", "goli maaro", "maro goli", "goli maar", "maar goli",
    "muthi", "tere ma ka bhosada", "bhosada", "teri maa ki choot", "teri ma ki chut"
]

def is_clean(text):
    text = text.lower()

    # remove symbols
    cleaned = re.sub(r'[^a-zA-Z\s]', '', text)

    for word in BAD_WORDS:
        if word in cleaned:
            return False

    return True


# =========================
# 🧠 INTENT DETECTION
# =========================
def detect_intent(text):
    text = text.lower().strip()

    greetings = ["hello", "hi", "hey", "what is this", "who are you"]

    if any(text.startswith(g) for g in greetings) and len(text.split()) <= 3:
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
# 🧠 MATCHING ENGINE
# =========================
def get_suggestions(problem_text):

    if not knowledge_base:
        return ["System is currently unavailable. Please try again later."], []

    problem_text = clean_text(problem_text)
    corrected = autocorrect_text(problem_text)

    matches = []

    for category in knowledge_base:
        for item in knowledge_base[category]:

            db_problem = clean_text(item["problem"])

            score = max(
                fuzz.token_set_ratio(corrected, db_problem),
                fuzz.partial_ratio(corrected, db_problem)
            )

            if score > 55:
                matches.append((score, item))

    matches.sort(reverse=True, key=lambda x: x[0])

    if not matches:
        return [
            "Break the problem into smaller parts",
            "Identify what's causing the issue",
            "Start with one small action",
            "Consider seeking help from others"
        ], []

    best = matches[0][1]
    similar = [m[1]["problem"] for m in matches[1:4]]

    return best["solutions"], similar


# =========================
# 🧠 RESPONSE FORMAT
# =========================
def format_response(problem, solutions):

    explanation = (
        f"It looks like you're dealing with this issue: '{problem}'. "
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
# 🔥 MAIN ROUTE
# =========================
@app.route("/problem", methods=["POST"])
def solve_problem():

    data = request.get_json()
    text = data.get("text", "").strip()

    # 🚫 ABUSE CHECK
    if not is_clean(text):
        return jsonify({
            "suggestions": [
                "Please use respectful language.",
                "Describe your problem without offensive words."
            ],
            "similar": [],
            "history": []
        })

    # validation
    if not is_valid_problem(text):
        return jsonify({
            "suggestions": ["Invalid input"],
            "similar": [],
            "history": []
        })

    # intent
    intent = detect_intent(text)

    if intent == "basic":
        return jsonify({
            "suggestions": basic_response(),
            "similar": [],
            "history": []
        })

    # 🔥 NORMALIZED STORAGE
    if problems_collection is not None:
        normalized = re.sub(r'\s+', ' ', clean_text(text))

        if not problems_collection.find_one({"problem": normalized}):
            problems_collection.insert_one({
                "problem": normalized,
                "original": text,
                "timestamp": datetime.now(timezone.utc)
            })

    # processing
    suggestions, similar = get_suggestions(text)
    response = format_response(text, suggestions)

    # memory
    history = []
    if problems_collection is not None:
        recent = problems_collection.find().sort("timestamp", -1).limit(3)
        history = [r.get("original", r["problem"]) for r in recent]

    return jsonify({
        "suggestions": response,
        "similar": similar,
        "history": history
    })


# =========================
# 🔍 SEARCH
# =========================
@app.route("/search", methods=["POST"])
def search():

    data = request.get_json()
    query = clean_text(data.get("query", ""))

    if len(query) < 2:
        return jsonify({"results": []})

    if not is_clean(query):
        return jsonify({"results": []})

    results = []

    for category in knowledge_base:
        for item in knowledge_base[category]:

            db_problem = clean_text(item["problem"])

            score = max(
                fuzz.token_set_ratio(query, db_problem),
                fuzz.partial_ratio(query, db_problem)
            )

            if score > 50:
                results.append((score, item["problem"]))

    results.sort(reverse=True, key=lambda x: x[0])

    seen = set()
    final = []

    for score, problem in results:
        if problem not in seen:
            seen.add(problem)
            final.append(problem)

    return jsonify({"results": final[:5]})


# =========================
# 📂 CATEGORY
# =========================
@app.route("/category", methods=["POST"])
def category():

    data = request.get_json()
    cat = data.get("category", "").lower()

    if cat not in knowledge_base:
        return jsonify({"problems": []})

    return jsonify({
        "problems": [item["problem"] for item in knowledge_base[cat][:5]]
    })


# =========================
# 🧠 RECENT
# =========================
@app.route("/recent")
def recent():

    if problems_collection is None:
        return jsonify({"problems": []})

    data = problems_collection.find().sort("timestamp", -1).limit(5)

    return jsonify({
        "problems": [d.get("original", d["problem"]) for d in data]
    })


# =========================
# 📈 TRENDING
# =========================
@app.route("/trending")
def trending():

    if problems_collection is None:
        return jsonify({"trending": []})

    last_week = datetime.now(timezone.utc) - timedelta(days=7)

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
# 📝 Feedback
# =========================

@app.route("/feedback", methods=["POST"])
def handle_feedback():

    if feedback_collection is None:
        return jsonify({"status": "error", "message": "Feedback system unavailable"})

    data = request.get_json()
    text = data.get("feedback", "").strip()

    #validation
    if not text or len(text) < 3:
        return jsonify({"status": "error", "message": "Feedback too short"})

    #optional : Block abusive feedback
    if not is_clean(text):
        return jsonify({"status": "error", "message": "Inappropriate feedback"})    

    try:
        normalized = re.sub(r'\s+', ' ', text.lower())
        if not feedback_collection.find_one({"feedback": normalized}):
            feedback_collection.insert_one({
                "feedback": normalized,
                "original": text,
                "timestamp": datetime.now(timezone.utc)
            })

        return jsonify({"status": "success", "message": "Feedback received"})
    
    except Exception as e:
        print("❌ Feedback Error:", e)
        return jsonify({"status": "error", "message": "Failed to save feedback"})   

# =========================
# 📂 GET FEEBACK HISTORY
# =========================

@app.route("/feedback/history")
def feedback_history():

    if feedback_collection is None:
        return jsonify({"feedback": []})

    data = feedback_collection.find().sort("timestamp", -1).limit(5)

    return jsonify({
        "feedback": [d.get("original", d["feedback"]) for d in data]
    })

# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)