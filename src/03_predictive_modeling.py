"""
AFRIMASH CUSTOMER INTELLIGENCE CHALLENGE
Hour 5-6: Predictive Modeling
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (classification_report, confusion_matrix, roc_auc_score,
                             roc_curve, mean_squared_error, r2_score, mean_absolute_error)
import pickle
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)

print("="*80)
print("AFRIMASH PREDICTIVE MODELING")
print("="*80)

# ============================================================================
# 1. LOAD SEGMENTED DATA
# ============================================================================
print("\n📁 STEP 1: LOADING SEGMENTED DATA...")
try:
    rfm_df = pd.read_csv('rfm_segmented.csv')
    print(f"✓ Loaded {len(rfm_df):,} customers with segments")
except FileNotFoundError:
    # Fallback to clean data if segmented doesn't exist
    rfm_df = pd.read_csv('rfm_clean.csv')
    print(f"✓ Loaded {len(rfm_df):,} customers (clean data)")

# ============================================================================
# 2. CHURN PREDICTION MODEL
# ============================================================================
print("\n🔮 STEP 2: BUILDING CHURN PREDICTION MODEL...")

# 2.1 Define churn (customers inactive for >90 days)
CHURN_THRESHOLD = 90
rfm_df['Is_Churned'] = (rfm_df['Recency'] > CHURN_THRESHOLD).astype(int)

print(f"✓ Defined churn threshold: {CHURN_THRESHOLD} days")
print(f"  Churned customers: {rfm_df['Is_Churned'].sum():,} ({rfm_df['Is_Churned'].mean()*100:.1f}%)")
print(f"  Active customers: {(1-rfm_df['Is_Churned']).sum():,} ({(1-rfm_df['Is_Churned'].mean())*100:.1f}%)")

# 2.2 Prepare features for churn prediction
churn_features = ['Frequency', 'Monetary', 'Avg_Order_Value', 'Customer_Age_Days',
                  'Purchase_Rate', 'Recency', 'Total_Items_Sold']

# Add category features if they exist
category_cols = [col for col in rfm_df.columns if col.startswith('Category_')]
churn_features.extend(category_cols)

# Add RFM scores if they exist
if 'R_Score' in rfm_df.columns:
    churn_features.extend(['R_Score', 'F_Score', 'M_Score'])

# Encode Customer_Type if exists
if 'Customer_Type' in rfm_df.columns:
    le_customer = LabelEncoder()
    rfm_df['Customer_Type_Encoded'] = le_customer.fit_transform(rfm_df['Customer_Type'])
    churn_features.append('Customer_Type_Encoded')

# Handle missing values
X_churn = rfm_df[churn_features].fillna(0)
y_churn = rfm_df['Is_Churned']

# 2.3 Train-test split
X_train_churn, X_test_churn, y_train_churn, y_test_churn = train_test_split(
    X_churn, y_churn, test_size=0.2, random_state=42, stratify=y_churn
)

print(f"\n✓ Training set: {len(X_train_churn):,} samples")
print(f"✓ Test set: {len(X_test_churn):,} samples")

# 2.4 Train Gradient Boosting Classifier
print("\n🤖 Training Gradient Boosting Classifier...")
churn_model = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    random_state=42,
    subsample=0.8
)

churn_model.fit(X_train_churn, y_train_churn)

# 2.5 Make predictions
y_pred_churn = churn_model.predict(X_test_churn)
y_pred_proba_churn = churn_model.predict_proba(X_test_churn)[:, 1]

# 2.6 Evaluate model
from sklearn.metrics import accuracy_score
accuracy = accuracy_score(y_test_churn, y_pred_churn)
auc_roc = roc_auc_score(y_test_churn, y_pred_proba_churn)

print(f"\n✓ Churn Model Performance:")
print(f"  Accuracy: {accuracy*100:.1f}%")
print(f"  AUC-ROC: {auc_roc:.3f}")

# 2.7 Predict churn probability for all customers
rfm_df['Churn_Probability'] = churn_model.predict_proba(X_churn)[:, 1]

# 2.8 Categorize churn risk
def categorize_churn_risk(prob):
    if prob < 0.3:
        return 'Low'
    elif prob < 0.5:
        return 'Medium'
    elif prob < 0.7:
        return 'High'
    else:
        return 'Critical'

rfm_df['Churn_Risk_Level'] = rfm_df['Churn_Probability'].apply(categorize_churn_risk)

print(f"\n✓ Churn Risk Distribution:")
print(rfm_df['Churn_Risk_Level'].value_counts())

# 2.9 Save churn model
with open('churn_model.pkl', 'wb') as f:
    pickle.dump(churn_model, f)
print("\n✓ Saved churn_model.pkl")

# ============================================================================
# 3. CUSTOMER LIFETIME VALUE (CLV) PREDICTION
# ============================================================================
print("\n💰 STEP 3: BUILDING CLV PREDICTION MODEL...")

# 3.1 Calculate actual CLV (historical monetary + expected future value)
# For simplicity, we'll predict future value based on current patterns
rfm_df['Historical_CLV'] = rfm_df['Monetary']

# 3.2 Prepare features for CLV prediction
clv_features = ['Frequency', 'Avg_Order_Value', 'Customer_Age_Days',
                'Purchase_Rate', 'Recency', 'Total_Items_Sold']

# Add category features
clv_features.extend(category_cols)

# Add RFM scores
if 'R_Score' in rfm_df.columns:
    clv_features.extend(['R_Score', 'F_Score', 'M_Score'])

if 'Customer_Type_Encoded' in rfm_df.columns:
    clv_features.append('Customer_Type_Encoded')

# Filter out customers with very low monetary value for better predictions
clv_data = rfm_df[rfm_df['Monetary'] > 0].copy()

X_clv = clv_data[clv_features].fillna(0)
y_clv = clv_data['Monetary']  # Predict based on historical monetary

# 3.3 Train-test split
X_train_clv, X_test_clv, y_train_clv, y_test_clv = train_test_split(
    X_clv, y_clv, test_size=0.2, random_state=42
)

print(f"\n✓ Training set: {len(X_train_clv):,} samples")
print(f"✓ Test set: {len(X_test_clv):,} samples")

# 3.4 Train Gradient Boosting Regressor
print("\n🤖 Training Gradient Boosting Regressor...")
clv_model = GradientBoostingRegressor(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    random_state=42,
    subsample=0.8
)

clv_model.fit(X_train_clv, y_train_clv)

# 3.5 Make predictions
y_pred_clv = clv_model.predict(X_test_clv)

# 3.6 Evaluate model
r2 = r2_score(y_test_clv, y_pred_clv)
mae = mean_absolute_error(y_test_clv, y_pred_clv)
rmse = np.sqrt(mean_squared_error(y_test_clv, y_pred_clv))

print(f"\n✓ CLV Model Performance:")
print(f"  R² Score: {r2:.3f} ({r2*100:.1f}% variance explained)")
print(f"  MAE: ₵{mae:,.0f}")
print(f"  RMSE: ₵{rmse:,.0f}")

# 3.7 Predict CLV for all customers
X_all_clv = rfm_df[clv_features].fillna(0)
rfm_df['Predicted_CLV'] = clv_model.predict(X_all_clv)

# Ensure non-negative CLV
rfm_df['Predicted_CLV'] = rfm_df['Predicted_CLV'].clip(lower=0)

# 3.8 Calculate 6-month CLV projection
rfm_df['CLV_6_Month'] = rfm_df['Predicted_CLV'] * 0.5  # Assume 50% in 6 months

# 3.9 Categorize CLV
clv_percentiles = rfm_df['Predicted_CLV'].quantile([0.25, 0.50, 0.75, 0.90])

def categorize_clv(clv):
    if clv >= clv_percentiles[0.90]:
        return 'Very High Value'
    elif clv >= clv_percentiles[0.75]:
        return 'High Value'
    elif clv >= clv_percentiles[0.50]:
        return 'Medium Value'
    elif clv >= clv_percentiles[0.25]:
        return 'Low Value'
    else:
        return 'Very Low Value'

rfm_df['CLV_Category'] = rfm_df['Predicted_CLV'].apply(categorize_clv)

print(f"\n✓ CLV Distribution:")
print(rfm_df['CLV_Category'].value_counts())
print(f"\n  Total Predicted CLV: ₵{rfm_df['Predicted_CLV'].sum()/1e9:.2f}B")
print(f"  Average CLV: ₵{rfm_df['Predicted_CLV'].mean()/1e6:.2f}M")

# 3.10 Save CLV model
with open('clv_model.pkl', 'wb') as f:
    pickle.dump(clv_model, f)
print("\n✓ Saved clv_model.pkl")

# ============================================================================
# 4. PURCHASE TIMING PREDICTION
# ============================================================================
print("\n⏰ STEP 4: PURCHASE TIMING ANALYSIS...")

# 4.1 Calculate expected days to next purchase
rfm_df['Days_Between_Purchases'] = rfm_df['Customer_Age_Days'] / rfm_df['Frequency'].replace(0, 1)
rfm_df['Expected_Days_to_Next_Purchase'] = rfm_df['Days_Between_Purchases']

# 4.2 Calculate days since last purchase and days overdue
rfm_df['Days_Since_Last_Purchase'] = rfm_df['Recency']
rfm_df['Days_Overdue'] = (rfm_df['Days_Since_Last_Purchase'] -
                          rfm_df['Expected_Days_to_Next_Purchase']).clip(lower=0)

# 4.3 Categorize purchase timing status
def categorize_purchase_timing(row):
    days_since = row['Days_Since_Last_Purchase']
    expected_days = row['Expected_Days_to_Next_Purchase']

    if row['Frequency'] == 1:
        return 'New/One-time'
    elif days_since < expected_days * 0.8:
        return 'Due Soon'
    elif days_since < expected_days * 1.2:
        return 'On Track'
    elif days_since < expected_days * 2:
        return 'Slightly Overdue'
    elif days_since < expected_days * 3:
        return 'Overdue'
    else:
        return 'Severely Overdue'

rfm_df['Purchase_Timing_Status'] = rfm_df.apply(categorize_purchase_timing, axis=1)

print(f"\n✓ Purchase Timing Distribution:")
print(rfm_df['Purchase_Timing_Status'].value_counts())

# 4.4 Calculate purchase probability in next 30 days
def calculate_purchase_probability(row):
    if row['Frequency'] == 1:
        return 0.3  # 30% chance for one-time customers
    elif row['Purchase_Timing_Status'] == 'Due Soon':
        return 0.8
    elif row['Purchase_Timing_Status'] == 'On Track':
        return 0.6
    elif row['Purchase_Timing_Status'] == 'Slightly Overdue':
        return 0.4
    elif row['Purchase_Timing_Status'] == 'Overdue':
        return 0.2
    else:
        return 0.1

rfm_df['Purchase_Probability_30_Days'] = rfm_df.apply(calculate_purchase_probability, axis=1)

# ============================================================================
# 5. CUSTOMER PRIORITY SCORING
# ============================================================================
print("\n🎯 STEP 5: CUSTOMER PRIORITY SCORING...")

# 5.1 Calculate customer value score (combination of CLV and churn risk)
rfm_df['Customer_Value_Score'] = (
    (rfm_df['Predicted_CLV'] / rfm_df['Predicted_CLV'].max() * 50) +  # 0-50 points
    (rfm_df['Churn_Probability'] * 50)  # 0-50 points (higher churn = higher priority)
)

# 5.2 Categorize customer priority
def categorize_priority(row):
    clv = row['Predicted_CLV']
    churn_prob = row['Churn_Probability']

    high_clv = clv > rfm_df['Predicted_CLV'].quantile(0.75)
    high_churn = churn_prob > 0.5

    if high_clv and high_churn:
        return 'CRITICAL - High Value at Risk'
    elif high_clv:
        return 'High - Protect VIP'
    elif high_churn and clv > rfm_df['Predicted_CLV'].quantile(0.5):
        return 'Medium - Win Back'
    else:
        return 'Low - Standard Engagement'

rfm_df['Customer_Priority'] = rfm_df.apply(categorize_priority, axis=1)

# Simplify for display
rfm_df['Customer_Priority'] = rfm_df['Customer_Priority'].str.split(' - ').str[0]

print(f"\n✓ Customer Priority Distribution:")
print(rfm_df['Customer_Priority'].value_counts())

# ============================================================================
# 6. SAVE PREDICTIONS
# ============================================================================
print("\n💾 STEP 6: SAVING PREDICTIONS...")

# Save complete dataset with all predictions
rfm_df.to_csv('rfm_with_predictions.csv', index=False)
print(f"✓ Saved rfm_with_predictions.csv ({len(rfm_df):,} customers)")

# Save high-risk customers
high_risk = rfm_df[
    (rfm_df['Churn_Risk_Level'].isin(['High', 'Critical'])) &
    (rfm_df['Monetary'] > rfm_df['Monetary'].quantile(0.5))
].sort_values('Monetary', ascending=False)

high_risk_export = high_risk[['Customer_ID', 'RFM_Segment', 'Monetary', 'Predicted_CLV',
                               'Churn_Probability', 'Churn_Risk_Level', 'Customer_Priority']]
high_risk_export.to_csv('high_risk_customers.csv', index=False)
print(f"✓ Saved high_risk_customers.csv ({len(high_risk):,} customers)")

# Save high-value opportunities
high_value = rfm_df[
    rfm_df['Predicted_CLV'] > rfm_df['Predicted_CLV'].quantile(0.90)
].sort_values('Predicted_CLV', ascending=False)

high_value_export = high_value[['Customer_ID', 'RFM_Segment', 'Monetary', 'Predicted_CLV',
                                 'Churn_Probability', 'CLV_Category']]
high_value_export.to_csv('high_value_opportunities.csv', index=False)
print(f"✓ Saved high_value_opportunities.csv ({len(high_value):,} customers)")

# Save action priority list
action_priority = rfm_df.sort_values('Customer_Value_Score', ascending=False)
action_priority_export = action_priority[['Customer_ID', 'RFM_Segment', 'Monetary',
                                          'Predicted_CLV', 'Churn_Probability',
                                          'Purchase_Timing_Status', 'Customer_Priority',
                                          'Customer_Value_Score']]
action_priority_export.to_csv('action_priority_list.csv', index=False)
print(f"✓ Saved action_priority_list.csv ({len(action_priority):,} customers)")

# Save model summary
model_summary = pd.DataFrame({
    'Model': ['Churn Prediction (Gradient Boosting)', 'CLV Prediction (Gradient Boosting/RF)'],
    'Accuracy/R²': [f'{auc_roc:.3f} (AUC-ROC)', f'{r2:.3f} (R²)'],
    'Training_Samples': [len(X_train_churn), len(X_train_clv)],
    'Test_Samples': [len(X_test_churn), len(X_test_clv)],
    'Features_Used': [len(churn_features), len(clv_features)]
})
model_summary.to_csv('model_summary.csv', index=False)
print(f"✓ Saved model_summary.csv")

# Save prediction impact summary
impact_summary = pd.DataFrame({
    'Metric': ['Total Customers', 'Churned Customers', 'High Risk Customers',
               'Total Predicted CLV', 'High Value Customers (Top 10%)',
               'Due Soon Customers', 'Critical Priority Customers'],
    'Value': [
        f"{len(rfm_df):,}",
        f"{rfm_df['Is_Churned'].sum():,} ({rfm_df['Is_Churned'].mean()*100:.1f}%)",
        f"{len(high_risk):,}",
        f"₵{rfm_df['Predicted_CLV'].sum()/1e9:.2f}B",
        f"{len(high_value):,}",
        f"{len(rfm_df[rfm_df['Purchase_Timing_Status']=='Due Soon']):,}",
        f"{len(rfm_df[rfm_df['Customer_Priority']=='CRITICAL']):,}"
    ]
})
impact_summary.to_csv('prediction_impact_summary.csv', index=False)
print(f"✓ Saved prediction_impact_summary.csv")

# ============================================================================
# 7. VISUALIZATIONS
# ============================================================================
print("\n📊 STEP 7: CREATING VISUALIZATIONS...")

# Churn Prediction Analysis
fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.suptitle('CHURN PREDICTION ANALYSIS', fontsize=20, fontweight='bold')

# 7.1 Churn Distribution
ax = axes[0, 0]
churn_dist = rfm_df['Is_Churned'].value_counts()
colors = ['#28a745', '#dc3545']
ax.pie(churn_dist.values, labels=['Active', 'Churned'], autopct='%1.1f%%',
       colors=colors, startangle=90)
ax.set_title('Churn Distribution', fontsize=14, fontweight='bold')

# 7.2 ROC Curve
ax = axes[0, 1]
fpr, tpr, _ = roc_curve(y_test_churn, y_pred_proba_churn)
ax.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {auc_roc:.3f})')
ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random')
ax.set_xlabel('False Positive Rate')
ax.set_ylabel('True Positive Rate')
ax.set_title('ROC Curve - Churn Prediction', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)

# 7.3 Feature Importance - Churn
ax = axes[0, 2]
feature_importance_churn = pd.DataFrame({
    'Feature': churn_features,
    'Importance': churn_model.feature_importances_
}).sort_values('Importance', ascending=False).head(10)

ax.barh(range(len(feature_importance_churn)), feature_importance_churn['Importance'])
ax.set_yticks(range(len(feature_importance_churn)))
ax.set_yticklabels(feature_importance_churn['Feature'])
ax.set_xlabel('Importance')
ax.set_title('Top 10 Features - Churn Prediction', fontsize=14, fontweight='bold')
ax.invert_yaxis()

# 7.4 Churn Risk Distribution
ax = axes[1, 0]
risk_counts = rfm_df['Churn_Risk_Level'].value_counts()
risk_order = ['Low', 'Medium', 'High', 'Critical']
risk_counts = risk_counts.reindex(risk_order, fill_value=0)
risk_colors = {'Low': '#28a745', 'Medium': '#ffc107', 'High': '#fd7e14', 'Critical': '#dc3545'}
colors = [risk_colors[x] for x in risk_order]
ax.bar(risk_order, risk_counts.values, color=colors)
ax.set_title('Churn Risk Level Distribution', fontsize=14, fontweight='bold')
ax.set_ylabel('Number of Customers')
for i, v in enumerate(risk_counts.values):
    ax.text(i, v, f'{v:,}', ha='center', va='bottom')

# 7.5 Churn Probability Distribution
ax = axes[1, 1]
ax.hist(rfm_df['Churn_Probability'], bins=50, color='steelblue', edgecolor='black', alpha=0.7)
ax.axvline(0.5, color='red', linestyle='--', linewidth=2, label='50% Threshold')
ax.set_xlabel('Churn Probability')
ax.set_ylabel('Number of Customers')
ax.set_title('Churn Probability Distribution', fontsize=14, fontweight='bold')
ax.legend()

# 7.6 Confusion Matrix
ax = axes[1, 2]
cm = confusion_matrix(y_test_churn, y_pred_churn)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax, cbar=False)
ax.set_xlabel('Predicted')
ax.set_ylabel('Actual')
ax.set_title('Confusion Matrix', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('churn_prediction_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Saved churn_prediction_analysis.png")

# CLV Prediction Analysis
fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.suptitle('CLV PREDICTION ANALYSIS', fontsize=20, fontweight='bold')

# 7.7 CLV Category Distribution
ax = axes[0, 0]
clv_counts = rfm_df['CLV_Category'].value_counts()
colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(clv_counts)))
clv_counts.plot(kind='bar', ax=ax, color=colors)
ax.set_title('CLV Category Distribution', fontsize=14, fontweight='bold')
ax.set_ylabel('Number of Customers')
ax.set_xlabel('CLV Category')
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
for i, v in enumerate(clv_counts.values):
    ax.text(i, v, f'{v:,}', ha='center', va='bottom')

# 7.8 Actual vs Predicted CLV
ax = axes[0, 1]
sample_indices = np.random.choice(len(y_test_clv), min(1000, len(y_test_clv)), replace=False)
ax.scatter(y_test_clv.iloc[sample_indices], y_pred_clv[sample_indices],
           alpha=0.5, s=20, color='steelblue')
ax.plot([y_test_clv.min(), y_test_clv.max()],
        [y_test_clv.min(), y_test_clv.max()],
        'r--', lw=2, label='Perfect Prediction')
ax.set_xlabel('Actual CLV (₵)')
ax.set_ylabel('Predicted CLV (₵)')
ax.set_title(f'Actual vs Predicted CLV (R² = {r2:.3f})', fontsize=14, fontweight='bold')
ax.legend()
ax.set_xscale('log')
ax.set_yscale('log')
ax.grid(True, alpha=0.3)

# 7.9 Feature Importance - CLV
ax = axes[0, 2]
feature_importance_clv = pd.DataFrame({
    'Feature': clv_features,
    'Importance': clv_model.feature_importances_
}).sort_values('Importance', ascending=False).head(10)

ax.barh(range(len(feature_importance_clv)), feature_importance_clv['Importance'], color='green', alpha=0.7)
ax.set_yticks(range(len(feature_importance_clv)))
ax.set_yticklabels(feature_importance_clv['Feature'])
ax.set_xlabel('Importance')
ax.set_title('Top 10 Features - CLV Prediction', fontsize=14, fontweight='bold')
ax.invert_yaxis()

# 7.10 CLV Distribution
ax = axes[1, 0]
ax.hist(rfm_df['Predicted_CLV'], bins=50, color='green', edgecolor='black', alpha=0.7)
ax.set_xlabel('Predicted CLV (₵)')
ax.set_ylabel('Number of Customers')
ax.set_title('Predicted CLV Distribution', fontsize=14, fontweight='bold')
ax.set_xscale('log')
ax.axvline(rfm_df['Predicted_CLV'].median(), color='red', linestyle='--',
           linewidth=2, label=f'Median: ₵{rfm_df["Predicted_CLV"].median()/1e6:.2f}M')
ax.legend()

# 7.11 CLV vs Churn Matrix
ax = axes[1, 1]
scatter = ax.scatter(rfm_df['Churn_Probability'], rfm_df['Predicted_CLV'],
                     c=rfm_df['Customer_Value_Score'], cmap='RdYlGn_r',
                     alpha=0.6, s=30)
ax.set_xlabel('Churn Probability')
ax.set_ylabel('Predicted CLV (₵)')
ax.set_title('CLV vs Churn Risk Matrix', fontsize=14, fontweight='bold')
ax.set_yscale('log')
ax.axvline(0.5, color='red', linestyle='--', linewidth=1, alpha=0.5)
ax.axhline(rfm_df['Predicted_CLV'].median(), color='blue', linestyle='--', linewidth=1, alpha=0.5)
plt.colorbar(scatter, ax=ax, label='Priority Score')
ax.grid(True, alpha=0.3)

# 7.12 Purchase Timing Status
ax = axes[1, 2]
timing_counts = rfm_df['Purchase_Timing_Status'].value_counts()
colors = plt.cm.Spectral(np.linspace(0, 1, len(timing_counts)))
timing_counts.plot(kind='barh', ax=ax, color=colors)
ax.set_title('Purchase Timing Status', fontsize=14, fontweight='bold')
ax.set_xlabel('Number of Customers')
for i, v in enumerate(timing_counts.values):
    ax.text(v, i, f' {v:,}', va='center')

plt.tight_layout()
plt.savefig('clv_prediction_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Saved clv_prediction_analysis.png")

# Customer Priority Matrix
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('CUSTOMER PRIORITY MATRIX', fontsize=18, fontweight='bold')

# Priority Distribution
ax = axes[0, 0]
priority_counts = rfm_df['Customer_Priority'].value_counts()
colors = {'CRITICAL': '#dc3545', 'High': '#fd7e14', 'Medium': '#ffc107', 'Low': '#28a745'}
priority_colors = [colors.get(p, '#6c757d') for p in priority_counts.index]
priority_counts.plot(kind='bar', ax=ax, color=priority_colors)
ax.set_title('Customer Priority Distribution', fontsize=14, fontweight='bold')
ax.set_ylabel('Number of Customers')
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
for i, v in enumerate(priority_counts.values):
    ax.text(i, v, f'{v:,}', ha='center', va='bottom')

# Priority by Revenue
ax = axes[0, 1]
priority_revenue = rfm_df.groupby('Customer_Priority')['Monetary'].sum() / 1e9
priority_revenue.plot(kind='bar', ax=ax, color=priority_colors)
ax.set_title('Total Revenue by Priority (₵ Billions)', fontsize=14, fontweight='bold')
ax.set_ylabel('Revenue (₵B)')
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
for i, v in enumerate(priority_revenue.values):
    ax.text(i, v, f'₵{v:.2f}B', ha='center', va='bottom')

# Top 20 High Priority Customers
ax = axes[1, 0]
top_priority = rfm_df.nlargest(20, 'Customer_Value_Score')[['Customer_ID', 'Customer_Value_Score']]
ax.barh(range(len(top_priority)), top_priority['Customer_Value_Score'], color='darkred', alpha=0.7)
ax.set_yticks(range(len(top_priority)))
ax.set_yticklabels(top_priority['Customer_ID'].values)
ax.set_xlabel('Priority Score')
ax.set_title('Top 20 Highest Priority Customers', fontsize=14, fontweight='bold')
ax.invert_yaxis()

# Quadrant Analysis
ax = axes[1, 1]
high_clv_threshold = rfm_df['Predicted_CLV'].quantile(0.75)
high_churn_threshold = 0.5

for priority in rfm_df['Customer_Priority'].unique():
    subset = rfm_df[rfm_df['Customer_Priority'] == priority]
    ax.scatter(subset['Churn_Probability'], subset['Predicted_CLV'],
               label=priority, alpha=0.6, s=30)

ax.axvline(high_churn_threshold, color='red', linestyle='--', linewidth=1, alpha=0.5)
ax.axhline(high_clv_threshold, color='blue', linestyle='--', linewidth=1, alpha=0.5)
ax.set_xlabel('Churn Probability')
ax.set_ylabel('Predicted CLV (₵)')
ax.set_title('Customer Segmentation Quadrant', fontsize=14, fontweight='bold')
ax.set_yscale('log')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# Add quadrant labels
ax.text(0.25, high_clv_threshold*2, 'Protect\n(High Value, Low Churn)',
        ha='center', va='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
ax.text(0.75, high_clv_threshold*2, 'CRITICAL\n(High Value, High Churn)',
        ha='center', va='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.5))

plt.tight_layout()
plt.savefig('customer_priority_matrix.png', dpi=300, bbox_inches='tight')
print("✓ Saved customer_priority_matrix.png")

# ============================================================================
# 8. MODEL PERFORMANCE SUMMARY
# ============================================================================
print("\n" + "="*80)
print("📊 MODEL PERFORMANCE SUMMARY")
print("="*80)

print("\n🔮 CHURN PREDICTION MODEL:")
print(f"  Algorithm: Gradient Boosting Classifier")
print(f"  Accuracy: {accuracy*100:.1f}%")
print(f"  AUC-ROC: {auc_roc:.3f}")
print(f"  Features Used: {len(churn_features)}")
print(f"\n  Top 3 Important Features:")
for idx, row in feature_importance_churn.head(3).iterrows():
    print(f"    {row['Feature']}: {row['Importance']:.3f}")

print("\n💰 CLV PREDICTION MODEL:")
print(f"  Algorithm: Gradient Boosting Regressor")
print(f"  R² Score: {r2:.3f} ({r2*100:.1f}% variance explained)")
print(f"  MAE: ₵{mae:,.0f}")
print(f"  RMSE: ₵{rmse:,.0f}")
print(f"  Features Used: {len(clv_features)}")
print(f"\n  Top 3 Important Features:")
for idx, row in feature_importance_clv.head(3).iterrows():
    print(f"    {row['Feature']}: {row['Importance']:.3f}")

print("\n🎯 KEY FINDINGS:")
print(f"  High Risk Customers: {len(high_risk):,}")
print(f"  Revenue at Risk: ₵{high_risk['Monetary'].sum()/1e9:.2f}B")
print(f"  High Value Opportunities: {len(high_value):,}")
print(f"  Total Predicted CLV: ₵{rfm_df['Predicted_CLV'].sum()/1e9:.2f}B")

print("\n" + "="*80)
print("✅ PREDICTIVE MODELING COMPLETE!")
print("="*80)
print("\n📁 Output Files:")
print("  1. rfm_with_predictions.csv - Complete predictions")
print("  2. high_risk_customers.csv - Customers at risk")
print("  3. high_value_opportunities.csv - High CLV customers")
print("  4. action_priority_list.csv - Prioritized action list")
print("  5. model_summary.csv - Model performance metrics")
print("  6. prediction_impact_summary.csv - Business impact")
print("  7. churn_model.pkl - Trained churn model")
print("  8. clv_model.pkl - Trained CLV model")
print("  9. churn_prediction_analysis.png - Churn visualizations")
print("  10. clv_prediction_analysis.png - CLV visualizations")
print("  11. customer_priority_matrix.png - Priority matrix")
