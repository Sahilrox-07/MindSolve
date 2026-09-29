from rapidfuzz import fuzz
from services.text_service import clean_text
from utils.data_loader import knowledge_base

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_suggestions(problem_text, category="general"):

    if not knowledge_base:
        return {
            "solutions": ["System unavailable"],
            "similar": [],
            "match": None,
            "score": 0
        }

    problem_text = clean_text(problem_text)

    documents = []
    items = []

    # =========================================
    # BUILD SEARCH DOCUMENTS
    # =========================================

    for kb_category in knowledge_base:
        for item in knowledge_base[kb_category]:

            db_problem = clean_text(
                item.get("problem", "")
            )

            aliases = [
                clean_text(alias)
                for alias in item.get("aliases", [])
            ]

            keywords = " ".join(
                clean_text(keyword)
                for keyword in item.get("keywords", [])
            )

            searchable_text = (
                f"{db_problem} "
                f"{' '.join(aliases)} "
                f"{keywords}"
            )

            documents.append(searchable_text)
            items.append(item)

    # =========================================
    # TF-IDF
    # =========================================

    try:

        vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2)
        )

        tfidf_matrix = vectorizer.fit_transform(
            documents
        )

        user_vector = vectorizer.transform(
            [problem_text]
        )

        cosine_scores = cosine_similarity(
            user_vector,
            tfidf_matrix
        )[0]

    except Exception as e:

        print(
            f"TF-IDF error: {e}"
        )

        cosine_scores = [
            0
        ] * len(items)

    # =========================================
    # RAPIDFUZZ + TF-IDF
    # =========================================

    matches = []

    for index, item in enumerate(items):

        db_problem = clean_text(
            item.get("problem", "")
        )

        aliases = [
            clean_text(alias)
            for alias in item.get("aliases", [])
        ]

        # -------------------------------------
        # Compare against main problem
        # -------------------------------------

        rapidfuzz_scores = [
            fuzz.token_set_ratio(
                problem_text,
                db_problem
            ),
            fuzz.partial_ratio(
                problem_text,
                db_problem
            )
        ]

        # -------------------------------------
        # Compare against each alias separately
        # -------------------------------------

        for alias in aliases:

            rapidfuzz_scores.append(
                fuzz.token_set_ratio(
                    problem_text,
                    alias
                )
            )

            rapidfuzz_scores.append(
                fuzz.partial_ratio(
                    problem_text,
                    alias
                )
            )

        # Strongest textual similarity
        rapidfuzz_score = max(
            rapidfuzz_scores
        )

        # -------------------------------------
        # TF-IDF score
        # -------------------------------------

        tfidf_score = (
            cosine_scores[index] * 100
        )

        # -------------------------------------
        # Combined score
        # -------------------------------------

        combined_score = (
            rapidfuzz_score * 0.7
            +
            tfidf_score * 0.3
        )

        if combined_score >= 50 and (
            tfidf_score > 10
            or rapidfuzz_score >= 85
        ):
            matches.append(
                (
                    combined_score,
                    rapidfuzz_score,
                    tfidf_score,
                    item
                )
            )

        # -------------------------------------
        # Keep reasonable matches
        # -------------------------------------

        if combined_score >= 50 and (
            tfidf_score > 10 or rapidfuzz_score >= 85
        ):
            matches.append(
                (
                    combined_score,
                    rapidfuzz_score,
                    tfidf_score,
                    item
                )
            )

    # =========================================
    # SORT
    # =========================================

    matches.sort(
        key=lambda x: x[0],
        reverse=True
    )

    # =========================================
    # NO MATCH
    # =========================================

    if not matches:

        if category == "study":

            return {
                "solutions": [
                    "Create a study plan and break topics into smaller sections",
                    "Focus on one subject at a time",
                    "Review your progress regularly"
                ],
                "similar": [],
                "match": None,
                "score": 0
            }

        elif category == "career":

            return {
                "solutions": [
                    "Identify the main career challenge you're facing",
                    "Research possible career paths and opportunities",
                    "Seek guidance from mentors or professionals"
                ],
                "similar": [],
                "match": None,
                "score": 0
            }

        elif category == "health":

            return {
                "solutions": [
                    "Pay attention to your sleep and daily routine",
                    "Try stress-management techniques",
                    "Consider consulting a healthcare professional if needed"
                ],
                "similar": [],
                "match": None,
                "score": 0
            }

        elif category == "productivity":

            return {
                "solutions": [
                    "Remove distractions from your environment",
                    "Set one small achievable goal",
                    "Track your progress consistently"
                ],
                "similar": [],
                "match": None,
                "score": 0
            }

        return {
            "solutions": [
                "Break the problem into smaller parts",
                "Identify the root cause",
                "Start with one small step"
            ],
            "similar": [],
            "match": None,
            "score": 0
        }

    # =========================================
    # BEST MATCH
    # =========================================

    best_score, best_rapidfuzz, best_tfidf, best = matches[0]

    # =========================================
    # SIMILAR PROBLEMS
    # =========================================

    similar = []

    for score, rapid, tfidf, item in matches[1:]:

        # Only include reasonably strong secondary matches
        if score >= 60:

            similar.append(
                item.get("problem", "")
            )

        if len(similar) == 3:
            break

    # =========================================
    # DEBUG INFORMATION
    # =========================================

    print(
        f"BEST MATCH: "
        f"{best.get('problem', '')}"
    )

    print(
        f"RapidFuzz Score: "
        f"{best_rapidfuzz:.2f}"
    )

    print(
        f"TF-IDF Score: "
        f"{best_tfidf:.2f}"
    )

    print(
        f"Combined Score: "
        f"{best_score:.2f}"
    )

    # =========================================
    # FINAL RESULT
    # =========================================

    return {
        "solutions": best.get(
            "solutions",
            []
        ),
        "similar": similar,
        "match": best,
        "score": best_score
    }


def format_response(problem, solutions):

    text = (
        f"You're dealing with: "
        f"{problem}\n\n"
    )

    text += (
        "Here's what you can do:\n"
    )

    for i, s in enumerate(
        solutions,
        1
    ):
        text += f"{i}. {s}\n"

    return [text]