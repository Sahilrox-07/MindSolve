from rapidfuzz import fuzz
from services.text_service import clean_text
from utils.data_loader import knowledge_base


def get_suggestions(problem_text):

    if not knowledge_base:
        return ["System unavailable"], []

    problem_text = clean_text(problem_text)

    matches = []

    for category in knowledge_base:
        for item in knowledge_base[category]:

            db_problem = clean_text(item["problem"])

            score = max(
                fuzz.token_set_ratio(problem_text, db_problem),
                fuzz.partial_ratio(problem_text, db_problem)
            )

            if score >= 70:
                matches.append((score, item))

    matches.sort(key=lambda x: x[0], reverse=True)

    if not matches:
        return [
            "Break problem into smaller parts",
            "Identify root cause",
            "Start with one small step"
        ], []

    best = matches[0][1]
    similar = [m[1]["problem"] for m in matches[1:4]]

    return best["solutions"], similar


def format_response(problem, solutions):

    text = f"You're dealing with: {problem}\n\n"
    text += "Here's what you can do:\n"

    for i, s in enumerate(solutions, 1):
        text += f"{i}. {s}\n"

    return [text]