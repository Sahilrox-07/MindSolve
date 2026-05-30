from flask import Blueprint, request, jsonify
from datetime import datetime, timezone

from utils.database import feedback_collection

from services.text_service import (
    is_clean
)

feedback_bp = Blueprint("feedback_bp", __name__)


@feedback_bp.route("/feedback", methods=["POST"])
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

    except Exception:
        return jsonify({"status": "error"})


@feedback_bp.route("/feedback/history")
def feedback_history():

    if feedback_collection is None:
        return jsonify({"feedback": []})

    try:
        data = feedback_collection.find().sort("time", -1).limit(5)

        return jsonify({
            "feedback": [d.get("text", "") for d in data]
        })

    except Exception:
        return jsonify({"feedback": []})