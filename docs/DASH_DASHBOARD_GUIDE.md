# Afrimash Dash Dashboard Guide

## Overview

The Dash/Plotly dashboard (`dashboard_dash.py`) is a comprehensive, interactive web application that provides powerful visualizations and analytics for the Afrimash Customer Intelligence Platform.

## Why Dash Instead of Streamlit?

### Advantages of Dash:
1. **Better for Complex Visualizations** - Plotly integration for advanced charts
2. **More Customizable** - Greater control over layout and styling
3. **Production-Ready** - Better suited for enterprise deployments
4. **Callback System** - More powerful interactivity
5. **Scalability** - Handles larger datasets more efficiently

## Features

### 📊 Executive Dashboard
- **KPI Cards**: Total Customers, Revenue, Churn Rate, CLV, Active Customers, High Risk
- **Critical Alerts**: Real-time warnings about business risks
- **Visualizations**:
  - Customer Distribution by RFM Segment
  - Revenue by Segment
  - Churn Risk Distribution
  - CLV Distribution
  - Monthly Revenue Trend

### 👥 Customer Segments
- **Segmentation Methods**:
  - RFM Segments (Traditional business-focused)
  - K-Means Clusters (ML-driven)
- **Segment Analysis**:
  - Performance summary table
  - Customer count by segment
  - Revenue by segment
  - RFM metrics heatmap
  - CLV distribution box plots
- **Deep Dive**: Detailed metrics for each segment

### 🔮 Predictive Analytics
**Churn Prediction Tab:**
- Churn probability distribution
- Risk level breakdown
- Churn by segment analysis
- Top 20 high-risk customers table

**CLV Prediction Tab:**
- CLV vs Churn risk matrix (scatter plot)
- Customer priority distribution
- Top 20 high-value customers table

**Purchase Timing Tab:**
- Purchase timing status distribution
- Days to next purchase histogram
- Customers due to purchase soon

### 🎯 Recommendations
- **Overview Metrics**: Total recommendations, customer coverage, avg confidence
- **Visualizations**:
  - Top 10 recommended categories
  - Recommendation methods breakdown
  - Confidence score distribution
- **Customer Lookup**: View recommendations for any customer

### 🔍 Customer Search
- Search any customer by ID
- Complete customer profile including:
  - Basic information (segment, revenue, frequency, recency)
  - Predictions (CLV, churn probability, risk level, priority)
  - Product recommendations
  - Recommended actions

### 📈 Business Insights
- **Executive Summary**: Key business metrics
- **Revenue Opportunities**: Identified growth areas with projected values
- **Phased Action Plan**:
  - Week 1: Emergency Response
  - Month 1: Stabilization
  - Quarter 1: Growth
  - Year 1: Transformation
- **Expected Impact**: 12-month projections

### 💰 ROI Calculator
- Interactive calculator with inputs:
  - Campaign budget
  - Expected win-back rate
  - Expected retention increase
  - Campaign duration
- **Outputs**:
  - Win-back revenue
  - Retention revenue
  - Total benefit
  - Net benefit
  - ROI ratio

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify Data Files
Ensure these files exist in `data/processed/`:
- rfm_with_predictions.csv
- transactions_clean.csv
- product_recommendations.csv
- cross_sell_opportunities.csv (optional)
- high_risk_customers.csv (optional)
- action_priority_list.csv (optional)

## Running the Dashboard

### From the src directory:
```bash
cd src
python dashboard_dash.py
```

### Access the dashboard:
Open your browser and navigate to:
```
http://127.0.0.1:8050
```

The dashboard will automatically load data and refresh every hour.

## Features Comparison: Dash vs Streamlit

| Feature | Streamlit | Dash |
|---------|-----------|------|
| **Setup** | Simpler | More complex |
| **Customization** | Limited | Extensive |
| **Interactivity** | Good | Excellent |
| **Visualizations** | Good | Superior |
| **Performance** | Good | Better |
| **Production** | Fair | Excellent |
| **Learning Curve** | Easy | Moderate |
| **Enterprise** | Good | Better |

## Dashboard Architecture

```
dashboard_dash.py
│
├── Data Loading
│   ├── dcc.Store (data-store)
│   ├── dcc.Interval (auto-refresh)
│   └── CSV file loading
│
├── Main Layout
│   ├── Header
│   ├── Navigation Tabs
│   └── Content Area
│
├── Tab Renderers
│   ├── render_executive_dashboard()
│   ├── render_segments()
│   ├── render_predictive()
│   ├── render_recommendations()
│   ├── render_search()
│   ├── render_insights()
│   └── render_roi_calculator()
│
├── Chart Creators
│   ├── create_segment_distribution_chart()
│   ├── create_churn_risk_chart()
│   ├── create_clv_scatter()
│   └── ... (20+ chart functions)
│
└── Callbacks
    ├── update_segment_analysis()
    ├── update_customer_recommendations()
    ├── search_customer()
    └── calculate_roi()
```

## Key Technologies

- **Dash**: Web framework
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation
- **NumPy**: Numerical operations

## Performance Optimization

1. **Data Caching**: dcc.Store caches loaded data
2. **Auto-Refresh**: Updates every hour (configurable)
3. **Sampling**: Large datasets sampled for scatter plots
4. **Lazy Loading**: Tabs load content on demand

## Customization

### Changing Colors
Edit the color constants in helper functions:
```python
colors = {
    'danger': '#dc3545',
    'warning': '#ffc107',
    'success': '#28a745',
    'info': '#17a2b8'
}
```

### Adding New Tabs
1. Add tab to main navigation
2. Create render function
3. Add callback for interactivity
4. Update tab_content callback

### Modifying Refresh Rate
Change the interval in milliseconds:
```python
dcc.Interval(id='interval-component', interval=60*60*1000)  # 1 hour
```

## Troubleshooting

### Dashboard won't start
- Verify all dependencies installed: `pip list | grep dash`
- Check data files exist in correct location
- Ensure port 8050 is not in use

### Data not loading
- Check file paths in load_data function
- Verify CSV files are not corrupted
- Check console for error messages

### Visualizations not showing
- Ensure data columns exist (check column names)
- Verify data is not empty
- Check browser console for JavaScript errors

### Slow performance
- Reduce auto-refresh interval
- Sample larger datasets
- Close unused browser tabs

## Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn dashboard_dash:app.server -b 0.0.0.0:8050
```

### Using Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/dashboard_dash.py"]
```

### Cloud Deployment
- **Heroku**: Deploy with Procfile
- **AWS**: Use Elastic Beanstalk
- **Google Cloud**: Use App Engine
- **Azure**: Use Web Apps

## Best Practices

1. **Data Updates**: Refresh data files regularly
2. **Model Retraining**: Retrain ML models monthly
3. **Monitoring**: Track dashboard usage and errors
4. **Backups**: Regular backups of data files
5. **Security**: Use authentication in production

## Support

For issues or questions:
1. Check this documentation
2. Review error messages in console
3. Verify data file integrity
4. Check Dash documentation: https://dash.plotly.com

## Next Steps

1. **Integrate with Database**: Replace CSV files with database
2. **Add Authentication**: Implement user login
3. **Real-time Updates**: Connect to live data sources
4. **Export Features**: Add PDF/Excel export
5. **Mobile Optimization**: Responsive design improvements

---

**Created for**: Afrimash Customer Intelligence Platform
**Version**: 2.0
**Last Updated**: October 2025
