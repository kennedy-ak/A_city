# Afrimash Customer Intelligence Platform Architecture

## System Architecture Diagram

```mermaid
graph TB
    subgraph Output["🎯 OUTPUT LAYER - Business Users"]
        sales[👥 Sales Team Portal<br/>Customer Alerts & Actions]
        marketing[📧 Marketing Automation<br/>Campaign Targeting]
        exec[📊 Executive Dashboard<br/>KPIs & Strategic Insights]
    end

    subgraph Application["💻 APPLICATION LAYER - User Interface"]
        dashboard[🖥️ Streamlit Dashboard<br/>10 Interactive Pages<br/>50+ Visualizations]
        api[🔌 FastAPI Service<br/>REST API Endpoints<br/>Real-time Predictions]
        crm[🔗 CRM Integration<br/>Salesforce | HubSpot<br/>Data Synchronization]
    end

    subgraph Models["🧠 MODEL LAYER - AI & Machine Learning"]
        churn[🔴 Churn Prediction<br/>Gradient Boosting Classifier<br/>✓ Accuracy: 93.4%<br/>✓ AUC-ROC: 0.979]
        clv[💰 CLV Prediction<br/>Gradient Boosting Regressor<br/>✓ R² Score: 0.896<br/>✓ MAE: ₦127,450]
        timing[⏰ Purchase Timing<br/>Pattern-based Algorithm<br/>✓ Accuracy: 85.2%<br/>✓ Real-time Analysis]
        recom[🎯 Recommendation Engine<br/>Collaborative Filtering<br/>✓ Precision@10: 72%<br/>✓ 4,984 Recommendations]
    end

    subgraph Processing["⚙️ PROCESSING LAYER - Data Engineering"]
        feature[🔧 Feature Engineering<br/>RFM Calculation<br/>Segmentation<br/>Clustering]
        pipeline[📊 Data Pipeline<br/>ETL Processing<br/>Data Cleaning<br/>Validation]
        rules[📋 Business Rules<br/>Risk Categorization<br/>Value Scoring<br/>Segment Assignment]
    end

    subgraph Data["💾 DATA LAYER - Storage"]
        trans[(📦 Transaction Data<br/>Purchase History<br/>Order Details<br/>Revenue Records)]
        rfm[(📈 RFM Dataset<br/>Recency, Frequency<br/>Monetary Metrics<br/>Customer Behavior)]
        master[(👤 Customer Master<br/>Demographics<br/>Contact Information<br/>Segment Data)]
    end

    %% Data Flow: Data to Processing
    trans -->|Raw Transactions| pipeline
    rfm -->|Customer Metrics| pipeline
    master -->|Profile Data| pipeline
    pipeline -->|Cleaned Data| feature
    feature -->|Engineered Features| rules

    %% Processing to Models
    rules -->|Training Data| churn
    rules -->|Training Data| clv
    rules -->|Training Data| timing
    rules -->|Training Data| recom

    %% Models to Application
    churn -->|Predictions| dashboard
    clv -->|Predictions| dashboard
    timing -->|Predictions| dashboard
    recom -->|Recommendations| dashboard

    churn -->|API Response| api
    clv -->|API Response| api
    timing -->|API Response| api
    recom -->|API Response| api

    dashboard -->|Integration| crm
    api -->|Data Sync| crm

    %% Application to Output
    dashboard -->|Insights| sales
    dashboard -->|Reports| marketing
    dashboard -->|Analytics| exec

    crm -->|Customer Data| sales
    api -->|Automated Actions| marketing

    %% Styling
    style Data fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#000
    style Processing fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#000
    style Models fill:#e8f5e9,stroke:#388e3c,stroke-width:3px,color:#000
    style Application fill:#fff3e0,stroke:#f57c00,stroke-width:3px,color:#000
    style Output fill:#ffebee,stroke:#c62828,stroke-width:3px,color:#000

    style churn fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#000
    style clv fill:#c8e6c9,stroke:#388e3c,stroke-width:2px,color:#000
    style timing fill:#fff9c4,stroke:#f57c00,stroke-width:2px,color:#000
    style recom fill:#bbdefb,stroke:#1976d2,stroke-width:2px,color:#000

    style dashboard fill:#ffe0b2,stroke:#e65100,stroke-width:2px,color:#000
    style api fill:#b3e5fc,stroke:#01579b,stroke-width:2px,color:#000
    style crm fill:#f8bbd0,stroke:#880e4f,stroke-width:2px,color:#000
```

## Technology Stack

| Layer | Technologies | Purpose |
|-------|-------------|---------|
| **Data Layer** | PostgreSQL, CSV Files | Store customer and transaction data |
| **Processing** | Python, Pandas, NumPy | ETL and feature engineering |
| **Models** | Scikit-learn, Gradient Boosting | Predictive analytics and ML |
| **Application** | Streamlit, FastAPI, Plotly | User interface and API services |
| **Output** | Web Dashboard, REST API | Business intelligence delivery |

## Key Metrics

- **Total Customers Analyzed:** 3,122
- **Churn Prediction Accuracy:** 93.4%
- **CLV Model R² Score:** 0.896
- **Recommendations Generated:** 4,984
- **Revenue at Risk Identified:** ₦1.81B
- **Projected ROI:** 15-20x

## Data Flow

1. **Data Collection** → Transaction and customer data feeds into the data layer
2. **Processing** → ETL pipelines clean and engineer features
3. **Model Training** → ML models trained on processed data
4. **Prediction** → Real-time predictions generated for customers
5. **Delivery** → Insights delivered via dashboard and API
6. **Action** → Business users take data-driven actions

## Deployment Options

### Option 1: Cloud Deployment (Recommended)
- **Platform:** AWS, GCP, or Azure
- **Cost:** $500-1,000/month
- **Timeline:** 2-4 weeks
- **Scalability:** High

### Option 2: On-Premise
- **Requirements:** 8 CPU cores, 32GB RAM, 500GB SSD
- **Cost:** Hardware + maintenance
- **Timeline:** 4-6 weeks
- **Scalability:** Medium

## How to View This Diagram

### Method 1: GitHub
1. Copy this file to your GitHub repository
2. View on GitHub - it will automatically render the Mermaid diagram

### Method 2: Mermaid Live Editor
1. Go to https://mermaid.live
2. Copy the Mermaid code above
3. Paste into the editor
4. Export as PNG/SVG

### Method 3: VS Code
1. Install "Markdown Preview Mermaid Support" extension
2. Open this file in VS Code
3. Click "Preview" button
4. Diagram renders automatically

### Method 4: Export as Image
1. Use Mermaid Live Editor (https://mermaid.live)
2. Click "Actions" → "PNG" or "SVG"
3. Download high-resolution image
4. Use in presentations

## Architecture Layers Explained

### 1. Data Layer (Blue)
Foundation layer storing all raw data from Afrimash's operations. Includes transaction history, customer profiles, and calculated RFM metrics.

### 2. Processing Layer (Purple)
Handles all data transformation, cleaning, and feature engineering. Prepares data for machine learning models through ETL processes.

### 3. Model Layer (Green)
Core intelligence layer with 4 trained ML models providing predictions and recommendations. Each model optimized for specific business needs.

### 4. Application Layer (Orange)
User-facing applications including interactive dashboard, REST API for integrations, and CRM connectors for seamless workflow integration.

### 5. Output Layer (Red)
Business user interfaces tailored for different stakeholders - sales teams, marketing, and executives - each with role-specific insights.

---

**Built with:** Python | Streamlit | Scikit-learn | Plotly | Pandas
**Version:** 1.0
**Last Updated:** October 2025
**Status:** Production Ready ✅
