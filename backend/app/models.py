"""
SQLAlchemy Database Models

Defines the database schema for COVID-19 data storage.
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text
from sqlalchemy.sql import func

from app.database import Base


class Country(Base):
    """Model for storing country information."""
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(3), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    population = Column(Integer)
    continent = Column(String(50))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class CovidData(Base):
    """Model for storing daily COVID-19 statistics."""
    __tablename__ = "covid_data"
    
    id = Column(Integer, primary_key=True, index=True)
    country_code = Column(String(3), index=True, nullable=False)
    country_name = Column(String(255))
    date = Column(Date, index=True, nullable=False)
    
    # Cases
    confirmed_cases = Column(Integer, default=0)
    new_cases = Column(Integer, default=0)
    
    # Deaths
    deaths = Column(Integer, default=0)
    new_deaths = Column(Integer, default=0)
    
    # Recoveries
    recovered = Column(Integer, default=0)
    new_recovered = Column(Integer, default=0)
    
    # Active cases
    active_cases = Column(Integer, default=0)
    
    # Vaccination
    total_vaccinations = Column(Integer, default=0)
    people_vaccinated = Column(Integer, default=0)
    people_fully_vaccinated = Column(Integer, default=0)
    vaccination_rate = Column(Float, default=0.0)
    
    # Testing
    total_tests = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Add index for better query performance
    __table_args__ = (
        Index('idx_country_date', 'country_code', 'date'),
    )


class GlobalSummary(Base):
    """Model for storing global daily summary."""
    __tablename__ = "global_summary"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True, nullable=False)
    
    # Global totals
    total_confirmed = Column(Integer, default=0)
    total_deaths = Column(Integer, default=0)
    total_recovered = Column(Integer, default=0)
    total_active = Column(Integer, default=0)
    total_vaccinations = Column(Integer, default=0)
    
    # Daily changes
    new_cases = Column(Integer, default=0)
    new_deaths = Column(Integer, default=0)
    new_recovered = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=func.now())


class Prediction(Base):
    """Model for storing ML predictions."""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    country_code = Column(String(3), index=True, nullable=False)
    prediction_date = Column(Date, nullable=False)
    target_date = Column(Date, nullable=False)
    
    # Predicted values
    predicted_cases = Column(Float)
    predicted_deaths = Column(Float)
    
    # Confidence intervals
    lower_bound = Column(Float)
    upper_bound = Column(Float)
    
    # Model info
    model_type = Column(String(50))
    accuracy_score = Column(Float)
    
    created_at = Column(DateTime, default=func.now())


# Add Index import
from sqlalchemy import Index
