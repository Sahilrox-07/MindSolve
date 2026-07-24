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