#!/bin/bash
# Deployment script for Streamlit Cloud

# Install dependencies
pip install -r requirements.txt

# Run Streamlit app from demo directory
streamlit run demo/streamlit_app.py
