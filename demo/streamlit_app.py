import streamlit as st
import requests
import json
from datetime import datetime
import time
import os

# ============================================
# FOOLPROOF CLOUD DETECTION
# ============================================
# Multiple ways to detect if we're on Streamlit Cloud
IS_CLOUD = any([
    os.environ.get("IS_DEPLOYED", "").lower() == "true",
    os.environ.get("STREAMLIT_SHARING", "") != "",
    os.environ.get("STREAMLIT_CLOUD", "") != "",
    os.environ.get("STREAMLIT_RUNTIME", "") != "",
    "share.streamlit.io" in str(os.environ.get("HOSTNAME", "")),
    # If we can't connect to localhost, assume we're in cloud
])

# FORCE MOCK MODE FOR STREAMLIT CLOUD - ALWAYS USE THIS FOR NOW
# This is the safest approach - uncomment if above detection fails
# IS_CLOUD = True

# API Configuration - FORCE MOCK MODE for cloud
if IS_CLOUD:
    # In cloud, ALWAYS use mock mode to avoid connection errors
    USE_MOCK = True
    API_URL = None
    st.info("🎭 Running in demo mode with simulated responses")
else:
    # Local development - try to connect to localhost
    API_URL = "http://localhost:8000"
    USE_MOCK = False
    try:
        # Test connection
        requests.get(f"{API_URL}/health", timeout=1)
    except:
        st.warning("⚠️ Local API not reachable - falling back to demo mode")
        USE_MOCK = True
        API_URL = None

# ============================================
# MOCK RESPONSES (Enhanced)
# ============================================
def get_mock_response(message, conv_id):
    """Generate realistic mock responses"""
    message_lower = message.lower().strip()
    
    # Greetings
    if message_lower in ['hi', 'hello', 'hey', 'hola', 'hello there', 'hi there']:
        return {
            "response": "Hello! 👋 How can I help you today? You can ask about login issues, API problems, billing questions, or technical support.",
            "persona": "general",
            "intent": "greeting",
            "confidence": 0.95,
            "escalated": False,
            "escalation_reason": "",
            "context_summary": "Persona: general, Intent: greeting"
        }
    
    # How are you?
    if 'how are you' in message_lower:
        return {
            "response": "I'm doing great, thanks for asking! 😊 How can I assist you today?",
            "persona": "general",
            "intent": "general_info",
            "confidence": 0.90,
            "escalated": False,
            "escalation_reason": "",
            "context_summary": "Persona: general, Intent: general_info"
        }
    
    # Technical/API issues (EXPANDED)
    if any(word in message_lower for word in ['api', '500', 'error', 'timeout', 'database', 'connection', 'endpoint']):
        return {
            "response": """🔧 **Technical Support - API Issue Detected**

I can help you with that API error! Here's what might be happening:

**For 500 errors with connection timeouts:**
• **Database connection pool** might be exhausted
• **Connection settings** may need adjustment
• **Server resources** could be under stress

**Recommended solutions:**
1. Increase connection pool size (pool_size=20, max_overflow=10)
2. Add connection timeout settings (timeout=30)
3. Implement retry logic with exponential backoff

Would you like me to guide you through the configuration changes? I can show you code examples for Python, Node.js, or Java.""",
            "persona": "technical",
            "intent": "technical_issue",
            "confidence": 0.88,
            "escalated": False,
            "escalation_reason": "",
            "context_summary": "Persona: technical, Intent: technical_issue"
        }
    
    # Login issues (EXPANDED)
    if any(word in message_lower for word in ['login', 'password', 'sign in', 'account locked', 'forgot', 'can\'t log']):
        return {
            "response": """🔑 **Login Support - Let's Get You Back In!**

Here's a step-by-step guide to resolve your login issue:

**Step 1: Reset Your Password**
• Click the **"Forgot Password"** link on the login page
• Enter your registered email address
• Check your inbox (and spam folder) for the reset link

**Step 2: Create New Password**
• Click the reset link (valid for 24 hours)
• Create a strong password (min 8 characters with numbers & letters)
• Confirm your new password

**Step 3: Try Logging In**
• Use your email and new password
• If still having issues, clear your browser cache

Need help with any specific step? I'm here to guide you through! 🔐""",
            "persona": "general",
            "intent": "password_reset",
            "confidence": 0.92,
            "escalated": False,
            "escalation_reason": "",
            "context_summary": "Persona: general, Intent: password_reset"
        }
    
    # Billing questions (EXPANDED)
    if any(word in message_lower for word in ['bill', 'payment', 'charge', 'refund', 'invoice', 'subscription']):
        return {
            "response": """💳 **Billing Support Center**

I can help you with your billing question. Here's what you can do:

**View Your Billing Details:**
• Check recent invoices in the **Billing Section** of your dashboard
• View payment history and transaction status
• Download receipts for your records

**Common Billing Actions:**
• Update payment method in Settings
• Request refund (within 30 days of purchase)
• Change subscription plan
• Report unauthorized charges

**For immediate billing support:**
Contact our billing team at **billing@company.com** with your account details.

What specific billing issue are you facing? I can help you resolve it! 💳""",
            "persona": "general",
            "intent": "billing",
            "confidence": 0.87,
            "escalated": False,
            "escalation_reason": "",
            "context_summary": "Persona: general, Intent: billing"
        }
    
    # Frustrated user (EXPANDED)
    if any(word in message_lower for word in ['frustrated', 'angry', 'not working', 'broken', 'stupid', 'terrible', 'awful', '!!!']):
        return {
            "response": """😟 I sincerely apologize for the frustration this has caused you.

I'm here to help make things right. Let's work together to resolve this:

**First, let me understand the issue better:**
• What were you trying to do when this happened?
• What error message did you see (if any)?
• When did this issue start occurring?

**I can help you with:**
• Immediate troubleshooting steps
• Escalating to a human support agent
• Creating a support ticket with priority handling

Please tell me more about what's happening, and I'll do everything I can to help! 🙏""",
            "persona": "frustrated",
            "intent": "complaint",
            "confidence": 0.78,
            "escalated": True,
            "escalation_reason": "User frustration detected - offering escalation",
            "context_summary": "Persona: frustrated, Intent: complaint"
        }
    
    # Thanks
    if any(word in message_lower for word in ['thanks', 'thank you', 'thx', 'appreciate']):
        return {
            "response": "You're very welcome! 😊 Is there anything else I can help you with today?",
            "persona": "general",
            "intent": "general_info",
            "confidence": 0.98,
            "escalated": False,
            "escalation_reason": "",
            "context_summary": "Persona: general, Intent: general_info"
        }
    
    # Bye
    if any(word in message_lower for word in ['bye', 'goodbye', 'see you', 'cya', 'take care']):
        return {
            "response": "Goodbye! 👋 Have a wonderful day! Feel free to come back anytime if you need more help.",
            "persona": "general",
            "intent": "general_info",
            "confidence": 0.98,
            "escalated": False,
            "escalation_reason": "",
            "context_summary": "Persona: general, Intent: general_info"
        }
    
    # Help
    if message_lower == 'help' or 'what can you do' in message_lower:
        return {
            "response": """🎯 **I can help you with:**

🔑 **Login Issues**
• Password reset
• Account access
• 2FA problems

🔧 **API & Technical Issues**
• Error troubleshooting
• Connection problems
• Configuration help

💳 **Billing Questions**
• Payment issues
• Refunds
• Subscription management

🛠️ **General Support**
• Account settings
• Feature questions
• Documentation

**Just tell me what you need help with!** 😊""",
            "persona": "general",
            "intent": "help",
            "confidence": 0.96,
            "escalated": False,
            "escalation_reason": "",
            "context_summary": "Persona: general, Intent: help"
        }
    
    # Default response
    return {
        "response": """I'm here to help! You can ask me about:

• 🔑 **Login issues** - Password reset, account access
• 🔧 **API problems** - Errors, timeouts, configuration
• 💳 **Billing questions** - Payments, refunds, invoices
• 🛠️ **Technical support** - Bugs, errors, troubleshooting

What would you like assistance with today? 😊""",
        "persona": "general",
        "intent": "general_info",
        "confidence": 0.75,
        "escalated": False,
        "escalation_reason": "",
        "context_summary": "Persona: general, Intent: general_info"
    }

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="AI Customer Support Assistant",
    page_icon="🤖",
    layout="wide"
)

