"""
Pydantic models for API request/response schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class BusinessMetrics(BaseModel):
    """High-level business metrics"""
    total_customers: int
    active_customers: int
    total_revenue: float
    predicted_clv: float
    churn_rate: float
    avg_clv: float
    high_value_customers: int
    at_risk_customers: int


class ProductRecommendation(BaseModel):
    """Single product recommendation"""
    category: str
    reason: str
    confidence: float


class CustomerProfile(BaseModel):
    """Detailed customer profile"""
    customer_id: str
    rfm_segment: str
    customer_type: str
    monetary: float
    frequency: float
    recency: float
    predicted_clv: float
    churn_probability: float
    churn_risk_level: str
    customer_priority: str
    rfm_score: int
    customer_value_score: float
    purchase_timing_status: str
    clv_category: str
    recommendations: List[Dict[str, Any]] = []


class CustomerSummary(BaseModel):
    """Summary customer information for lists"""
    customer_id: str
    rfm_segment: str
    monetary: float
    frequency: float
    recency: float
    predicted_clv: float
    churn_probability: float
    churn_risk_level: str
    customer_priority: str


class CustomerListResponse(BaseModel):
    """Paginated customer list response"""
    customers: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int


class CustomerSegmentSummary(BaseModel):
    """Summary statistics for a customer segment"""
    segment_name: str
    customer_count: int
    total_revenue: float
    avg_revenue: float
    avg_frequency: float
    avg_recency: float
    avg_clv: float
    avg_churn_probability: float


class ChurnPrediction(BaseModel):
    """Churn prediction for a customer"""
    customer_id: str
    churn_probability: float
    churn_risk_level: str
    rfm_segment: str
    monetary: float
    recency: float
    frequency: float


class CLVPrediction(BaseModel):
    """CLV prediction for a customer"""
    customer_id: str
    predicted_clv: float
    current_value: float
    clv_category: str
    rfm_segment: str
    churn_probability: float


class RecommendationResponse(BaseModel):
    """Product recommendations for a customer"""
    customer_id: str
    recommendations: List[Dict[str, Any]]
    total_recommendations: int


class AnalyticsData(BaseModel):
    """Generic analytics data structure"""
    data: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

