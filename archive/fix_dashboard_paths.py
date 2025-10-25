"""
Quick Fix Script for Afrimash Dashboard
Fixes the critical file path issues
"""

import os

# Read the current dashboard file
dashboard_file = 'afrimash_dashboard.py'

print("Reading current dashboard file...")
with open(dashboard_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("Applying fixes...")

# Fix 1: Change Linux absolute paths to relative paths
fixes = [
    ("'/home/claude/rfm_with_predictions.csv'", "'rfm_with_predictions.csv'"),
    ("'/home/claude/transactions_clean.csv'", "'transactions_clean.csv'"),
    ("'/home/claude/product_recommendations.csv'", "'product_recommendations.csv'"),
]

changes_made = 0
for old, new in fixes:
    if old in content:
        content = content.replace(old, new)
        changes_made += 1
        print(f"  ✓ Fixed: {old} → {new}")

# Fix 2: Update load_data function to handle optional files
old_load_data = """    try:
        rfm_data = pd.read_csv('rfm_with_predictions.csv')
        transactions = pd.read_csv('transactions_clean.csv')
        recommendations = pd.read_csv('product_recommendations.csv')

        # Parse dates
        transactions['Date'] = pd.to_datetime(transactions['Date'])

        return rfm_data, transactions, recommendations
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None"""

new_load_data = """    try:
        # Use relative paths - works on all operating systems
        rfm_data = pd.read_csv('rfm_with_predictions.csv')
        transactions = pd.read_csv('transactions_clean.csv')

        # Try to load optional files
        try:
            recommendations = pd.read_csv('product_recommendations.csv')
        except:
            recommendations = None

        try:
            cross_sell = pd.read_csv('cross_sell_opportunities.csv')
        except:
            cross_sell = None

        # Parse dates
        transactions['Date'] = pd.to_datetime(transactions['Date'])

        return rfm_data, transactions, recommendations, cross_sell
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Please ensure rfm_with_predictions.csv and transactions_clean.csv are in the same directory as this dashboard.")
        return None, None, None, None"""

if old_load_data in content:
    content = content.replace(old_load_data, new_load_data)
    changes_made += 1
    print(f"  ✓ Updated load_data function to handle optional files")

# Fix 3: Update the load_data call
old_call = "rfm_data, transactions, recommendations = load_data()"
new_call = "rfm_data, transactions, recommendations, cross_sell = load_data()"

if old_call in content:
    content = content.replace(old_call, new_call)
    changes_made += 1
    print(f"  ✓ Updated load_data() call")

# Write the fixed file
print("\nWriting fixed dashboard...")
with open(dashboard_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nSUCCESS! Applied {changes_made} fixes to {dashboard_file}")
print("\nThe dashboard is now ready to use!")
print("\nTo run the dashboard:")
print("  streamlit run afrimash_dashboard.py")
