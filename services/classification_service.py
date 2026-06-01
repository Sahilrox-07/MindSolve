def classify_problem(text):

    text = text.lower()

    categories = {
            "study": [
            "study", "exam", "focus", "college",
            "school", "learn", "subject", "marks"
        ],

        "career": [
            "job", "career", "interview",
            "resume", "salary", "work"
        ],

        "health": [
            "sleep", "stress", "anxiety",
            "health", "tired", "energy"
        ],

        "productivity": [
            "lazy", "procrastinate", "phone",
            "instagram", "youtube", "distraction"
        ]
    }
     
    scores = {}

    for category, words in categories.items():
        
        score = 0

        for word in words:
            
             if word in text:
                score += 1

        scores[category] = score

    best_category = max(scores, key=scores.get)

    if scores[best_category] == 0:
        return "general"
    
    return best_category

def detect_cause(text):

    text = text.lower()

    causes = {

        "phone_addiction": [
            "phone",
            "instagram",
            "youtube",
            "reels"
        ],

        "lack_of_focus": [
            "focus",
            "concentration",
            "attention"
        ],

        "procrastination": [
            "lazy",
            "later",
            "delay",
            "procrastinate"
        ],

        "stress": [
            "stress",
            "anxiety",
            "pressure"
        ]
    }

    for cause, keywords in causes.items():

        if any(word in text for word in keywords):
            return cause

    return "unknown"