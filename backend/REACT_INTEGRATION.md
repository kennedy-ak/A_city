# React Frontend Integration Guide

This guide shows how to integrate the Afrimash Customer Intelligence API with a React frontend.

## Installation

### 1. Create React App (or use existing project)

```bash
npx create-react-app afrimash-frontend
cd afrimash-frontend
npm install axios react-router-dom @tanstack/react-query
npm install recharts  # For charts
npm install @headlessui/react @heroicons/react  # For UI components (optional)
```

### 2. Or with Vite (recommended for faster development)

```bash
npm create vite@latest afrimash-frontend -- --template react
cd afrimash-frontend
npm install
npm install axios react-router-dom @tanstack/react-query recharts
```

## API Client Setup

Create an API client to interact with the backend:

### `src/api/client.js`

```javascript
import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error);
    return Promise.reject(error);
  }
);

export default apiClient;
```

### `src/api/services.js`

```javascript
import apiClient from "./client";

export const metricsService = {
  getBusinessMetrics: () => apiClient.get("/api/metrics"),
};

export const customerService = {
  getCustomers: (params) => apiClient.get("/api/customers", { params }),
  getCustomerProfile: (customerId) =>
    apiClient.get(`/api/customers/${customerId}`),
  searchCustomers: (query) =>
    apiClient.get("/api/search/customers", { params: { query } }),
};

export const segmentService = {
  getSegments: (segmentType = "rfm") =>
    apiClient.get("/api/segments", { params: { segment_type: segmentType } }),
};

export const predictionService = {
  getChurnPredictions: (params) =>
    apiClient.get("/api/churn/predictions", { params }),
  getCLVPredictions: (params) =>
    apiClient.get("/api/clv/predictions", { params }),
};

export const recommendationService = {
  getRecommendations: (customerId) =>
    apiClient.get(`/api/recommendations/${customerId}`),
};

export const analyticsService = {
  getRevenueTrend: () => apiClient.get("/api/analytics/revenue-trend"),
  getSegmentDistribution: () =>
    apiClient.get("/api/analytics/segment-distribution"),
  getRiskDistribution: () => apiClient.get("/api/analytics/risk-distribution"),
  getRevenueBySegment: () => apiClient.get("/api/analytics/revenue-by-segment"),
  getCLVDistribution: () => apiClient.get("/api/analytics/clv-distribution"),
};
```

## React Query Setup

### `src/App.js`

```javascript
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import CustomerProfile from "./pages/CustomerProfile";
import Customers from "./pages/Customers";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/customers" element={<Customers />} />
          <Route path="/customers/:customerId" element={<CustomerProfile />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
```

## Example Components

### Dashboard Component

```javascript
// src/pages/Dashboard.js
import { useQuery } from "@tanstack/react-query";
import { metricsService, analyticsService } from "../api/services";

function Dashboard() {
  const { data: metrics, isLoading: metricsLoading } = useQuery({
    queryKey: ["metrics"],
    queryFn: () => metricsService.getBusinessMetrics().then((res) => res.data),
  });

  const { data: segmentData } = useQuery({
    queryKey: ["segment-distribution"],
    queryFn: () =>
      analyticsService.getSegmentDistribution().then((res) => res.data),
  });

  if (metricsLoading) return <div>Loading...</div>;

  return (
    <div className="dashboard">
      <h1>Afrimash Customer Intelligence</h1>

      {/* Key Metrics */}
      <div className="metrics-grid">
        <MetricCard
          title="Total Customers"
          value={metrics.total_customers.toLocaleString()}
        />
        <MetricCard
          title="Total Revenue"
          value={`₦${(metrics.total_revenue / 1e9).toFixed(2)}B`}
        />
        <MetricCard
          title="Churn Rate"
          value={`${metrics.churn_rate.toFixed(1)}%`}
        />
        <MetricCard
          title="At Risk"
          value={metrics.at_risk_customers.toLocaleString()}
        />
      </div>

      {/* Charts */}
      <div className="charts">
        {segmentData && <SegmentChart data={segmentData.data} />}
      </div>
    </div>
  );
}

function MetricCard({ title, value }) {
  return (
    <div className="metric-card">
      <h3>{title}</h3>
      <p className="metric-value">{value}</p>
    </div>
  );
}

export default Dashboard;
```

