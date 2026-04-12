import os
import json
import re
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify, render_template
from rapidfuzz import fuzz
from textblob import TextBlob
from pymongo import MongoClient
from dotenv import load_dotenv
from langdetect import detect
from deep_translator import GoogleTranslator

load_dotenv()
app = Flask(__name__)

# =========================
# 🔗 MONGODB
# =========================
problems_collection = None
feedback_collection = None

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
except:
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
    return (
        text
        and 5 <= len(text) <= 200
        and len(set(text)) > 2
        and any(c.isalpha() for c in text)
    )


# =========================
# 🧠 HINGLISH DETECTION
# =========================
def is_hinglish(text):
    hinglish_words = {
        "hai","nahi","kyu","kaise","bekar","acha","kharab",
        "jarurat","mujhe","tum","ye","wo","kya","kar",
        "raha","rahi","mai","hum","aap","samajh",
        "bekar", "bhai", "sahi", "kaam", "help chahiye"
    }

    words = text.lower().split()
    score = sum(1 for w in words if w in hinglish_words)

    return score >= 1


# =========================
# 🌐 LANGUAGE CONTROL
# =========================
def detect_language(text):
    try:
        if is_hinglish(text):
            return "hi"

        detected = detect(text)

        if detected not in ["en", "hi"]:
            return "en"

        return detected

    except:
        return "en"


def translate_to_english(text):
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except:
        return text


def translate_from_english(text, lang):
    try:
        if lang == "en":
            return text
        return GoogleTranslator(source='en', target=lang).translate(text)
    except:
        return text


# =========================
# 🚫 ABUSE FILTER
# =========================
BAD_WORDS = [
    "madarchod", "behenchod", "bhosdike", "chutiya", "gandu",
    "loda", "randi", "harami", "kaminey", "mc", "bc", "bkl", "bsdk",
    "mutthi maroge", "goli maaro", "maro goli", "goli maar", "maar goli",
    "muthi", "tere ma ka bhosada", "bhosada", "teri maa ki choot", "teri ma ki chut"
]

def is_clean(text):
    text = text.lower()

    # normalize FIRST (critical fix)
    text = text.replace("1", "i").replace("5", "s").replace("0", "o")
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    # phrase check AFTER normalization
    for bad in BAD_WORDS:
        if bad in text:
            return False

    words = re.findall(r'[a-zA-Z]+', text)

    for w in words:
        for bad in BAD_WORDS:
            if fuzz.ratio(w, bad) > 85:
                return False

    return True


# =========================
# 😐 SENTIMENT
# =========================
def is_negative_sentiment(text):
    try:
        polarity = TextBlob(text).sentiment.polarity

        negative_words = [
            "sucks","bad","worst","useless","hate",
            "terrible","awful","frustrating","annoying"
        ]

        if any(w in text.lower() for w in negative_words):
            return True

        return polarity < -0.4
    except:
        return False


# =========================
# 🤖 RESPONSES
# =========================
def basic_response():
    return [
        "I'm MindSolve — a system designed to help you solve real-life problems.",
        "Describe your issue and I’ll guide you.",
        "Example: I can't focus while studying"
    ]


def negative_response():
    return [
        "It seems like you're having a frustrating experience.",
        "We’re here to help improve things.",
        "Tell us what went wrong so we can assist better."
    ]


# =========================
# 🧠 MATCHING ENGINE
# =========================
def get_suggestions(problem_text):
    if not knowledge_base:
        return ["System unavailable"], []

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

            if score > 70:
                matches.append((score, item))

    matches.sort(key=lambda x: x[0], reverse=True)

    if not matches:
        return [
            "Break problem into smaller parts",
            "Identify root cause",
            "Start with one small step"
        ], []

    best = matches[0][1]
    similar = [m[1]["problem"] for m in matches[1:4]]

    return best["solutions"], similar


def format_response(problem, solutions):
    explanation = f"You're dealing with: '{problem}'."

    steps = "Steps:\n"
    for i, s in enumerate(solutions, 1):
        steps += f"{i}. {s}\n"

    return [explanation, steps]


