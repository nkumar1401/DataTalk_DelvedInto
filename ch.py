from google import genai
import streamlit as st

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])


response = client.models.generate_content(
    model="gemini-3-flash-preview", contents="Explain how AI works in a few words"
)
print(response.text)
