# ============================================================================
# POWERPOINT PRESENTATION VISUALS
# High-quality, presentation-ready charts for executive presentations
# ============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')

# Set professional style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Professional color schemes
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'success': '#06A77D',
    'warning': '#F18F01',
    'danger': '#C73E1D',
    'info': '#6C757D',
    'light_blue': '#6FCDCD',
    'purple': '#7B68EE',
    'green': '#3CB371',
    'orange': '#FF8C42',
    'red': '#E63946'
}

print("="*80)
print("GENERATING POWERPOINT-READY VISUALIZATIONS")
print("="*80)

# Load the processed data
try:
    rfm_df = pd.read_csv('rfm_with_predictions.csv')
    trans_df = pd.read_csv('transactions_clean.csv')
    segment_summary = pd.read_csv('rfm_segment_summary.csv')
    print("✓ Data loaded successfully\n")
except FileNotFoundError as e:
    print(f"❌ Error: {e}")
    print("Please run the main analysis first to generate the required CSV files.")
    exit()

# Create output directory for slides
import os
if not os.path.exists('powerpoint_slides'):
    os.makedirs('powerpoint_slides')
    print("✓ Created 'powerpoint_slides' directory\n")


# ============================================================================
# SLIDE 1: EXECUTIVE SUMMARY - KEY METRICS
# ============================================================================
print("Creating Slide 1: Executive Summary - Key Metrics...")

fig = plt.figure(figsize=(16, 9))
fig.patch.set_facecolor('white')

# Title
fig.text(0.5, 0.95, 'AFRIMASH CUSTOMER INTELLIGENCE',
         ha='center', fontsize=28, fontweight='bold', color=COLORS['primary'])
fig.text(0.5, 0.90, 'Executive Summary',
         ha='center', fontsize=20, color=COLORS['info'])

# Key Metrics in boxes
metrics = [
    {
        'title': 'Total Customers',
        'value': f"{len(rfm_df):,}",
        'subtitle': 'In Database',
        'color': COLORS['primary']
    },
    {
        'title': 'Total Revenue',
        'value': f"₦{trans_df['Revenue'].sum()/1e9:.2f}B",
        'subtitle': 'Lifetime Value',
        'color': COLORS['success']
    },
    {
        'title': 'Active Customers',
        'value': f"{len(rfm_df[rfm_df['Recency'] <= 30]):,}",
        'subtitle': f"{len(rfm_df[rfm_df['Recency'] <= 30])/len(rfm_df)*100:.1f}% of total",
        'color': COLORS['green']
    },
    {
        'title': 'Churn Rate',
        'value': f"{len(rfm_df[rfm_df['Recency'] > 90])/len(rfm_df)*100:.1f}%",
        'subtitle': 'At Risk Customers',
        'color': COLORS['danger']
    },
    {
        'title': 'Avg Customer Value',
        'value': f"₦{rfm_df['Monetary'].mean()/1e6:.2f}M",
        'subtitle': 'Per Customer',
        'color': COLORS['purple']
    },
    {
        'title': 'Revenue at Risk',
        'value': f"₦{rfm_df[rfm_df['Recency'] > 90]['Monetary'].sum()/1e9:.2f}B",
        'subtitle': 'From Churned',
        'color': COLORS['warning']
    }
]

# Create metric boxes
positions = [(0.08, 0.55), (0.37, 0.55), (0.66, 0.55),
             (0.08, 0.15), (0.37, 0.15), (0.66, 0.15)]

for i, (metric, pos) in enumerate(zip(metrics, positions)):
    # Box background
    ax = fig.add_axes([pos[0], pos[1], 0.25, 0.28])
    ax.add_patch(Rectangle((0, 0), 1, 1, facecolor=metric['color'], alpha=0.1, transform=ax.transAxes))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Title
    ax.text(0.5, 0.75, metric['title'],
            ha='center', va='center', fontsize=14, color=COLORS['info'],
            transform=ax.transAxes, fontweight='bold')

    # Value
    ax.text(0.5, 0.45, metric['value'],
            ha='center', va='center', fontsize=24, color=metric['color'],
            transform=ax.transAxes, fontweight='bold')

    # Subtitle
    ax.text(0.5, 0.20, metric['subtitle'],
            ha='center', va='center', fontsize=11, color=COLORS['info'],
            transform=ax.transAxes, style='italic')