### Customer List Component

```javascript
// src/pages/Customers.js
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { customerService } from "../api/services";
import { Link } from "react-router-dom";

function Customers() {
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({
    segment: "",
    risk_level: "",
  });

  const { data, isLoading } = useQuery({
    queryKey: ["customers", page, filters],
    queryFn: () =>
      customerService
        .getCustomers({
          page,
          page_size: 20,
          ...filters,
        })
        .then((res) => res.data),
  });

  if (isLoading) return <div>Loading customers...</div>;

  return (
    <div className="customers-page">
      <h1>Customers</h1>

      {/* Filters */}
      <div className="filters">
        <select
          value={filters.segment}
          onChange={(e) => setFilters({ ...filters, segment: e.target.value })}
        >
          <option value="">All Segments</option>
          <option value="Champions">Champions</option>
          <option value="Loyal">Loyal</option>
          {/* Add more segments */}
        </select>

        <select
          value={filters.risk_level}
          onChange={(e) =>
            setFilters({ ...filters, risk_level: e.target.value })
          }
        >
          <option value="">All Risk Levels</option>
          <option value="Low">Low</option>
          <option value="Medium">Medium</option>
          <option value="High">High</option>
          <option value="Critical">Critical</option>
        </select>
      </div>

      {/* Customer Table */}
      <table className="customer-table">
        <thead>
          <tr>
            <th>Customer ID</th>
            <th>Segment</th>
            <th>Revenue</th>
            <th>CLV</th>
            <th>Churn Risk</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {data?.customers.map((customer) => (
            <tr key={customer.customer_id}>
              <td>{customer.customer_id}</td>
              <td>{customer.rfm_segment}</td>
              <td>₦{customer.monetary.toLocaleString()}</td>
              <td>₦{customer.predicted_clv.toLocaleString()}</td>
              <td>
                <span
                  className={`risk-badge ${customer.churn_risk_level.toLowerCase()}`}
                >
                  {customer.churn_risk_level}
                </span>
              </td>
              <td>
                <Link to={`/customers/${customer.customer_id}`}>
                  View Profile
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Pagination */}
      <div className="pagination">
        <button
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page === 1}
        >
          Previous
        </button>
        <span>
          Page {page} of {data?.total_pages}
        </span>
        <button
          onClick={() => setPage((p) => p + 1)}
          disabled={page === data?.total_pages}
        >
          Next
        </button>
      </div>
    </div>
  );
}

export default Customers;
```

### Customer Profile Component

