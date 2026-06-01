def classify_problem(text):

    text = text.lower()
    words = text.split()

    categories = {
            "study": [
            "study", "exam", "focus", "college",
            "school", "learn", "subject", "marks",
            "studies",
            "studying", "concentrate", "concentration", "assignment", "homework"
        ],

        "career": [
            "job", "career", "interview",
            "resume", "salary", "work",
            "career_confusion", 
            "confused", "career", "future",
            "direction", "path", "choose",
            "decision"
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

    for category, words_list in categories.items():
        
        score = 0

        for word in words_list:
            
            if word in words:
                score += 1

        scores[category] = score

    best_category = max(scores, key=scores.get)

    if scores[best_category] == 0:
        return {
            "category": "general",
            "confidence": 0
        }

    return {
        "category": best_category,
        "confidence": scores[best_category]
    }

def detect_cause(text):

    text = text.lower()
    words = text.split()

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

    best_cause = "unknown"
    best_score = 0

    for cause, keywords in causes.items():

        score = 0

        for word in keywords:
            if word in words:
                score += 1

        if score > best_score:
            best_score = score
            best_cause = cause

    return {
        "cause": best_cause,
        "confidence": best_score
    }