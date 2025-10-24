"""
AFRIMASH CUSTOMER INTELLIGENCE CHALLENGE
Hour 7: Product Recommendation Engine
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from itertools import combinations
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)

print("="*80)
print("AFRIMASH PRODUCT RECOMMENDATION ENGINE")
print("="*80)

# ============================================================================
# 1. LOAD DATA
# ============================================================================
print("\n📁 STEP 1: LOADING DATA...")
rfm_df = pd.read_csv('rfm_with_predictions.csv')
trans_df = pd.read_csv('transactions_clean.csv')

print(f"✓ Loaded {len(rfm_df):,} customers")
print(f"✓ Loaded {len(trans_df):,} transactions")

# ============================================================================
# 2. PREPARE PRODUCT DATA
# ============================================================================
print("\n🛒 STEP 2: PREPARING PRODUCT DATA...")

# Get category columns
category_cols = [col for col in rfm_df.columns if col.startswith('Category_')]
print(f"✓ Found {len(category_cols)} product categories")

# Create customer-product matrix
customer_product_matrix = rfm_df[['Customer_ID'] + category_cols].copy()
print(f"✓ Created customer-product matrix: {customer_product_matrix.shape}")

# ============================================================================
# 3. COLLABORATIVE FILTERING RECOMMENDATIONS
# ============================================================================
print("\n🤝 STEP 3: COLLABORATIVE FILTERING...")

def get_similar_customers(customer_id, customer_product_matrix, top_n=10):
    """Find similar customers based on purchase patterns"""
    # Get target customer's purchases
    target_purchases = customer_product_matrix[customer_product_matrix['Customer_ID'] == customer_id].iloc[0, 1:].values

    # Calculate similarity with all other customers (Jaccard similarity)
    similarities = []
    for idx, row in customer_product_matrix.iterrows():
        if row['Customer_ID'] == customer_id:
            continue

        other_purchases = row[1:].values

        # Jaccard similarity
        intersection = np.sum(np.minimum(target_purchases, other_purchases))
        union = np.sum(np.maximum(target_purchases, other_purchases))

        if union > 0:
            similarity = intersection / union
            similarities.append((row['Customer_ID'], similarity))

    # Sort by similarity
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_n]

def recommend_products_collaborative(customer_id, customer_product_matrix, rfm_df, top_n=5):
    """Recommend products based on similar customers"""
    # Get similar customers
    similar_customers = get_similar_customers(customer_id, customer_product_matrix, top_n=20)

    if not similar_customers:
        return []

    # Get target customer's current purchases
    target_row = customer_product_matrix[customer_product_matrix['Customer_ID'] == customer_id]
    if target_row.empty:
        return []

    target_purchases = target_row.iloc[0, 1:].values
    category_names = category_cols

    # Count recommendations from similar customers
    recommendations = defaultdict(float)

    for similar_id, similarity in similar_customers:
        similar_row = customer_product_matrix[customer_product_matrix['Customer_ID'] == similar_id]
        if similar_row.empty:
            continue

        similar_purchases = similar_row.iloc[0, 1:].values

        # Recommend categories that similar customer bought but target didn't
        for i, category in enumerate(category_names):
            if similar_purchases[i] > 0 and target_purchases[i] == 0:
                recommendations[category] += similarity

    # Sort by score
    sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)

    # Format recommendations
    result = []
    for category, score in sorted_recs[:top_n]:
        category_name = category.replace('Category_', '')
        result.append({
            'Category': category_name,
            'Score': score,
            'Method': 'Collaborative Filtering'
        })

    return result

# ============================================================================
# 4. ASSOCIATION RULES (MARKET BASKET ANALYSIS)
# ============================================================================
print("\n🛍️ STEP 4: MARKET BASKET ANALYSIS...")

def calculate_association_rules(customer_product_matrix, min_support=0.01, min_confidence=0.1):
    """Calculate product association rules"""
    # Get binary purchase matrix
    purchase_matrix = customer_product_matrix.iloc[:, 1:].values > 0
    category_names = [col.replace('Category_', '') for col in category_cols]

    n_customers = len(purchase_matrix)

    # Calculate support for individual items
    item_support = {}
    for i, category in enumerate(category_names):
        support = np.sum(purchase_matrix[:, i]) / n_customers
        if support >= min_support:
            item_support[category] = support

    # Calculate association rules for pairs
    rules = []

    for i, cat1 in enumerate(category_names):
        if cat1 not in item_support:
            continue

        for j, cat2 in enumerate(category_names):
            if i >= j or cat2 not in item_support:
                continue

            # Count co-occurrences
            both = np.sum(purchase_matrix[:, i] & purchase_matrix[:, j])
            support_both = both / n_customers

            if support_both < min_support:
                continue

            # Calculate confidence and lift
            confidence_1_to_2 = support_both / item_support[cat1]
            confidence_2_to_1 = support_both / item_support[cat2]
            lift = support_both / (item_support[cat1] * item_support[cat2])

            if confidence_1_to_2 >= min_confidence:
                rules.append({
                    'Antecedent': cat1,
                    'Consequent': cat2,
                    'Support': support_both,
                    'Confidence': confidence_1_to_2,
                    'Lift': lift
                })

            if confidence_2_to_1 >= min_confidence:
                rules.append({
                    'Antecedent': cat2,
                    'Consequent': cat1,
                    'Support': support_both,
                    'Confidence': confidence_2_to_1,
                    'Lift': lift
                })

    return pd.DataFrame(rules)

# Calculate association rules
association_rules = calculate_association_rules(customer_product_matrix, min_support=0.01, min_confidence=0.1)
association_rules = association_rules.sort_values('Lift', ascending=False)

print(f"✓ Found {len(association_rules)} association rules")
print(f"\n📊 Top 5 Association Rules:")
if len(association_rules) > 0:
    print(association_rules.head()[['Antecedent', 'Consequent', 'Confidence', 'Lift']])

# Save association rules
association_rules.to_csv('product_association_rules.csv', index=False)
print(f"\n✓ Saved product_association_rules.csv")

def recommend_products_association(customer_id, customer_product_matrix, association_rules, top_n=5):
    """Recommend products based on association rules"""
    # Get customer's current purchases
    target_row = customer_product_matrix[customer_product_matrix['Customer_ID'] == customer_id]
    if target_row.empty:
        return []

    target_purchases = target_row.iloc[0, 1:].values
    purchased_categories = [col.replace('Category_', '') for i, col in enumerate(category_cols) if target_purchases[i] > 0]

    if not purchased_categories:
        return []

    # Find recommendations based on rules
    recommendations = defaultdict(float)

    for category in purchased_categories:
        relevant_rules = association_rules[association_rules['Antecedent'] == category]

        for _, rule in relevant_rules.iterrows():
            consequent = rule['Consequent']
            # Check if customer hasn't bought this yet
            consequent_col = f'Category_{consequent}'
            if consequent_col in category_cols:
                idx = category_cols.index(consequent_col)
                if target_purchases[idx] == 0:
                    # Score based on confidence and lift
                    score = rule['Confidence'] * rule['Lift']
                    recommendations[consequent] = max(recommendations[consequent], score)

    # Sort by score
    sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)

    # Format recommendations
    result = []
    for category, score in sorted_recs[:top_n]:
        result.append({
            'Category': category,
            'Score': score,
            'Method': 'Association Rules'
        })

    return result

# ============================================================================
# 5. HYBRID RECOMMENDATION SYSTEM
# ============================================================================
print("\n🎯 STEP 5: BUILDING HYBRID RECOMMENDATION SYSTEM...")

def get_hybrid_recommendations(customer_id, customer_product_matrix, association_rules, rfm_df, top_n=5):
    """Combine collaborative filtering and association rules"""

    # Get collaborative recommendations
    collab_recs = recommend_products_collaborative(customer_id, customer_product_matrix, rfm_df, top_n=10)

    # Get association-based recommendations
    assoc_recs = recommend_products_association(customer_id, customer_product_matrix, association_rules, top_n=10)

    # Combine and score
    combined_scores = defaultdict(lambda: {'score': 0, 'methods': []})

    for rec in collab_recs:
        category = rec['Category']
        combined_scores[category]['score'] += rec['Score'] * 0.3  # 30% weight
        combined_scores[category]['methods'].append('Collaborative')

    for rec in assoc_recs:
        category = rec['Category']
        combined_scores[category]['score'] += rec['Score'] * 0.7  # 70% weight
        combined_scores[category]['methods'].append('Association')

    # Sort by combined score
    sorted_recs = sorted(combined_scores.items(), key=lambda x: x[1]['score'], reverse=True)

    # Format final recommendations
    recommendations = []
    for category, data in sorted_recs[:top_n]:
        # Normalize score to 0-1 range
        normalized_score = min(1.0, data['score'] / 5.0)

        recommendations.append({
            'Customer_ID': customer_id,
            'Recommended_Category': category,
            'Confidence': normalized_score,
            'Reason': ', '.join(data['methods'])
        })

    return recommendations

# ============================================================================
# 6. GENERATE RECOMMENDATIONS FOR ALL CUSTOMERS
# ============================================================================
print("\n🚀 STEP 6: GENERATING RECOMMENDATIONS...")

# Generate for top customers (or all if dataset is small)
target_customers = rfm_df.nlargest(1000, 'Monetary')['Customer_ID'].tolist()
print(f"✓ Generating recommendations for {len(target_customers):,} customers...")

all_recommendations = []
for i, customer_id in enumerate(target_customers):
    if (i + 1) % 100 == 0:
        print(f"  Progress: {i+1}/{len(target_customers)} customers processed...")

    recs = get_hybrid_recommendations(customer_id, customer_product_matrix, association_rules, rfm_df, top_n=5)
    all_recommendations.extend(recs)

recommendations_df = pd.DataFrame(all_recommendations)
print(f"\n✓ Generated {len(recommendations_df):,} recommendations")

# Save recommendations
recommendations_df.to_csv('product_recommendations.csv', index=False)
print(f"✓ Saved product_recommendations.csv")

# ============================================================================
# 7. CROSS-SELL OPPORTUNITIES
# ============================================================================
print("\n💰 STEP 7: IDENTIFYING CROSS-SELL OPPORTUNITIES...")

# Identify customers who could buy more categories
cross_sell_opportunities = []

for _, customer in rfm_df.iterrows():
    customer_id = customer['Customer_ID']

    # Count categories purchased
    purchased_categories = sum([customer[col] for col in category_cols if col in customer.index])

    # If customer bought from <3 categories and has high CLV
    if purchased_categories < 3 and customer['Predicted_CLV'] > rfm_df['Predicted_CLV'].median():

        # Get recommendations for this customer
        customer_recs = recommendations_df[recommendations_df['Customer_ID'] == customer_id]

        if len(customer_recs) > 0:
            top_rec = customer_recs.iloc[0]

            cross_sell_opportunities.append({
                'Customer_ID': customer_id,
                'RFM_Segment': customer.get('RFM_Segment', 'Unknown'),
                'Current_Categories': purchased_categories,
                'Predicted_CLV': customer['Predicted_CLV'],
                'Recommended_Category': top_rec['Recommended_Category'],
                'Confidence': top_rec['Confidence'],
                'Potential_Value': customer['Predicted_CLV'] * 0.2  # Assume 20% uplift
            })

cross_sell_df = pd.DataFrame(cross_sell_opportunities)
cross_sell_df = cross_sell_df.sort_values('Potential_Value', ascending=False)

print(f"✓ Identified {len(cross_sell_df):,} cross-sell opportunities")
print(f"  Potential Revenue: ₵{cross_sell_df['Potential_Value'].sum()/1e9:.2f}B")

# Save cross-sell opportunities
cross_sell_df.to_csv('cross_sell_opportunities.csv', index=False)
print(f"✓ Saved cross_sell_opportunities.csv")

# ============================================================================
# 8. RECOMMENDATION SUMMARY STATISTICS
# ============================================================================
print("\n📊 STEP 8: CALCULATING SUMMARY STATISTICS...")

# Overall statistics
summary_stats = {
    'Total Customers Analyzed': f"{len(rfm_df):,}",
    'Customers with Recommendations': f"{len(target_customers):,}",
    'Total Recommendations Generated': f"{len(recommendations_df):,}",
    'Avg Recommendations per Customer': f"{len(recommendations_df)/len(target_customers):.1f}",
    'Unique Categories Recommended': recommendations_df['Recommended_Category'].nunique(),
    'Avg Recommendation Confidence': f"{recommendations_df['Confidence'].mean():.2f}",
    'High Confidence Recs (>0.7)': f"{len(recommendations_df[recommendations_df['Confidence'] > 0.7]):,} ({len(recommendations_df[recommendations_df['Confidence'] > 0.7])/len(recommendations_df)*100:.1f}%)",
    'Cross-sell Opportunities': f"{len(cross_sell_df):,}",
    'Product Association Rules': len(association_rules),
    'Top Recommended Category': recommendations_df['Recommended_Category'].mode()[0] if len(recommendations_df) > 0 else 'N/A'
}

summary_df = pd.DataFrame(list(summary_stats.items()), columns=['Metric', 'Value'])
summary_df.to_csv('recommendation_summary.csv', index=False)
print(f"✓ Saved recommendation_summary.csv")

# Top recommendations per customer
top_recs_per_customer = recommendations_df.sort_values(['Customer_ID', 'Confidence'], ascending=[True, False])
top_3_per_customer = top_recs_per_customer.groupby('Customer_ID').head(3)
top_3_per_customer.to_csv('top_recommendations_per_customer.csv', index=False)
print(f"✓ Saved top_recommendations_per_customer.csv")

# ============================================================================
# 9. VISUALIZATIONS
# ============================================================================
print("\n📊 STEP 9: CREATING VISUALIZATIONS...")

fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.suptitle('PRODUCT RECOMMENDATION ANALYSIS', fontsize=20, fontweight='bold')

# 9.1 Top Recommended Categories
ax = axes[0, 0]
if len(recommendations_df) > 0:
    top_categories = recommendations_df['Recommended_Category'].value_counts().head(10)
    colors = plt.cm.Set3(range(len(top_categories)))
    top_categories.plot(kind='barh', ax=ax, color=colors)
    ax.set_title('Top 10 Recommended Categories', fontsize=14, fontweight='bold')
    ax.set_xlabel('Number of Recommendations')
    for i, v in enumerate(top_categories.values):
        ax.text(v, i, f' {v:,}', va='center')

# 9.2 Recommendation Method Distribution
ax = axes[0, 1]
if len(recommendations_df) > 0:
    method_dist = recommendations_df['Reason'].value_counts()
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    ax.pie(method_dist.values, labels=method_dist.index, autopct='%1.1f%%',
           colors=colors[:len(method_dist)], startangle=90)
    ax.set_title('Recommendation Method Distribution', fontsize=14, fontweight='bold')

# 9.3 Confidence Distribution
ax = axes[0, 2]
if len(recommendations_df) > 0:
    ax.hist(recommendations_df['Confidence'], bins=30, color='steelblue', edgecolor='black', alpha=0.7)
    ax.axvline(0.7, color='red', linestyle='--', linewidth=2, label='High Confidence (0.7)')
    ax.set_xlabel('Confidence Score')
    ax.set_ylabel('Number of Recommendations')
    ax.set_title('Recommendation Confidence Distribution', fontsize=14, fontweight='bold')
    ax.legend()

# 9.4 Association Rules - Top Pairs
ax = axes[1, 0]
if len(association_rules) > 0:
    top_rules = association_rules.nlargest(10, 'Lift')
    rule_labels = [f"{row['Antecedent']}\n→ {row['Consequent']}" for _, row in top_rules.iterrows()]
    y_pos = range(len(rule_labels))
    ax.barh(y_pos, top_rules['Lift'].values, color='green', alpha=0.7)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(rule_labels, fontsize=9)
    ax.set_xlabel('Lift')
    ax.set_title('Top 10 Product Associations (by Lift)', fontsize=14, fontweight='bold')
    ax.invert_yaxis()

# 9.5 Cross-sell Potential by Segment
ax = axes[1, 1]
if len(cross_sell_df) > 0 and 'RFM_Segment' in cross_sell_df.columns:
    segment_potential = cross_sell_df.groupby('RFM_Segment')['Potential_Value'].sum() / 1e9
    segment_potential = segment_potential.sort_values(ascending=False)
    colors = plt.cm.Pastel1(range(len(segment_potential)))
    segment_potential.plot(kind='bar', ax=ax, color=colors)
    ax.set_title('Cross-sell Potential by Segment (₵B)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Potential Revenue (₵B)')
    ax.set_xlabel('Segment')
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    for i, v in enumerate(segment_potential.values):
        ax.text(i, v, f'₵{v:.2f}B', ha='center', va='bottom')

# 9.6 Recommendations by Customer CLV
ax = axes[1, 2]
if len(recommendations_df) > 0:
    # Merge with customer CLV
    recs_with_clv = recommendations_df.merge(
        rfm_df[['Customer_ID', 'Predicted_CLV', 'CLV_Category']],
        on='Customer_ID',
        how='left'
    )

    if 'CLV_Category' in recs_with_clv.columns:
        clv_recs = recs_with_clv['CLV_Category'].value_counts()
        colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(clv_recs)))
        clv_recs.plot(kind='bar', ax=ax, color=colors)
        ax.set_title('Recommendations by Customer CLV Category', fontsize=14, fontweight='bold')
        ax.set_ylabel('Number of Recommendations')
        ax.set_xlabel('CLV Category')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.savefig('recommendation_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Saved recommendation_analysis.png")

# Cross-sell Opportunities Visualization
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('CROSS-SELL OPPORTUNITIES ANALYSIS', fontsize=18, fontweight='bold')

# Top Cross-sell Opportunities
ax = axes[0, 0]
if len(cross_sell_df) > 0:
    top_cross_sell = cross_sell_df.nlargest(20, 'Potential_Value')
    ax.barh(range(len(top_cross_sell)), top_cross_sell['Potential_Value']/1e6, color='darkgreen', alpha=0.7)
    ax.set_yticks(range(len(top_cross_sell)))
    ax.set_yticklabels(top_cross_sell['Customer_ID'].values, fontsize=8)
    ax.set_xlabel('Potential Value (₵M)')
    ax.set_title('Top 20 Cross-sell Opportunities', fontsize=14, fontweight='bold')
    ax.invert_yaxis()

# Cross-sell by Current Categories
ax = axes[0, 1]
if len(cross_sell_df) > 0:
    category_dist = cross_sell_df['Current_Categories'].value_counts().sort_index()
    ax.bar(category_dist.index, category_dist.values, color='teal', alpha=0.7)
    ax.set_xlabel('Number of Current Categories')
    ax.set_ylabel('Number of Customers')
    ax.set_title('Cross-sell Customers by Current Category Count', fontsize=14, fontweight='bold')
    for i, v in enumerate(category_dist.values):
        ax.text(category_dist.index[i], v, f'{v:,}', ha='center', va='bottom')

# Recommended Categories for Cross-sell
ax = axes[1, 0]
if len(cross_sell_df) > 0:
    rec_categories = cross_sell_df['Recommended_Category'].value_counts().head(10)
    colors = plt.cm.Paired(range(len(rec_categories)))
    rec_categories.plot(kind='barh', ax=ax, color=colors)
    ax.set_title('Top Categories for Cross-sell', fontsize=14, fontweight='bold')
    ax.set_xlabel('Number of Opportunities')
    for i, v in enumerate(rec_categories.values):
        ax.text(v, i, f' {v:,}', va='center')

# CLV vs Cross-sell Confidence
ax = axes[1, 1]
if len(cross_sell_df) > 0:
    scatter = ax.scatter(cross_sell_df['Confidence'], cross_sell_df['Predicted_CLV'],
                        c=cross_sell_df['Potential_Value'], cmap='viridis',
                        alpha=0.6, s=50)
    ax.set_xlabel('Recommendation Confidence')
    ax.set_ylabel('Predicted CLV (₵)')
    ax.set_title('CLV vs Recommendation Confidence', fontsize=14, fontweight='bold')
    ax.set_yscale('log')
    plt.colorbar(scatter, ax=ax, label='Potential Value (₵)')
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('cross_sell_opportunities.png', dpi=300, bbox_inches='tight')
print("✓ Saved cross_sell_opportunities.png")

# ============================================================================
# 10. KEY INSIGHTS
# ============================================================================
print("\n" + "="*80)
print("📈 KEY INSIGHTS")
print("="*80)

print("\n🎯 RECOMMENDATION SUMMARY:")
for metric, value in summary_stats.items():
    print(f"  {metric}: {value}")

if len(recommendations_df) > 0:
    print(f"\n🏆 TOP 5 MOST RECOMMENDED CATEGORIES:")
    top_5_cats = recommendations_df['Recommended_Category'].value_counts().head(5)
    for i, (cat, count) in enumerate(top_5_cats.items(), 1):
        pct = (count / len(recommendations_df)) * 100
        print(f"  {i}. {cat}: {count:,} recommendations ({pct:.1f}%)")

if len(association_rules) > 0:
    print(f"\n🔗 TOP 5 PRODUCT ASSOCIATIONS:")
    top_5_rules = association_rules.nlargest(5, 'Lift')
    for i, (_, rule) in enumerate(top_5_rules.iterrows(), 1):
        print(f"  {i}. {rule['Antecedent']} → {rule['Consequent']}: Lift={rule['Lift']:.2f}, Confidence={rule['Confidence']:.2f}")

if len(cross_sell_df) > 0:
    print(f"\n💰 CROSS-SELL OPPORTUNITIES:")
    print(f"  Total Opportunities: {len(cross_sell_df):,}")
    print(f"  Potential Revenue: ₵{cross_sell_df['Potential_Value'].sum()/1e9:.2f}B")
    print(f"  Average Potential per Customer: ₵{cross_sell_df['Potential_Value'].mean()/1e6:.2f}M")
    print(f"  High Confidence (>0.7): {len(cross_sell_df[cross_sell_df['Confidence'] > 0.7]):,}")

print("\n" + "="*80)
print("✅ RECOMMENDATION ENGINE COMPLETE!")
print("="*80)
print("\n📁 Output Files:")
print("  1. product_recommendations.csv - All recommendations")
print("  2. product_association_rules.csv - Association rules")
print("  3. cross_sell_opportunities.csv - Cross-sell targets")
print("  4. recommendation_summary.csv - Summary statistics")
print("  5. top_recommendations_per_customer.csv - Top 3 per customer")
print("  6. recommendation_analysis.png - Recommendation visualizations")
print("  7. cross_sell_opportunities.png - Cross-sell visualizations")
