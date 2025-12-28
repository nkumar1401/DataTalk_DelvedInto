import streamlit as st
import pandas as pd
import plotly.express as px
from src.processor import clean_dataframe

st.set_page_config(page_title="Auto Visualizations", layout="wide")

st.title("📈 Auto-Visualization Engine")
st.markdown("Select your variables to generate instant, high-quality visualizations.")

# Ensure data is available in session state
if 'df' in st.session_state:
    df = st.session_state['df']
    
    # Sidebar for Chart Controls
    st.sidebar.header("Chart Configuration")
    
    # Identify column types for better user experience
    all_cols = df.columns.tolist()
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist()

    # User selections for axes
    x_axis = st.sidebar.selectbox("Select X-Axis (Dimensions)", all_cols)
    y_axis = st.sidebar.selectbox("Select Y-Axis (Measures)", numeric_cols)
    
    # Smart Chart Selection logic
    st.sidebar.subheader("Select Visualization Type")
    chart_type = st.sidebar.selectbox(
        "Choose a Chart Type", 
        ["Bar Chart", "Line Chart", "Scatter Plot", "Box Plot", "Histogram", "Pie Chart"]
    )

    # Main Display Area
    st.subheader(f"{chart_type}: {x_axis} vs {y_axis}")
    
    try:
        if chart_type == "Bar Chart":
            # Best for Comparisons [cite: 59, 105]
            fig = px.bar(df, x=x_axis, y=y_axis, color=x_axis, template="plotly_white")
            
        elif chart_type == "Line Chart":
            # Best for Trends & Time Analysis [cite: 59, 105]
            fig = px.line(df, x=x_axis, y=y_axis, markers=True, template="plotly_white")
            
        elif chart_type == "Scatter Plot":
            # Best for Statistical Insights/Correlations [cite: 53, 59]
            fig = px.scatter(df, x=x_axis, y=y_axis, color=x_axis, trendline="ols", template="plotly_white")
            
        elif chart_type == "Box Plot":
            # Best for Outlier Detection [cite: 59, 105]
            fig = px.box(df, x=x_axis, y=y_axis, color=x_axis, template="plotly_white")
            
        elif chart_type == "Histogram":
            # Best for Distribution Analysis [cite: 53, 59]
            fig = px.histogram(df, x=x_axis, marginal="box", template="plotly_white")
            
        elif chart_type == "Pie Chart":
            # Best for Composition/Cardinality [cite: 59, 60]
            fig = px.pie(df, names=x_axis, values=y_axis, hole=0.3, template="plotly_white")

        # Render the interactive chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Deliverable: Downloadable charts [cite: 113]
        st.success("Visualization generated successfully. You can interact with or download this chart using the icons above.")

    except Exception as e:
        st.error(f"Error generating chart: {e}. Please ensure the selected columns are compatible with the chart type.")

else:
    st.warning("⚠️ No dataset detected. Please navigate to the 'Upload Dataset' page to start.")
    if st.button("Go to Upload Page"):
        st.switch_page("pages/1_Upload.py")