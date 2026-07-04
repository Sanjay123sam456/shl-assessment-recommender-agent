import json
import re

from services.llm import llm
from services.retriever import retrieve_recommendations
from services.comparer import compare_assessments
from services.router import classify_query



CATEGORY_QUERIES = {
    "personality": "personality assessments",
    "behavior": "behavioral assessments",
    "behaviour": "behavioral assessments",
    "leadership": "leadership assessments",
    "simulation": "simulation assessments",
    "simulations": "simulation assessments",
    "language": "language assessments",
    "coding": "programming assessments",
    "programming": "programming assessments",
    "technical": "technical assessments",
    "aptitude": "aptitude assessments",
    "ability": "ability assessments",
    "cognitive": "cognitive ability assessments",
}


def is_vague(query: str):
    query = re.sub(r"[^\w\s]", "", query.lower()).strip()

    vague_queries = {
        "assessment",
        "test",
        "i need an assessment",
        "recommend an assessment",
        "recommend a test",
        "i need a test",
        "help me hire",
    }

    return query in vague_queries

def _parse_json_object(value: str):
    value = value.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", value, re.DOTALL)
    if fenced:
        value = fenced.group(1)
    else:
        start = value.find("{")
        end = value.rfind("}")
        if start >= 0 and end > start:
            value = value[start:end + 1]
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return {}


def _recommendation(doc):
    return {
        "name": doc.metadata["name"],
        "url": doc.metadata["link"],
        "test_type": ", ".join(doc.metadata["keys"]),
    }


def _build_reply(selected_docs, reasons):
    lines = ["Recommended assessments:"]
    for doc in selected_docs:
        entity_id = str(doc.metadata["entity_id"])
        reason = reasons.get(entity_id, "").strip()
        if not reason:
            reason = "Matches the role and assessment requirements in your request."
        lines.append(f"- {doc.metadata['name']}: {reason}")
    return "\n".join(lines)


def get_recommendation(messages):

    if not messages:
        return {
            "reply": "Please provide the role or assessment requirements.",
            "recommendations": [],
            "end_of_conversation": False,
        }

    latest_query = messages[-1].content

    user_messages = [m for m in messages if m.role == "user"]
    # A short follow-up usually answers the assistant's previous question.
    if len(user_messages) == 1 and is_vague(latest_query):
        return {
            "reply": (
                "I'd be happy to help.\n"
                "Could you tell me:\n"
                "1. What role are you hiring for?\n"
                "2. What seniority level?\n"
                "3. Are you looking for technical, aptitude, personality, or behavioral assessments?"
            ),
            "recommendations": [],
            "end_of_conversation": False,
        }

    # Step 2: Route the query
    route = classify_query(latest_query)

    if (
        len(user_messages) > 1
        and route == "OUT_OF_SCOPE"
        and len(latest_query.split()) <= 5
    ):
        route = "RECOMMENDATION"

    if route == "OUT_OF_SCOPE":
        return {
            "reply": (
                "I'm designed to help with SHL assessment recommendations, "
                "assessment comparisons, hiring, and candidate evaluation. "
                "Please ask me something related to SHL assessments."
            ),
            "recommendations": [],
            "end_of_conversation": False,
        }

    if route == "COMPARISON":
        return compare_assessments(latest_query)

    # Step 3: Recommendation flow

    conversation = "\n".join(
        f"{m.role}: {m.content}"
        for m in messages
    )

    conversation_query = "\n".join(
        m.content
        for m in messages
        if m.role == "user"
    )

    docs = []

    docs.extend(retrieve_recommendations(conversation_query))

    conversation_lower = conversation_query.lower()

    for keyword, search_query in CATEGORY_QUERIES.items():
        if keyword in conversation_lower:
            docs.extend(retrieve_recommendations(search_query))

    unique_docs = {}

    for doc in docs:
        unique_docs[doc.metadata["entity_id"]] = doc

    docs = list(unique_docs.values())
    # Re-rank retrieved assessments
    # docs = rerank_documents(conversation_query, docs)[:10]

    context = "\n\n".join(
        f"""
Assessment Name: {doc.metadata['name']}
Entity ID:
{doc.metadata["entity_id"]}


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

    decision_prompt = f"""
You are selecting SHL assessments for a hiring request.

Conversation:
{conversation}

Retrieved catalog entries:
{context}

Return ONLY valid JSON with this shape:
{{
  "needs_clarification": false,
  "clarification_question": "",
  "selected_entity_ids": ["catalog entity_id"],
  "reasons": {{"entity_id": "one short reason"}},
  "task_complete": true
}}

Do not include markdown.
Do not wrap the JSON in ``` blocks.
Return exactly one JSON object.

Rules:
1. Interpret every user message using the complete conversation history.
2. A short user reply normally answers the assistant's preceding question.
3. Select 1 to 10 entries only when the request contains enough information.
4. Select only entity IDs present in the retrieved catalog entries.
5. Select only assessments directly relevant to all current constraints.
6. Ask one focused clarification question ONLY if the missing information
   prevents you from recommending a reasonable SHL assessment shortlist.

   If the user's request already specifies enough information (such as a role,
   skill, technology, assessment category, or experience level), recommend
   appropriate assessments instead of asking unnecessary follow-up questions.

   Do not ask clarification questions about optional preferences that do not
   materially change the recommendation.

   If you can produce a relevant shortlist, return selected_entity_ids and set
   task_complete to true.
7. A changed constraint replaces the conflicting older constraint.
8. Set task_complete true when the shortlist satisfies the request without
   requiring another answer. Otherwise set it false.
9. Prefer making a recommendation over asking unnecessary clarification
   questions. Only ask for clarification when the missing information is
   essential to choose between substantially different assessment shortlists.
"""

    decision = _parse_json_object(llm.invoke(decision_prompt).content)

    if not decision:
        return {
            "reply": (
                "I couldn't determine reliable recommendations. "
                "Please try rephrasing your request."
            ),
            "recommendations": [],
            "end_of_conversation": False,
        }

    if decision.get("needs_clarification"):
        question = str(decision.get("clarification_question", "")).strip()
        return {
            "reply": question or "What role and seniority level are you hiring for?",
            "recommendations": [],
            "end_of_conversation": False,
        }

    docs_by_id = {str(doc.metadata["entity_id"]): doc for doc in docs}
    selected_docs = []
    seen_ids = set()
    for entity_id in decision.get("selected_entity_ids", []):
        entity_id = str(entity_id)
        if entity_id in docs_by_id and entity_id not in seen_ids:
            selected_docs.append(docs_by_id[entity_id])
            seen_ids.add(entity_id)
        if len(selected_docs) == 10:
            break

    raw_reasons = decision.get("reasons", {})
    reasons = (
        {str(entity_id): str(reason) for entity_id, reason in raw_reasons.items()}
        if isinstance(raw_reasons, dict)
        else {}
    )
    recommendations = [_recommendation(doc) for doc in selected_docs]
    reply = (
        _build_reply(selected_docs, reasons)
        if selected_docs
        else "I couldn't find a catalog assessment that reliably matches those requirements."
    )

    return {
        "reply": reply,
        "recommendations": recommendations,
        "end_of_conversation": bool(
            selected_docs and decision.get("task_complete", True)
        ),
    }