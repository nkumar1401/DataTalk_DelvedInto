import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score, f1_score
import xgboost as xgb
import os
import time

data_file = None
for attempt in range(12): # Wait up to 60 seconds
    for root, dirs, files in os.walk('/kaggle/input'):
        for file in files:
            if file.endswith('.csv'):
                data_file = os.path.join(root, file)
                break
    if data_file: break
    time.sleep(5)

if not data_file:
    raise FileNotFoundError("Dataset mount timeout in /kaggle/input")

data = pd.read_csv(data_file)

target_column = 'Price_in_Lakhs'

X = data.drop(target_column, axis=1)
y = data[target_column]

numeric_cols = X.select_dtypes(include=['int64', 'float64']).columns
categorical_cols = X.select_dtypes(include=['object']).columns

X[numeric_cols] = X[numeric_cols].fillna(X[numeric_cols].median())
X[categorical_cols] = X[categorical_cols].fillna(X[categorical_cols].mode().iloc[0])

le = LabelEncoder()
for col in categorical_cols:
    X[col] = le.fit_transform(X[col])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

models = {
    'LinearRegression': LinearRegression(),
    'RandomForestRegressor': RandomForestRegressor(),
    'XGBoost': xgb.XGBRegressor(),
    'SVR': SVR(),
    'GradientBoosting': GradientBoostingRegressor()
}

best_model = None
best_score = -np.inf
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    if target_column == 'Price_in_Lakhs':
        score = r2_score(y_test, y_pred)
    else:
        score = f1_score(y_test, y_pred)
    if score > best_score:
        best_score = score
        best_model = name

final_X = pd.DataFrame({
    'Property_Type': ['Flat'],
    'BHK': [4],
    'Size_in_SqFt': [X['Size_in_SqFt'].median()],
    'Year_Built': [2030],
    'Furnished_Status': [le.transform(['Unfurnished'])],
    'Floor_No': [X['Floor_No'].median()],
    'Total_Floors': [X['Total_Floors'].median()],
    'Age_of_Property': [0],
    'Nearby_Schools': [le.transform(['Yes'])],
    'Nearby_Hospitals': [le.transform(['Yes'])],
    'Public_Transport_Accessibility': [le.transform(['Yes'])],
    'Parking_Space': [le.transform(['Yes'])],
    'Security': [le.transform(['Yes'])],
    'Amenities': [le.transform(['Yes'])],
    'Facing': [le.transform(['North'])],
    'Owner_Type': [le.transform(['Builder'])],
    'Availability_Status': [le.transform(['Ready_to_Move'])],
    'Locality': [le.transform(['Mumbai'])],
    'City': [le.transform(['Mumbai'])],
    'State': [le.transform(['Maharashtra'])]
})

final_X = final_X.drop(categorical_cols, axis=1)

for col in categorical_cols:
    final_X[col] = le.transform([X[col].mode().iloc[0]])

final_model = models[best_model]
final_model.fit(X_train, y_train)

final_result = final_model.predict(final_X)

print('BEST_MODEL:', best_model)
print('FINAL_RESULT:', final_result[0])