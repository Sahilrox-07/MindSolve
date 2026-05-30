from flask import Blueprint, jsonify
from datetime import datetime, timezone, timedelta

from utils.database import problems_collection

api_bp = Blueprint("api_bp", __name__)

# =========================
# RECENT PROBLEMS
# =========================

@api_bp.route("/recent")
def recent():

    if problems_collection is None:
        return jsonify({"problems": []})

    data = problems_collection.find().sort("time", -1).limit(5)

    return jsonify({
        "problems": [d.get("text", "") for d in data]
    })


# =========================
# TRENDING PROBLEMS
# =========================

@api_bp.route("/trending")
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

        return jsonify({
            "trending": [r["_id"] for r in results]
        })

    except Exception:
        return jsonify({
            "trending": []
        })