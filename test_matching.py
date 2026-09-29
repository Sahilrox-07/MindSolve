from services.matching_service import get_suggestions

test_cases = [
    # Study
    "I cannot focus while studying",
    "padhai me man nahi lagta",
    "I forget what i study",
    "I keep procrastinating my studies",

    # Career
    "I don't know which career to choose",
    "how can I prepare for an interview",
    "my resume is not getting selected",

    # Productivity
    "I waste too much time every day",
    "I keep getting distracted by my phone",
    "I cannot manage my time",

    # Health
    "I cannot sleep at night",
    "I feel tired all day",
    "I spend too much time on my phone"
]

print("=" * 70)
print("MINDSOLVE MATCHING BENCHMARK")
print("=" * 70)

for test in test_cases:

    print("\n" + "=" * 70)
    print(f"TEST : {test}")

    result = get_suggestions(test)

    match = result["match"]

    if match:
        print(
            f"MATCHED: {match.get('problem', 'Unknown')}"
        )

        print(
            f"SCORE: {result['score']:.2f})"
        )

        print(
            "SIMILAR:",
            result["similar"]
        )

    else:
        print("MATCHED: None")
        print("SCORE: 0")