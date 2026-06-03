import re


def classify_problem(text):

    words = re.findall(r"\b\w+\b", text.lower())

    categories = {

        "study": [
            "study", "studies", "studying",
            "exam", "exams", "test", "tests",
            "quiz", "quizzes",
            "focus", "concentrate", "concentration",
            "college", "school", "university",
            "campus", "class", "classes",
            "lecture", "lectures",
            "teacher", "professor",
            "learn", "learning",
            "subject", "subjects",
            "marks", "grade", "grades",
            "cgpa", "gpa", "percentage",
            "syllabus", "chapter", "chapters",
            "assignment", "assignments",
            "homework", "project", "projects",
            "presentation", "presentations",
            "education", "academic", "academics",
            "revision", "revise",
            "memory", "memorize",
            "concept", "concepts",
            "notes", "notebook",
            "preparation", "preparing",
            "semester", "rank", "ranking",
            "performance", "lab",
            "practical", "tutorial",
            "doubt", "understand",
            "understanding", "course",
            "courses"
        ],

        "career": [
            "job", "jobs",
            "career", "future",
            "interview", "interviews",
            "resume", "cv",
            "salary", "package",
            "work", "working",
            "employment", "employer",
            "employee", "profession",
            "professional", "occupation",
            "office", "workplace",
            "promotion", "manager",
            "management", "boss",
            "company", "organization",
            "startup", "business",
            "internship", "intern",
            "placement", "placements",
            "recruiter", "recruitment",
            "hiring", "vacancy",
            "opening", "application",
            "applying", "offer",
            "income", "earning",
            "earnings", "pay",
            "skill", "skills",
            "upskill", "certification",
            "certificate", "linkedin",
            "freelance", "freelancing",
            "remote", "confused",
            "direction", "path",
            "choose", "decision"
        ],

        "health": [
            "health", "healthy",
            "unhealthy",
            "sleep", "sleeping",
            "insomnia", "rest",
            "stress", "stressed",
            "stressful",
            "anxiety", "anxious",
            "panic", "panicking",
            "nervous",
            "worried", "worry",
            "mental", "physical",
            "fitness", "fit",
            "exercise", "workout",
            "gym", "diet",
            "nutrition", "meal",
            "meals", "food",
            "eating", "weight",
            "body", "doctor",
            "hospital", "medicine",
            "treatment", "therapy",
            "fatigue", "exhaustion",
            "burnout", "depression",
            "headache", "migraine",
            "pain", "injury",
            "illness", "disease",
            "fever", "cold",
            "cough", "breathing",
            "recovery", "hydration",
            "water", "energy",
            "tired"
        ],

        "productivity": [
            "lazy", "laziness",
            "procrastinate", "procrastination",
            "delay", "postpone",
            "phone", "mobile",
            "instagram", "youtube",
            "facebook", "snapchat",
            "whatsapp", "telegram",
            "reels", "shorts",
            "scrolling", "scroll",
            "distraction", "distracted",
            "productive", "productivity",
            "waste", "time",
            "routine", "habit",
            "consistency", "consistent",
            "goal", "goals",
            "target", "targets",
            "planning", "plan",
            "organize", "organization",
            "schedule", "calendar",
            "deadline", "deadlines",
            "priority", "priorities",
            "discipline",
            "motivation", "motivated",
            "demotivated", "unmotivated",
            "multitasking", "workflow",
            "task", "tasks",
            "progress", "tracking",
            "achievement", "achieve",
            "accomplish", "effort"
        ]
    }

    scores = {}
    category_matches = {}

    for category, keywords in categories.items():

        matched_words = [
            word for word in keywords
            if word in words
        ]

        score = len(matched_words)

        scores[category] = score
        category_matches[category] = matched_words

    best_category = max(scores, key=scores.get)

    if scores[best_category] == 0:
        return {
            "category": "general",
            "confidence": 0,
            "matched_words": []
        }

    return {
        "category": best_category,
        "confidence": scores[best_category],
        "matched_words": category_matches[best_category]
    }


