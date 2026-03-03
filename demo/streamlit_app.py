import streamlit as st
import requests
import json
from datetime import datetime
import time
import os

# ============================================
# CONFIGURATION
# ============================================
# Detect if running on Streamlit Cloud
IS_CLOUD = os.environ.get("IS_DEPLOYED", "false").lower() == "true" or \
           "STREAMLIT_SHARING" in os.environ or \
           "STREAMLIT_CLOUD" in os.environ or \
           "STREAMLIT_RUNTIME" in os.environ

# API Configuration
if IS_CLOUD:
    # In cloud, try to get from secrets, otherwise use mock mode
    API_URL = st.secrets.get("API_URL", None)
    USE_MOCK = API_URL is None
    if USE_MOCK:
        st.warning("⚠️ Running in demo mode - using mock responses")
else:
    # Local development
    API_URL = "http://localhost:8000"
    USE_MOCK = False

# ============================================
# MOCK RESPONSES FOR DEMO MODE
# ============================================
def get_mock_response(message, conv_id):
    """Generate mock responses when backend is not available"""
    message_lower = message.lower()
    
    # Greetings
    if message_lower in ['hi', 'hello', 'hey', 'hola']:
        return {
            "response": "Hello! 👋 How can I help you today?",
            "persona": "general",
            "intent": "greeting",
            "confidence": 0.95,
            "escalated": False,
            "escalation_reason": "",
            "context_summary": "Persona: general, Intent: greeting"
        }
    
    # Technical/API issues
    if any(word in message_lower for word in ['api', '500', 'error', 'timeout', 'database']):
        return {
            "response": """🔧 **Technical Support**

I see you're having an API issue. Here's what might help:

**For 500 errors with connection timeouts:**
• Check database connection pool settings
• Increase pool_size and max_overflow
• Verify database server resources
• Review timeout configurations

Would you like me to guide you through specific configuration changes?""",
            "persona": "technical",
            "intent": "technical_issue",
            "confidence": 0.85,
            "escalated": False,
            "escalation_reason": "",
            "context_summary": "Persona: technical, Intent: technical_issue"
        }
    
    # Login issues
    if any(word in message_lower for word in ['login', 'password', 'sign in', 'account locked']):
        return {
            "response": """🔑 **Login Support**

I can help you with login issues! Here are the steps:

1. Click **'Forgot Password'** on the login page
2. Check your email for reset link (check spam folder)
3. Create a new password (min 8 characters)
4. Try logging in again

Need help with any specific step?""",
            "persona": "general",
            "intent": "password_reset",
            "confidence": 0.90,
            "escalated": False,
            "escalation_reason": "",
            "context_summary": "Persona: general, Intent: password_reset"
        }
    
    # Billing questions
    if any(word in message_lower for word in ['bill', 'payment', 'charge', 'refund']):
        return {
            "response": """💳 **Billing Support**

For billing questions:

• Check your invoices in the Billing section
• View payment history and receipts
• Update payment methods in Settings
• Contact billing@company.com for disputes

What specific billing issue are you facing?""",
            "persona": "general",
            "intent": "billing",
            "confidence": 0.88,
            "escalated": False,
            "escalation_reason": "",
            "context_summary": "Persona: general, Intent: billing"
        }
    
    # Frustrated user
    if any(word in message_lower for word in ['frustrated', 'angry', 'not working', 'broken', 'stupid']):
        return {
            "response": """I sincerely apologize for the frustration this has caused. 😟

I'm here to help resolve this for you. Could you please tell me more about what's happening? I'll do my best to find a solution quickly.

• What were you trying to do?
• What error message did you see?
• When did this start happening?""",
            "persona": "frustrated",
            "intent": "complaint",
            "confidence": 0.75,
            "escalated": True,
            "escalation_reason": "User appears frustrated",
            "context_summary": "Persona: frustrated, Intent: complaint"
        }
    
    # Thanks
    if any(word in message_lower for word in ['thanks', 'thank you', 'thx']):
        return {
            "response": "You're welcome! 😊 Is there anything else I can help you with?",
            "persona": "general",
            "intent": "general_info",
            "confidence": 0.95,
            "escalated": False,
            "escalation_reason": "",
            "context_summary": "Persona: general, Intent: general_info"
        }
    
    # Bye
    if any(word in message_lower for word in ['bye', 'goodbye', 'see you']):
        return {
            "response": "Goodbye! 👋 Have a great day! Feel free to come back if you need more help.",
            "persona": "general",
            "intent": "general_info",
            "confidence": 0.95,
            "escalated": False,
            "escalation_reason": "",
            "context_summary": "Persona: general, Intent: general_info"
        }
    
    # Default response
    return {
        "response": "I'm here to help! You can ask me about:\n\n• 🔑 Login issues\n• 🔧 API problems\n• 💳 Billing questions\n• 🛠️ Technical support\n\nWhat would you like assistance with?",
        "persona": "general",
        "intent": "general_info",
        "confidence": 0.70,
        "escalated": False,
        "escalation_reason": "",
        "context_summary": "Persona: general, Intent: general_info"
    }

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Persona-Adaptive Customer Support Demo",
    page_icon="🤖",
    layout="wide"
)

# Title
st.title("🤖 Persona-Adaptive Customer Support Agent")
st.markdown("---")

# Initialize session state
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = datetime.now().strftime("%Y%m%d%H%M%S")
if "messages" not in st.session_state:
    st.session_state.messages = []
