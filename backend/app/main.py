"""
COVID-19 Global Data Visualization Dashboard - Backend API

Main FastAPI application entry point.
Provides REST APIs for global COVID-19 statistics, country data, time series, and predictions.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.database import engine, Base
from app.routers import summary, countries, timeseries, prediction

# Create FastAPI application
app = FastAPI(
    title="COVID-19 Global Dashboard API",
    description="REST API for COVID-19 global data visualization dashboard",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(summary.router, prefix="/api/v1", tags=["Summary"])
app.include_router(countries.router, prefix="/api/v1", tags=["Countries"])
app.include_router(timeseries.router, prefix="/api/v1", tags=["Time Series"])
app.include_router(prediction.router, prefix="/api/v1", tags=["Predictions"])


@app.on_event("startup")
async def startup_event():
    """Initialize database and load data on startup."""
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully")


@app.get("/")
async def root():
    """Root endpoint - returns API information."""
    return {
        "message": "COVID-19 Global Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "summary": "/api/v1/summary",
            "countries": "/api/v1/countries",
            "timeseries": "/api/v1/timeseries/{country}",
            "prediction": "/api/v1/prediction/{country}",
            "top_countries": "/api/v1/top-countries"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "database": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
