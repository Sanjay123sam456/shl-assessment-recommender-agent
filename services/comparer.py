from services.llm import llm
from services.retriever import retrieve_exact


def compare_assessments(query: str):
    extraction_prompt = f"""
Extract the SHL assessment names mentioned in the user's query.

Rules:
- Return ONLY assessment names.
- Separate multiple names with commas.
- Do NOT explain.
- Do NOT use bullets.
- Do NOT add quotes.

Examples:

Compare Python (New) and Java 8 (New)
Python (New), Java 8 (New)

Difference between OPQ32r and Verify G+
OPQ32r, Verify G+

User Query:
{query}
"""

    extracted = llm.invoke(extraction_prompt).content.strip()

    assessment_names = [
        name.strip()
        for name in extracted.split(",")
        if name.strip()
    ]

    # Fallback if the LLM returns "Python and Java"
    if len(assessment_names) < 2:
        assessment_names = [
            part.strip()
            for part in extracted.replace(" and ", ",").split(",")
            if part.strip()
        ]

    docs = []

    for name in assessment_names:
        matches = retrieve_exact(name)
        if matches:
            docs.extend(matches)

    # Remove duplicates
    unique_docs = {}

    for doc in docs:
        unique_docs[doc.metadata["entity_id"]] = doc

    docs = list(unique_docs.values())

    # Nothing found → don't hallucinate
    if not docs:
        return {
            "reply": (
                "I couldn't identify the requested SHL assessments. "
                "Please provide the exact assessment names."
            ),
            "recommendations": [],
            "end_of_conversation": False,
        }

    context = "\n\n".join(
        f"""
Assessment Name: {doc.metadata['name']}

Category:
{", ".join(doc.metadata["keys"])}

Job Levels:
{", ".join(doc.metadata["job_levels"])}

Duration:
{doc.metadata["duration"]}

Description:
{doc.page_content}
"""
        for doc in docs
    )

    comparison_prompt = f"""
You are an SHL Assessment expert.

Compare ONLY the retrieved assessments.

User Request:
{query}

Retrieved Assessments:
{context}

Explain:

- Purpose
- Skills measured
- Target audience
- When to use each assessment

Do NOT invent information.
Do NOT mention assessments that are not in the retrieved context.

Keep the comparison concise.
"""

    reply = llm.invoke(comparison_prompt).content

    recommendations = [
        {
            "name": doc.metadata["name"],
            "url": doc.metadata["link"],
            "test_type": ", ".join(doc.metadata["keys"]),
        }
        for doc in docs
    ]

    return {
        "reply": reply,
        "recommendations": recommendations,
        "end_of_conversation": True,
    }