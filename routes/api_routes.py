# routes/api_routes.py
from flask import Blueprint, jsonify
from utils.database import problems_collection
from routes.api_routes import api_bp

api_bp = Blueprint("api_bp", __name__)

@api_bp.route("/recent")
def recent():

    if problems_collection is None:
        return jsonify({"problems": []})

    data = problems_collection.find().sort("time", -1).limit(5)

    return jsonify({
        "problems": [d.get("text", "") for d in data]
    })