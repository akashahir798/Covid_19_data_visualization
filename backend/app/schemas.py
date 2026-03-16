"""
Pydantic Schemas for Request/Response Validation

Defines data models for API request/response handling.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


# Country Schemas
class CountryBase(BaseModel):
    """Base country schema."""
    code: str = Field(..., max_length=3)
    name: str = Field(..., max_length=255)
    population: Optional[int] = None
    continent: Optional[str] = None


class CountryCreate(CountryBase):
    """Schema for creating a country."""
    pass


class Country(CountryBase):
    """Schema for country response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# COVID Data Schemas
class CovidDataBase(BaseModel):
    """Base COVID data schema."""
    country_code: str = Field(..., max_length=3)
    country_name: Optional[str] = None
    date: date
    
    confirmed_cases: int = 0
    new_cases: int = 0
    deaths: int = 0
    new_deaths: int = 0
    recovered: int = 0
    new_recovered: int = 0
    active_cases: int = 0
    total_vaccinations: int = 0
    people_vaccinated: int = 0
    people_fully_vaccinated: int = 0
    vaccination_rate: float = 0.0


class CovidDataCreate(CovidDataBase):
    """Schema for creating COVID data entry."""
    pass


class CovidData(CovidDataBase):
    """Schema for COVID data response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Global Summary Schemas
class GlobalSummaryBase(BaseModel):
    """Base global summary schema."""
    date: date
    total_confirmed: int = 0
    total_deaths: int = 0
    total_recovered: int = 0
    total_active: int = 0
    total_vaccinations: int = 0
    new_cases: int = 0
    new_deaths: int = 0
    new_recovered: int = 0


class GlobalSummary(GlobalSummaryBase):
    """Schema for global summary response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Prediction Schemas
class PredictionBase(BaseModel):
    """Base prediction schema."""
    country_code: str = Field(..., max_length=3)
    prediction_date: date
    target_date: date
    predicted_cases: Optional[float] = None
    predicted_deaths: Optional[float] = None
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    model_type: str = "linear_regression"
    accuracy_score: Optional[float] = None


class PredictionCreate(PredictionBase):
    """Schema for creating prediction."""
    pass


class Prediction(PredictionBase):
    """Schema for prediction response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = TimeSeriesResponse


class TimeSeriesResponse(BaseModel):
    """Schema for time series data response."""
    country: str
    country_code: str
    data: List[CovidData]
    
    class Config:
        from_attributes = True


class TopCountry(BaseModel):
    """Schema for top country response."""
    country_code: str
    country_name: str
    total_cases: int
    total_deaths: int
    total_recovered: int
    total_vaccinations: int
    mortality_rate: float


class PredictionResponse(BaseModel):
    """Schema for prediction response."""
    country: str
    country_code: str
    historical_data: List[CovidData]
    predictions: List[PredictionBase]
    model_accuracy: Optional[float] = None
    
    class Config:
        from_attributes = True
