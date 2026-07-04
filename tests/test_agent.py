from services.agent import get_recommendation

reply, docs = get_recommendation(
    "I need a Python assessment for freshers."
)

print("LLM Response:\n")
print(reply)

print("\nRetrieved Assessments:\n")

for doc in docs:
    print(doc.metadata["name"])