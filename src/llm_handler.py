import streamlit as st
import os
import re
from google import genai
from groq import Groq

def ask_ai(user_query, df):
    """
    Multi-LLM Resilience Handler
    Primary: Gemini 2.0 Flash
    Fallback: Groq (Llama-3-70b)
    """
    # 1. Setup API Keys
    gemini_key = st.secrets.get("GENAI_API_KEY") or os.getenv("GENAI_API_KEY")
    groq_key = st.secrets.get("groq_API_KEY") or os.getenv("groq_API_KEY")
    
    # Common Prompt
    prompt = f"""
    Context: Expert Data Analyst. 
    Data: 'df' with columns: {list(df.columns)}.
    Query: "{user_query}"
    Task: Write Python code using pandas and plotly.express.
    - Summary calculations: variable 'result'.
    - Visualizations: plotly.express object 'fig'.
    - Output format: RAW code inside ```python blocks.
    """

    # --- TRY GEMINI (PRIMARY) ---
    try:
        client_gemini = genai.Client(api_key=gemini_key)
        response = client_gemini.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        return extract_code(response.text)

    except Exception as e:
        # Check if error is Quota Exhausted (429)
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            st.warning("⚠️ Gemini Quota Exhausted. Switching to Groq Infrastructure...")
            
            # --- TRY GROQ (FALLBACK) ---
            try:
                if not groq_key:
                    st.error("Groq API Key missing. Cannot failover.")
                    return None
                
                client_groq = Groq(api_key=groq_key)
                completion = client_groq.chat.completions.create(
                    model="llama-3.3-70b-versatile", # Reliable Groq model
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1 # Low temperature for accurate code
                )
                return extract_code(completion.choices[0].message.content)
            
            except Exception as groq_err:
                st.error(f"Critical System Failure: {groq_err}")
                return None
        else:
            st.error(f"⚡ Connection Error: {str(e)}")
            return None

def extract_code(text):
    """Helper to pull Python code from markdown blocks"""
    code_match = re.search(r"```python\n(.*?)```", text, re.DOTALL)
    if code_match:
        return code_match.group(1).strip()
    return None