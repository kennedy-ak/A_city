"""
Simple API test script to verify all endpoints are working
"""

import requests
import sys
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"


def test_endpoint(endpoint: str, description: str) -> bool:
    """Test a single endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
        if response.status_code == 200:
            print(f"✅ {description}")
            return True
        else:
            print(f"❌ {description} - Status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {description} - Connection refused. Is the API running?")
        return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False


def main():
    """Run all API tests"""
    print("🧪 Testing Afrimash Customer Intelligence API\n")
    print(f"API URL: {API_BASE_URL}\n")
    
    tests = [
        ("/", "Health Check"),
        ("/api/metrics", "Business Metrics"),
        ("/api/customers?page=1&page_size=5", "Customer List"),
        ("/api/customers/CUS000001", "Customer Profile"),
        ("/api/segments?segment_type=rfm", "RFM Segments"),
        ("/api/churn/predictions?limit=10", "Churn Predictions"),
        ("/api/clv/predictions?limit=10", "CLV Predictions"),
        ("/api/recommendations/CUS000001", "Product Recommendations"),
        ("/api/analytics/revenue-trend", "Revenue Trend"),
        ("/api/analytics/segment-distribution", "Segment Distribution"),
        ("/api/analytics/risk-distribution", "Risk Distribution"),
        ("/api/analytics/revenue-by-segment", "Revenue by Segment"),
        ("/api/search/customers?query=CUS000001", "Customer Search"),
    ]
    
    results = []
    for endpoint, description in tests:
        results.append(test_endpoint(endpoint, description))
    
    # Summary
    print("\n" + "="*50)
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
        print(f"\n📚 View interactive docs at: {API_BASE_URL}/docs")
        return 0
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        print("\nTroubleshooting:")
        print("1. Make sure the API is running: python run.py")
        print("2. Verify CSV files are in the project root")
        print("3. Check for any error messages in the API console")
        return 1


if __name__ == "__main__":
    sys.exit(main())

