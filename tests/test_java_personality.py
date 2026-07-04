from services.retriever import retriever

query = """
I'm hiring a Java developer.
Actually add personality assessments.
"""

docs = retriever.invoke(query)

for i, doc in enumerate(docs, 1):
    print(f"\nResult {i}")
    print(doc.metadata["name"])
    print(doc.metadata["keys"])