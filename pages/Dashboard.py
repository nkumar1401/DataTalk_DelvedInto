import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="EDA Dashboard", layout="wide")

if 'df' in st.session_state:
    df = st.session_state['df']
    st.title("📊 Automated EDA Dashboard")

    # Summary Statistics [cite: 44, 69]
    st.subheader("Descriptive Statistics")
    st.dataframe(df.describe(), use_container_width=True)

    # Data Quality: Missing Values [cite: 44, 71]
    st.subheader("Missing Values Report")
    missing_data = df.isnull().sum()
    st.write(missing_data[missing_data > 0] if not missing_data.empty else "No missing values detected.")

    # Visualizations [cite: 45, 46]
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Correlation Heatmap")
        numeric_df = df.select_dtypes(include=['number'])
        if not numeric_df.empty:
            fig_corr = px.imshow(numeric_df.corr(), text_auto=True, aspect="auto", color_continuous_scale='RdBu_r')
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("No numerical data available for correlation.")

    with col2:
        st.subheader("Column Distribution")
        target_col = st.selectbox("Select column to view distribution", df.columns)
        fig_dist = px.histogram(df, x=target_col, marginal="box", nbins=30)
        st.plotly_chart(fig_dist, use_container_width=True)

else:
    st.warning("Please upload a dataset on the Home page first.")