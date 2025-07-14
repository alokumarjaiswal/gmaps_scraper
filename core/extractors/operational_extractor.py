"""
Operational information extractor for Google Maps business information.
"""

from typing import Dict, Any, List
from .base_extractor import BaseExtractor, SELECTORS, safe_extract_text, format_time


class OperationalExtractor(BaseExtractor):
    """Extracts operational information like hours, status, and special features."""
    
    def extract_operational_info(self) -> Dict[str, Any]:
        """
        Extract operational information like hours and status.
        
        Returns:
            dict: Operational information
        """
        self.logger.info("Extracting operational information...")
        
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
                    day_elem = row.locator(SELECTORS["table_cell"]).nth(0)
                    time_elem = row.locator(SELECTORS["table_cell"]).nth(1)
                    
                    day = safe_extract_text(day_elem)
                    raw_time = safe_extract_text(time_elem)
                    
                    if day and raw_time:
                        weekly_hours[day] = format_time(raw_time)
                except Exception as e:
                    self.logger.warning(f"Error extracting hour row: {e}")
                    continue
            
            operational_info['weekly_hours'] = weekly_hours
            
            self.logger.info("✅ Operational information extracted successfully")
            return operational_info
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting operational info: {e}")
            return operational_info
    
    def extract_special_features(self) -> List[str]:
        """
        Extract special features and amenities.
        
        Returns:
            list: List of special features
        """
        self.logger.info("Extracting special features...")
        
        special_features = []
        
        try:
            feature_elements = self.page.locator(SELECTORS["special_features"]).all()
            
            for feat in feature_elements:
                feature_text = safe_extract_text(feat)
                if feature_text:
                    special_features.append(feature_text)
            
            self.logger.info(f"✅ Extracted {len(special_features)} special features")
            return special_features
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting special features: {e}")
            return special_features
