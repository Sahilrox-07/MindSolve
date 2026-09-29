import os
from dotenv import load_dotenv
from google import genai

# Load variables from .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Create Gemini client
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    client = None


def generate_ai_response(
    problem,
    matched_solution=None,
    category=None,
    cause=None
):
    """
    Generate an AI-based response for MindSolve.

    Returns:
        str: AI response
        None: if Gemini is unavailable or an error occurs
    """

    if not client:
        print("Gemini API key not configured.")
        return None

    local_context = matched_solution or "No relevant local solution was found."

    prompt = f"""
You are MindSolve, an AI-powered problem-solving assistant.

Your job is to help users with practical problems related to:
- Study
- Career
- Productivity
- Health and lifestyle

USER PROBLEM:
{problem}

CATEGORY:
{category or "Unknown"}

DETECTED CAUSE:
{cause or "Unknown"}

RELEVANT MINDSOLVE KNOWLEDGE:
{local_context}

Instructions:

1. Understand the user's actual problem.
2. Use the provided MindSolve knowledge when it is relevant.
3. If the local knowledge is incomplete, improve or expand it.
4. If no useful local knowledge exists, generate a suitable general response.
5. Give practical and realistic steps.
6. Keep the response concise and easy to understand.
7. Do not mention Gemini.
8. Do not mention internal datasets, APIs, algorithms, or implementation.
9. Do not make medical diagnoses.
10. For serious health problems, recommend consulting a qualified professional.

Return the response in this format:

Problem Understanding:
<brief explanation>

Possible Cause:
<brief explanation>

Recommended Steps:
1. <step>
2. <step>
3. <step>

Quick Tip:
<one useful practical tip>
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        return response.text

    except Exception as e:

        print(f"Gemini API error: {e}")
        return None