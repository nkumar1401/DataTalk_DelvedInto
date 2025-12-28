import streamlit as st
import pandas as pd
import os
from src.processor import clean_dataframe
from sklearn import datasets

st.set_page_config(page_title="Data Source - DataTalk", layout="wide")

st.title("📂 Data Acquisition & Preparation")
st.markdown("Choose between uploading your own business data or fetching industry-standard datasets.")

# Create Two Paths: Manual and Automated
tab1, tab2 = st.tabs(["📤 Manual Upload", "📥 Automated Downloader"])

with tab1:
    st.subheader("Upload Local Dataset")
    uploaded_file = st.file_uploader("Drag and drop your CSV or XLSX file", type=['csv', 'xlsx'])
    
    if uploaded_file:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        # We store in raw_df to show the preview before cleaning
        st.session_state['raw_df'] = df
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")

with tab2:
    st.subheader("Fetch Standard Datasets")
    st.write("Retrieve datasets directly from Scikit-Learn or established GitHub repositories.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        ds_choice = st.selectbox("Select a Dataset", ["Iris (Classification)", "Titanic (Survival)"])
    
    if st.button("Fetch and Load"):
        with st.spinner("Fetching data..."):
            if ds_choice == "Iris (Classification)":
                data = datasets.load_iris()
                df = pd.DataFrame(data.data, columns=data.feature_names)
                df['target'] = data.target
            else:
                url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
                df = pd.read_csv(url)
            
            # Update session state
            st.session_state['raw_df'] = df
            st.success(f"Successfully loaded {ds_choice}!")
            # Rerun to show the preview and cleaning button immediately
            st.rerun()

# Processing Section (Only shows if raw_df is in session state)
if 'raw_df' in st.session_state:
    raw_data = st.session_state['raw_df']
    st.markdown("---")
    
    # Display Metadata & Preview
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Dataset Preview")
        st.dataframe(raw_data.head(10), use_container_width=True)
    
    with col2:
        st.subheader("File Metadata")
        st.write(f"**Rows:** {raw_data.shape[0]} | **Columns:** {raw_data.shape[1]}")
        st.write("**Data Types Summary:**")
        st.write(raw_data.dtypes.value_counts())

    # Trigger Data Preparation Module
    st.markdown("### 🛠️ Data Engineering")
    if st.button("Run Automated Cleaning"):
        with st.spinner("Executing architecture-level cleaning (Imputation & IQR)..."):
            # 1. Clean the data using your src/processor.py logic
            cleaned_df = clean_dataframe(raw_data)
            
            # 2. CRITICAL: Store in 'df'. This is the variable used by Dashboard and Viz pages.
            st.session_state['df'] = cleaned_df
            
            st.success("Cleaning complete! Data is now active across all modules.")
            st.balloons()
            
            # Show a button to jump to the next step
            if st.button("Go to Dashboard 📊"):
                st.switch_page("pages/2_Dashboard.py")