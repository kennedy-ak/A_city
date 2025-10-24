
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import pandas as pd
from typing import Optional, Dict, List
import google.generativeai as genai
from functools import lru_cache
import os
from dotenv import load_dotenv



app = FastAPI()

# Configure Gemini
def setup_gemini():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not found")
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-pro')

# Load data
def load_data():
    try:
        rfm_data = pd.read_csv('rfm_with_predictions.csv')
        transactions = pd.read_csv('transactions_clean.csv')
        recommendations = pd.read_csv('product_recommendations.csv')
        
        # Parse dates
        transactions['Date'] = pd.to_datetime(transactions['Date'])
        return {
            'rfm_data': rfm_data,
            'transactions': transactions,
            'recommendations': recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")

class Query(BaseModel):
    question: str
    context: Optional[Dict] = None

class ChartData(BaseModel):
    chart_type: str
    data: Dict
    context: Optional[Dict] = None

@app.post("/get_insight/")
async def get_insight(query: Query):
    try:
        data = load_data()
        # Process the question and generate insights
        insight = generate_data_insight(query.question, data)
        return {"insight": insight}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze_chart/")
async def analyze_chart(chart_data: ChartData):
    try:
        # Validate incoming data
        if not chart_data:
            raise HTTPException(status_code=400, detail="No chart data provided")
            
        if not chart_data.chart_type:
            raise HTTPException(status_code=400, detail="Chart type is required")
            
        if not chart_data.data:
            raise HTTPException(status_code=400, detail="Chart data is required")
            
        # Generate summary for specific chart/visualization
        summary = generate_chart_summary(chart_data)
        return {"summary": summary}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while analyzing the chart: {str(e)}")

@app.get("/automated_insights/")
async def get_automated_insights():
    try:
        data = load_data()
        insights = generate_automated_insights(data)
        return {"insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/generate_recommendations/")
async def generate_recommendations_endpoint():
    try:
        data = load_data()
        recommendations = generate_recommendations(data)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_data_insight(question: str, data: Dict[str, pd.DataFrame]) -> str:
    """
    Process natural language questions using Gemini AI and generate insights from data.
    """
    try:
        model = setup_gemini()
        
        # Prepare data context
        rfm_summary = data['rfm_data'].describe().to_string()
        segment_summary = data['rfm_data']['RFM_Segment'].value_counts().to_string()
        churn_summary = data['rfm_data']['Churn_Risk_Level'].value_counts().to_string()
        
        recent_transactions = data['transactions'].sort_values('Date').tail(30)
        transaction_summary = recent_transactions.describe().to_string()
        
        # Create prompt
        prompt = f"""As a customer intelligence analyst, analyze the following data and answer this question: {question}

Data Summaries:
RFM Metrics:
{rfm_summary}

Customer Segments:
{segment_summary}

Churn Risk Distribution:
{churn_summary}

Recent Transaction Statistics:
{transaction_summary}

Please provide a clear, concise insight based on this data. Focus on the most relevant metrics and trends that answer the question."""

        # Get response from Gemini
        response = model.generate_content(prompt)
        
        # Clean and format the response
        insight = response.text.strip()
        return insight
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insight: {str(e)}")

def generate_chart_summary(chart_data: ChartData) -> str:
    """Generate an AI-powered summary for a specific chart or visualization"""
    try:
        model = setup_gemini()
        
        if not hasattr(chart_data, 'chart_type') or not hasattr(chart_data, 'data'):
            raise ValueError("Invalid chart data format: Missing required fields")
            
        chart_type = chart_data.chart_type
        data = chart_data.data
        
        # Validate data structure
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
            
        # Create prompt based on chart type and data
        if chart_type == "segment_distribution":
            if 'values' not in data or 'labels' not in data:
                raise ValueError("Segment distribution requires 'values' and 'labels' in data")
                
            if len(data['values']) == 0 or len(data['labels']) == 0:
                raise ValueError("Empty values or labels provided")
                
            total = sum(data['values'])
            if total == 0:
                raise ValueError("Sum of values cannot be zero")
                
            segments_data = [f"{label}: {value} ({(value/total)*100:.1f}%)" 
                           for label, value in zip(data['labels'], data['values'])]
            data_description = "\n".join(segments_data)
            
            prompt = f"""As a customer intelligence analyst, analyze this customer segment distribution:

{data_description}

Please provide a concise, insightful summary that highlights:
1. The dominant segment and its significance
2. Any notable patterns or imbalances
3. Potential business implications

Keep the response focused and actionable."""
        else:
            data_str = "\n".join([f"{k}: {v}" for k, v in data.items()])
            prompt = f"""Analyze this {chart_type} visualization data:

{data_str}

Please provide a concise, insightful summary focusing on key patterns and business implications."""

        # Get response from Gemini
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating chart summary: {str(e)}")

def generate_automated_insights(data: Dict[str, pd.DataFrame]) -> List[Dict[str, str]]:
    """Generate AI-powered automated insights from the data"""
    try:
        model = setup_gemini()
        
        # Prepare comprehensive data summary
        rfm_data = data['rfm_data']
        transactions = data['transactions']
        
        # Recent trends
        recent_transactions = transactions.sort_values('Date').tail(60)
        last_month = recent_transactions.tail(30)['Amount'].sum()
        prev_month = recent_transactions.head(30)['Amount'].sum()
        revenue_change = ((last_month - prev_month) / prev_month) * 100
        
        # Customer segments and churn
        segment_counts = rfm_data['RFM_Segment'].value_counts()
        churn_risk = rfm_data['Churn_Risk_Level'].value_counts()
        
        # Create analysis prompt
        prompt = f"""As a customer intelligence analyst, analyze these business metrics and generate key insights:

Revenue Trends:
- Last Month Revenue: ${last_month:,.2f}
- Previous Month Revenue: ${prev_month:,.2f}
- Change: {revenue_change:.1f}%

Customer Segments Distribution:
{segment_counts.to_string()}

Churn Risk Distribution:
{churn_risk.to_string()}

Please identify 3-4 significant insights about:
1. Critical risks or alerts
2. Notable trends
3. Business opportunities
4. Customer behavior patterns

Format each insight as a JSON object with "type" (risk_alert/trend/opportunity), "title", and "description"."""

        # Get response from Gemini
        response = model.generate_content(prompt)
        
        # Parse response into insights list
        # Assuming Gemini returns properly formatted JSON-like strings
        insights_text = response.text.strip()
        
        # Convert text insights into structured format
        insights = []
        for line in insights_text.split('\n'):
            if line.strip() and '"type"' in line:
                # Clean up the line to make it valid JSON
                clean_line = line.strip().replace("'", '"')
                if clean_line.endswith(','):
                    clean_line = clean_line[:-1]
                try:
                    import json
                    insight = json.loads(clean_line)
                    insights.append(insight)
                except json.JSONDecodeError:
                    # If parsing fails, create a formatted insight manually
                    insights.append({
                        "type": "analysis",
                        "title": "Data Analysis",
                        "description": line.strip()
                    })
        
        return insights
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating automated insights: {str(e)}")

def generate_recommendations(data: Dict[str, pd.DataFrame]) -> List[Dict[str, str]]:
    """Generate AI-powered business recommendations from the data"""
    try:
        model = setup_gemini()
        
        # Prepare comprehensive data summary
        rfm_data = data['rfm_data']
        
        # Create analysis prompt
        prompt = f"""As a business strategist, analyze the provided customer intelligence data and generate a list of 5-7 actionable business recommendations. For each recommendation, provide an 'Initiative', a 'Target' audience, a 'Potential Revenue' impact, and a 'Timeline'.

        Data Summary:
        {rfm_data.describe().to_string()}

        Please format the output as a list of JSON objects, where each object has the keys: 'Initiative', 'Target', 'Potential Revenue', and 'Timeline'."""

        # Get response from Gemini
        response = model.generate_content(prompt)
        
        # Parse response into recommendations list
        recommendations_text = response.text.strip()
        
        # Convert text recommendations into structured format
        recommendations = []
        for line in recommendations_text.split('\n'):
            if line.strip() and '"Initiative"' in line:
                # Clean up the line to make it valid JSON
                clean_line = line.strip().replace("'", '"')
                if clean_line.endswith(','):
                    clean_line = clean_line[:-1]
                try:
                    import json
                    recommendation = json.loads(clean_line)
                    recommendations.append(recommendation)
                except json.JSONDecodeError:
                    # If parsing fails, create a formatted recommendation manually
                    recommendations.append({
                        "Initiative": "Error parsing recommendation",
                        "Target": "N/A",
                        "Potential Revenue": "N/A",
                        "Timeline": "N/A"
                    })
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")
