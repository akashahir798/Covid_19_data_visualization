"""
Global Summary Router

Provides endpoints for global COVID-19 statistics.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date, datetime, timedelta

from app.database import get_db
from app.models import CovidData, GlobalSummary

router = APIRouter()


@router.get("/summary")
async def get_global_summary(
    db: Session = Depends(get_db),
    date_filter: Optional[str] = None
):
    """
    Get global COVID-19 summary statistics.
    
    Returns:
        Dictionary containing global COVID-19 statistics
    """
    # Try to get from cached summary first
    if date_filter:
        try:
            target_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
            summary = db.query(GlobalSummary).filter(
                GlobalSummary.date == target_date
            ).first()
            
            if summary:
                return {
                    "date": summary.date.isoformat(),
                    "total_confirmed": summary.total_confirmed,
                    "total_deaths": summary.total_deaths,
                    "total_recovered": summary.total_recovered,
                    "total_active": summary.total_active,
                    "total_vaccinations": summary.total_vaccinations,
                    "new_cases": summary.new_cases,
                    "new_deaths": summary.new_deaths,
                    "new_recovered": summary.new_recovered
                }
        except ValueError:
            pass
    
    # Calculate from COVID data
    result = db.query(
        func.sum(CovidData.confirmed_cases).label("total_confirmed"),
        func.sum(CovidData.deaths).label("total_deaths"),
        func.sum(CovidData.recovered).label("total_recovered"),
        func.sum(CovidData.active_cases).label("total_active"),
        func.sum(CovidData.total_vaccinations).label("total_vaccinations"),
    ).first()
    
    # Get latest date
    latest = db.query(CovidData).order_by(CovidData.date.desc()).first()
    latest_date = latest.date if latest else date.today()
    
    # Get today's new cases
    today_new = db.query(
        func.sum(CovidData.new_cases).label("new_cases"),
        func.sum(CovidData.new_deaths).label("new_deaths"),
    ).filter(CovidData.date == latest_date).first()
    
    return {
        "date": latest_date.isoformat() if latest_date else date.today().isoformat(),
        "total_confirmed": result.total_confirmed or 0,
        "total_deaths": result.total_deaths or 0,
        "total_recovered": result.total_recovered or 0,
        "total_active": result.total_active or 0,
        "total_vaccinations": result.total_vaccinations or 0,
        "new_cases": today_new.new_cases or 0,
        "new_deaths": today_new.new_deaths or 0,
        "new_recovered": 0
    }


@router.get("/summary/historical")
async def get_historical_summary(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get historical global summary for the specified number of days.
    
    Args:
        days: Number of days to fetch (default: 30)
    
    Returns:
        List of daily global summaries
    """
    start_date = date.today() - timedelta(days=days)
    
    summaries = db.query(GlobalSummary).filter(
        GlobalSummary.date >= start_date
    ).order_by(GlobalSummary.date.asc()).all()
    
    return {
        "data": [
            {
                "date": s.date.isoformat(),
                "total_confirmed": s.total_confirmed,
                "total_deaths": s.total_deaths,
                "total_recovered": s.total_recovered,
                "new_cases": s.new_cases,
                "new_deaths": s.new_deaths
            }
            for s in summaries
        ]
    }
