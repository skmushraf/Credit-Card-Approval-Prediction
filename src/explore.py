import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    # 1. Imports and environment setup (Story 1)
    sns.set_theme(style="whitegrid")
    
    data_dir = r"D:\smartbridge"
    plots_dir = os.path.join(data_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)
    
    app_path = os.path.join(data_dir, "data", "application_record.csv")
    credit_path = os.path.join(data_dir, "data", "credit_record.csv")
    
    print("--- Story 2: Read and explore the dataset ---")
    app = pd.read_csv(app_path)
    credit = pd.read_csv(credit_path)
    
    print(f"Application Record Shape: {app.shape}")
    print(f"Credit Record Shape: {credit.shape}")
    
    print("\nApplication Record Columns:")
    print(app.columns.tolist())
    print("\nCredit Record Columns:")
    print(credit.columns.tolist())
    
    # 2. Target Variable Definition (Story 2 continued)
    # Status: '0' (1-29 days past due), '1' (30-59 days past due), '2' (60-89 days overdue),
    #         '3' (90-119 days overdue), '4' (120-149 days overdue), '5' (overdue/bad debt > 150 days),
    #         'C' (paid off), 'X' (no loan)
    # Define "bad" (1 - rejected) as any status in '2', '3', '4', '5'.
    # Define "good" (0 - approved) otherwise.
    print("\nProcessing Credit Record to construct target variable...")
    credit['is_bad'] = credit['STATUS'].isin(['2', '3', '4', '5']).astype(int)
    
    # Group by ID to see if the customer was ever "bad"
    customer_target = credit.groupby('ID')['is_bad'].max().reset_index()
    print(f"Unique customers in Credit Record: {customer_target['ID'].nunique()}")
    print("Target distribution (0 = Approved, 1 = Rejected):")
    print(customer_target['is_bad'].value_counts())
    print(customer_target['is_bad'].value_counts(normalize=True))
    
    # 3. Descriptive Statistical Analysis (Story 5)
    print("\n--- Story 5: Descriptive Statistical Analysis ---")
    stats_file = os.path.join(plots_dir, "descriptive_stats.txt")
    with open(stats_file, 'w') as f:
        f.write("=== Application Record Descriptive Stats ===\n")
        f.write(app.describe(include='all').to_string())
        f.write("\n\n=== Credit Record Descriptive Stats ===\n")
        f.write(credit.describe(include='all').to_string())
        f.write("\n\n=== Missing Values in Application Record ===\n")
        f.write(app.isnull().sum().to_string())
        f.write("\n\n=== Missing Values in Credit Record ===\n")
        f.write(credit.isnull().sum().to_string())
    print(f"Saved descriptive stats to {stats_file}")
    
    # 4. Univariate Analysis (Story 3)
    print("\n--- Story 3: Perform univariate analysis ---")
    
    # Occupation Type Countplot (matches user upload)
    print("Generating OCCUPATION_TYPE countplot...")
    print("Number of people working status :")
    print(app['OCCUPATION_TYPE'].value_counts(dropna=False))
    
    plt.figure(figsize=(18, 6))
    # Replace NaN with 'Unknown' for plotting
    app_plot = app.copy()
    app_plot['OCCUPATION_TYPE'] = app_plot['OCCUPATION_TYPE'].fillna('Unknown')
    sns.countplot(x='OCCUPATION_TYPE', data=app_plot, palette='Set2')
    plt.title("Distribution of Occupation Types")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "univariate_occupation.png"))
    plt.close()
    
    # Income Distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(app['AMT_INCOME_TOTAL'], kde=True, bins=50, color='skyblue')
    plt.title("Distribution of Annual Income")
    plt.xlabel("Annual Income")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "univariate_income.png"))
    plt.close()
    
    # 5. Multivariate Analysis (Story 4)
    print("\n--- Story 4: Conduct multivariate analysis ---")
    # Merge datasets to analyze relations with target
    df = pd.merge(app, customer_target, on='ID', how='inner')
    print(f"Merged Dataset Shape (customers with application and credit history): {df.shape}")
    
    # Correlation of numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    corr = df[numeric_cols].corr()
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title("Correlation Heatmap of Numerical Features")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "multivariate_correlation.png"))
    plt.close()
    
    # Occupation vs Target Rate
    plt.figure(figsize=(14, 6))
    df_plot = df.copy()
    df_plot['OCCUPATION_TYPE'] = df_plot['OCCUPATION_TYPE'].fillna('Unknown')
    # Calculate Bad Customer Rate (%) by occupation
    bad_rate = df_plot.groupby('OCCUPATION_TYPE')['is_bad'].mean().reset_index()
    bad_rate['is_bad'] = bad_rate['is_bad'] * 100
    bad_rate = bad_rate.sort_values(by='is_bad', ascending=False)
    
    sns.barplot(x='OCCUPATION_TYPE', y='is_bad', data=bad_rate, palette='Oranges_r')
    plt.title("Bad Customer (Rejection) Rate by Occupation Type (%)")
    plt.xlabel("Occupation Type")
    plt.ylabel("Rejection Rate (%)")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "multivariate_occupation_vs_target.png"))
    plt.close()
    
    print(f"All exploratory analysis and plots successfully saved to {plots_dir}")

if __name__ == "__main__":
    main()