```javascript
// src/pages/CustomerProfile.js
import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { customerService, recommendationService } from "../api/services";

function CustomerProfile() {
  const { customerId } = useParams();

  const { data: customer, isLoading } = useQuery({
    queryKey: ["customer", customerId],
    queryFn: () =>
      customerService.getCustomerProfile(customerId).then((res) => res.data),
  });

  if (isLoading) return <div>Loading profile...</div>;
  if (!customer) return <div>Customer not found</div>;

  return (
    <div className="customer-profile">
      <h1>Customer Profile: {customer.customer_id}</h1>

      {/* Overview */}
      <div className="profile-overview">
        <div className="info-section">
          <h2>Basic Information</h2>
          <p>
            <strong>Segment:</strong> {customer.rfm_segment}
          </p>
          <p>
            <strong>Customer Type:</strong> {customer.customer_type}
          </p>
          <p>
            <strong>Priority:</strong> {customer.customer_priority}
          </p>
        </div>

        <div className="info-section">
          <h2>Financial Metrics</h2>
          <p>
            <strong>Total Spent:</strong> ₦{customer.monetary.toLocaleString()}
          </p>
          <p>
            <strong>Predicted CLV:</strong> ₦
            {customer.predicted_clv.toLocaleString()}
          </p>
          <p>
            <strong>Value Score:</strong>{" "}
            {customer.customer_value_score.toFixed(1)}
          </p>
        </div>

        <div className="info-section">
          <h2>Behavior</h2>
          <p>
            <strong>Frequency:</strong> {customer.frequency} purchases
          </p>
          <p>
            <strong>Recency:</strong> {customer.recency} days ago
          </p>
          <p>
            <strong>RFM Score:</strong> {customer.rfm_score}/15
          </p>
        </div>

        <div className="info-section">
          <h2>Risk Assessment</h2>
          <p>
            <strong>Churn Probability:</strong>{" "}
            {(customer.churn_probability * 100).toFixed(1)}%
          </p>
          <p>
            <strong>Risk Level:</strong>
            <span
              className={`risk-badge ${customer.churn_risk_level.toLowerCase()}`}
            >
              {customer.churn_risk_level}
            </span>
          </p>
        </div>
      </div>

      {/* Recommendations */}
      {customer.recommendations && customer.recommendations.length > 0 && (
        <div className="recommendations-section">
          <h2>Product Recommendations</h2>
          <div className="recommendations-grid">
            {customer.recommendations.map((rec, idx) => (
              <div key={idx} className="recommendation-card">
                <h3>{rec.category}</h3>
                <p>{rec.reason}</p>
                <p>
                  <strong>Confidence:</strong>{" "}
                  {(rec.confidence * 100).toFixed(0)}%
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action Items */}
      {customer.churn_risk_level === "Critical" && (
        <div className="alert alert-danger">
          <strong>⚠️ URGENT:</strong> Customer at critical churn risk. Immediate
          intervention needed!
        </div>
      )}
    </div>
  );
}

export default CustomerProfile;
```

## Environment Variables

Create `.env` file in your React project root:

```env
REACT_APP_API_URL=http://localhost:8000
```

For production:

```env
REACT_APP_API_URL=https://api.afrimash.com
```

## Styling

Add basic styles in `src/App.css`:

```css
.dashboard {
  padding: 2rem;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin: 2rem 0;
}

.metric-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.metric-value {
  font-size: 2rem;
  font-weight: bold;
  color: #2e86ab;
}

.risk-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
}

.risk-badge.low {
  background: #d4edda;
  color: #155724;
}
.risk-badge.medium {
  background: #fff3cd;
  color: #856404;
}
.risk-badge.high {
  background: #f8d7da;
  color: #721c24;
}
.risk-badge.critical {
  background: #dc3545;
  color: white;
}

.customer-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.customer-table th,
.customer-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.customer-table th {
  background: #f8f9fa;
  font-weight: 600;
}

.alert {
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
}

.alert-danger {
  background: #f8d7da;
  border-left: 4px solid #dc3545;
  color: #721c24;
}
```

## Running the Application

1. Start the backend API:

```bash
cd backend
python run.py
```

2. Start the React frontend:

```bash
cd afrimash-frontend
npm start
```

Your app should now be running at http://localhost:3000 and communicating with the API at http://localhost:8000!

## TypeScript Version

If you prefer TypeScript, create type definitions:

```typescript
// src/types/api.ts
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

export interface Customer {
  customer_id: string;
  rfm_segment: string;
  monetary: number;
  frequency: number;
  recency: number;
  predicted_clv: number;
  churn_probability: number;
  churn_risk_level: string;
  customer_priority: string;
}

// Add more types as needed
```

## Next Steps

1. Add authentication if needed
2. Implement real-time updates with WebSockets
3. Add data visualization with Recharts or Chart.js
4. Implement error boundaries
5. Add loading states and skeletons
6. Add unit tests with Jest and React Testing Library

Happy coding! 🚀
