import os
from dotenv import load_dotenv

load_dotenv()


PORT = int(os.getenv("PORT", "5000"))

# =========================
# ENVIRONMENT VARIABLES
# =========================

MONGO_URI = os.getenv("MONGO_URI")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")