plt.savefig('powerpoint_slides/01_executive_summary.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("✓ Saved: 01_executive_summary.png\n")


# ============================================================================
# SLIDE 2: CUSTOMER SEGMENTATION OVERVIEW
# ============================================================================
print("Creating Slide 2: Customer Segmentation Overview...")

fig, axes = plt.subplots(1, 2, figsize=(16, 9), facecolor='white')
fig.suptitle('Customer Segmentation Analysis', fontsize=22, fontweight='bold', y=0.98)

# Left: RFM Segment Distribution (Pie Chart)
segment_counts = rfm_df['RFM_Segment'].value_counts()
colors_palette = plt.cm.Set3(range(len(segment_counts)))

wedges, texts, autotexts = axes[0].pie(segment_counts, labels=segment_counts.index,
                                         autopct='%1.1f%%', startangle=90,
                                         colors=colors_palette, textprops={'fontsize': 11})

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(12)

axes[0].set_title('Customer Distribution by Segment', fontsize=16, fontweight='bold', pad=20)

# Right: Revenue by Segment (Horizontal Bar)
segment_revenue = rfm_df.groupby('RFM_Segment')['Monetary'].sum().sort_values(ascending=True) / 1e9
colors_bars = [colors_palette[segment_counts.index.tolist().index(seg)]
               for seg in segment_revenue.index]

bars = axes[1].barh(segment_revenue.index, segment_revenue.values, color=colors_bars, alpha=0.8)

# Add value labels on bars
for i, (bar, value) in enumerate(zip(bars, segment_revenue.values)):
    axes[1].text(value, i, f'  ₦{value:.2f}B',
                va='center', fontsize=11, fontweight='bold')

axes[1].set_xlabel('Total Revenue (₦ Billions)', fontsize=13, fontweight='bold')
axes[1].set_title('Revenue by Customer Segment', fontsize=16, fontweight='bold', pad=20)
axes[1].grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('powerpoint_slides/02_customer_segmentation.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("✓ Saved: 02_customer_segmentation.png\n")


# ============================================================================
# SLIDE 3: REVENUE INSIGHTS
# ============================================================================
print("Creating Slide 3: Revenue Insights...")

fig = plt.figure(figsize=(16, 9), facecolor='white')
gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

fig.suptitle('Revenue Analysis & Insights', fontsize=22, fontweight='bold', y=0.98)

# Top Left: Revenue by Customer Type
ax1 = fig.add_subplot(gs[0, 0])
customer_type_revenue = rfm_df.groupby('Customer_Type')['Monetary'].sum() / 1e9
bars = ax1.bar(customer_type_revenue.index, customer_type_revenue.values,
               color=[COLORS['primary'], COLORS['success']], alpha=0.8, width=0.6)
for bar, value in zip(bars, customer_type_revenue.values):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'₦{value:.2f}B\n({value/customer_type_revenue.sum()*100:.1f}%)',
            ha='center', va='bottom', fontsize=12, fontweight='bold')
ax1.set_title('Revenue by Customer Type', fontsize=14, fontweight='bold', pad=15)
ax1.set_ylabel('Revenue (₦ Billions)', fontsize=12, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)

# Top Right: Top 10 Product Categories by Revenue
ax2 = fig.add_subplot(gs[0, 1])
category_revenue = trans_df.groupby('Product_Category')['Revenue'].sum().sort_values(ascending=False).head(10) / 1e6
colors_grad = plt.cm.viridis(np.linspace(0.3, 0.9, len(category_revenue)))
ax2.barh(range(len(category_revenue)), category_revenue.values, color=colors_grad, alpha=0.8)
ax2.set_yticks(range(len(category_revenue)))
ax2.set_yticklabels(category_revenue.index, fontsize=11)
ax2.set_xlabel('Revenue (₦ Millions)', fontsize=12, fontweight='bold')
ax2.set_title('Top 10 Product Categories by Revenue', fontsize=14, fontweight='bold', pad=15)
ax2.grid(axis='x', alpha=0.3)
# Add value labels
for i, value in enumerate(category_revenue.values):
    ax2.text(value, i, f'  ₦{value:.1f}M', va='center', fontsize=10, fontweight='bold')

# Bottom: Monthly Revenue Trend
ax3 = fig.add_subplot(gs[1, :])
trans_df['Date'] = pd.to_datetime(trans_df['Date'])
monthly_revenue = trans_df.groupby(trans_df['Date'].dt.to_period('M'))['Revenue'].sum() / 1e6
monthly_revenue.index = monthly_revenue.index.to_timestamp()

# Plot trend
ax3.plot(monthly_revenue.index, monthly_revenue.values,
         marker='o', linewidth=3, markersize=8, color=COLORS['primary'], alpha=0.8)
ax3.fill_between(monthly_revenue.index, monthly_revenue.values, alpha=0.2, color=COLORS['primary'])

# Add trend line
z = np.polyfit(range(len(monthly_revenue)), monthly_revenue.values, 1)
p = np.poly1d(z)
ax3.plot(monthly_revenue.index, p(range(len(monthly_revenue))),
         "--", color=COLORS['danger'], linewidth=2, label='Trend', alpha=0.7)

ax3.set_xlabel('Month', fontsize=12, fontweight='bold')
ax3.set_ylabel('Revenue (₦ Millions)', fontsize=12, fontweight='bold')
ax3.set_title('Monthly Revenue Trend', fontsize=14, fontweight='bold', pad=15)
ax3.grid(True, alpha=0.3)
ax3.legend(fontsize=11)
plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.savefig('powerpoint_slides/03_revenue_insights.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("✓ Saved: 03_revenue_insights.png\n")


# ============================================================================
# SLIDE 4: CHURN ANALYSIS
# ============================================================================
print("Creating Slide 4: Churn Analysis...")

fig = plt.figure(figsize=(16, 9), facecolor='white')
gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

fig.suptitle('Customer Churn Analysis', fontsize=22, fontweight='bold', y=0.98)

# Top Left: Churn Risk Distribution
ax1 = fig.add_subplot(gs[0, 0])
risk_counts = rfm_df['Churn_Risk_Level'].value_counts()
risk_order = ['Low', 'Medium', 'High', 'Critical']
risk_counts = risk_counts.reindex(risk_order, fill_value=0)
risk_colors = ['#28a745', '#ffc107', '#fd7e14', '#dc3545']

bars = ax1.bar(risk_order, risk_counts.values, color=risk_colors, alpha=0.8, width=0.6)
for bar, value in zip(bars, risk_counts.values):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(value):,}\n({value/len(rfm_df)*100:.1f}%)',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

ax1.set_ylabel('Number of Customers', fontsize=12, fontweight='bold')
ax1.set_title('Churn Risk Distribution', fontsize=14, fontweight='bold', pad=15)
ax1.grid(axis='y', alpha=0.3)

# Top Right: Recency Category Distribution
ax2 = fig.add_subplot(gs[0, 1])
recency_cats = rfm_df['Recency_Category'].value_counts()
colors2 = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(recency_cats)))
wedges, texts, autotexts = ax2.pie(recency_cats, labels=recency_cats.index,
                                     autopct='%1.1f%%', startangle=90,
                                     colors=colors2)
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(11)
ax2.set_title('Customer Status by Recency', fontsize=14, fontweight='bold', pad=15)

