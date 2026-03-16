"""
Time Series Router

Provides endpoints for COVID-19 time series data.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime, timedelta
from dateutil import parser

from app.database import get_db
from app.models import CovidData

router = APIRouter()


@router.get("/timeseries/{country}")
async def get_country_timeseries(
    country: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    metric: str = Query("cases", regex="^(cases|deaths|recovered|vaccinations)$"),
    db: Session = Depends(get_db)
):
    """
    Get time series data for a specific country.
    
    Args:
        country: Country name or ISO code
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        metric: Metric to retrieve (cases, deaths, recovered, vaccinations)
    
    Returns:
        Time series data for the country
    """
    country_code = country.upper()
    
    # Validate country exists
    country_data = db.query(CovidData).filter(
        CovidData.country_code == country_code
    ).first()
    
    if not country_data:
        # Try searching by name
        country_data = db.query(CovidData).filter(
            CovidData.country_name.ilike(f"%{country}%")
        ).first()
        
        if not country_data:
            raise HTTPException(
                status_code=404,
                detail=f"Country '{country}' not found"
            )
        
        country_code = country_data.country_code
    
    # Build query
    query = db.query(CovidData).filter(
        CovidData.country_code == country_code
    )
    
    # Apply date filters
    if start_date:
        try:
            start = parser.parse(start_date).date()
            query = query.filter(CovidData.date >= start)
        except ValueError:
            pass
    
    if end_date:
        try:
            end = parser.parse(end_date).date()
            query = query.filter(CovidData.date <= end)
        except ValueError:
            pass
    
    # Get data ordered by date
    results = query.order_by(CovidData.date.asc()).all()
    
    # Format data based on metric
    metric_map = {
        "cases": "confirmed_cases",
        "deaths": "deaths",
        "recovered": "recovered",
        "vaccinations": "total_vaccinations"
    }
    
    field = getattr(CovidData, metric_map.get(metric, "confirmed_cases"))
    
    return {
        "country": results[0].country_name if results else country_code,
        "country_code": country_code,
        "metric": metric,
        "data": [
            {
                "date": r.date.isoformat(),
                "value": getattr(r, metric_map.get(metric, "confirmed_cases")) or 0,
                "new_cases": r.new_cases or 0,
                "new_deaths": r.new_deaths or 0,
            }
            for r in results
        ]
    }


@router.get("/timeseries/{country}/comparison")
async def compare_countries(
    countries: str = Query(..., description="Comma-separated country codes"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    metric: str = Query("cases", regex="^(cases|deaths|recovered|vaccinations)$"),
    db: Session = Depends(get_db)
):
    """
    Compare time series data across multiple countries.
    
    Args:
        countries: Comma-separated country codes
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        metric: Metric to compare
    
    Returns:
        Comparison data for all countries
    """
    country_codes = [c.strip().upper() for c in countries.split(",")]
    
    metric_map = {
        "cases": "confirmed_cases",
        "deaths": "deaths",
        "recovered": "recovered",
        "vaccinations": "total_vaccinations"
    }
    
    # Build query for all countries
    query = db.query(CovidData).filter(
        CovidData.country_code.in_(country_codes)
    )
    
    if start_date:
        try:
            start = parser.parse(start_date).date()
            query = query.filter(CovidData.date >= start)
        except ValueError:
            pass
    
    if end_date:
        try:
            end = parser.parse(end_date).date()
            query = query.filter(CovidData.date <= end)
        except ValueError:
            pass
    
    results = query.order_by(CovidData.date.asc()).all()
    
    # Group by country
    data_by_country = {}
    for r in results:
        if r.country_code not in data_by_country:
            data_by_country[r.country_code] = {
                "code": r.country_code,
                "name": r.country_name,
                "data": []
            }
        
        data_by_country[r.country_code]["data"].append({
            "date": r.date.isoformat(),
            "value": getattr(r, metric_map.get(metric, "confirmed_cases")) or 0
        })
    
    return {
        "metric": metric,
        "countries": list(data_by_country.values())
    }


@router.get("/global/timeseries")
async def get_global_timeseries(
    days: int = Query(90, ge=1, le=365),
    metric: str = Query("cases", regex="^(cases|deaths|recovered)$"),
    db: Session = Depends(get_db)
):
    """
    Get global time series data.
    
    Args:
        days: Number of days to fetch
        metric: Metric to retrieve
    
    Returns:
        Global time series data
    """
    start_date = date.today() - timedelta(days=days)
    
    # Get all data for the period
    results = db.query(CovidData).filter(
        CovidData.date >= start_date
    ).order_by(CovidData.date.asc()).all()
    
    # Aggregate by date
    daily_data = {}
    for r in results:
        date_str = r.date.isoformat()
        if date_str not in daily_data:
            daily_data[date_str] = {
                "date": date_str,
                "confirmed": 0,
                "deaths": 0,
                "recovered": 0
            }
        
        daily_data[date_str]["confirmed"] += r.confirmed_cases or 0
        daily_data[date_str]["deaths"] += r.deaths or 0
        daily_data[date_str]["recovered"] += r.recovered or 0
    
    metric_key = {
        "cases": "confirmed",
        "deaths": "deaths",
        "recovered": "recovered"
    }.get(metric, "confirmed")
    
    return {
        "global": True,
        "metric": metric,
        "data": [
            {
                "date": d["date"],
                "value": d[metric_key]
            }
            for d in sorted(daily_data.values(), key=lambda x: x["date"])
        ]
    }
