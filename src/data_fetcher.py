import pandas as pd
from sklearn import datasets
import os

def download_from_sklearn(dataset_name="iris"):
    """Fetch classic datasets from Scikit-Learn."""
    try:
        if dataset_name == "iris":
            data = datasets.load_iris()
        elif dataset_name == "titanic":
            # Titanic isn't native to sklearn anymore, usually fetched from OpenML
            from sklearn.datasets import fetch_openml
            data = fetch_openml('titanic', version=1, as_frame=True)
            return data.frame
        
        # Convert to DataFrame
        df = pd.DataFrame(data.data, columns=data.feature_names)
        if hasattr(data, 'target'):
            df['target'] = data.target
        return df
    except Exception as e:
        print(f"Error fetching from sklearn: {e}")
        return None

def download_from_url(url):
    """Fetch CSV data from raw GitHub or Web sources."""
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        print(f"Error fetching from URL: {e}")
        return None

def save_dataset(df, filename):
    """Save the fetched data to the data/ folder."""
    if df is not None:
        if not os.path.exists("data"):
            os.makedirs("data")
        path = f"data/{filename}.csv"
        df.to_csv(path, index=False)
        print(f"✅ Success: Dataset saved to {path}")
        return path
    return None

if __name__ == "__main__":
    print("🚀 DataTalk Downloader Initialized...")
    
    # Example 1: Raw Source (Titanic)
    titanic_url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
    df_titanic = download_from_url(titanic_url)
    save_dataset(df_titanic, "titanic_raw")

    # Example 2: Sklearn (Iris)
    df_iris = download_from_sklearn("iris")
    save_dataset(df_iris, "iris_standard")