# Bottom Left: Revenue at Risk by Segment
ax3 = fig.add_subplot(gs[1, 0])
churned = rfm_df[rfm_df['Recency'] > 90]
risk_revenue = churned.groupby('RFM_Segment')['Monetary'].sum().sort_values(ascending=True) / 1e6
colors3 = plt.cm.Reds(np.linspace(0.4, 0.9, len(risk_revenue)))
bars = ax3.barh(range(len(risk_revenue)), risk_revenue.values, color=colors3, alpha=0.8)
ax3.set_yticks(range(len(risk_revenue)))
ax3.set_yticklabels(risk_revenue.index, fontsize=10)
ax3.set_xlabel('Revenue at Risk (₦ Millions)', fontsize=12, fontweight='bold')
ax3.set_title('Revenue at Risk by Segment', fontsize=14, fontweight='bold', pad=15)
ax3.grid(axis='x', alpha=0.3)
for i, value in enumerate(risk_revenue.values):
    ax3.text(value, i, f'  ₦{value:.1f}M', va='center', fontsize=10, fontweight='bold')

# Bottom Right: Key Churn Metrics
ax4 = fig.add_subplot(gs[1, 1])
ax4.axis('off')

churn_metrics = [
    ('Total Churned', f"{len(churned):,}", 'customers', COLORS['danger']),
    ('Churn Rate', f"{len(churned)/len(rfm_df)*100:.1f}%", 'of customer base', COLORS['warning']),
    ('Revenue Lost', f"₦{churned['Monetary'].sum()/1e9:.2f}B", 'total value', COLORS['red']),
    ('Avg Days Inactive', f"{churned['Recency'].mean():.0f}", 'days', COLORS['info'])
]

