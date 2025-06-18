import pandas as pd
from typing import Dict, List
import numpy as np

class IncomeParser:
    @staticmethod
    def parse_csv(file_path: str) -> Dict:
        """
        Parse a CSV file containing income data.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Dict containing parsed income data and statistics
        """
        try:
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Validate and clean data
            df['month'] = pd.to_datetime(df['month'])
            df['income'] = pd.to_numeric(df['income'])
            
            # Calculate basic statistics
            stats = {
                'total_months': len(df),
                'average_income': df['income'].mean(),
                'min_income': df['income'].min(),
                'max_income': df['income'].max(),
                'std_income': df['income'].std()
            }
            
            # Identify seasonal patterns
            monthly_avg = df.groupby(df['month'].dt.month)['income'].mean()
            seasonal_pattern = monthly_avg.to_dict()
            
            return {
                'raw_data': df.to_dict(orient='records'),
                'statistics': stats,
                'seasonal_pattern': seasonal_pattern
            }
            
        except Exception as e:
            raise ValueError(f"Error parsing CSV file: {str(e)}")
    
    @staticmethod
    def detect_seasons(data: List[Dict]) -> Dict:
        """
        Detect high and low income seasons based on historical data.
        
        Args:
            data: List of monthly income records
            
        Returns:
            Dict containing season information
        """
        df = pd.DataFrame(data)
        monthly_avg = df.groupby(df['month'].dt.month)['income'].mean()
        
        # Define seasons based on income patterns
        high_season = monthly_avg[monthly_avg > monthly_avg.mean()].index.tolist()
        low_season = monthly_avg[monthly_avg <= monthly_avg.mean()].index.tolist()
        
        return {
            'high_season_months': high_season,
            'low_season_months': low_season,
            'monthly_averages': monthly_avg.to_dict()
        } 