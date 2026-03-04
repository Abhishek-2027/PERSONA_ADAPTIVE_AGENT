import streamlit as st
import requests
from datetime import datetime

# ============================================
# BACKEND CONFIGURATION
# ============================================

# CHANGE THIS TO YOUR RENDER BACKEND URL
BACKEND_URL = "https://your-backend-name.onrender.com/chat"


# ============================================
# PAGE CONFIG
# ============================================

st.set_page_config(
    page_title="Persona Adaptive Support Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Persona-Adaptive Customer Support Agent")
st.markdown("---")


# ============================================
# SESSION STATE
# ============================================

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = datetime.now().strftime("%Y%m%d%H%M%S")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "escalated" not in st.session_state:
    st.session_state.escalated = False


# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.header("ℹ️ About")

    st.markdown("""
This demo shows a **persona-adaptive customer support AI agent**.

### Features
- 🔍 Persona Detection
- 🎯 Intent Classification
- 📚 Knowledge Base Retrieval
- 🗣 Adaptive Responses
- ⚠️ Human Escalation

### Example Queries

**Technical**
> I'm getting a 500 error when calling your API endpoint.

**Frustrated**
> YOUR APP IS NOT WORKING!!!

**Business**
> What's the ROI timeline for implementing your solution?

**General**
> How do I reset my password?
""")

    st.markdown("---")

    if st.session_state.escalated:
        st.error("🚨 Escalated to Human Agent")

    if st.button("🔄 New Conversation"):
        st.session_state.conversation_id = datetime.now().strftime("%Y%m%d%H%M%S")
        st.session_state.messages = []
        st.session_state.escalated = False
        st.rerun()


# ============================================
# MAIN LAYOUT
# ============================================

col1, col2 = st.columns([2, 1])

# ============================================
# CHAT PANEL
# ============================================

with col1:

    # Show chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input(
        "Type your message...",
        disabled=st.session_state.escalated
    )

    if prompt and not st.session_state.escalated:

        # Show user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        # Call backend
        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:

                    response = requests.post(
                        BACKEND_URL,
                        json={
                            "message": prompt,
                            "conversation_id": st.session_state.conversation_id,
                            "history": []
                        },
                        timeout=60
                    )

                    data = response.json()

                    response_text = data.get("response", "No response received.")
                    persona = data.get("persona", {})
                    intent = data.get("intent", {})
                    escalated = data.get("escalated", False)

                    # show response
                    st.markdown(response_text)

                    # store assistant message
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_text
                    })

                    if escalated:
                        st.session_state.escalated = True

                except Exception as e:

                    error_msg = f"⚠️ Backend connection error: {e}"

                    st.markdown(error_msg)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })


# ============================================
# CONTEXT PANEL
# ============================================

with col2:

    st.header("📊 AI Context")

    if st.session_state.escalated:

        st.error("🚨 Conversation Escalated")
        st.info("A human support agent will assist shortly.")

    elif st.session_state.messages:

        last_message = st.session_state.messages[-1]

        if last_message["role"] == "assistant":

            st.info("Latest Response")

            st.markdown(last_message["content"][:200] + "...")

            st.markdown("---")

            st.markdown("### 💡 Try Asking")

            st.markdown("""
🔑 Login problems  
🔧 API errors  
💳 Billing questions  
🛠 Technical support
""")

            st.markdown("---")

            st.markdown("### ⚠️ Need Human Help?")

            st.markdown("""
Type:

- **talk to human**
- **agent**
- **escalate**
""")


# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown(f"Conversation ID: `{st.session_state.conversation_id}`")