y_pos = 0.85
for title, value, subtitle, color in churn_metrics:
    ax4.text(0.1, y_pos, title, fontsize=13, fontweight='bold', color=COLORS['info'])
    ax4.text(0.5, y_pos, value, fontsize=18, fontweight='bold', color=color)
    ax4.text(0.5, y_pos-0.08, subtitle, fontsize=10, color=COLORS['info'], style='italic')
    y_pos -= 0.25

ax4.set_title('Key Churn Metrics', fontsize=14, fontweight='bold', pad=15, loc='left')

plt.savefig('powerpoint_slides/04_churn_analysis.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("✓ Saved: 04_churn_analysis.png\n")


# ============================================================================
# SLIDE 5: CUSTOMER VALUE ANALYSIS
# ============================================================================
print("Creating Slide 5: Customer Value Analysis...")

fig = plt.figure(figsize=(16, 9), facecolor='white')
gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

fig.suptitle('Customer Lifetime Value Analysis', fontsize=22, fontweight='bold', y=0.98)

# Top Left: CLV Distribution
ax1 = fig.add_subplot(gs[0, 0])
clv_categories = rfm_df['CLV_Category'].value_counts()
cat_order = ['Very Low Value', 'Low Value', 'Medium Value', 'High Value', 'Very High Value']
clv_categories = clv_categories.reindex(cat_order, fill_value=0)
colors_clv = plt.cm.YlGn(np.linspace(0.3, 0.9, len(clv_categories)))

bars = ax1.bar(range(len(clv_categories)), clv_categories.values, color=colors_clv, alpha=0.8)
ax1.set_xticks(range(len(clv_categories)))
ax1.set_xticklabels(['Very Low', 'Low', 'Medium', 'High', 'Very High'], fontsize=11)
ax1.set_ylabel('Number of Customers', fontsize=12, fontweight='bold')
ax1.set_title('CLV Category Distribution', fontsize=14, fontweight='bold', pad=15)
ax1.grid(axis='y', alpha=0.3)

for bar, value in zip(bars, clv_categories.values):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(value):,}',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

# Top Right: Top 10 Customers by CLV
ax2 = fig.add_subplot(gs[0, 1])
top_10_clv = rfm_df.nlargest(10, 'Predicted_CLV')[['Customer_ID', 'Predicted_CLV']].reset_index(drop=True)
top_10_clv['Customer_ID'] = top_10_clv['Customer_ID'].astype(str)
colors_top = plt.cm.plasma(np.linspace(0.2, 0.8, 10))

