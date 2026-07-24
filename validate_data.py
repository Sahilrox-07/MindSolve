import json

from utils.vocabulary import VALID_TAGS
from utils.categories import VALID_CATEGORIES
from utils.causes import VALID_CAUSES
from utils.difficulties import VALID_DIFFICULTIES

with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

invalid_count = 0

print("Checking tags...\n")

for category in data.values():
    for item in category:
        for tag in item["tags"]:
            if tag not in VALID_TAGS:
                invalid_count += 1
                print(f"{item['id']} -> {tag}")

print(f"\nFinished. Invalid tags found: {invalid_count}")

print("\nChecking categories...\n")

invalid = 0

for category in data.values():
    for item in category:
        if item["category"] not in VALID_CATEGORIES:
            invalid += 1
            print(item["id"], "->", item["category"])

print(f"Invalid categories: {invalid}")

print("\nChecking causes...\n")

invalid = 0

for category in data.values():
    for item in category:
        if item["cause"] not in VALID_CAUSES:
            invalid += 1
            print(item["id"], "->", item["cause"])

print(f"Invalid causes: {invalid}")

print("\nChecking related causes...\n")

invalid = 0

for category in data.values():
    for item in category:
        for cause in item["related_causes"]:
            if cause not in VALID_CAUSES:
                invalid += 1
                print(item["id"], "->", cause)

print(f"Invalid related causes: {invalid}")

print("\nChecking difficulty...\n")

invalid = 0

for category in data.values():
    for item in category:
        if item["difficulty"] not in VALID_DIFFICULTIES:
            invalid += 1
            print(item["id"], "->", item["difficulty"])

print(f"Invalid difficulty values: {invalid}")

print("\nChecking duplicate IDs...\n")

ids = set()
duplicates = []

for category in data.values():
    for item in category:
        if item["id"] in ids:
            duplicates.append(item["id"])
        else:
            ids.add(item["id"])

if duplicates:
    print("Duplicate IDs found:")
    for dup in duplicates:
        print(" -", dup)
else:
    print("Duplicate IDs: 0")


print("\nChecking duplicate problems...\n")

problems = {}
duplicates = []

for category in data.values():
    for item in category:
        problem = item["problem"].strip().lower()

        if problem in problems:
            duplicates.append((problem, problems[problem], item["id"]))
        else:
            problems[problem] = item["id"]

if duplicates:
    print("Duplicate problems found:")
    for problem, first, second in duplicates:
        print(f"{first} <-> {second}: {problem}")
else:
    print("Duplicate problems: 0")

REQUIRED_FIELDS = {
    "id",
    "problem",
    "category",
    "cause",
    "difficulty",
    "keywords",
    "tags",
    "related_causes",
    "solutions"
}

print("\nChecking required fields...\n")

missing = 0

for category in data.values():
    for item in category:
        for field in REQUIRED_FIELDS:
            if field not in item:
                missing += 1
                print(item.get("id", "UNKNOWN"), "missing", field)

print(f"Missing fields: {missing}")    

print("\nChecking keyword count...\n")

issues = 0

for category in data.values():
    for item in category:
        count = len(item["keywords"])

        if count < 8 or count > 12:
            issues += 1
            print(item["id"], "has", count, "keywords")

print(f"Keyword count issues: {issues}")

print("\nChecking solution count...\n")

issues = 0

for category in data.values():
    for item in category:

        if len(item["solutions"]) != 3:
            issues += 1
            print(item["id"], "has", len(item["solutions"]), "solutions")

print(f"Solution count issues: {issues}")

print("\nChecking duplicate keywords...\n")

issues = 0

for category in data.values():
    for item in category:

        if len(item["keywords"]) != len(set(item["keywords"])):
            issues += 1
            print(item["id"], "contains duplicate keywords")

print(f"Duplicate keyword issues: {issues}")