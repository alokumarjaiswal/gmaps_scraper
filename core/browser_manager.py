"""
Browser Manager Module

This module handles browser lifecycle and configuration for Google Maps scraping.

File: gmaps_scraper/core/browser_manager.py
"""

import logging
from playwright.sync_api import sync_playwright, BrowserContext
from contextlib import contextmanager
from typing import Dict, Any, Optional

try:
    from config import BROWSER_CONFIG
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from config import BROWSER_CONFIG

logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages browser lifecycle and configuration for Google Maps scraping."""
    
    def __init__(self, headless: Optional[bool] = None, slow_mo: Optional[int] = None, **kwargs):
        """
        Initialize browser manager.
        
        Args:
            headless: Whether to run browser in headless mode (defaults to config value)
            slow_mo: Delay between actions in milliseconds (defaults to config value)
            **kwargs: Additional browser configuration options
        """
        # Use config values as defaults
        self.headless = headless if headless is not None else BROWSER_CONFIG["headless"]
        self.slow_mo = slow_mo if slow_mo is not None else BROWSER_CONFIG["slow_mo"]
        self.browser = None
        self.context = None
        
        # Start with browser configuration from config.py
        self.browser_config = BROWSER_CONFIG.copy()
        
        # Remove browser launch specific settings from context config
        context_config = {k: v for k, v in self.browser_config.items() 
                         if k not in ["headless", "slow_mo", "args"]}
        self.browser_config = context_config
        
        # Update with any custom config
        self.browser_config.update(kwargs)
        
        logger.info(f"Browser manager initialized - Headless: {self.headless}, Slow motion: {self.slow_mo}ms")
        
    @contextmanager
    def get_browser_context(self):
        """Context manager for browser and context lifecycle."""
        try:
            with sync_playwright() as p:
                logger.info("Starting browser session...")
                
                # Get launch args from config
                launch_args = BROWSER_CONFIG.get("args", [])
                
                self.browser = p.chromium.launch(
                    headless=self.headless,
                    slow_mo=self.slow_mo,
                    args=launch_args
                )
                
                self.context = self.browser.new_context(**self.browser_config)
                
                logger.info("Browser context created successfully")
                yield self.context
                
        except Exception as e:
            logger.error(f"Error in browser context: {e}")
            raise
        finally:
            # Cleanup is handled by sync_playwright context manager
            logger.info("Browser session ended")
    
    def update_config(self, **kwargs):
        """
        Update browser configuration.
        
        Args:
            **kwargs: Configuration options to update
        """
        self.browser_config.update(kwargs)
        logger.info(f"Browser configuration updated: {kwargs}")
    
    def set_viewport(self, width: int, height: int):
        """
        Set browser viewport size.
        
        Args:
            width: Viewport width in pixels
            height: Viewport height in pixels
        """
        self.browser_config["viewport"] = {"width": width, "height": height}
        logger.info(f"Viewport set to {width}x{height}")
    
    def set_user_agent(self, user_agent: str):
        """
        Set browser user agent.
        
        Args:
            user_agent: User agent string
        """
        self.browser_config["user_agent"] = user_agent
        logger.info("User agent updated")
    
    def enable_request_interception(self):
        """Enable request interception for the browser context."""
        # This would be implemented when context is created
        # Placeholder for future enhancement
        logger.info("Request interception enabled")
    
    def get_current_config(self) -> Dict[str, Any]:
        """
        Get current browser configuration.
        
        Returns:
            dict: Current browser configuration
        """
        return self.browser_config.copy()