bars = ax2.barh(range(10), top_10_clv['Predicted_CLV'].values / 1e6, color=colors_top, alpha=0.8)
ax2.set_yticks(range(10))
ax2.set_yticklabels([f"Customer {i+1}" for i in range(10)], fontsize=10)
ax2.set_xlabel('Predicted CLV (₦ Millions)', fontsize=12, fontweight='bold')
ax2.set_title('Top 10 Customers by Predicted CLV', fontsize=14, fontweight='bold', pad=15)
ax2.grid(axis='x', alpha=0.3)
ax2.invert_yaxis()

for i, value in enumerate(top_10_clv['Predicted_CLV'].values / 1e6):
    ax2.text(value, i, f'  ₦{value:.2f}M', va='center', fontsize=10, fontweight='bold')

# Bottom: RFM Score Distribution
ax3 = fig.add_subplot(gs[1, :])
rfm_score_dist = rfm_df['RFM_Score'].value_counts().sort_index()

bars = ax3.bar(rfm_score_dist.index, rfm_score_dist.values,
               color=COLORS['primary'], alpha=0.7, edgecolor='black', linewidth=0.5)

# Highlight high-value customers
high_value_threshold = rfm_df['RFM_Score'].quantile(0.75)
for bar, score in zip(bars, rfm_score_dist.index):
    if score >= high_value_threshold:
        bar.set_color(COLORS['success'])
        bar.set_alpha(0.9)

ax3.axvline(high_value_threshold, color=COLORS['danger'], linestyle='--',
           linewidth=2, label=f'Top 25% (Score ≥ {high_value_threshold:.0f})', alpha=0.7)

ax3.set_xlabel('RFM Score', fontsize=12, fontweight='bold')
ax3.set_ylabel('Number of Customers', fontsize=12, fontweight='bold')
ax3.set_title('RFM Score Distribution', fontsize=14, fontweight='bold', pad=15)
ax3.grid(axis='y', alpha=0.3)
ax3.legend(fontsize=11)

plt.savefig('powerpoint_slides/05_customer_value_analysis.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("✓ Saved: 05_customer_value_analysis.png\n")


# ============================================================================
# SLIDE 6: CUSTOMER BEHAVIOR PATTERNS
# ============================================================================
print("Creating Slide 6: Customer Behavior Patterns...")

fig = plt.figure(figsize=(16, 9), facecolor='white')
gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

fig.suptitle('Customer Behavior Patterns', fontsize=22, fontweight='bold', y=0.98)

# Top Left: Frequency Category Distribution
ax1 = fig.add_subplot(gs[0, 0])
freq_cat = rfm_df['Frequency_Category'].value_counts()
freq_order = ['One-time', 'Low', 'Medium', 'High', 'Very High']
freq_cat = freq_cat.reindex(freq_order, fill_value=0)
colors_freq = ['#E63946', '#F77F00', '#FCBF49', '#06A77D', '#118AB2']

bars = ax1.bar(range(len(freq_cat)), freq_cat.values, color=colors_freq, alpha=0.8)
ax1.set_xticks(range(len(freq_cat)))
ax1.set_xticklabels(freq_order, fontsize=11)
ax1.set_ylabel('Number of Customers', fontsize=12, fontweight='bold')
ax1.set_title('Purchase Frequency Categories', fontsize=14, fontweight='bold', pad=15)
ax1.grid(axis='y', alpha=0.3)

for bar, value in zip(bars, freq_cat.values):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(value):,}\n({value/len(rfm_df)*100:.1f}%)',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

# Top Right: Transaction Day of Week
ax2 = fig.add_subplot(gs[0, 1])
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_trans = trans_df['DayName'].value_counts().reindex(day_order)
colors_days = plt.cm.Set2(range(7))

bars = ax2.bar(range(7), day_trans.values, color=colors_days, alpha=0.8)
ax2.set_xticks(range(7))
ax2.set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], fontsize=11)
ax2.set_ylabel('Number of Transactions', fontsize=12, fontweight='bold')
ax2.set_title('Transactions by Day of Week', fontsize=14, fontweight='bold', pad=15)
ax2.grid(axis='y', alpha=0.3)

# Highlight weekend
bars[5].set_alpha(0.5)
bars[6].set_alpha(0.5)

