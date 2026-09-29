from services.recommendation_service import (
    build_local_recommendation
)

test_match = {
    "problem": "I can't focus while studying.",
    "solutions": [
        "Use the Pomodoro technique to break study sessions into intervals.",
        "Eliminate distractions by studying in a quiet environment.",
        "Study in a fixed location to create a routine."
    ]
}

result = build_local_recommendation(
    match=test_match,
    match_score=100,
    cause="lack_of_focus"
)

print("\nRecommendation Result:")
print(result)