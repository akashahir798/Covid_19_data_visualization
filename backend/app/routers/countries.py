"""
Countries Router

Provides endpoints for country-specific COVID-19 data.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import date, timedelta

from app.database import get_db
from app.models import CovidData, Country

router = APIRouter()


@router.get("/countries")
async def get_countries(
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get list of all countries with COVID-19 data.
    
    Args:
        search: Optional search filter by country name
        limit: Maximum number of results
        offset: Pagination offset
    
    Returns:
        List of countries with basic information
    """
    query = db.query(
        CovidData.country_code,
        CovidData.country_name,
        func.max(CovidData.confirmed_cases).label("total_cases"),
        func.max(CovidData.deaths).label("total_deaths"),
        func.max(CovidData.recovered).label("total_recovered"),
    ).group_by(CovidData.country_code, CovidData.country_name)
    
    if search:
        query = query.filter(CovidData.country_name.ilike(f"%{search}%"))
    
    results = query.order_by(func.max(CovidData.confirmed_cases).desc()).offset(offset).limit(limit).all()
    
    return {
        "total": len(results),
        "data": [
            {
                "code": r.country_code,
                "name": r.country_name,
                "total_cases": r.total_cases or 0,
                "total_deaths": r.total_deaths or 0,
                "total_recovered": r.total_recovered or 0
            }
            for r in results
        ]
    }


@router.get("/countries/{country_code}")
async def get_country_data(
    country_code: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed COVID-19 data for a specific country.
    
    Args:
        country_code: ISO 3166-1 alpha-3 country code
    
    Returns:
        Country details with latest statistics
    """
    # Get latest data for country
    latest = db.query(CovidData).filter(
        CovidData.country_code == country_code.upper()
    ).order_by(CovidData.date.desc()).first()
    
    if not latest:
        raise HTTPException(
            status_code=404,
            detail=f"Country with code '{country_code}' not found"
        )
    
    # Get country metadata
    country_info = db.query(Country).filter(
        Country.code == country_code.upper()
    ).first()
    
    return {
        "code": latest.country_code,
        "name": latest.country_name,
        "population": country_info.population if country_info else None,
        "continent": country_info.continent if country_info else None,
        "latest_date": latest.date.isoformat(),
        "statistics": {
            "confirmed_cases": latest.confirmed_cases,
            "new_cases": latest.new_cases,
            "deaths": latest.deaths,
            "new_deaths": latest.new_deaths,
            "recovered": latest.recovered,
            "new_recovered": latest.new_recovered,
            "active_cases": latest.active_cases,
            "total_vaccinations": latest.total_vaccinations,
            "people_vaccinated": latest.people_vaccinated,
            "people_fully_vaccinated": latest.people_fully_vaccinated,
            "vaccination_rate": latest.vaccination_rate
        }
    }


@router.get("/top-countries")
async def get_top_countries(
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("cases", regex="^(cases|deaths|recovered|vaccinations)$"),
    db: Session = Depends(get_db)
):
    """
    Get top countries by COVID-19 metrics.
    
    Args:
        limit: Number of countries to return
        sort_by: Metric to sort by (cases, deaths, recovered, vaccinations)
    
    Returns:
        List of top countries with their statistics
    """
    sort_column = {
        "cases": CovidData.confirmed_cases,
        "deaths": CovidData.deaths,
        "recovered": CovidData.recovered,
        "vaccinations": CovidData.total_vaccinations
    }.get(sort_by, CovidData.confirmed_cases)
    
    # Get latest data for each country
    subquery = db.query(
        CovidData.country_code,
        func.max(CovidData.date).label("max_date")
    ).group_by(CovidData.country_code).subquery()
    
    results = db.query(
        CovidData.country_code,
        CovidData.country_name,
        CovidData.confirmed_cases,
        CovidData.deaths,
        CovidData.recovered,
        CovidData.total_vaccinations,
        CovidData.population,
    ).join(
        subquery,
        CovidData.country_code == subquery.c.country_code
    ).filter(
        CovidData.date == subquery.c.max_date
    ).order_by(sort_column.desc()).limit(limit).all()
    
    return {
        "sort_by": sort_by,
        "data": [
            {
                "code": r.country_code,
                "name": r.country_name,
                "total_cases": r.confirmed_cases or 0,
                "total_deaths": r.deaths or 0,
                "total_recovered": r.recovered or 0,
                "total_vaccinations": r.total_vaccinations or 0,
                "mortality_rate": round((r.deaths / r.confirmed_cases * 100) if r.confirmed_cases else 0, 2)
            }
            for r in results
        ]
    }


@router.get("/map-data")
async def get_map_data(db: Session = Depends(get_db)):
    """
    Get data for world map visualization.
    
    Returns:
        List of countries with coordinates and case counts
    """
    # Get latest data for each country
    subquery = db.query(
        CovidData.country_code,
        func.max(CovidData.date).label("max_date")
    ).group_by(CovidData.country_code).subquery()
    
    results = db.query(
        CovidData.country_code,
        CovidData.country_name,
        CovidData.confirmed_cases,
        CovidData.deaths,
    ).join(
        subquery,
        CovidData.country_code == subquery.c.country_code
    ).filter(
        CovidData.date == subquery.c.max_date
    ).all()
    
    # Country code to coordinates mapping (ISO 3 to lat/lon)
    country_coords = {
        "USA": {"lat": 37.0902, "lon": -95.7129},
        "BRA": {"lat": -14.2350, "lon": -51.9253},
        "IND": {"lat": 20.5937, "lon": 78.9629},
        "FRA": {"lat": 46.2276, "lon": 2.2137},
        "TUR": {"lat": 38.9637, "lon": 35.2433},
        "GBR": {"lat": 55.3781, "lon": -3.4360},
        "RUS": {"lat": 61.5240, "lon": 105.3188},
        "ITA": {"lat": 41.8719, "lon": 12.5674},
        "DEU": {"lat": 51.1657, "lon": 10.4515},
        "ESP": {"lat": 40.4637, "lon": -3.7492},
        "MEX": {"lat": 23.6345, "lon": -102.5528},
        "POL": {"lat": 51.9194, "lon": 19.1451},
        "COL": {"lat": 4.5709, "lon": -74.2973},
        "ARG": {"lat": -38.4161, "lon": -63.6167},
        "ZAF": {"lat": -30.5595, "lon": 22.9375},
        "CHN": {"lat": 35.8617, "lon": 104.1954},
        "JPN": {"lat": 36.2048, "lon": 138.2529},
        "AUS": {"lat": -25.2744, "lon": 133.7751},
        "CAN": {"lat": 56.1304, "lon": -106.3468},
        "IDN": {"lat": -0.7893, "lon": 113.9213},
    }
    
    return {
        "data": [
            {
                "code": r.country_code,
                "name": r.country_name,
                "cases": r.confirmed_cases or 0,
                "deaths": r.deaths or 0,
                "lat": country_coords.get(r.country_code, {}).get("lat"),
                "lon": country_coords.get(r.country_code, {}).get("lon"),
            }
            for r in results
            if r.country_code in country_coords
        ]
    }
