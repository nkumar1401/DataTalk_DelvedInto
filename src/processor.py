import pandas as pd
import numpy as np

def auto_clean_data(df):
    """
    The 'Standard Cleaning Engine' for DataTalk.
    This function is called by both the Upload page and the Chat Pin.
    """
    # 1. Create a copy to avoid modifying the original until ready
    working_df = df.copy()

    # 2. Basic Cleaning: Remove duplicates
    working_df = working_df.drop_duplicates()

    # 3. Handle Missing Values (Automated Imputation)
    for col in working_df.columns:
        if working_df[col].dtype in ['int64', 'float64']:
            # Fill numbers with the median
            working_df[col] = working_df[col].fillna(working_df[col].median())
        else:
            # Fill text/categories with 'Unknown'
            working_df[col] = working_df[col].fillna('Unknown')

    # 4. Outlier Removal (Using IQR Method)
    # This keeps your AI's predictions accurate
    numeric_cols = working_df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        Q1 = working_df[col].quantile(0.25)
        Q3 = working_df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        working_df = working_df[(working_df[col] >= lower_bound) & (working_df[col] <= upper_bound)]

    return working_df