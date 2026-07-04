from services.llm import llm


def classify_query(query: str):

    prompt = f"""
You are a routing classifier for an SHL Assessment Assistant.

Classify the user's query into exactly ONE category.

Return ONLY one of these labels:

COMPARISON
RECOMMENDATION
OUT_OF_SCOPE

Definitions:

COMPARISON
- User wants to compare two or more assessments.
Examples:
- Compare Python and Java
- Difference between OPQ and Verify

RECOMMENDATION
- User wants assessment recommendations.
- User is hiring.
- User wants candidate evaluation.
- User wants technical, aptitude, personality, behavioral or simulation assessments.

OUT_OF_SCOPE
- Anything unrelated to SHL assessments.
Examples:
- Write a poem
- Capital of France
- IPL score
- Weather
- General programming help

Return ONLY the label.

User Query:
{query}
"""

    response = llm.invoke(prompt)

    return response.content.strip().upper()