if "context" not in st.session_state:
    st.session_state.context = []

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This demo shows a **persona-adaptive customer support agent** that:
    
    - 🔍 **Detects** user persona (technical, frustrated, business, general)
    - 🎯 **Classifies** user intent
    - 📚 **Retrieves** relevant knowledge
    - 🗣️ **Adapts** response tone
    - ⚠️ **Escalates** to human when needed
    """)
    
    # Show mode indicator
    if USE_MOCK:
        st.info("📢 **Demo Mode**\n\nRunning without backend. Responses are simulated.")
    else:
        # Health check for local mode
        try:
            response = requests.get(f"{API_URL}/health", timeout=2)
            if response.status_code == 200:
                st.success(f"✅ Connected to API at {API_URL}")
            else:
                st.error("❌ API connection failed")
        except:
            st.error(f"❌ Cannot reach API at {API_URL}")
    
    st.markdown("---")
    
    st.markdown("### 📝 Sample Messages")
    st.markdown("""
    **Technical:**
    > "I'm getting a 500 error when calling your API endpoint. The stack trace shows a database connection timeout."
    
    **Login Issue:**
    > "How do I reset my password? I forgot it and can't log in."
    
    **Billing:**
    > "I was charged twice for my subscription last month."
    
    **Frustrated:**
    > "YOUR APP IS NOT WORKING!!! This is ridiculous!!"
    """)
    
    st.markdown("---")
    
    # Reset button
    if st.button("🔄 New Conversation"):
        st.session_state.conversation_id = datetime.now().strftime("%Y%m%d%H%M%S")
        st.session_state.messages = []
        st.session_state.context = []
        st.rerun()

# Main chat area
col1, col2 = st.columns([2, 1])

with col1:
    # Display chat messages
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "metadata" in message:
                    with st.expander("🔍 Details"):
                        st.json(message["metadata"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Show assistant thinking
        with st.chat_message("assistant"):
            with st.spinner("Analyzing and generating response..."):
                try:
                    if USE_MOCK:
                        # Use mock responses
                        time.sleep(1)  # Simulate thinking
                        data = get_mock_response(prompt, st.session_state.conversation_id)
                    else:
                        # Call actual API
                        response = requests.post(
                            f"{API_URL}/chat",
                            json={
                                "message": prompt,
                                "conversation_id": st.session_state.conversation_id,
                                "history": [m["content"] for m in st.session_state.messages[-5:]]
                            },
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                        else:
                            st.error(f"API Error: {response.status_code}")
                            # Fallback to mock on error
                            data = get_mock_response(prompt, st.session_state.conversation_id)
                    
                    # Display response
                    st.markdown(data["response"])
                    
                    # Show escalation warning if needed
                    if data.get("escalated", False):
                        st.warning(f"⚠️ **Escalation Needed**: {data.get('escalation_reason', 'Needs human attention')}")
                    
                    # Show details in expander
                    with st.expander("🔍 View Analysis"):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("Persona", data.get("persona", "unknown").title() if isinstance(data.get("persona"), str) else data.get("persona", {}).get("persona", "unknown").title())
                            intent = data.get("intent", "unknown")
                            if isinstance(intent, dict):
                                intent = intent.get("intent", "unknown")
                            st.metric("Intent", intent.replace("_", " ").title())
                        with col_b:
                            st.metric("Confidence", f"{data.get('confidence', 0):.2%}")
                            st.metric("Escalated", "Yes" if data.get("escalated", False) else "No")
                        
                        st.subheader("Full Context")
                        st.json(data)
                    
                    # Add to session
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": data["response"],
                        "metadata": {
                            "persona": data.get("persona", "general") if isinstance(data.get("persona"), str) else data.get("persona", {}).get("persona", "general"),
                            "intent": intent if 'intent' in locals() else "unknown",
                            "confidence": data.get("confidence", 0),
                            "escalated": data.get("escalated", False)
                        }
                    })
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    # Final fallback
                    st.markdown("I'm here to help! What would you like assistance with?")

with col2:
    # Context panel
    st.header("📊 Current Context")
    
    if st.session_state.messages:
        last_message = st.session_state.messages[-1]
        if last_message["role"] == "assistant" and "metadata" in last_message:
            meta = last_message["metadata"]
            
            # Persona badge
            persona_colors = {
                "technical": "🔵",
                "frustrated": "🔴",
                "business": "🟢",
                "general": "⚪"
            }
            st.markdown(f"### {persona_colors.get(meta.get('persona', 'general'), '⚪')} Persona: {meta.get('persona', 'General').title()}")
            
            # Intent
            st.markdown(f"### 🎯 Intent: {meta.get('intent', 'unknown').replace('_', ' ').title()}")
            
            # Confidence
            st.progress(meta.get('confidence', 0), text=f"Confidence: {meta.get('confidence', 0):.2%}")
            
            # Escalation status
            if meta.get('escalated', False):
                st.error("🚨 **Escalated to Human**")
            else:
                st.success("✅ **AI Handling**")
            
            # Quick suggestions based on persona
            st.markdown("---")
            st.markdown("### 💡 Suggested Responses")
            
            persona = meta.get('persona', 'general')
            if persona == "technical":
                st.info("• Provide specific error codes\n• Include technical documentation links\n• Suggest configuration changes")
            elif persona == "frustrated":
                st.info("• Apologize first\n• Use simple steps\n• Offer immediate assistance")
            elif persona == "business":
                st.info("• Focus on outcomes\n• Be concise\n• Highlight ROI/value")
            else:
                st.info("• Be friendly and clear\n• Provide standard help\n• Ask clarifying questions")
    else:
        st.info("Send a message to see context analysis")

# Footer
st.markdown("---")
col_left, col_right = st.columns(2)
with col_left:
    st.markdown(f"**Conversation ID:** `{st.session_state.conversation_id}`")
with col_right:
    if USE_MOCK:
        st.markdown("**Mode:** 🎭 Demo (Mock Responses)")
    else:
        st.markdown(f"**API:** `{API_URL}`")
