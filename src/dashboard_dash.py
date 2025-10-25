"""
AFRIMASH CUSTOMER INTELLIGENCE DASHBOARD - DASH/PLOTLY VERSION
Interactive Dashboard with Advanced Visualizations

Features:
- Executive Dashboard with KPIs and critical alerts
- Customer Segmentation Analysis (RFM & K-Means)
- Predictive Analytics (Churn, CLV, Purchase Timing)
- Product Recommendations Engine
- Customer Search & Profile
- Business Insights & Action Plans
- ROI Calculator
- Export Functionality

Version: 2.0
Last Updated: 2025-10-25
"""

import dash
from dash import dcc, html, dash_table, Input, Output, State, callback
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Initialize the Dash app
app = dash.Dash(
    __name__,
    title="Afrimash Customer Intelligence",
    suppress_callback_exceptions=True
)

# Load data
@callback(Output('data-store', 'data'), Input('interval-component', 'n_intervals'))
def load_data(n):
    try:
        rfm_data = pd.read_csv('../data/processed/rfm_with_predictions.csv')
        transactions = pd.read_csv('../data/processed/transactions_clean.csv')
        recommendations = pd.read_csv('../data/processed/product_recommendations.csv')

        # Parse dates
        transactions['Date'] = pd.to_datetime(transactions['Date'])

        # Try to load optional files
        try:
            cross_sell = pd.read_csv('../data/processed/cross_sell_opportunities.csv')
        except:
            cross_sell = pd.DataFrame()

        try:
            high_risk = pd.read_csv('../data/processed/high_risk_customers.csv')
        except:
            high_risk = pd.DataFrame()

        try:
            action_priority = pd.read_csv('../data/processed/action_priority_list.csv')
        except:
            action_priority = pd.DataFrame()

        return {
            'rfm': rfm_data.to_dict('records'),
            'transactions': transactions.to_dict('records'),
            'recommendations': recommendations.to_dict('records'),
            'cross_sell': cross_sell.to_dict('records') if not cross_sell.empty else [],
            'high_risk': high_risk.to_dict('records') if not high_risk.empty else [],
            'action_priority': action_priority.to_dict('records') if not action_priority.empty else []
        }
    except Exception as e:
        print(f"Error loading data: {e}")
        return {}

# Custom CSS
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