# Bottom Left: Purchase Timing Status
ax3 = fig.add_subplot(gs[1, 0])
timing_status = rfm_df['Purchase_Timing_Status'].value_counts()
colors_timing = plt.cm.RdYlGn(np.linspace(0.9, 0.2, len(timing_status)))

wedges, texts, autotexts = ax3.pie(timing_status, labels=timing_status.index,
                                     autopct='%1.1f%%', startangle=90,
                                     colors=colors_timing, textprops={'fontsize': 10})
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(11)

ax3.set_title('Purchase Timing Status', fontsize=14, fontweight='bold', pad=15)

# Bottom Right: Average Order Value by Segment
ax4 = fig.add_subplot(gs[1, 1])
aov_by_segment = rfm_df.groupby('RFM_Segment')['Avg_Order_Value'].mean().sort_values(ascending=False).head(8)
colors_aov = plt.cm.viridis(np.linspace(0.3, 0.9, len(aov_by_segment)))

bars = ax4.barh(range(len(aov_by_segment)), aov_by_segment.values / 1000, color=colors_aov, alpha=0.8)
ax4.set_yticks(range(len(aov_by_segment)))
ax4.set_yticklabels(aov_by_segment.index, fontsize=10)
ax4.set_xlabel('Average Order Value (₦ Thousands)', fontsize=12, fontweight='bold')
ax4.set_title('Avg Order Value by Segment (Top 8)', fontsize=14, fontweight='bold', pad=15)
ax4.grid(axis='x', alpha=0.3)

for i, value in enumerate(aov_by_segment.values / 1000):
    ax4.text(value, i, f'  ₦{value:.0f}K', va='center', fontsize=10, fontweight='bold')

