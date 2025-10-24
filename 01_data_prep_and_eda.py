"""
AFRIMASH CUSTOMER INTELLIGENCE CHALLENGE
Hour 1-2: Data Preparation & Exploratory Data Analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 6)

print("="*80)
print("AFRIMASH DATA PREPARATION & EDA")
print("="*80)

# ============================================================================
# 1. LOAD DATA
# ============================================================================
print("\n📁 STEP 1: LOADING DATASETS...")
rfm_df = pd.read_excel('/mnt/user-data/uploads/Copy_of_RFM_Data.xlsx')
trans_df = pd.read_excel('/mnt/user-data/uploads/Copy_of_Transaction_Data.xlsx')

print(f"✓ RFM Data: {rfm_df.shape[0]:,} customers, {rfm_df.shape[1]} columns")
print(f"✓ Transaction Data: {trans_df.shape[0]:,} transactions, {trans_df.shape[1]} columns")

# ============================================================================
# 2. DATA CLEANING
# ============================================================================
print("\n🧹 STEP 2: DATA CLEANING...")

# 2.1 Handle missing products (fill with "Unknown Product")
trans_df['Product(s)'].fillna("Unknown Product", inplace=True)
print(f"✓ Filled {2347} missing product names with 'Unknown Product'")

# 2.2 Check for negative values
negative_revenue = trans_df[trans_df['Revenue'] < 0]
negative_monetary = rfm_df[rfm_df['Monetary'] < 0]
print(f"✓ Found {len(negative_revenue)} negative revenue transactions (refunds/returns)")
print(f"✓ Found {len(negative_monetary)} customers with negative monetary values")

# 2.3 Remove duplicates
initial_trans = len(trans_df)
trans_df = trans_df.drop_duplicates(subset=['Order #'], keep='first')
print(f"✓ Removed {initial_trans - len(trans_df)} duplicate orders")

# ============================================================================
# 3. FEATURE ENGINEERING
# ============================================================================
print("\n⚙️ STEP 3: FEATURE ENGINEERING...")

# 3.1 Calculate Recency (days since last purchase)
current_date = trans_df['Date'].max()
print(f"Analysis Date: {current_date}")

last_purchase = trans_df.groupby('Customer_ID')['Date'].max().reset_index()
last_purchase.columns = ['Customer_ID', 'Last_Purchase_Date']
last_purchase['Recency'] = (current_date - last_purchase['Last_Purchase_Date']).dt.days

# Merge recency with RFM
rfm_df = rfm_df.merge(last_purchase[['Customer_ID', 'Recency', 'Last_Purchase_Date']], 
                       on='Customer_ID', how='left')
print(f"✓ Added Recency (days since last purchase)")

# 3.2 Extract time features from transactions
trans_df['Year'] = trans_df['Date'].dt.year
trans_df['Month'] = trans_df['Date'].dt.month
trans_df['Quarter'] = trans_df['Date'].dt.quarter
trans_df['DayOfWeek'] = trans_df['Date'].dt.dayofweek
trans_df['DayName'] = trans_df['Date'].dt.day_name()
trans_df['MonthName'] = trans_df['Date'].dt.month_name()
print("✓ Added time-based features (Year, Month, Quarter, Day)")

# 3.3 First purchase date per customer
first_purchase = trans_df.groupby('Customer_ID')['Date'].min().reset_index()
first_purchase.columns = ['Customer_ID', 'First_Purchase_Date']
rfm_df = rfm_df.merge(first_purchase, on='Customer_ID', how='left')
print("✓ Added First Purchase Date")

# 3.4 Customer Age (days since first purchase)
rfm_df['Customer_Age_Days'] = (current_date - rfm_df['First_Purchase_Date']).dt.days
print("✓ Added Customer Age (days since first purchase)")

# 3.5 Categorize customers by frequency
def categorize_frequency(freq):
    if freq == 1:
        return 'One-time'
    elif freq <= 3:
        return 'Low'
    elif freq <= 10:
        return 'Medium'
    elif freq <= 20:
        return 'High'
    else:
        return 'Very High'

rfm_df['Frequency_Category'] = rfm_df['Frequency'].apply(categorize_frequency)
print("✓ Added Frequency Category")

# 3.6 Categorize customers by monetary value
def categorize_monetary(value):
    if value < 50000:
        return 'Low Value'
    elif value < 200000:
        return 'Medium Value'
    elif value < 1000000:
        return 'High Value'
    else:
        return 'Very High Value'

rfm_df['Monetary_Category'] = rfm_df['Monetary'].apply(categorize_monetary)
print("✓ Added Monetary Category")

# 3.7 Categorize customers by recency
def categorize_recency(recency):
    if recency <= 30:
        return 'Active (0-30 days)'
    elif recency <= 90:
        return 'Recent (31-90 days)'
    elif recency <= 180:
        return 'Cooling (91-180 days)'
    elif recency <= 365:
        return 'At Risk (181-365 days)'
    else:
        return 'Lost (>365 days)'

rfm_df['Recency_Category'] = rfm_df['Recency'].apply(categorize_recency)
print("✓ Added Recency Category")

# 3.8 Extract product categories (simplified)
def extract_product_category(product_text):
    if pd.isna(product_text) or product_text == "Unknown Product":
        return "Unknown"
    
    product_lower = str(product_text).lower()
    
    # Define category keywords
    if any(word in product_lower for word in ['chick', 'pullet', 'broiler', 'poultry', 'bird']):
        return 'Poultry'
    elif any(word in product_lower for word in ['seed', 'maize', 'corn', 'soybean', 'rice']):
        return 'Seeds'
    elif any(word in product_lower for word in ['feed', 'concentrate', 'premix']):
        return 'Feed'
    elif any(word in product_lower for word in ['fertilizer', 'npk', 'urea']):
        return 'Fertilizer'
    elif any(word in product_lower for word in ['pesticide', 'herbicide', 'insecticide', 'fungicide']):
        return 'Agrochemicals'
    elif any(word in product_lower for word in ['tractor', 'machine', 'equipment', 'processing', 'pump']):
        return 'Equipment'
    elif any(word in product_lower for word in ['vegetable', 'tomato', 'pepper', 'cucumber', 'carrot']):
        return 'Vegetables'
    elif any(word in product_lower for word in ['fruit', 'papaya', 'mango', 'watermelon']):
        return 'Fruits'
    else:
        return 'Other'

trans_df['Product_Category'] = trans_df['Product(s)'].apply(extract_product_category)
print("✓ Extracted Product Categories")

# 3.9 Add product category counts to RFM
category_counts = trans_df.groupby('Customer_ID')['Product_Category'].value_counts().unstack(fill_value=0)
category_counts.columns = [f'Category_{col}' for col in category_counts.columns]
rfm_df = rfm_df.merge(category_counts, on='Customer_ID', how='left')
rfm_df.fillna(0, inplace=True)
print("✓ Added product category purchase counts per customer")

# 3.10 Days between purchases (for returning customers)
rfm_df['Days_Between_Purchases'] = rfm_df['Customer_Age_Days'] / rfm_df['Frequency']
print("✓ Added average days between purchases")

# ============================================================================
# 4. SAVE CLEANED DATA
# ============================================================================
print("\n💾 STEP 4: SAVING CLEANED DATA...")
rfm_df.to_csv('/home/claude/rfm_clean.csv', index=False)
trans_df.to_csv('/home/claude/transactions_clean.csv', index=False)
print("✓ Saved: rfm_clean.csv")
print("✓ Saved: transactions_clean.csv")

# ============================================================================
# 5. EXPLORATORY DATA ANALYSIS
# ============================================================================
print("\n📊 STEP 5: EXPLORATORY DATA ANALYSIS...")

# 5.1 Customer Type Distribution
print("\n--- Customer Type Distribution ---")
print(rfm_df['Customer_Type'].value_counts())
print(f"\nNew Customers: {(rfm_df['Customer_Type']=='new').sum()/len(rfm_df)*100:.1f}%")
print(f"Returning Customers: {(rfm_df['Customer_Type']=='returning').sum()/len(rfm_df)*100:.1f}%")

# 5.2 Frequency Category Distribution
print("\n--- Frequency Category Distribution ---")
print(rfm_df['Frequency_Category'].value_counts())

# 5.3 Monetary Category Distribution
print("\n--- Monetary Category Distribution ---")
print(rfm_df['Monetary_Category'].value_counts())

# 5.4 Recency Category Distribution
print("\n--- Recency Category Distribution ---")
print(rfm_df['Recency_Category'].value_counts())

# 5.5 Top Product Categories
print("\n--- Top Product Categories ---")
print(trans_df['Product_Category'].value_counts())

# 5.6 Revenue by Product Category
print("\n--- Revenue by Product Category ---")
category_revenue = trans_df.groupby('Product_Category')['Revenue'].sum().sort_values(ascending=False)
print(category_revenue)

# 5.7 Monthly Transaction Trends
print("\n--- Monthly Transaction Count (Last 12 Months) ---")
last_12_months = trans_df[trans_df['Date'] >= (current_date - timedelta(days=365))]
monthly_trends = last_12_months.groupby(['Year', 'MonthName']).size().tail(12)
print(monthly_trends)

# 5.8 Top 10 Customers by Revenue
print("\n--- Top 10 Customers by Revenue ---")
top_customers = rfm_df.nlargest(10, 'Monetary')[['Customer_ID', 'Monetary', 'Frequency', 'Recency']]
print(top_customers)

# 5.9 Churn Analysis (customers who haven't purchased in 90+ days)
churned_customers = rfm_df[rfm_df['Recency'] > 90]
print(f"\n--- Churn Analysis ---")
print(f"Total Customers: {len(rfm_df):,}")
print(f"At Risk/Churned (>90 days): {len(churned_customers):,} ({len(churned_customers)/len(rfm_df)*100:.1f}%)")
print(f"Revenue from Churned Customers: ₦{churned_customers['Monetary'].sum():,.2f}")

# 5.10 Attribution Channel Performance
print("\n--- Top 5 Attribution Channels ---")
top_channels = rfm_df['Attribution'].value_counts().head(5)
print(top_channels)

# ============================================================================
# 6. CREATE VISUALIZATIONS
# ============================================================================
print("\n📈 STEP 6: CREATING VISUALIZATIONS...")

fig, axes = plt.subplots(3, 3, figsize=(20, 15))
fig.suptitle('AFRIMASH CUSTOMER INTELLIGENCE - EXPLORATORY DATA ANALYSIS', fontsize=20, fontweight='bold')

# 6.1 Frequency Distribution
axes[0, 0].hist(rfm_df['Frequency'], bins=50, color='skyblue', edgecolor='black')
axes[0, 0].set_title('Frequency Distribution', fontsize=14, fontweight='bold')
axes[0, 0].set_xlabel('Number of Purchases')
axes[0, 0].set_ylabel('Number of Customers')
axes[0, 0].axvline(rfm_df['Frequency'].median(), color='red', linestyle='--', label=f'Median: {rfm_df["Frequency"].median():.0f}')
axes[0, 0].legend()

# 6.2 Monetary Distribution (log scale)
axes[0, 1].hist(np.log10(rfm_df['Monetary'][rfm_df['Monetary'] > 0]), bins=50, color='lightgreen', edgecolor='black')
axes[0, 1].set_title('Monetary Value Distribution (Log Scale)', fontsize=14, fontweight='bold')
axes[0, 1].set_xlabel('Log10(Total Spent)')
axes[0, 1].set_ylabel('Number of Customers')

# 6.3 Recency Distribution
axes[0, 2].hist(rfm_df['Recency'], bins=50, color='lightcoral', edgecolor='black')
axes[0, 2].set_title('Recency Distribution', fontsize=14, fontweight='bold')
axes[0, 2].set_xlabel('Days Since Last Purchase')
axes[0, 2].set_ylabel('Number of Customers')
axes[0, 2].axvline(90, color='red', linestyle='--', label='90 days (Churn threshold)')
axes[0, 2].legend()

# 6.4 Customer Type
customer_type_counts = rfm_df['Customer_Type'].value_counts()
axes[1, 0].pie(customer_type_counts, labels=customer_type_counts.index, autopct='%1.1f%%', 
               colors=['#ff9999', '#66b3ff'], startangle=90)
axes[1, 0].set_title('Customer Type Distribution', fontsize=14, fontweight='bold')

# 6.5 Frequency Category
freq_cat = rfm_df['Frequency_Category'].value_counts()
axes[1, 1].bar(freq_cat.index, freq_cat.values, color='purple', alpha=0.7)
axes[1, 1].set_title('Frequency Categories', fontsize=14, fontweight='bold')
axes[1, 1].set_xlabel('Category')
axes[1, 1].set_ylabel('Number of Customers')
axes[1, 1].tick_params(axis='x', rotation=45)

# 6.6 Recency Category
rec_cat = rfm_df['Recency_Category'].value_counts()
axes[1, 2].barh(rec_cat.index, rec_cat.values, color='orange', alpha=0.7)
axes[1, 2].set_title('Recency Categories', fontsize=14, fontweight='bold')
axes[1, 2].set_xlabel('Number of Customers')

# 6.7 Product Categories
prod_cat = trans_df['Product_Category'].value_counts().head(8)
axes[2, 0].bar(prod_cat.index, prod_cat.values, color='teal', alpha=0.7)
axes[2, 0].set_title('Top Product Categories', fontsize=14, fontweight='bold')
axes[2, 0].set_xlabel('Category')
axes[2, 0].set_ylabel('Number of Transactions')
axes[2, 0].tick_params(axis='x', rotation=45)

# 6.8 Monthly Revenue Trend
monthly_revenue = trans_df.groupby(['Year', 'Month'])['Revenue'].sum().reset_index()
monthly_revenue['YearMonth'] = monthly_revenue['Year'].astype(str) + '-' + monthly_revenue['Month'].astype(str).str.zfill(2)
recent_months = monthly_revenue.tail(24)
axes[2, 1].plot(range(len(recent_months)), recent_months['Revenue'], marker='o', color='green', linewidth=2)
axes[2, 1].set_title('Monthly Revenue Trend (Last 24 Months)', fontsize=14, fontweight='bold')
axes[2, 1].set_xlabel('Month')
axes[2, 1].set_ylabel('Revenue (₦)')
axes[2, 1].tick_params(axis='x', rotation=45)
axes[2, 1].grid(True, alpha=0.3)

# 6.9 Revenue by Customer Type
customer_type_revenue = rfm_df.groupby('Customer_Type')['Monetary'].sum()
axes[2, 2].bar(customer_type_revenue.index, customer_type_revenue.values, color=['#ff9999', '#66b3ff'])
axes[2, 2].set_title('Total Revenue by Customer Type', fontsize=14, fontweight='bold')
axes[2, 2].set_xlabel('Customer Type')
axes[2, 2].set_ylabel('Total Revenue (₦)')

plt.tight_layout()
plt.savefig('/home/claude/eda_dashboard.png', dpi=300, bbox_inches='tight')
print("✓ Saved: eda_dashboard.png")
plt.close()

# ============================================================================
# 7. ADDITIONAL INSIGHTS VISUALIZATION
# ============================================================================

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('AFRIMASH DEEP DIVE ANALYSIS', fontsize=18, fontweight='bold')

# 7.1 RFM Scatter Plot
scatter = axes[0, 0].scatter(rfm_df['Recency'], rfm_df['Frequency'], 
                            c=rfm_df['Monetary'], cmap='viridis', 
                            alpha=0.6, s=50)
axes[0, 0].set_title('RFM Analysis: Recency vs Frequency', fontsize=14, fontweight='bold')
axes[0, 0].set_xlabel('Recency (Days)')
axes[0, 0].set_ylabel('Frequency (Purchases)')
axes[0, 0].axvline(90, color='red', linestyle='--', alpha=0.5, label='90-day threshold')
axes[0, 0].legend()
plt.colorbar(scatter, ax=axes[0, 0], label='Monetary Value (₦)')

# 7.2 Top 10 Revenue Products Category
cat_rev = trans_df.groupby('Product_Category')['Revenue'].sum().sort_values(ascending=True).tail(10)
axes[0, 1].barh(cat_rev.index, cat_rev.values, color='coral')
axes[0, 1].set_title('Revenue by Product Category (Top 10)', fontsize=14, fontweight='bold')
axes[0, 1].set_xlabel('Total Revenue (₦)')

# 7.3 Customer Lifetime Distribution
axes[1, 0].hist(rfm_df['Customer_Age_Days'], bins=50, color='mediumpurple', edgecolor='black')
axes[1, 0].set_title('Customer Lifetime Distribution', fontsize=14, fontweight='bold')
axes[1, 0].set_xlabel('Days Since First Purchase')
axes[1, 0].set_ylabel('Number of Customers')
axes[1, 0].axvline(rfm_df['Customer_Age_Days'].median(), color='red', 
                   linestyle='--', label=f'Median: {rfm_df["Customer_Age_Days"].median():.0f} days')
axes[1, 0].legend()

# 7.4 Day of Week Analysis
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_trans = trans_df['DayName'].value_counts().reindex(day_order)
axes[1, 1].bar(day_trans.index, day_trans.values, color='steelblue', alpha=0.7)
axes[1, 1].set_title('Transactions by Day of Week', fontsize=14, fontweight='bold')
axes[1, 1].set_xlabel('Day')
axes[1, 1].set_ylabel('Number of Transactions')
axes[1, 1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('/home/claude/deep_dive_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Saved: deep_dive_analysis.png")
plt.close()

# ============================================================================
# 8. SUMMARY STATISTICS EXPORT
# ============================================================================
print("\n📄 STEP 7: GENERATING SUMMARY REPORT...")

summary_stats = {
    'Metric': [
        'Total Customers',
        'Total Transactions',
        'Total Revenue',
        'Total Net Sales',
        'Average Customer Value',
        'Average Transaction Value',
        'Median Frequency',
        'Median Recency (days)',
        'Active Customers (0-30 days)',
        'At Risk Customers (>90 days)',
        'One-time Buyers',
        'Returning Customers Rate',
        'Average Purchase Frequency',
        'Most Popular Category'
    ],
    'Value': [
        f"{len(rfm_df):,}",
        f"{len(trans_df):,}",
        f"₦{trans_df['Revenue'].sum():,.2f}",
        f"₦{trans_df['Net_Sales'].sum():,.2f}",
        f"₦{rfm_df['Monetary'].mean():,.2f}",
        f"₦{trans_df['Revenue'].mean():,.2f}",
        f"{rfm_df['Frequency'].median():.0f}",
        f"{rfm_df['Recency'].median():.0f}",
        f"{len(rfm_df[rfm_df['Recency'] <= 30]):,} ({len(rfm_df[rfm_df['Recency'] <= 30])/len(rfm_df)*100:.1f}%)",
        f"{len(rfm_df[rfm_df['Recency'] > 90]):,} ({len(rfm_df[rfm_df['Recency'] > 90])/len(rfm_df)*100:.1f}%)",
        f"{len(rfm_df[rfm_df['Frequency'] == 1]):,} ({len(rfm_df[rfm_df['Frequency'] == 1])/len(rfm_df)*100:.1f}%)",
        f"{(rfm_df['Customer_Type']=='returning').sum()/len(rfm_df)*100:.1f}%",
        f"{rfm_df['Frequency'].mean():.2f}",
        trans_df['Product_Category'].mode()[0]
    ]
}

summary_df = pd.DataFrame(summary_stats)
summary_df.to_csv('/home/claude/summary_statistics.csv', index=False)
print("✓ Saved: summary_statistics.csv")

print("\n" + "="*80)
print("✅ DATA PREPARATION & EDA COMPLETE!")
print("="*80)
print("\nGenerated Files:")
print("  1. rfm_clean.csv - Cleaned RFM data with new features")
print("  2. transactions_clean.csv - Cleaned transaction data")
print("  3. eda_dashboard.png - Main EDA visualizations")
print("  4. deep_dive_analysis.png - Additional insights")
print("  5. summary_statistics.csv - Key metrics summary")
print("\n" + "="*80)

# Display summary
print("\n📊 KEY INSIGHTS SUMMARY:")
print("="*80)
print(summary_df.to_string(index=False))
