import os
import pickle
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Define paths dynamically relative to the application's root directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODELS_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "best_model.pkl")
ENCODER_PATH = os.path.join(MODELS_DIR, "encoder.pkl")
COLUMNS_PATH = os.path.join(MODELS_DIR, "model_columns.pkl")

# Load models and column specs
print("Loading model and preprocessors...")
with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)
with open(ENCODER_PATH, 'rb') as f:
    encoder = pickle.load(f)
with open(COLUMNS_PATH, 'rb') as f:
    model_columns = pickle.load(f)

print("Loaded successfully. Features list length:", len(model_columns))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get data from request
        data = request.json
        
        # Build pandas DataFrame for a single sample matching preprocess schema
        input_data = {
            'CODE_GENDER': [int(data.get('CODE_GENDER', 0))],
            'FLAG_OWN_CAR': [int(data.get('FLAG_OWN_CAR', 0))],
            'FLAG_OWN_REALTY': [int(data.get('FLAG_OWN_REALTY', 0))],
            'CNT_CHILDREN': [int(data.get('CNT_CHILDREN', 0))],
            'AMT_INCOME_TOTAL': [float(data.get('AMT_INCOME_TOTAL', 0.0))],
            'FLAG_WORK_PHONE': [int(data.get('FLAG_WORK_PHONE', 0))],
            'FLAG_PHONE': [int(data.get('FLAG_PHONE', 0))],
            'FLAG_EMAIL': [int(data.get('FLAG_EMAIL', 0))],
            'CNT_FAM_MEMBERS': [int(data.get('CNT_FAM_MEMBERS', 1))],
            'AGE': [int(data.get('AGE', 30))],
            'YEARS_EMPLOYED': [int(data.get('YEARS_EMPLOYED', 0))],
            'UNEMPLOYED': [int(data.get('UNEMPLOYED', 0))]
        }
        
        df_numeric = pd.DataFrame(input_data)
        
        # Build categorical dataframe
        categorical_data = {
            'NAME_INCOME_TYPE': [data.get('NAME_INCOME_TYPE', 'Working')],
            'NAME_EDUCATION_TYPE': [data.get('NAME_EDUCATION_TYPE', 'Secondary / secondary special')],
            'NAME_FAMILY_STATUS': [data.get('NAME_FAMILY_STATUS', 'Married')],
            'NAME_HOUSING_TYPE': [data.get('NAME_HOUSING_TYPE', 'House / apartment')],
            'OCCUPATION_TYPE': [data.get('OCCUPATION_TYPE', 'Unknown')]
        }
        df_categ = pd.DataFrame(categorical_data)
        
        # One-hot encode using fitted encoder
        encoded_features = encoder.transform(df_categ)
        encoded_feature_names = encoder.get_feature_names_out(list(categorical_data.keys()))
        encoded_df = pd.DataFrame(encoded_features, columns=encoded_feature_names)
        
        # Concatenate numeric and encoded df
        df_processed = pd.concat([df_numeric, encoded_df], axis=1)
        
        # Reorder columns to match original model training columns
        df_processed = df_processed[model_columns]
        
        # Predict class and probability
        prediction = int(model.predict(df_processed)[0])
        probabilities = model.predict_proba(df_processed)[0]
        
        # probability of being a "good" client (class 0) which corresponds to approval rate
        approval_prob = float(probabilities[0])
        
        # Result logic
        # prediction is_bad = 1 means Rejection (High Risk)
        # prediction is_bad = 0 means Approval (Low Risk)
        status = "Approved" if prediction == 0 else "Rejected"
        
        # If approval probability is high, status is Approved.
        # Let's return details
        return jsonify({
            'status': 'success',
            'prediction': prediction,
            'status_label': status,
            'approval_rate': round(approval_prob * 100, 2),
            'rejection_rate': round((1 - approval_prob) * 100, 2),
            'message': "Application Approved! You have a low credit risk profile." if prediction == 0 else "Application Rejected. You have a high credit risk profile."
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

if __name__ == '__main__':
    # Running on local port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
