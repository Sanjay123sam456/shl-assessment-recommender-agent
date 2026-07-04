import json

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


with open("data/shl_catalog.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)

documents = []

for item in catalog:
    text = f"""
Assessment Name: {item['name']}

Description:
{item['description']}

Category:
{", ".join(item['keys'])}

Job Levels:
{", ".join(item['job_levels'])}

Duration:
{item['duration']}
"""

    doc = Document(
        page_content=text,
        metadata={
            "entity_id": item["entity_id"],
            "name": item["name"],
            "link": item["link"],
            "duration": item["duration"],
            "job_levels": item["job_levels"],
            "keys": item["keys"],
        },
    )

    documents.append(doc)


embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)

vectorstore = FAISS.from_documents(
    documents=documents,
    embedding=embedding_model,
)

vectorstore.save_local("embeddings/faiss_index")

print(f"Indexed {len(documents)} assessments successfully.")