# App layout
app.layout = html.Div([
    # Hidden components for data storage
    dcc.Store(id='data-store'),
    dcc.Interval(id='interval-component', interval=60*60*1000, n_intervals=0),  # Update every hour

    # Header
    html.Div([
        html.Div([
            html.H1('🌾 Afrimash Customer Intelligence Platform',
                   style={
                       'textAlign': 'center',
                       'color': '#2E86AB',
                       'marginBottom': '10px',
                       'fontSize': '2.5rem',
                       'fontWeight': 'bold'
                   }),
            html.P('AI-Powered Customer Analytics & Insights',
                  style={
                      'textAlign': 'center',
                      'color': '#666',
                      'fontSize': '1.2rem',
                      'marginBottom': '20px'
                  })
        ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px', 'marginBottom': '20px'})
    ]),

    # Main Navigation Tabs
    dcc.Tabs(id='main-tabs', value='executive', children=[
        dcc.Tab(label='📊 Executive Dashboard', value='executive', style={'fontWeight': 'bold'}),
        dcc.Tab(label='👥 Customer Segments', value='segments', style={'fontWeight': 'bold'}),
        dcc.Tab(label='🔮 Predictive Analytics', value='predictive', style={'fontWeight': 'bold'}),
        dcc.Tab(label='🎯 Recommendations', value='recommendations', style={'fontWeight': 'bold'}),
        dcc.Tab(label='🔍 Customer Search', value='search', style={'fontWeight': 'bold'}),
        dcc.Tab(label='📈 Business Insights', value='insights', style={'fontWeight': 'bold'}),
        dcc.Tab(label='💰 ROI Calculator', value='roi', style={'fontWeight': 'bold'}),
    ], style={'marginBottom': '20px'}),

    # Content area
    html.Div(id='tab-content', style={'padding': '20px'})
], style={'padding': '20px', 'backgroundColor': '#ffffff', 'fontFamily': 'Arial, sans-serif'})


# Callback for tab content
@callback(
    Output('tab-content', 'children'),
    Input('main-tabs', 'value'),
    State('data-store', 'data')
)
def render_tab_content(active_tab, data):
    if data is None or not data:
        return html.Div("Loading data...", style={'textAlign': 'center', 'padding': '50px'})

    rfm_df = pd.DataFrame(data['rfm'])
    transactions_df = pd.DataFrame(data['transactions'])
    recommendations_df = pd.DataFrame(data['recommendations'])

    if active_tab == 'executive':
        return render_executive_dashboard(rfm_df, transactions_df)
    elif active_tab == 'segments':
        return render_segments(rfm_df)
    elif active_tab == 'predictive':
        return render_predictive(rfm_df)
    elif active_tab == 'recommendations':
        return render_recommendations(rfm_df, recommendations_df)
    elif active_tab == 'search':
        return render_search(rfm_df, recommendations_df)
    elif active_tab == 'insights':
        return render_insights(rfm_df)
    elif active_tab == 'roi':
        return render_roi_calculator(rfm_df)

    return html.Div("Select a tab")


def render_executive_dashboard(rfm_df, transactions_df):
    """Executive Dashboard with KPIs and Critical Alerts"""

    # Calculate KPIs
    total_customers = len(rfm_df)
    total_revenue = rfm_df['Monetary'].sum()
    churn_rate = (rfm_df['Is_Churned'].sum() / len(rfm_df)) * 100 if 'Is_Churned' in rfm_df.columns else 0
    avg_clv = rfm_df['Predicted_CLV'].mean() if 'Predicted_CLV' in rfm_df.columns else 0
    active_customers = len(rfm_df[rfm_df['Recency'] <= 90]) if 'Recency' in rfm_df.columns else 0

    # High-risk customers
    if 'Churn_Risk_Level' in rfm_df.columns:
        high_risk = len(rfm_df[rfm_df['Churn_Risk_Level'].isin(['High', 'Critical'])])
    else:
        high_risk = 0

    # Create KPI cards
    kpi_cards = html.Div([
        html.Div([
            create_kpi_card('Total Customers', f'{total_customers:,}', '👥', '#17a2b8'),
            create_kpi_card('Total Revenue', f'₦{total_revenue/1e9:.2f}B', '💰', '#28a745'),
            create_kpi_card('Churn Rate', f'{churn_rate:.1f}%', '⚠️', '#dc3545'),
            create_kpi_card('Avg CLV', f'₦{avg_clv/1e6:.2f}M', '📊', '#6f42c1'),
            create_kpi_card('Active Customers', f'{active_customers:,}', '✅', '#20c997'),
            create_kpi_card('High Risk', f'{high_risk:,}', '🚨', '#fd7e14'),
        ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))', 'gap': '20px', 'marginBottom': '30px'})
    ])

    # Critical Alerts
    alerts = html.Div([
        html.H3('🚨 Critical Alerts', style={'color': '#dc3545', 'marginBottom': '15px'}),
        html.Div([
            create_alert('High Churn Rate', f'{churn_rate:.1f}% of customers have churned', 'danger'),
            create_alert('Revenue at Risk', f'₦{(rfm_df[rfm_df["Churn_Risk_Level"].isin(["High", "Critical"])]["Monetary"].sum() if "Churn_Risk_Level" in rfm_df.columns else 0)/1e9:.2f}B from high-risk customers', 'warning') if 'Churn_Risk_Level' in rfm_df.columns else None,
            create_alert('Low Activity', f'{(active_customers/total_customers)*100:.1f}% customer activity rate', 'warning'),
        ], style={'display': 'flex', 'flexDirection': 'column', 'gap': '10px'})
    ], style={'marginBottom': '30px'})

    # Charts
    charts_row1 = html.Div([
        html.Div([
            dcc.Graph(
                figure=create_segment_distribution_chart(rfm_df),
                style={'height': '400px'}
            )
        ], style={'flex': '1'}),
        html.Div([
            dcc.Graph(
                figure=create_revenue_by_segment_chart(rfm_df),
                style={'height': '400px'}
            )
        ], style={'flex': '1'})
    ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'})

    charts_row2 = html.Div([
        html.Div([
            dcc.Graph(
                figure=create_churn_risk_chart(rfm_df),
                style={'height': '400px'}
            )
        ], style={'flex': '1'}),
        html.Div([
            dcc.Graph(
                figure=create_clv_distribution_chart(rfm_df),
                style={'height': '400px'}
            )
        ], style={'flex': '1'})
    ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'})

    # Monthly revenue trend
    if 'Date' in transactions_df.columns:
        transactions_df['Date'] = pd.to_datetime(transactions_df['Date'])
        monthly_revenue = transactions_df.groupby(transactions_df['Date'].dt.to_period('M'))['Revenue'].sum().reset_index()
        monthly_revenue['Date'] = monthly_revenue['Date'].astype(str)

        revenue_trend = html.Div([
            dcc.Graph(
                figure=px.line(
                    monthly_revenue,
                    x='Date',
                    y='Revenue',
                    title='Monthly Revenue Trend',
                    markers=True
                ).update_layout(
                    xaxis_title='Month',
                    yaxis_title='Revenue (₦)',
                    hovermode='x unified',
                    template='plotly_white'
                ),
                style={'height': '400px'}
            )
        ], style={'marginBottom': '20px'})
    else:
        revenue_trend = html.Div()

    return html.Div([
        kpi_cards,
        alerts,
        charts_row1,
        charts_row2,
        revenue_trend
    ])


def render_segments(rfm_df):
    """Customer Segmentation Analysis"""

    # Segment type selector
    segment_selector = html.Div([
        html.H3('Select Segmentation Method', style={'marginBottom': '15px'}),
        dcc.RadioItems(
            id='segment-type-radio',
            options=[
                {'label': ' RFM Segments (Traditional)', 'value': 'RFM_Segment'},
                {'label': ' K-Means Clusters (ML-Driven)', 'value': 'Cluster_Name'}
            ],
            value='RFM_Segment' if 'RFM_Segment' in rfm_df.columns else 'Cluster_Name',
            inline=True,
            style={'marginBottom': '20px'}
        )
    ], style={'marginBottom': '30px'})

    # Segment summary table
    segment_summary = html.Div([
        html.H3('Segment Performance Summary', style={'marginBottom': '15px'}),
        html.Div(id='segment-summary-table')
    ], style={'marginBottom': '30px'})

    # Segment visualizations
    segment_charts = html.Div([
        html.Div([
            html.Div([
                dcc.Graph(id='segment-count-chart', style={'height': '400px'})
            ], style={'flex': '1'}),
            html.Div([
                dcc.Graph(id='segment-revenue-chart', style={'height': '400px'})
            ], style={'flex': '1'})
        ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}),

        html.Div([
            html.Div([
                dcc.Graph(id='segment-rfm-heatmap', style={'height': '500px'})
            ], style={'flex': '1'}),
            html.Div([
                dcc.Graph(id='segment-clv-box', style={'height': '500px'})
            ], style={'flex': '1'})
        ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'})
    ])

    # Segment details
    segment_details = html.Div([
        html.H3('Segment Deep Dive', style={'marginBottom': '15px'}),
        dcc.Dropdown(
            id='segment-dropdown',
            placeholder='Select a segment to explore...',
            style={'marginBottom': '20px'}
        ),
        html.Div(id='segment-details-content')
    ], style={'marginTop': '30px'})

    return html.Div([
        segment_selector,
        segment_summary,
        segment_charts,
        segment_details
    ])


def render_predictive(rfm_df):
    """Predictive Analytics Dashboard"""

    predictive_tabs = dcc.Tabs([
        dcc.Tab(label='Churn Prediction', children=[
            html.Div([
                html.H3('Churn Risk Analysis', style={'marginBottom': '20px'}),

                # Churn overview
                html.Div([
                    html.Div([
                        dcc.Graph(
                            figure=create_churn_probability_dist(rfm_df),
                            style={'height': '400px'}
                        )
                    ], style={'flex': '1'}),
                    html.Div([
                        dcc.Graph(
                            figure=create_churn_risk_level_chart(rfm_df),
                            style={'height': '400px'}
                        )
                    ], style={'flex': '1'})
                ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}),

                # Churn by segment
                html.Div([
                    dcc.Graph(
                        figure=create_churn_by_segment_chart(rfm_df),
                        style={'height': '400px'}
                    )
                ], style={'marginBottom': '20px'}),

                # High-risk customer table
                html.Div([
                    html.H4('Top 20 High-Risk Customers', style={'marginBottom': '15px'}),
                    create_high_risk_table(rfm_df)
                ], style={'marginTop': '20px'})
            ], style={'padding': '20px'})
        ]),

        dcc.Tab(label='CLV Prediction', children=[
            html.Div([
                html.H3('Customer Lifetime Value Analysis', style={'marginBottom': '20px'}),

                # CLV overview
                html.Div([
                    html.Div([
                        dcc.Graph(
                            figure=create_clv_scatter(rfm_df),
                            style={'height': '500px'}
                        )
                    ], style={'flex': '2'}),
                    html.Div([
                        dcc.Graph(
                            figure=create_clv_priority_matrix(rfm_df),
                            style={'height': '500px'}
                        )
                    ], style={'flex': '1'})
                ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}),

                # Top CLV customers
                html.Div([
                    html.H4('Top 20 High-Value Customers', style={'marginBottom': '15px'}),
                    create_top_clv_table(rfm_df)
                ], style={'marginTop': '20px'})
            ], style={'padding': '20px'})
        ]),

        dcc.Tab(label='Purchase Timing', children=[
            html.Div([
                html.H3('Purchase Timing Predictions', style={'marginBottom': '20px'}),

                html.Div([
                    html.Div([
                        dcc.Graph(
                            figure=create_timing_status_chart(rfm_df),
                            style={'height': '400px'}
                        )
                    ], style={'flex': '1'}),
                    html.Div([
                        dcc.Graph(
                            figure=create_days_to_next_purchase_chart(rfm_df),
                            style={'height': '400px'}
                        )
                    ], style={'flex': '1'})
                ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}),

                # Due soon customers
                html.Div([
                    html.H4('Customers Due to Purchase Soon', style={'marginBottom': '15px'}),
                    create_due_soon_table(rfm_df)
                ], style={'marginTop': '20px'})
            ], style={'padding': '20px'})
        ])
    ])

    return html.Div([predictive_tabs])


def render_recommendations(rfm_df, recommendations_df):
    """Product Recommendations Dashboard"""

    # Overview metrics
    total_recs = len(recommendations_df)
    unique_customers = recommendations_df['Customer_ID'].nunique() if 'Customer_ID' in recommendations_df.columns else 0
    avg_confidence = recommendations_df['Confidence'].mean() if 'Confidence' in recommendations_df.columns else 0

    overview = html.Div([
        create_kpi_card('Total Recommendations', f'{total_recs:,}', '🎯', '#17a2b8'),
        create_kpi_card('Customers Covered', f'{unique_customers:,}', '👥', '#28a745'),
        create_kpi_card('Avg Confidence', f'{avg_confidence:.2%}', '✨', '#6f42c1'),
    ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))', 'gap': '20px', 'marginBottom': '30px'})

    # Recommendation charts
    charts = html.Div([
        html.Div([
            html.Div([
                dcc.Graph(
                    figure=create_top_recommended_categories(recommendations_df),
                    style={'height': '400px'}
                )
            ], style={'flex': '1'}),
            html.Div([
                dcc.Graph(
                    figure=create_recommendation_method_chart(recommendations_df),
                    style={'height': '400px'}
                )
            ], style={'flex': '1'})
        ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}),

        html.Div([
            dcc.Graph(
                figure=create_confidence_distribution(recommendations_df),
                style={'height': '400px'}
            )
        ], style={'marginBottom': '20px'})
    ])

    # Customer recommendation lookup
    lookup = html.Div([
        html.H3('Customer Recommendation Lookup', style={'marginBottom': '15px'}),
        dcc.Dropdown(
            id='rec-customer-dropdown',
            options=[{'label': f'Customer {cid}', 'value': cid} for cid in rfm_df['Customer_ID'].head(100).tolist()],
            placeholder='Select a customer to view recommendations...',
            style={'marginBottom': '20px'}
        ),
        html.Div(id='customer-rec-content')
    ], style={'marginTop': '30px'})

    return html.Div([
        overview,
        charts,
        lookup
    ])


def render_search(rfm_df, recommendations_df):
    """Customer Search and Profile"""

    search_section = html.Div([
        html.H3('Search Customer by ID', style={'marginBottom': '15px'}),
        html.Div([
            dcc.Dropdown(
                id='search-customer-dropdown',
                options=[{'label': f'Customer {cid}', 'value': cid} for cid in rfm_df['Customer_ID'].tolist()],
                placeholder='Type or select Customer ID...',
                style={'flex': '3', 'marginRight': '10px'}
            ),
            html.Button('Search', id='search-button', n_clicks=0,
                       style={'flex': '1', 'backgroundColor': '#2E86AB', 'color': 'white', 'border': 'none', 'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer'})
        ], style={'display': 'flex', 'marginBottom': '30px'}),

        html.Div(id='customer-profile-content')
    ])

    return search_section


def render_insights(rfm_df):
    """Business Insights and Action Plans"""

    # Calculate key insights
    total_revenue = rfm_df['Monetary'].sum()

    if 'Churn_Risk_Level' in rfm_df.columns:
        high_risk_revenue = rfm_df[rfm_df['Churn_Risk_Level'].isin(['High', 'Critical'])]['Monetary'].sum()
        high_risk_count = len(rfm_df[rfm_df['Churn_Risk_Level'].isin(['High', 'Critical'])])
    else:
        high_risk_revenue = 0
        high_risk_count = 0

    if 'RFM_Segment' in rfm_df.columns:
        champions = rfm_df[rfm_df['RFM_Segment'] == 'Champions']
        champions_revenue = champions['Monetary'].sum() if len(champions) > 0 else 0
    else:
        champions_revenue = 0

    # Executive summary
    summary = html.Div([
        html.H2('Executive Summary', style={'color': '#2E86AB', 'marginBottom': '20px'}),
        html.Div([
            html.P([
                html.Strong('Total Revenue: '),
                f'₦{total_revenue/1e9:.2f}B across {len(rfm_df):,} customers'
            ]),
            html.P([
                html.Strong('Revenue at Risk: '),
                f'₦{high_risk_revenue/1e9:.2f}B from {high_risk_count:,} high-risk customers'
            ]),
            html.P([
                html.Strong('Champions Revenue: '),
                f'₦{champions_revenue/1e9:.2f}B ({(champions_revenue/total_revenue)*100:.1f}% of total)'
            ]),
        ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '30px'})
    ])

    # Revenue opportunities
    opportunities = html.Div([
        html.H3('💰 Revenue Opportunities', style={'marginBottom': '20px'}),
        html.Div([
            create_opportunity_card('Save High-Risk VIPs', f'₦{high_risk_revenue * 0.3 / 1e9:.2f}B', 'Win back 30% of at-risk customers', '90 days'),
            create_opportunity_card('Protect Champions', f'₦{champions_revenue / 1e9:.2f}B', 'Maintain VIP retention at 95%', 'Ongoing'),
            create_opportunity_card('Cross-Sell', '₦0.42B', 'Equipment to feed buyers', '6 months'),
            create_opportunity_card('Upsell', '₦0.30B', 'Premium product bundles', '12 months'),
        ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))', 'gap': '20px', 'marginBottom': '30px'})
    ])

    # Action plan
    action_plan = html.Div([
        html.H3('📋 Phased Action Plan', style={'marginBottom': '20px'}),

        create_phase_card('Week 1: Emergency Response', [
            f'Contact {high_risk_count:,} high-risk customers',
            'Launch win-back campaign with 15-20% discounts',
            'Personal calls to top 100 VIP customers',
            'Set up dedicated support hotline'
        ], 'danger'),

        create_phase_card('Month 1: Stabilization', [
            'Implement VIP loyalty program',
            'Deploy personalized recommendations',
            'Launch cross-sell campaigns',
            'Weekly customer health monitoring'
        ], 'warning'),

        create_phase_card('Quarter 1: Growth', [
            'Scale automated campaigns',
            'Expand product recommendation coverage',
            'Launch referral program',
            'Monthly model retraining'
        ], 'success'),

        create_phase_card('Year 1: Transformation', [
            'Achieve 65% reduction in churn',
            'Increase CLV by 25%',
            'Grow active customers to 35%',
            'Full CRM integration'
        ], 'info')
    ])

    # Expected impact
    impact = html.Div([
        html.H3('📈 Expected Impact (12 Months)', style={'marginBottom': '20px'}),
        dash_table.DataTable(
            data=[
                {'Metric': 'Revenue', 'Current': f'₦{total_revenue/1e9:.2f}B', 'Target': f'₦{total_revenue*1.23/1e9:.2f}B', 'Improvement': '+23%'},
                {'Metric': 'Active Customers', 'Current': f'{len(rfm_df[rfm_df["Recency"] <= 90]):,}', 'Target': '1,100+', 'Improvement': '+175%'},
                {'Metric': 'Churn Rate', 'Current': f'{(rfm_df["Is_Churned"].sum() / len(rfm_df)) * 100:.1f}%', 'Target': '65%', 'Improvement': '-22.2%'},
                {'Metric': 'Avg CLV', 'Current': f'₦{rfm_df["Predicted_CLV"].mean()/1e6:.2f}M', 'Target': f'₦{rfm_df["Predicted_CLV"].mean()*1.25/1e6:.2f}M', 'Improvement': '+25%'},
            ],
            columns=[{'name': i, 'id': i} for i in ['Metric', 'Current', 'Target', 'Improvement']],
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={'backgroundColor': '#2E86AB', 'color': 'white', 'fontWeight': 'bold'},
            style_data_conditional=[
                {'if': {'column_id': 'Improvement'}, 'color': '#28a745', 'fontWeight': 'bold'}
            ]
        )
    ])

    return html.Div([
        summary,
        opportunities,
        action_plan,
        impact
    ])


def render_roi_calculator(rfm_df):
    """ROI Calculator"""

    calculator = html.Div([
        html.H2('ROI Calculator', style={'color': '#2E86AB', 'marginBottom': '20px'}),

        html.Div([
            html.Div([
                html.H4('Input Parameters', style={'marginBottom': '15px'}),
                html.Div([
                    html.Label('Campaign Budget (₦ Millions)'),
                    dcc.Input(id='campaign-budget', type='number', value=50, style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}),

                    html.Label('Expected Win-Back Rate (%)'),
                    dcc.Input(id='winback-rate', type='number', value=30, style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}),

                    html.Label('Expected Retention Increase (%)'),
                    dcc.Input(id='retention-increase', type='number', value=15, style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}),

                    html.Label('Campaign Duration (Months)'),
                    dcc.Input(id='campaign-duration', type='number', value=12, style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}),

                    html.Button('Calculate ROI', id='calculate-roi', n_clicks=0,
                               style={'width': '100%', 'backgroundColor': '#28a745', 'color': 'white', 'border': 'none', 'padding': '12px', 'borderRadius': '5px', 'cursor': 'pointer', 'fontWeight': 'bold'})
                ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'borderRadius': '10px'})
            ], style={'flex': '1'}),

            html.Div([
                html.H4('Projected Results', style={'marginBottom': '15px'}),
                html.Div(id='roi-results', style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'borderRadius': '10px', 'minHeight': '400px'})
            ], style={'flex': '2'})
        ], style={'display': 'flex', 'gap': '30px'})
    ])

    return calculator


# Helper functions for creating UI components
def create_kpi_card(title, value, icon, color):
    return html.Div([
        html.Div([
            html.Span(icon, style={'fontSize': '2rem', 'marginRight': '10px'}),
            html.Div([
                html.P(title, style={'margin': '0', 'fontSize': '0.9rem', 'color': '#666'}),
                html.P(value, style={'margin': '0', 'fontSize': '1.5rem', 'fontWeight': 'bold', 'color': color})
            ])
        ], style={'display': 'flex', 'alignItems': 'center'})
    ], style={
        'backgroundColor': '#f8f9fa',
        'padding': '20px',
        'borderRadius': '10px',
        'border': f'3px solid {color}',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
    })


def create_alert(title, message, alert_type):
    colors = {
        'danger': {'bg': '#f8d7da', 'border': '#dc3545'},
        'warning': {'bg': '#fff3cd', 'border': '#ffc107'},
        'success': {'bg': '#d4edda', 'border': '#28a745'},
        'info': {'bg': '#d1ecf1', 'border': '#17a2b8'}
    }
    color = colors.get(alert_type, colors['info'])

    return html.Div([
        html.Strong(title),
        html.P(message, style={'margin': '5px 0 0 0'})
    ], style={
        'backgroundColor': color['bg'],
        'borderLeft': f'4px solid {color["border"]}',
        'padding': '15px',
        'borderRadius': '5px'
    })


def create_opportunity_card(title, value, description, timeline):
    return html.Div([
        html.H4(title, style={'color': '#2E86AB', 'marginBottom': '10px'}),
        html.P(value, style={'fontSize': '2rem', 'fontWeight': 'bold', 'color': '#28a745', 'margin': '10px 0'}),
        html.P(description, style={'color': '#666', 'marginBottom': '10px'}),
        html.P([html.Strong('Timeline: '), timeline], style={'color': '#999', 'fontSize': '0.9rem'})
    ], style={
        'backgroundColor': '#f8f9fa',
        'padding': '20px',
        'borderRadius': '10px',
        'border': '2px solid #28a745',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
    })


def create_phase_card(title, items, card_type):
    colors = {
        'danger': '#dc3545',
        'warning': '#ffc107',
        'success': '#28a745',
        'info': '#17a2b8'
    }
    color = colors.get(card_type, colors['info'])

    return html.Div([
        html.H4(title, style={'color': color, 'marginBottom': '15px'}),
        html.Ul([html.Li(item) for item in items])
    ], style={
        'backgroundColor': '#f8f9fa',
        'padding': '20px',
        'borderRadius': '10px',
        'borderLeft': f'5px solid {color}',
        'marginBottom': '20px'
    })


# Chart creation functions
def create_segment_distribution_chart(rfm_df):
    if 'RFM_Segment' not in rfm_df.columns:
        return go.Figure()

    segment_counts = rfm_df['RFM_Segment'].value_counts().sort_values(ascending=True)

    fig = go.Figure(go.Bar(
        x=segment_counts.values,
        y=segment_counts.index,
        orientation='h',
        marker=dict(color='#2E86AB')
    ))

    fig.update_layout(
        title='Customer Distribution by RFM Segment',
        xaxis_title='Number of Customers',
        yaxis_title='Segment',
        template='plotly_white',
        height=400
    )

    return fig


def create_revenue_by_segment_chart(rfm_df):
    if 'RFM_Segment' not in rfm_df.columns:
        return go.Figure()

    segment_revenue = rfm_df.groupby('RFM_Segment')['Monetary'].sum().sort_values(ascending=True) / 1e6

    fig = go.Figure(go.Bar(
        x=segment_revenue.values,
        y=segment_revenue.index,
        orientation='h',
        marker=dict(color='#28a745')
    ))

    fig.update_layout(
        title='Revenue by RFM Segment (₦ Millions)',
        xaxis_title='Revenue (₦M)',
        yaxis_title='Segment',
        template='plotly_white',
        height=400
    )

    return fig


def create_churn_risk_chart(rfm_df):
    if 'Churn_Risk_Level' not in rfm_df.columns:
        return go.Figure()

    risk_counts = rfm_df['Churn_Risk_Level'].value_counts()

    colors = {'Low': '#28a745', 'Medium': '#ffc107', 'High': '#fd7e14', 'Critical': '#dc3545'}
    bar_colors = [colors.get(level, '#666') for level in risk_counts.index]

    fig = go.Figure(go.Bar(
        x=risk_counts.index,
        y=risk_counts.values,
        marker=dict(color=bar_colors)
    ))

    fig.update_layout(
        title='Churn Risk Distribution',
        xaxis_title='Risk Level',
        yaxis_title='Number of Customers',
        template='plotly_white',
        height=400
    )

    return fig


def create_clv_distribution_chart(rfm_df):
    if 'Predicted_CLV' not in rfm_df.columns:
        return go.Figure()

    clv_data = rfm_df[rfm_df['Predicted_CLV'] > 0]['Predicted_CLV'] / 1e6

    fig = go.Figure(go.Histogram(
        x=clv_data,
        nbinsx=50,
        marker=dict(color='#6f42c1')
    ))

    fig.update_layout(
        title='Customer Lifetime Value Distribution',
        xaxis_title='CLV (₦ Millions)',
        yaxis_title='Number of Customers',
        template='plotly_white',
        height=400
    )

    return fig


def create_churn_probability_dist(rfm_df):
    if 'Churn_Probability' not in rfm_df.columns:
        return go.Figure()

    fig = px.histogram(
        rfm_df,
        x='Churn_Probability',
        nbins=50,
        title='Churn Probability Distribution',
        labels={'Churn_Probability': 'Churn Probability'},
        color_discrete_sequence=['#dc3545']
    )

    fig.update_layout(template='plotly_white', height=400)
    return fig


def create_churn_risk_level_chart(rfm_df):
    if 'Churn_Risk_Level' not in rfm_df.columns:
        return go.Figure()

    risk_counts = rfm_df['Churn_Risk_Level'].value_counts()

    colors = {'Low': '#28a745', 'Medium': '#ffc107', 'High': '#fd7e14', 'Critical': '#dc3545'}
    pie_colors = [colors.get(level, '#666') for level in risk_counts.index]

    fig = go.Figure(go.Pie(
        labels=risk_counts.index,
        values=risk_counts.values,
        marker=dict(colors=pie_colors)
    ))

    fig.update_layout(
        title='Churn Risk Level Distribution',
        template='plotly_white',
        height=400
    )

    return fig


def create_churn_by_segment_chart(rfm_df):
    if 'RFM_Segment' not in rfm_df.columns or 'Churn_Probability' not in rfm_df.columns:
        return go.Figure()

    fig = px.box(
        rfm_df,
        x='RFM_Segment',
        y='Churn_Probability',
        title='Churn Probability by Segment',
        color='RFM_Segment'
    )

    fig.update_layout(
        template='plotly_white',
        showlegend=False,
        height=400
    )

    return fig


def create_clv_scatter(rfm_df):
    if 'Churn_Probability' not in rfm_df.columns or 'Predicted_CLV' not in rfm_df.columns:
        return go.Figure()

    sample_df = rfm_df.sample(min(1000, len(rfm_df)))

    fig = px.scatter(
        sample_df,
        x='Churn_Probability',
        y='Predicted_CLV',
        color='Customer_Priority' if 'Customer_Priority' in sample_df.columns else None,
        size='Monetary' if 'Monetary' in sample_df.columns else None,
        hover_data=['Customer_ID'],
        title='CLV vs Churn Risk Matrix',
        labels={'Churn_Probability': 'Churn Probability', 'Predicted_CLV': 'Predicted CLV (₦)'}
    )

    fig.update_layout(template='plotly_white', height=500)
    fig.update_yaxes(type='log')

    return fig


def create_clv_priority_matrix(rfm_df):
    if 'Customer_Priority' not in rfm_df.columns:
        return go.Figure()

    priority_counts = rfm_df['Customer_Priority'].value_counts()

    colors = {'Critical': '#dc3545', 'High': '#fd7e14', 'Medium': '#ffc107', 'Low': '#28a745'}
    pie_colors = [colors.get(p, '#666') for p in priority_counts.index]

    fig = go.Figure(go.Pie(
        labels=priority_counts.index,
        values=priority_counts.values,
        marker=dict(colors=pie_colors)
    ))

    fig.update_layout(
        title='Customer Priority Distribution',
        template='plotly_white',
        height=500
    )

    return fig


def create_timing_status_chart(rfm_df):
    if 'Purchase_Timing_Status' not in rfm_df.columns:
        return go.Figure()

    timing_counts = rfm_df['Purchase_Timing_Status'].value_counts()

    fig = go.Figure(go.Pie(
        labels=timing_counts.index,
        values=timing_counts.values
    ))

    fig.update_layout(
        title='Purchase Timing Status Distribution',
        template='plotly_white',
        height=400
    )

    return fig


def create_days_to_next_purchase_chart(rfm_df):
    if 'Days_To_Next_Purchase' not in rfm_df.columns:
        return go.Figure()

    days_data = rfm_df[rfm_df['Days_To_Next_Purchase'] > 0]['Days_To_Next_Purchase']

    fig = go.Figure(go.Histogram(
        x=days_data,
        nbinsx=30,
        marker=dict(color='#17a2b8')
    ))

    fig.update_layout(
        title='Days Until Next Purchase Distribution',
        xaxis_title='Days',
        yaxis_title='Number of Customers',
        template='plotly_white',
        height=400
    )

    return fig


def create_top_recommended_categories(recommendations_df):
    if 'Recommended_Category' not in recommendations_df.columns:
        return go.Figure()

    top_cats = recommendations_df['Recommended_Category'].value_counts().head(10).sort_values(ascending=True)

    fig = go.Figure(go.Bar(
        x=top_cats.values,
        y=top_cats.index,
        orientation='h',
        marker=dict(color='#6f42c1')
    ))

    fig.update_layout(
        title='Top 10 Recommended Categories',
        xaxis_title='Number of Recommendations',
        yaxis_title='Category',
        template='plotly_white',
        height=400
    )

    return fig


def create_recommendation_method_chart(recommendations_df):
    if 'Reason' not in recommendations_df.columns:
        return go.Figure()

    method_counts = recommendations_df['Reason'].value_counts()

    fig = go.Figure(go.Pie(
        labels=method_counts.index,
        values=method_counts.values
    ))

    fig.update_layout(
        title='Recommendation Methods Used',
        template='plotly_white',
        height=400
    )

    return fig


def create_confidence_distribution(recommendations_df):
    if 'Confidence' not in recommendations_df.columns:
        return go.Figure()

    fig = go.Figure(go.Histogram(
        x=recommendations_df['Confidence'],
        nbinsx=30,
        marker=dict(color='#20c997')
    ))

    fig.update_layout(
        title='Recommendation Confidence Distribution',
        xaxis_title='Confidence Score',
        yaxis_title='Number of Recommendations',
        template='plotly_white',
        height=400
    )

    return fig


def create_high_risk_table(rfm_df):
    if 'Churn_Risk_Level' not in rfm_df.columns:
        return html.Div("No churn risk data available")

    high_risk = rfm_df[rfm_df['Churn_Risk_Level'].isin(['High', 'Critical'])].nlargest(20, 'Monetary')

    if len(high_risk) == 0:
        return html.Div("No high-risk customers found")

    table_data = high_risk[['Customer_ID', 'RFM_Segment', 'Monetary', 'Churn_Probability', 'Churn_Risk_Level', 'Predicted_CLV']].copy()
    table_data['Monetary'] = table_data['Monetary'].apply(lambda x: f'₦{x/1e6:.2f}M')
    table_data['Predicted_CLV'] = table_data['Predicted_CLV'].apply(lambda x: f'₦{x/1e6:.2f}M')
    table_data['Churn_Probability'] = table_data['Churn_Probability'].apply(lambda x: f'{x:.2%}')

    return dash_table.DataTable(
        data=table_data.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in table_data.columns],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': '#dc3545', 'color': 'white', 'fontWeight': 'bold'},
        style_data_conditional=[
            {'if': {'filter_query': '{Churn_Risk_Level} = "Critical"'}, 'backgroundColor': '#f8d7da'}
        ],
        page_size=20
    )


def create_top_clv_table(rfm_df):
    if 'Predicted_CLV' not in rfm_df.columns:
        return html.Div("No CLV data available")

    top_clv = rfm_df.nlargest(20, 'Predicted_CLV')

    table_data = top_clv[['Customer_ID', 'RFM_Segment', 'Monetary', 'Predicted_CLV', 'Churn_Risk_Level', 'Customer_Priority']].copy()
    table_data['Monetary'] = table_data['Monetary'].apply(lambda x: f'₦{x/1e6:.2f}M')
    table_data['Predicted_CLV'] = table_data['Predicted_CLV'].apply(lambda x: f'₦{x/1e6:.2f}M')

    return dash_table.DataTable(
        data=table_data.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in table_data.columns],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': '#28a745', 'color': 'white', 'fontWeight': 'bold'},
        page_size=20
    )


def create_due_soon_table(rfm_df):
    if 'Purchase_Timing_Status' not in rfm_df.columns:
        return html.Div("No timing data available")

    due_soon = rfm_df[rfm_df['Purchase_Timing_Status'] == 'Due Soon'].nlargest(20, 'Predicted_CLV')

    if len(due_soon) == 0:
        return html.Div("No customers due to purchase soon")

    table_data = due_soon[['Customer_ID', 'RFM_Segment', 'Days_To_Next_Purchase', 'Predicted_CLV', 'Monetary']].copy()
    table_data['Monetary'] = table_data['Monetary'].apply(lambda x: f'₦{x/1e6:.2f}M')
    table_data['Predicted_CLV'] = table_data['Predicted_CLV'].apply(lambda x: f'₦{x/1e6:.2f}M')

    return dash_table.DataTable(
        data=table_data.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in table_data.columns],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': '#17a2b8', 'color': 'white', 'fontWeight': 'bold'},
        page_size=20
    )


