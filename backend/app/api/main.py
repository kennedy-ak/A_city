"""
AFRIMASH CUSTOMER INTELLIGENCE API
FastAPI Backend for React Frontend
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime
import pandas as pd
import numpy as np
from pathlib import Path

from .models import (
    CustomerProfile,
    CustomerSegmentSummary,
    RecommendationResponse,
    BusinessMetrics,
    ChurnPrediction,
    CLVPrediction,
    CustomerListResponse,
    AnalyticsData
)
from .data_loader import DataLoader
from .analytics import AnalyticsService
import logging

logger = logging.getLogger(__name__)
# Initialize FastAPI app
app = FastAPI(
    title="Afrimash Customer Intelligence API",
    description="AI/ML powered customer analytics and predictions",
    version="1.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React default ports
    allow_origins=["*"],  # React default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize data loader and analytics service
data_loader = DataLoader(f"{Path(__file__).parent.parent.parent.parent}/data/processed")
print(f"Data loader initialized with data directory: {data_loader.data_dir}")
analytics = AnalyticsService()


@app.on_event("startup")
async def startup_event():
    """Load data on startup"""
    try:
        data_loader.load_all_data()
        print("✅ Data loaded successfully")
    except Exception as e:
        print(f"⚠️ Error loading data: {e}")


@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "service": "Afrimash Customer Intelligence API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/metrics", response_model=BusinessMetrics)
async def get_business_metrics():
    """Get high-level business metrics"""
    try:
        rfm_data = data_loader.get_rfm_data()
        
        total_customers = len(rfm_data)
        active_customers = len(rfm_data[rfm_data['Recency'] <= 30])
        total_revenue = float(rfm_data['Monetary'].sum())
        predicted_clv = float(rfm_data['Predicted_CLV'].sum())
        churn_rate = float((rfm_data['Is_Churned'].sum() / len(rfm_data)) * 100)
        avg_clv = float(rfm_data['Predicted_CLV'].mean())
        high_value_customers = len(rfm_data[rfm_data['CLV_Category'] == 'Very High Value'])
        at_risk_customers = len(rfm_data[rfm_data['Churn_Risk_Level'].isin(['High', 'Critical'])])
        
        return BusinessMetrics(
            total_customers=total_customers,
            active_customers=active_customers,
            total_revenue=total_revenue,
            predicted_clv=predicted_clv,
            churn_rate=churn_rate,
            avg_clv=avg_clv,
            high_value_customers=high_value_customers,
            at_risk_customers=at_risk_customers
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/customers", response_model=CustomerListResponse)
async def get_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: Optional[str] = Query(None),
    segment: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None)
):
    """Get paginated customer list with optional filters"""
    try:
        rfm_data = data_loader.get_rfm_data()
        
        # Apply filters
        if segment:
            rfm_data = rfm_data[rfm_data['RFM_Segment'] == segment]
        if risk_level:
            rfm_data = rfm_data[rfm_data['Churn_Risk_Level'] == risk_level]
        
        # Sort
        if sort_by:
            ascending = False if sort_by in ['Monetary', 'Predicted_CLV', 'Frequency'] else True
            rfm_data = rfm_data.sort_values(sort_by, ascending=ascending)
        
        # Pagination
        total = len(rfm_data)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_data = rfm_data.iloc[start:end]
        
        customers = []
        for _, row in paginated_data.iterrows():
            customers.append({
                "customer_id": str(row['Customer_ID']),
                "rfm_segment": str(row['RFM_Segment']),
                "monetary": float(row['Monetary']),
                "frequency": float(row['Frequency']),
                "recency": float(row['Recency']),
                "predicted_clv": float(row['Predicted_CLV']),
                "churn_probability": float(row['Churn_Probability']),
                "churn_risk_level": str(row['Churn_Risk_Level']),
                "customer_priority": str(row['Customer_Priority'])
            })
        
        return CustomerListResponse(
            customers=customers,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/customers/{customer_id}", response_model=CustomerProfile)
async def get_customer_profile(customer_id: str):
    """Get detailed profile for a specific customer"""
    try:
        rfm_data = data_loader.get_rfm_data()
        customer = rfm_data[rfm_data['Customer_ID'] == customer_id]
        
        if customer.empty:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        customer = customer.iloc[0]
        
        # Get recommendations for this customer
        recommendations = data_loader.get_recommendations()
        customer_recs = recommendations[recommendations['Customer_ID'] == customer_id]
        
        rec_list = []
        for _, rec in customer_recs.iterrows():
            rec_list.append({
                "category": str(rec['Recommended_Category']),
                "reason": str(rec['Reason']),
                "confidence": float(rec['Confidence'])
            })
        
        return CustomerProfile(
            customer_id=str(customer['Customer_ID']),
            rfm_segment=str(customer['RFM_Segment']),
            customer_type=str(customer['Customer_Type']),
            monetary=float(customer['Monetary']),
            frequency=float(customer['Frequency']),
            recency=float(customer['Recency']),
            predicted_clv=float(customer['Predicted_CLV']),
            churn_probability=float(customer['Churn_Probability']),
            churn_risk_level=str(customer['Churn_Risk_Level']),
            customer_priority=str(customer['Customer_Priority']),
            rfm_score=int(customer['RFM_Score']),
            customer_value_score=float(customer['Customer_Value_Score']),
            purchase_timing_status=str(customer['Purchase_Timing_Status']),
            clv_category=str(customer['CLV_Category']),
            recommendations=rec_list
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/segments", response_model=List[CustomerSegmentSummary])
async def get_segment_analysis(segment_type: str = Query("rfm", regex="^(rfm|kmeans)$")):
    """Get customer segment analysis"""
    try:
        rfm_data = data_loader.get_rfm_data()
        
        segment_col = 'RFM_Segment' if segment_type == 'rfm' else 'Cluster_Name'
        
        segment_summary = rfm_data.groupby(segment_col).agg({
            'Customer_ID': 'count',
            'Monetary': ['sum', 'mean'],
            'Frequency': 'mean',
            'Recency': 'mean',
            'Predicted_CLV': 'mean',
            'Churn_Probability': 'mean'
        }).round(2)
        
        segments = []
        for segment_name in segment_summary.index:
            row = segment_summary.loc[segment_name]
            segments.append(CustomerSegmentSummary(
                segment_name=str(segment_name),
                customer_count=int(row[('Customer_ID', 'count')]),
                total_revenue=float(row[('Monetary', 'sum')]),
                avg_revenue=float(row[('Monetary', 'mean')]),
                avg_frequency=float(row[('Frequency', 'mean')]),
                avg_recency=float(row[('Recency', 'mean')]),
                avg_clv=float(row[('Predicted_CLV', 'mean')]),
                avg_churn_probability=float(row[('Churn_Probability', 'mean')])
            ))
        
        # Sort by total revenue descending
        segments.sort(key=lambda x: x.total_revenue, reverse=True)
        return segments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/churn/predictions", response_model=List[ChurnPrediction])
async def get_churn_predictions(
    risk_level: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get churn predictions with optional risk level filter"""
    try:
        rfm_data = data_loader.get_rfm_data()
        
        if risk_level:
            rfm_data = rfm_data[rfm_data['Churn_Risk_Level'] == risk_level]
        
        # Get top customers by monetary value
        rfm_data = rfm_data.nlargest(limit, 'Monetary')
        
        predictions = []
        for _, row in rfm_data.iterrows():
            predictions.append(ChurnPrediction(
                customer_id=str(row['Customer_ID']),
                churn_probability=float(row['Churn_Probability']),
                churn_risk_level=str(row['Churn_Risk_Level']),
                rfm_segment=str(row['RFM_Segment']),
                monetary=float(row['Monetary']),
                recency=float(row['Recency']),
                frequency=float(row['Frequency'])
            ))
        
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/clv/predictions", response_model=List[CLVPrediction])
async def get_clv_predictions(
    limit: int = Query(100, ge=1, le=1000),
    sort_by: str = Query("predicted_clv", regex="^(predicted_clv|monetary)$")
):
    """Get CLV predictions sorted by value"""
    try:
        rfm_data = data_loader.get_rfm_data()
        
        sort_column = 'Predicted_CLV' if sort_by == 'predicted_clv' else 'Monetary'
        rfm_data = rfm_data.nlargest(limit, sort_column)
        
        predictions = []
        for _, row in rfm_data.iterrows():
            predictions.append(CLVPrediction(
                customer_id=str(row['Customer_ID']),
                predicted_clv=float(row['Predicted_CLV']),
                current_value=float(row['Monetary']),
                clv_category=str(row['CLV_Category']),
                rfm_segment=str(row['RFM_Segment']),
                churn_probability=float(row['Churn_Probability'])
            ))
        
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recommendations/{customer_id}", response_model=RecommendationResponse)
async def get_customer_recommendations(customer_id: str):
    """Get product recommendations for a specific customer"""
    try:
        recommendations = data_loader.get_recommendations()
        customer_recs = recommendations[recommendations['Customer_ID'] == customer_id]
        
        if customer_recs.empty:
            raise HTTPException(status_code=404, detail="No recommendations found for this customer")
        
        rec_list = []
        for _, rec in customer_recs.iterrows():
            rec_list.append({
                "category": str(rec['Recommended_Category']),
                "reason": str(rec['Reason']),
                "confidence": float(rec['Confidence'])
            })
        
        return RecommendationResponse(
            customer_id=customer_id,
            recommendations=rec_list,
            total_recommendations=len(rec_list)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/revenue-trend")
async def get_revenue_trend():
    """Get monthly revenue trend data"""
    try:
        transactions = data_loader.get_transactions()
        
        monthly_rev = transactions.groupby(
            transactions['Date'].dt.to_period('M')
        )['Revenue'].sum()
        
        data = []
        for period, revenue in monthly_rev.items():
            data.append({
                "month": period.to_timestamp().strftime('%Y-%m'),
                "revenue": float(revenue)
            })
        
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/segment-distribution")
async def get_segment_distribution():
    """Get customer count by segment"""
    try:
        rfm_data = data_loader.get_rfm_data()
        segment_counts = rfm_data['RFM_Segment'].value_counts()
        
        data = []
        for segment, count in segment_counts.items():
            data.append({
                "segment": str(segment),
                "count": int(count)
            })
        
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/risk-distribution")
async def get_risk_distribution():
    """Get customer count by churn risk level"""
    try:
        rfm_data = data_loader.get_rfm_data()
        risk_counts = rfm_data['Churn_Risk_Level'].value_counts()
        
        data = []
        for risk, count in risk_counts.items():
            data.append({
                "risk_level": str(risk),
                "count": int(count)
            })
        
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/revenue-by-segment")
async def get_revenue_by_segment():
    """Get revenue distribution by customer segment"""
    try:
        rfm_data = data_loader.get_rfm_data()
        segment_revenue = rfm_data.groupby('RFM_Segment')['Monetary'].sum()
        
        data = []
        for segment, revenue in segment_revenue.items():
            data.append({
                "segment": str(segment),
                "revenue": float(revenue)
            })
        
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/clv-distribution")
async def get_clv_distribution():
    """Get CLV distribution data for histogram"""
    try:
        rfm_data = data_loader.get_rfm_data()
        clv_data = rfm_data[rfm_data['Predicted_CLV'] > 0]['Predicted_CLV']
        
        # Create histogram bins
        hist, bin_edges = np.histogram(np.log10(clv_data), bins=50)
        
        data = []
        for i in range(len(hist)):
            data.append({
                "bin_start": float(10 ** bin_edges[i]),
                "bin_end": float(10 ** bin_edges[i + 1]),
                "count": int(hist[i])
            })
        
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search/customers")
async def search_customers(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50)
):
    """Search customers by ID or other criteria"""
    try:
        rfm_data = data_loader.get_rfm_data()
        
        # Search by customer ID
        results = rfm_data[rfm_data['Customer_ID'].str.contains(query, case=False, na=False)]
        results = results.head(limit)
        
        customers = []
        for _, row in results.iterrows():
            customers.append({
                "customer_id": str(row['Customer_ID']),
                "rfm_segment": str(row['RFM_Segment']),
                "monetary": float(row['Monetary']),
                "churn_risk_level": str(row['Churn_Risk_Level'])
            })
        
        return {"results": customers, "total": len(customers)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

