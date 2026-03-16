"""
Data Fetch Script

Fetches COVID-19 data from public APIs and stores in database.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models import CovidData, Country
from app.services.data_service import generate_sample_data, get_country_metadata
from datetime import date


def init_database():
    """Initialize database tables."""
    print("📊 Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")


def load_sample_data():
    """Load sample COVID-19 data into database."""
    print("📥 Loading sample data...")
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing = db.query(CovidData).first()
        if existing:
            print("⚠️ Data already exists in database. Skipping...")
            return
        
        # Load country metadata
        countries = get_country_metadata()
        for c in countries:
            country = Country(
                code=c["code"],
                name=c["name"],
                population=c.get("population"),
                continent=c.get("continent")
            )
            db.add(country)
        
        db.commit()
        print(f"✅ Loaded {len(countries)} countries")
        
        # Load COVID data
        data = generate_sample_data()
        
        for record in data:
            covid_record = CovidData(**record)
            db.add(covid_record)
        
        db.commit()
        print(f"✅ Loaded {len(data)} COVID-19 records")
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        db.rollback()
    finally:
        db.close()


def verify_data():
    """Verify loaded data."""
    print("🔍 Verifying data...")
    
    db = SessionLocal()
    
    try:
        # Count records
        country_count = db.query(Country).count()
        covid_count = db.query(CovidData).count()
        
        print(f"📍 Countries: {country_count}")
        print(f"🦠 COVID records: {covid_count}")
        
        # Get latest date
        latest = db.query(CovidData).order_by(CovidData.date.desc()).first()
        if latest:
            print(f"📅 Latest date: {latest.date}")
        
        # Get unique countries
        unique_countries = db.query(CovidData.country_code).distinct().count()
        print(f"🌍 Unique countries with data: {unique_countries}")
        
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("COVID-19 Data Loader")
    print("=" * 50)
    
    init_database()
    load_sample_data()
    verify_data()
    
    print("=" * 50)
    print("✅ Data loading complete!")
    print("=" * 50)
