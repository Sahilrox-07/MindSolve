import logging

from flask import Flask, jsonify, render_template

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from utils.config import PORT

from routes.problems_routes import problem_bp
from routes.search_routes import search_bp
from routes.api_routes import api_bp
from routes.feedback_routes import feedback_bp

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"]
)

# =========================
# REGISTER BLUEPRINTS
# =========================

app.register_blueprint(problem_bp)
app.register_blueprint(search_bp)
app.register_blueprint(api_bp)
app.register_blueprint(feedback_bp)

logging.basicConfig(level=logging.INFO)

# =========================
# ERROR HANDLER
# =========================

@app.errorhandler(429)
def rate_limit_handler(e):

    app.logger.warning(f"Rate limit exceeded: {e}")

    return jsonify({
        "error": "Too many requests. Please slow down."
    }), 429


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=PORT
    )