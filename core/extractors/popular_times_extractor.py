"""
Popular times extractor for Google Maps business information.
"""

import time
from typing import Dict, List, Any
from .base_extractor import BaseExtractor, SELECTORS, safe_extract_text, safe_extract_attribute, parse_busy_time, get_day_order_from_current


class PopularTimesExtractor(BaseExtractor):
    """Extracts popular times data for all days of the week."""
    
    def extract_popular_times(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract popular times data for all days of the week.
        
        Returns:
            dict: Popular times data organized by day
        """
        self.logger.info("📊 Extracting popular times...")
        
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
                self.logger.info(f"📅 Processing {day}")
                
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
                        self.logger.warning(f"Error processing bar {i}: {e}")
                        continue
                
                popular_times_data[day] = day_entries
                
                # Move to next day
                try:
                    next_button = self.page.locator(SELECTORS["next_day_button"]).first
                    if next_button.is_visible():
                        next_button.click()
                        time.sleep(1.2)  # Wait for transition
                except Exception as e:
                    self.logger.warning(f"Could not navigate to next day from {day}: {e}")
            
            self.logger.info(f"✅ Popular times extracted for {len(popular_times_data)} days")
            return popular_times_data
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting popular times: {e}")
            return {}
