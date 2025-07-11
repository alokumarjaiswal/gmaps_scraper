"""
Business Profile Data Model

This module contains the BusinessProfile dataclass that represents
a complete business profile from Google Maps.

File: gmaps_scraper/models/business_profile.py
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any


@dataclass
class BusinessProfile:
    """Data class representing a complete business profile from Google Maps."""
    
    # Overview Tab Data
    overview: Optional[Dict[str, Any]] = None
    
    # Reviews Tab Data  
    reviews: Optional[Dict[str, Any]] = None
    
    # About Tab Data
    about: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize empty dictionaries if None."""
        if self.overview is None:
            self.overview = {}
        if self.reviews is None:
            self.reviews = {}
        if self.about is None:
            self.about = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the business profile to a dictionary."""
        return asdict(self)
    
    def has_contact_info(self) -> bool:
        """Check if business has any contact information."""
        overview = self.overview or {}
        contact_info = overview.get('contact_info', {})
        return any([
            contact_info.get('phone'), 
            contact_info.get('website'), 
            contact_info.get('address')
        ])
    
    def is_operational_info_available(self) -> bool:
        """Check if operational information is available."""
        overview = self.overview or {}
        operational_info = overview.get('operational_info', {})
        return bool(operational_info.get('status') or operational_info.get('weekly_hours'))