"""
Basic information extractor for Google Maps business information.
"""

from typing import Dict, Any
from .base_extractor import BaseExtractor, SELECTORS, safe_extract_text, safe_extract_attribute


class BasicInfoExtractor(BaseExtractor):
    """Extracts basic business information like name, rating, type."""
    
    def extract_basic_info(self) -> Dict[str, Any]:
        """
        Extract basic business information.
        
        Returns:
            dict: Basic business information
        """
        self.logger.info("Extracting basic business information...")
        
        basic_info = {}
        
        try:
            # Hero image
            hero_image_elem = self.page.locator(SELECTORS["hero_image"]).first
            basic_info['hero_image_url'] = safe_extract_attribute(hero_image_elem, "src")
            
            # Business names
            name_elem = self.page.locator(SELECTORS["business_name_en"]).first
            basic_info['business_name_en'] = safe_extract_text(name_elem)
            
            try:
                name_hi_elem = self.page.locator(SELECTORS["business_name_hi"]).first
                basic_info['business_name_hi'] = safe_extract_text(name_hi_elem)
            except:
                basic_info['business_name_hi'] = None
            
            # Rating and reviews
            rating_elem = self.page.locator(SELECTORS["rating"]).first
            basic_info['rating'] = safe_extract_text(rating_elem)
            
            review_elem = self.page.locator(SELECTORS["review_count"]).first
            basic_info['review_count'] = safe_extract_text(review_elem)
            
            # Business type
            type_elem = self.page.locator(SELECTORS["business_type"]).first
            basic_info['business_type'] = safe_extract_text(type_elem)
            
            # Accessibility
            accessible_elem = self.page.locator(SELECTORS["wheelchair_accessible"])
            basic_info['wheelchair_accessible'] = accessible_elem.count() > 0
            
            self.logger.info("✅ Basic information extracted successfully")
            return basic_info
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting basic info: {e}")
            return basic_info