# Title
st.title("🤖 AI Customer Support Assistant")
st.markdown("---")

# Initialize session state
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = datetime.now().strftime("%Y%m%d%H%M%S")
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This AI assistant helps with:
    - 🔑 Login issues
    - 🔧 API problems  
    - 💳 Billing questions
    - 🛠️ Technical support
    """)
    
    # Show mode clearly
    if USE_MOCK:
        st.success("✅ **Demo Mode Active**")
        st.info("Running with simulated responses - no backend needed!")
    else:
        if API_URL:
            st.caption(f"Connected to: `{API_URL}`")
    
    st.markdown("---")
    
    st.markdown("### 📝 Try These Examples")
    st.markdown("""
    - "Hi"
    - "I can't login"
    - "API 500 error"
    - "Billing question"
    - "This is frustrating"
    - "Thanks"
    - "Bye"
    """)
    
    st.markdown("---")
    
    # Reset button
    if st.button("🔄 New Conversation", use_container_width=True):
        st.session_state.conversation_id = datetime.now().strftime("%Y%m%d%H%M%S")
        st.session_state.messages = []
        st.rerun()

# Main chat area
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            time.sleep(0.8)  # Small delay for realism
            
            # Get mock response
            data = get_mock_response(prompt, st.session_state.conversation_id)
            
            # Display response
            st.markdown(data["response"])
            
            # Show optional details
            if data.get("escalated"):
                st.warning(f"🚨 {data.get('escalation_reason', 'Escalation needed')}")
            
            # Add to session
            st.session_state.messages.append({
                "role": "assistant",
                "content": data["response"]
            })

# Footer
st.markdown("---")
st.caption(f"Conversation ID: `{st.session_state.conversation_id}` | Mode: {'🎭 Demo' if USE_MOCK else '🔌 Live API'}")
