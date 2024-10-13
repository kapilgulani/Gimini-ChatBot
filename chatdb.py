import streamlit as st
import requests
import json
from datetime import datetime
import sqlite3

# Set up Gemini API key (replace with your actual key)
GEMINI_API_KEY = "AIzaSyC50aOjo706mEK7uR2I15Veipda14KW_mI"

# Function to initialize the database
def init_db():
    conn = sqlite3.connect('tax_conversations.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS conversations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  prompt TEXT,
                  response TEXT)''')
    conn.commit()
    conn.close()

# Function to save conversation to database
def save_to_db(prompt, response):
    conn = sqlite3.connect('tax_conversations.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO conversations (timestamp, prompt, response) VALUES (?, ?, ?)",
              (timestamp, prompt, response))
    conn.commit()
    conn.close()

# Function to get conversation history from database
def get_conversation_history(limit=5):
    conn = sqlite3.connect('tax_conversations.db')
    c = conn.cursor()
    c.execute("SELECT prompt, response FROM conversations ORDER BY id DESC LIMIT ?", (limit,))
    history = c.fetchall()
    conn.close()
    return history

# Function to generate response using Gemini model
def generate_response(prompt, history):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        
        # Prepare context from history
        context = "\n".join([f"User: {h[0]}\nAssistant: {h[1]}" for h in history])
        
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"You are a knowledgeable tax advisor specializing in US tax law. Provide accurate and helpful information about tax deductions, credits, and regulations. Only answer tax-related questions. Here's the conversation history and the new question:\n\nContext:\n{context}\n\nNew question: {prompt}"
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

# Initialize database
init_db()

# Streamlit UI
st.title("Deloitte Tax Advisor")
st.write("Ask tax-related questions and get expert advice.")

# User input
user_input = st.text_input("Enter your tax-related question:")

if st.button("Submit"):
    if user_input:
        # Get conversation history
        history = get_conversation_history()
        
        # Generate response
        response = generate_response(user_input, history)
        
        # Save to database
        save_to_db(user_input, response)
        
        # Display response
        st.write("Response:")
        st.write(response)
    else:
        st.warning("Please enter a question.")

# Display conversation history
history = get_conversation_history()
if history:
    st.write("Conversation History:")
    for prompt, response in history:
        st.write(f"User: {prompt}")
        st.write(f"Assistant: {response}")
        st.write("---")

# Clear conversation button
if st.button("Clear Conversation"):
    conn = sqlite3.connect('tax_conversations.db')
    c = conn.cursor()
    c.execute("DELETE FROM conversations")
    conn.commit()
    conn.close()
    st.success("Conversation history cleared.")