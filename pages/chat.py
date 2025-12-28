import streamlit as st
import pandas as pd
import plotly.express as px
from src.llm_handler import ask_ai  # Importing your refined AI brain

st.set_page_config(page_title="Chat with Data", layout="wide")

def execute_llm_code(code, df):
    """Safely executes code with access to Pandas and Plotly."""
    try:
        # Include px so the LLM can generate charts successfully
        local_vars = {'df': df, 'pd': pd, 'px': px} 
        exec(code, {}, local_vars)
        
        # Priority 1: Visualization, Priority 2: Text Result
        return local_vars.get('result', ""), local_vars.get('fig', None)
    except Exception as e:
        return f"⚠️ Logic Error: {e}", None

if 'df' in st.session_state:
    df = st.session_state['df']
    st.title("💬 Chat with DataTalk")
    st.info("Example: 'Show me a bar chart of survival rate by class' or 'What is the median age?'")

    # Chat history UI for better user experience
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("fig"):
                st.plotly_chart(message["fig"])

    # Handle new input
    if prompt := st.chat_input("Ask about your dataset..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Gemini is thinking..."):
            # Use the refined logic from your src folder
            code = ask_ai(prompt, df)
            
            if code:
                ans, fig = execute_llm_code(code, df)
                
                with st.chat_message("assistant"):
                    if ans: st.write(ans)
                    if fig: st.plotly_chart(fig)
                
                # Save to history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": str(ans), 
                    "fig": fig
                })
            else:
                st.error("I couldn't generate code for that query. Please try rephrasing.")
else:
    st.error("No dataset found. Please upload a file on the Home page first.")