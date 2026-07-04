from services.retriever import retriever

query = "I need a Python assessment for freshers"

results = retriever.invoke(query)

for i, doc in enumerate(results, start=1):
    print(f"\nResult {i}")
    print("Name:", doc.metadata["name"])
    print("Link:", doc.metadata["link"])
    print("Description:", doc.page_content[:200])