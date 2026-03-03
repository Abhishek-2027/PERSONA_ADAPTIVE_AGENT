import re
from typing import Dict, Any, List, Tuple
from app.utils.logger import logger
from app.config import config

class EscalationEngine:
    """Determine if conversation should be escalated to human agent"""
    
    def __init__(self):
        self.confidence_threshold = config.ESCALATION_CONFIDENCE_THRESHOLD
        
        # Keywords that trigger escalation
        self.escalation_keywords = [
            r'speak to human', r'talk to agent', r'real person', r'human agent',
            r'supervisor', r'manager', r'escalate', r'complaint', r'lawsuit',
            r'legal', r'attorney', r'lawyer', r'sue', r'compensation'
        ]
        
        # Sentiment indicators
        self.negative_sentiment = [
            r'terrible', r'awful', r'worst', r'hate', r'disgusting',
            r'unacceptable', r'ridiculous', r'useless', r'hopeless'
        ]
    
    def should_escalate(
        self,
        message: str,
        persona: str,
        intent: Dict[str, Any],
        confidence: float,
        history: List[str] = None
    ) -> Tuple[bool, str]:
        """Determine if escalation is needed"""
        
        message_lower = message.lower()
        history = history or []
        
        # Check for direct escalation requests
        for keyword in self.escalation_keywords:
            if re.search(keyword, message_lower):
                reason = f"User requested human agent (matched: {keyword})"
                logger.info(f"Escalation triggered: {reason}")
                return True, reason
        
        # Check for strong negative sentiment
        for keyword in self.negative_sentiment:
            if re.search(keyword, message_lower):
                reason = f"Strong negative sentiment detected (matched: {keyword})"
                logger.info(f"Escalation triggered: {reason}")
                return True, reason
        
        # Check confidence threshold
        if confidence < self.confidence_threshold:
            reason = f"Low confidence in response ({confidence:.2f} < {self.confidence_threshold})"
            logger.info(f"Escalation triggered: {reason}")
            return True, reason
        
        # Check for frustration indicators
        if persona == "frustrated" and confidence < 0.7:
            reason = "Frustrated user with low confidence response"
            logger.info(f"Escalation triggered: {reason}")
            return True, reason
        
        # Check repetition in history
        if len(history) >= 3:
            # Check if current message is similar to previous ones
            recent_messages = history[-3:]
            for prev_msg in recent_messages:
                if prev_msg and message and prev_msg.lower() == message.lower():
                    reason = "User repeating same issue multiple times"
                    logger.info(f"Escalation triggered: {reason}")
                    return True, reason
        
        # Check for ALL CAPS (shouting)
        if len(message) > 20 and sum(1 for c in message if c.isupper()) > len(message) * 0.6:
            reason = "User shouting (ALL CAPS detected)"
            logger.info(f"Escalation triggered: {reason}")
            return True, reason
        
        return False, ""
    
    def prepare_context(self, message: str, persona: str, intent: Dict[str, Any], 
                        response: str, history: List[str]) -> Dict[str, Any]:
        """Prepare context for human agent handoff"""
        
        context = {
            "user_message": message,
            "detected_persona": persona,
            "detected_intent": intent,
            "ai_response": response,
            "conversation_history": history[-5:] if history else [],
            "priority": self._calculate_priority(persona, intent)
        }
        
        return context
    
    def _calculate_priority(self, persona: str, intent: Dict[str, Any]) -> str:
        """Calculate priority for human agent"""
        
        # High priority cases
        if persona == "frustrated":
            if intent.get("category") in ["financial", "technical"]:
                return "high"
            return "medium"
        
        # Medium priority
        if intent.get("category") == "financial":
            return "medium"
        
        # Low priority
        return "low"

# Create a global instance
escalation_engine = EscalationEngine()