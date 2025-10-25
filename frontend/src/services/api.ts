import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Types
export interface BusinessMetrics {
  total_customers: number;
  active_customers: number;
  total_revenue: number;
  predicted_clv: number;
  churn_rate: number;
  avg_clv: number;
  high_value_customers: number;
  at_risk_customers: number;
}

export interface RevenueDataPoint {
  month: string;
  revenue: number;
}

export interface SegmentDataPoint {
  segment: string;
  count: number;
}

export interface RiskDataPoint {
  risk_level: string;
  count: number;
}

export interface RevenueBySegmentDataPoint {
  segment: string;
  revenue: number;
}

export interface CustomerSegmentSummary {
  segment_name: string;
  customer_count: number;
  total_revenue: number;
  avg_revenue: number;
  avg_frequency: number;
  avg_recency: number;
  avg_clv: number;
  avg_churn_probability: number;
}

export interface ChurnPrediction {
  customer_id: string;
  churn_probability: number;
  churn_risk_level: string;
  rfm_segment: string;
  monetary: number;
  recency: number;
  frequency: number;
}

export interface CLVPrediction {
  customer_id: string;
  predicted_clv: number;
  current_value: number;
  clv_category: string;
  rfm_segment: string;
  churn_probability: number;
}

export interface RecommendationItem {
  category: string;
  reason: string;
  confidence: number;
}

export interface RecommendationResponse {
  customer_id: string;
  recommendations: RecommendationItem[];
  total_recommendations: number;
}

export interface CustomerListResponse {
  customers: any[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// API Services
export const metricsService = {
  getBusinessMetrics: () => apiClient.get<BusinessMetrics>('/api/metrics'),
};

export const analyticsService = {
  getRevenueTrend: () => apiClient.get<{ data: RevenueDataPoint[] }>('/api/analytics/revenue-trend'),
  getSegmentDistribution: () => apiClient.get<{ data: SegmentDataPoint[] }>('/api/analytics/segment-distribution'),
  getRiskDistribution: () => apiClient.get<{ data: RiskDataPoint[] }>('/api/analytics/risk-distribution'),
  getRevenueBySegment: () => apiClient.get<{ data: RevenueBySegmentDataPoint[] }>('/api/analytics/revenue-by-segment'),
};

export const customerService = {
  getCustomers: (params: any) => apiClient.get('/api/customers', { params }),
  getCustomerProfile: (customerId: string) => apiClient.get(`/api/customers/${customerId}`),
  searchCustomers: (query: string) => apiClient.get('/api/search/customers', { params: { query } }),
};

export const segmentService = {
  getSegments: (segmentType: 'rfm' | 'kmeans' = 'rfm') => 
    apiClient.get('/api/segments', { params: { segment_type: segmentType } }),
};

export const predictionService = {
  getChurnPredictions: (params: any) => apiClient.get('/api/churn/predictions', { params }),
  getCLVPredictions: (params: any) => apiClient.get('/api/clv/predictions', { params }),
};

export const recommendationService = {
  getRecommendations: (customerId: string) => 
    apiClient.get(`/api/recommendations/${customerId}`),
};

