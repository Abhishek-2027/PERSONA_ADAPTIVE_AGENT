#!/usr/bin/env python
"""
Diagnostic script to test API connectivity and functionality.
Run this to troubleshoot the "Expecting value: line 1 column 1 (char 0)" error.
"""

import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")
print(f"🔍 Testing API at: {API_URL}")
print("=" * 60)

# Test 1: Health check
print("\n1️⃣  Testing /health endpoint...")
try:
    response = requests.get(f"{API_URL}/health", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Health check passed: {data}")
    else:
        print(f"   ❌ Health check failed with status {response.status_code}")
except requests.exceptions.ConnectionError as e:
    print(f"   ❌ Connection error: {e}")
    print(f"      Make sure FastAPI is running at {API_URL}")
except requests.exceptions.Timeout:
    print(f"   ❌ Timeout: API is not responding")
except Exception as e:
    print(f"   ❌ Error: {type(e).__name__}: {e}")

# Test 2: Simple chat request
print("\n2️⃣  Testing /chat endpoint with a simple message...")
try:
    payload = {
        "message": "Hello, how do I reset my password?",
        "conversation_id": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "history": []
    }
    
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{API_URL}/chat",
        json=payload,
        timeout=30
    )
    
    print(f"   Status: {response.status_code}")
    print(f"   Response length: {len(response.text)} characters")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"   ✅ Chat request successful!")
            print(f"   Response: {data.get('response', 'N/A')[:200]}...")
            print(f"   Persona: {data.get('persona', {}).get('persona', 'N/A')}")
            print(f"   Intent: {data.get('intent', {}).get('intent', 'N/A')}")
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON parse error: {e}")
            print(f"   Response text (first 500 chars): {response.text[:500]}")
    else:
        print(f"   ❌ Chat request failed with status {response.status_code}")
        try:
            error_data = response.json()
            print(f"   Error: {error_data}")
        except:
            print(f"   Response: {response.text[:500]}")
            
except requests.exceptions.ConnectionError as e:
    print(f"   ❌ Connection error: {e}")
except requests.exceptions.Timeout:
    print(f"   ❌ Timeout: API took too long to respond")
except Exception as e:
    print(f"   ❌ Error: {type(e).__name__}: {e}")

# Test 3: Check if services are initialized
print("\n3️⃣  Checking service initialization...")
try:
    from app.services.persona import persona_detector
    from app.services.intent import intent_classifier
    from app.services.retriever import retriever
    from app.services.generator import generator
    from app.services.escalation import escalation_engine
    
    print("   ✅ All service modules imported successfully")
    
    # Try persona detection locally
    test_message = "I'm having trouble logging in"
    persona_result = persona_detector.detect(test_message)
    print(f"   ✅ Persona detection works: {persona_result}")
    
except ImportError as e:
    print(f"   ❌ Import error: {e}")
except Exception as e:
    print(f"   ❌ Service error: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("\n💡 Troubleshooting tips:")
print(f"   • API URL: {API_URL}")
print("   • Make sure FastAPI is running: python -m uvicorn app.main:app --reload")
print("   • Check that Ollama is running: ollama serve")
print("   • Review logs in the logs/ directory")
print("\n")
