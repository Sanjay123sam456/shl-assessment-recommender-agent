from services.retriever import retriever

docs = retriever.invoke("personality assessments")

for i, doc in enumerate(docs, 1):
    print(f"\nResult {i}")
    print(doc.metadata["name"])
    print(doc.metadata["keys"])