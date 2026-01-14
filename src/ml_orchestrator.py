import streamlit as st
from google import genai
from groq import Groq
import re

def generate_ml_script_via_llm(user_query, df):
    
    columns = list(df.columns)
    
    # ⚡ FOUNDER TIP: Remove 'data.csv' from the DATA CONTEXT to avoid confusing the LLM
    ml_prompt = f"""
    Role: Senior Machine Learning Engineer.
    Task: Write a production-ready Python script for: "{user_query}"
    
    DATA CONTEXT:
    - Columns: {columns}
    
    SCRIPT REQUIREMENTS (STRICT):
    1. Import pandas, numpy, sklearn, and os.
    2. KAGGLE DATA LOADING (RESILIENT):
       The data might take a moment to mount. Use this loop:
       
       import os, time
       data_file = None
       for attempt in range(12): # Wait up to 60 seconds
           for root, dirs, files in os.walk('/kaggle/input'):
               for file in files:
                   if file.endswith('.csv'):
                       data_file = os.path.join(root, file)
                       break
           if data_file: break
           time.sleep(5)
           
       if not data_file:
           raise FileNotFoundError("Dataset mount timeout in /kaggle/input")
       
       data = pd.read_csv(data_file)
           
    3. Auto-detect target column from: "{user_query}".
    4. PREPROCESS (ROBUST):
       - Separate features (X) and target (y).
       - For numeric columns: Fill missing values with the median. 
         Use: X[numeric_cols] = X[numeric_cols].fillna(X[numeric_cols].median())
       - For categorical columns: Fill missing values with the mode.
         Then, use LabelEncoder or pd.get_dummies to convert them to numbers.
       - Ensure NO string data remains in X before training.
    5. TOURNAMENT: Train/Eval 5 models: Linear/Logistic, RF, XGBoost, SVR, GradientBoosting.
    6. PERFORMANCE: Calculate R2 Score or F1-Score.
    7. OUTPUT: Print "BEST_MODEL: <name>" and "FINAL_RESULT: <prediction>".
    
    Return ONLY raw Python code. No markdown, no backticks, no introduction.
    """

    # --- ATTEMPT 1: GEMINI (Primary) ---
    try:
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=ml_prompt
        )
        # Clean response: Remove markdown blocks and trailing text
        script = re.sub(r'```(?:python)?|```', '', response.text).strip()
        if script:
            return script
    except Exception as e:
        st.toast("⚡ Gemini Limit Reached. Failing over to Groq...", icon="🔄")

    # --- ATTEMPT 2: GROQ (Failover) ---
    try:
        groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": ml_prompt}],
            model="llama-3.3-70b-versatile",
        )
        script_raw = chat_completion.choices[0].message.content
        script = re.sub(r'```(?:python)?|```', '', script_raw).strip()
        return script
    except Exception as e:
        return f"# Critical Error: All LLM providers failed. {str(e)}"