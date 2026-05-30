from pymongo import MongoClient
from dotenv import load_dotenv
import os
import logging

load_dotenv()

# =========================
# 📦 MONGODB
# =========================

problems_collection = None
feedback_collection = None

try:

    print("MONGO_URI =", os.getenv("MONGO_URI"))

    mongo_uri = os.getenv("MONGO_URI")

    if mongo_uri:
        client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=5000,
            socketTimeoutMS=5000
        )

        # Test connection
        client.admin.command("ping")

        db = client["mindsolve"]

        problems_collection = db["problems"]
        feedback_collection = db["feedback"]

        logging.info("✅ MongoDB Connected")

    else:
        logging.warning("⚠️ MONGO_URI not found")

except Exception as e:
    logging.error(f"❌ MongoDB connection failed: {e}")