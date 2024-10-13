import streamlit as st
import requests
import json
from datetime import datetime

# Set up Gemini API key (replace with your actual key)
GEMINI_API_KEY = "YOUR_API_KEY"

# Function to generate response using Gemini model
def generate_response(prompt):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": "You are a knowledgeable tax advisor specializing in US tax law. Provide accurate and helpful information about tax deductions, credits, and regulations. Only answer tax-related questions. Here's the question: " + prompt
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()
        
        if 'candidates' in response_json:
            return response_json['candidates'][0]['content']['parts'][0]['text']
        else:
            return "Sorry, I couldn't generate a response."
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Function to save conversation to local file
def save_conversation(conversation):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"tax_conversation_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(conversation, f, indent=2)
    return filename

# Streamlit UI
st.title("Deloitte Tax Advisor")
st.write("Ask tax-related questions and get expert advice.")

# Initialize session state for conversation history
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

# User input
user_input = st.text_input("Enter your tax-related question:")

if st.button("Submit"):
    if user_input:
        # Generate response
        response = generate_response(user_input)
        
        # Add to conversation history
        st.session_state.conversation.append({"user": user_input, "assistant": response})
        
        # Display response
        st.write("Response:")
        st.write(response)
    else:
        st.warning("Please enter a question.")

# Display conversation history
if st.session_state.conversation:
    st.write("Conversation History:")
    for entry in st.session_state.conversation:
        st.write(f"User: {entry['user']}")
        st.write(f"Assistant: {entry['assistant']}")
        st.write("---")

# Save conversation button
if st.button("Save Conversation"):
    if st.session_state.conversation:
        filename = save_conversation(st.session_state.conversation)
        st.success(f"Conversation saved to {filename}")
    else:
        st.warning("No conversation to save.")

# Clear conversation button
if st.button("Clear Conversation"):
    st.session_state.conversation = []
    st.success("Conversation cleared.")