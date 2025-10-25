"""
Example script showing how to use the API from Python
"""

import requests
import json
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"


def pretty_print(title: str, data: Any):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"📊 {title}")
    print('='*60)
    print(json.dumps(data, indent=2))


def main():
    """Demonstrate API usage"""
    
    print("🚀 Afrimash Customer Intelligence API - Usage Examples")
    print("="*60)
    
    try:
        # 1. Get Business Metrics
        print("\n1️⃣ Getting Business Metrics...")
        response = requests.get(f"{API_BASE_URL}/api/metrics")
        metrics = response.json()
        pretty_print("Business Metrics", metrics)
        
        # 2. Get Customer List with Filters
        print("\n2️⃣ Getting High-Risk Customers...")
        response = requests.get(
            f"{API_BASE_URL}/api/customers",
            params={
                "page": 1,
                "page_size": 5,
                "risk_level": "Critical"
            }
        )
        customers = response.json()
        pretty_print(f"High-Risk Customers (Total: {customers['total']})", 
                    customers['customers'][:3])  # Show first 3
        
        # 3. Get Specific Customer Profile
        print("\n3️⃣ Getting Customer Profile...")
        customer_id = "CUS000001"
        response = requests.get(f"{API_BASE_URL}/api/customers/{customer_id}")
        customer = response.json()
        
        print(f"\n📋 Customer Profile: {customer_id}")
        print(f"   Segment: {customer['rfm_segment']}")
        print(f"   Total Spent: ₦{customer['monetary']:,.0f}")
        print(f"   Predicted CLV: ₦{customer['predicted_clv']:,.0f}")
        print(f"   Churn Risk: {customer['churn_risk_level']} ({customer['churn_probability']:.1%})")
        print(f"   Recommendations: {len(customer['recommendations'])}")
        
        # 4. Get Product Recommendations
        if customer['recommendations']:
            print(f"\n🎯 Top Recommendations for {customer_id}:")
            for i, rec in enumerate(customer['recommendations'][:3], 1):
                print(f"   {i}. {rec['category']} (Confidence: {rec['confidence']:.2f})")
                print(f"      Reason: {rec['reason']}")
        
        # 5. Get RFM Segment Analysis
        print("\n4️⃣ Getting RFM Segment Analysis...")
        response = requests.get(
            f"{API_BASE_URL}/api/segments",
            params={"segment_type": "rfm"}
        )
        segments = response.json()
        
        print("\n📊 Top 3 Segments by Revenue:")
        for i, segment in enumerate(segments[:3], 1):
            print(f"   {i}. {segment['segment_name']}")
            print(f"      Customers: {segment['customer_count']:,}")
            print(f"      Total Revenue: ₦{segment['total_revenue']/1e9:.2f}B")
            print(f"      Avg CLV: ₦{segment['avg_clv']:,.0f}")
        
        # 6. Get Churn Predictions
        print("\n5️⃣ Getting Critical Churn Predictions...")
        response = requests.get(
            f"{API_BASE_URL}/api/churn/predictions",
            params={"risk_level": "Critical", "limit": 5}
        )
        churn_predictions = response.json()
        
        print(f"\n🚨 Top 5 Critical Churn Risk Customers:")
        for i, pred in enumerate(churn_predictions[:5], 1):
            print(f"   {i}. {pred['customer_id']}")
            print(f"      Segment: {pred['rfm_segment']}")
            print(f"      Revenue: ₦{pred['monetary']:,.0f}")
            print(f"      Churn Probability: {pred['churn_probability']:.1%}")
        
        # 7. Get Revenue Trend
        print("\n6️⃣ Getting Revenue Trend...")
        response = requests.get(f"{API_BASE_URL}/api/analytics/revenue-trend")
        trend = response.json()
        
        print("\n📈 Recent Revenue Trend:")
        for month_data in trend['data'][-6:]:  # Last 6 months
            print(f"   {month_data['month']}: ₦{month_data['revenue']/1e6:.1f}M")
        
        # 8. Search Customers
        print("\n7️⃣ Searching Customers...")
        response = requests.get(
            f"{API_BASE_URL}/api/search/customers",
            params={"query": "CUS0001", "limit": 5}
        )
        search_results = response.json()
        
        print(f"\n🔍 Search Results (Found {search_results['total']}):")
        for customer in search_results['results'][:3]:
            print(f"   {customer['customer_id']} - {customer['rfm_segment']} "
                  f"(Risk: {customer['churn_risk_level']})")
        
        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print(f"\n📚 For more details, visit: {API_BASE_URL}/docs")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to API")
        print("Please make sure the API is running:")
        print("  cd backend")
        print("  python run.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()

