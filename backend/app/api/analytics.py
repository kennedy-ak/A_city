"""
Analytics service for processing and analyzing customer data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta


class AnalyticsService:
    """Service for customer analytics and insights"""
    
    @staticmethod
    def calculate_segment_metrics(rfm_data: pd.DataFrame, segment_column: str = 'RFM_Segment') -> pd.DataFrame:
        """
        Calculate comprehensive metrics for each segment
        
        Args:
            rfm_data: Customer RFM DataFrame
            segment_column: Column to segment by (RFM_Segment or Cluster_Name)
        
        Returns:
            DataFrame with segment metrics
        """
        metrics = rfm_data.groupby(segment_column).agg({
            'Customer_ID': 'count',
            'Monetary': ['sum', 'mean', 'median'],
            'Frequency': ['mean', 'median'],
            'Recency': ['mean', 'median'],
            'Predicted_CLV': ['sum', 'mean', 'median'],
            'Churn_Probability': ['mean', 'median'],
            'Customer_Value_Score': 'mean'
        }).round(2)
        
        return metrics
    
    @staticmethod
    def get_churn_risk_summary(rfm_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Get summary of churn risk across customer base
        
        Args:
            rfm_data: Customer RFM DataFrame
        
        Returns:
            Dictionary with churn risk summary
        """
        risk_counts = rfm_data['Churn_Risk_Level'].value_counts().to_dict()
        
        high_risk = rfm_data[rfm_data['Churn_Risk_Level'].isin(['High', 'Critical'])]
        revenue_at_risk = high_risk['Monetary'].sum()
        
        return {
            'risk_distribution': risk_counts,
            'total_high_risk': len(high_risk),
            'revenue_at_risk': float(revenue_at_risk),
            'percent_at_risk': float((len(high_risk) / len(rfm_data)) * 100)
        }
    
    @staticmethod
    def get_clv_insights(rfm_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Get insights about customer lifetime value
        
        Args:
            rfm_data: Customer RFM DataFrame
        
        Returns:
            Dictionary with CLV insights
        """
        return {
            'total_predicted_clv': float(rfm_data['Predicted_CLV'].sum()),
            'average_clv': float(rfm_data['Predicted_CLV'].mean()),
            'median_clv': float(rfm_data['Predicted_CLV'].median()),
            'clv_std': float(rfm_data['Predicted_CLV'].std()),
            'high_value_count': int((rfm_data['CLV_Category'] == 'Very High Value').sum()),
            'clv_by_segment': rfm_data.groupby('RFM_Segment')['Predicted_CLV'].mean().to_dict()
        }
    
    @staticmethod
    def get_revenue_trends(transactions: pd.DataFrame, period: str = 'M') -> pd.DataFrame:
        """
        Calculate revenue trends over time
        
        Args:
            transactions: Transaction DataFrame
            period: Pandas period string ('D', 'W', 'M', 'Q', 'Y')
        
        Returns:
            DataFrame with revenue trends
        """
        trends = transactions.groupby(transactions['Date'].dt.to_period(period)).agg({
            'Revenue': ['sum', 'mean', 'count'],
            'Customer_ID': 'nunique'
        })
        
        trends.columns = ['total_revenue', 'avg_transaction', 'transaction_count', 'unique_customers']
        trends.index = trends.index.to_timestamp()
        
        return trends
    
    @staticmethod
    def get_top_categories(transactions: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """
        Get top product categories by revenue
        
        Args:
            transactions: Transaction DataFrame
            top_n: Number of top categories to return
        
        Returns:
            DataFrame with top categories
        """
        if 'Category' not in transactions.columns:
            return pd.DataFrame()
        
        category_metrics = transactions.groupby('Category').agg({
            'Revenue': ['sum', 'count'],
            'Customer_ID': 'nunique'
        }).sort_values(('Revenue', 'sum'), ascending=False).head(top_n)
        
        category_metrics.columns = ['total_revenue', 'transaction_count', 'unique_customers']
        
        return category_metrics
    
    @staticmethod
    def calculate_customer_cohorts(transactions: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate customer cohorts based on first purchase date
        
        Args:
            transactions: Transaction DataFrame
        
        Returns:
            DataFrame with cohort analysis
        """
        # Get first purchase date for each customer
        first_purchase = transactions.groupby('Customer_ID')['Date'].min().reset_index()
        first_purchase.columns = ['Customer_ID', 'cohort_date']
        first_purchase['cohort'] = first_purchase['cohort_date'].dt.to_period('M')
        
        # Merge back with transactions
        transactions_with_cohort = transactions.merge(first_purchase[['Customer_ID', 'cohort']], on='Customer_ID')
        
        # Calculate cohort metrics
        cohort_data = transactions_with_cohort.groupby('cohort').agg({
            'Customer_ID': 'nunique',
            'Revenue': 'sum'
        })
        
        return cohort_data
    
    @staticmethod
    def get_purchase_patterns(rfm_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze purchase patterns across customer base
        
        Args:
            rfm_data: Customer RFM DataFrame
        
        Returns:
            Dictionary with purchase pattern insights
        """
        timing_status = rfm_data['Purchase_Timing_Status'].value_counts().to_dict()
        
        return {
            'timing_distribution': timing_status,
            'avg_frequency': float(rfm_data['Frequency'].mean()),
            'avg_recency': float(rfm_data['Recency'].mean()),
            'one_time_buyers': int((rfm_data['Frequency'] == 1).sum()),
            'repeat_customers': int((rfm_data['Frequency'] > 1).sum()),
            'highly_active': int((rfm_data['Frequency'] >= 5).sum())
        }
    
    @staticmethod
    def get_recommendation_summary(recommendations: pd.DataFrame) -> Dict[str, Any]:
        """
        Get summary statistics for recommendations
        
        Args:
            recommendations: Product recommendations DataFrame
        
        Returns:
            Dictionary with recommendation summary
        """
        return {
            'total_recommendations': len(recommendations),
            'unique_customers': int(recommendations['Customer_ID'].nunique()),
            'avg_confidence': float(recommendations['Confidence'].mean()),
            'high_confidence_count': int((recommendations['Confidence'] > 0.7).sum()),
            'top_categories': recommendations['Recommended_Category'].value_counts().head(10).to_dict(),
            'recommendation_methods': recommendations['Reason'].value_counts().to_dict()
        }
    
    @staticmethod
    def identify_cross_sell_opportunities(rfm_data: pd.DataFrame, 
                                         recommendations: pd.DataFrame,
                                         min_confidence: float = 0.6) -> pd.DataFrame:
        """
        Identify high-value cross-sell opportunities
        
        Args:
            rfm_data: Customer RFM DataFrame
            recommendations: Product recommendations DataFrame
            min_confidence: Minimum confidence threshold
        
        Returns:
            DataFrame with cross-sell opportunities
        """
        # Filter high-confidence recommendations
        high_conf_recs = recommendations[recommendations['Confidence'] >= min_confidence]
        
        # Merge with customer data
        opportunities = high_conf_recs.merge(
            rfm_data[['Customer_ID', 'Monetary', 'Predicted_CLV', 'RFM_Segment', 'Churn_Risk_Level']],
            on='Customer_ID',
            how='left'
        )
        
        # Sort by potential value
        opportunities = opportunities.sort_values('Predicted_CLV', ascending=False)
        
        return opportunities
    
    @staticmethod
    def calculate_business_health_score(rfm_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate overall business health metrics
        
        Args:
            rfm_data: Customer RFM DataFrame
        
        Returns:
            Dictionary with health score and metrics
        """
        # Calculate component scores (0-100)
        active_rate = (rfm_data['Recency'] <= 90).sum() / len(rfm_data) * 100
        retention_rate = 100 - ((rfm_data['Is_Churned'].sum() / len(rfm_data)) * 100)
        repeat_rate = (rfm_data['Frequency'] > 1).sum() / len(rfm_data) * 100
        high_value_rate = (rfm_data['CLV_Category'].isin(['High Value', 'Very High Value'])).sum() / len(rfm_data) * 100
        
        # Overall health score (weighted average)
        health_score = (
            active_rate * 0.25 +
            retention_rate * 0.35 +
            repeat_rate * 0.25 +
            high_value_rate * 0.15
        )
        
        return {
            'overall_health_score': float(health_score),
            'active_customer_rate': float(active_rate),
            'retention_rate': float(retention_rate),
            'repeat_purchase_rate': float(repeat_rate),
            'high_value_rate': float(high_value_rate),
            'health_status': 'Good' if health_score >= 70 else 'Fair' if health_score >= 50 else 'Poor'
        }

