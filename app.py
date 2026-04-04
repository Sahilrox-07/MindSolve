import os
import json
from flask import Flask, request, jsonify, render_template
from rapidfuzz import fuzz
from textblob import TextBlob
from pymongo import MongoClient
from dotenv import load_dotenv

# 🔐 Load environment variables
load_dotenv()

app = Flask(__name__)

# =========================
# 🔗 MongoDB Connection
# =========================
problems_collection = None

try:
    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        raise Exception("MONGO_URI not found")

    client = MongoClient(mongo_uri)

    # Test connection
    client.admin.command("ping")

    db = client["mindsolve"]
    problems_collection = db["problems"]

    print("✅ MongoDB Connected")

except Exception as e:
    print("❌ MongoDB Connection Failed:", e)
    problems_collection = None


# =========================
# 📂 Load JSON Knowledge Base
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "data.json"), encoding="utf-8") as f:
    knowledge_base = json.load(f)


# =========================
# 🧹 Utilities
# =========================
def clean_text(text):
    return text.lower().strip()


def autocorrect_text(text):
    try:
        return str(TextBlob(text).correct())
    except:
        return text


# =========================
# 🧠 Suggestion Engine (JSON)
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

    if best_score < 40 or not best_match:
        return ["No good match found. Try rephrasing."], []

    return best_match["solutions"], [best_match["problem"]]


# =========================
# 🌐 ROUTES
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# 🔥 SOLVE PROBLEM (SMART MEMORY)
# =========================
@app.route("/problem", methods=["POST"])
def solve_problem():
    try:
        data = request.get_json()
        text = data.get("text", "").strip()

        if not text:
            return jsonify({"suggestions": [], "similar": []})

        # =========================
        # 💾 SAVE TO MONGODB
        # =========================
        if problems_collection is not None:
            try:
                problems_collection.insert_one({"problem": text})
            except Exception as e:
                print("⚠️ Insert Error:", e)

        # =========================
        # 🧠 JSON Suggestions
        # =========================
        suggestions, json_similar = get_suggestions(text)

        # =========================
        # 🔥 SMART MEMORY (Mongo Search)
        # =========================
        mongo_similar = []

        if problems_collection is not None:
            try:
                cursor = problems_collection.find({
                    "problem": {"$regex": text, "$options": "i"}
                }).limit(5)

                mongo_similar = [
                    doc.get("problem", "")
                    for doc in cursor
                    if doc.get("problem", "").lower() != text.lower()
                ]

            except Exception as e:
                print("⚠️ Mongo search error:", e)

        # =========================
        # 🔗 MERGE RESULTS
        # =========================
        similar = list(set(json_similar + mongo_similar))

        return jsonify({
            "suggestions": suggestions,
            "similar": similar
        })

    except Exception as e:
        print("❌ /problem error:", e)
        return jsonify({"suggestions": [], "similar": []}), 500


# =========================
# 🔍 SEARCH (JSON + Mongo)
# =========================
@app.route("/search", methods=["POST"])
def search():
    try:
        data = request.get_json()
        query = clean_text(data.get("query", ""))

        corrected_query = autocorrect_text(query)

        results = []

        # JSON search
        for category in knowledge_base:
            for item in knowledge_base[category]:

                db_problem = clean_text(item["problem"])

                score = fuzz.partial_ratio(corrected_query, db_problem)

                if score > 40:
                    results.append(item["problem"])

        # Mongo search
        if problems_collection is not None:
            try:
                cursor = problems_collection.find({
                    "problem": {"$regex": corrected_query, "$options": "i"}
                }).limit(5)

                for doc in cursor:
                    results.append(doc.get("problem", ""))

            except Exception as e:
                print("⚠️ Mongo search error:", e)

        results = list(set(results))

        return jsonify({"results": results[:5]})

    except Exception as e:
        print("❌ /search error:", e)
        return jsonify({"results": []}), 500


# =========================
# 📂 CATEGORY
# =========================
@app.route("/category", methods=["POST"])
def get_category():
    try:
        data = request.get_json()
        category = data.get("category", "").lower().strip()

        if category not in knowledge_base:
            return jsonify({"problems": []})

        problems = [item["problem"] for item in knowledge_base[category]]

        return jsonify({"problems": problems})

    except Exception as e:
        print("❌ /category error:", e)
        return jsonify({"problems": []}), 500


# =========================
# 🧠 RECENT (MongoDB)
# =========================
@app.route("/recent", methods=["GET"])
def get_recent():
    try:
        if problems_collection is None:
            return jsonify({"problems": []})

        problems = list(
            problems_collection.find().sort("_id", -1).limit(10)
        )

        return jsonify({
            "problems": [p.get("problem", "") for p in problems]
        })

    except Exception as e:
        print("❌ /recent error:", e)
        return jsonify({"problems": []}), 500


# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))