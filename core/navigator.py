"""
Navigation module for Google Maps interface interactions.
"""

import logging
from typing import Optional, Dict, Any
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
        self.current_business_url = None
        
    def load_business_page(self, url: str, timeout: Optional[int] = None) -> None:
        """
        Load Google Maps business page.
        
        Args:
            url: Google Maps business URL
            timeout: Page load timeout in milliseconds
        """
        if timeout is None:
            timeout = TIMEOUTS["page_load"]
            
        # Store the URL for potential reloading
        self.current_business_url = url
            
        logger.info(f"Loading business page: {url}")
        self.page.goto(url, timeout=timeout)
        
        # Wait for essential elements to load
        self.page.wait_for_selector("h1", timeout=TIMEOUTS["element_wait"])
        self.page.wait_for_selector('button[aria-label^="Photo of"] img', timeout=TIMEOUTS["tab_wait"])
        
        # Wait for page to stabilize
        self.page.wait_for_timeout(2000)
        
        # Try to trigger tab loading by interacting with the page
        try:
            # Scroll down slightly to trigger any lazy loading
            self.page.evaluate("window.scrollBy(0, 100)")
            self.page.wait_for_timeout(1000)
            
            # Scroll back up
            self.page.evaluate("window.scrollBy(0, -100)")
            self.page.wait_for_timeout(1000)
            
            # Wait for tabs to appear - try multiple selectors
            tab_selectors = [
                'button[role="tab"]',
                'button[aria-label*="Overview"]',
                'button[aria-label*="Reviews"]',
                'button:has-text("Overview")',
                'button:has-text("Reviews")'
            ]
            
            for selector in tab_selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=3000)
                    logger.info(f"✅ Found tabs using selector: {selector}")
                    break
                except:
                    continue
            else:
                logger.warning("⚠️ No tabs found after waiting - they may not be available for this business")
                
        except Exception as e:
            logger.warning(f"⚠️ Error during tab loading interaction: {e}")
        
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
    
    def navigate_to_tab(self, tab_name: str) -> bool:
        """
        Navigate to a specific tab (Overview, Reviews, About).
        
        Args:
            tab_name: Name of the tab to navigate to
            
        Returns:
            bool: True if navigation was successful
        """
        # Multiple selectors to try for each tab
        tab_selectors = {
            "Overview": [
                'button[aria-label*="Overview" i]',
                'button[role="tab"][aria-label*="Overview"]',
                'button:has-text("Overview")'
            ],
            "Reviews": [
                'button[aria-label*="Reviews" i]',
                'button[role="tab"][aria-label*="Reviews"]', 
                'button:has-text("Reviews")'
            ],
            "About": [
                'button[aria-label*="About" i]',
                'button[role="tab"][aria-label*="About"]',
                'button:has-text("About")'
            ]
        }
        
        if tab_name not in tab_selectors:
            logger.error(f"❌ Unknown tab: {tab_name}")
            return False
        
        logger.info(f"🔄 Navigating to {tab_name} tab...")
        
        # Try each selector for the tab
        for selector in tab_selectors[tab_name]:
            try:
                # Check if element exists
                element = self.page.locator(selector).first
                if element.count() > 0:
                    # Try to click even if not visible (might be hidden by CSS)
                    element.click(force=True)
                    self.wait_for_page_stabilization()
                    logger.info(f"✅ Successfully navigated to {tab_name} tab using selector: {selector}")
                    return True
                else:
                    logger.debug(f"Selector '{selector}' found no elements")
            except Exception as e:
                logger.debug(f"Selector '{selector}' failed: {e}")
                continue
        
        logger.error(f"❌ Failed to navigate to {tab_name} tab - no working selectors found")
        return False
    
    def check_tab_availability(self) -> Dict[str, bool]:
        """
        Check which tabs are available on the current page.
        Uses multiple selector strategies and inspection to find tabs.
        
        Returns:
            dict: Dictionary showing availability of each tab
        """
        # First, inspect the page to understand structure
        inspection = self.inspect_page_tabs()
        
        availability = {
            "Overview": False,
            "Reviews": False,
            "About": False
        }
        
        # Use inspection results to determine availability more reliably
        found_buttons = inspection.get('buttons_with_overview_reviews_about', [])
        
        for button_info in found_buttons:
            keyword = button_info.get('keyword', '').lower()
            aria_label = button_info.get('aria_label', '').lower()
            text = button_info.get('text', '').lower()
            
            # More flexible matching
            if 'overview' in keyword or 'overview' in aria_label or 'overview' in text:
                availability["Overview"] = True
                logger.info(f"✅ Found Overview tab: {button_info}")
                
            elif 'reviews' in keyword or 'reviews' in aria_label or 'reviews' in text:
                availability["Reviews"] = True
                logger.info(f"✅ Found Reviews tab: {button_info}")
                
            elif 'about' in keyword or 'about' in aria_label or 'about' in text:
                availability["About"] = True
                logger.info(f"✅ Found About tab: {button_info}")
        
        # Double-check with direct element existence (not visibility)
        tab_selectors = {
            "Overview": 'button[aria-label*="Overview" i]',
            "Reviews": 'button[aria-label*="Reviews" i]',
            "About": 'button[aria-label*="About" i]'
        }
        
        for tab_name, selector in tab_selectors.items():
            if not availability[tab_name]:  # Only check if not already found
                try:
                    element = self.page.locator(selector).first
                    # Check if element exists (not necessarily visible)
                    if element.count() > 0:
                        availability[tab_name] = True
                        logger.info(f"✅ Found {tab_name} tab via direct selector")
                except Exception as e:
                    logger.debug(f"Direct selector for {tab_name} failed: {e}")
                
        logger.info(f"📋 Tab availability: {availability}")
        return availability
    
    def reload_business_page(self, timeout: Optional[int] = None) -> bool:
        """
        Reload the current business page to return to the default Overview state.
        
        Args:
            timeout: Page load timeout in milliseconds
            
        Returns:
            bool: True if page was reloaded successfully
        """
        if not self.current_business_url:
            logger.error("❌ No business URL stored for reloading")
            return False
            
        try:
            logger.info("🔄 Reloading business page to return to Overview tab...")
            self.load_business_page(self.current_business_url, timeout)
            logger.info("✅ Business page reloaded successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to reload business page: {e}")
            return False
    
    def inspect_page_for_tabs(self) -> None:
        """
        Inspect the current page to find what tab-like elements exist.
        This is useful for debugging tab detection issues.
        """
        logger.info("🔍 Inspecting page for tab elements...")
        
        # Common patterns for tabs in Google Maps
        tab_patterns = [
            'button[role="tab"]',
            'div[role="tab"]', 
            'button[data-value]',
            'button[aria-label*="tab"]',
            'button:has-text("Overview")',
            'button:has-text("Reviews")',
            'button:has-text("About")',
            'a[href*="overview"]',
            'a[href*="reviews"]',
            'a[href*="about"]'
        ]
        
        for pattern in tab_patterns:
            try:
                elements = self.page.locator(pattern).all()
                if elements:
                    logger.info(f"Found {len(elements)} elements matching '{pattern}':")
                    for i, elem in enumerate(elements[:3]):  # Show first 3 matches
                        try:
                            text = elem.inner_text()[:50]  # First 50 chars
                            aria_label = elem.get_attribute("aria-label") or "No aria-label"
                            logger.info(f"  {i+1}. Text: '{text}' | Aria-label: '{aria_label}'")
                        except:
                            logger.info(f"  {i+1}. Could not get element details")
            except Exception as e:
                logger.debug(f"Pattern '{pattern}' failed: {e}")
                
        # Also check for any buttons with common tab words
        tab_words = ["Overview", "Reviews", "About", "Photos"]
        for word in tab_words:
            try:
                elements = self.page.locator(f"button:has-text('{word}')").all()
                if elements:
                    logger.info(f"Found {len(elements)} buttons containing '{word}'")
            except:
                pass
    
    def inspect_page_tabs(self) -> Dict[str, Any]:
        """
        Inspect the page to find available tabs and their selectors.
        This is a debugging method to understand the page structure.
        
        Returns:
            dict: Information about found tabs and buttons
        """
        logger.info("🔍 Inspecting page for tabs...")
        
        inspection_result = {
            'buttons_with_role_tab': [],
            'buttons_with_tab_in_aria': [],
            'buttons_with_overview_reviews_about': [],
            'all_buttons': []
        }
        
        try:
            # Find all buttons with role="tab"
            tab_buttons = self.page.locator('button[role="tab"]').all()
            for btn in tab_buttons:
                try:
                    aria_label = btn.get_attribute('aria-label') or ''
                    text_content = btn.text_content() or ''
                    inspection_result['buttons_with_role_tab'].append({
                        'aria_label': aria_label,
                        'text': text_content
                    })
                except:
                    pass
            
            # Find buttons with "tab" in aria-label
            tab_aria_buttons = self.page.locator('button[aria-label*="tab" i]').all()
            for btn in tab_aria_buttons:
                try:
                    aria_label = btn.get_attribute('aria-label') or ''
                    text_content = btn.text_content() or ''
                    inspection_result['buttons_with_tab_in_aria'].append({
                        'aria_label': aria_label,
                        'text': text_content
                    })
                except:
                    pass
            
            # Look for buttons with Overview, Reviews, About keywords
            keywords = ['Overview', 'Reviews', 'About']
            for keyword in keywords:
                buttons = self.page.locator(f'button:has-text("{keyword}")').all()
                buttons.extend(self.page.locator(f'button[aria-label*="{keyword}" i]').all())
                
                for btn in buttons:
                    try:
                        aria_label = btn.get_attribute('aria-label') or ''
                        text_content = btn.text_content() or ''
                        inspection_result['buttons_with_overview_reviews_about'].append({
                            'keyword': keyword,
                            'aria_label': aria_label,
                            'text': text_content
                        })
                    except:
                        pass
            
            # Get first 10 buttons on page for general inspection
            all_buttons = self.page.locator('button').all()[:10]
            for btn in all_buttons:
                try:
                    aria_label = btn.get_attribute('aria-label') or ''
                    text_content = btn.text_content() or ''
                    if aria_label or text_content:
                        inspection_result['all_buttons'].append({
                            'aria_label': aria_label,
                            'text': text_content
                        })
                except:
                    pass
            
            logger.info(f"📋 Page inspection complete. Found {len(inspection_result['buttons_with_role_tab'])} role=tab buttons")
            return inspection_result
            
        except Exception as e:
            logger.error(f"❌ Error inspecting page: {e}")
            return inspection_result
        
    def test_specific_selectors(self) -> None:
        """
        Test specific selectors we know should work based on inspection.
        """
        logger.info("🧪 Testing specific selectors...")
        
        # Test the exact selectors we expect to work
        test_selectors = [
            'button[role="tab"][aria-label*="Overview"]',
            'button[role="tab"][aria-label*="Reviews"]',
            'button[aria-label*="Overview"]',
            'button[aria-label*="Reviews"]',
            'button[aria-label="Overview of Tej Tyre Agencies"]',
            'button[aria-label="Reviews for Tej Tyre Agencies"]',
            'button:has-text("Overview")',
            'button:has-text("Reviews")'
        ]
        
        for selector in test_selectors:
            try:
                elements = self.page.locator(selector).all()
                visible_count = 0
                for elem in elements:
                    if elem.is_visible(timeout=500):
                        visible_count += 1
                        
                if visible_count > 0:
                    logger.info(f"✅ Selector '{selector}' found {visible_count} visible elements")
                else:
                    logger.info(f"❌ Selector '{selector}' found {len(elements)} elements but none visible")
                    
            except Exception as e:
                logger.info(f"❌ Selector '{selector}' failed: {e}")
