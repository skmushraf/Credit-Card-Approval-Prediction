import os
import pickle
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix, f1_score, accuracy_score, precision_score, recall_score

def train_and_eval(model, model_name, X_train, y_train, X_test, y_test):
    print(f"\n--- Training {model_name} ---")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    print(f"Accuracy: {acc:.4f}")
    print(f"Precision (Class 1): {prec:.4f}")
    print(f"Recall (Class 1): {rec:.4f}")
    print(f"F1-Score (Class 1): {f1:.4f}")
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))
    
    return {
        "model": model,
        "name": model_name,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1
    }

def main():
    data_dir = r"D:\smartbridge"
    train_path = os.path.join(data_dir, "data", "processed_train.csv")
    test_path = os.path.join(data_dir, "data", "processed_test.csv")
    
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    
    X_train = train_df.drop(columns=['is_bad'])
    y_train = train_df['is_bad']
    X_test = test_df.drop(columns=['is_bad'])
    y_test = test_df['is_bad']
    
    print(f"Training features size: {X_train.shape}")
    print(f"Testing features size: {X_test.shape}")
    
    # Define models (with class balancing to handle extreme imbalance)
    models = {
        "Logistic Regression": LogisticRegression(
            class_weight='balanced', max_iter=2000, random_state=42
        ),
        "Decision Tree": DecisionTreeClassifier(
            class_weight='balanced', max_depth=10, random_state=42
        ),
        "Random Forest": RandomForestClassifier(
            class_weight='balanced', n_estimators=100, max_depth=12, random_state=42
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42
        )
    }
    
    results = []
    for name, model in models.items():
        res = train_and_eval(model, name, X_train, y_train, X_test, y_test)
        results.append(res)
        
    # Story 4: Compare all models and select/save the best-performing one
    print("\n--- Model Comparison Table ---")
    comparison_df = pd.DataFrame(results).drop(columns=['model'])
    print(comparison_df.to_string(index=False))
    
    # Select the model with the highest F1-Score on the minority class
    # (Since accuracy is high simply by predicting all 0s, F1-score is a much better metric)
    best_idx = comparison_df['f1'].idxmax()
    best_model_name = comparison_df.iloc[best_idx]['name']
    best_model = results[best_idx]['model']
    print(f"\nBest model selected based on Class 1 F1-score: {best_model_name}")
    
    models_dir = os.path.join(data_dir, "models")
    best_model_path = os.path.join(models_dir, "best_model.pkl")
    with open(best_model_path, 'wb') as f:
        pickle.dump(best_model, f)
    print(f"Saved the best model to {best_model_path}")
    
    # Also save the model columns for the web app to verify feature order
    columns_path = os.path.join(models_dir, "model_columns.pkl")
    with open(columns_path, 'wb') as f:
        pickle.dump(list(X_train.columns), f)
    print(f"Saved model column list to {columns_path}")

if __name__ == "__main__":
    main()