# Callbacks for segment analysis
@callback(
    [Output('segment-summary-table', 'children'),
     Output('segment-count-chart', 'figure'),
     Output('segment-revenue-chart', 'figure'),
     Output('segment-rfm-heatmap', 'figure'),
     Output('segment-clv-box', 'figure'),
     Output('segment-dropdown', 'options')],
    [Input('segment-type-radio', 'value'),
     State('data-store', 'data')]
)
def update_segment_analysis(segment_col, data):
    if data is None or not data:
        return html.Div("No data"), go.Figure(), go.Figure(), go.Figure(), go.Figure(), []

    rfm_df = pd.DataFrame(data['rfm'])

    if segment_col not in rfm_df.columns:
        return html.Div(f"Column {segment_col} not found"), go.Figure(), go.Figure(), go.Figure(), go.Figure(), []

    # Segment summary table
    segment_summary = rfm_df.groupby(segment_col).agg({
        'Customer_ID': 'count',
        'Monetary': ['sum', 'mean'],
        'Frequency': 'mean',
        'Recency': 'mean',
        'Predicted_CLV': 'mean' if 'Predicted_CLV' in rfm_df.columns else 'count'
    }).round(2)

    segment_summary.columns = ['Customers', 'Total Revenue', 'Avg Revenue', 'Avg Frequency', 'Avg Recency', 'Avg CLV']
    segment_summary = segment_summary.sort_values('Total Revenue', ascending=False)
    segment_summary['Total Revenue'] = segment_summary['Total Revenue'].apply(lambda x: f'₦{x/1e9:.2f}B')
    segment_summary['Avg Revenue'] = segment_summary['Avg Revenue'].apply(lambda x: f'₦{x/1e6:.2f}M')
    segment_summary['Avg CLV'] = segment_summary['Avg CLV'].apply(lambda x: f'₦{x/1e6:.2f}M')
    segment_summary = segment_summary.reset_index()

    summary_table = dash_table.DataTable(
        data=segment_summary.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in segment_summary.columns],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': '#2E86AB', 'color': 'white', 'fontWeight': 'bold'},
        style_data_conditional=[
            {'if': {'row_index': 0}, 'backgroundColor': '#d4edda'}
        ]
    )

    # Count chart
    segment_counts = rfm_df[segment_col].value_counts().sort_values(ascending=True)
    count_fig = go.Figure(go.Bar(
        x=segment_counts.values,
        y=segment_counts.index,
        orientation='h',
        marker=dict(color='#2E86AB')
    ))
    count_fig.update_layout(
        title=f'Customer Count by {segment_col}',
        xaxis_title='Number of Customers',
        yaxis_title='Segment',
        template='plotly_white'
    )

    # Revenue chart
    segment_revenue = rfm_df.groupby(segment_col)['Monetary'].sum().sort_values(ascending=True) / 1e6
    revenue_fig = go.Figure(go.Bar(
        x=segment_revenue.values,
        y=segment_revenue.index,
        orientation='h',
        marker=dict(color='#28a745')
    ))
    revenue_fig.update_layout(
        title=f'Revenue by {segment_col} (₦ Millions)',
        xaxis_title='Revenue (₦M)',
        yaxis_title='Segment',
        template='plotly_white'
    )

    # RFM Heatmap
    rfm_avg = rfm_df.groupby(segment_col)[['Recency', 'Frequency', 'Monetary']].mean()
    heatmap_fig = go.Figure(go.Heatmap(
        z=rfm_avg.T.values,
        x=rfm_avg.index,
        y=rfm_avg.columns,
        colorscale='RdYlGn_r',
        text=rfm_avg.T.values.round(0),
        texttemplate='%{text}',
        textfont={"size": 10}
    ))
    heatmap_fig.update_layout(
        title=f'RFM Metrics Heatmap by {segment_col}',
        xaxis_title='Segment',
        yaxis_title='Metric',
        template='plotly_white'
    )

    # CLV Box plot
    if 'Predicted_CLV' in rfm_df.columns:
        clv_fig = px.box(
            rfm_df,
            x=segment_col,
            y='Predicted_CLV',
            title=f'CLV Distribution by {segment_col}',
            color=segment_col
        )
        clv_fig.update_layout(template='plotly_white', showlegend=False)
        clv_fig.update_yaxes(type='log')
    else:
        clv_fig = go.Figure()

    # Dropdown options
    dropdown_options = [{'label': seg, 'value': seg} for seg in rfm_df[segment_col].unique()]

    return summary_table, count_fig, revenue_fig, heatmap_fig, clv_fig, dropdown_options


