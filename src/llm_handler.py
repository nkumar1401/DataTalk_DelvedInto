import streamlit as st
import os
import re
import pandas as pd
from google import genai
from groq import Groq
from collections.abc import Iterable


# -------------------------------------------------
# Utility: Normalize any input into a DataFrame
# -------------------------------------------------
def normalize_to_dataframe(data):
    if isinstance(data, pd.DataFrame):
        return data

    if isinstance(data, list) and all(isinstance(i, dict) for i in data):
        return pd.DataFrame(data)

    if isinstance(data, dict):
        # dict of iterables → columns
        if all(
            isinstance(v, Iterable) and not isinstance(v, (str, bytes))
            for v in data.values()
        ):
            return pd.DataFrame(data)

        # dict of scalars → single-row DataFrame
        return pd.DataFrame([data])

    raise TypeError(f"Unsupported data type: {type(data)}")


# -------------------------------------------------
# Utility: Extract code, suggestions, and text
# -------------------------------------------------
def extract_code_and_suggestions(text):
    if not text:
        return None, [], "No response received."

    # 1. Extract Python code
    code_match = re.search(r"```python\s+(.*?)```", text, re.DOTALL)
    code = code_match.group(1).strip() if code_match else None

    # 2. Extract suggestions
    suggestions = []
    if "[SUGGESTIONS]:" in text:
        s_part = text.split("[SUGGESTIONS]:")[-1].strip()
        suggestions = [s.strip() for s in s_part.split("|") if s.strip()]

    # 3. Extract conversational text
    convo_text = re.sub(r"```python.*?```", "", text, flags=re.DOTALL)
    convo_text = convo_text.split("[SUGGESTIONS]:")[0].strip()

    if not convo_text and code:
        convo_text = "I've generated the analysis for you."

    return code, suggestions, convo_text


# -------------------------------------------------
# Main LLM Handler
# -------------------------------------------------
def ask_ai(user_query, data_lake):
    """
    Predictive Multi-LLM Handler
    Returns: (code, suggestions, response_text)
    """

    gemini_key = st.secrets.get("GENAI_API_KEY") or os.getenv("GENAI_API_KEY")
    groq_key = st.secrets.get("groq_API_KEY") or os.getenv("groq_API_KEY")

    # -------------------------------------------------
    # Normalize all datasets in the data lake
    # -------------------------------------------------
    normalized_lake = {}
    for name, raw_data in data_lake.items():
        normalized_lake[name] = normalize_to_dataframe(raw_data)

    # -------------------------------------------------
    # Build dataset metadata for prompt
    # -------------------------------------------------
    dataset_info = ""
    for name, df in data_lake.items():
        dataset_info += f"\n- Table: '{name}' | Columns: {list(df.columns)}"

    prompt = f"""
    Role: Senior Data Architect (DataTalk).
    Target: Answer the user's query first, then provide metrics/visuals.
    Context: {dataset_info}

    RULES:
    1. GREETING/UNKNOWN: If the user says "hello" or asks something outside the data, respond with a professional text message. NO code.
    2. DATA QUERIES:
       - FIRST: Provide a clear, 1-sentence textual answer.
       - SECOND: Generate Python code to prove the answer.
       - For "Average/Total": Use `st.metric(label="Result", value=...)`.
       - For "Trends/Patterns/Relationships": Use `st.plotly_chart(px.bar(...) or px.line(...) or px.scatter(...))`.
    3. NO ANNOTATIONS: Do NOT use `var: type = val`. Use `var = val`.
    4. DATA ACCESS: Use `df = data_lake['Uploaded_Data']`.

    FORMAT:
    [ANSWER]: Your direct textual answer here.
    ```python
    # Code using st.metric, st.write, or st.plotly_chart
    ```
    [SUGGESTIONS]: Question 1 | Question 2
    
    User Query: "{user_query}"
    """
    # Ensure your extraction logic captures [ANSWER] as 'response_text'
# -------------------------------------------------
# PRIMARY ENGINE: GEMINI
# -------------------------------------------------
    try:
        client_gemini = genai.Client(api_key=gemini_key)
        response = client_gemini.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return extract_code_and_suggestions(response.text)

# -------------------------------------------------
# FALLBACK ENGINE: GROQ
# -------------------------------------------------
    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            st.warning("Gemini quota exhausted. Switching to Groq.")

            try:
                client_groq = Groq(api_key=groq_key)
                completion = client_groq.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1
                )
                return extract_code_and_suggestions(
                    completion.choices[0].message.content
                )

            except Exception as groq_err:
                return None, [], f"Groq failure: {groq_err}"

        return None, [], f"Connection error: {e}"
