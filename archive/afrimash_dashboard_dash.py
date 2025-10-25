import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

# Load data
rfm_data = pd.read_csv('rfm_with_predictions.csv')
transactions = pd.read_csv('transactions_clean.csv')
transactions['Date'] = pd.to_datetime(transactions['Date'])
recommendations = pd.read_csv('product_recommendations.csv')

from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1('Afrimash Customer Intelligence Dashboard'),
    
    dcc.Tabs([
        dcc.Tab(label='Executive Dashboard', children=[
            # Key Metrics
            html.Div([
                html.Div([
                    html.H3('Total Customers'),
                    html.P(f"{len(rfm_data):,}")
                ], className='metric-card'),
                html.Div([
                    html.H3('Total Revenue'),
                    html.P(f"GH₵{rfm_data['Monetary'].sum()/1e9:.2f}B")
                ], className='metric-card'),
                html.Div([
                    html.H3('Churn Rate'),
                    html.P(f"{(rfm_data['Is_Churned'].sum() / len(rfm_data)) * 100:.1f}%")
                ], className='metric-card'),
                html.Div([
                    html.H3('Avg Customer CLV'),
                    html.P(f"GH₵{rfm_data['Predicted_CLV'].mean()/1e6:.2f}M")
                ], className='metric-card'),
                html.Div([
                    html.H3('At Risk Customers'),
                    html.P(f"{len(rfm_data[rfm_data['Churn_Risk_Level'].isin(['High', 'Critical'])]):,}")
                ], className='metric-card'),
            ], className='metrics-container'),
            
            # Charts
            html.Div([
                dcc.Graph(
                    id='rfm-segment-chart',
                    figure=px.bar(
                        rfm_data['RFM_Segment'].value_counts(),
                        x=rfm_data['RFM_Segment'].value_counts().values,
                        y=rfm_data['RFM_Segment'].value_counts().index,
                        orientation='h',
                        title='Customer Distribution by RFM Segment'
                    )
                ),
                dcc.Graph(
                    id='revenue-segment-chart',
                    figure=px.bar(
                        rfm_data.groupby('RFM_Segment')['Monetary'].sum().sort_values(ascending=True),
                        x=rfm_data.groupby('RFM_Segment')['Monetary'].sum().sort_values(ascending=True).values,
                        y=rfm_data.groupby('RFM_Segment')['Monetary'].sum().sort_values(ascending=True).index,
                        orientation='h',
                        title='Revenue by RFM Segment'
                    )
                ),
                dcc.Graph(
                    id='churn-risk-chart',
                    figure=px.bar(
                        rfm_data['Churn_Risk_Level'].value_counts(),
                        x=rfm_data['Churn_Risk_Level'].value_counts().index,
                        y=rfm_data['Churn_Risk_Level'].value_counts().values,
                        title='Churn Risk Distribution'
                    )
                ),
                dcc.Graph(
                    id='clv-dist-chart',
                    figure=px.histogram(
                        rfm_data[rfm_data['Predicted_CLV'] > 0],
                        x='Predicted_CLV',
                        nbins=50,
                        title='Customer Lifetime Value Distribution'
                    )
                ),
                dcc.Graph(
                    id='monthly-revenue-chart',
                    figure=px.line(
                        transactions.groupby(transactions['Date'].dt.to_period('M'))['Revenue'].sum().reset_index(),
                        x='Date',
                        y='Revenue',
                        title='Monthly Revenue Trend'
                    )
                )
            ], className='charts-container')
        ]),
        dcc.Tab(label='Customer Segments', children=[
            dcc.RadioItems(
                id='segment-type-radio',
                options=[
                    {'label': 'RFM Segments', 'value': 'RFM_Segment'},
                    {'label': 'K-Means Clusters', 'value': 'Cluster_Name'}
                ],
                value='RFM_Segment',
                labelStyle={'display': 'inline-block'}
            ),
            dcc.Graph(id='segment-summary-table'),
            dcc.Dropdown(
                id='segment-dropdown',
                options=[{'label': i, 'value': i} for i in rfm_data['RFM_Segment'].unique()],
                value=rfm_data['RFM_Segment'].unique()[0]
            ),
            html.Div(id='segment-details')
        ]),
        dcc.Tab(label='Predictive Analytics', children=[
            dcc.Tabs([
                dcc.Tab(label='Churn Prediction', children=[
                    dcc.Graph(
                        id='churn-dist-chart',
                        figure=px.histogram(
                            rfm_data,
                            x='Churn_Probability',
                            color='Churn_Risk_Level',
                            nbins=50,
                            title='Churn Risk Distribution'
                        )
                    )
                ]),
                dcc.Tab(label='CLV Prediction', children=[
                    dcc.Graph(
                        id='clv-scatter-chart',
                        figure=px.scatter(
                            rfm_data.sample(min(1000, len(rfm_data))),
                            x='Churn_Probability',
                            y='Predicted_CLV',
                            color='Customer_Priority',
                            size='Monetary',
                            hover_data=['Customer_ID', 'RFM_Segment', 'Monetary'],
                            log_y=True,
                            title='CLV vs Churn Risk Matrix'
                        )
                    )
                ]),
                dcc.Tab(label='Purchase Timing', children=[
                    dcc.Graph(
                        id='timing-dist-chart',
                        figure=px.pie(
                            rfm_data['Purchase_Timing_Status'].value_counts(),
                            values=rfm_data['Purchase_Timing_Status'].value_counts().values,
                            names=rfm_data['Purchase_Timing_Status'].value_counts().index,
                            title='Purchase Timing Status'
                        )
                    )
                ])
            ])
        ]),
        dcc.Tab(label='Recommendations', children=[
            dcc.Graph(
                id='top-recs-chart',
                figure=px.bar(
                    recommendations['Recommended_Category'].value_counts().head(10),
                    x=recommendations['Recommended_Category'].value_counts().head(10).values,
                    y=recommendations['Recommended_Category'].value_counts().head(10).index,
                    orientation='h',
                    title='Top Recommended Categories'
                )
            ),
            dcc.Graph(
                id='rec-method-chart',
                figure=px.pie(
                    recommendations['Reason'].value_counts(),
                    values=recommendations['Reason'].value_counts().values,
                    names=recommendations['Reason'].value_counts().index,
                    title='Recommendation Methods'
                )
            ),
            dcc.Dropdown(
                id='customer-dropdown',
                options=[{'label': i, 'value': i} for i in rfm_data['Customer_ID'].head(100)],
                value=rfm_data['Customer_ID'].head(100)[0]
            ),
            html.Div(id='customer-recs')
        ])
    ])
])