@callback(
    Output('segment-details-content', 'children'),
    [Input('segment-dropdown', 'value'),
     Input('segment-type-radio', 'value'),
     State('data-store', 'data')]
)
def update_segment_details(segment, segment_col, data):
    if data is None or not data or segment is None:
        return html.Div("Select a segment to view details")

    rfm_df = pd.DataFrame(data['rfm'])
    segment_data = rfm_df[rfm_df[segment_col] == segment]

    if len(segment_data) == 0:
        return html.Div("No data for selected segment")

    # Calculate metrics
    total_customers = len(segment_data)
    total_revenue = segment_data['Monetary'].sum()
    avg_frequency = segment_data['Frequency'].mean()
    avg_recency = segment_data['Recency'].mean()
    avg_clv = segment_data['Predicted_CLV'].mean() if 'Predicted_CLV' in segment_data.columns else 0
    churn_rate = (segment_data['Is_Churned'].sum() / len(segment_data)) * 100 if 'Is_Churned' in segment_data.columns else 0

    # Details card
    details = html.Div([
        html.H3(f'{segment} - Segment Details', style={'color': '#2E86AB', 'marginBottom': '20px'}),

        html.Div([
            create_kpi_card('Customers', f'{total_customers:,}', '👥', '#17a2b8'),
            create_kpi_card('Total Revenue', f'₦{total_revenue/1e9:.2f}B', '💰', '#28a745'),
            create_kpi_card('Avg Frequency', f'{avg_frequency:.1f}', '🔄', '#6f42c1'),
            create_kpi_card('Avg Recency', f'{avg_recency:.0f} days', '📅', '#fd7e14'),
            create_kpi_card('Avg CLV', f'₦{avg_clv/1e6:.2f}M', '📊', '#20c997'),
            create_kpi_card('Churn Rate', f'{churn_rate:.1f}%', '⚠️', '#dc3545'),
        ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))', 'gap': '20px', 'marginBottom': '30px'}),

        # Top customers in segment
        html.H4('Top 10 Customers in Segment', style={'marginBottom': '15px'}),
        dash_table.DataTable(
            data=segment_data.nlargest(10, 'Monetary')[['Customer_ID', 'Monetary', 'Frequency', 'Recency']].to_dict('records'),
            columns=[
                {'name': 'Customer ID', 'id': 'Customer_ID'},
                {'name': 'Revenue (₦)', 'id': 'Monetary'},
                {'name': 'Frequency', 'id': 'Frequency'},
                {'name': 'Recency (days)', 'id': 'Recency'}
            ],
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={'backgroundColor': '#2E86AB', 'color': 'white', 'fontWeight': 'bold'}
        )
    ])

    return details


