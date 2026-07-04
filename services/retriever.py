import re
import unicodedata

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)

vectorstore = FAISS.load_local(
    "embeddings/faiss_index",
    embedding_model,
    allow_dangerous_deserialization=True,
)


# Used for recommendation retrieval
recommendation_retriever = vectorstore.as_retriever(
    search_kwargs={"k": 15}
)


def retrieve_recommendations(query: str):
    """Semantic retrieval used for recommendations."""
    return recommendation_retriever.invoke(query)


def _normalize_name(value: str) -> str:
    """Normalize assessment names for robust matching."""
    value = unicodedata.normalize("NFKD", value).lower()
    value = value.replace("+", " plus ")
    return " ".join(re.findall(r"[a-z0-9]+", value))


def _catalog_documents():
    """Return all catalog documents stored in FAISS."""
    return list(vectorstore.docstore._dict.values())


def retrieve_exact(query: str):
    """
    Resolve an assessment using:
    1. Exact normalized title
    2. Common aliases
    3. Partial title matching
    4. Semantic fallback
    """

    normalized_query = _normalize_name(query)
    documents = _catalog_documents()

    # ----------------------------
    # 1. Exact normalized match
    # ----------------------------
    exact = [
        doc
        for doc in documents
        if _normalize_name(doc.metadata["name"]) == normalized_query
    ]

    if exact:
        return exact[:1]

    # ----------------------------
    # 2. Common aliases
    # ----------------------------
    aliases = {
        "opq": "occupational personality questionnaire opq32r",
        "opq32": "occupational personality questionnaire opq32r",
        "opq32r": "occupational personality questionnaire opq32r",
        "verify g+": "verify interactive g plus",
        "verify g plus": "verify interactive g plus",
    }

    target = aliases.get(normalized_query)

    if target:
        candidates = [
            doc
            for doc in documents
            if target in _normalize_name(doc.metadata["name"])
        ]

        if candidates:
            return candidates[:1]

    # ----------------------------
    # 3. Partial title match
    # ----------------------------
    contained = [
        doc
        for doc in documents
        if normalized_query
        and normalized_query in _normalize_name(doc.metadata["name"])
        and "report" not in _normalize_name(doc.metadata["name"])
    ]

    if contained:
        contained.sort(
            key=lambda doc: (
                len(_normalize_name(doc.metadata["name"])),
                doc.metadata["name"],
            )
        )
        return contained[:1]

    # ----------------------------
    # 4. Semantic fallback
    # ----------------------------
    return retrieve_recommendations(query)[:1]