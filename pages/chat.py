import streamlit as st
import pandas as pd
from src.llm_handler import ask_ai 
from src.executor import execute_llm_code
# NEW: Import the specialized ML Orchestrator and Router
from src.router import get_intent_router
from src.ml_orchestrator import generate_ml_script_via_llm
from src.kaggle_automator import autonomous_kaggle_run

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
st.info("Ask for standard analysis or heavy predictive modeling (Singapore Housing, etc.)")

# --- 4. CHAT DISPLAY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        # Persist standard visualizations
        if "code" in message and message["code"]:
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
user_text = st.chat_input("Ask about patterns, or say 'Predict the price after 5 years'...")

# --- 7. LOGIC EXECUTION ---
final_query = st.session_state.get('active_prompt') or user_text

if final_query:
    st.session_state.active_prompt = None 
    st.session_state.messages.append({"role": "user", "content": final_query})
    
    if active_df is None:
        st.warning("Please upload data first!")
    else:
        # STEP 1: ROUTE INTENT (Semantic Check)
        with st.spinner("Determining Intent..."):
            intent = get_intent_router(final_query)
        
        # STEP 2: BRANCHING LOGIC
        if intent == "ML_FOUNDRY":
            # PATH A: HEAVY ML (Kaggle Offload)
            with st.status("🤖 Orchestrating Heavy ML Pipeline...") as status:
                st.write("Generating 5-Model Tournament Script...")
                ml_script = generate_ml_script_via_llm(final_query, active_df)
                
                st.write("Offloading to Kaggle Compute Clusters...")
                # This function handles the API upload and returns the final prediction result
                response_text = autonomous_kaggle_run(active_df, ml_script)
                
                status.update(label="Cloud Analysis Complete!", state="complete")
            
            code = None # No local code execution needed for Kaggle path
            suggestions = ["Show model comparison", "Predict for 10 years", "Analyze outliers"]

        else:
            # PATH B: GENERAL CHAT (Your stable logic)
            with st.spinner("Analyzing Data..."):
                code, suggestions, response_text = ask_ai(final_query, {"Uploaded_Data": active_df})
            
            if code:
                with st.chat_message("assistant"):
                    success, err = execute_llm_code(code, {"Uploaded_Data": active_df})
                    if not success: st.error(f"Execution Error: {err}")

        # STEP 3: SAVE TO HISTORY
        st.session_state.last_suggestions = suggestions
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response_text,
            "code": code 
        })
        st.rerun()