import google.generativeai as genai
import streamlit as st
import os
import re

def ask_ai(user_query, df):
    """
    Refined AI Handler: Interprets user query and returns executable Python code.
    Developed by: Nirmal Kumar Bhagatkar (AI/ML Expert)
    """
    # 1. API Configuration (Using st.secrets for Streamlit Cloud / .env for Local)
    api_key = st.secrets.get("GENAI_API_KEY") or os.getenv("GENAI_API_KEY")
    
    if not api_key:
        st.error("API Key not found. Please set GENAI_API_KEY in secrets.toml or .env file.")
        return None

    genai.configure(api_key=api_key)
    
    # 2. Model Initialization (Using the stable 1.5-flash for speed)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # 3. Prompt Engineering (Optimized for the project's 'Chat with Data' module)
    prompt = f"""
    You are an expert Data Analyst. The dataframe 'df' is already loaded and has columns: {list(df.columns)}.
    User Query: "{user_query}"
    
    Task: Write Python code to answer the query using pandas and plotly.express.
    Instructions:
    - If user asks for a calculation or summary: Store the final answer in a variable called 'result'.
    - If user asks for a chart: Use plotly.express (as px) and assign the chart object to 'fig'.
    - Return ONLY the raw Python code within ```python ``` blocks.
    - Do not include any explanations or conversational text.
    """
    
    try:
        response = model.generate_content(prompt)
        full_text = response.text
        
        # 4. Code Extraction using Regular Expressions
        code_match = re.search(r"```python\n(.*?)```", full_text, re.DOTALL)
        
        if code_match:
            return code_match.group(1).strip()
        else:
            # Fallback if the model returns text instead of code
            return None
            
    except Exception as e:
        st.error(f"Error connecting to Gemini: {str(e)}")
        return None