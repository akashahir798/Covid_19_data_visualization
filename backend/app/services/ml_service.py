"""
Machine Learning Service

Provides COVID-19 prediction using Linear Regression and time series forecasting.
"""

import math
from typing import List, Dict, Any
from datetime import date, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures


def predict_cases(historical_data: List[Any], days_to_predict: int = 30) -> List[Dict[str, Any]]:
    """
    Generate predictions for COVID-19 cases using Linear Regression.
    
    Args:
        historical_data: List of COVID data objects with date and confirmed_cases
        days_to_predict: Number of days to predict ahead
    
    Returns:
        List of prediction dictionaries
    """
    if not historical_data:
        raise ValueError("No historical data provided")
    
    # Prepare data - convert dates to numeric features
    dates = []
    cases = []
    deaths = []
    
    for record in historical_data:
        if hasattr(record, 'date'):
            record_date = record.date
            record_cases = record.confirmed_cases or 0
            record_deaths = record.deaths or 0
        else:
            record_date = record.get('date')
            record_cases = record.get('confirmed_cases', 0) or record.get('cases', 0)
            record_deaths = record.get('deaths', 0)
        
        if record_date:
            # Convert date to days since first date
            if not dates:
                first_date = record_date
            days_diff = (record_date - (dates[0] if dates else record_date)).days if dates else 0
            
            # Use ordinal values for better linear fitting
            dates.append(record_date.toordinal())
            cases.append(record_cases)
            deaths.append(record_deaths)
    
    if not dates:
        raise ValueError("No valid dates in historical data")
    
    # Ensure we have a reference point
    first_date = min(dates)
    
    # Convert to numpy arrays
    X = [d for d in dates]
    y_cases = [c for c in cases]
    y_deaths = [d for d in deaths]
    
    # Train Linear Regression model for cases
    X_array = [[x] for x in X]
    y_cases_array = y_cases
    
    model_cases = LinearRegression()
    model_cases.fit(X_array, y_cases_array)
    
    # Calculate R² score for cases
    y_pred = model_cases.predict(X_array)
    ss_res = sum((y - y_pred[i]) ** 2 for i, y in enumerate(y_cases_array))
    ss_tot = sum((y - sum(y_cases_array)/len(y_cases_array)) ** 2 for y in y_cases_array)
    r2_cases = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    # Generate future dates
    last_date = date.fromordinal(int(dates[-1]))
    predictions = []
    
    for i in range(1, days_to_predict + 1):
        future_date = last_date + timedelta(days=i)
        future_ordinal = future_date.toordinal()
        
        # Predict cases
        predicted_cases = model_cases.predict([[future_ordinal]])[0]
        
        # Ensure non-negative
        predicted_cases = max(0, predicted_cases)
        
        # Calculate confidence interval (wider as we go further into future)
        uncertainty = 0.05 * (1 + i / days_to_predict)  # 5% + increasing uncertainty
        
        lower_bound = predicted_cases * (1 - uncertainty)
        upper_bound = predicted_cases * (1 + uncertainty)
        
        predictions.append({
            "date": future_date.isoformat(),
            "predicted_cases": int(predicted_cases),
            "lower_bound": int(lower_bound),
            "upper_bound": int(upper_bound)
        })
    
    return predictions


def predict_with_polynomial(historical_data: List[Any], degree: int = 2, days_to_predict: int = 30) -> List[Dict[str, Any]]:
    """
    Generate predictions using Polynomial Regression.
    
    Args:
        historical_data: List of COVID data objects
        degree: Polynomial degree
        days_to_predict: Number of days to predict
    
    Returns:
        List of prediction dictionaries
    """
    if not historical_data:
        raise ValueError("No historical data provided")
    
    dates = []
    cases = []
    
    for record in historical_data:
        if hasattr(record, 'date'):
            record_date = record.date
            record_cases = record.confirmed_cases or 0
        else:
            record_date = record.get('date')
            record_cases = record.get('confirmed_cases', 0)
        
        if record_date:
            dates.append(record_date.toordinal())
            cases.append(record_cases)
    
    if len(dates) < degree + 1:
        # Fall back to linear if not enough data
        return predict_cases(historical_data, days_to_predict)
    
    # Apply polynomial features
    X = [[d] for d in dates]
    y = cases
    
    # Train model
    model = LinearRegression()
    model.fit(X, y)
    
    # Generate predictions
    last_date = date.fromordinal(int(dates[-1]))
    predictions = []
    
    for i in range(1, days_to_predict + 1):
        future_date = last_date + timedelta(days=i)
        future_ordinal = future_date.toordinal()
        
        predicted_cases = model.predict([[future_ordinal]])[0]
        predicted_cases = max(0, predicted_cases)
        
        uncertainty = 0.08 * (1 + i / days_to_predict)
        
        predictions.append({
            "date": future_date.isoformat(),
            "predicted_cases": int(predicted_cases),
            "lower_bound": int(predicted_cases * (1 - uncertainty)),
            "upper_bound": int(predicted_cases * (1 + uncertainty))
        })
    
    return predictions


def calculate_moving_average(data: List[float], window: int = 7) -> List[float]:
    """
    Calculate moving average for smoothing data.
    
    Args:
        data: List of numeric values
        window: Window size for moving average
    
    Returns:
        List of smoothed values
    """
    if not data or window <= 0:
        return data
    
    result = []
    for i in range(len(data)):
        start = max(0, i - window + 1)
        window_data = data[start:i+1]
        result.append(sum(window_data) / len(window_data))
    
    return result


def detect_trend(historical_data: List[Any]) -> Dict[str, Any]:
    """
    Detect trend direction in the data.
    
    Args:
        historical_data: List of COVID data objects
    
    Returns:
        Dictionary with trend information
    """
    if not historical_data or len(historical_data) < 2:
        return {"trend": "insufficient_data", "slope": 0}
    
    cases = []
    for record in historical_data:
        if hasattr(record, 'confirmed_cases'):
            cases.append(record.confirmed_cases or 0)
        else:
            cases.append(record.get('confirmed_cases', 0))
    
    # Calculate simple trend using first and last values
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
