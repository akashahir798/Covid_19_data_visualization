"""
Machine Learning Service

Provides COVID-19 prediction using simple linear regression.
"""

from typing import List, Dict, Any
from datetime import date, timedelta


def predict_cases(historical_data: List[Any], days_to_predict: int = 30) -> List[Dict[str, Any]]:
    """
    Generate predictions for COVID-19 cases using simple linear regression.
    """
    if not historical_data:
        raise ValueError("No historical data provided")
    
    # Prepare data
    dates = []
    cases = []
    
    for record in historical_data:
        if hasattr(record, 'date'):
            record_date = record.date
            record_cases = record.confirmed_cases or 0
        else:
            record_date = record.get('date')
            record_cases = record.get('confirmed_cases', 0) or record.get('cases', 0)
        
        if record_date:
            dates.append(record_date.toordinal())
            cases.append(record_cases)
    
    if not dates:
        raise ValueError("No valid dates in historical data")
    
    # Simple linear regression using least squares
    n = len(dates)
    sum_x = sum(dates)
    sum_y = sum(cases)
    sum_xy = sum(d * c for d, c in zip(dates, cases))
    sum_x2 = sum(d * d for d in dates)
    
    # Calculate slope and intercept
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x) if (n * sum_x2 - sum_x * sum_x) != 0 else 0
    intercept = (sum_y - slope * sum_x) / n
    
    # Generate future dates
    last_date = date.fromordinal(int(dates[-1]))
    predictions = []
    
    for i in range(1, days_to_predict + 1):
        future_date = last_date + timedelta(days=i)
        future_ordinal = future_date.toordinal()
        
        # Predict cases using linear regression
        predicted_cases = slope * future_ordinal + intercept
        
        # Ensure non-negative
        predicted_cases = max(0, predicted_cases)
        
        # Calculate confidence interval
        uncertainty = 0.05 * (1 + i / days_to_predict)
        
        lower_bound = predicted_cases * (1 - uncertainty)
        upper_bound = predicted_cases * (1 + uncertainty)
        
        predictions.append({
            "date": future_date.isoformat(),
            "predicted_cases": int(predicted_cases),
            "lower_bound": int(lower_bound),
            "upper_bound": int(upper_bound)
        })
    
    return predictions


def detect_trend(historical_data: List[Any]) -> Dict[str, Any]:
    """Detect trend direction in the data."""
    if not historical_data or len(historical_data) < 2:
        return {"trend": "insufficient_data", "slope": 0}
    
    cases = []
    for record in historical_data:
        if hasattr(record, 'confirmed_cases'):
            cases.append(record.confirmed_cases or 0)
        else:
            cases.append(record.get('confirmed_cases', 0))
    
    # Calculate simple trend
    first_half_avg = sum(cases[:len(cases)//2]) / (len(cases)//2) if len(cases) > 1 else cases[0]
    second_half_avg = sum(cases[len(cases)//2:]) / (len(cases) - len(cases)//2)
    
    if second_half_avg > first_half_avg * 1.1:
        trend = "increasing"
    elif second_half_avg < first_half_avg * 0.9:
        trend = "decreasing"
    else:
        trend = "stable"
    
    return {
        "trend": trend,
        "first_period_avg": first_half_avg,
        "second_period_avg": second_half_avg,
        "change_percentage": ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0
    }
