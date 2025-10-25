# Afrimash Customer Intelligence API

REST API backend for the Afrimash Customer Intelligence platform, providing AI/ML-powered customer analytics and predictions.

## Features

- 📊 **Business Metrics**: Real-time KPIs and performance indicators
- 👥 **Customer Segmentation**: RFM and K-Means clustering analysis
- 🔮 **Churn Prediction**: AI-powered customer churn risk assessment
- 💎 **CLV Prediction**: Customer Lifetime Value forecasting
- 🎯 **Product Recommendations**: Personalized product suggestions
- 📈 **Analytics**: Revenue trends, segment distribution, and insights
- 🔍 **Customer Search**: Detailed customer profiles and history

## Tech Stack

- **FastAPI**: Modern, fast web framework
- **Pandas**: Data processing and analysis
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server

## Installation

1. Navigate to the backend directory:

```bash
cd backend
```

2. Create and activate a virtual environment (if not already done):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the API

### Development Mode

```bash
cd backend
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

Or using Python directly:

```bash
cd backend
python -m app.api.main
```

### Production Mode

```bash
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check

- `GET /` - API health check

### Business Metrics

- `GET /api/metrics` - Get high-level business metrics

### Customers

- `GET /api/customers` - Get paginated customer list (with filters)
- `GET /api/customers/{customer_id}` - Get detailed customer profile
- `GET /api/search/customers` - Search customers by ID

### Segmentation

- `GET /api/segments` - Get customer segment analysis (RFM or K-Means)

### Predictions

- `GET /api/churn/predictions` - Get churn predictions with risk levels
- `GET /api/clv/predictions` - Get CLV predictions

### Recommendations

- `GET /api/recommendations/{customer_id}` - Get product recommendations for customer

### Analytics

- `GET /api/analytics/revenue-trend` - Monthly revenue trends
- `GET /api/analytics/segment-distribution` - Customer distribution by segment
- `GET /api/analytics/risk-distribution` - Customer distribution by risk level
- `GET /api/analytics/revenue-by-segment` - Revenue by customer segment
- `GET /api/analytics/clv-distribution` - CLV distribution data

## Data Requirements

The API expects the following CSV files in the project root directory:

1. `rfm_with_predictions.csv` - Customer RFM data with ML predictions
2. `transactions_clean.csv` - Transaction history
3. `product_recommendations.csv` - Product recommendations

## CORS Configuration

The API is configured to accept requests from:

- `http://localhost:3000` (Create React App default)
- `http://localhost:5173` (Vite default)

Update the CORS settings in `app/api/main.py` to add additional origins.

## Environment Variables

Create a `.env` file in the backend directory (optional):

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Data Configuration
DATA_DIR=../
```

## Example API Calls

### Get Business Metrics

```bash
curl http://localhost:8000/api/metrics
```

### Get Customer Profile

```bash
curl http://localhost:8000/api/customers/CUS000001
```

### Get Churn Predictions

```bash
curl "http://localhost:8000/api/churn/predictions?risk_level=High&limit=50"
```

### Search Customers

```bash
curl "http://localhost:8000/api/search/customers?query=CUS001"
```

## Response Format

All endpoints return JSON responses:

```json
{
  "status": "success",
  "data": { ... }
}
```

Errors return:

```json
{
  "detail": "Error message",
  "timestamp": "2025-10-25T12:00:00"
}
```

## Performance

- Data is cached in memory for fast response times
- Pagination support for large datasets
- Efficient data filtering and sorting

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
```

### Type Checking

```bash
mypy app/
```

## Troubleshooting

### Data Files Not Found

- Ensure CSV files are in the correct location (project root)
- Check file permissions
- Verify file paths in `data_loader.py`

### CORS Errors

- Update `allow_origins` in `main.py` to include your frontend URL
- Verify the frontend is making requests to the correct API endpoint

### Port Already in Use

```bash
# Use a different port
uvicorn app.api.main:app --port 8001
```

## License

Copyright © 2025 Afrimash

## Support

For issues and questions, please contact the development team.
