from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.utils.logger import logger
from app.config import config

# Lazy imports (important for Render startup speed)
persona_detector = None
intent_classifier = None
retriever = None
generator = None
escalation_engine = None


# ---------------------------------------------
# FastAPI initialization
# ---------------------------------------------
app = FastAPI(
    title=config.APP_NAME,
    description="Persona-Adaptive Customer Support Agent",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------
# Load heavy modules after startup
# ---------------------------------------------
@app.on_event("startup")
def load_services():
    global persona_detector, intent_classifier, retriever, generator, escalation_engine

    logger.info("Loading AI services...")

    from app.services.persona import persona_detector as p
    from app.services.intent import intent_classifier as i
    from app.services.retriever import retriever as r
    from app.services.generator import generator as g
    from app.services.escalation import escalation_engine as e

    persona_detector = p
    intent_classifier = i
    retriever = r
    generator = g
    escalation_engine = e

    logger.info("All services loaded successfully.")


# ---------------------------------------------
# Validation error handler
# ---------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):

    logger.error(f"Validation error for request to {request.url}: {exc}")

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": [
                {
                    "location": " -> ".join(str(loc) for loc in err["loc"]),
                    "message": err["msg"],
                    "type": err["type"]
                }
                for err in exc.errors()
            ]
        }
    )


# ---------------------------------------------
# Request / Response Models
# ---------------------------------------------
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
    history: Optional[List[str]] = []


class ChatResponse(BaseModel):
    conversation_id: str
    persona: Dict[str, Any]
    intent: Dict[str, Any]
    response: str
    escalated: bool
    escalation_reason: str
    confidence: float
    context_summary: str
    timestamp: datetime


# ---------------------------------------------
# In-memory history store
# ---------------------------------------------
conversation_history = {}


# ---------------------------------------------
# Health Routes
# ---------------------------------------------
@app.get("/")
def root():
    return {
        "message": "Persona-Adaptive Customer Support Agent API",
        "status": "running"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


# ---------------------------------------------
# Chat Endpoint
# ---------------------------------------------
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    try:

        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        conv_id = request.conversation_id or datetime.now().strftime("%Y%m%d%H%M%S")

        if conv_id not in conversation_history:
            conversation_history[conv_id] = []

        history = conversation_history[conv_id][-5:]
        conversation_history[conv_id].append(request.message)

        # Persona detection
        persona_result = persona_detector.detect(request.message)

        # Intent classification
        intent_result = intent_classifier.classify(request.message)

        # Knowledge retrieval
        context, confidence = retriever.get_context_string(request.message)

        # Generate response
        response = generator.generate(
            user_message=request.message,
            context=context,
            persona=persona_result["persona"],
            intent=intent_result,
            conv_id=conv_id
        )

        # Escalation check
        escalate, reason = escalation_engine.should_escalate(
            message=request.message,
            persona=persona_result["persona"],
            intent=intent_result,
            confidence=confidence,
            history=history
        )

        return ChatResponse(
            conversation_id=conv_id,
            persona=persona_result,
            intent=intent_result,
            response=response,
            escalated=escalate,
            escalation_reason=reason,
            confidence=confidence,
            context_summary=f"Persona: {persona_result['persona']}, Intent: {intent_result['intent']}",
            timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
