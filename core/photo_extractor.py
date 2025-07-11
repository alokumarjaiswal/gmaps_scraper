"""
Photo extraction module for Google Maps business media.
"""

import time
import logging
from pathlib import Path
from typing import Dict, List, Optional
from playwright.sync_api import Page

logger = logging.getLogger(__name__)


class PhotoExtractor:
    """Handles extraction of photos and screenshots from different categories."""
    
    def __init__(self, page: Page, output_dir: Path):
        """
        Initialize photo extractor.
        
        Args:
            page: Playwright page instance
            output_dir: Directory to save screenshots
        """
        self.page = page
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
    
    def extract_photo_categories(self) -> None:
        """Extract screenshots from all photo categories."""
        logger.info("🖼️ Extracting photo categories...")
        
        try:
            # Click "All" button first
            self._click_photos_all_button()
            
            # Find and iterate through photo tabs
            tablist_selector = 'div[role="tablist"]'
            self.page.wait_for_selector(tablist_selector, timeout=10000)
            
            # Wait for dynamic content to load
            self._wait_for_photo_tabs_to_load(tablist_selector)
            
            tab_buttons = self.page.locator(f'{tablist_selector} button[role="tab"]')
            total_tabs = tab_buttons.count()
            logger.info(f"🔍 Found {total_tabs} photo tabs")
            
            for i in range(total_tabs):
                try:
                    # Re-query tabs each iteration (DOM might change)
                    tab_buttons = self.page.locator(f'{tablist_selector} button[role="tab"]')
                    tab = tab_buttons.nth(i)
                    
                    tab_name = tab.locator('div.Gpq6kf').inner_text().strip()
                    logger.info(f"➡️ Processing tab: {tab_name}")
                    
                    # Click tab and wait for content
                    tab.click()
                    self.page.wait_for_timeout(1500)
                    
                    # Wait for images to load
                    self.page.wait_for_selector(
                        'img[class~="DaSXdd"], img[src^="https://lh3.googleusercontent.com/"]',
                        timeout=5000
                    )
                    
                    # Take screenshot
                    filename = f"photo_tab_{tab_name.replace(' ', '_').lower()}.png"
                    filepath = self.output_dir / filename
                    self.page.screenshot(path=str(filepath))
                    logger.info(f"📸 Saved screenshot: {filename}")
                    
                except Exception as tab_error:
                    logger.warning(f"⚠️ Skipped tab due to error: {tab_error}")
                    
        except Exception as e:
            logger.error(f"❌ Error extracting photo categories: {e}")
    
    def _click_photos_all_button(self) -> None:
        """Click the 'All' button in photos section."""
        try:
            self.page.locator('button[aria-label="All"]').first.click()
            logger.info("🖼️ Clicked 'All' button in Photos & Videos")
        except Exception as e:
            logger.warning(f"❌ Couldn't click 'All' button: {e}")
    
    def _wait_for_photo_tabs_to_load(self, tablist_selector: str, max_wait: int = 6000) -> None:
        """
        Wait for photo tabs to load dynamically.
        
        Args:
            tablist_selector: CSS selector for tab list
            max_wait: Maximum wait time in milliseconds
        """
        step = 500
        waited = 0
        
        while waited < max_wait:
            tab_buttons = self.page.locator(f'{tablist_selector} button[role="tab"]')
            if tab_buttons.count() >= 5:  # Assuming 5+ tabs indicate full load
                break
            time.sleep(step / 1000)
            waited += step
