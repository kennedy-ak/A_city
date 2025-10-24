"""
AFRIMASH CUSTOMER INTELLIGENCE CHALLENGE
Hour 3-4: Customer Segmentation
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)

print("="*80)
print("AFRIMASH CUSTOMER SEGMENTATION")
print("="*80)

# ============================================================================
# 1. LOAD CLEANED DATA
# ============================================================================
print("\n📁 STEP 1: LOADING CLEANED RFM DATA...")
rfm_df = pd.read_csv('rfm_clean.csv')
print(f"✓ Loaded {len(rfm_df):,} customers with {rfm_df.shape[1]} features")

# ============================================================================
# 2. RFM SEGMENTATION (TRADITIONAL BUSINESS APPROACH)
# ============================================================================
print("\n📊 STEP 2: RFM SEGMENTATION...")

# 2.1 Calculate RFM Scores (1-5 scale)
rfm_df['R_Score'] = pd.qcut(rfm_df['Recency'], q=5, labels=[5,4,3,2,1], duplicates='drop')
rfm_df['F_Score'] = pd.qcut(rfm_df['Frequency'].rank(method='first'), q=5, labels=[1,2,3,4,5], duplicates='drop')
rfm_df['M_Score'] = pd.qcut(rfm_df['Monetary'], q=5, labels=[1,2,3,4,5], duplicates='drop')

# Convert to numeric
rfm_df['R_Score'] = rfm_df['R_Score'].astype(int)
rfm_df['F_Score'] = rfm_df['F_Score'].astype(int)
rfm_df['M_Score'] = rfm_df['M_Score'].astype(int)

# 2.2 Calculate overall RFM Score
rfm_df['RFM_Score'] = rfm_df['R_Score'] + rfm_df['F_Score'] + rfm_df['M_Score']

print(f"✓ Calculated RFM Scores (Range: {rfm_df['RFM_Score'].min()}-{rfm_df['RFM_Score'].max()})")

# 2.3 Define RFM Segments based on scores
def get_rfm_segment(row):
    """Assign customer to RFM segment based on R, F, M scores"""
    r, f, m = row['R_Score'], row['F_Score'], row['M_Score']

    # Champions: Best customers (bought recently, buy often, spend most)
    if r >= 4 and f >= 4 and m >= 4:
        return 'Champions'

    # Loyal Customers: Buy regularly
    elif r >= 3 and f >= 4:
        return 'Loyal Customers'

    # Big Spenders: High monetary value but low frequency
    elif m >= 4 and f <= 3:
        return 'Big Spenders'

    # Promising: Recent customers with potential
    elif r >= 4 and f <= 2:
        return 'Promising'

    # Needs Attention: Above average but declining
    elif r >= 3 and f >= 2 and m >= 2:
        return 'Needs Attention'

    # About to Sleep: Declining engagement
    elif r == 2 or r == 3:
        return 'About to Sleep'

    # At Risk: Used to be good, now fading
    elif r <= 2 and f >= 3 and m >= 3:
        return 'At Risk'

    # Can't Lose Them: High value but haven't bought recently
    elif f >= 4 and m >= 4:
        return "Can't Lose Them"

    # Hibernating: Low engagement, previously active
    elif r <= 2 and f <= 2 and m >= 2:
        return 'Hibernating'

    # Lost: Lowest engagement
    else:
        return 'Lost'

rfm_df['RFM_Segment'] = rfm_df.apply(get_rfm_segment, axis=1)

print(f"✓ Created {rfm_df['RFM_Segment'].nunique()} RFM segments")
print("\nSegment Distribution:")
print(rfm_df['RFM_Segment'].value_counts())

# ============================================================================
# 3. K-MEANS CLUSTERING (ML-DRIVEN APPROACH)
# ============================================================================
print("\n🤖 STEP 3: K-MEANS CLUSTERING...")

# 3.1 Select features for clustering
clustering_features = ['Recency', 'Frequency', 'Monetary', 'Avg_Order_Value',
                       'Customer_Age_Days', 'Purchase_Rate']

# Handle any missing values
X = rfm_df[clustering_features].fillna(0)

# 3.2 Standardize features (important for K-Means)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 3.3 Find optimal number of clusters using elbow method
inertias = []
silhouette_scores = []
K_range = range(2, 11)

print("\nFinding optimal number of clusters...")
for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertias.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_score(X_scaled, kmeans.labels_))

# 3.4 Apply K-Means with optimal clusters (let's use 5 for business interpretability)
optimal_k = 5
print(f"\n✓ Using {optimal_k} clusters based on business interpretability")

kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
rfm_df['Cluster'] = kmeans.fit_predict(X_scaled)

# 3.5 Name clusters based on characteristics
def name_cluster(cluster_id, cluster_data):
    """Assign meaningful names to clusters"""
    avg_recency = cluster_data['Recency'].mean()
    avg_frequency = cluster_data['Frequency'].mean()
    avg_monetary = cluster_data['Monetary'].mean()

    # High value, high frequency, low recency
    if avg_monetary > rfm_df['Monetary'].quantile(0.75) and avg_frequency > 10 and avg_recency < 180:
        return 'Loyal High-Value'

    # High value but high recency (dormant)
    elif avg_monetary > rfm_df['Monetary'].quantile(0.5) and avg_recency > 365:
        return 'Dormant Veterans'

    # Low value, high recency
    elif avg_monetary < rfm_df['Monetary'].quantile(0.25) and avg_recency > 365:
        return 'Lost Low-Value'

    # Medium everything
    elif avg_recency > 180 and avg_frequency < 10:
        return 'Mid-Tier Customers'

    # New/Recent customers
    elif avg_recency < 90:
        return 'Recent Engagers'

    return f'Cluster_{cluster_id}'

cluster_names = {}
for cluster_id in range(optimal_k):
    cluster_data = rfm_df[rfm_df['Cluster'] == cluster_id]
    cluster_names[cluster_id] = name_cluster(cluster_id, cluster_data)

rfm_df['Cluster_Name'] = rfm_df['Cluster'].map(cluster_names)

print(f"✓ Named {optimal_k} clusters")
print("\nCluster Distribution:")
print(rfm_df['Cluster_Name'].value_counts())

# ============================================================================
# 4. SEGMENT ANALYSIS & PROFILING
# ============================================================================
print("\n📊 STEP 4: SEGMENT ANALYSIS...")

# 4.1 RFM Segment Summary
rfm_segment_summary = rfm_df.groupby('RFM_Segment').agg({
    'Customer_ID': 'count',
    'Monetary': ['sum', 'mean', 'std'],
    'Frequency': 'mean',
    'Recency': 'mean',
    'Avg_Order_Value': 'mean',
    'Purchase_Rate': 'mean',
    'Customer_Age_Days': 'mean'
}).round(2)

rfm_segment_summary.columns = ['_'.join(col).strip('_') for col in rfm_segment_summary.columns]
rfm_segment_summary = rfm_segment_summary.reset_index()
rfm_segment_summary = rfm_segment_summary.sort_values('Monetary_sum', ascending=False)

print("\n📊 RFM Segment Summary:")
print(rfm_segment_summary[['RFM_Segment', 'Customer_ID_count', 'Monetary_sum', 'Monetary_mean']])

# 4.2 K-Means Cluster Summary
cluster_summary = rfm_df.groupby('Cluster_Name').agg({
    'Customer_ID': 'count',
    'Monetary': ['sum', 'mean', 'std'],
    'Frequency': 'mean',
    'Recency': 'mean',
    'Avg_Order_Value': 'mean',
    'Purchase_Rate': 'mean',
    'Customer_Age_Days': 'mean'
}).round(2)

cluster_summary.columns = ['_'.join(col).strip('_') for col in cluster_summary.columns]
cluster_summary = cluster_summary.reset_index()
cluster_summary = cluster_summary.sort_values('Monetary_sum', ascending=False)

print("\n🤖 K-Means Cluster Summary:")
print(cluster_summary[['Cluster_Name', 'Customer_ID_count', 'Monetary_sum', 'Monetary_mean']])

# ============================================================================
# 5. SAVE SEGMENTED DATA
# ============================================================================
print("\n💾 STEP 5: SAVING RESULTS...")

# Save segmented customer data
rfm_df.to_csv('rfm_segmented.csv', index=False)
print(f"✓ Saved rfm_segmented.csv ({len(rfm_df):,} customers)")

# Save segment summaries
rfm_segment_summary.to_csv('rfm_segment_summary.csv', index=False)
print(f"✓ Saved rfm_segment_summary.csv ({len(rfm_segment_summary)} segments)")

cluster_summary.to_csv('cluster_summary.csv', index=False)
print(f"✓ Saved cluster_summary.csv ({len(cluster_summary)} clusters)")

# ============================================================================
# 6. VISUALIZATIONS
# ============================================================================
print("\n📊 STEP 6: CREATING VISUALIZATIONS...")

fig, axes = plt.subplots(3, 2, figsize=(20, 18))
fig.suptitle('AFRIMASH CUSTOMER SEGMENTATION ANALYSIS', fontsize=20, fontweight='bold', y=0.995)

# 6.1 RFM Segment Distribution
ax = axes[0, 0]
segment_counts = rfm_df['RFM_Segment'].value_counts()
colors = plt.cm.Set3(range(len(segment_counts)))
segment_counts.plot(kind='barh', ax=ax, color=colors)
ax.set_title('Customer Distribution by RFM Segment', fontsize=14, fontweight='bold')
ax.set_xlabel('Number of Customers')
ax.set_ylabel('Segment')
for i, v in enumerate(segment_counts.values):
    ax.text(v, i, f' {v:,}', va='center')

# 6.2 Revenue by RFM Segment
ax = axes[0, 1]
segment_revenue = rfm_df.groupby('RFM_Segment')['Monetary'].sum().sort_values(ascending=False)
segment_revenue_billions = segment_revenue / 1e9
colors = plt.cm.Set3(range(len(segment_revenue)))
segment_revenue_billions.plot(kind='barh', ax=ax, color=colors)
ax.set_title('Total Revenue by RFM Segment (₵ Billions)', fontsize=14, fontweight='bold')
ax.set_xlabel('Revenue (₵B)')
ax.set_ylabel('Segment')
for i, v in enumerate(segment_revenue_billions.values):
    ax.text(v, i, f' ₵{v:.2f}B', va='center')

# 6.3 K-Means Cluster Distribution
ax = axes[1, 0]
cluster_counts = rfm_df['Cluster_Name'].value_counts()
colors = plt.cm.Pastel1(range(len(cluster_counts)))
cluster_counts.plot(kind='barh', ax=ax, color=colors)
ax.set_title('Customer Distribution by K-Means Cluster', fontsize=14, fontweight='bold')
ax.set_xlabel('Number of Customers')
ax.set_ylabel('Cluster')
for i, v in enumerate(cluster_counts.values):
    ax.text(v, i, f' {v:,}', va='center')

# 6.4 Revenue by Cluster
ax = axes[1, 1]
cluster_revenue = rfm_df.groupby('Cluster_Name')['Monetary'].sum().sort_values(ascending=False)
cluster_revenue_billions = cluster_revenue / 1e9
colors = plt.cm.Pastel1(range(len(cluster_revenue)))
cluster_revenue_billions.plot(kind='barh', ax=ax, color=colors)
ax.set_title('Total Revenue by Cluster (₵ Billions)', fontsize=14, fontweight='bold')
ax.set_xlabel('Revenue (₵B)')
ax.set_ylabel('Cluster')
for i, v in enumerate(cluster_revenue_billions.values):
    ax.text(v, i, f' ₵{v:.2f}B', va='center')

# 6.5 RFM Score Distribution
ax = axes[2, 0]
rfm_df['RFM_Score'].hist(bins=range(3, 16), ax=ax, color='skyblue', edgecolor='black')
ax.set_title('RFM Score Distribution', fontsize=14, fontweight='bold')
ax.set_xlabel('RFM Score')
ax.set_ylabel('Number of Customers')
ax.axvline(rfm_df['RFM_Score'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {rfm_df["RFM_Score"].mean():.1f}')
ax.legend()

# 6.6 Scatter: Recency vs Monetary by Segment
ax = axes[2, 1]
for segment in rfm_df['RFM_Segment'].unique():
    segment_data = rfm_df[rfm_df['RFM_Segment'] == segment]
    ax.scatter(segment_data['Recency'], segment_data['Monetary'],
               alpha=0.6, s=50, label=segment)
ax.set_title('Recency vs Monetary Value by RFM Segment', fontsize=14, fontweight='bold')
ax.set_xlabel('Recency (Days)')
ax.set_ylabel('Monetary Value (₵)')
ax.set_yscale('log')
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('rfm_segmentation.png', dpi=300, bbox_inches='tight')
print("✓ Saved rfm_segmentation.png")

# Additional visualization: K-Means Clustering
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('K-MEANS CLUSTERING ANALYSIS', fontsize=18, fontweight='bold')

# Scatter plots for different feature combinations
feature_pairs = [
    ('Recency', 'Frequency'),
    ('Recency', 'Monetary'),
    ('Frequency', 'Monetary'),
    ('Avg_Order_Value', 'Purchase_Rate')
]

for idx, (feat1, feat2) in enumerate(feature_pairs):
    ax = axes[idx // 2, idx % 2]
    for cluster in rfm_df['Cluster'].unique():
        cluster_data = rfm_df[rfm_df['Cluster'] == cluster]
        cluster_name = cluster_data['Cluster_Name'].iloc[0]
        ax.scatter(cluster_data[feat1], cluster_data[feat2],
                   alpha=0.6, s=30, label=cluster_name)

    ax.set_xlabel(feat1, fontsize=11)
    ax.set_ylabel(feat2, fontsize=11)
    ax.set_title(f'{feat1} vs {feat2}', fontsize=12, fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    if feat2 == 'Monetary':
        ax.set_yscale('log')

plt.tight_layout()
plt.savefig('kmeans_clustering.png', dpi=300, bbox_inches='tight')
print("✓ Saved kmeans_clustering.png")

# Segment Comparison visualization
fig, axes = plt.subplots(2, 2, figsize=(18, 12))
fig.suptitle('SEGMENT COMPARISON: RFM vs K-MEANS', fontsize=18, fontweight='bold')

# Compare key metrics
metrics = ['Recency', 'Frequency', 'Monetary', 'Avg_Order_Value']

for idx, metric in enumerate(metrics):
    ax = axes[idx // 2, idx % 2]

    # RFM segments
    rfm_means = rfm_df.groupby('RFM_Segment')[metric].mean().sort_values()

    rfm_means.plot(kind='barh', ax=ax, color='steelblue', alpha=0.7)
    ax.set_title(f'Average {metric} by RFM Segment', fontsize=12, fontweight='bold')
    ax.set_xlabel(f'Average {metric}')

    if metric == 'Monetary':
        ax.set_xlabel(f'Average {metric} (₵)')

plt.tight_layout()
plt.savefig('segment_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved segment_comparison.png")

# ============================================================================
# 7. KEY INSIGHTS & RECOMMENDATIONS
# ============================================================================
print("\n" + "="*80)
print("📈 KEY INSIGHTS")
print("="*80)

# Top segments by revenue
top_segments = rfm_segment_summary.nlargest(3, 'Monetary_sum')
print("\n🏆 TOP 3 RFM SEGMENTS BY REVENUE:")
for idx, row in top_segments.iterrows():
    revenue_bn = row['Monetary_sum'] / 1e9
    pct = (row['Monetary_sum'] / rfm_df['Monetary'].sum()) * 100
    print(f"  {row['RFM_Segment']}: {row['Customer_ID_count']} customers, ₵{revenue_bn:.2f}B ({pct:.1f}%)")

# At-risk customers
at_risk = rfm_df[rfm_df['RFM_Segment'].isin(['At Risk', 'About to Sleep', 'Hibernating'])]
print(f"\n⚠️ AT-RISK CUSTOMERS:")
print(f"  {len(at_risk):,} customers ({len(at_risk)/len(rfm_df)*100:.1f}%)")
print(f"  Revenue at stake: ₵{at_risk['Monetary'].sum()/1e9:.2f}B")

# High-value opportunities
champions = rfm_df[rfm_df['RFM_Segment'] == 'Champions']
print(f"\n💎 CHAMPIONS SEGMENT:")
print(f"  {len(champions):,} customers ({len(champions)/len(rfm_df)*100:.1f}%)")
print(f"  Revenue: ₵{champions['Monetary'].sum()/1e9:.2f}B ({champions['Monetary'].sum()/rfm_df['Monetary'].sum()*100:.1f}%)")
print(f"  Avg spend: ₵{champions['Monetary'].mean()/1e6:.2f}M")

print("\n" + "="*80)
print("✅ SEGMENTATION COMPLETE!")
print("="*80)
print("\n📁 Output Files:")
print("  1. rfm_segmented.csv - Customer data with segments")
print("  2. rfm_segment_summary.csv - RFM segment statistics")
print("  3. cluster_summary.csv - K-Means cluster statistics")
print("  4. rfm_segmentation.png - RFM visualization")
print("  5. kmeans_clustering.png - K-Means visualization")
print("  6. segment_comparison.png - Comparison charts")
