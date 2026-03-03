from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.services.persona import persona_detector
from app.services.intent import intent_classifier
from app.services.retriever import retriever
from app.services.generator import generator
from app.services.escalation import escalation_engine
from app.utils.logger import logger
from app.config import config

# Initialize FastAPI app
app = FastAPI(
    title=config.APP_NAME,
    description="Persona-Adaptive Customer Support Agent",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed response"""
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

# Request/Response Models
class ChatRequest(BaseModel):
    message: str = Field(
        ..., 
        description="User message", 
        min_length=1, 
        max_length=2000,
        example="I'm getting a 500 error when calling your API"
    )
    conversation_id: Optional[str] = Field(
        None, 
        description="Conversation ID for history tracking",
        example="conv_123456"
    )
    history: Optional[List[str]] = Field(
        default=[], 
        description="Recent message history",
        example=["Previous message 1", "Previous message 2"]
    )

class ChatResponse(BaseModel):
    conversation_id: str = Field(..., example="conv_123456")
    persona: Dict[str, Any] = Field(..., example={
        "persona": "technical",
        "confidence": 0.8,
        "description": "Technical expert user"
    })
    intent: Dict[str, Any] = Field(..., example={
        "intent": "technical_issue",
        "confidence": 0.85,
        "description": "Technical problem",
        "category": "technical"
    })
    response: str = Field(..., example="Based on our documentation, here's how to fix the 500 error...")
    escalated: bool = Field(..., example=False)
    escalation_reason: str = Field("", example="")
    confidence: float = Field(..., example=0.75, ge=0, le=1)
    context_summary: str = Field(..., example="Persona: technical, Intent: technical_issue")
    timestamp: datetime = Field(..., example="2024-03-03T02:56:37.943720")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_123456",
                "persona": {
                    "persona": "technical",
                    "confidence": 0.8,
                    "description": "Technical expert user"
                },
                "intent": {
                    "intent": "technical_issue",
                    "confidence": 0.85,
                    "description": "Technical problem",
                    "category": "technical"
                },
                "response": "Based on our documentation, here's how to fix the 500 error...",
                "escalated": False,
                "escalation_reason": "",
                "confidence": 0.75,
                "context_summary": "Persona: technical, Intent: technical_issue",
                "timestamp": "2024-03-03T02:56:37.943720"
            }
        }

# Store for conversation history (in production, use Redis/database)
conversation_history = {}

@app.get("/")
async def root():
    return {
        "message": "Persona-Adaptive Customer Support Agent API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Additional input validation
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Check for obviously malicious content
        dangerous_patterns = ['<script', 'javascript:', 'onclick=']
        if any(pattern in request.message.lower() for pattern in dangerous_patterns):
            raise HTTPException(status_code=400, detail="Message contains invalid content")
        
        # Generate or use conversation ID
        conv_id = request.conversation_id or datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Get conversation history
        if conv_id not in conversation_history:
            conversation_history[conv_id] = []
        
        # Add current message to history
        history = conversation_history[conv_id][-5:]  # Last 5 messages
        conversation_history[conv_id].append(request.message)
        
        # 1. Detect persona
        logger.info(f"Processing message: {request.message[:50]}...")
        persona_result = persona_detector.detect(request.message)
        
        # 2. Classify intent
        intent_result = intent_classifier.classify(request.message)
        
        # 3. Retrieve knowledge base content
        context, confidence = retriever.get_context_string(request.message)
        
        # 4. Generate response
        response = generator.generate(
            user_message=request.message,
            context=context,
            persona=persona_result["persona"],
            intent=intent_result,
            conv_id=conv_id
        )
        
        # 5. Check if escalation needed
        should_escalate, reason = escalation_engine.should_escalate(
            message=request.message,
            persona=persona_result["persona"],
            intent=intent_result,
            confidence=confidence,
            history=history
        )
        
        # Prepare context summary
        context_summary = f"Persona: {persona_result['persona']}, Intent: {intent_result['intent']}"
        
        # Prepare response
        chat_response = ChatResponse(
            conversation_id=conv_id,
            persona=persona_result,
            intent=intent_result,
            response=response,
            escalated=should_escalate,
            escalation_reason=reason,
            confidence=confidence,
            context_summary=context_summary,
            timestamp=datetime.now()
        )
        
        # If escalated, prepare context for human
        if should_escalate:
            escalation_context = escalation_engine.prepare_context(
                message=request.message,
                persona=persona_result["persona"],
                intent=intent_result,
                response=response,
                history=history
            )
            logger.info(f"Escalation context prepared with priority: {escalation_context.get('priority', 'unknown')}")
        
        logger.info(f"Response generated successfully for conv_id: {conv_id}")
        return chat_response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/history/{conversation_id}")
async def get_history(conversation_id: str):
    """Get conversation history"""
    # Clean the ID - remove any accidental quotes
    clean_id = conversation_id.strip('"\'')
    logger.info(f"Getting history for: {clean_id}")
    
    if clean_id in conversation_history:
        return {
            "conversation_id": clean_id,
            "history": conversation_history[clean_id],
            "message_count": len(conversation_history[clean_id])
        }
    
    # Return 404 with clear message
    raise HTTPException(
        status_code=404,
        detail=f"Conversation '{clean_id}' not found"
    )

# Run with: uvicorn app.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=config.DEBUG)