@callback(
    Output('customer-rec-content', 'children'),
    [Input('rec-customer-dropdown', 'value'),
     State('data-store', 'data')]
)
def update_customer_recommendations(customer_id, data):
    if data is None or not data or customer_id is None:
        return html.Div("Select a customer to view recommendations")

    recommendations_df = pd.DataFrame(data['recommendations'])
    customer_recs = recommendations_df[recommendations_df['Customer_ID'] == customer_id]

    if len(customer_recs) == 0:
        return html.Div(f"No recommendations found for Customer {customer_id}")

    return html.Div([
        html.H4(f'Recommendations for Customer {customer_id}', style={'marginBottom': '15px'}),
        dash_table.DataTable(
            data=customer_recs[['Recommended_Category', 'Confidence', 'Reason']].to_dict('records'),
            columns=[
                {'name': 'Product Category', 'id': 'Recommended_Category'},
                {'name': 'Confidence', 'id': 'Confidence'},
                {'name': 'Method', 'id': 'Reason'}
            ],
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={'backgroundColor': '#6f42c1', 'color': 'white', 'fontWeight': 'bold'},
            page_size=10
        )
    ])


@callback(
    Output('customer-profile-content', 'children'),
    [Input('search-button', 'n_clicks'),
     State('search-customer-dropdown', 'value'),
     State('data-store', 'data')]
)
def search_customer(n_clicks, customer_id, data):
    if n_clicks == 0 or customer_id is None or data is None or not data:
        return html.Div("Enter a Customer ID and click Search")

    rfm_df = pd.DataFrame(data['rfm'])
    recommendations_df = pd.DataFrame(data['recommendations'])

    customer = rfm_df[rfm_df['Customer_ID'] == customer_id]

    if len(customer) == 0:
        return html.Div(f"Customer {customer_id} not found", style={'color': '#dc3545', 'fontWeight': 'bold'})

    customer = customer.iloc[0]
    customer_recs = recommendations_df[recommendations_df['Customer_ID'] == customer_id]

    # Customer profile
    profile = html.Div([
        html.H2(f'Customer Profile: {customer_id}', style={'color': '#2E86AB', 'marginBottom': '20px'}),

        # Basic info
        html.Div([
            html.H3('Basic Information', style={'marginBottom': '15px'}),
            html.Div([
                create_kpi_card('RFM Segment', customer.get('RFM_Segment', 'N/A'), '🏷️', '#17a2b8'),
                create_kpi_card('Total Revenue', f'₦{customer["Monetary"]/1e6:.2f}M', '💰', '#28a745'),
                create_kpi_card('Purchase Frequency', f'{customer["Frequency"]:.0f}', '🔄', '#6f42c1'),
                create_kpi_card('Days Since Last Purchase', f'{customer["Recency"]:.0f}', '📅', '#fd7e14'),
            ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))', 'gap': '20px', 'marginBottom': '30px'})
        ]),

        # Predictions
        html.Div([
            html.H3('Predictions & Risk', style={'marginBottom': '15px'}),
            html.Div([
                create_kpi_card('Predicted CLV', f'₦{customer.get("Predicted_CLV", 0)/1e6:.2f}M', '📊', '#20c997') if 'Predicted_CLV' in customer else None,
                create_kpi_card('Churn Probability', f'{customer.get("Churn_Probability", 0):.2%}', '⚠️', '#dc3545') if 'Churn_Probability' in customer else None,
                create_kpi_card('Risk Level', customer.get('Churn_Risk_Level', 'N/A'), '🚨', '#fd7e14') if 'Churn_Risk_Level' in customer else None,
                create_kpi_card('Priority', customer.get('Customer_Priority', 'N/A'), '⭐', '#ffc107') if 'Customer_Priority' in customer else None,
            ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))', 'gap': '20px', 'marginBottom': '30px'})
        ]),

        # Recommendations
        html.Div([
            html.H3('Product Recommendations', style={'marginBottom': '15px'}),
            dash_table.DataTable(
                data=customer_recs[['Recommended_Category', 'Confidence', 'Reason']].to_dict('records') if len(customer_recs) > 0 else [],
                columns=[
                    {'name': 'Product Category', 'id': 'Recommended_Category'},
                    {'name': 'Confidence', 'id': 'Confidence'},
                    {'name': 'Method', 'id': 'Reason'}
                ],
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={'backgroundColor': '#6f42c1', 'color': 'white', 'fontWeight': 'bold'},
                page_size=5
            ) if len(customer_recs) > 0 else html.P("No recommendations available for this customer")
        ]),

        # Action items
        html.Div([
            html.H3('Recommended Actions', style={'marginBottom': '15px'}),
            html.Ul([
                html.Li(f"Contact within {customer.get('Days_To_Next_Purchase', 'N/A')} days" if 'Days_To_Next_Purchase' in customer else "Monitor activity"),
                html.Li(f"Offer personalized recommendations from {len(customer_recs)} suggested categories" if len(customer_recs) > 0 else "Collect more data for recommendations"),
                html.Li("Priority intervention required" if customer.get('Churn_Risk_Level') in ['High', 'Critical'] else "Regular engagement"),
                html.Li("VIP treatment" if customer.get('RFM_Segment') == 'Champions' else "Standard service")
            ])
        ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'borderRadius': '10px', 'marginTop': '20px'})
    ])

    return profile


