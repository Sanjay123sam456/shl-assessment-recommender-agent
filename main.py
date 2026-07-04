from fastapi import FastAPI

from models.schemas import ChatRequest, ChatResponse, Recommendation
from services.agent import get_recommendation

app = FastAPI(
    title="SHL Assessment Recommendation Agent",
    version="1.0.0"
)


@app.get("/")
def root():
    return {"message": "SHL Agent is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    result = get_recommendation(request.messages)

    recommendations = [
        Recommendation(
            name=item["name"],
            url=item["url"],
            test_type=item["test_type"],
        )
        for item in result["recommendations"]
    ]

    return ChatResponse(
        reply=result["reply"],
        recommendations=recommendations,
        end_of_conversation=result["end_of_conversation"],
    )