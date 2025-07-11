"""
Navigation module for Google Maps interface interactions.
"""

import logging
from typing import Optional
from playwright.sync_api import Page

try:
    from config import TIMEOUTS
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from config import TIMEOUTS

logger = logging.getLogger(__name__)


class GoogleMapsNavigator:
    """Handles navigation and interaction with Google Maps interface."""
    
    def __init__(self, page: Page):
        """
        Initialize navigator with page instance.
        
        Args:
            page: Playwright page instance
        """
        self.page = page
        
    def load_business_page(self, url: str, timeout: Optional[int] = None) -> None:
        """
        Load Google Maps business page.
        
        Args:
            url: Google Maps business URL
            timeout: Page load timeout in milliseconds
        """
        if timeout is None:
            timeout = TIMEOUTS["page_load"]
            
        logger.info(f"Loading business page: {url}")
        self.page.goto(url, timeout=timeout)
        
        # Wait for essential elements to load
        self.page.wait_for_selector("h1", timeout=TIMEOUTS["element_wait"])
        self.page.wait_for_selector('button[aria-label^="Photo of"] img', timeout=TIMEOUTS["tab_wait"])
        logger.info("Business page loaded successfully")
    
    def click_tab_by_label(self, tab_label: str, timeout: Optional[int] = None) -> bool:
        """
        Click a tab by its aria-label.
        
        Args:
            tab_label: Partial label text to match
            timeout: Wait timeout in milliseconds
            
        Returns:
            bool: True if tab was clicked successfully
        """
        if timeout is None:
            timeout = TIMEOUTS["button_wait"]
            
        selector = f'button[role="tab"][aria-label*="{tab_label}"]'
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            self.page.click(selector)
            self.page.wait_for_timeout(TIMEOUTS["screenshot_delay"])
            logger.info(f"✅ Clicked tab: {tab_label}")
            return True
        except Exception as e:
            logger.warning(f"❌ Failed to click tab '{tab_label}': {e}")
            return False
    
    def check_action_button(self, label: str, click: bool = False, timeout: Optional[int] = None) -> bool:
        """
        Check if an action button exists and optionally click it.
        
        Args:
            label: Exact aria-label of the button
            click: Whether to click the button
            timeout: Wait timeout in milliseconds
            
        Returns:
            bool: True if button exists (and was clicked if requested)
        """
        if timeout is None:
            timeout = TIMEOUTS["action_wait"]
            
        selector = f'button[aria-label="{label}"]'
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            if click:
                self.page.click(selector)
                logger.info(f"🔄 Clicked button: {label}")
            else:
                logger.info(f"✅ Button available: {label}")
            return True
        except Exception as e:
            logger.warning(f"❌ Button not found: {label}")
            return False
    
    def scroll_to_element(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Scroll to a specific element.
        
        Args:
            selector: CSS selector for the element
            timeout: Wait timeout in milliseconds
            
        Returns:
            bool: True if element was found and scrolled to
        """
        if timeout is None:
            timeout = TIMEOUTS["action_wait"]
            
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            element = self.page.locator(selector).first
            element.scroll_into_view_if_needed()
            logger.info(f"✅ Scrolled to element: {selector}")
            return True
        except Exception as e:
            logger.warning(f"❌ Failed to scroll to element '{selector}': {e}")
            return False
    
    def wait_for_page_stabilization(self, wait_time: Optional[int] = None) -> None:
        """
        Wait for page to stabilize after navigation or interaction.
        
        Args:
            wait_time: Time to wait in milliseconds
        """
        if wait_time is None:
            wait_time = TIMEOUTS["screenshot_delay"]
            
        self.page.wait_for_timeout(wait_time)
        logger.info(f"⏳ Waited {wait_time}ms for page stabilization")
    
    def click_element_safely(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Safely click an element with error handling.
        
        Args:
            selector: CSS selector for the element
            timeout: Wait timeout in milliseconds
            
        Returns:
            bool: True if element was clicked successfully
        """
        if timeout is None:
            timeout = TIMEOUTS["action_wait"]
            
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            element = self.page.locator(selector).first
            
            if element.is_visible():
                element.click()
                logger.info(f"✅ Clicked element: {selector}")
                return True
            else:
                logger.warning(f"⚠️ Element not visible: {selector}")
                return False
        except Exception as e:
            logger.warning(f"❌ Failed to click element '{selector}': {e}")
            return False
    
    def hover_element(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Hover over an element.
        
        Args:
            selector: CSS selector for the element
            timeout: Wait timeout in milliseconds
            
        Returns:
            bool: True if element was hovered successfully
        """
        if timeout is None:
            timeout = TIMEOUTS["action_wait"]
            
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            element = self.page.locator(selector).first
            
            if element.is_visible():
                element.hover()
                logger.info(f"✅ Hovered over element: {selector}")
                return True
            else:
                logger.warning(f"⚠️ Element not visible for hover: {selector}")
                return False
        except Exception as e:
            logger.warning(f"❌ Failed to hover over element '{selector}': {e}")
            return False
    
    def navigate_to_photos_section(self) -> bool:
        """
        Navigate to the photos section of the business page.
        
        Returns:
            bool: True if navigation was successful
        """
        try:
            # Try to find and click photos tab or button
            photos_selectors = [
                'button[aria-label*="Photos"]',
                'button[role="tab"][aria-label*="Photos"]',
                'a[href*="@"][href*="photos"]'
            ]
            
            for selector in photos_selectors:
                if self.click_element_safely(selector):
                    self.wait_for_page_stabilization()
                    logger.info("✅ Successfully navigated to photos section")
                    return True
            
            logger.warning("❌ Could not find photos section")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error navigating to photos section: {e}")
            return False
    
    def navigate_back(self) -> bool:
        """
        Navigate back to previous page.
        
        Returns:
            bool: True if navigation was successful
        """
        try:
            self.page.go_back()
            self.wait_for_page_stabilization()
            logger.info("✅ Navigated back successfully")
            return True
        except Exception as e:
            logger.warning(f"❌ Failed to navigate back: {e}")
            return False
    
    def close_modal_if_present(self) -> bool:
        """
        Close any modal or overlay that might be open.
        
        Returns:
            bool: True if modal was found and closed
        """
        close_selectors = [
            'button[aria-label="Close"]',
            'button[aria-label*="close"]',
            '[role="button"][aria-label*="Close"]',
            'button.VfPpkd-icon-LgbsSe',
            'button[jsaction*="cancel"]'
        ]
        
        for selector in close_selectors:
            try:
                element = self.page.locator(selector).first
                if element.is_visible():
                    element.click()
                    self.page.wait_for_timeout(TIMEOUTS["click_delay"])
                    logger.info(f"✅ Closed modal using selector: {selector}")
                    return True
            except Exception:
                continue
        
        # Try pressing Escape key as fallback
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(TIMEOUTS["click_delay"])
            logger.info("✅ Pressed Escape to close modal")
            return True
        except Exception:
            pass
        
        return False
