"""
Contact information extractor for Google Maps business information.
"""

from typing import Dict, Any
from .base_extractor import BaseExtractor, SELECTORS, TIMEOUTS, safe_extract_text, safe_extract_attribute, clean_address_text, clean_phone_text, clean_plus_code_text


class ContactExtractor(BaseExtractor):
    """Extracts contact and location information."""
    
    def extract_contact_info(self) -> Dict[str, Any]:
        """
        Extract contact and location information.
        
        Returns:
            dict: Contact and location information
        """
        self.logger.info("Extracting contact information...")
        
        contact_info = {}
        
        try:
            # Wait for info section
            self.page.wait_for_selector(SELECTORS["info_section"], timeout=TIMEOUTS["element_wait"])
            
            # Address
            address_elem = self.page.locator(SELECTORS["address"]).first
            address = safe_extract_attribute(address_elem, "aria-label")
            contact_info['address'] = clean_address_text(address) if address else None
            
            # Phone
            phone_elem = self.page.locator(SELECTORS["phone"]).first
            phone = safe_extract_attribute(phone_elem, "aria-label")
            contact_info['phone'] = clean_phone_text(phone) if phone else None
            
            # Website
            website_elem = self.page.locator(SELECTORS["website"]).first
            contact_info['website'] = safe_extract_attribute(website_elem, "href")
            
            # Plus code
            plus_code_elem = self.page.locator(SELECTORS["plus_code"]).first
            plus_code = safe_extract_attribute(plus_code_elem, "aria-label")
            contact_info['plus_code'] = clean_plus_code_text(plus_code) if plus_code else None
            
            # Services URL
            services_elem = self.page.locator(SELECTORS["services_url"]).first
            services_url = safe_extract_attribute(services_elem, "href")
            contact_info['services_url'] = services_url
            self.logger.info(f"Services URL extracted: {services_url if services_url else 'Not found'}")
            
            self.logger.info("✅ Contact information extracted successfully")
            return contact_info
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting contact info: {e}")
            return contact_info
