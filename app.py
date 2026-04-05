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
# MongoDB
# =========================
problems_collection = None

try:
    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        raise Exception("Missing MONGO_URI")

    client = MongoClient(mongo_uri)
    client.admin.command("ping")

    db = client["mindsolve"]
    problems_collection = db["problems"]

    print("✅ MongoDB Connected")

except Exception as e:
    print("❌ MongoDB Error:", e)


# =========================
# Load JSON
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "data.json"), encoding="utf-8") as f:
    knowledge_base = json.load(f)


# =========================
# Utils
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
    if not text:
        return False

    text = text.strip()

    if len(text) < 5 or len(text) > 200:
        return False

    if len(set(text)) <= 2:
        return False

    if not any(c.isalpha() for c in text):
        return False

    return True


# =========================
# Suggestions
# =========================
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

    if best_score < 70 or not best_match:
        return ["No good match found"], []

    return best_match["solutions"], [best_match["problem"]]


# =========================
# Routes
# =========================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/problem", methods=["POST"])
def solve_problem():
    data = request.get_json()
    text = data.get("text", "").strip()

    if not is_valid_problem(text):
        return jsonify({"suggestions": ["Invalid input"], "similar": []})

    # SAVE
    if problems_collection is not None:
        existing = problems_collection.find_one({"problem": text})

        if not existing:
            problems_collection.insert_one({
                "problem": text,
                "timestamp": datetime.utcnow()
            })

    suggestions, json_similar = get_suggestions(text)

    mongo_similar = []
    if problems_collection is not None:
        cursor = problems_collection.find({
            "problem": {"$regex": text, "$options": "i"}
        }).limit(5)

        mongo_similar = [
            doc["problem"]
            for doc in cursor
            if doc["problem"].lower() != text.lower()
        ]

    return jsonify({
        "suggestions": suggestions,
        "similar": list(set(json_similar + mongo_similar))
    })


@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = clean_text(data.get("query", ""))

    corrected = autocorrect_text(query)
    results = []

    for category in knowledge_base:
        for item in knowledge_base[category]:
            score = fuzz.partial_ratio(corrected, clean_text(item["problem"]))

            if score > 70:
                results.append(item["problem"])

    return jsonify({"results": list(set(results))[:5]})


@app.route("/category", methods=["POST"])
def category():
    data = request.get_json()
    cat = data.get("category", "").lower()

    if cat not in knowledge_base:
        return jsonify({"problems": []})

    return jsonify({
        "problems": [item["problem"] for item in knowledge_base[cat]]
    })


@app.route("/recent")
def recent():
    if problems_collection is None:
        return jsonify({"problems": []})

    data = problems_collection.find().sort("timestamp", -1).limit(5)

    return jsonify({
        "problems": [d["problem"] for d in data]
    })


@app.route("/trending")
def trending():
    if problems_collection is None:
        return jsonify({"trending": []})

    recent_time = datetime.utcnow() - timedelta(days=7)

    pipeline = [
        {"$match": {"timestamp": {"$gte": recent_time}}},
        {"$group": {"_id": "$problem", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]

    results = list(problems_collection.aggregate(pipeline))

    return jsonify({
        "trending": [r["_id"] for r in results]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)