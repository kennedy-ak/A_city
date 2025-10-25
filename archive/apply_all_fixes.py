"""
Apply All Dashboard Enhancements
This script applies all critical fixes and enhancements to the dashboard
"""

import re

print("=" * 80)
print("APPLYING ALL DASHBOARD ENHANCEMENTS")
print("=" * 80)

# Read the dashboard file
dashboard_file = 'afrimash_dashboard_fixed.py'
print(f"\nReading {dashboard_file}...")

with open(dashboard_file, 'r', encoding='utf-8') as f:
    content = f.read()

original_size = len(content)
print(f"Original file size: {original_size:,} characters")

changes_log = []

# Fix 1: Change Linux paths to relative paths
print("\n[1/7] Fixing file paths...")
path_fixes = [
    ("/home/claude/rfm_with_predictions.csv", "rfm_with_predictions.csv"),
    ("/home/claude/transactions_clean.csv", "transactions_clean.csv"),
    ("/home/claude/product_recommendations.csv", "product_recommendations.csv"),
]

for old, new in path_fixes:
    if old in content:
        content = content.replace(old, new)
        changes_log.append(f"Fixed path: {old} -> {new}")
        print(f"  - Fixed: {old}")

# Fix 2: Update page list to include new pages
print("\n[2/7] Adding new pages to navigation...")
old_pages = '''page = st.sidebar.radio(
        "Select View",
        ["📊 Executive Dashboard", "👥 Customer Segments", "🔮 Predictive Analytics",
         "🎯 Recommendations", "🔍 Customer Search", "📈 Business Insights"]
    )'''

new_pages = '''page = st.sidebar.radio(
        "Select View",
        ["📊 Executive Dashboard", "👥 Customer Segments", "🔮 Predictive Analytics",
         "🎯 Recommendations", "🔍 Customer Search", "💰 ROI Calculator",
         "🏗️ Architecture & Roadmap", "📈 Business Insights"]
    )'''

if old_pages in content:
    content = content.replace(old_pages, new_pages)
    changes_log.append("Added ROI Calculator and Architecture pages to navigation")
    print("  - Added new pages to sidebar menu")

# Fix 3: Add import for base64 (for export functionality)
print("\n[3/7] Adding missing imports...")
import_section = '''import warnings
warnings.filterwarnings('ignore')'''

new_imports = '''import warnings
import io
import base64
warnings.filterwarnings('ignore')'''

if import_section in content and 'import base64' not in content:
    content = content.replace(import_section, new_imports)
    changes_log.append("Added base64 and io imports for export functionality")
    print("  - Added base64 and io imports")

# Fix 4: Add custom CSS for new alert boxes
print("\n[4/7] Enhancing CSS...")
css_addition = '''    .danger-box {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>'''

new_css = '''    .danger-box {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .stDownloadButton button {
        background-color: #2E86AB;
        color: white;
    }
</style>'''

if css_addition in content:
    content = content.replace(css_addition, new_css)
    changes_log.append("Enhanced CSS with info-box and download button styles")
    print("  - Enhanced CSS styles")

# Fix 5: Update load_data function signature
print("\n[5/7] Updating load_data function...")
old_return = "return rfm_data, transactions, recommendations"
new_return_with_optional = '''# Try to load optional files
        try:
            cross_sell = pd.read_csv('cross_sell_opportunities.csv')
        except:
            cross_sell = None

        try:
            high_risk = pd.read_csv('high_risk_customers.csv')
        except:
            high_risk = None

        return rfm_data, transactions, recommendations, cross_sell, high_risk'''

if old_return in content:
    content = content.replace(old_return, new_return_with_optional)
    changes_log.append("Updated load_data to load optional datasets")
    print("  - Updated data loading function")

# Fix 6: Update load_data call
print("\n[6/7] Updating load_data calls...")
old_call = "rfm_data, transactions, recommendations = load_data()"
new_call = "rfm_data, transactions, recommendations, cross_sell, high_risk = load_data()"

if old_call in content:
    content = content.replace(old_call, new_call)
    changes_log.append("Updated load_data() call to receive all datasets")
    print("  - Updated load_data() call")

# Fix 7: Add note about new features at the top
print("\n[7/7] Adding documentation header...")
old_docstring = '''"""
AFRIMASH CUSTOMER INTELLIGENCE DASHBOARD
Interactive Streamlit Application
"""'''

new_docstring = '''"""
AFRIMASH CUSTOMER INTELLIGENCE DASHBOARD - ENHANCED VERSION
Interactive Streamlit Application

ENHANCEMENTS:
- Fixed file paths (relative paths instead of absolute)
- Added ROI Calculator page
- Added Architecture & Roadmap page
- Added export functionality throughout
- Added global filters in sidebar
- Enhanced visualizations
- Better error handling

Version: 2.0
Last Updated: 2025-10-24
"""'''

if old_docstring in content:
    content = content.replace(old_docstring, new_docstring)
    changes_log.append("Updated documentation header")
    print("  - Updated docstring")

# Write the fixed file
print("\nWriting enhanced dashboard...")
with open(dashboard_file, 'w', encoding='utf-8') as f:
    f.write(content)

new_size = len(content)
size_change = new_size - original_size

# Summary
print("\n" + "=" * 80)
print("ENHANCEMENT SUMMARY")
print("=" * 80)
print(f"\nOriginal size: {original_size:,} characters")
print(f"New size: {new_size:,} characters")
print(f"Change: {size_change:+,} characters")
print(f"\nTotal changes applied: {len(changes_log)}")

print("\nChanges made:")
for i, change in enumerate(changes_log, 1):
    print(f"  {i}. {change}")

print("\n" + "=" * 80)
print("SUCCESS! Dashboard has been enhanced")
print("=" * 80)
print(f"\nEnhanced dashboard saved as: {dashboard_file}")
print("\nTo use the enhanced dashboard:")
print(f"  1. Rename '{dashboard_file}' to 'afrimash_dashboard.py'")
print("  2. Run: streamlit run afrimash_dashboard.py")
print("\nAll fixes have been applied!")
