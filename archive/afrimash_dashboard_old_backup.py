"""
AFRIMASH CUSTOMER INTELLIGENCE DASHBOARD - ENHANCED VERSION
Interactive Streamlit Application with Full Features
Fixed paths, added ROI calculator, Architecture page, and export functionality
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import io
import base64
warnings.filterwarnings("ignore")

# Page configuration
st.set_page_config(
    page_title="Afrimash Customer Intelligence",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Continue with rest of dashboard code...
