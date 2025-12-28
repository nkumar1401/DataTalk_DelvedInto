import streamlit as st
import pandas as pd
from src.processor import clean_dataframe

st.set_page_config(page_title="Upload Dataset", layout="wide")

st.title("📂 Data Upload & Preparation")
st.markdown("Upload your business datasets to begin automated analysis.")

# File Uploader for CSV/XLSX [cite: 33, 64]
uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx'])

if uploaded_file:
    # Read dataset [cite: 33]
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    # Store raw data in session state
    st.session_state['raw_df'] = df

    # Display Metadata & Preview [cite: 34, 66, 67]
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Dataset Preview")
        st.dataframe(df.head(10))
    
    with col2:
        st.subheader("File Metadata")
        st.write(f"**Filename:** {uploaded_file.name}")
        st.write(f"**Rows:** {df.shape[0]} | **Columns:** {df.shape[1]}")
        st.write("**Data Types:**")
        st.write(df.dtypes)

    # Trigger Data Preparation Module [cite: 36]
    if st.button("Run Automated Cleaning"):
        with st.spinner("Handling missing values and outliers..."):
            # This calls the logic we defined in src/processor.py
            cleaned_df = clean_dataframe(df)
            st.session_state['df'] = cleaned_df
            st.success("Cleaning complete! Missing values imputed and outliers handled.")
            st.info("You can now proceed to the Dashboard or Chat sections.")