def detect_cause(text):

    words = re.findall(r"\b\w+\b", text.lower())

    causes = {

        "phone_addiction": [
            "phone", "mobile", "smartphone",
            "android", "iphone", "device",
            "screen", "screentime",
            "instagram", "youtube", "facebook",
            "snapchat", "whatsapp", "telegram",
            "twitter", "reddit", "discord",
            "social", "media",
            "reels", "shorts", "stories",
            "scroll", "scrolling",
            "feed", "binge", "video",
            "videos", "gaming", "games",
            "notification", "notifications",
            "chat", "chatting",
            "message", "messages",
            "online", "internet",
            "wifi", "content",
            "streaming", "watching",
            "addicted", "addiction",
            "compulsive", "checking",
            "refreshing"
        ],

        "lack_of_focus": [
            "focus", "focused", "focusing",
            "concentrate", "concentrating",
            "concentration", "attention",
            "attentive",
            "distracted", "distraction",
            "mind", "mindset",
            "daydream", "daydreaming",
            "wander", "wandering",
            "overthinking",
            "thoughts", "thinking",
            "clarity",
            "study", "studying",
            "learn", "learning",
            "reading", "revision",
            "memory", "remember",
            "memorize", "forget",
            "forgetting",
            "retention",
            "understand",
            "understanding",
            "deepwork",
            "interruptions",
            "noise",
            "bored",
            "boredom",
            "restless",
            "restlessness",
            "mental",
            "fatigue",
            "tired"
        ],

        "procrastination": [
            "lazy", "laziness",
            "delay", "delayed",
            "postpone", "postponing",
            "later", "tomorrow",
            "avoid", "avoiding",
            "procrastinate",
            "procrastinating",
            "pending",
            "unfinished",
            "uncompleted",
            "stuck",
            "unmotivated",
            "demotivated",
            "motivation",
            "discipline",
            "habit",
            "habits",
            "routine",
            "consistency",
            "task", "tasks",
            "deadline",
            "deadlines",
            "hesitation",
            "hesitate",
            "start",
            "starting",
            "begin",
            "beginning",
            "complete",
            "completion",
            "finish",
            "finishing",
            "effort",
            "wasting",
            "waste"
        ],

        "stress": [
            "stress",
            "stressed",
            "stressful",
            "anxiety",
            "anxious",
            "pressure",
            "pressured",
            "panic",
            "panicking",
            "worried",
            "worry",
            "burnout",
            "overwhelmed",
            "mental",
            "fatigue",
            "tired",
            "exhausted",
            "exhaustion"
        ],

        "career_confusion": [
            "career",
            "future",
            "confused",
            "confusion",
            "direction",
            "path",
            "choose",
            "choice",
            "decision",
            "decide",
            "goal",
            "goals",
            "purpose",
            "ambition",
            "dream",
            "dreams",
            "interest",
            "interests",
            "passion",
            "field",
            "profession",
            "occupation",
            "job",
            "jobs",
            "work",
            "employment",
            "opportunity",
            "opportunities",
            "guidance",
            "mentor",
            "advice",
            "uncertain",
            "unsure",
            "lost",
            "switch",
            "change",
            "stream",
            "branch",
            "specialization",
            "major",
            "degree",
            "graduation",
            "placement",
            "interview",
            "resume",
            "skill",
            "skills",
            "upskill",
            "growth",
            "roadmap"
        ]
    }

    best_cause = "unknown"
    best_score = 0
    best_matches = []

    for cause, keywords in causes.items():

        matched_words = [
            word for word in keywords
            if word in words
        ]

        score = len(matched_words)

        if score > best_score:
            best_score = score
            best_cause = cause
            best_matches = matched_words

    return {
        "cause": best_cause,
        "confidence": best_score,
        "matched_words": best_matches
    }