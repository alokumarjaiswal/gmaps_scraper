"""
Browser Manager Module

This module handles browser lifecycle and configuration for Google Maps scraping.

File: gmaps_scraper/core/browser_manager.py
"""

import logging
from playwright.sync_api import sync_playwright, BrowserContext
from contextlib import contextmanager
from typing import Dict, Any

logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages browser lifecycle and configuration for Google Maps scraping."""
    
    def __init__(self, headless: bool = False, slow_mo: int = 50, **kwargs):
        """
        Initialize browser manager.
        
        Args:
            headless: Whether to run browser in headless mode
            slow_mo: Delay between actions in milliseconds
            **kwargs: Additional browser configuration options
        """
        self.headless = headless
        self.slow_mo = slow_mo
        self.browser = None
        self.context = None
        
        # Default browser configuration
        self.browser_config = {
            "viewport": {"width": 1280, "height": 800},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
            "locale": "en-US",
        }
        
        # Update with any custom config
        self.browser_config.update(kwargs)
        
        logger.info(f"Browser manager initialized - Headless: {headless}, Slow motion: {slow_mo}ms")
        
    @contextmanager
    def get_browser_context(self):
        """Context manager for browser and context lifecycle."""
        try:
            with sync_playwright() as p:
                logger.info("Starting browser session...")
                
                self.browser = p.chromium.launch(
                    headless=self.headless,
                    slow_mo=self.slow_mo
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