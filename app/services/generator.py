import random
import re
import time
from typing import Dict, Any, Optional, List
from app.utils.logger import logger
from app.config import config

class ResponseGenerator:
    """Generator with Llama disabled - uses templates + KB"""
    
    def __init__(self):
        # Completely disable Llama
        self.ollama_available = False
        logger.info("🚀 Llama disabled - using template + KB mode")
        
        # Track conversation state per user
        self.conversation_state = {}
        
        # Greeting templates
        self.greetings = [
            "Hello! 👋 How can I help you today?",
            "Hi there! What can I do for you?",
            "Hey! How can I assist you?",
            "Welcome! I'm here to help. What do you need?"
        ]
        
        # Support flows for different topics
        self.support_flows = {
            'api': {
                'name': 'API Issues',
                'emoji': '🔧',
                'steps': [
                    {
                        'step': 1,
                        'instruction': "I can help with API issues. What specific API problem are you facing?",
                        'options': [
                            "500 Internal Error",
                            "Authentication errors",
                            "Rate limiting",
                            "Slow response times",
                            "Connection timeouts"
                        ]
                    },
                    {
                        'step': 2,
                        'instruction': "**For 500 errors with connection timeouts:**\nThis typically indicates:\n• Database connection pool exhaustion\n• Backend service overload\n• Network latency issues\n\n**Quick checks:**\n• Verify database is running\n• Check connection pool settings\n• Review timeout configurations",
                        'options': [
                            "How to fix connection pool?",
                            "Show configuration examples",
                            "Check server logs",
                            "This helped! 🎉"
                        ]
                    },
                    {
                        'step': 3,
                        'instruction': "**Connection Pool Configuration Examples:**\n\n**Python/SQLAlchemy:**\n```python\ncreate_engine(\n    'postgresql://user:pass@localhost/db',\n    pool_size=20,\n    max_overflow=10,\n    pool_timeout=30,\n    pool_recycle=3600\n)\n```\n\n**Node.js/PostgreSQL:**\n```javascript\nconst pool = new Pool({\n    max: 20,\n    idleTimeoutMillis: 30000,\n    connectionTimeoutMillis: 2000,\n})\n```",
                        'options': [
                            "Applied these settings",
                            "Still getting errors",
                            "Need more help",
                            "Escalate to engineering"
                        ]
                    }
                ],
                'completion': "Awesome! Your API issue should be resolved. Test it out and let me know if you need more help! 🔧",
                'escalation': "I'm escalating this to our API engineering team. They'll investigate and get back to you within 2 hours. Your ticket ID is #API-" + str(random.randint(1000, 9999)) + " 👤"
            },
            
            'technical': {
                'name': 'Technical Issues',
                'emoji': '🛠️',
                'steps': [
                    {
                        'step': 1,
                        'instruction': "I see you're having a technical issue. Let me check our documentation for you...",
                        'options': [
                            "Check API/Server issues",
                            "Check App/Website issues",
                            "Check Database issues",
                            "Other technical problem"
                        ]
                    },
                    {
                        'step': 2,
                        'instruction': "**For API 500 errors with database timeout:**\nThis usually indicates connection pool exhaustion or database overload.\n\n**Common fixes:**\n• Increase connection pool size\n• Optimize slow queries\n• Check database server resources\n• Implement connection retry logic",
                        'options': [
                            "How do I fix this?",
                            "Show me code examples",
                            "This worked! 🎉",
                            "Still need help"
                        ]
                    },
                    {
                        'step': 3,
                        'instruction': "**Solution Steps:**\n1. Check `max_connections` in database config\n2. Review connection pool settings (pool_size, overflow)\n3. Add connection timeout and retry logic\n4. Monitor database CPU/memory usage\n\nWould you like specific code examples?",
                        'options': [
                            "Yes, show code examples",
                            "I'll try these steps",
                            "Need advanced help",
                            "Escalate to engineering team"
                        ]
                    }
                ],
                'completion': "Great! Your technical issue should be resolved. Let me know if you need anything else! 🛠️",
                'escalation': "This needs engineering team attention. I'm creating a ticket and connecting you to our senior technical support. They'll contact you shortly. 👤"
            },
            
            'login': {
                'name': 'Login Issues',
                'emoji': '🔑',
                'steps': [
                    {
                        'step': 1,
                        'instruction': "Click on **'Forgot Password'** on the login page",
                        'options': [
                            "I did that, what's next?",
                            "I don't see that option",
                            "I want to try something else"
                        ]
                    },
                    {
                        'step': 2,
                        'instruction': "Check your email inbox (and spam folder) for the password reset link",
                        'options': [
                            "I got the email, what now?",
                            "I didn't get any email",
                            "The link expired"
                        ]
                    },
                    {
                        'step': 3,
                        'instruction': "Click the reset link and create a new password (minimum 8 characters)",
                        'options': [
                            "Password created, but still can't login",
                            "It says password is invalid",
                            "I'm done, thanks!"
                        ]
                    }
                ],
                'completion': "Great! Your login issue should be resolved. Is there anything else I can help with? 🎉",
                'escalation': "I understand this is frustrating. Let me connect you with a human support agent who can help further. Please wait a moment... 👤"
            },
            
            'billing': {
                'name': 'Billing Issues',
                'emoji': '💳',
                'steps': [
                    {
                        'step': 1,
                        'instruction': "Let me check your billing details. Which issue are you facing?",
                        'options': [
                            "Wrong charge amount",
                            "Duplicate payment",
                            "Want refund",
                            "Update payment method"
                        ]
                    },
                    {
                        'step': 2,
                        'instruction': "Please check your recent transactions in the Billing section",
                        'options': [
                            "I see the charge",
                            "I don't see it",
                            "Need to dispute it"
                        ]
                    }
                ],
                'completion': "Your billing issue has been noted. You'll receive an email confirmation shortly. Anything else? 💳",
                'escalation': "I'm connecting you to our billing specialists who can assist with this. Please hold on... 👤"
            },
            
            'account': {
                'name': 'Account Settings',
                'emoji': '⚙️',
                'steps': [
                    {
                        'step': 1,
                        'instruction': "What account setting would you like to update?",
                        'options': [
                            "Change email",
                            "Update profile",
                            "Delete account",
                            "Notification settings"
                        ]
                    },
                    {
                        'step': 2,
                        'instruction': "You can update this in Settings > Account. Would you like step-by-step guidance?",
                        'options': [
                            "Yes, guide me",
                            "I'll do it myself",
                            "I don't see the option"
                        ]
                    }
                ],
                'completion': "Your account has been updated successfully! ✅",
                'escalation': "This requires account verification. Let me connect you with our account specialists. 👤"
            }
        }
    
    def _get_user_state(self, conv_id: str) -> Dict:
        """Get or create user conversation state"""
        if conv_id not in self.conversation_state:
            self.conversation_state[conv_id] = {
                'current_topic': None,
                'current_step': 0,
                'awaiting_response': False,
                'history': [],
                'escalation_count': 0,
                'frustration_level': 0
            }
        return self.conversation_state[conv_id]
    
    def _detect_topic(self, message: str) -> Optional[str]:
        """Detect the main topic from user message"""
        message_lower = message.lower()
        
        # Priority detection for API issues
        if any(word in message_lower for word in ['api', '500', 'endpoint', 'database connection', 'timeout', 'stack trace']):
            return 'api'
        
        topic_keywords = {
            'technical': ['error', 'bug', 'crash', 'not working', 'broken', 'freeze', 'slow', 'glitch', 'exception'],
            'login': ['login', 'log in', 'sign in', 'signin', 'password', 'forgot', "can't access", 'account locked'],
            'billing': ['bill', 'payment', 'charge', 'refund', 'invoice', 'subscription', 'cancel', 'money'],
            'account': ['account', 'profile', 'email', 'username', 'settings', 'preferences', 'update']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return topic
        
        return None
    
    def _is_greeting(self, message: str) -> bool:
        """Check if message is a greeting"""
        greetings = ['hi', 'hello', 'hey', 'hola', 'hi there', 'hello there']
        return message.lower().strip() in greetings
    
    def _format_options(self, options: List[str]) -> str:
        """Format options as a numbered list"""
        formatted = "\n\n**What would you like to do?**\n"
        for i, option in enumerate(options, 1):
            formatted += f"{i}. {option}\n"
        return formatted
    
    def _get_flow_step_response(self, topic: str, step_num: int) -> str:
        """Get response for a specific step in the flow"""
        flow = self.support_flows.get(topic)
        if not flow:
            return None
        
        steps = flow['steps']
        if step_num <= 0 or step_num > len(steps):
            return None
        
        step = steps[step_num - 1]
        response = f"{flow['emoji']} **Step {step_num}: {step['instruction']}**"
        
        if step.get('options'):
            response += self._format_options(step['options'])
        
        return response
    
    def _check_escalation_needed(self, message: str, state: Dict) -> bool:
        """Check if conversation should be escalated to human"""
        
        message_lower = message.lower()
        
        # 1. Direct escalation keywords
        escalation_keywords = [
            'human', 'agent', 'speak to', 'talk to', 'real person',
            'supervisor', 'manager', 'complaint', 'escalate',
            'customer service', 'representative'
        ]
        
        if any(keyword in message_lower for keyword in escalation_keywords):
            state['escalation_count'] += 1
            return True
        
        # 2. High frustration detection
        frustration_indicators = [
            'frustrated', 'angry', 'annoyed', 'ridiculous', 'terrible',
            'useless', 'worst', 'horrible', 'disgusting', 'hate'
        ]
        
        if any(word in message_lower for word in frustration_indicators):
            state['frustration_level'] += 2
        
        # 3. ALL CAPS detection (shouting)
        if len(message) > 10 and sum(1 for c in message if c.isupper()) > len(message) * 0.5:
            state['frustration_level'] += 1
        
        # 4. Repetition detection (same issue multiple times)
        if len(state['history']) >= 3:
            last_three = state['history'][-3:]
            similar_count = sum(1 for msg in last_three if msg == message)
            if similar_count >= 2:
                state['escalation_count'] += 1
                return True
        
        # 5. Check frustration threshold
        if state['frustration_level'] >= 3:
            return True
        
        return False
    
    def _process_option_selection(self, message: str, state: Dict) -> Optional[str]:
        """Process user's option selection"""
        message_lower = message.lower().strip()
        topic = state['current_topic']
        step = state['current_step']
        
        flow = self.support_flows.get(topic)
        if not flow or step <= 0:
            return None
        
        steps = flow['steps']
        if step > len(steps):
            return None
        
        current_step = steps[step - 1]
        options = current_step.get('options', [])
        
        # Success phrases
        success_phrases = ['worked', 'done', 'thanks', 'helped', 'great', '🎉']
        if any(phrase in message_lower for phrase in success_phrases):
            state['current_topic'] = None
            state['current_step'] = 0
            state['awaiting_response'] = False
            return f"{flow['completion']} Is there anything else I can help with?"
        
        # Escalation phrases
        escalation_phrases = ['human', 'escalate', 'agent', 'engineering']
        if any(phrase in message_lower for phrase in escalation_phrases):
            state['current_topic'] = None
            state['current_step'] = 0
            state['awaiting_response'] = False
            return flow['escalation']
        
        # Check if user selected by number
        if message_lower.isdigit():
            choice_num = int(message_lower)
            if 1 <= choice_num <= len(options):
                selected = options[choice_num - 1]
                
                # Check if selected option is a success option
                if '🎉' in selected or 'worked' in selected.lower():
                    state['current_topic'] = None
                    state['current_step'] = 0
                    state['awaiting_response'] = False
                    return f"{flow['completion']} Is there anything else I can help with?"
                
                # Move to next step
                next_step = step + 1
                if next_step <= len(steps):
                    state['current_step'] = next_step
                    return self._get_flow_step_response(topic, next_step)
                else:
                    state['current_topic'] = None
                    state['current_step'] = 0
                    state['awaiting_response'] = False
                    return flow['completion']
            else:
                return "Please select a valid option number."
        
        return None
    
    def _format_kb_response(self, context: str, topic: str) -> Optional[str]:
        """Format knowledge base response"""
        if not context or context == "No relevant information found in knowledge base.":
            return None
        
        # Extract useful info from context
        lines = context.split('\n')
        useful = []
        for line in lines:
            if line and not line.startswith('[Source:') and len(line) > 20:
                useful.append(line)
        
        if useful:
            info = useful[0][:250]
            return f"📚 **From our knowledge base:**\n{info}...\n\nWould you like more specific information about this?"
        
        return None
    
    def generate(self, user_message: str, context: str, persona: str, intent: Dict[str, Any], 
                 conv_id: str = "default") -> str:
        """Generate response using templates + KB (Llama disabled)"""
        
        message = user_message.strip()
        
        # Get user state
        state = self._get_user_state(conv_id)
        state['history'].append(message)
        
        # Check escalation first
        if self._check_escalation_needed(message, state):
            state['current_topic'] = None
            state['current_step'] = 0
            state['awaiting_response'] = False
            if state['current_topic'] and state['current_topic'] in self.support_flows:
                return self.support_flows[state['current_topic']]['escalation']
            return "I understand you need additional assistance. Let me connect you with a human support agent. Please wait... 👤"
        
        # Handle greetings
        if self._is_greeting(message):
            state['current_topic'] = None
            state['current_step'] = 0
            state['awaiting_response'] = False
            return random.choice(self.greetings)
        
        # Check if we're in an active flow
        if state['current_topic'] and state['awaiting_response']:
            result = self._process_option_selection(message, state)
            if result:
                return result
        
        # Try KB first (this is the key part - use the knowledge base!)
        kb_response = self._format_kb_response(context, None)
        if kb_response:
            logger.info("📚 Using KB response")
            return kb_response
        
        # Detect topic
        topic = self._detect_topic(message)
        
        # If topic detected, start a new flow
        if topic and topic in self.support_flows:
            state['current_topic'] = topic
            state['current_step'] = 1
            state['awaiting_response'] = True
            return self._get_flow_step_response(topic, 1)
        
        # Default response based on persona
        persona_responses = {
            'technical': "I can help with technical issues. Could you provide more details about what's happening?",
            'frustrated': "I apologize for the inconvenience. I'm here to help resolve this. What seems to be the problem?",
            'business': "I understand this is important. How can I assist you with your business needs today?",
            'general': "I'm here to help! What do you need assistance with?"
        }
        
        return persona_responses.get(persona, "How can I help you today?")

# Global instance
generator = ResponseGenerator()