# =========================
# 🌐 ROUTES
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# 🔥 MAIN ROUTE (UPDATED)
# =========================
@app.route("/problem", methods=["POST"])
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

    lang = detect_language(original)

    text = original
    if lang != "en":
        text = translate_to_english(original)

    # 🚫 ABUSE
    if not is_clean(text):
        return jsonify({
            "type": "abuse",
            "suggestions": [
                "Please avoid offensive language.",
                "Describe your issue clearly."
            ],
            "similar": [],
            "history": []
        })

    # 😐 NEGATIVE
    if is_negative_sentiment(text):
        return jsonify({
            "type": "negative",
            "suggestions": negative_response(),
            "similar": [],
            "history": []
        })

    # ❌ INVALID
    if not is_valid_problem(text):
        return jsonify({
            "type": "error",
            "suggestions": ["Invalid input"],
            "similar": [],
            "history": []
        })

    # ✅ STORE PROBLEM (YOU WERE MISSING THIS)
    if problems_collection is not None:
        try:
            problems_collection.insert_one({
                "text": original,
                "time": datetime.now(timezone.utc)
            })
        except:
            pass

    # 🔍 PROCESS
    suggestions, similar = get_suggestions(text)
    response = format_response(text, suggestions)

    # 🌐 TRANSLATE BACK
    if lang == "hi":
        response = [translate_from_english(r, "hi") for r in response]
        similar = [translate_from_english(s, "hi") for s in similar]

    history = []
    if problems_collection is not None:
        try:
            recent = problems_collection.find().sort("time", -1).limit(3)
            history = [r.get("text", "") for r in recent]
        except:
            history = []

    return jsonify({
        "type": "normal",
        "suggestions": response,
        "similar": similar,
        "history": history
    })


# =========================
# 🧾 RECENT (NEW)
# =========================
@app.route("/recent")
def recent():

    if problems_collection is None:
        return jsonify({"problems": []})

    data = problems_collection.find().sort("time", -1).limit(5)

    return jsonify({
        "problems": [d.get("text", "") for d in data]
    })


# =========================
# 📈 TRENDING (NEW SIMPLE VERSION)
# =========================
@app.route("/trending")
def trending():

    if problems_collection is None:
        return jsonify({"trending": []})

    last_week = datetime.now(timezone.utc) - timedelta(days=7)

    try:
        pipeline = [
            {"$match": {"time": {"$gte": last_week}}},
            {"$group": {"_id": "$text", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]

        results = list(problems_collection.aggregate(pipeline))

        return jsonify({
            "trending": [r["_id"] for r in results]
        })
    except:
        return jsonify({"trending": []})


# =========================
# 📂 FEEDBACK HISTORY (NEW)
# =========================
@app.route("/feedback/history")
def feedback_history():

    if feedback_collection is None:
        return jsonify({"feedback": []})

    data = feedback_collection.find().sort("time", -1).limit(5)

    return jsonify({
        "feedback": [d.get("text", "") for d in data]
    })


# =========================
# 🔍 SEARCH
# =========================
@app.route("/search", methods=["POST"])
def search():

    data = request.get_json()
    original_query = data.get("query", "")

    lang = detect_language(original_query)

    if lang == "hi":
        query = translate_to_english(original_query)
    else:
        query = original_query

    if not query:
        return jsonify({"results": []})

    query = clean_text(query)

    if len(query) < 2 or not is_clean(query):
        return jsonify({"results": []})

    results = []

    for category in knowledge_base:
        for item in knowledge_base[category]:
            db_problem = clean_text(item["problem"])

            score = fuzz.token_set_ratio(query, db_problem)

            if score > 50:
                results.append((score, item["problem"]))

    results.sort(key=lambda x: x[0], reverse=True)

    seen = set()
    final = []

    for _, p in results:
        if p not in seen:
            seen.add(p)
            final.append(p)

    # translate back if Hindi
    if lang == "hi":
        final = [translate_from_english(r, "hi") for r in final]

    return jsonify({"results": final[:5]})


# =========================
# 📝 FEEDBACK
# =========================
@app.route("/feedback", methods=["POST"])
def feedback():

    if feedback_collection is None:
        return jsonify({"status": "error"})

    data = request.get_json()
    text = data.get("feedback", "").strip()

    if not text or not is_clean(text):
        return jsonify({"status": "error"})

    try:
        feedback_collection.insert_one({
            "text": text,
            "time": datetime.now(timezone.utc)
        })
        return jsonify({"status": "ok"})
    except:
        return jsonify({"status": "error"})


# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)