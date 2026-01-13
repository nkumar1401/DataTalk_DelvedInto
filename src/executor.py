import pandas as pd
import plotly.express as px
import streamlit as st

def execute_llm_code(code, data_lake):
    """Executes code and renders to the UI. Returns nothing so we don't see 'nonsense'."""
    try:
        # Pass st and px so the code can actually draw things
        context = {
            "pd": pd, "px": px, "st": st, 
            "data_lake": data_lake,
            "df": list(data_lake.values())[0] if data_lake else None
        }
        # Run the AI's code (which includes st.write/st.plotly_chart)
        exec(code, context)
        return True, None
    except Exception as e:
        return False, str(e)