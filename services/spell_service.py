from rapidfuzz import process

VOCABULARY = [
    "network issue",
    "slow performance",
    "application crash",
    "login failure",
    "data loss",
    "security breach",
    "hardware failure",
    "software bug",
    "compatibility issue",
    "user error",
    "configuration problem",
    "update failure",
    "memory leak",
    "disk space issue",
    "power failure",
    "study",
    "studying",
    "focus",
    "concentration",
    "career",
    "job",
    "future",
    "stress",
    "anxiety",
    "sleep",
    "health",
    "lazy",
    "procrastinate",
    "phone",
    "instagram",
    "youtube",
    "reels",
    "productivity",
    "assignment",
    "exam",
    "college",
    "university"
]

def correct_text(text):
    
    words = text.split()

    corrected = []

    for word in words:
        match = process.extractOne(
            word, 
            VOCABULARY,
            score_cutoff=80
        )

        if match:
            corrected.append(match[0])
        else:
            corrected.append(word)
    return " ".join(corrected)