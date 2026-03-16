"""
Data Service

Provides data processing and cleaning functions.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import date, datetime
import requests


def fetch_covid_data(source: str = "jhu") -> pd.DataFrame:
    """
    Fetch COVID-19 data from public sources.
    
    Args:
        source: Data source (jhu, owid)
    
    Returns:
        DataFrame with COVID data
    """
    if source == "jhu":
        # Johns Hopkins GitHub repository
        url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
        
        try:
            df = pd.read_csv(url)
            return df
        except Exception as e:
            print(f"Error fetching JHU data: {e}")
            return pd.DataFrame()
    
    return pd.DataFrame()


def clean_covid_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and preprocess COVID-19 data.
    
    Args:
        df: Raw DataFrame
    
    Returns:
        Cleaned DataFrame
    """
    if df.empty:
        return df
    
    # Rename columns
    df = df.rename(columns={
        'Province/State': 'province',
        'Country/Region': 'country',
        'Lat': 'lat',
        'Long': 'lon'
    })
    
    # Melt the dataframe (convert wide to long format)
    id_cols = ['province', 'country', 'lat', 'lon']
    date_cols = [col for col in df.columns if col not in id_cols]
    
    df_melted = df.melt(
        id_vars=id_cols,
        value_vars=date_cols,
        var_name='date_str',
        value_name='confirmed'
    )
    
    # Convert date
    df_melted['date'] = pd.to_datetime(df_melted['date_str'], format='%m/%d/%y').dt.date
    
    # Fill NaN values
    df_melted['province'] = df_melted['province'].fillna('')
    df_melted['confirmed'] = df_melted['confirmed'].fillna(0)
    
    # Aggregate by country (sum provinces)
    df_agg = df_melted.groupby(['country', 'date']).agg({
        'confirmed': 'sum',
        'lat': 'first',
        'lon': 'first'
    }).reset_index()
    
    # Sort by country and date
    df_agg = df_agg.sort_values(['country', 'date'])
    
    # Calculate daily new cases
    df_agg['new_cases'] = df_agg.groupby('country')['confirmed'].diff().fillna(0)
    df_agg['new_cases'] = df_agg['new_cases'].clip(lower=0)
    
    return df_agg


def generate_sample_data() -> List[Dict[str, Any]]:
    """
    Generate sample COVID-19 data for testing.
    
    Returns:
        List of sample data records
    """
    # Sample countries
    countries = [
        {"code": "USA", "name": "United States", "lat": 37.0902, "lon": -95.7129},
        {"code": "BRA", "name": "Brazil", "lat": -14.2350, "lon": -51.9253},
        {"code": "IND", "name": "India", "lat": 20.5937, "lon": 78.9629},
        {"code": "FRA", "name": "France", "lat": 46.2276, "lon": 2.2137},
        {"code": "TUR", "name": "Turkey", "lat": 38.9637, "lon": 35.2433},
        {"code": "GBR", "name": "United Kingdom", "lat": 55.3781, "lon": -3.4360},
        {"code": "RUS", "name": "Russia", "lat": 61.5240, "lon": 105.3188},
        {"code": "ITA", "name": "Italy", "lat": 41.8719, "lon": 12.5674},
        {"code": "DEU", "name": "Germany", "lat": 51.1657, "lon": 10.4515},
        {"code": "ESP", "name": "Spain", "lat": 40.4637, "lon": -3.7492},
        {"code": "CHN", "name": "China", "lat": 35.8617, "lon": 104.1954},
        {"code": "JPN", "name": "Japan", "lat": 36.2048, "lon": 138.2529},
        {"code": "AUS", "name": "Australia", "lat": -25.2744, "lon": 133.7751},
        {"code": "CAN", "name": "Canada", "lat": 56.1304, "lon": -106.3468},
        {"code": "MEX", "name": "Mexico", "lat": 23.6345, "lon": -102.5528},
    ]
    
    # Generate 90 days of data
    data = []
    start_date = date.today() - pd.Timedelta(days=90)
    
    for country in countries:
        cases = 100000 + np.random.randint(0, 100000)
        deaths = int(cases * 0.02)
        recovered = int(cases * 0.85)
        
        for day in range(90):
            current_date = start_date + pd.Timedelta(days=day)
            
            # Add some variation
            new_cases = np.random.randint(1000, 10000)
            new_deaths = int(new_cases * 0.02)
            new_recovered = int(new_cases * 0.9)
            
            cases += new_cases
            deaths += new_deaths
            recovered += new_recovered
            
            data.append({
                "country_code": country["code"],
                "country_name": country["name"],
                "date": current_date,
                "confirmed_cases": cases,
                "new_cases": new_cases,
                "deaths": deaths,
                "new_deaths": new_deaths,
                "recovered": recovered,
                "new_recovered": new_recovered,
                "active_cases": cases - deaths - recovered,
                "total_vaccinations": int(cases * 1.2),
                "people_vaccinated": int(cases * 0.6),
                "people_fully_vaccinated": int(cases * 0.4),
                "vaccination_rate": 0.6,
            })
    
    return data


def calculate_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate summary statistics from COVID data.
    
    Args:
        df: DataFrame with COVID data
    
    Returns:
        Dictionary with statistics
    """
    if df.empty:
        return {}
    
    return {
        "total_cases": int(df['confirmed_cases'].max()) if 'confirmed_cases' in df.columns else 0,
        "total_deaths": int(df['deaths'].max()) if 'deaths' in df.columns else 0,
        "total_recovered": int(df['recovered'].max()) if 'recovered' in df.columns else 0,
        "total_vaccinations": int(df['total_vaccinations'].max()) if 'total_vaccinations' in df.columns else 0,
        "latest_date": df['date'].max().isoformat() if 'date' in df.columns else None,
        "countries_count": df['country'].nunique() if 'country' in df.columns else 0
    }


def get_country_metadata() -> List[Dict[str, Any]]:
    """
    Get country metadata for mapping.
    
    Returns:
        List of country metadata
    """
    return [
        {"code": "USA", "name": "United States", "population": 331893745, "continent": "North America"},
        {"code": "BRA", "name": "Brazil", "population": 212559417, "continent": "South America"},
        {"code": "IND", "name": "India", "population": 1380004385, "continent": "Asia"},
        {"code": "FRA", "name": "France", "population": 67390000, "continent": "Europe"},
        {"code": "TUR", "name": "Turkey", "population": 84339067, "continent": "Europe/Asia"},
        {"code": "GBR", "name": "United Kingdom", "population": 67886011, "continent": "Europe"},
        {"code": "RUS", "name": "Russia", "population": 145934462, "continent": "Europe/Asia"},
        {"code": "ITA", "name": "Italy", "population": 60461826, "continent": "Europe"},
        {"code": "DEU", "name": "Germany", "population": 83783942, "continent": "Europe"},
        {"code": "ESP", "name": "Spain", "population": 46754778, "continent": "Europe"},
        {"code": "CHN", "name": "China", "population": 1439323776, "continent": "Asia"},
        {"code": "JPN", "name": "Japan", "population": 126476461, "continent": "Asia"},
        {"code": "AUS", "name": "Australia", "population": 25499884, "continent": "Oceania"},
        {"code": "CAN", "name": "Canada", "population": 37742154, "continent": "North America"},
        {"code": "MEX", "name": "Mexico", "population": 128932753, "continent": "North America"},
    ]
