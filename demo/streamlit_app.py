import streamlit as st
import requests
import json
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="Persona-Adaptive Customer Support Demo",
    page_icon="🤖",
    layout="wide"
)

# API endpoint
API_URL = "http://localhost:8000"

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
    
    ### Sample Messages to Try:
    
    **Technical Expert:**
    > "I'm getting a 500 error when calling your API endpoint. The stack trace shows a database connection timeout. Can you check the connection pool settings?"
    
    **Frustrated User:**
    > "YOUR APP IS NOT WORKING!!! I've tried logging in 5 times and it keeps saying error. This is ridiculous!!"
    
    **Business Executive:**
    > "What's the ROI timeline for implementing your solution? We need to present to the board next quarter and need concrete numbers."
    
    **General User:**
    > "How do I reset my password? I forgot it and can't log in."
    """)
    
    st.markdown("---")
    
    # Health check
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            st.success("✅ Connected to API")
        else:
            st.error("❌ API connection failed")
    except:
        st.error("❌ API not reachable. Make sure FastAPI is running.")
    
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
                    # Call API
                    response = requests.post(
                        f"{API_URL}/chat",
                        json={
                            "message": prompt,
                            "conversation_id": st.session_state.conversation_id,
                            "history": [m["content"] for m in st.session_state.messages[-5:]]
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Display response
                        st.markdown(data["response"])
                        
                        # Show escalation warning if needed
                        if data["escalated"]:
                            st.warning(f"⚠️ **Escalation Needed**: {data['escalation_reason']}")
                        
                        # Show details in expander
                        with st.expander("🔍 View Analysis"):
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.metric("Persona", data["persona"]["persona"].title())
                                st.metric("Intent", data["intent"]["intent"].replace("_", " ").title())
                            with col_b:
                                st.metric("Confidence", f"{data['confidence']:.2%}")
                                st.metric("Escalated", "Yes" if data["escalated"] else "No")
                            
                            st.subheader("Full Context")
                            st.json({
                                "persona": data["persona"],
                                "intent": data["intent"],
                                "context_summary": data["context_summary"]
                            })
                        
                        # Add to session
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": data["response"],
                            "metadata": {
                                "persona": data["persona"]["persona"],
                                "intent": data["intent"]["intent"],
                                "confidence": data["confidence"],
                                "escalated": data["escalated"]
                            }
                        })
                        
                    else:
                        st.error(f"API Error: {response.status_code}")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")

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
            st.markdown(f"### {persona_colors.get(meta['persona'], '⚪')} Persona: {meta['persona'].title()}")
            
            # Intent
            st.markdown(f"### 🎯 Intent: {meta['intent'].replace('_', ' ').title()}")
            
            # Confidence
            st.progress(meta['confidence'], text=f"Confidence: {meta['confidence']:.2%}")
            
            # Escalation status
            if meta['escalated']:
                st.error("🚨 **Escalated to Human**")
            else:
                st.success("✅ **AI Handling**")
            
            # Quick suggestions based on persona
            st.markdown("---")
            st.markdown("### 💡 Suggested Responses")
            
            if meta['persona'] == "technical":
                st.info("• Provide specific error codes\n• Include technical documentation links\n• Suggest configuration changes")
            elif meta['persona'] == "frustrated":
                st.info("• Apologize first\n• Use simple steps\n• Offer immediate assistance")
            elif meta['persona'] == "business":
                st.info("• Focus on outcomes\n• Be concise\n• Highlight ROI/value")
            else:
                st.info("• Be friendly and clear\n• Provide standard help\n• Ask clarifying questions")
    else:
        st.info("Send a message to see context analysis")

# Footer
st.markdown("---")
st.markdown(f"**Conversation ID:** `{st.session_state.conversation_id}`")