"""
Media URL extractor for Google Maps business photos and videos.

This module extracts actual media URLs from different photo tabs by analyzing
the DOM structure as described in logic.txt.
"""

import re
import time
import logging
from typing import Dict, List, Any, Optional
from playwright.sync_api import Page

try:
    from config import TIMEOUTS, MEDIA_CONFIG, MEDIA_SELECTORS, REGEX_PATTERNS
    from .base_extractor import BaseExtractor, safe_extract_attribute, safe_extract_text
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from config import TIMEOUTS, MEDIA_CONFIG, MEDIA_SELECTORS, REGEX_PATTERNS
    from core.extractors.base_extractor import BaseExtractor, safe_extract_attribute, safe_extract_text


class MediaExtractor(BaseExtractor):
    """Extracts media URLs from photo and video tabs on Google Maps business pages."""
    
    def __init__(self, page: Page):
        """
        Initialize media extractor.
        
        Args:
            page: Playwright page instance
        """
        super().__init__(page)
        self.logger = logging.getLogger(__name__)
    
    def extract_all_media_urls(self) -> Dict[str, Any]:
        """
        Extract media URLs from all available photo tabs.
        
        Returns:
            dict: Media URLs organized by tab name
        """
        self.logger.info("🎬 Starting media URL extraction from all photo tabs...")
        
        media_data = {
            "total_media_count": 0,
            "tabs": {}
        }
        
        try:
            # Step 1: Click "All" button to ensure we're in the photos section
            self._click_photos_all_button()
            
            # Step 2: Wait for photo tabs to load
            self._wait_for_photo_tabs_to_load()
            
            # Step 3: Get all available tabs
            tab_buttons = self.page.locator(MEDIA_SELECTORS["photo_tabs"])
            total_tabs = tab_buttons.count()
            self.logger.info(f"🔍 Found {total_tabs} photo tabs for media extraction")
            
            # Step 4: Extract media from each tab
            for i in range(total_tabs):
                try:
                    # Re-query tabs each iteration (DOM might change)
                    tab_buttons = self.page.locator(MEDIA_SELECTORS["photo_tabs"])
                    tab = tab_buttons.nth(i)
                    
                    # Get tab name
                    tab_name = self._get_tab_name(tab)
                    self.logger.info(f"📂 Processing tab: {tab_name}")
                    
                    # Click tab and wait for content
                    tab.click()
                    self.page.wait_for_timeout(MEDIA_CONFIG["tab_switch_delay"])
                    
                    # Extract media URLs from this tab
                    tab_media = self._extract_media_from_current_tab(tab_name)
                    
                    if tab_media:
                        media_data["tabs"][tab_name] = tab_media
                        media_count = len(tab_media.get("photos", [])) + len(tab_media.get("videos", []))
                        media_data["total_media_count"] += media_count
                        self.logger.info(f"✅ Extracted {media_count} media items from {tab_name} tab")
                    else:
                        self.logger.warning(f"⚠️ No media found in {tab_name} tab")
                        
                except Exception as tab_error:
                    self.logger.error(f"❌ Error processing tab {i}: {tab_error}")
                    continue
            
            self.logger.info(f"🎉 Media extraction complete: {media_data['total_media_count']} total media items across {len(media_data['tabs'])} tabs")
            return media_data
            
        except Exception as e:
            self.logger.error(f"❌ Fatal error in media extraction: {e}")
            return media_data
    
    def _click_photos_all_button(self) -> None:
        """Click the 'All' button in photos section."""
        try:
            all_button = self.page.locator(MEDIA_SELECTORS["photos_all_button"]).first
            if all_button.is_visible():
                all_button.click()
                self.page.wait_for_timeout(MEDIA_CONFIG["interaction_delay"])
                self.logger.info("🖼️ Clicked 'All' button in Photos & Videos section")
            else:
                self.logger.warning("⚠️ 'All' button not visible")
        except Exception as e:
            self.logger.warning(f"❌ Couldn't click 'All' button: {e}")
    
    def _wait_for_photo_tabs_to_load(self) -> None:
        """Wait for photo tabs to load dynamically."""
        try:
            tablist_selector = MEDIA_SELECTORS["photo_tablist"]
            self.page.wait_for_selector(tablist_selector, timeout=TIMEOUTS["element_wait"])
            
            # Wait for the photo gallery container to be ready
            gallery_container_selector = MEDIA_SELECTORS["photo_gallery_container"]
            self.page.wait_for_selector(gallery_container_selector, timeout=TIMEOUTS["element_wait"])
            
            # Wait a bit more for dynamic content and initial photos to load
            self.page.wait_for_timeout(MEDIA_CONFIG["lazy_load_wait"])
            
            # Wait for at least some photo containers to be present
            photo_containers_selector = MEDIA_SELECTORS["photo_containers"]
            self.page.wait_for_selector(photo_containers_selector, timeout=TIMEOUTS["element_wait"])
            
            self.logger.info("✅ Photo tabs and gallery container loaded successfully")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error waiting for photo tabs: {e}")
    
    def _get_tab_name(self, tab_element) -> str:
        """
        Extract tab name from tab element.
        
        Args:
            tab_element: Playwright locator for tab element
            
        Returns:
            str: Tab name
        """
        try:
            name_div = tab_element.locator(MEDIA_SELECTORS["tab_name"]).first
            tab_name = safe_extract_text(name_div)
            return tab_name.strip() if tab_name else "Unknown"
        except Exception as e:
            self.logger.warning(f"⚠️ Error extracting tab name: {e}")
            return "Unknown"
    
    def _extract_media_from_current_tab(self, tab_name: str) -> Dict[str, Any]:
        """
        Extract media URLs from the currently active tab.
        
        Args:
            tab_name: Name of the current tab
            
        Returns:
            dict: Media data for this tab
        """
        tab_data = {
            "tab_name": tab_name,
            "photos": [],
            "videos": [],
            "total_count": 0
        }
        
        try:
            # Check if this is a video tab (needs special handling)
            if "video" in tab_name.lower():
                self.logger.info(f"🎥 Processing Videos tab - extracting video URLs from iframes")
                
                # Wait for video content to load
                self.page.wait_for_timeout(MEDIA_CONFIG["lazy_load_wait"])
                
                # Extract video URLs
                videos = self._extract_video_urls()
                tab_data["videos"] = videos
            else:
                # Trigger lazy loading with scrolling and interactions for photo tabs
                self._trigger_lazy_loading()
                
                # Extract photo URLs for other tabs
                photos = self._extract_photo_urls()
                tab_data["photos"] = photos
            
            tab_data["total_count"] = len(tab_data["photos"]) + len(tab_data["videos"])
            return tab_data
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting media from {tab_name}: {e}")
            return tab_data
    
    def _trigger_lazy_loading(self) -> None:
        """Trigger lazy loading by scrolling within the photo gallery container."""
        try:
            self.logger.info("🔄 Triggering lazy loading with container-specific scrolling...")
            
            # Find the scrollable photo gallery container
            gallery_container = self.page.locator(MEDIA_SELECTORS["photo_gallery_container"]).first
            
            if gallery_container.count() == 0:
                self.logger.warning("⚠️ Photo gallery container not found, falling back to page scrolling")
                self._fallback_page_scrolling()
                return
            
            # Get container dimensions and scroll height
            container_info = gallery_container.evaluate("""
                (element) => {
                    return {
                        scrollHeight: element.scrollHeight,
                        clientHeight: element.clientHeight,
                        scrollTop: element.scrollTop
                    };
                }
            """)
            
            self.logger.info(f"� Container info - ScrollHeight: {container_info['scrollHeight']}, ClientHeight: {container_info['clientHeight']}")
            
            # Scroll through the container in steps
            scroll_steps = MEDIA_CONFIG["max_scroll_steps"]
            scroll_height = container_info['scrollHeight']
            
            for step in range(scroll_steps):
                # Calculate scroll position
                scroll_position = (step + 1) / scroll_steps
                target_scroll = int(scroll_height * scroll_position)
                
                # Scroll the container to the target position
                gallery_container.evaluate(f"""
                    (element) => {{
                        element.scrollTop = {target_scroll};
                    }}
                """)
                
                self.logger.info(f"📍 Scroll step {step + 1}/{scroll_steps}: scrolled to {target_scroll}px")
                
                # Wait for content to load
                self.page.wait_for_timeout(MEDIA_CONFIG["scroll_delay"])
                
                # Additional wait for lazy loading
                self.page.wait_for_timeout(MEDIA_CONFIG["interaction_delay"])
            
            # Scroll back to top for consistent state
            gallery_container.evaluate("(element) => { element.scrollTop = 0; }")
            self.page.wait_for_timeout(MEDIA_CONFIG["interaction_delay"])
            
            # Additional step: Try to hover over photo containers to trigger any hover-based lazy loading
            self._trigger_hover_interactions()
            
            self.logger.info("✅ Container lazy loading triggered successfully")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error during container scrolling: {e}")
            self.logger.info("🔄 Falling back to page scrolling...")
            self._fallback_page_scrolling()
    
    def _fallback_page_scrolling(self) -> None:
        """Fallback method using page-level scrolling."""
        try:
            self.logger.info("🔄 Using fallback page scrolling...")
            
            # Scroll through the content to trigger lazy loading
            for step in range(MEDIA_CONFIG["max_scroll_steps"]):
                # Scroll down
                scroll_position = (step + 1) / MEDIA_CONFIG["max_scroll_steps"]
                self.page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {scroll_position})")
                self.page.wait_for_timeout(MEDIA_CONFIG["scroll_delay"])
                
                # Wait for potential new content to load
                self.page.wait_for_timeout(MEDIA_CONFIG["interaction_delay"])
            
            # Scroll back to top
            self.page.evaluate("window.scrollTo(0, 0)")
            self.page.wait_for_timeout(MEDIA_CONFIG["interaction_delay"])
            
            self.logger.info("✅ Fallback page scrolling completed")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error during fallback scrolling: {e}")
    
    def _trigger_hover_interactions(self) -> None:
        """Trigger hover interactions on photo containers to force lazy loading."""
        try:
            self.logger.info("🎯 Triggering hover interactions for lazy loading...")
            
            # Get visible photo containers
            photo_containers = self.page.locator(MEDIA_SELECTORS["photo_containers"]).all()
            
            # Hover over first few containers to trigger lazy loading
            max_hovers = min(5, len(photo_containers))  # Limit to avoid excessive operations
            
            for i in range(max_hovers):
                try:
                    container = photo_containers[i]
                    if container.is_visible():
                        container.hover()
                        self.page.wait_for_timeout(200)  # Brief pause between hovers
                except Exception as hover_error:
                    self.logger.warning(f"⚠️ Error hovering over container {i}: {hover_error}")
                    continue
            
            self.logger.info(f"✅ Completed hover interactions on {max_hovers} containers")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error during hover interactions: {e}")
    
    def _extract_photo_urls(self) -> List[Dict[str, str]]:
        """
        Extract photo URLs from photo containers.
        Based on logic.txt patterns for All, Inside, and By Owner tabs.
        
        Returns:
            list: List of photo data dictionaries
        """
        photos = []
        
        try:
            # Find all photo containers (a.OKAoZd elements)
            photo_containers = self.page.locator(MEDIA_SELECTORS["photo_containers"]).all()
            self.logger.info(f"🔍 Found {len(photo_containers)} photo containers")
            
            for i, container in enumerate(photo_containers):
                if i >= MEDIA_CONFIG["max_media_per_tab"]:
                    self.logger.info(f"📊 Reached maximum media limit ({MEDIA_CONFIG['max_media_per_tab']}) for this tab")
                    break
                
                try:
                    photo_data = self._extract_single_photo_data(container, i)
                    if photo_data:
                        photos.append(photo_data)
                        
                except Exception as photo_error:
                    self.logger.warning(f"⚠️ Error extracting photo {i}: {photo_error}")
                    continue
            
            self.logger.info(f"✅ Extracted {len(photos)} photo URLs")
            return photos
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting photo URLs: {e}")
            return photos
    
    def _extract_single_photo_data(self, container, index: int) -> Optional[Dict[str, str]]:
        """
        Extract photo data from a single photo container.
        
        Args:
            container: Playwright locator for photo container
            index: Photo index for logging
            
        Returns:
            dict: Photo data or None if extraction fails
        """
        try:
            photo_data = {}
            
            # Extract data-photo-index attribute
            photo_index = safe_extract_attribute(container, "data-photo-index")
            if photo_index:
                photo_data["photo_index"] = photo_index
            
            # Extract aria-label for photo description
            aria_label = safe_extract_attribute(container, "aria-label")
            if aria_label:
                photo_data["description"] = aria_label.strip()
            
            # Extract URLs from div.Uf0tqf.loaded (high-quality image) - only if loaded
            loaded_div = container.locator(MEDIA_SELECTORS["photo_loaded_div"]).first
            if loaded_div.count() > 0:
                style = safe_extract_attribute(loaded_div, "style")
                if style:
                    # Extract background-image URL using regex
                    url_match = re.search(REGEX_PATTERNS["background_image_url"], style)
                    if url_match:
                        photo_data["high_quality_url"] = url_match.group(1)
            else:
                # Check if there's an unloaded div.Uf0tqf (without .loaded class)
                unloaded_div = container.locator('div.Uf0tqf').first
                if unloaded_div.count() > 0:
                    self.logger.info(f"📷 Photo {index + 1}: High-quality image not yet loaded")
            
            # Extract URL from div.U39Pmb (thumbnail image)
            background_div = container.locator(MEDIA_SELECTORS["photo_background_div"]).first
            if background_div.count() > 0:
                style = safe_extract_attribute(background_div, "style")
                if style:
                    # Extract background-image URL using regex
                    url_match = re.search(REGEX_PATTERNS["background_image_url"], style)
                    if url_match:
                        photo_data["thumbnail_url"] = url_match.group(1)
            
            # Return photo data if we have at least one URL
            if photo_data.get("high_quality_url") or photo_data.get("thumbnail_url"):
                self.logger.info(f"📷 Photo {index + 1}: Found URLs - HQ: {'✅' if photo_data.get('high_quality_url') else '❌'}, Thumb: {'✅' if photo_data.get('thumbnail_url') else '❌'}")
                return photo_data
            else:
                self.logger.warning(f"⚠️ Photo {index + 1}: No URLs found")
                return None
                
        except Exception as e:
            self.logger.warning(f"❌ Error extracting photo {index + 1}: {e}")
            return None
    
    def _extract_video_urls(self) -> List[Dict[str, str]]:
        """
        Extract video URLs from iframe elements with simple logic.
        Based on logic.txt: iframe.widget-scene-imagery-iframe -> content frame -> video element
        """
        videos = []
        
        try:
            # Find iframe.widget-scene-imagery-iframe elements
            iframes = self.page.locator("iframe.widget-scene-imagery-iframe")
            iframe_count = iframes.count()
            
            self.logger.info(f"🎥 Found {iframe_count} video iframes")
            
            for i in range(min(iframe_count, MEDIA_CONFIG["max_media_per_tab"])):
                iframe = iframes.nth(i)
                video_data = {}
                
                try:
                    # Access iframe content frame
                    content_frame = iframe.content_frame
                    if content_frame:
                        # Find video element inside iframe
                        video_element = content_frame.locator("video").first
                        if video_element.count() > 0:
                            # Extract video src (main video URL)
                            video_src = safe_extract_attribute(video_element, "src")
                            if video_src:
                                video_data["video_url"] = video_src
                                self.logger.info(f"🎥 Video {i + 1}: Found video URL")
                            
                            # Extract poster image
                            poster_url = safe_extract_attribute(video_element, "poster")
                            if poster_url:
                                video_data["poster_url"] = poster_url
                            
                            # Extract additional attributes
                            video_format = safe_extract_attribute(video_element, "format")
                            if video_format:
                                video_data["format"] = video_format
                            
                            docid = safe_extract_attribute(video_element, "docid")
                            if docid:
                                video_data["docid"] = docid
                            
                            cpn = safe_extract_attribute(video_element, "cpn")
                            if cpn:
                                video_data["cpn"] = cpn
                            
                            if video_data.get("video_url"):
                                videos.append(video_data)
                        else:
                            self.logger.warning(f"🎥 Video {i + 1}: No video element found in iframe")
                    else:
                        self.logger.warning(f"🎥 Video {i + 1}: Could not access iframe content")
                        
                except Exception as iframe_error:
                    self.logger.warning(f"🎥 Video {i + 1}: Error accessing iframe: {iframe_error}")
            
            self.logger.info(f"✅ Extracted {len(videos)} video URLs")
            return videos
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting video URLs: {e}")
            return []
    
    