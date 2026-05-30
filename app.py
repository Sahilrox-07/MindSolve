import logging

from flask import Flask, request, jsonify, render_template

from datetime import datetime, timezone, timedelta

from services.text_service import (
    clean_text,
    detect_language,
    translate_to_english,
    is_clean,
    is_negative_sentiment
)

from utils.database import (
    problems_collection,
    feedback_collection
)

from utils.data_loader import knowledge_base
from utils.config import PORT

from rapidfuzz import fuzz

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from routes.problems_routes import problem_bp
from routes.search_routes import search_bp
from routes.api_routes import api_bp

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"]
)



app.register_blueprint(problem_bp)
app.register_blueprint(api_bp)
app.register_blueprint(search_bp)

logging.basicConfig(level=logging.INFO)

@app.errorhandler(429)
def rate_limit_handler(e):

    app.logger.warning(f"Rate limit exceeded: {e}")

    return jsonify({
        "error": "Too many requests. Please slow down."}), 429    





# =========================
# 🌐 ROUTES
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# 📈 TRENDING
# =========================
@app.route("/trending")
def trending():
    if problems_collection is None:
        return jsonify({"trending": []})

    last_week = datetime.now(timezone.utc) - timedelta(days=7)

    pipeline = [
        {"$match": {"time": {"$gte": last_week}}},
        {"$group": {"_id": "$text", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]

    try:
        results = list(problems_collection.aggregate(pipeline))
        return jsonify({"trending": [r["_id"] for r in results]})
    except Exception as e:
        app.logger.error(f"Trending problems fetch failed: {e}")
        return jsonify({"trending": []})




# =========================
# 📝 FEEDBACK
# =========================
@app.route("/feedback", methods=["POST"])
@limiter.limit("5 per minute")  
def feedback():

    if feedback_collection is None:
        return jsonify({"status":"error"})

    data = request.get_json()
    text = data.get("feedback","").strip()

    if not text or not is_clean(text):
        return jsonify({"status":"error"})

    try:
        feedback_collection.insert_one({
            "text": text,
            "time": datetime.now(timezone.utc)
        })
        return jsonify({"status":"ok"})
    except Exception as e:
        app.logger.error(f"Feedback insertion failed: {e}")
        return jsonify({"status":"error"})


# =========================
# 📂 FEEDBACK HISTORY
# =========================
@app.route("/feedback/history")
def feedback_history():

    if feedback_collection is None:
        return jsonify({"feedback": []})

    try:
        data = feedback_collection.find().sort("time", -1).limit(5)

        return jsonify({
            "feedback": [d.get("text", "") for d in data]
        })
    except Exception as e:
        app.logger.error(f"Feedback history fetch failed: {e}")
        return jsonify({"feedback": []})


# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=PORT
    )