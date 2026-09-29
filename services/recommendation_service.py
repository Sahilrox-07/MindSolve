CAUSE_SOLUTIONS = {

    "lack_of_focus": [
        "Use the Pomodoro technique (25 minutes focus, 5 minutes break)",
        "Remove distractions from your study area",
        "Study one topic at a time"
    ],

    "phone_addiction": [
        "Use app blockers during work or study sessions",
        "Keep your phone in another room",
        "Disable unnecessary notifications"
    ],

    "procrastination": [
        "Start with the smallest possible task",
        "Set a timer for 5 minutes and begin immediately",
        "Break large tasks into smaller steps"
    ],

    "stress": [
        "Take regular short breaks",
        "Practice breathing exercises",
        "Avoid multitasking excessively"
    ],

    "lack_of_energy": [
        "Maintain a consistent sleep schedule",
        "Take short breaks instead of pushing through exhaustion",
        "Eat balanced meals and stay hydrated"
    ],
}


def get_cause_solutions(cause):

    return CAUSE_SOLUTIONS.get(cause, [])


def build_local_recommendation(
    match=None,
    match_score=0,
    cause=None
):

    """
    Build a local recommendation using:

    1. Matched knowledge-base problem
    2. Matched problem solutions
    3. Cause-based solutions

    This function does not call Gemini.
    """

    cause_suggestions = get_cause_solutions(cause)

    # =========================
    # STRONG MATCH
    # =========================

    if match and match_score >= 75:

        matched_solutions = match.get(
            "solutions",
            []
        )

        return {
            "source": "local",
            "score": match_score,
            "matched_problem": match.get(
                "problem",
                ""
            ),
            "solutions": matched_solutions,
            "cause_solutions": cause_suggestions
        }

    # =========================
    # WEAK / NO MATCH
    # =========================

    if cause_suggestions:

        return {
            "source": "cause",
            "score": match_score,
            "matched_problem": (
                match.get("problem")
                if match
                else None
            ),
            "solutions": cause_suggestions,
            "cause_solutions": cause_suggestions
        }

    # =========================
    # NOTHING AVAILABLE
    # =========================

    return {
        "source": "none",
        "score": match_score,
        "matched_problem": (
            match.get("problem")
            if match
            else None
        ),
        "solutions": [],
        "cause_solutions": []
    }