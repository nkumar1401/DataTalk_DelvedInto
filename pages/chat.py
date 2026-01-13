import streamlit as st
import pandas as pd
from src.llm_handler import ask_ai 
from src.executor import execute_llm_code

st.set_page_config(page_title="DataTalk Intelligence", layout="wide")

# --- 1. INITIALIZE SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if 'last_suggestions' not in st.session_state:
    st.session_state.last_suggestions = []
if 'active_prompt' not in st.session_state:
    st.session_state.active_prompt = None

# --- 2. GLOBAL DATA SYNC ---
active_df = st.session_state.get('df')

# --- 3. UI HEADER ---
st.title("💬 DataTalk: Autonomous Insights")

# --- 4. CHAT DISPLAY ---
# This ensures previous answers and graphs stay visible
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "code" in message and message["code"]:
            # Re-run the visual code so the graph stays on screen
            data_to_analyze = {"Uploaded_Data": active_df}
            execute_llm_code(message["code"], data_to_analyze)

# --- 5. PREDICTIVE FOLLOW-UPS ---
if st.session_state.last_suggestions:
    st.markdown("🔍 **Predictive Follow-ups:**")
    cols = st.columns(len(st.session_state.last_suggestions))
    for i, sugg in enumerate(st.session_state.last_suggestions):
        if cols[i].button(sugg, key=f"sugg_{i}_{len(st.session_state.messages)}"):
            st.session_state.active_prompt = sugg
            st.rerun()

# --- 6. USER INPUT ---
user_text = st.chat_input("Ask about patterns, averages, or trends...")

# --- 7. LOGIC EXECUTION ---
final_query = st.session_state.get('active_prompt') or user_text

if final_query:
    # Reset active prompt to prevent loops
    st.session_state.active_prompt = None 
    
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": final_query})
    
    # Process Response
    if active_df is None:
        st.warning("Please upload data first!")
    else:
        data_to_analyze = {"Uploaded_Data": active_df}
        
        # Get AI Response
        with st.spinner("Analyzing..."):
            code, suggestions, response_text = ask_ai(final_query, data_to_analyze)
        
        # Update suggestions for next turn
        st.session_state.last_suggestions = suggestions
        
        # SAVE AND RENDER IMMEDIATELY
        # We append to history first, then rerun to trigger the 'Chat Display' section
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response_text,
            "code": code 
        })
        st.rerun()