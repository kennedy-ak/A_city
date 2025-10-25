# Backend API Quick Start Guide

## 🚀 What Was Built

A complete FastAPI backend that extracts all AI/ML functionality from the Streamlit dashboard (`app.py` and `afrimash_dashboard.py`) and makes it available as REST API endpoints for a React frontend.

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   └── api/
│       ├── __init__.py
│       ├── main.py           # Main FastAPI application
│       ├── models.py          # Pydantic data models
│       ├── data_loader.py     # Data loading utilities
│       └── analytics.py       # Analytics service
├── venv/                      # Virtual environment (existing)
├── requirements.txt           # Python dependencies
├── run.py                     # Development server script
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── README.md                 # Detailed documentation
└── REACT_INTEGRATION.md      # React integration guide
```

## ⚡ Quick Start

### 1. Install Dependencies (if needed)

The backend already has a virtual environment. Just ensure all dependencies are installed:

```bash
cd backend
.\venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

### 2. Run the API Server

**Option A: Using the run script (recommended)**

```bash
cd backend
python run.py
```

**Option B: Using uvicorn directly**

```bash
cd backend
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Option C: From project root**

```bash
cd backend
python -m app.api.main
```

### 3. Access the API

- **API Base URL**: http://localhost:8000
- **Interactive Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/

## 🎯 Available API Endpoints

### Business Metrics

```http
GET /api/metrics
```

Returns KPIs: total customers, revenue, churn rate, CLV, at-risk customers

### Customer Management

```http
GET /api/customers?page=1&page_size=20&segment=Champions&risk_level=High
GET /api/customers/{customer_id}
GET /api/search/customers?query=CUS001
```

### Segmentation

```http
GET /api/segments?segment_type=rfm
GET /api/segments?segment_type=kmeans
```

### Predictions

```http
GET /api/churn/predictions?risk_level=High&limit=100
GET /api/clv/predictions?limit=100&sort_by=predicted_clv
```

### Recommendations

```http
GET /api/recommendations/{customer_id}
```

### Analytics

```http
GET /api/analytics/revenue-trend
GET /api/analytics/segment-distribution
GET /api/analytics/risk-distribution
GET /api/analytics/revenue-by-segment
GET /api/analytics/clv-distribution
```

## 🧪 Test the API

### Using cURL

```bash
# Health check
curl http://localhost:8000/

# Get business metrics
curl http://localhost:8000/api/metrics

# Get customer profile
curl http://localhost:8000/api/customers/CUS000001

# Get churn predictions
curl "http://localhost:8000/api/churn/predictions?risk_level=Critical&limit=20"
```

### Using the Browser

1. Navigate to http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Enter parameters (if needed)
5. Click "Execute"
6. See the response below

## 🔗 Connect to React Frontend

### CORS Configuration

The API is already configured to accept requests from:

- `http://localhost:3000` (Create React App)
- `http://localhost:5173` (Vite)

### Example React Usage

```javascript
import axios from "axios";

// Get business metrics
const response = await axios.get("http://localhost:8000/api/metrics");
console.log(response.data);

// Get customer profile
const customer = await axios.get(
  "http://localhost:8000/api/customers/CUS000001"
);
console.log(customer.data);
```

See `backend/REACT_INTEGRATION.md` for complete React integration guide with examples!

## 🎨 Key Features Extracted from Streamlit

### From `app.py` and `afrimash_dashboard.py`:

✅ **Business Metrics Dashboard**

- Total customers, revenue, churn rate
- Active customers, at-risk customers
- CLV predictions

✅ **Customer Segmentation**

- RFM segmentation
- K-Means clustering
- Segment analysis and metrics

✅ **Predictive Analytics**

- Churn prediction (93.4% accuracy)
- CLV prediction (89.6% R² score)
- Purchase timing analysis

✅ **Product Recommendations**

- Personalized recommendations
- Confidence scores
- Recommendation reasoning

✅ **Customer Profiles**

- Detailed customer information
- Purchase history analysis
- Risk assessment
- Value scoring

✅ **Analytics & Insights**

- Revenue trends
- Segment distribution
- Risk distribution
- CLV distribution

## 📊 Data Flow

```
CSV Files (Project Root)
    ↓
DataLoader (caching)
    ↓
FastAPI Endpoints
    ↓
JSON Response
    ↓
React Frontend
```

## 🛠️ Development Tips

### View Logs

The API logs all data loading and errors. Watch the console output.

### Reload Data

Data is cached in memory. Restart the server to reload from CSV files.

### Add New Endpoints

1. Define route in `app/api/main.py`
2. Add response model in `app/api/models.py`
3. Use DataLoader to access data
4. Return JSON response

### Environment Variables

Create `.env` file from `.env.example`:

```bash
cp .env.example .env
```

## 🐛 Troubleshooting

### "File not found" error

- Ensure CSV files are in the project root directory:
  - `rfm_with_predictions.csv`
  - `transactions_clean.csv`
  - `product_recommendations.csv`

### Port already in use

```bash
# Use a different port
python run.py  # Then edit run.py to change port
# Or
uvicorn app.api.main:app --port 8001
```

### CORS errors from frontend

- Check frontend URL is in `allow_origins` in `main.py`
- Verify API URL in frontend code

### Module import errors

```bash
# Make sure you're in the backend directory
cd backend
# Activate virtual environment
.\venv\Scripts\activate
# Install dependencies
pip install -r requirements.txt
```

## 📚 Next Steps

1. ✅ **API is Ready** - Start building your React frontend
2. 📖 **Read Integration Guide** - See `REACT_INTEGRATION.md`
3. 🎨 **Build UI Components** - Use the API endpoints
4. 🚀 **Deploy** - Deploy backend to cloud platform

## 🎉 Success!

Your AI/ML backend is now running and ready to power a modern React frontend. All the intelligence from the Streamlit dashboard is now available via clean REST API endpoints!

Visit http://localhost:8000/docs to explore the API interactively.
