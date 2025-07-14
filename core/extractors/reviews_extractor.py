"""
Reviews information extractor for Google Maps business information.
"""

import time
from typing import Dict, Any, Optional
from .base_extractor import BaseExtractor, SELECTORS, safe_extract_text, safe_extract_attribute


class ReviewsExtractor(BaseExtractor):
    """Extracts comprehensive review information from Reviews tab."""
    
    def extract_reviews_tab_info(self) -> Dict[str, Any]:
        """
        Extract comprehensive review information from Reviews tab.
        Uses the precise HTML structure from logic.txt.
        
        Returns:
            dict: Reviews information with individual review details
        """
        self.logger.info("📋 Extracting Reviews tab information...")
        
        reviews_info = {
            "total_reviews": 0,
            "reviews": []
        }
        
        try:
            # Step 1: Load all reviews by scrolling and clicking "More" buttons
            self.logger.info("🔄 Step 1: Loading all reviews...")
            self._load_all_reviews()
            
            # Step 2: Find all review containers using exact selector from logic.txt
            # Each div.jftiEf[data-review-id] is one complete review container
            review_containers = self.page.locator(SELECTORS["review_container"]).all()
            self.logger.info(f"🔍 Step 2: Found {len(review_containers)} review containers")
            
            # Step 3: Extract data from each review container
            for i, container in enumerate(review_containers):
                self.logger.info(f"📊 Processing review {i+1}/{len(review_containers)}...")
                
                try:
                    review_data = self._extract_single_review_simple(container, i)
                    if review_data:
                        reviews_info["reviews"].append(review_data)
                        self.logger.info(f"✅ Successfully extracted review {i+1}: {review_data.get('reviewer_name', 'Unknown')}")
                    else:
                        self.logger.warning(f"⚠️ Failed to extract review {i+1}")
                        
                except Exception as e:
                    self.logger.error(f"❌ Error extracting review {i+1}: {e}")
                    continue
            
            reviews_info["total_reviews"] = len(reviews_info["reviews"])
            self.logger.info(f"✅ Reviews extraction complete: {reviews_info['total_reviews']} total reviews")
            
            return reviews_info
            
        except Exception as e:
            self.logger.error(f"❌ Fatal error in Reviews tab extraction: {e}")
            return reviews_info
    
    def _load_all_reviews(self) -> None:
        """Load all reviews by scrolling and clicking 'More' buttons."""
        self.logger.info("🔄 Loading all reviews with scrolling...")
        
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
                self.logger.info(f"📊 Scroll attempt {scroll_attempts + 1}: Found {current_review_count} reviews")
                
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
                    self.logger.info(f"🔄 Clicked {clicked_count} 'More' buttons")
                
                # Check if we loaded new reviews
                if current_review_count == last_review_count:
                    self.logger.info(f"✅ No new reviews loaded. Stopping at {current_review_count} reviews")
                    break
                
                last_review_count = current_review_count
                scroll_attempts += 1
            
            final_count = self.page.locator(SELECTORS["review_container"]).count()
            self.logger.info(f"✅ Review loading complete: {final_count} total reviews found")
            
            # SECOND PASS: Wait and click any remaining "More" buttons
            self.logger.info("🔄 Second pass: Checking for any remaining 'More' buttons...")
            self.page.wait_for_timeout(3000)  # Wait for any lazy-loaded content
            
            # Try multiple times to catch all "More" buttons
            for attempt in range(3):
                self.logger.info(f"🔍 More button check attempt {attempt + 1}/3...")
                
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
                    self.logger.info(f"🔄 Second pass clicked {total_clicked} additional 'More' buttons")
                    self.page.wait_for_timeout(1000)  # Wait for content to expand
                else:
                    self.logger.info(f"✅ No more 'More' buttons found in attempt {attempt + 1}")
                    break
            
            self.logger.info("✅ All 'More' buttons processed. Reviews should be fully expanded.")
            
        except Exception as e:
            self.logger.error(f"❌ Error in _load_all_reviews: {e}")
    
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
            self.logger.info(f"🔍 Extracting review {index+1}...")
            
            # 1. Extract reviewer photo URL from button.WEBjve > img.NBa7we
            try:
                photo_button = container.locator(SELECTORS["reviewer_photo_button"]).first
                photo_img = photo_button.locator(SELECTORS["reviewer_photo_image"]).first
                review_data["reviewer_photo_url"] = safe_extract_attribute(photo_img, "src")
                self.logger.info(f"  📷 Photo URL: {review_data['reviewer_photo_url'][:50] if review_data['reviewer_photo_url'] else 'None'}...")
            except Exception as e:
                self.logger.warning(f"  ⚠️ Failed to extract photo URL: {e}")
                review_data["reviewer_photo_url"] = None
            
            # 2. Extract reviewer name and details from button.al6Kxe
            try:
                reviewer_button = container.locator(SELECTORS["reviewer_info_button"]).first
                name_div = reviewer_button.locator(SELECTORS["reviewer_name_div"]).first
                details_div = reviewer_button.locator(SELECTORS["reviewer_details_div"]).first
                
                review_data["reviewer_name"] = safe_extract_text(name_div)
                review_data["reviewer_details"] = safe_extract_text(details_div)
                
                self.logger.info(f"  👤 Name: {review_data['reviewer_name']}")
                self.logger.info(f"  📝 Details: {review_data['reviewer_details']}")
                
                # If no reviewer name, this is invalid
                if not review_data["reviewer_name"]:
                    self.logger.warning(f"  ❌ No reviewer name found - skipping")
                    return None
                    
            except Exception as e:
                self.logger.error(f"  ❌ Failed to extract reviewer info: {e}")
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
                
                self.logger.info(f"  ⭐ Rating: {review_data['rating']}")
                self.logger.info(f"  🕒 Time: {review_data['review_time']}")
                
            except Exception as e:
                self.logger.warning(f"  ⚠️ Failed to extract rating/time: {e}")
                review_data["rating"] = None
                review_data["review_time"] = None
            
            # 4. Extract review text from span.wiI7pd
            try:
                text_span = container.locator(SELECTORS["review_text_span"]).first
                review_data["review_text"] = safe_extract_text(text_span)
                self.logger.info(f"  💬 Text: {review_data['review_text'][:50] if review_data['review_text'] else 'None'}...")
            except Exception as e:
                self.logger.warning(f"  ⚠️ Failed to extract review text: {e}")
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
                self.logger.info(f"  📷 Photos: {len(review_photos)} found")
                
            except Exception as e:
                self.logger.warning(f"  ⚠️ Failed to extract review photos: {e}")
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
                        self.logger.info(f"  💼 Owner response: {response_text[:50]}...")
                    else:
                        review_data["owner_response"] = None
                else:
                    review_data["owner_response"] = None
                    
            except Exception as e:
                self.logger.warning(f"  ⚠️ Failed to extract owner response: {e}")
                review_data["owner_response"] = None
            
            self.logger.info(f"✅ Successfully extracted review {index+1}")
            return review_data
                
        except Exception as e:
            self.logger.error(f"❌ Fatal error extracting review {index+1}: {e}")
            return None
