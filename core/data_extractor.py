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
        clean_phone_text, clean_plus_code_text, 
        get_day_order_from_current
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
        clean_phone_text, clean_plus_code_text, 
        get_day_order_from_current
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
                    day_elem = row.locator(SELECTORS["table_cell"]).nth(0)
                    time_elem = row.locator(SELECTORS["table_cell"]).nth(1)
                    
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
    
    def extract_about_tab_info(self) -> Dict[str, Any]:
        """
        Extract detailed information from the About tab.
        
        Returns:
            dict: About tab information organized by categories
        """
        logger.info("📋 Extracting About tab information...")
        
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
                            logger.warning(f"Error extracting feature item: {e}")
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
                    logger.warning(f"Error processing section: {e}")
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
            
            logger.info(f"✅ About tab information extracted: {total_features} total features across categories")
            return about_info
            
        except Exception as e:
            logger.error(f"❌ Error extracting About tab info: {e}")
            return about_info
    
    def extract_reviews_tab_info(self) -> Dict[str, Any]:
        """
        Extract comprehensive review information from Reviews tab.
        Uses the precise HTML structure from logic.txt.
        
        Returns:
            dict: Reviews information with individual review details
        """
        logger.info("📋 Extracting Reviews tab information...")
        
        reviews_info = {
            "total_reviews": 0,
            "reviews": []
        }
        
        try:
            # Step 1: Load all reviews by scrolling and clicking "More" buttons
            logger.info("� Step 1: Loading all reviews...")
            self._load_all_reviews()
            
            # Step 2: Find all review containers using exact selector from logic.txt
            # Each div.jftiEf[data-review-id] is one complete review container
            review_containers = self.page.locator(SELECTORS["review_container"]).all()
            logger.info(f"🔍 Step 2: Found {len(review_containers)} review containers")
            
            # Step 3: Extract data from each review container
            for i, container in enumerate(review_containers):
                logger.info(f"📊 Processing review {i+1}/{len(review_containers)}...")
                
                try:
                    review_data = self._extract_single_review_simple(container, i)
                    if review_data:
                        reviews_info["reviews"].append(review_data)
                        logger.info(f"✅ Successfully extracted review {i+1}: {review_data.get('reviewer_name', 'Unknown')}")
                    else:
                        logger.warning(f"⚠️ Failed to extract review {i+1}")
                        
                except Exception as e:
                    logger.error(f"❌ Error extracting review {i+1}: {e}")
                    continue
            
            reviews_info["total_reviews"] = len(reviews_info["reviews"])
            logger.info(f"✅ Reviews extraction complete: {reviews_info['total_reviews']} total reviews")
            
            return reviews_info
            
        except Exception as e:
            logger.error(f"❌ Fatal error in Reviews tab extraction: {e}")
            return reviews_info
    
    def _load_all_reviews(self) -> None:
        """Load all reviews by scrolling and clicking 'More' buttons."""
        logger.info("🔄 Loading all reviews with scrolling...")
        
        try:
            # Simple scrolling approach - scroll until no new reviews load
            last_review_count = 0
            scroll_attempts = 0
            max_scroll_attempts = 15
            
            while scroll_attempts < max_scroll_attempts:
                # Scroll to bottom
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                self.page.wait_for_timeout(2000)  # Wait for content to load
                
                # Count current reviews
                current_review_count = self.page.locator(SELECTORS["review_container"]).count()
                logger.info(f"📊 Scroll attempt {scroll_attempts + 1}: Found {current_review_count} reviews")
                
                # Click all visible "More" buttons to expand truncated text
                more_buttons = self.page.locator(SELECTORS["review_more_button"]).all()
                clicked_count = 0
                for button in more_buttons:
                    try:
                        if button.is_visible():
                            button.click()
                            clicked_count += 1
                            self.page.wait_for_timeout(100)  # Brief pause between clicks
                    except:
                        continue
                
                if clicked_count > 0:
                    logger.info(f"🔄 Clicked {clicked_count} 'More' buttons")
                
                # Check if we loaded new reviews
                if current_review_count == last_review_count:
                    logger.info(f"✅ No new reviews loaded. Stopping at {current_review_count} reviews")
                    break
                
                last_review_count = current_review_count
                scroll_attempts += 1
            
            final_count = self.page.locator(SELECTORS["review_container"]).count()
            logger.info(f"✅ Review loading complete: {final_count} total reviews found")
            
            # SECOND PASS: Wait and click any remaining "More" buttons
            logger.info("🔄 Second pass: Checking for any remaining 'More' buttons...")
            self.page.wait_for_timeout(3000)  # Wait for any lazy-loaded content
            
            # Try multiple times to catch all "More" buttons
            for attempt in range(3):
                logger.info(f"🔍 More button check attempt {attempt + 1}/3...")
                
                # Click "More" buttons for review text expansion
                review_more_buttons = self.page.locator(SELECTORS["review_more_button"]).all()
                
                # Click "More" buttons for owner response expansion  
                owner_more_buttons = self.page.locator(SELECTORS["owner_response_more_button"]).all()
                
                total_clicked = 0
                
                # Click review "More" buttons
                for button in review_more_buttons:
                    try:
                        if button.is_visible():
                            button.click()
                            total_clicked += 1
                            self.page.wait_for_timeout(200)  # Pause between clicks
                    except:
                        continue
                
                # Click owner response "More" buttons
                for button in owner_more_buttons:
                    try:
                        if button.is_visible():
                            button.click()
                            total_clicked += 1
                            self.page.wait_for_timeout(200)  # Pause between clicks
                    except:
                        continue
                
                if total_clicked > 0:
                    logger.info(f"🔄 Second pass clicked {total_clicked} additional 'More' buttons")
                    self.page.wait_for_timeout(1000)  # Wait for content to expand
                else:
                    logger.info(f"✅ No more 'More' buttons found in attempt {attempt + 1}")
                    break
            
            logger.info("✅ All 'More' buttons processed. Reviews should be fully expanded.")
            
        except Exception as e:
            logger.error(f"❌ Error in _load_all_reviews: {e}")
    
    def _extract_single_review_simple(self, container, index: int) -> Optional[Dict[str, Any]]:
        """
        Extract data from a single review container using exact selectors from logic.txt.
        
        Args:
            container: Playwright locator for review container (div.jftiEf[data-review-id])
            index: Review index for logging
            
        Returns:
            dict: Single review data or None if extraction fails
        """
        try:
            review_data = {}
            logger.info(f"🔍 Extracting review {index+1}...")
            
            # 1. Extract reviewer photo URL from button.WEBjve > img.NBa7we
            try:
                photo_button = container.locator(SELECTORS["reviewer_photo_button"]).first
                photo_img = photo_button.locator(SELECTORS["reviewer_photo_image"]).first
                review_data["reviewer_photo_url"] = safe_extract_attribute(photo_img, "src")
                logger.info(f"  📷 Photo URL: {review_data['reviewer_photo_url'][:50] if review_data['reviewer_photo_url'] else 'None'}...")
            except Exception as e:
                logger.warning(f"  ⚠️ Failed to extract photo URL: {e}")
                review_data["reviewer_photo_url"] = None
            
            # 2. Extract reviewer name and details from button.al6Kxe
            try:
                reviewer_button = container.locator(SELECTORS["reviewer_info_button"]).first
                name_div = reviewer_button.locator(SELECTORS["reviewer_name_div"]).first
                details_div = reviewer_button.locator(SELECTORS["reviewer_details_div"]).first
                
                review_data["reviewer_name"] = safe_extract_text(name_div)
                review_data["reviewer_details"] = safe_extract_text(details_div)
                
                logger.info(f"  👤 Name: {review_data['reviewer_name']}")
                logger.info(f"  📝 Details: {review_data['reviewer_details']}")
                
                # If no reviewer name, this is invalid
                if not review_data["reviewer_name"]:
                    logger.warning(f"  ❌ No reviewer name found - skipping")
                    return None
                    
            except Exception as e:
                logger.error(f"  ❌ Failed to extract reviewer info: {e}")
                return None
            
            # 3. Extract rating and time from div.DU9Pgb
            try:
                rating_time_div = container.locator(SELECTORS["review_rating_time_div"]).first
                
                # Rating from aria-label of span.kvMYJc
                rating_span = rating_time_div.locator(SELECTORS["review_rating_span"]).first
                rating_aria = safe_extract_attribute(rating_span, "aria-label")
                if rating_aria and "star" in rating_aria:
                    review_data["rating"] = rating_aria.split()[0]  # Extract "5" from "5 stars"
                else:
                    review_data["rating"] = None
                
                # Time from span.rsqaWe
                time_span = rating_time_div.locator(SELECTORS["review_time_span"]).first
                review_data["review_time"] = safe_extract_text(time_span)
                
                logger.info(f"  ⭐ Rating: {review_data['rating']}")
                logger.info(f"  🕒 Time: {review_data['review_time']}")
                
            except Exception as e:
                logger.warning(f"  ⚠️ Failed to extract rating/time: {e}")
                review_data["rating"] = None
                review_data["review_time"] = None
            
            # 4. Extract review text from span.wiI7pd
            try:
                text_span = container.locator(SELECTORS["review_text_span"]).first
                review_data["review_text"] = safe_extract_text(text_span)
                logger.info(f"  💬 Text: {review_data['review_text'][:50] if review_data['review_text'] else 'None'}...")
            except Exception as e:
                logger.warning(f"  ⚠️ Failed to extract review text: {e}")
                review_data["review_text"] = None
            
            # 5. Extract review photos from button.Tya61d (background-image URLs)
            try:
                photo_buttons = container.locator(SELECTORS["review_photo_button"]).all()
                review_photos = []
                for photo_btn in photo_buttons:
                    style = safe_extract_attribute(photo_btn, "style")
                    if style and "background-image: url(" in style:
                        # Extract URL from style="background-image: url("https://...")"
                        url_start = style.find('url("') + 5
                        url_end = style.find('")', url_start)
                        if url_start > 4 and url_end > url_start:
                            photo_url = style[url_start:url_end]
                            review_photos.append(photo_url)
                
                review_data["review_photos"] = review_photos
                logger.info(f"  📷 Photos: {len(review_photos)} found")
                
            except Exception as e:
                logger.warning(f"  ⚠️ Failed to extract review photos: {e}")
                review_data["review_photos"] = []
            
            # 6. Extract owner response from div.CDe7pd
            try:
                owner_response_div = container.locator(SELECTORS["owner_response_div"]).first
                if owner_response_div.count() > 0:
                    # Extract response time from span.DZSIDd
                    response_time_span = owner_response_div.locator(SELECTORS["owner_response_time_span"]).first
                    response_time = safe_extract_text(response_time_span)
                    
                    # Extract response text from div.wiI7pd
                    response_text_div = owner_response_div.locator(SELECTORS["owner_response_text_div"]).first
                    response_text = safe_extract_text(response_text_div)
                    
                    if response_text:
                        review_data["owner_response"] = {
                            "response_text": response_text,
                            "response_time": response_time
                        }
                        logger.info(f"  💼 Owner response: {response_text[:50]}...")
                    else:
                        review_data["owner_response"] = None
                else:
                    review_data["owner_response"] = None
                    
            except Exception as e:
                logger.warning(f"  ⚠️ Failed to extract owner response: {e}")
                review_data["owner_response"] = None
            
            logger.info(f"✅ Successfully extracted review {index+1}")
            return review_data
                
        except Exception as e:
            logger.error(f"❌ Fatal error extracting review {index+1}: {e}")
            return None
