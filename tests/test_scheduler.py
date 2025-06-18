import pytest
from datetime import datetime
from ..services.scheduler import RepaymentScheduler

def test_scheduler_initialization():
    scheduler = RepaymentScheduler(total_amount=10000, term_months=12)
    assert scheduler.total_amount == 10000
    assert scheduler.term_months == 12

def test_generate_schedule():
    scheduler = RepaymentScheduler(total_amount=12000, term_months=12)
    income_pattern = {
        'monthly_averages': {1: 1000, 2: 2000, 3: 1500, 4: 2500},
        'high_season_months': [2, 4],
        'low_season_months': [1, 3]
    }
    
    schedule = scheduler.generate_schedule(income_pattern)
    
    # Basic validation
    assert len(schedule) == 12
    assert all('date' in record for record in schedule)
    assert all('payment' in record for record in schedule)
    assert all('remaining_balance' in record for record in schedule)
    assert all('season' in record for record in schedule)
    
    # Check total payments
    total_payments = sum(record['payment'] for record in schedule)
    assert abs(total_payments - 12000) < 0.01  # Allow for floating point errors

def test_calculate_metrics():
    scheduler = RepaymentScheduler(total_amount=12000, term_months=12)
    test_schedule = [
        {'payment': 1000, 'date': '2023-01-01'},
        {'payment': 1200, 'date': '2023-02-01'},
        {'payment': 800, 'date': '2023-03-01'}
    ]
    
    metrics = scheduler.calculate_metrics(test_schedule)
    
    assert metrics['total_payments'] == 3000
    assert metrics['average_payment'] == 1000
    assert metrics['min_payment'] == 800
    assert metrics['max_payment'] == 1200
    assert metrics['completion_date'] == '2023-03-01'
    assert metrics['total_months'] == 3 