@app.callback(
    Output('segment-summary-table', 'figure'),
    [Input('segment-type-radio', 'value')])
def update_segment_table(segment_col):
    segment_summary = rfm_data.groupby(segment_col).agg({
        'Customer_ID': 'count',
        'Monetary': ['sum', 'mean'],
        'Frequency': 'mean',
        'Recency': 'mean',
        'Predicted_CLV': 'mean'
    }).round(2)
    
    segment_summary.columns = ['Customers', 'Total Revenue', 'Avg Revenue', 'Avg Frequency', 'Avg Recency', 'Avg CLV']
    segment_summary = segment_summary.sort_values('Total Revenue', ascending=False)
    
    return px.bar(segment_summary, x=segment_summary.index, y='Customers', title=f'Customer Distribution by {segment_col}')

@app.callback(
    Output('segment-dropdown', 'options'),
    [Input('segment-type-radio', 'value')])
def update_segment_dropdown_options(segment_col):
    return [{'label': i, 'value': i} for i in rfm_data[segment_col].unique()]

@app.callback(
    Output('segment-dropdown', 'value'),
    [Input('segment-dropdown', 'options')])
def update_segment_dropdown_value(options):
    return options[0]['value']

@app.callback(
    Output('segment-details', 'children'),
    [Input('segment-dropdown', 'value'),
     Input('segment-type-radio', 'value')])
def update_segment_details(segment, segment_col):
    segment_data = rfm_data[rfm_data[segment_col] == segment]
    
    return html.Div([
        html.H3(f'Details for {segment}'),
        html.P(f"Customers: {len(segment_data):,}"),
        html.P(f"Total Revenue: GH₵{segment_data['Monetary'].sum()/1e6:.1f}M"),
        html.P(f"Avg CLV: GH₵{segment_data['Predicted_CLV'].mean()/1e6:.2f}M"),
        html.P(f"Avg Churn Risk: {(segment_data['Churn_Probability'].mean()) * 100:.1f}%")
    ])

if __name__ == '__main__':
    app.run_server(debug=True)