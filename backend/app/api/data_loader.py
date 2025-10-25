"""
Data loading and caching utilities
"""

import pandas as pd
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """Handles loading and caching of data files"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize DataLoader
        
        Args:
            data_dir: Directory containing data files. If None, uses parent directory.
        """
        if data_dir is None:
            # Assume data files are in project root (3 levels up from this file)
            current_file = Path(__file__)
            self.data_dir = current_file.parent.parent.parent.parent
        else:
            self.data_dir = Path(data_dir)
        
        self._rfm_data: Optional[pd.DataFrame] = None
        self._transactions: Optional[pd.DataFrame] = None
        self._recommendations: Optional[pd.DataFrame] = None
        
        logger.info(f"DataLoader initialized with data directory: {self.data_dir}")
    
    def load_all_data(self) -> None:
        """Load all data files"""
        self.get_rfm_data()
        self.get_transactions()
        self.get_recommendations()
        logger.info("All data files loaded successfully")
    
    def get_rfm_data(self) -> pd.DataFrame:
        """Load and cache RFM data with predictions"""
        if self._rfm_data is None:
            file_path = self.data_dir / 'rfm_with_predictions.csv'
            logger.info(f"Loading RFM data from {file_path}")
            
            try:
                self._rfm_data = pd.read_csv(file_path)
                logger.info(f"Loaded {len(self._rfm_data)} customer records")
            except FileNotFoundError:
                logger.error(f"File not found: {file_path}")
                raise
            except Exception as e:
                logger.error(f"Error loading RFM data: {e}")
                raise
        
        return self._rfm_data
    
    def get_transactions(self) -> pd.DataFrame:
        """Load and cache transaction data"""
        if self._transactions is None:
            file_path = self.data_dir / 'transactions_clean.csv'
            logger.info(f"Loading transaction data from {file_path}")
            
            try:
                self._transactions = pd.read_csv(file_path)
                self._transactions['Date'] = pd.to_datetime(self._transactions['Date'])
                logger.info(f"Loaded {len(self._transactions)} transaction records")
            except FileNotFoundError:
                logger.error(f"File not found: {file_path}")
                raise
            except Exception as e:
                logger.error(f"Error loading transaction data: {e}")
                raise
        
        return self._transactions
    
    def get_recommendations(self) -> pd.DataFrame:
        """Load and cache product recommendations"""
        if self._recommendations is None:
            file_path = self.data_dir / 'product_recommendations.csv'
            logger.info(f"Loading recommendations from {file_path}")
            
            try:
                self._recommendations = pd.read_csv(file_path)
                logger.info(f"Loaded {len(self._recommendations)} recommendations")
            except FileNotFoundError:
                logger.error(f"File not found: {file_path}")
                raise
            except Exception as e:
                logger.error(f"Error loading recommendations: {e}")
                raise
        
        return self._recommendations
    
    def reload_data(self) -> None:
        """Force reload all data from disk"""
        logger.info("Reloading all data files")
        self._rfm_data = None
        self._transactions = None
        self._recommendations = None
        self.load_all_data()
    
    def get_customer(self, customer_id: str) -> Optional[pd.Series]:
        """Get a specific customer by ID"""
        rfm_data = self.get_rfm_data()
        customer = rfm_data[rfm_data['Customer_ID'] == customer_id]
        
        if customer.empty:
            return None
        
        return customer.iloc[0]
    
    def get_customers_by_segment(self, segment: str) -> pd.DataFrame:
        """Get all customers in a specific segment"""
        rfm_data = self.get_rfm_data()
        return rfm_data[rfm_data['RFM_Segment'] == segment]
    
    def get_high_risk_customers(self, top_n: int = 100) -> pd.DataFrame:
        """Get high-risk customers sorted by value"""
        rfm_data = self.get_rfm_data()
        high_risk = rfm_data[rfm_data['Churn_Risk_Level'].isin(['High', 'Critical'])]
        return high_risk.nlargest(top_n, 'Monetary')
    
    def get_high_value_customers(self, top_n: int = 100) -> pd.DataFrame:
        """Get highest CLV customers"""
        rfm_data = self.get_rfm_data()
        return rfm_data.nlargest(top_n, 'Predicted_CLV')

