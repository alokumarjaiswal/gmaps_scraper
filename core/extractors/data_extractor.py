"""
Main data extraction orchestrator for Google Maps business information.
"""

import logging
from typing import Dict, List, Any
from playwright.sync_api import Page

from .basic_info_extractor import BasicInfoExtractor
from .contact_extractor import ContactExtractor
from .operational_extractor import OperationalExtractor
from .popular_times_extractor import PopularTimesExtractor
from .about_extractor import AboutExtractor
from .reviews_extractor import ReviewsExtractor
from .media_extractor import MediaExtractor

logger = logging.getLogger(__name__)


class DataExtractor:
    """Main orchestrator for extracting various types of data from Google Maps business pages."""
    
    def __init__(self, page: Page):
        """
        Initialize extractor with page instance.
        
        Args:
            page: Playwright page instance
        """
        self.page = page
        
        # Initialize individual extractors
        self.basic_info_extractor = BasicInfoExtractor(page)
        self.contact_extractor = ContactExtractor(page)
        self.operational_extractor = OperationalExtractor(page)
        self.popular_times_extractor = PopularTimesExtractor(page)
        self.about_extractor = AboutExtractor(page)
        self.reviews_extractor = ReviewsExtractor(page)
        self.media_extractor = MediaExtractor(page)
    
    def extract_basic_info(self) -> Dict[str, Any]:
        """
        Extract basic business information.
        
        Returns:
            dict: Basic business information
        """
        return self.basic_info_extractor.extract_basic_info()
    
    def extract_contact_info(self) -> Dict[str, Any]:
        """
        Extract contact and location information.
        
        Returns:
            dict: Contact and location information
        """
        return self.contact_extractor.extract_contact_info()
    
    def extract_operational_info(self) -> Dict[str, Any]:
        """
        Extract operational information like hours and status.
        
        Returns:
            dict: Operational information
        """
        return self.operational_extractor.extract_operational_info()
    
    def extract_special_features(self) -> List[str]:
        """
        Extract special features and amenities.
        
        Returns:
            list: List of special features
        """
        return self.operational_extractor.extract_special_features()
    
    def extract_popular_times(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract popular times data for all days of the week.
        
        Returns:
            dict: Popular times data organized by day
        """
        return self.popular_times_extractor.extract_popular_times()
    
    def extract_about_tab_info(self) -> Dict[str, Any]:
        """
        Extract detailed information from the About tab.
        
        Returns:
            dict: About tab information organized by categories
        """
        return self.about_extractor.extract_about_tab_info()
    
    def extract_reviews_tab_info(self) -> Dict[str, Any]:
        """
        Extract comprehensive review information from Reviews tab.
        
        Returns:
            dict: Reviews information with individual review details
        """
        return self.reviews_extractor.extract_reviews_tab_info()
    
    def extract_media_urls(self) -> Dict[str, Any]:
        """
        Extract media URLs from all photo and video tabs.
        
        Returns:
            dict: Media URLs organized by tab name
        """
        return self.media_extractor.extract_all_media_urls()
        return self.reviews_extractor.extract_reviews_tab_info()
