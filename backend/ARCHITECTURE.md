# Backend Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         REACT FRONTEND                          │
│                    (or any frontend framework)                  │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Dashboard │  │Customers │  │ Analytics│  │ Profiles │      │
│  │Component │  │   List   │  │  Charts  │  │  Detail  │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼─────────────┼─────────────┼─────────────┼─────────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                      │
                      │ HTTP/REST API
                      │ (JSON)
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                        FASTAPI BACKEND                          │
│                     http://localhost:8000                       │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API ENDPOINTS (main.py)                │  │
│  │                                                           │  │
│  │  GET /api/metrics              → Business Metrics        │  │
│  │  GET /api/customers            → Customer List           │  │
│  │  GET /api/customers/{id}       → Customer Profile        │  │
│  │  GET /api/segments             → Segment Analysis        │  │
│  │  GET /api/churn/predictions    → Churn Predictions       │  │
│  │  GET /api/clv/predictions      → CLV Predictions          │  │
│  │  GET /api/recommendations/{id} → Product Recommendations │  │
│  │  GET /api/analytics/*          → Analytics Data          │  │
│  │  GET /api/search/customers     → Customer Search         │  │
│  └───────────┬──────────────────────────────────────────────┘  │
│              │                                                  │
│              ▼                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              DATA LAYER (data_loader.py)                  │  │
│  │                                                           │  │
│  │  - Data Caching                                          │  │
│  │  - CSV File Loading                                      │  │
│  │  - Data Validation                                       │  │
│  └───────────┬──────────────────────────────────────────────┘  │
│              │                                                  │
│              ▼                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            ANALYTICS SERVICE (analytics.py)               │  │
│  │                                                           │  │
│  │  - Segment Metrics Calculation                           │  │
│  │  - Churn Risk Analysis                                   │  │
│  │  - CLV Insights                                          │  │
│  │  - Revenue Trends                                        │  │
│  │  - Business Health Score                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                            │
│                                                                 │
│  📄 rfm_with_predictions.csv    (Customer data with ML models) │
│  📄 transactions_clean.csv      (Transaction history)          │
│  📄 product_recommendations.csv (Recommendation engine output)  │
└─────────────────────────────────────────────────────────────────┘
```

## Request Flow

### Example: Get Customer Profile

```
1. User clicks on customer in React app
   ↓
2. React makes GET request:
   fetch('http://localhost:8000/api/customers/CUS000001')
   ↓
3. FastAPI receives request at endpoint
   @app.get("/api/customers/{customer_id}")
   ↓
4. DataLoader retrieves customer from cached DataFrame
   rfm_data = data_loader.get_rfm_data()
   customer = rfm_data[rfm_data['Customer_ID'] == customer_id]
   ↓
5. Get recommendations for customer
   recommendations = data_loader.get_recommendations()
   ↓
6. Build CustomerProfile response model
   CustomerProfile(
     customer_id="CUS000001",
     rfm_segment="Champions",
     ...
   )
   ↓
7. Pydantic validates and serializes to JSON
   ↓
8. FastAPI returns JSON response with CORS headers
   ↓
9. React receives and displays customer data
```

## Component Architecture

### 1. API Layer (`main.py`)

**Responsibilities:**

- Route definitions and request handling
- Request parameter validation
- Response formatting
- Error handling
- CORS configuration

**Key Features:**

- 15+ REST endpoints
- Automatic OpenAPI documentation
- Type-safe request/response handling
- Pagination support
- Query parameter filtering

### 2. Data Models (`models.py`)

**Responsibilities:**

- Define request/response schemas
- Data validation
- Type checking
- Documentation generation

**Key Models:**

- `BusinessMetrics` - KPIs and metrics
- `CustomerProfile` - Complete customer data
- `CustomerSegmentSummary` - Segment statistics
- `ChurnPrediction` - Churn risk data
- `CLVPrediction` - Lifetime value data
- `RecommendationResponse` - Product recommendations

### 3. Data Loader (`data_loader.py`)

**Responsibilities:**

- Load CSV files from disk
- Cache data in memory
- Provide data access methods
- Handle file errors

**Key Features:**

- Lazy loading (load on first access)
- In-memory caching for performance
- Automatic date parsing
- Error handling and logging

**Methods:**

```python
get_rfm_data() → pd.DataFrame
get_transactions() → pd.DataFrame
get_recommendations() → pd.DataFrame
get_customer(customer_id) → pd.Series
get_high_risk_customers(n) → pd.DataFrame
get_high_value_customers(n) → pd.DataFrame
```

### 4. Analytics Service (`analytics.py`)

**Responsibilities:**

- Complex data analysis
- Metric calculations
- Statistical computations
- Business intelligence

**Key Methods:**

```python
calculate_segment_metrics(rfm_data)
get_churn_risk_summary(rfm_data)
get_clv_insights(rfm_data)
get_revenue_trends(transactions)
calculate_business_health_score(rfm_data)
identify_cross_sell_opportunities(rfm_data, recommendations)
```

## Data Flow

### Startup Sequence

```
1. FastAPI application starts
   ↓
2. @app.on_event("startup") triggered
   ↓
3. DataLoader initialized
   ↓
4. All CSV files loaded into memory
   ↓
5. Data cached in DataLoader instance
   ↓
6. API ready to handle requests
```

### Request Handling

```
HTTP Request
   ↓
FastAPI Route Handler
   ↓
Parameter Validation (Pydantic)
   ↓
Data Access (DataLoader)
   ↓
Business Logic (Analytics Service - if needed)
   ↓
Response Model Creation
   ↓
JSON Serialization (Pydantic)
   ↓
HTTP Response with CORS headers
```

## Performance Optimization

### Caching Strategy

```python
class DataLoader:
    _rfm_data = None        # Cached in memory
    _transactions = None    # Cached in memory
    _recommendations = None # Cached in memory

    def get_rfm_data(self):
        if self._rfm_data is None:
            self._rfm_data = pd.read_csv('rfm_with_predictions.csv')
        return self._rfm_data  # Return cached data
```

**Benefits:**

- CSV files read only once at startup
- Subsequent requests use cached DataFrames
- Response time < 100ms for most endpoints
- No database overhead

### Pagination

```python
# Efficient pagination without loading all data
start = (page - 1) * page_size
end = start + page_size
paginated_data = rfm_data.iloc[start:end]
```

## Error Handling

### Exception Hierarchy

```
Exception
└── HTTPException (FastAPI)
    ├── 404 Not Found (Customer/Resource not found)
    ├── 500 Internal Server Error (Data loading errors)
    └── 422 Validation Error (Invalid parameters)
```

### Error Response Format

```json
{
  "detail": "Customer not found",
  "timestamp": "2025-10-25T12:00:00"
}
```

## CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React (CRA)
        "http://localhost:5173",  # React (Vite)
    ],
    allow_credentials=True,
    allow_methods=["*"],        # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],        # Accept, Content-Type, etc.
)
```

## Scalability Considerations

### Current Architecture (Single Instance)

- ✅ Fast (< 100ms response time)
- ✅ Simple deployment
- ✅ Good for < 1000 concurrent users
- ⚠️ Data loaded in memory (~200MB)
- ⚠️ No horizontal scaling

### For Production Scale

1. **Add Database**: Move from CSV to PostgreSQL/MongoDB
2. **Add Redis**: Cache frequently accessed data
3. **Load Balancer**: Distribute across multiple instances
4. **CDN**: Cache API responses at edge
5. **API Gateway**: Rate limiting and authentication

### Example Production Architecture

```
                   ┌─────────┐
                   │   CDN   │
                   └────┬────┘
                        │
                   ┌────▼────────┐
                   │ API Gateway │
                   └────┬────────┘
                        │
              ┌─────────┴──────────┐
              │   Load Balancer    │
              └──┬─────────┬───────┘
                 │         │
         ┌───────▼───┐ ┌──▼────────┐
         │ FastAPI 1 │ │ FastAPI 2 │
         └─────┬─────┘ └─────┬─────┘
               │             │
         ┌─────┴─────────────┴─────┐
         │                          │
    ┌────▼──────┐           ┌──────▼───┐
    │ PostgreSQL│           │  Redis   │
    │ Database  │           │  Cache   │
    └───────────┘           └──────────┘
```

## Security Architecture

### Current (Development)

- ✅ CORS protection
- ✅ Input validation (Pydantic)
- ✅ Type safety
- ⚠️ No authentication

### Production Recommendations

1. **JWT Authentication**

   ```python
   @app.get("/api/customers")
   async def get_customers(token: str = Depends(verify_token)):
       ...
   ```

2. **API Keys**

   ```python
   @app.get("/api/customers")
   async def get_customers(api_key: str = Header(...)):
       if api_key not in valid_keys:
           raise HTTPException(403)
   ```

3. **Rate Limiting**
   ```python
   @limiter.limit("100/minute")
   @app.get("/api/customers")
   async def get_customers():
       ...
   ```

## Monitoring & Logging

### Current Logging

```python
logger.info("DataLoader initialized")
logger.info(f"Loaded {len(rfm_data)} customer records")
logger.error(f"Error loading data: {e}")
```

### Production Monitoring (Recommended)

- **Sentry** - Error tracking
- **Prometheus** - Metrics collection
- **Grafana** - Visualization
- **ELK Stack** - Log aggregation

## Testing Strategy

### Manual Testing

```bash
curl http://localhost:8000/api/metrics
```

### Automated Testing

```bash
python test_api.py
```

### Integration Testing (Recommended)

```python
import pytest
from fastapi.testclient import TestClient

client = TestClient(app)

def test_get_metrics():
    response = client.get("/api/metrics")
    assert response.status_code == 200
    assert "total_customers" in response.json()
```

## Deployment Architecture

### Simple Deployment (Current)

```bash
uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment Options

- **Heroku**: `git push heroku main`
- **AWS Lambda**: Serverless deployment
- **Google Cloud Run**: Container deployment
- **Azure App Service**: PaaS deployment
- **DigitalOcean**: Simple VPS deployment

## Summary

This architecture provides:

- ✅ Clean separation of concerns
- ✅ Scalable and maintainable code
- ✅ Fast response times with caching
- ✅ Type-safe with Pydantic
- ✅ Well-documented API
- ✅ Easy to test and deploy
- ✅ Ready for production with minor changes

The backend successfully extracts all AI/ML features from the Streamlit app and makes them accessible via a modern REST API that any frontend can consume!
