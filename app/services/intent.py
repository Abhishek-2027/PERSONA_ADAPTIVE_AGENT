import re
from typing import Dict, Any, List, Tuple
from app.utils.logger import logger

class IntentClassifier:
    """Enhanced intent classifier with weighted keywords and better matching"""
    
    def __init__(self):
        # Intents with weighted keywords (higher weight = more important)
        self.intents = {
            "password_reset": {
                "keywords": {
                    # High weight keywords (direct indicators)
                    r'password': 3,
                    r'forgot password': 5,
                    r'reset password': 5,
                    r'can\'t login': 4,
                    r'can\'t sign in': 4,
                    r'unable to log in': 4,
                    # Medium weight keywords
                    r'login': 2,
                    r'sign in': 2,
                    r'forgot': 2,
                    r'reset': 2,
                    r'credentials': 2,
                    # Low weight keywords
                    r'access': 1,
                    r'account': 1
                },
                "description": "User needs help with password or login issues",
                "category": "account",
                "threshold": 3.0
            },
            
            "billing": {
                "keywords": {
                    # High weight
                    r'billing': 5,
                    r'invoice': 4,
                    r'refund': 4,
                    r'payment failed': 4,
                    r'charged twice': 5,
                    r'cancel subscription': 4,
                    # Medium weight
                    r'payment': 3,
                    r'subscription': 3,
                    r'upgrade': 3,
                    r'downgrade': 3,
                    r'cost': 2,
                    r'price': 2,
                    r'receipt': 3,
                    # Low weight
                    r'money': 1,
                    r'paid': 1,
                    r'bill': 2,
                    r'charge': 2
                },
                "description": "User has billing or payment questions",
                "category": "financial",
                "threshold": 3.0
            },
            
            "technical_issue": {
                "keywords": {
                    # High weight
                    r'error': 4,
                    r'exception': 4,
                    r'stack trace': 5,
                    r'crash': 4,
                    r'bug': 4,
                    r'500 error': 5,
                    r'404 error': 5,
                    r'timeout': 4,
                    r'connection pool': 5,
                    r'database error': 5,
                    r'api error': 4,
                    # Medium weight
                    r'not working': 3,
                    r'broken': 3,
                    r'fail': 3,
                    r'issue': 2,
                    r'problem': 2,
                    r'freeze': 3,
                    r'slow': 2,
                    # Low weight
                    r'api': 1,
                    r'endpoint': 1,
                    r'database': 2,
                    r'server': 1
                },
                "description": "User is experiencing technical problems",
                "category": "technical",
                "threshold": 3.0
            },
            
            "account_management": {
                "keywords": {
                    # High weight
                    r'update profile': 4,
                    r'change email': 4,
                    r'delete account': 5,
                    r'close account': 5,
                    r'change password': 4,
                    # Medium weight
                    r'settings': 3,
                    r'preferences': 3,
                    r'notification settings': 3,
                    r'security settings': 3,
                    r'privacy settings': 3,
                    # Low weight
                    r'profile': 2,
                    r'account': 1,
                    r'update': 1,
                    r'change': 1
                },
                "description": "User wants to manage account settings",
                "category": "account",
                "threshold": 3.0
            },
            
            "general_info": {
                "keywords": {
                    # High weight
                    r'how do i': 3,
                    r'how to': 3,
                    r'what is': 2,
                    r'tell me about': 2,
                    r'guide': 3,
                    r'tutorial': 3,
                    r'documentation': 4,
                    # Medium weight
                    r'help with': 2,
                    r'explain': 2,
                    r'information': 2,
                    r'learn about': 2,
                    # Low weight
                    r'where can i': 1,
                    r'when can i': 1,
                    r'what are': 1
                },
                "description": "User seeks general information or guidance",
                "category": "information",
                "threshold": 2.0
            },
            
            "feature_request": {
                "keywords": {
                    # High weight
                    r'feature request': 5,
                    r'suggestion': 4,
                    r'would be great if': 4,
                    r'can you add': 4,
                    # Medium weight
                    r'improvement': 3,
                    r'enhancement': 3,
                    r'wish list': 3,
                    r'idea': 2,
                    # Low weight
                    r'add': 1,
                    r'implement': 1,
                    r'want': 1
                },
                "description": "User is requesting a new feature or improvement",
                "category": "feedback",
                "threshold": 3.0
            },
            
            "complaint": {
                "keywords": {
                    # High weight
                    r'complaint': 5,
                    r'very disappointed': 4,
                    r'terrible service': 4,
                    r'waste of money': 4,
                    # Medium weight
                    r'frustrated': 3,
                    r'annoyed': 3,
                    r'unacceptable': 3,
                    r'ridiculous': 3,
                    # Low weight
                    r'bad': 1,
                    r'poor': 1,
                    r'not happy': 2
                },
                "description": "User is lodging a complaint",
                "category": "feedback",
                "threshold": 3.0
            }
        }
    
    def classify(self, message: str) -> Dict[str, Any]:
        """
        Classify intent from message using weighted keyword matching
        
        Args:
            message: The user's message
            
        Returns:
            Dictionary with intent, confidence, description, and category
        """
        message_lower = message.lower()
        
        # Store scores for each intent
        intent_scores: Dict[str, float] = {}
        intent_matches: Dict[str, List[str]] = {}
        
        # Calculate weighted score for each intent
        for intent, config in self.intents.items():
            total_score = 0.0
            matched_keywords = []
            
            for pattern, weight in config["keywords"].items():
                if re.search(pattern, message_lower):
                    total_score += weight
                    matched_keywords.append(pattern)
            
            if total_score > 0:
                intent_scores[intent] = total_score
                intent_matches[intent] = matched_keywords
                logger.debug(f"Intent '{intent}' score: {total_score}, matches: {matched_keywords}")
        
        # Find the best matching intent
        if intent_scores:
            # Get intent with highest score
            best_intent = max(intent_scores, key=intent_scores.get)
            best_score = intent_scores[best_intent]
            threshold = self.intents[best_intent]["threshold"]
            
            # Calculate confidence based on score and threshold
            # Confidence = min(score / (threshold * 2), 0.95)
            confidence = min(best_score / (threshold * 2), 0.95)
            
            # Check if any other intent has a close score (within 20%)
            second_best = None
            second_score = 0
            for intent, score in intent_scores.items():
                if intent != best_intent and score > second_score:
                    second_score = score
            
            # If second best is too close, reduce confidence
            if second_score > 0 and (best_score - second_score) / best_score < 0.2:
                confidence *= 0.8  # Reduce confidence if ambiguous
            
            result = {
                "intent": best_intent,
                "confidence": round(confidence, 2),
                "description": self.intents[best_intent]["description"],
                "category": self.intents[best_intent]["category"],
                "score": best_score,
                "matches": intent_matches[best_intent][:3]  # Top 3 matches
            }
            
            logger.info(f"Classified intent: {best_intent} with confidence {confidence:.2f} (score: {best_score})")
            return result
        
        # No intent matched
        logger.info("No intent matched, returning unknown")
        return {
            "intent": "unknown",
            "confidence": 0.0,
            "description": "Unable to determine user intent",
            "category": "unknown",
            "score": 0.0,
            "matches": []
        }
    
    def classify_with_details(self, message: str) -> Dict[str, Any]:
        """
        Enhanced classification with all intent scores for debugging
        
        Args:
            message: The user's message
            
        Returns:
            Dictionary with all intent scores and the best match
        """
        message_lower = message.lower()
        
        # Calculate scores for all intents
        all_scores = {}
        for intent, config in self.intents.items():
            total_score = 0.0
            matched_keywords = []
            
            for pattern, weight in config["keywords"].items():
                if re.search(pattern, message_lower):
                    total_score += weight
                    matched_keywords.append(pattern)
            
            all_scores[intent] = {
                "score": total_score,
                "matches": matched_keywords,
                "threshold": config["threshold"]
            }
        
        # Get best intent
        best_intent = max(all_scores.items(), key=lambda x: x[1]["score"]) if all_scores else ("unknown", {"score": 0})
        
        return {
            "message": message,
            "best_intent": best_intent[0] if best_intent[0] != "unknown" else "unknown",
            "best_score": best_intent[1]["score"] if best_intent[0] != "unknown" else 0,
            "all_scores": all_scores
        }

# Create a global instance
intent_classifier = IntentClassifier()

# For backward compatibility, also export the classifier function
def classify_intent(message: str) -> Dict[str, Any]:
    """Convenience function for intent classification"""
    return intent_classifier.classify(message)