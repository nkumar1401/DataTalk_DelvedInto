import streamlit as st
import pandas as pd
from src.processor import clean_dataframe

st.set_page_config(page_title="DataTalk AI", layout="wide")

# Section: Introduction [cite: 288]
st.title("🏠 DataTalk: Conversational Analytics")
st.markdown("Transform your datasets into insights through intelligent automation.")

# Section: Upload Dataset [cite: 289]
uploaded_file = st.file_uploader("Upload your CSV or XLSX file", type=['csv', 'xlsx'])

if uploaded_file:
    # Load and Preview [cite: 203, 204]
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    
    st.session_state['raw_df'] = df
    st.write("### Data Preview", df.head())
    
    if st.button("Clean Data & Proceed"):
        cleaned_df = clean_dataframe(df)
        st.session_state['df'] = cleaned_df
        st.success("Data cleaned! Navigate to the Dashboard or Chat.")
# import google.generativeai as genai
# import streamlit as st

# genai.configure(api_key=st.secrets["GENAI_API_KEY"])

# try:
#     for m in genai.list_models():
#         if 'generateContent' in m.supported_generation_methods:
#             st.write(f"✅ Available Model Name: `{m.name}`")
# except Exception as e:
#     st.error(f"Cannot list models: {e}")        