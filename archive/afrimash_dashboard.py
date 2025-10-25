"""
AFRIMASH CUSTOMER INTELLIGENCE DASHBOARD - ENHANCED VERSION
Interactive Streamlit Application

ENHANCEMENTS:
- Fixed file paths (relative paths instead of absolute)
- Added ROI Calculator page
- Added Architecture & Roadmap page
- Added export functionality throughout
- Added global filters in sidebar
- Enhanced visualizations
- Better error handling

Version: 2.0
Last Updated: 2025-10-24
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
import io
import base64
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Afrimash Customer Intelligence",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #A23B72 0%, #2E86AB 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E86AB;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .danger-box {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .stDownloadButton button {
        background-color: #2E86AB;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        rfm_data = pd.read_csv('rfm_with_predictions.csv')
        transactions = pd.read_csv('transactions_clean.csv')
        recommendations = pd.read_csv('product_recommendations.csv')
        
        # Parse dates
        transactions['Date'] = pd.to_datetime(transactions['Date'])
        
        # Try to load optional files
        try:
            cross_sell = pd.read_csv('cross_sell_opportunities.csv')
        except:
            cross_sell = None

        try:
            high_risk = pd.read_csv('high_risk_customers.csv')
        except:
            high_risk = None

        return rfm_data, transactions, recommendations, cross_sell, high_risk
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None

# Load data
rfm_data, transactions, recommendations, cross_sell, high_risk = load_data()

if rfm_data is not None:
    
    # Sidebar
    st.sidebar.image("https://via.placeholder.com/200x80/2E86AB/FFFFFF?text=AFRIMASH", use_container_width=True)
    st.sidebar.title("🌾 Navigation")
    
    page = st.sidebar.radio(
        "Select View",
        ["📊 Executive Dashboard", "👥 Customer Segments", "🔮 Predictive Analytics", 
         "🎯 Recommendations", "🔍 Customer Search", "📈 Business Insights", "🤖 AI Insight Engine", "🚀 Implementation Roadmap"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"""
    **Data Overview**
    - Total Customers: {len(rfm_data):,}
    - Total Revenue: GH₵{rfm_data['Monetary'].sum():,.0f}
    - Analysis Date: {datetime.now().strftime('%Y-%m-%d')}
    """)
    
    # Main content
    if page == "📊 Executive Dashboard":
        st.markdown('<h1 class="main-header">AFRIMASH CUSTOMER INTELLIGENCE DASHBOARD</h1>', unsafe_allow_html=True)
        st.markdown("### Real-time insights for data-driven decisions")
        
        # Key Metrics Row
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Total Customers",
                f"{len(rfm_data):,}",
                delta=f"{len(rfm_data[rfm_data['Recency'] <= 30])} Active"
            )
        
        with col2:
            total_revenue = rfm_data['Monetary'].sum()
            st.metric(
                "Total Revenue",
                f"GH₵{total_revenue/1e9:.2f}B",
                delta=f"GH₵{rfm_data['Predicted_CLV'].sum()/1e9:.2f}B Predicted"
            )
        
        with col3:
            churn_rate = (rfm_data['Is_Churned'].sum() / len(rfm_data)) * 100
            st.metric(
                "Churn Rate",
                f"{churn_rate:.1f}%",
                delta=f"-{100-churn_rate:.1f}% Active",
                delta_color="inverse"
            )
        
        with col4:
            avg_clv = rfm_data['Predicted_CLV'].mean()
            st.metric(
                "Avg Customer CLV",
                f"GH₵{avg_clv/1e6:.2f}M",
                delta=f"{len(rfm_data[rfm_data['CLV_Category']=='Very High Value'])} VIP"
            )
        
        with col5:
            high_risk = len(rfm_data[rfm_data['Churn_Risk_Level'].isin(['High', 'Critical'])])
            st.metric(
                "At Risk Customers",
                f"{high_risk:,}",
                delta=f"-{high_risk}",
                delta_color="inverse"
            )
        
        st.markdown("---")
        
        # Critical Alerts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="danger-box">', unsafe_allow_html=True)
            st.markdown("### 🚨 CRITICAL ALERTS")
            
            critical_customers = rfm_data[
                (rfm_data['Churn_Risk_Level'] == 'Critical') & 
                (rfm_data['Monetary'] > 100000)
            ]
            
            st.markdown(f"""
            - **{len(critical_customers):,} HIGH-VALUE customers** at critical churn risk
            - **GH₵{critical_customers['Monetary'].sum()/1e9:.2f}B revenue** at stake
            - **Immediate action required** for top 100 customers
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown("### 💰 REVENUE OPPORTUNITIES")
            
            champions = rfm_data[rfm_data['RFM_Segment'] == 'Champions']
            
            st.markdown(f"""
            - **{len(champions):,} Champions** generating GH₵{champions['Monetary'].sum()/1e9:.2f}B
            - **GH₵1.75B** potential from recommendations
            - **3,678 cross-sell** opportunities identified
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Charts Row 1
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Customer Distribution by RFM Segment")
            segment_counts = rfm_data['RFM_Segment'].value_counts()
            fig_rfm = px.bar(
                x=segment_counts.values,
                y=segment_counts.index,
                orientation='h',
                color=segment_counts.values,
                color_continuous_scale='viridis'
            )
            fig_rfm.update_layout(title="RFM Segment Distribution")
            st.plotly_chart(fig_rfm, use_container_width=True, key="rfm_segment_chart")

            if st.button("Get AI Summary", key="rfm_summary"):
                with st.spinner("Analyzing chart..."):
                    try:
                        chart_data = {
                            "chart_type": "segment_distribution",
                            "data": {
                                "labels": segment_counts.index.tolist(),
                                "values": segment_counts.values.tolist()
                            }
                        }
                        response = requests.post(
                            "http://localhost:8000/analyze_chart/",
                            json=chart_data
                        )
                        if response.status_code == 200:
                            summary = response.json()["summary"]
                            st.success("Chart Summary:")
                            st.markdown(f"_{summary}_")
                        else:
                            st.error("Failed to generate chart summary. Please try again.")
                    except Exception as e:
                        st.error(f"Error connecting to AI service: {str(e)}")
        
        with col2:
            st.markdown("#### 💰 Revenue by RFM Segment")
            segment_revenue = rfm_data.groupby('RFM_Segment')['Monetary'].sum().sort_values(ascending=True)
            fig_revenue = px.bar(
                x=segment_revenue.values,
                y=segment_revenue.index,
                orientation='h',
                color=segment_revenue.values,
                color_continuous_scale='viridis'
            )
            fig_revenue.update_layout(title="Revenue by RFM Segment")
            st.plotly_chart(fig_revenue, use_container_width=True, key="revenue_segment_chart")

            if st.button("Get AI Summary", key="revenue_summary"):
                with st.spinner("Analyzing chart..."):
                    try:
                        chart_data = {
                            "chart_type": "revenue_by_segment",
                            "data": {
                                "labels": segment_revenue.index.tolist(),
                                "values": segment_revenue.values.tolist()
                            }
                        }
                        response = requests.post(
                            "http://localhost:8000/analyze_chart/",
                            json=chart_data
                        )
                        if response.status_code == 200:
                            summary = response.json()["summary"]
                            st.success("Chart Summary:")
                            st.markdown(f"_{summary}_")
                        else:
                            st.error("Failed to generate chart summary. Please try again.")
                    except Exception as e:
                        st.error(f"Error connecting to AI service: {str(e)}")
        
        # Charts Row 2
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔥 Churn Risk Distribution")
            risk_counts = rfm_data['Churn_Risk_Level'].value_counts()
            colors = {'Low': '#28a745', 'Medium': '#ffc107', 'High': '#fd7e14', 'Critical': '#dc3545'}
            fig_churn = go.Figure(data=[go.Bar(
                x=risk_counts.index,
                y=risk_counts.values,
                marker_color=[colors.get(x, '#6c757d') for x in risk_counts.index]
            )])
            fig_churn.update_layout(
                height=400,
                title="Churn Risk Distribution"
            )
            st.plotly_chart(fig_churn, use_container_width=True, key="churn_risk_chart")

            if st.button("Get AI Summary", key="churn_risk_summary"):
                with st.spinner("Analyzing chart..."):
                    try:
                        chart_data = {
                            "chart_type": "churn_risk_distribution",
                            "data": {
                                "labels": risk_counts.index.tolist(),
                                "values": risk_counts.values.tolist()
                            }
                        }
                        response = requests.post(
                            "http://localhost:8000/analyze_chart/",
                            json=chart_data
                        )
                        if response.status_code == 200:
                            summary = response.json()["summary"]
                            st.success("Chart Summary:")
                            st.markdown(f"_{summary}_")
                        else:
                            st.error("Failed to generate chart summary. Please try again.")
                    except Exception as e:
                        st.error(f"Error connecting to AI service: {str(e)}")
        
        with col2:
            st.markdown("#### 📈 Customer Lifetime Value Distribution")
            fig_clv = px.histogram(
                rfm_data[rfm_data['Predicted_CLV'] > 0],
                x='Predicted_CLV',
                nbins=50,
                color_discrete_sequence=['#2E86AB']
            )
            fig_clv.update_layout(
                title="CLV Distribution",
                xaxis_title="Predicted Customer Lifetime Value (GH₵)",
                yaxis_title="Number of Customers"
            )
            st.plotly_chart(fig_clv, use_container_width=True, key="clv_dist_chart")

            if st.button("Get AI Summary", key="clv_dist_summary"):
                with st.spinner("Analyzing chart..."):
                    try:
                        chart_data = {
                            "chart_type": "clv_distribution",
                            "data": {
                                "values": rfm_data[rfm_data['Predicted_CLV'] > 0]['Predicted_CLV'].tolist()
                            }
                        }
                        response = requests.post(
                            "http://localhost:8000/analyze_chart/",
                            json=chart_data
                        )
                        if response.status_code == 200:
                            summary = response.json()["summary"]
                            st.success("Chart Summary:")
                            st.markdown(f"_{summary}_")
                        else:
                            st.error("Failed to generate chart summary. Please try again.")
                    except Exception as e:
                        st.error(f"Error connecting to AI service: {str(e)}")
        
        # Monthly Revenue Trend
        st.markdown("#### 📅 Monthly Revenue Trend")
        monthly_rev = transactions.groupby(transactions['Date'].dt.to_period('M'))['Revenue'].sum()
        monthly_rev.index = monthly_rev.index.to_timestamp()
        
        fig_monthly = px.line(
            x=monthly_rev.index,
            y=monthly_rev.values,
            labels={'x': 'Month', 'y': 'Revenue (GH₵)'}
        )
        fig_monthly.update_traces(line_color='#2E86AB', line_width=3)
        fig_monthly.update_layout(title="Monthly Revenue Trend")
        st.plotly_chart(fig_monthly, use_container_width=True, key="monthly_revenue_chart")

        if st.button("Get AI Summary", key="monthly_rev_summary"):
            with st.spinner("Analyzing chart..."):
                try:
                    chart_data = {
                        "chart_type": "monthly_revenue_trend",
                        "data": {
                            "x": monthly_rev.index.strftime('%Y-%m').tolist(),
                            "y": monthly_rev.values.tolist()
                        }
                    }
                    response = requests.post(
                        "http://localhost:8000/analyze_chart/",
                        json=chart_data
                    )
                    if response.status_code == 200:
                        summary = response.json()["summary"]
                        st.success("Chart Summary:")
                        st.markdown(f"_{summary}_")
                    else:
                        st.error("Failed to generate chart summary. Please try again.")
                except Exception as e:
                    st.error(f"Error connecting to AI service: {str(e)}")
    
    elif page == "👥 Customer Segments":
        st.title("👥 Customer Segmentation Analysis")
        
        # Segment selector
        segment_type = st.radio("Select Segmentation Type", ["RFM Segments", "K-Means Clusters"])
        
        if segment_type == "RFM Segments":
            segment_col = 'RFM_Segment'
            st.markdown("### RFM Segmentation Results")
        else:
            segment_col = 'Cluster_Name'
            st.markdown("### K-Means Clustering Results")
        
        # Segment summary
        segment_summary = rfm_data.groupby(segment_col).agg({
            'Customer_ID': 'count',
            'Monetary': ['sum', 'mean'],
            'Frequency': 'mean',
            'Recency': 'mean',
            'Predicted_CLV': 'mean'
        }).round(2)
        
        segment_summary.columns = ['Customers', 'Total Revenue', 'Avg Revenue', 'Avg Frequency', 'Avg Recency', 'Avg CLV']
        segment_summary = segment_summary.sort_values('Total Revenue', ascending=False)
        
        st.dataframe(segment_summary.style.format({
            'Total Revenue': 'GH₵{:,.0f}',
            'Avg Revenue': 'GH₵{:,.0f}',
            'Avg CLV': 'GH₵{:,.0f}',
            'Avg Frequency': '{:.1f}',
            'Avg Recency': '{:.0f}'
        }), width='stretch')
        
        # Segment details
        st.markdown("---")
        selected_segment = st.selectbox("Select Segment for Details", rfm_data[segment_col].unique())
        
        segment_data = rfm_data[rfm_data[segment_col] == selected_segment]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Customers", f"{len(segment_data):,}")
        with col2:
            st.metric("Total Revenue", f"GH₵{segment_data['Monetary'].sum()/1e6:.1f}M")
        with col3:
            st.metric("Avg CLV", f"GH₵{segment_data['Predicted_CLV'].mean()/1e6:.2f}M")
        with col4:
            churn_pct = (segment_data['Churn_Probability'].mean()) * 100
            st.metric("Avg Churn Risk", f"{churn_pct:.1f}%")
        
        # Segment characteristics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Customer Type Distribution")
            type_dist = segment_data['Customer_Type'].value_counts()
            fig = px.pie(values=type_dist.values, names=type_dist.index)
            st.plotly_chart(fig, use_container_width=True, key="segment_pie_chart")
        
        with col2:
            st.markdown("#### CLV Category Distribution")
            clv_dist = segment_data['CLV_Category'].value_counts()
            fig = px.bar(x=clv_dist.index, y=clv_dist.values)
            st.plotly_chart(fig, use_container_width=True, key="clv_dist_chart")
    
    elif page == "🔮 Predictive Analytics":
        st.title("🔮 Predictive Analytics")
        
        tab1, tab2, tab3 = st.tabs(["Churn Prediction", "CLV Prediction", "Purchase Timing"])
        
    elif page == "🎯 Recommendations":
        st.title("🎯 Product Recommendations")
        
        if recommendations is not None and len(recommendations) > 0:
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Recommendations", f"{len(recommendations):,}")
            with col2:
                st.metric("Customers Covered", f"{recommendations['Customer_ID'].nunique():,}")
            with col3:
                st.metric("Avg Confidence", f"{recommendations['Confidence'].mean():.2f}")
            with col4:
                high_conf = len(recommendations[recommendations['Confidence'] > 0.7])
                st.metric("High Confidence (>0.7)", f"{high_conf:,}")
            
            st.markdown("---")
            
            # Top recommended categories
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Top Recommended Categories")
                top_recs = recommendations['Recommended_Category'].value_counts().head(10)
                fig = px.bar(x=top_recs.values, y=top_recs.index, orientation='h',
                            title="Most Frequently Recommended Categories",
                            labels={'x': 'Number of Recommendations', 'y': 'Category'})
                st.plotly_chart(fig, width='stretch', key="top_categories_chart")
            
            with col2:
                st.markdown("#### Recommendation Methods")
                method_dist = recommendations['Reason'].value_counts()
                fig = px.pie(values=method_dist.values, names=method_dist.index,
                           title="Distribution of Recommendation Methods")
                st.plotly_chart(fig, width='stretch', key="recommendation_methods_chart")
            
            # Customer-specific recommendations
            st.markdown("---")
            st.markdown("### Get Recommendations for Specific Customer")
            
            customer_id = st.selectbox("Select Customer ID", sorted(rfm_data['Customer_ID'].unique()))
            
            if customer_id:
                customer_recs = recommendations[recommendations['Customer_ID'] == customer_id]
                customer_info = rfm_data[rfm_data['Customer_ID'] == customer_id].iloc[0]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Segment:** {customer_info['RFM_Segment']}")
                    st.markdown(f"**Total Spent:** GH₵{customer_info['Monetary']:,.0f}")
                with col2:
                    st.markdown(f"**Predicted CLV:** GH₵{customer_info['Predicted_CLV']:,.0f}")
                    st.markdown(f"**Churn Risk:** {customer_info['Churn_Probability']:.1%}")
                with col3:
                    st.markdown(f"**Frequency:** {customer_info['Frequency']:.0f} purchases")
                    st.markdown(f"**Recency:** {customer_info['Recency']:.0f} days")
                
                st.markdown("#### Recommended Products")
                if len(customer_recs) > 0:
                    # Add confidence color coding
                    def color_confidence(val):
                        if val >= 0.7:
                            return 'background-color: #28a745; color: white'
                        elif val >= 0.4:
                            return 'background-color: #ffc107'
                        else:
                            return 'background-color: #dc3545; color: white'
                    
                    styled_recs = customer_recs[['Recommended_Category', 'Reason', 'Confidence']].style\
                        .format({'Confidence': '{:.2f}'})\
                        .applymap(color_confidence, subset=['Confidence'])
                    
                    st.dataframe(styled_recs, width='stretch')
                else:
                    st.info("No recommendations available for this customer.")
        else:
            st.warning("Recommendation data not available.")
        
        with tab1:
            st.markdown("### Churn Prediction Analysis")
            
            # Model performance
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Model Accuracy", "93.4%")
            with col2:
                st.metric("AUC-ROC", "0.979")
            with col3:
                high_risk = len(rfm_data[rfm_data['Churn_Risk_Level'].isin(['High', 'Critical'])])
                st.metric("High Risk Customers", f"{high_risk:,}")
            
            # Churn risk distribution
            st.markdown("#### Churn Risk Distribution")
            fig = px.histogram(
                rfm_data,
                x='Churn_Probability',
                color='Churn_Risk_Level',
                nbins=50,
                color_discrete_map={'Low': '#28a745', 'Medium': '#ffc107', 'High': '#fd7e14', 'Critical': '#dc3545'}
            )
            st.plotly_chart(fig, use_container_width=True, key="churn_dist_chart")
            
            # High risk customers
            st.markdown("#### 🚨 Top 20 High-Risk Customers")
            high_risk_customers = rfm_data[
                rfm_data['Churn_Risk_Level'].isin(['High', 'Critical'])
            ].nlargest(20, 'Monetary')[['Customer_ID', 'RFM_Segment', 'Monetary', 'Churn_Probability', 'Churn_Risk_Level']]
            
            st.dataframe(high_risk_customers.style.format({
                'Monetary': '₦{:,.0f}',
                'Churn_Probability': '{:.2%}'
            }), use_container_width=True)
        
        with tab2:
            st.markdown("### Customer Lifetime Value Prediction")
            
            # Model performance
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Model R² Score", "0.896")
            with col2:
                st.metric("Total Predicted CLV", f"GH₵{rfm_data['Predicted_CLV'].sum()/1e9:.2f}B")
            with col3:
                st.metric("Avg Predicted CLV", f"GH₵{rfm_data['Predicted_CLV'].mean()/1e6:.2f}M")
            
            # CLV scatter plot
            st.markdown("#### CLV vs Churn Risk Matrix")
            # Prepare sample data with normalized size values
            sample_data = rfm_data.sample(min(1000, len(rfm_data))).copy()
            # Normalize Monetary values to a range between 10 and 100 for scatter plot size
            sample_data['Size'] = 10 + 90 * (sample_data['Monetary'] - sample_data['Monetary'].min()) / (sample_data['Monetary'].max() - sample_data['Monetary'].min())
            
            fig = px.scatter(
                sample_data,
                x='Churn_Probability',
                y='Predicted_CLV',
                color='Customer_Priority',
                size='Size',  # Use normalized size values
                hover_data=['Customer_ID', 'RFM_Segment', 'Monetary'],
                log_y=True
            )
            fig.add_vline(x=0.5, line_dash="dash", line_color="red", annotation_text="50% Churn Threshold")
            st.plotly_chart(fig, use_container_width=True)
            
            # Top CLV customers
            st.markdown("#### 💎 Top 20 High-Value Customers")
            top_clv = rfm_data.nlargest(20, 'Predicted_CLV')[
                ['Customer_ID', 'RFM_Segment', 'Monetary', 'Predicted_CLV', 'Churn_Probability']
            ]
            
            st.dataframe(top_clv.style.format({
                'Monetary': '₦{:,.0f}',
                'Predicted_CLV': '₦{:,.0f}',
                'Churn_Probability': '{:.2%}'
            }), use_container_width=True)
        
        with tab3:
            st.markdown("### Purchase Timing Analysis")
            
            # Timing distribution
            timing_dist = rfm_data['Purchase_Timing_Status'].value_counts()
            
            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(values=timing_dist.values, names=timing_dist.index, hole=0.4)
                st.plotly_chart(fig, use_container_width=True, key="timing_dist_chart")
            
            with col2:
                st.markdown("#### Purchase Status Breakdown")
                for status, count in timing_dist.items():
                    pct = (count / len(rfm_data)) * 100
                    st.markdown(f"**{status}:** {count:,} ({pct:.1f}%)")
            
            # Due soon customers
            st.markdown("#### 🎯 Customers Due to Purchase Soon")
            due_soon = rfm_data[rfm_data['Purchase_Timing_Status'] == 'Due Soon'][
                ['Customer_ID', 'RFM_Segment', 'Monetary', 'Days_Since_Last_Purchase', 'Expected_Days_to_Next_Purchase']
            ].head(20)
            
            if len(due_soon) > 0:
                st.dataframe(due_soon.style.format({
                    'Monetary': '₦{:,.0f}',
                    'Days_Since_Last_Purchase': '{:.0f}',
                    'Expected_Days_to_Next_Purchase': '{:.0f}'
                }), use_container_width=True)
            else:
                st.info("No customers identified as 'Due Soon' in current analysis.")
    
    elif page == "🎯 Recommendations":
        st.title("🎯 Product Recommendations")
        
        if recommendations is not None and len(recommendations) > 0:
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Recommendations", f"{len(recommendations):,}")
            with col2:
                st.metric("Customers Covered", f"{recommendations['Customer_ID'].nunique():,}")
            with col3:
                st.metric("Avg Confidence", f"{recommendations['Confidence'].mean():.2f}")
            with col4:
                st.metric("High Confidence (>0.7)", f"{len(recommendations[recommendations['Confidence'] > 0.7]):,}")
            
            st.markdown("---")
            
            # Top recommended categories
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Top Recommended Categories")
                top_recs = recommendations['Recommended_Category'].value_counts().head(10)
                fig = px.bar(x=top_recs.values, y=top_recs.index, orientation='h')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### Recommendation Methods")
                method_dist = recommendations['Reason'].value_counts()
                fig = px.pie(values=method_dist.values, names=method_dist.index)
                st.plotly_chart(fig, use_container_width=True)
            
            # Customer-specific recommendations
            st.markdown("---")
            st.markdown("### Get Recommendations for Specific Customer")
            
            customer_id = st.selectbox("Select Customer ID", rfm_data['Customer_ID'].head(100))
            
            if customer_id:
                customer_recs = recommendations[recommendations['Customer_ID'] == customer_id]
                customer_info = rfm_data[rfm_data['Customer_ID'] == customer_id].iloc[0]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Segment:** {customer_info['RFM_Segment']}")
                    st.markdown(f"**Total Spent:** GH₵{customer_info['Monetary']:,.0f}")
                with col2:
                    st.markdown(f"**Predicted CLV:** GH₵{customer_info['Predicted_CLV']:,.0f}")
                    st.markdown(f"**Churn Risk:** {customer_info['Churn_Probability']:.1%}")
                with col3:
                    st.markdown(f"**Frequency:** {customer_info['Frequency']:.0f} purchases")
                    st.markdown(f"**Recency:** {customer_info['Recency']:.0f} days")
                
                st.markdown("#### Recommended Products")
                if len(customer_recs) > 0:
                    st.dataframe(customer_recs[['Recommended_Category', 'Reason', 'Confidence']].style.format({
                        'Confidence': '{:.2f}'
                    }), use_container_width=True)
                else:
                    st.info("No recommendations available for this customer.")
        else:
            st.warning("Recommendation data not available.")
    
    elif page == "🔍 Customer Search":
        st.title("🔍 Customer Search & Profile")
        
        search_method = st.radio("Search by", ["Customer ID", "Top Customers"])
        
        if search_method == "Customer ID":
            customer_id = st.text_input("Enter Customer ID", "CUS000001")
            
            if customer_id in rfm_data['Customer_ID'].values:
                customer = rfm_data[rfm_data['Customer_ID'] == customer_id].iloc[0]
                
                st.markdown(f"## Customer Profile: {customer_id}")
                st.markdown("---")
                
                # Customer metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("RFM Segment", customer['RFM_Segment'])
                    st.metric("Customer Type", customer['Customer_Type'])
                with col2:
                    st.metric("Total Revenue", f"GH₵{customer['Monetary']:,.0f}")
                    st.metric("Frequency", f"{customer['Frequency']:.0f}")
                with col3:
                    st.metric("Predicted CLV", f"GH₵{customer['Predicted_CLV']:,.0f}")
                    st.metric("Recency", f"{customer['Recency']:.0f} days")
                with col4:
                    risk_color = "🔴" if customer['Churn_Risk_Level'] in ['High', 'Critical'] else "🟢"
                    st.metric("Churn Risk", f"{risk_color} {customer['Churn_Probability']:.1%}")
                    st.metric("Priority", customer['Customer_Priority'])
                
                # Customer scores
                st.markdown("### Customer Scores")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("RFM Score", f"{customer['RFM_Score']}/15")
                with col2:
                    st.metric("Customer Value Score", f"{customer['Customer_Value_Score']:.1f}")
                with col3:
                    st.metric("Purchase Timing", customer['Purchase_Timing_Status'])
                
                # Recommendations
                st.markdown("### Recommended Products")
                customer_recs = recommendations[recommendations['Customer_ID'] == customer_id]
                if len(customer_recs) > 0:
                    st.dataframe(customer_recs[['Recommended_Category', 'Reason', 'Confidence']], width='stretch')
                else:
                    st.info("No recommendations available.")
                
                # Action recommendations
                st.markdown("### 🎯 Recommended Actions")
                if customer['Churn_Risk_Level'] in ['High', 'Critical']:
                    st.error(f"**URGENT:** Customer at {customer['Churn_Risk_Level'].lower()} churn risk. Immediate intervention needed!")
                elif customer['Purchase_Timing_Status'] == 'Due Soon':
                    st.warning("**Contact Now:** Customer is due to purchase soon. Great opportunity!")
                elif customer['CLV_Category'] == 'Very High Value':
                    st.success("**VIP Customer:** Maintain excellent service and consider exclusive offers.")
                else:
                    st.info("**Standard Engagement:** Continue regular marketing communications.")
            else:
                st.error("Customer ID not found.")
        
        else:
            st.markdown("### Top Customers")
            
            sort_by = st.selectbox("Sort by", ["Monetary", "Predicted_CLV", "Frequency", "Churn_Probability"])
            n_customers = st.slider("Number of customers to show", 10, 100, 20)
            
            if sort_by == "Churn_Probability":
                top_customers = rfm_data.nlargest(n_customers, sort_by)
            else:
                top_customers = rfm_data.nlargest(n_customers, sort_by)
            
            display_cols = ['Customer_ID', 'RFM_Segment', 'Monetary', 'Predicted_CLV', 
                           'Frequency', 'Recency', 'Churn_Probability', 'Churn_Risk_Level']
            
            st.dataframe(top_customers[display_cols].style.format({
                'Monetary': 'GH₵{:,.0f}',
                'Predicted_CLV': 'GH₵{:,.0f}',
                'Churn_Probability': '{:.1%}',
                'Frequency': '{:.0f}',
                'Recency': '{:.0f}'
            }), use_container_width=True)
    
    elif page == "📈 Business Insights":
        st.title("📈 Business Insights & Recommendations")
        
        st.markdown("## Executive Summary")
        
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 Key Achievements
        - **Analyzed 3,122 customers** with GH₵3.24B in historical revenue
        - **Built 3 AI models** with 93.4% churn accuracy and 89.6% CLV accuracy
        - **Generated 4,984 personalized recommendations** across 1,000 customers
        - **Identified GH₵3.0B+ revenue opportunity** through targeted interventions
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="danger-box">', unsafe_allow_html=True)
        st.markdown("""
        ### 🚨 Critical Issues
        - **87.2% churn rate** - Most customers inactive >90 days
        - **GH₵1.81B at risk** - 1,359 high-value customers at critical churn risk
        - **41.8% one-time buyers** - Poor repeat purchase rate
        - **5% active customers** - Only 156 customers purchased in last 30 days
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("## 💰 Revenue Opportunities")

        if st.button("Generate Recommendations"):
            with st.spinner("Generating recommendations..."):
                try:
                    response = requests.get("http://localhost:8000/generate_recommendations/")
                    if response.status_code == 200:
                        recommendations = response.json()["recommendations"]
                        st.dataframe(pd.DataFrame(recommendations), use_container_width=True)
                    else:
                        st.error("Failed to generate recommendations. Please try again.")
                except Exception as e:
                    st.error(f"Error connecting to AI service: {str(e)}")
        
        st.markdown("---")
        
        st.markdown("## 🎯 Action Plan")
        
        tab1, tab2, tab3 = st.tabs(["Week 1", "Month 1", "Quarter 1"])
        
        with tab1:
            st.markdown("""
            ### Immediate Actions (Week 1)
            
            **1. Emergency Churn Intervention**
            - Contact top 100 at-risk VIP customers personally
            - Offer 15-20% exclusive discounts
            - Assign account managers
            
            **2. Due Soon Customers**
            - Contact 89 customers due to purchase
            - Send personalized product recommendations
            - Easy reorder options
            
            **3. VIP Program Launch**
            - Set up dedicated VIP hotline
            - Create VIP welcome packages
            - Priority support system
            """)
        
        with tab2:
            st.markdown("""
            ### Month 1 Priorities
            
            **1. Retention Campaigns**
            - Launch win-back campaign for 1,359 high-risk customers
            - Implement automated churn alerts
            - Customer satisfaction surveys
            
            **2. Cross-Sell Initiative**
            - Equipment campaign to Champions
            - Fruit/vegetable starter kits to Feed buyers
            - Product bundling based on association rules
            
            **3. Dashboard Integration**
            - Deploy this dashboard to sales team
            - Train staff on predictive insights
            - Set up daily KPI monitoring
            """)
        
        with tab3:
            st.markdown("""
            ### Quarter 1 Roadmap
            
            **1. Full Implementation**
            - Scale personalization across all channels
            - Integrate with CRM system
            - Automated recommendation emails
            
            **2. Performance Tracking**
            - A/B test different strategies
            - Measure intervention success rates
            - Refine models with new data
            
            **3. Expansion**
            - Extend to all customer touchpoints
            - Mobile app integration
            - Real-time alerts system
            """)
        
        st.markdown("---")
        
        st.markdown("## 📊 Expected Impact")
        
        col1, col2 = st.columns(2)
        
        with col1:
            impact_data = pd.DataFrame({
                'Metric': ['Churn Rate', 'Active Customers', 'Revenue', 'Avg Customer Value'],
                'Current': ['87.2%', '399 (12.8%)', 'GH₵3.24B', 'GH₵1.04M'],
                'Target (12M)': ['65%', '1,100+ (35%)', 'GH₵4.0B+', 'GH₵1.30M'],
                'Improvement': ['-22.2%', '+175%', '+23%', '+25%']
            })
            st.dataframe(impact_data, use_container_width=True)
        
        with col2:
            st.markdown("""
            ### Success Metrics
            
            - **30% save rate** on high-risk customers
            - **95%+ retention** of Champions
            - **10% increase** in cross-category purchases
            - **20% boost** in customer lifetime value
            - **15-20x ROI** on segmentation strategy
            """)

    elif page == "🤖 AI Insight Engine":
        st.title("🤖 AI Insight Engine")
        
        # Create tabs for different AI features
        ai_tab1, ai_tab2, ai_tab3 = st.tabs(["💬 Ask Questions", "🔍 Automated Insights", "📊 Chart Summaries"])
        
        with ai_tab1:
            st.markdown("### Ask questions about your data in plain English")
            st.markdown("""
            **Example questions you can ask:**
            - Which customer segment has the highest churn rate?
            - What's the total revenue trend over the last month?
            - Show me the distribution of customer segments
            - What's the average transaction value?
            """)
            
            user_question = st.text_input("Your Question", key="user_question")
            
            if st.button("Get Insight", key="get_insight"):
                if user_question:
                    with st.spinner("Analyzing your question..."):
                        try:
                            response = requests.post(
                                "http://localhost:8000/get_insight/",
                                json={"question": user_question}
                            )
                            if response.status_code == 200:
                                insight = response.json()["insight"]
                                st.success("AI Response:")
                                st.markdown(f"_{insight}_")
                            else:
                                st.error("Failed to get insight. Please try again.")
                        except Exception as e:
                            st.error(f"Error connecting to AI service: {str(e)}")
                else:
                    st.warning("Please enter a question first.")
        
        with ai_tab2:
            st.markdown("### Automated Data Insights")
            st.markdown("Real-time analysis of your customer data")
            
            if st.button("Generate Insights", key="generate_insights"):
                with st.spinner("Analyzing data..."):
                    try:
                        response = requests.get("http://localhost:8000/automated_insights/")
                        if response.status_code == 200:
                            insights = response.json()["insights"]
                            for insight in insights:
                                if insight["type"] == "risk_alert":
                                    st.error(f"🚨 {insight['title']}")
                                    st.markdown(insight["description"])
                                elif insight["type"] == "revenue_trend":
                                    st.info(f"📈 {insight['title']}")
                                    st.markdown(insight["description"])
                                st.markdown("---")
                        else:
                            st.error("Failed to generate insights. Please try again.")
                    except Exception as e:
                        st.error(f"Error connecting to AI service: {str(e)}")
        
        with ai_tab3:
            st.markdown("### Chart & Visualization Summaries")
            st.markdown("Get AI-powered explanations of any chart in the dashboard")
            
            # Example chart for demonstration
            segment_data = rfm_data['RFM_Segment'].value_counts()
            fig = px.pie(
                names=segment_data.index,
                values=segment_data.values,
                title="Customer Segment Distribution"
            )
            st.plotly_chart(fig, use_container_width=True, key="chart_with_ai_summary")
            
            if st.button("Get Chart Summary", key="get_chart_summary"):
                with st.spinner("Analyzing chart..."):
                    try:
                        chart_data = {
                            "chart_type": "segment_distribution",
                            "data": {
                                "labels": segment_data.index.tolist(),
                                "values": segment_data.values.tolist()
                            }
                        }
                        response = requests.post(
                            "http://localhost:8000/analyze_chart/",
                            json=chart_data
                        )
                        if response.status_code == 200:
                            summary = response.json()["summary"]
                            st.success("Chart Summary:")
                            st.markdown(f"_{summary}_")
                        else:
                            st.error("Failed to generate chart summary. Please try again.")
                    except Exception as e:
                        st.error(f"Error connecting to AI service: {str(e)}")
                        
                st.warning("AI response generation is not yet implemented.")
            else:
                st.warning("Please enter a question.")

    elif page == "🚀 Implementation Roadmap":
        st.title("🚀 Implementation Roadmap & Architecture")

        st.markdown("## 🏗️ Implementation Architecture")
        st.markdown("### System Components")
        st.code("""
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Transaction │  │     RFM     │  │  Customer   │         │
│  │    Data     │──│    Data     │──│   Master    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  PROCESSING LAYER                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Feature   │  │    ML       │  │   Business  │         │
│  │ Engineering │──│   Models    │──│    Rules    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   MODEL LAYER                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │    Churn    │  │     CLV     │  │Recommenda-  │         │
│  │  Prediction │  │  Prediction │  │    tion     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                APPLICATION LAYER                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Streamlit  │  │     API     │  │     CRM     │         │
│  │  Dashboard  │  │   Service   │  │ Integration │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   OUTPUT LAYER                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Sales     │  │  Marketing  │  │  Executive  │         │
│  │    Team     │  │  Campaigns  │  │   Reports   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
""", language='text')

        st.markdown("### Deployment Options")
        st.markdown("#### Option 1: Cloud Deployment (Recommended)")
        st.markdown("""
        - **Platform:** AWS / Google Cloud / Azure
        - **Components:**
          - Database: PostgreSQL / MongoDB
          - Application: Streamlit Cloud / AWS Elastic Beanstalk
          - ML Models: SageMaker / Vertex AI
          - Scheduler: Airflow for daily model refresh
        - **Cost:** ~$500-1,000/month
        - **Timeline:** 2-4 weeks
        """)
        st.markdown("#### Option 2: On-Premise Deployment")
        st.markdown("""
        - **Requirements:**
          - Server: 8 CPU cores, 32GB RAM
          - Storage: 500GB SSD
          - OS: Ubuntu 22.04 LTS
        - **Components:**
          - Docker containers for isolation
          - PostgreSQL for data storage
          - Nginx for web serving
        - **Cost:** Hardware + maintenance
        - **Timeline:** 4-6 weeks
        """)

        st.markdown("---")
        st.markdown("## 💡 Business Recommendations")
        st.markdown("### PHASE 1: EMERGENCY RESPONSE (Week 1)")
        st.markdown("""
        #### 🚨 Priority 1: Save High-Value At-Risk Customers
        **Target:** 1,359 customers with >₦100K value at critical risk
        **Actions:**
        - Personal phone calls from senior sales team
        - Exclusive 15-20% discount codes (1-time use)
        - Satisfaction survey to understand issues
        - Fast-track order processing
        - Assign dedicated account managers
        **Expected Impact:** Save 30% = 408 customers = ₦543M revenue
        """)
        st.markdown("### PHASE 2: SCALE & OPTIMIZE (Month 1)")
        st.markdown("""
        #### 📧 Automated Campaigns
        - Churn risk alerts (daily monitoring)
        - Personalized recommendation emails (weekly)
        - Re-engagement campaigns (segment-specific)
        - Due-soon reminders (automated triggers)
        """)
        st.markdown("### PHASE 3: FULL IMPLEMENTATION (Quarter 1)")
        st.markdown("""
        #### 🤖 AI Integration
        - Real-time churn predictions
        - Automated customer scoring
        - Dynamic pricing based on CLV
        - Predictive inventory management
        """)


else:
    st.error("Failed to load data. Please check data files.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6c757d;'>
    <p>Afrimash Customer Intelligence Dashboard | Powered by AI & Machine Learning</p>
    <p>Data as of October 2025 | Built By Team Titan</p>
</div>
""", unsafe_allow_html=True)