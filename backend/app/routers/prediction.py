"""
Prediction Router

Provides endpoints for COVID-19 trend predictions using ML.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime, timedelta

from app.database import get_db
from app.models import CovidData, Prediction
from app.services.ml_service import predict_cases

router = APIRouter()


@router.get("/prediction/{country}")
async def get_prediction(
    country: str,
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """
    Get COVID-19 predictions for a specific country.
    
    Args:
        country: Country name or ISO code
        days: Number of days to predict (default: 30)
    
    Returns:
        Historical data and predictions
    """
    country_code = country.upper()
    
    # Find country
    country_data = db.query(CovidData).filter(
        CovidData.country_code == country_code
    ).order_by(CovidData.date.desc()).first()
    
    if not country_data:
        # Try searching by name
        country_data = db.query(CovidData).filter(
            CovidData.country_name.ilike(f"%{country}%")
        ).order_by(CovidData.date.desc()).first()
        
        if not country_data:
            raise HTTPException(
                status_code=404,
                detail=f"Country '{country}' not found"
            )
        
        country_code = country_data.country_code
    
    # Get historical data (last 90 days)
    start_date = date.today() - timedelta(days=90)
    historical = db.query(CovidData).filter(
        CovidData.country_code == country_code,
        CovidData.date >= start_date
    ).order_by(CovidData.date.asc()).all()
    
    if len(historical) < 7:
        raise HTTPException(
            status_code=400,
            detail="Not enough historical data for prediction (minimum 7 days required)"
        )
    
    # Generate predictions using ML service
    try:
        predictions = predict_cases(historical, days)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )
    
    # Save prediction to database
    prediction_records = []
    for pred in predictions:
        pred_record = Prediction(
            country_code=country_code,
            prediction_date=date.today(),
            target_date=pred["date"],
            predicted_cases=pred["predicted_cases"],
            predicted_deaths=pred.get("predicted_deaths"),
            lower_bound=pred.get("lower_bound"),
            upper_bound=pred.get("upper_bound"),
            model_type="linear_regression"
        )
        db.add(pred_record)
        prediction_records.append(pred_record)
    
    db.commit()
    
    return {
        "country": historical[0].country_name,
        "country_code": country_code,
        "prediction_days": days,
        "historical_data": [
            {
                "date": h.date.isoformat(),
                "cases": h.confirmed_cases,
                "new_cases": h.new_cases,
                "deaths": h.deaths
            }
            for h in historical
        ],
        "predictions": predictions,
        "model_info": {
            "type": "linear_regression",
            "training_data_points": len(historical)
        }
    }


@router.get("/prediction/{country}/accuracy")
async def get_model_accuracy(
    country: str,
    db: Session = Depends(get_db)
):
    """
    Get model accuracy metrics for a country.
    
    Args:
        country: Country name or ISO code
    
    Returns:
        Model accuracy metrics
    """
    country_code = country.upper()
    
    # Get historical predictions
    predictions = db.query(Prediction).filter(
        Prediction.country_code == country_code
    ).order_by(Prediction.target_date.desc()).limit(30).all()
    
    if not predictions:
        return {
            "message": "No predictions available for accuracy calculation",
            "accuracy": None
        }
    
    # Get actual values for comparison
    actual_values = db.query(CovidData).filter(
        CovidData.country_code == country_code,
        CovidData.date.in_([p.target_date for p in predictions])
    ).all()
    
    actual_dict = {a.date: a.confirmed_cases for a in actual_values}
    
    # Calculate accuracy (MAPE)
    errors = []
    for pred in predictions:
        if pred.target_date in actual_dict:
            actual = actual_dict[pred.target_date]
            if actual > 0:
                error = abs(pred.predicted_cases - actual) / actual
                errors.append(error)
    
    if errors:
        mape = sum(errors) / len(errors) * 100
        accuracy = max(0, 100 - mape)
    else:
        accuracy = None
    
    return {
        "country_code": country_code,
        "predictions_analyzed": len(errors),
        "accuracy_score": accuracy,
        "mean_absolute_percentage_error": mape if errors else None
    }


@router.get("/prediction/global")
async def get_global_predictions(
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """
    Get global COVID-19 predictions.
    
    Args:
        days: Number of days to predict
    
    Returns:
        Global predictions
    """
    # Aggregate historical global data
    start_date = date.today() - timedelta(days=90)
    
    all_data = db.query(CovidData).filter(
        CovidData.date >= start_date
    ).order_by(CovidData.date.asc()).all()
    
    # Aggregate by date
    daily_aggregates = {}
    for d in all_data:
        date_str = d.date.isoformat()
        if date_str not in daily_aggregates:
            daily_aggregates[date_str] = {
                "date": d.date,
                "confirmed_cases": 0,
                "deaths": 0
            }
        daily_aggregates[date_str]["confirmed_cases"] += d.confirmed_cases or 0
        daily_aggregates[date_str]["deaths"] += d.deaths or 0
    
    historical = list(daily_aggregates.values())
    
    if len(historical) < 7:
        raise HTTPException(
            status_code=400,
            detail="Not enough historical data for prediction"
        )
    
    # Generate predictions
    try:
        predictions = predict_cases(historical, days)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )
    
    return {
        "global": True,
        "prediction_days": days,
        "predictions": predictions
    }
