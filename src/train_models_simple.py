"""
Simple Model Training Script for Dashboard
Trains and saves churn and CLV models without matplotlib dependency
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, roc_auc_score, r2_score, mean_absolute_error
import pickle
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("TRAINING PREDICTIVE MODELS FOR DASHBOARD")
print("="*80)

# ============================================================================
# 1. LOAD DATA
# ============================================================================
print("\n[1/4] Loading data...")
try:
    rfm_data = pd.read_csv('../data/processed/rfm_with_predictions.csv')
    print(f"SUCCESS: Loaded {len(rfm_data):,} customers")
except FileNotFoundError:
    print("ERROR: rfm_with_predictions.csv not found")
    print("Please ensure the data file exists in ../data/processed/")
    exit(1)

# ============================================================================
# 2. CHURN PREDICTION MODEL
# ============================================================================
print("\n[2/4] Training Churn Prediction Model...")

# Define churn if not already in data
if 'Is_Churned' not in rfm_data.columns:
    CHURN_THRESHOLD = 90
    rfm_data['Is_Churned'] = (rfm_data['Recency'] > CHURN_THRESHOLD).astype(int)
    print(f"  Defined churn threshold: {CHURN_THRESHOLD} days")

# Prepare features
churn_features = ['Frequency', 'Monetary', 'Recency']

# Add optional features if they exist
optional_features = ['Avg_Order_Value', 'Customer_Age_Days', 'Purchase_Rate',
                     'Total_Items_Sold', 'R_Score', 'F_Score', 'M_Score']
for feat in optional_features:
    if feat in rfm_data.columns:
        churn_features.append(feat)

# Handle category features
category_cols = [col for col in rfm_data.columns if col.startswith('Category_')]
churn_features.extend(category_cols)

# Encode Customer_Type if exists
if 'Customer_Type' in rfm_data.columns:
    le_customer = LabelEncoder()
    rfm_data['Customer_Type_Encoded'] = le_customer.fit_transform(rfm_data['Customer_Type'])
    churn_features.append('Customer_Type_Encoded')

# Prepare data
X_churn = rfm_data[churn_features].fillna(0)
y_churn = rfm_data['Is_Churned']

# Train-test split
X_train_churn, X_test_churn, y_train_churn, y_test_churn = train_test_split(
    X_churn, y_churn, test_size=0.2, random_state=42, stratify=y_churn
)

# Train model
churn_model = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    random_state=42,
    subsample=0.8
)

churn_model.fit(X_train_churn, y_train_churn)

# Evaluate
y_pred_churn = churn_model.predict(X_test_churn)
y_pred_proba = churn_model.predict_proba(X_test_churn)[:, 1]
accuracy = accuracy_score(y_test_churn, y_pred_churn)
auc_roc = roc_auc_score(y_test_churn, y_pred_proba)

print(f"  Accuracy: {accuracy*100:.1f}%")
print(f"  AUC-ROC: {auc_roc:.3f}")

# Save model and feature list
with open('churn_model.pkl', 'wb') as f:
    pickle.dump(churn_model, f)
with open('churn_features.pkl', 'wb') as f:
    pickle.dump(churn_features, f)
print("  Saved churn_model.pkl and churn_features.pkl")

# ============================================================================
# 3. CLV PREDICTION MODEL
# ============================================================================
print("\n[3/4] Training CLV Prediction Model...")

# Prepare features
clv_features = ['Frequency', 'Recency']

# Add optional features
optional_clv_features = ['Avg_Order_Value', 'Customer_Age_Days', 'Purchase_Rate',
                         'Total_Items_Sold', 'R_Score', 'F_Score', 'M_Score']
for feat in optional_clv_features:
    if feat in rfm_data.columns:
        clv_features.append(feat)

clv_features.extend(category_cols)

if 'Customer_Type_Encoded' in rfm_data.columns:
    clv_features.append('Customer_Type_Encoded')

# Filter out zero monetary customers
clv_data = rfm_data[rfm_data['Monetary'] > 0].copy()

X_clv = clv_data[clv_features].fillna(0)
y_clv = clv_data['Monetary']

# Train-test split
X_train_clv, X_test_clv, y_train_clv, y_test_clv = train_test_split(
    X_clv, y_clv, test_size=0.2, random_state=42
)

# Train model
clv_model = GradientBoostingRegressor(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    random_state=42,
    subsample=0.8
)

clv_model.fit(X_train_clv, y_train_clv)

# Evaluate
y_pred_clv = clv_model.predict(X_test_clv)
r2 = r2_score(y_test_clv, y_pred_clv)
mae = mean_absolute_error(y_test_clv, y_pred_clv)

print(f"  R2 Score: {r2:.3f}")
print(f"  MAE: ₦{mae:,.0f}")

# Save model and feature list
with open('clv_model.pkl', 'wb') as f:
    pickle.dump(clv_model, f)
with open('clv_features.pkl', 'wb') as f:
    pickle.dump(clv_features, f)
print("  Saved clv_model.pkl and clv_features.pkl")

# ============================================================================
# 4. SAVE FEATURE STATISTICS FOR INPUT VALIDATION
# ============================================================================
print("\n[4/4] Saving feature statistics...")

feature_stats = {
    'churn_features': churn_features,
    'clv_features': clv_features,
    'feature_ranges': {
        'Recency': {'min': float(rfm_data['Recency'].min()),
                    'max': float(rfm_data['Recency'].max()),
                    'mean': float(rfm_data['Recency'].mean())},
        'Frequency': {'min': float(rfm_data['Frequency'].min()),
                      'max': float(rfm_data['Frequency'].max()),
                      'mean': float(rfm_data['Frequency'].mean())},
        'Monetary': {'min': float(rfm_data['Monetary'].min()),
                     'max': float(rfm_data['Monetary'].max()),
                     'mean': float(rfm_data['Monetary'].mean())},
    }
}

# Add optional feature ranges
for feat in ['Avg_Order_Value', 'Customer_Age_Days', 'Purchase_Rate', 'Total_Items_Sold']:
    if feat in rfm_data.columns:
        feature_stats['feature_ranges'][feat] = {
            'min': float(rfm_data[feat].min()),
            'max': float(rfm_data[feat].max()),
            'mean': float(rfm_data[feat].mean())
        }

with open('feature_stats.pkl', 'wb') as f:
    pickle.dump(feature_stats, f)
print("  Saved feature_stats.pkl")

print("\n" + "="*80)
print("SUCCESS: MODEL TRAINING COMPLETE!")
print("="*80)
print("\nFiles created:")
print("  - churn_model.pkl")
print("  - churn_features.pkl")
print("  - clv_model.pkl")
print("  - clv_features.pkl")
print("  - feature_stats.pkl")
print("\nYou can now use these models in the dashboard!")
