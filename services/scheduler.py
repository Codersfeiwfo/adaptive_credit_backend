from typing import Dict, List
import numpy as np
from datetime import datetime, timedelta

class RepaymentScheduler:
    def __init__(self, total_amount: float, term_months: int):
        self.total_amount = total_amount
        self.term_months = term_months
    
    def generate_schedule(self, income_pattern: Dict) -> List[Dict]:
        """
        Generate a flexible repayment schedule based on income patterns.
        
        Args:
            income_pattern: Dictionary containing income patterns and season information
            
        Returns:
            List of monthly repayment records
        """
        monthly_avg = income_pattern['monthly_averages']
        high_season = income_pattern['high_season_months']
        low_season = income_pattern['low_season_months']
        
        # Calculate base monthly payment
        base_payment = self.total_amount / self.term_months
        
        # Generate schedule
        schedule = []
        current_date = datetime.now()
        remaining_amount = self.total_amount
        
        for month in range(self.term_months):
            payment_date = current_date + timedelta(days=30 * month)
            month_number = payment_date.month
            
            # Adjust payment based on season
            if month_number in high_season:
                payment = base_payment * 1.2  # 20% higher in high season
            elif month_number in low_season:
                payment = base_payment * 0.8  # 20% lower in low season
            else:
                payment = base_payment
            
            # Ensure we don't exceed remaining amount
            payment = min(payment, remaining_amount)
            remaining_amount -= payment
            
            schedule.append({
                'date': payment_date.strftime('%Y-%m-%d'),
                'payment': round(payment, 2),
                'remaining_balance': round(remaining_amount, 2),
                'season': 'high' if month_number in high_season else 'low'
            })
            
            if remaining_amount <= 0:
                break
        
        return schedule
    
    def calculate_metrics(self, schedule: List[Dict]) -> Dict:
        """
        Calculate key metrics for the repayment schedule.
        
        Args:
            schedule: List of monthly repayment records
            
        Returns:
            Dictionary containing schedule metrics
        """
        payments = [record['payment'] for record in schedule]
        
        return {
            'total_payments': sum(payments),
            'average_payment': np.mean(payments),
            'min_payment': min(payments),
            'max_payment': max(payments),
            'completion_date': schedule[-1]['date'],
            'total_months': len(schedule)
        } 