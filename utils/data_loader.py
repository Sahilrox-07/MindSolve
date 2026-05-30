import json
import os
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

knowledge_base = {}

try:
    with open(
        os.path.join(BASE_DIR, "data.json"),
        encoding="utf-8"
    ) as f:

        knowledge_base = json.load(f)

    logging.info("Knowledge base loaded")

except Exception as e:
    logging.error(f"Failed loading data.json: {e}")