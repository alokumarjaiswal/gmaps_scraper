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
    
    # Basic Information
    hero_image_url: Optional[str] = None
    business_name_en: Optional[str] = None
    business_name_hi: Optional[str] = None
    rating: Optional[str] = None
    review_count: Optional[str] = None
    business_type: Optional[str] = None
    
    # Location & Contact
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    plus_code: Optional[str] = None
    
    # Operational Details
    status: Optional[str] = None
    weekly_hours: Optional[Dict[str, str]] = None
    wheelchair_accessible: bool = False
    
    # Additional Information
    special_features: Optional[List[str]] = None
    services_url: Optional[str] = None
    popular_times: Optional[Dict[str, List[Dict[str, Any]]]] = None
    
    def __post_init__(self):
        """Initialize empty collections if None."""
        if self.weekly_hours is None:
            self.weekly_hours = {}
        if self.special_features is None:
            self.special_features = []
        if self.popular_times is None:
            self.popular_times = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the business profile to a dictionary."""
        return asdict(self)
    
    def has_contact_info(self) -> bool:
        """Check if business has any contact information."""
        return any([self.phone, self.website, self.address])
    
    def is_operational_info_available(self) -> bool:
        """Check if operational information is available."""
        return bool(self.status or self.weekly_hours)