@callback(
    Output('roi-results', 'children'),
    [Input('calculate-roi', 'n_clicks'),
     State('campaign-budget', 'value'),
     State('winback-rate', 'value'),
     State('retention-increase', 'value'),
     State('campaign-duration', 'value'),
     State('data-store', 'data')]
)
def calculate_roi(n_clicks, budget, winback_rate, retention_increase, duration, data):
    if n_clicks == 0 or data is None or not data:
        return html.Div("Enter parameters and click Calculate ROI")

    rfm_df = pd.DataFrame(data['rfm'])

    # Calculate potential revenue
    if 'Churn_Risk_Level' in rfm_df.columns:
        high_risk_revenue = rfm_df[rfm_df['Churn_Risk_Level'].isin(['High', 'Critical'])]['Predicted_CLV'].sum()
        winback_revenue = (high_risk_revenue * (winback_rate / 100))
    else:
        winback_revenue = 0

    total_clv = rfm_df['Predicted_CLV'].sum() if 'Predicted_CLV' in rfm_df.columns else 0
    retention_revenue = (total_clv * (retention_increase / 100))

    total_benefit = winback_revenue + retention_revenue
    budget_millions = budget * 1e6
    net_benefit = total_benefit - budget_millions
    roi_ratio = total_benefit / budget_millions if budget_millions > 0 else 0

    results = html.Div([
        html.H4('Projected Results', style={'color': '#28a745', 'marginBottom': '20px'}),

        html.Div([
            html.Div([
                html.P('Win-Back Revenue', style={'fontSize': '0.9rem', 'color': '#666', 'margin': '0'}),
                html.P(f'₦{winback_revenue/1e9:.2f}B', style={'fontSize': '2rem', 'fontWeight': 'bold', 'color': '#28a745', 'margin': '10px 0'})
            ], style={'flex': '1', 'textAlign': 'center'}),
            html.Div([
                html.P('Retention Revenue', style={'fontSize': '0.9rem', 'color': '#666', 'margin': '0'}),
                html.P(f'₦{retention_revenue/1e9:.2f}B', style={'fontSize': '2rem', 'fontWeight': 'bold', 'color': '#17a2b8', 'margin': '10px 0'})
            ], style={'flex': '1', 'textAlign': 'center'}),
        ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}),

        html.Hr(),

        html.Div([
            html.Div([
                html.P('Total Benefit', style={'fontSize': '0.9rem', 'color': '#666', 'margin': '0'}),
                html.P(f'₦{total_benefit/1e9:.2f}B', style={'fontSize': '2.5rem', 'fontWeight': 'bold', 'color': '#28a745', 'margin': '10px 0'})
            ], style={'textAlign': 'center', 'marginBottom': '20px'}),

            html.Div([
                html.P('Campaign Budget', style={'fontSize': '0.9rem', 'color': '#666', 'margin': '0'}),
                html.P(f'₦{budget:.0f}M', style={'fontSize': '1.5rem', 'fontWeight': 'bold', 'color': '#dc3545', 'margin': '10px 0'})
            ], style={'textAlign': 'center', 'marginBottom': '20px'}),

            html.Div([
                html.P('Net Benefit', style={'fontSize': '0.9rem', 'color': '#666', 'margin': '0'}),
                html.P(f'₦{net_benefit/1e9:.2f}B', style={'fontSize': '2rem', 'fontWeight': 'bold', 'color': '#6f42c1', 'margin': '10px 0'})
            ], style={'textAlign': 'center', 'marginBottom': '20px'}),

            html.Div([
                html.P('ROI Ratio', style={'fontSize': '0.9rem', 'color': '#666', 'margin': '0'}),
                html.P(f'{roi_ratio:.1f}x', style={'fontSize': '3rem', 'fontWeight': 'bold', 'color': '#fd7e14', 'margin': '10px 0'})
            ], style={'textAlign': 'center'})
        ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'borderRadius': '10px'}),

        html.Div([
            html.H5('Summary', style={'marginTop': '20px', 'marginBottom': '10px'}),
            html.P(f'For every ₦1 invested, you could generate ₦{roi_ratio:.2f} in return over {duration} months.'),
            html.P(f'This represents a {((roi_ratio - 1) * 100):.1f}% return on investment.'),
            html.P('Note: Results are projections based on model predictions and historical data.',
                  style={'fontSize': '0.8rem', 'color': '#999', 'fontStyle': 'italic', 'marginTop': '20px'})
        ])
    ])

    return results


# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8050)
