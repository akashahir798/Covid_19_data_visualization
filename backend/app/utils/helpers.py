"""
Helper Utilities

Provides common utility functions for the application.
"""

from datetime import date, datetime
from typing import Optional, Any, Dict
import json


def format_number(num: int) -> str:
    """
    Format large numbers with commas.
    
    Args:
        num: Number to format
    
    Returns:
        Formatted string
    """
    if num is None:
        return "0"
    return f"{num:,}"


def format_date(date_obj: date) -> str:
    """
    Format date object to string.
    
    Args:
        date_obj: Date object
    
    Returns:
        Formatted date string
    """
    if date_obj is None:
        return ""
    return date_obj.strftime("%B %d, %Y")


def calculate_percentage(part: int, total: int) -> float:
    """
    Calculate percentage.
    
    Args:
        part: Part value
        total: Total value
    
    Returns:
        Percentage
    """
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)


def serialize_model(obj: Any) -> Dict:
    """
    Serialize SQLAlchemy model to dictionary.
    
    Args:
        obj: SQLAlchemy model instance
    
    Returns:
        Dictionary representation
    """
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        
        if isinstance(value, date):
            result[column.name] = value.isoformat()
        elif isinstance(value, datetime):
            result[column.name] = value.isoformat()
        else:
            result[column.name] = value
    
    return result


def parse_date(date_str: str) -> Optional[date]:
    """
    Parse date string to date object.
    
    Args:
        date_str: Date string in various formats
    
    Returns:
        Date object or None
    """
    if not date_str:
        return None
    
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%m-%d-%Y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None


def get_color_scale(value: float, min_val: float, max_val: float) -> str:
    """
    Get color based on value range for visualizations.
    
    Args:
        value: Current value
        min_val: Minimum value
        max_val: Maximum value
    
    Returns:
        Color hex code
    """
    if max_val == min_val:
        return "#FFA500"
    
    normalized = (value - min_val) / (max_val - min_val)
    
    if normalized < 0.25:
        return "#FFE4B5"  # Light orange
    elif normalized < 0.5:
        return "#FFA500"  # Orange
    elif normalized < 0.75:
        return "#FF6347"  # Tomato
    else:
        return "#FF0000"  # Red


def clean_string(s: str) -> str:
    """
    Clean and normalize string.
    
    Args:
        s: Input string
    
    Returns:
        Cleaned string
    """
    if s is None:
        return ""
    return s.strip()
