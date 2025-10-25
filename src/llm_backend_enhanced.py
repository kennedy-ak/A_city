"""
AFRIMASH AI BACKEND - ENHANCED VERSION
FastAPI backend with Google Gemini AI integration

Features:
- Natural language query processing
- Chart analysis and summarization
- Automated business insights generation
- Customer recommendation generation

Version: 2.0 Enhanced
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from typing import Optional, Dict, List
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

# Initialize FastAPI
app = FastAPI(
    title="Afrimash AI Backend",
    description="AI-powered insights for customer intelligence",
    version="2.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini AI
def setup_gemini():
    """Initialize Gemini AI model"""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY not found in environment variables. Please add it to your .env file."
        )

    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-pro')

# Load customer data
def load_data():
    """Load all data files"""
    try:
        rfm_data = pd.read_csv('../data/processed/rfm_with_predictions.csv')
        transactions = pd.read_csv('../data/processed/transactions_clean.csv')
        recommendations = pd.read_csv('../data/processed/product_recommendations.csv')

        transactions['Date'] = pd.to_datetime(transactions['Date'])

        return {
            'rfm_data': rfm_data,
            'transactions': transactions,
            'recommendations': recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")

# Pydantic models for request/response
class Query(BaseModel):
    question: str
    context: Optional[Dict] = None

class ChartData(BaseModel):
    chart_type: str
    data: Dict
    context: Optional[Dict] = None

# === API ENDPOINTS ===

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "message": "Afrimash AI Backend is operational",
        "version": "2.0"
    }

@app.post("/get_insight/")
async def get_insight(query: Query):
    """Process natural language questions about customer data"""
    try:
        data = load_data()
        model = setup_gemini()

        # Prepare data summary for context
        rfm_summary = f"""
        Customer Data Summary:
        - Total Customers: {len(data['rfm_data']):,}
        - Total Revenue: ₦{data['rfm_data']['Monetary'].sum()/1e9:.2f}B
        - Average CLV: ₦{data['rfm_data']['Predicted_CLV'].mean()/1e6:.2f}M
        - Churn Rate: {(data['rfm_data']['Is_Churned'].sum() / len(data['rfm_data'])) * 100:.1f}%

        Segment Distribution:
        {data['rfm_data']['RFM_Segment'].value_counts().to_dict()}

        Top Risk Levels:
        {data['rfm_data']['Churn_Risk_Level'].value_counts().to_dict()}
        """

        # Create prompt for Gemini
        prompt = f"""
        You are an expert data analyst for Afrimash, an agricultural marketplace.

        {rfm_summary}

        User Question: {query.question}

        Provide a clear, actionable answer based on the data. Include specific numbers and recommendations.
        Keep the response concise (2-3 paragraphs max).
        """

        # Get response from Gemini
        response = model.generate_content(prompt)

        return {"insight": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insight: {str(e)}")

@app.post("/analyze_chart/")
async def analyze_chart(chart_data: ChartData):
    """Generate AI summary for visualizations"""
    try:
        model = setup_gemini()

        # Create prompt based on chart type
        if chart_data.chart_type == "segment_distribution":
            labels = chart_data.data.get('labels', [])
            values = chart_data.data.get('values', [])

            data_text = "\n".join([f"- {label}: {value:,} customers" for label, value in zip(labels, values)])

            prompt = f"""
            Analyze this customer segment distribution:

            {data_text}

            Provide a 2-3 sentence summary highlighting:
            1. The dominant segment
            2. Any concerning patterns
            3. A key actionable insight
            """

        elif chart_data.chart_type == "revenue_by_segment":
            labels = chart_data.data.get('labels', [])
            values = chart_data.data.get('values', [])

            data_text = "\n".join([f"- {label}: ₦{value/1e9:.2f}B" for label, value in zip(labels, values)])

            prompt = f"""
            Analyze this revenue distribution by segment:

            {data_text}

            Provide a 2-3 sentence summary highlighting:
            1. The highest revenue segment and its contribution
            2. Revenue concentration patterns
            3. A recommendation for revenue optimization
            """

        elif chart_data.chart_type == "churn_risk_distribution":
            labels = chart_data.data.get('labels', [])
            values = chart_data.data.get('values', [])

            data_text = "\n".join([f"- {label} Risk: {value:,} customers" for label, value in zip(labels, values)])

            prompt = f"""
            Analyze this churn risk distribution:

            {data_text}

            Provide a 2-3 sentence summary highlighting:
            1. The most critical risk level and its impact
            2. The urgency of intervention needed
            3. A specific action recommendation
            """

        elif chart_data.chart_type == "sunburst_hierarchy":
            segments = chart_data.data.get('segments', {})
            risk_levels = chart_data.data.get('risk_levels', {})

            prompt = f"""
            Analyze this customer hierarchy:

            Segments: {segments}
            Risk Levels: {risk_levels}

            Provide a 2-3 sentence summary highlighting:
            1. The overall customer structure
            2. Key risk patterns across segments
            3. Priority action areas
            """

        else:
            prompt = f"""
            Analyze this chart data:
            Type: {chart_data.chart_type}
            Data: {json.dumps(chart_data.data)}

            Provide a brief 2-3 sentence summary with key insights and recommendations.
            """

        # Get response from Gemini
        response = model.generate_content(prompt)

        return {"summary": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing chart: {str(e)}")

@app.get("/automated_insights/")
async def get_automated_insights():
    """Generate automated business insights from data"""
    try:
        data = load_data()
        model = setup_gemini()
        rfm_data = data['rfm_data']

        # Calculate key metrics
        high_risk_customers = rfm_data[rfm_data['Churn_Risk_Level'].isin(['High', 'Critical'])]
        high_risk_revenue = high_risk_customers['Monetary'].sum()

        champions = rfm_data[rfm_data['RFM_Segment'] == 'Champions']
        champions_revenue = champions['Monetary'].sum()

        due_soon = rfm_data[rfm_data['Purchase_Timing_Status'] == 'Due Soon']

        # Create detailed prompt
        prompt = f"""
        As an expert business analyst for Afrimash, analyze this customer data and generate 5 actionable insights.

        Key Metrics:
        - Total Customers: {len(rfm_data):,}
        - High-Risk Customers: {len(high_risk_customers):,} (₦{high_risk_revenue/1e9:.2f}B at risk)
        - Champions: {len(champions):,} (₦{champions_revenue/1e9:.2f}B revenue)
        - Due Soon: {len(due_soon):,} customers

        Segment Distribution:
        {rfm_data['RFM_Segment'].value_counts().to_dict()}

        Generate exactly 5 insights in this JSON format:
        [
            {{
                "type": "risk_alert",
                "title": "Brief title",
                "description": "Detailed insight with specific numbers and recommendations"
            }},
            ...
        ]

        Types: risk_alert, opportunity, trend, recommendation

        Focus on actionable insights that can drive business decisions.
        """

        # Get response from Gemini
        response = model.generate_content(prompt)

        # Try to parse as JSON, if it fails return formatted insights
        try:
            insights = json.loads(response.text)
        except:
            # Fallback to manual insights if AI doesn't return proper JSON
            insights = [
                {
                    "type": "risk_alert",
                    "title": "High-Value Customers at Critical Risk",
                    "description": f"{len(high_risk_customers):,} high-value customers are at critical churn risk, representing ₦{high_risk_revenue/1e9:.2f}B in potential revenue loss. Immediate intervention required for top 100 customers."
                },
                {
                    "type": "opportunity",
                    "title": "Champions Segment Driving Revenue",
                    "description": f"{len(champions):,} Champions are generating ₦{champions_revenue/1e9:.2f}B ({(champions_revenue/rfm_data['Monetary'].sum())*100:.1f}% of total). Protect this segment with VIP treatment and exclusive offers."
                },
                {
                    "type": "trend",
                    "title": "Purchase Timing Opportunities",
                    "description": f"{len(due_soon):,} customers are due to purchase soon. Contact them within 48 hours with personalized recommendations for optimal conversion."
                },
                {
                    "type": "recommendation",
                    "title": "Focus on Retention Over Acquisition",
                    "description": f"With {(rfm_data['Is_Churned'].sum() / len(rfm_data)) * 100:.1f}% churn rate, retention should be priority. Launch targeted win-back campaigns for high-value segments."
                },
                {
                    "type": "opportunity",
                    "title": "Cross-Sell Revenue Potential",
                    "description": f"Product recommendations cover {data['recommendations']['Customer_ID'].nunique():,} customers. Implementing these could generate additional ₦500M+ in revenue."
                }
            ]

        return {"insights": insights}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")

@app.get("/generate_recommendations/")
async def generate_recommendations_endpoint():
    """Generate business recommendations based on data"""
    try:
        data = load_data()
        model = setup_gemini()
        rfm_data = data['rfm_data']

        prompt = f"""
        Based on this Afrimash customer data, generate 5 specific business recommendations:

        Total Customers: {len(rfm_data):,}
        Churn Rate: {(rfm_data['Is_Churned'].sum() / len(rfm_data)) * 100:.1f}%
        Total Revenue: ₦{rfm_data['Monetary'].sum()/1e9:.2f}B

        Segments: {rfm_data['RFM_Segment'].value_counts().to_dict()}

        Format as a list of actionable recommendations with expected impact.
        """

        response = model.generate_content(prompt)

        return {
            "recommendations": [
                {"text": rec.strip()} for rec in response.text.split('\n') if rec.strip()
            ][:5]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

# Run with: uvicorn llm_backend_enhanced:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
