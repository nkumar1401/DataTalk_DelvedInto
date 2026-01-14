import streamlit as st
from google import genai
from groq import Groq
def get_intent_router(user_query):
    """
    Uses LLM to decide if the query requires standard Analysis or Heavy ML/Kaggle.
    """
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    
    routing_prompt = f"""
    Analyze the following user query for a Data Science app.
    Categorize it into exactly one of these two buckets:
    
    1. 'ML_FOUNDRY': Use this if the user wants predictions, future forecasting, 
       machine learning model comparisons, clustering, or any "heavy" statistical modeling.
    2. 'GENERAL_CHAT': Use this for data summaries, "hello" messages, basic charts, 
       filtering, or general questions about the current data.

    User Query: "{user_query}"
    
    Return ONLY the bucket name.
    """
    
    try:
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            # model="gemini-3-flash-preview",
            contents=routing_prompt
        )
        intent = response.text.strip().upper()
        if intent in ["ML_FOUNDRY", "GENERAL_CHAT"]:
            return intent
    except Exception as e:
        st.warning("⚡ Gemini Exhausted. Switching to Groq Failover...")
        
    # --- ATTEMPT 2: GROQ (Secondary / Failover) ---
    try:
        # Ensure you have GROQ_API_KEY in st.secrets
        groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": routing_prompt}],
            model="llama-3.3-70b-versatile",
        )
        intent = chat_completion.choices[0].message.content.strip().upper()
        return intent if intent in ["ML_FOUNDRY", "GENERAL_CHAT"] else "GENERAL_CHAT"
    except Exception as e:
        st.error(f"❌ All LLM Providers exhausted: {e}")
        return "GENERAL_CHAT"