plt.savefig('powerpoint_slides/06_customer_behavior.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("✓ Saved: 06_customer_behavior.png\n")


# ============================================================================
# SLIDE 7: RECOMMENDATIONS & OPPORTUNITIES
# ============================================================================
print("Creating Slide 7: Recommendations & Opportunities...")

try:
    recommendations_df = pd.read_csv('product_recommendations.csv')
    cross_sell_df = pd.read_csv('cross_sell_opportunities.csv')

    fig = plt.figure(figsize=(16, 9), facecolor='white')
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

    fig.suptitle('Product Recommendations & Growth Opportunities', fontsize=22, fontweight='bold', y=0.98)

    # Top Left: Top Recommended Categories
    ax1 = fig.add_subplot(gs[0, 0])
    top_recs = recommendations_df['Recommended_Category'].value_counts().head(10)
    colors_recs = plt.cm.Set3(range(len(top_recs)))

    bars = ax1.barh(range(len(top_recs)), top_recs.values, color=colors_recs, alpha=0.8)
    ax1.set_yticks(range(len(top_recs)))
    ax1.set_yticklabels(top_recs.index, fontsize=11)
    ax1.set_xlabel('Number of Recommendations', fontsize=12, fontweight='bold')
    ax1.set_title('Top 10 Recommended Product Categories', fontsize=14, fontweight='bold', pad=15)
    ax1.grid(axis='x', alpha=0.3)
    ax1.invert_yaxis()

    for i, value in enumerate(top_recs.values):
        ax1.text(value, i, f'  {int(value):,}', va='center', fontsize=10, fontweight='bold')

    # Top Right: Recommendation Confidence
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.hist(recommendations_df['Confidence'], bins=30, color=COLORS['primary'],
            alpha=0.7, edgecolor='black', linewidth=0.5)
    ax2.axvline(0.7, color=COLORS['danger'], linestyle='--', linewidth=2,
               label='High Confidence (0.7)', alpha=0.7)
    ax2.axvline(recommendations_df['Confidence'].mean(), color=COLORS['success'],
               linestyle='--', linewidth=2,
               label=f'Average ({recommendations_df["Confidence"].mean():.2f})', alpha=0.7)
    ax2.set_xlabel('Confidence Score', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Number of Recommendations', fontsize=12, fontweight='bold')
    ax2.set_title('Recommendation Confidence Distribution', fontsize=14, fontweight='bold', pad=15)
    ax2.grid(axis='y', alpha=0.3)
    ax2.legend(fontsize=10)

    # Bottom Left: Cross-Sell Revenue Potential
    ax3 = fig.add_subplot(gs[1, 0])
    top_cross_sell = cross_sell_df.groupby('Recommended_Category')['Potential_Value'].sum().sort_values(ascending=False).head(8)
    colors_cs = plt.cm.Greens(np.linspace(0.4, 0.9, len(top_cross_sell)))

    bars = ax3.barh(range(len(top_cross_sell)), top_cross_sell.values / 1e6, color=colors_cs, alpha=0.8)
    ax3.set_yticks(range(len(top_cross_sell)))
    ax3.set_yticklabels(top_cross_sell.index, fontsize=11)
    ax3.set_xlabel('Potential Revenue (₦ Millions)', fontsize=12, fontweight='bold')
    ax3.set_title('Cross-Sell Revenue Potential by Category', fontsize=14, fontweight='bold', pad=15)
    ax3.grid(axis='x', alpha=0.3)
    ax3.invert_yaxis()

    for i, value in enumerate(top_cross_sell.values / 1e6):
        ax3.text(value, i, f'  ₦{value:.1f}M', va='center', fontsize=10, fontweight='bold')

    # Bottom Right: Key Opportunity Metrics
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.axis('off')

    opp_metrics = [
        ('Total Recommendations', f"{len(recommendations_df):,}", 'generated', COLORS['primary']),
        ('Customers Covered', f"{recommendations_df['Customer_ID'].nunique():,}", 'unique customers', COLORS['success']),
        ('Cross-Sell Opportunities', f"{len(cross_sell_df):,}", 'identified', COLORS['purple']),
        ('Potential Revenue', f"₦{cross_sell_df['Potential_Value'].sum()/1e9:.2f}B", 'total value', COLORS['green'])
    ]

    y_pos = 0.85
    for title, value, subtitle, color in opp_metrics:
        ax4.text(0.1, y_pos, title, fontsize=13, fontweight='bold', color=COLORS['info'])
        ax4.text(0.6, y_pos, value, fontsize=18, fontweight='bold', color=color)
        ax4.text(0.6, y_pos-0.08, subtitle, fontsize=10, color=COLORS['info'], style='italic')
        y_pos -= 0.25

    ax4.set_title('Key Opportunity Metrics', fontsize=14, fontweight='bold', pad=15, loc='left')

    plt.savefig('powerpoint_slides/07_recommendations_opportunities.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✓ Saved: 07_recommendations_opportunities.png\n")

except FileNotFoundError:
    print("⚠ Skipping recommendations slide - recommendation files not found\n")


# ============================================================================
# SLIDE 8: ACTION PLAN & NEXT STEPS
# ============================================================================
print("Creating Slide 8: Strategic Action Plan...")

fig = plt.figure(figsize=(16, 9), facecolor='white')
fig.patch.set_facecolor('white')

# Title
fig.text(0.5, 0.95, 'STRATEGIC ACTION PLAN',
         ha='center', fontsize=28, fontweight='bold', color=COLORS['primary'])
fig.text(0.5, 0.90, 'Immediate Priorities & Revenue Opportunities',
         ha='center', fontsize=18, color=COLORS['info'])

# Priority Actions
actions = [
    {
        'priority': 'CRITICAL',
        'action': 'Save High-Risk VIP Customers',
        'target': f"{len(rfm_df[(rfm_df['Churn_Risk_Level'].isin(['High', 'Critical'])) & (rfm_df['Monetary'] > rfm_df['Monetary'].quantile(0.5))]):,} customers",
        'impact': f"₦{rfm_df[(rfm_df['Churn_Risk_Level'].isin(['High', 'Critical'])) & (rfm_df['Monetary'] > rfm_df['Monetary'].quantile(0.5))]['Monetary'].sum()/1e9:.2f}B at risk",
        'timeline': 'Week 1',
        'color': COLORS['danger']
    },
    {
        'priority': 'HIGH',
        'action': 'Reactivate Dormant Champions',
        'target': f"{len(rfm_df[(rfm_df['RFM_Segment'] == 'Champions') & (rfm_df['Recency'] > 90)]):,} customers",
        'impact': f"₦{rfm_df[(rfm_df['RFM_Segment'] == 'Champions') & (rfm_df['Recency'] > 90)]['Monetary'].sum()/1e6:.0f}M potential",
        'timeline': 'Week 2-4',
        'color': COLORS['warning']
    },
    {
        'priority': 'MEDIUM',
        'action': 'Cross-Sell to High-Value Customers',
        'target': f"{len(cross_sell_df) if 'cross_sell_df' in locals() else 0:,} opportunities",
        'impact': f"₦{cross_sell_df['Potential_Value'].sum()/1e6 if 'cross_sell_df' in locals() else 0:.0f}M potential",
        'timeline': 'Month 2-3',
        'color': COLORS['success']
    },
    {
        'priority': 'ONGOING',
        'action': 'Implement Loyalty Program',
        'target': f"{len(rfm_df[rfm_df['RFM_Segment'].isin(['Champions', 'Loyal Customers'])]):,} customers",
        'impact': 'Retain top customers',
        'timeline': 'Continuous',
        'color': COLORS['primary']
    }
]

# Create action boxes
y_positions = [0.70, 0.52, 0.34, 0.16]

for action, y_pos in zip(actions, y_positions):
    # Box
    ax = fig.add_axes([0.08, y_pos, 0.85, 0.14])
    ax.add_patch(Rectangle((0, 0), 1, 1, facecolor=action['color'], alpha=0.15, transform=ax.transAxes))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Priority badge
    ax.text(0.02, 0.75, action['priority'],
            ha='left', va='center', fontsize=11, color='white',
            transform=ax.transAxes, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=action['color'], alpha=0.9))

    # Action
    ax.text(0.15, 0.75, action['action'],
            ha='left', va='center', fontsize=16, color=action['color'],
            transform=ax.transAxes, fontweight='bold')

    # Target
    ax.text(0.15, 0.45, f"Target: {action['target']}",
            ha='left', va='center', fontsize=12, color=COLORS['info'],
            transform=ax.transAxes)

    # Impact
    ax.text(0.15, 0.20, f"Impact: {action['impact']}",
            ha='left', va='center', fontsize=12, color=action['color'],
            transform=ax.transAxes, fontweight='bold')

    # Timeline
    ax.text(0.88, 0.50, action['timeline'],
            ha='right', va='center', fontsize=13, color=COLORS['info'],
            transform=ax.transAxes, style='italic',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=action['color'], linewidth=2))

plt.savefig('powerpoint_slides/08_action_plan.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("✓ Saved: 08_action_plan.png\n")


# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("="*80)
print("✅ ALL POWERPOINT SLIDES GENERATED SUCCESSFULLY!")
print("="*80)
print("\n📁 Slides saved in 'powerpoint_slides/' directory:")
print("\n  1. 01_executive_summary.png - Key business metrics")
print("  2. 02_customer_segmentation.png - Segment distribution & revenue")
print("  3. 03_revenue_insights.png - Revenue analysis by multiple dimensions")
print("  4. 04_churn_analysis.png - Churn risk & customer status")
print("  5. 05_customer_value_analysis.png - CLV distribution & top customers")
print("  6. 06_customer_behavior.png - Purchase patterns & timing")
print("  7. 07_recommendations_opportunities.png - Product recommendations")
print("  8. 08_action_plan.png - Strategic priorities & timeline")

print("\n💡 PRO TIP: All slides are 16:9 format, perfect for PowerPoint!")
print("   Simply insert these images into your presentation.")
print("\n🎯 Each slide is designed for executive presentations with:")
print("   • Clean, professional design")
print("   • High-resolution (300 DPI)")
print("   • Clear labels and insights")
print("   • Color-coded for easy understanding")

print("\n🚀 Ready to present your findings!")
