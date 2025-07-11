"""
Data extraction module for Google Maps business information.
"""

import logging
import time
from typing import Dict, List, Any, Optional
from playwright.sync_api import Page

try:
    from utils.helpers import (
        format_time, parse_busy_time, safe_extract_text, 
        safe_extract_attribute, clean_address_text, 
        clean_phone_text, clean_plus_code_text, get_day_order_from_current
    )
    from config import SELECTORS, TIMEOUTS
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from utils.helpers import (
        format_time, parse_busy_time, safe_extract_text, 
        safe_extract_attribute, clean_address_text, 
        clean_phone_text, clean_plus_code_text, get_day_order_from_current
    )
    from config import SELECTORS, TIMEOUTS

logger = logging.getLogger(__name__)


class DataExtractor:
    """Extracts various types of data from Google Maps business pages."""
    
    def __init__(self, page: Page):
        """
        Initialize extractor with page instance.
        
        Args:
            page: Playwright page instance
        """
        self.page = page
    
    def extract_basic_info(self) -> Dict[str, Any]:
        """
        Extract basic business information.
        
        Returns:
            dict: Basic business information
        """
        logger.info("Extracting basic business information...")
        
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
            
            logger.info("✅ Basic information extracted successfully")
            return basic_info
            
        except Exception as e:
            logger.error(f"❌ Error extracting basic info: {e}")
            return basic_info
    
    def extract_contact_info(self) -> Dict[str, Any]:
        """
        Extract contact and location information.
        
        Returns:
            dict: Contact and location information
        """
        logger.info("Extracting contact information...")
        
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
            logger.info(f"Services URL extracted: {services_url if services_url else 'Not found'}")
            
            logger.info("✅ Contact information extracted successfully")
            return contact_info
            
        except Exception as e:
            logger.error(f"❌ Error extracting contact info: {e}")
            return contact_info
    
    def extract_operational_info(self) -> Dict[str, Any]:
        """
        Extract operational information like hours and status.
        
        Returns:
            dict: Operational information
        """
        logger.info("Extracting operational information...")
        
        operational_info = {}
        
        try:
            # Status
            status_elem = self.page.locator(SELECTORS["status"]).first
            operational_info['status'] = safe_extract_text(status_elem)
            
            # Weekly hours
            weekly_hours = {}
            hour_rows = self.page.locator(SELECTORS["hours_table"]).all()
            
            for row in hour_rows:
                try:
                    day_elem = row.locator("td").nth(0)
                    time_elem = row.locator("td").nth(1)
                    
                    day = safe_extract_text(day_elem)
                    raw_time = safe_extract_text(time_elem)
                    
                    if day and raw_time:
                        weekly_hours[day] = format_time(raw_time)
                except Exception as e:
                    logger.warning(f"Error extracting hour row: {e}")
                    continue
            
            operational_info['weekly_hours'] = weekly_hours
            
            logger.info("✅ Operational information extracted successfully")
            return operational_info
            
        except Exception as e:
            logger.error(f"❌ Error extracting operational info: {e}")
            return operational_info
    
    def extract_special_features(self) -> List[str]:
        """
        Extract special features and amenities.
        
        Returns:
            list: List of special features
        """
        logger.info("Extracting special features...")
        
        special_features = []
        
        try:
            feature_elements = self.page.locator(SELECTORS["special_features"]).all()
            
            for feat in feature_elements:
                feature_text = safe_extract_text(feat)
                if feature_text:
                    special_features.append(feature_text)
            
            logger.info(f"✅ Extracted {len(special_features)} special features")
            return special_features
            
        except Exception as e:
            logger.error(f"❌ Error extracting special features: {e}")
            return special_features
    
    def extract_popular_times(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract popular times data for all days of the week.
        
        Returns:
            dict: Popular times data organized by day
        """
        logger.info("📊 Extracting popular times...")
        
        try:
            # Get current day to determine the starting point
            try:
                current_day_elem = self.page.locator(SELECTORS["popular_times_current_day"]).first
                current_day = safe_extract_text(current_day_elem, "Monday")
            except:
                current_day = "Monday"
            
            # Get ordered days starting from current day
            ordered_days = get_day_order_from_current(current_day)
            
            popular_times_data = {}
            
            for day in ordered_days:
                logger.info(f"📅 Processing {day}")
                
                # Extract busy times for current day
                bars = self.page.locator(SELECTORS["popular_times_bars"])
                time.sleep(0.5)  # Allow time for data to load
                
                day_entries = []
                bar_count = bars.count()
                
                for i in range(bar_count):
                    try:
                        bar = bars.nth(i)
                        aria_label = safe_extract_attribute(bar, "aria-label")
                        
                        if aria_label:
                            time_data = parse_busy_time(aria_label)
                            if time_data:
                                day_entries.append(time_data)
                    except Exception as e:
                        logger.warning(f"Error processing bar {i}: {e}")
                        continue
                
                popular_times_data[day] = day_entries
                
                # Move to next day
                try:
                    next_button = self.page.locator(SELECTORS["next_day_button"]).first
                    if next_button.is_visible():
                        next_button.click()
                        time.sleep(1.2)  # Wait for transition
                except Exception as e:
                    logger.warning(f"Could not navigate to next day from {day}: {e}")
            
            logger.info(f"✅ Popular times extracted for {len(popular_times_data)} days")
            return popular_times_data
            
        except Exception as e:
            logger.error(f"❌ Error extracting popular times: {e}")
            return {}
