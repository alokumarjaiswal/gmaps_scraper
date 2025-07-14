"""
About tab information extractor for Google Maps business information.
"""

from typing import Dict, Any
from .base_extractor import BaseExtractor, SELECTORS, TIMEOUTS, safe_extract_text, safe_extract_attribute


class AboutExtractor(BaseExtractor):
    """Extracts detailed information from the About tab."""
    
    def extract_about_tab_info(self) -> Dict[str, Any]:
        """
        Extract detailed information from the About tab.
        
        Returns:
            dict: About tab information organized by categories
        """
        self.logger.info("📋 Extracting About tab information...")
        
        about_info = {
            'accessibility_features': {},
            'service_options': [],
            'amenities': [],
            'crowd_info': [],
            'planning_info': [],
            'payment_methods': [],
            'parking_options': []
        }
        
        try:
            # Wait for About tab content to load
            self.page.wait_for_selector(SELECTORS["about_section_container"], timeout=TIMEOUTS["element_wait"])
            
            # Find all section containers
            section_items = self.page.locator(SELECTORS["about_section_items"]).all()
            
            for section in section_items:
                try:
                    # Get section title
                    title_elem = section.locator(SELECTORS["about_section_titles"]).first
                    section_title = safe_extract_text(title_elem).lower() if title_elem else ""
                    
                    if not section_title:
                        continue
                    
                    # Get all features in this section
                    feature_items = section.locator(SELECTORS["about_feature_lists"]).all()
                    features = []
                    
                    for item in feature_items:
                        try:
                            # Extract aria-label which contains the full feature description
                            feature_span = item.locator(SELECTORS["about_feature_text"]).first
                            if feature_span:
                                feature_text = safe_extract_attribute(feature_span, "aria-label")
                                if feature_text:
                                    features.append(feature_text)
                        except Exception as e:
                            self.logger.warning(f"Error extracting feature item: {e}")
                            continue
                    
                    # Categorize features based on section title
                    if "accessibility" in section_title:
                        # For accessibility, separate available vs not available features
                        available_features = []
                        unavailable_features = []
                        
                        for feature in features:
                            if any(keyword in feature.lower() for keyword in ["has ", "accessible"]) and not any(keyword in feature.lower() for keyword in ["no ", "does not"]):
                                available_features.append(feature)
                            else:
                                unavailable_features.append(feature)
                        
                        about_info['accessibility_features'] = {
                            'available': available_features,
                            'unavailable': unavailable_features
                        }
                        
                    elif "service" in section_title:
                        about_info['service_options'].extend(features)
                    elif "amenities" in section_title:
                        about_info['amenities'].extend(features)
                    elif "crowd" in section_title:
                        about_info['crowd_info'].extend(features)
                    elif "planning" in section_title:
                        about_info['planning_info'].extend(features)
                    elif "payment" in section_title:
                        about_info['payment_methods'].extend(features)
                    elif "parking" in section_title:
                        about_info['parking_options'].extend(features)
                        
                except Exception as e:
                    self.logger.warning(f"Error processing section: {e}")
                    continue
            
            # Log extraction summary
            total_features = (
                len(about_info['accessibility_features'].get('available', [])) +
                len(about_info['accessibility_features'].get('unavailable', [])) +
                len(about_info['service_options']) +
                len(about_info['amenities']) +
                len(about_info['crowd_info']) +
                len(about_info['planning_info']) +
                len(about_info['payment_methods']) +
                len(about_info['parking_options'])
            )
            
            self.logger.info(f"✅ About tab information extracted: {total_features} total features across categories")
            return about_info
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting About tab info: {e}")
            return about_info
