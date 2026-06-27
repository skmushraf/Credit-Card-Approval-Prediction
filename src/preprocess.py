import os
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder

def main():
    data_dir = r"D:\smartbridge"
    app_path = os.path.join(data_dir, "data", "application_record.csv")
    credit_path = os.path.join(data_dir, "data", "credit_record.csv")
    
    print("Loading datasets...")
    app = pd.read_csv(app_path)
    credit = pd.read_csv(credit_path)
    
    # Story 1: Identify and remove duplicate records in application_record
    print(f"Initial application record size: {app.shape}")
    app = app.drop_duplicates(subset='ID', keep='last')
    print(f"Application record size after removing ID duplicates: {app.shape}")
    
    # Story 2: Detect and handle missing values
    # Fill missing OCCUPATION_TYPE with 'Unknown'
    app['OCCUPATION_TYPE'] = app['OCCUPATION_TYPE'].fillna('Unknown')
    
    # Story 4: Feature engineering on Credit Record (generate target variable)
    # Define "bad" (1 - rejected) as any status in '2', '3', '4', '5'
    credit['is_bad'] = credit['STATUS'].isin(['2', '3', '4', '5']).astype(int)
    customer_target = credit.groupby('ID')['is_bad'].max().reset_index()
    
    # Story 3: Perform data cleaning and merging operations
    df = pd.merge(app, customer_target, on='ID', how='inner')
    print(f"Merged dataset shape (inner join on ID): {df.shape}")
    
    # Story 4: Apply feature engineering techniques on merged dataset
    # Convert birth days to age (years)
    df['AGE'] = -df['DAYS_BIRTH'] // 365
    
    # Convert employment days to years employed (0 if unemployed/retired)
    df['YEARS_EMPLOYED'] = np.where(df['DAYS_EMPLOYED'] < 0, -df['DAYS_EMPLOYED'] // 365, 0)
    df['UNEMPLOYED'] = (df['DAYS_EMPLOYED'] > 0).astype(int)
    
    # Binary variables encoding (0 or 1)
    df['CODE_GENDER'] = df['CODE_GENDER'].map({'F': 0, 'M': 1})
    df['FLAG_OWN_CAR'] = df['FLAG_OWN_CAR'].map({'N': 0, 'Y': 1})
    df['FLAG_OWN_REALTY'] = df['FLAG_OWN_REALTY'].map({'N': 0, 'Y': 1})
    
    # Drop columns that are no longer needed
    cols_to_drop = ['ID', 'DAYS_BIRTH', 'DAYS_EMPLOYED', 'FLAG_MOBIL']
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns])
    
    # Story 5: Convert categorical variables into numerical representations
    categorical_cols = [
        'NAME_INCOME_TYPE', 
        'NAME_EDUCATION_TYPE', 
        'NAME_FAMILY_STATUS', 
        'NAME_HOUSING_TYPE', 
        'OCCUPATION_TYPE'
    ]
    
    # One-hot encode categorical columns
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    encoded_features = encoder.fit_transform(df[categorical_cols])
    
    # Get feature names for encoding
    encoded_feature_names = encoder.get_feature_names_out(categorical_cols)
    encoded_df = pd.DataFrame(encoded_features, columns=encoded_feature_names)
    
    # Drop original categorical columns and concatenate encoded ones
    df_numeric = df.drop(columns=categorical_cols).reset_index(drop=True)
    df_processed = pd.concat([df_numeric, encoded_df], axis=1)
    
    print(f"Processed dataset shape: {df_processed.shape}")
    print("Class distribution in processed dataset:")
    print(df_processed['is_bad'].value_counts())
    
    # Save processed files
    models_dir = os.path.join(data_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    
    # Save the fitted encoder
    encoder_path = os.path.join(models_dir, "encoder.pkl")
    with open(encoder_path, 'wb') as f:
        pickle.dump(encoder, f)
    print(f"Saved fitted OneHotEncoder to {encoder_path}")
    
    # Split into train and test sets (80-20 split, stratified on target due to imbalance)
    X = df_processed.drop(columns=['is_bad'])
    y = df_processed['is_bad']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    train_df = pd.concat([X_train, y_train], axis=1)
    test_df = pd.concat([X_test, y_test], axis=1)
    
    train_path = os.path.join(data_dir, "data", "processed_train.csv")
    test_path = os.path.join(data_dir, "data", "processed_test.csv")
    
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    
    print(f"Saved processed train set to {train_path} ({train_df.shape})")
    print(f"Saved processed test set to {test_path} ({test_df.shape})")

if __name__ == "__main__":
    main()
