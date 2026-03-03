import re
from typing import Dict, Any
from app.utils.logger import logger

class PersonaDetector:
    """Detect user persona from message"""
    
    def __init__(self):
        self.personas = {
            "technical": {
                "keywords": [
                    r'api', r'code', r'server', r'database', r'error log', r'debug',
                    r'endpoint', r'json', r'xml', r'http', r'status code', r'stack trace',
                    r'git', r'deploy', r'configuration', r'syntax', r'variable', r'function',
                    r'array', r'object', r'loop', r'conditional', r'class', r'method'
                ],
                "description": "Technical expert user looking for detailed technical information"
            },
            "frustrated": {
                "keywords": [
                    r'stupid', r'broken', r'not working', r'frustrated', r'angry',
                    r'hate', r'!!!', r'\?{2,}', r'useless', r'waste', r'terrible',
                    r'fed up', r'annoying', r'ridiculous', r'unacceptable', r'worst',
                    r'awful', r'horrible', r'disgusting'
                ],
                "description": "Frustrated user needing empathy and simple solutions"
            },
            "business": {
                "keywords": [
                    r'budget', r'roi', r'quarter', r'deadline', r'cost', r'profit',
                    r'team', r'project', r'manager', r'report', r'revenue', r'forecast',
                    r'strategy', r'business', r'executive', r'meeting', r'presentation',
                    r'kpi', r'metric', r'growth', r'revenue', r'client', r'stakeholder'
                ],
                "description": "Business executive focused on outcomes and efficiency"
            },
            "general": {
                "keywords": [],
                "description": "General user needing standard support"
            }
        }
    
    def detect(self, message: str) -> Dict[str, Any]:
        """Detect persona from message"""
        message_lower = message.lower()
        
        # Check each persona
        for persona, config in self.personas.items():
            if persona == "general":
                continue
            
            for keyword in config["keywords"]:
                if re.search(keyword, message_lower):
                    logger.info(f"Detected {persona} persona from keyword: {keyword}")
                    return {
                        "persona": persona,
                        "confidence": 0.8,
                        "description": config["description"]
                    }
        
        # Check for ALL CAPS (frustration indicator)
        if len(message) > 10 and sum(1 for c in message if c.isupper()) > len(message) * 0.5:
            logger.info("Detected frustrated persona from ALL CAPS")
            return {
                "persona": "frustrated",
                "confidence": 0.7,
                "description": self.personas["frustrated"]["description"]
            }
        
        # Default to general
        logger.info("Detected general persona")
        return {
            "persona": "general",
            "confidence": 1.0,
            "description": self.personas["general"]["description"]
        }

# Create a global instance
persona_detector = PersonaDetector()