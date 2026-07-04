from services.comparer import compare_assessments


result = compare_assessments(
    "Compare Python (New) and Java 8 (New)"
)

print(result["reply"])

print("\nRecommendations:\n")

for item in result["recommendations"]:
    print(item["name"])