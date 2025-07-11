"""
Configuration settings for Google Maps scraper.
"""

from pathlib import Path
from typing import Dict, Any

# Browser configuration
BROWSER_CONFIG = {
    "headless": False,
    "slow_mo": 50,
    "viewport": {"width": 1920, "height": 1080},
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "locale": "en-US",
    "args": [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-blink-features=AutomationControlled',
        '--disable-extensions'
    ]
}

# Timeout configurations (in milliseconds)
TIMEOUTS = {
    "page_load": 60000,
    "element_wait": 30000,
    "tab_wait": 15000,
    "button_wait": 10000,
    "action_wait": 5000,
    "screenshot_delay": 1500,
    "scroll_delay": 800,
    "click_delay": 300
}

# Selectors for Google Maps elements
SELECTORS = {
    "business_name_en": "h1.DUwDvf",
    "business_name_hi": "h2.bwoZTb",
    "hero_image": 'button[aria-label^="Photo of"] img',
    "rating": '.F7nice span[aria-hidden="true"]',
    "review_count": '.F7nice span[aria-label$="reviews"]',
    "business_type": 'button[jsaction="pane.wfvdle17.category"]',
    "wheelchair_accessible": 'span[aria-label*="accessible entrance"]',
    "info_section": 'div[aria-label^="Information for"]',
    "address": 'button[aria-label^="Address:"]',
    "phone": 'button[aria-label^="Phone:"]',
    "website": 'a[data-item-id="authority"]',
    "plus_code": 'button[aria-label^="Plus code:"]',
    "services_url": 'a[data-item-id="services"]',
    "status": ".ZDu9vd",
    "hours_table": "table.eK4R0e tr",
    "special_features": 'div[data-item-id^="place-info-links"] div.Io6YTe',
    "popular_times_current_day": "div[role='option'][aria-selected='true']",
    "popular_times_bars": "div[role='img'][aria-label*='% busy']",
    "next_day_button": "button[aria-label='Go to the next day']",
    "photo_tabs": 'div[role="tablist"] button[role="tab"]',
    "all_photos_button": 'button[aria-label="All"]',
    "photo_divs": 'div.U39Pmb[role="img"]',
    "photo_images": 'img[src^="https://lh3.googleusercontent.com/"]',
    "data_src_elements": '[data-src^="https://lh3.googleusercontent.com/"]'
}

# Navigation tabs to check
NAVIGATION_TABS = ["Reviews", "About", "Overview"]

# Action buttons to verify
ACTION_BUTTONS = ["Directions", "Save", "Nearby", "Send to phone", "Share"]

# Output configuration
OUTPUT_CONFIG = {
    "directory": "output",
    "business_profile_file": "business_profile.json",
    "media_summary_file": "media_summary.json",
    "final_screenshot": "business_profile_final.png",
    "log_file": "gmaps_scraper.log"
}

# Days of the week for popular times
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Regular expressions for data extraction
REGEX_PATTERNS = {
    "time_format": r"(\d{1,2})(am|pm)[–\-](\d{1,2})(am|pm)",
    "background_image_url": r'url\("([^"]+)"\)',
    "busy_percentage": r"(\d+)% busy at (.+)",
    "emoji_pattern": r'[🚀✅📊📅🔄🔍🖼️📸💾❌⚠️➡️]+'
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "encoding": "utf-8"
}

# Photo extraction configuration
PHOTO_CONFIG = {
    "max_scroll_steps": 5,
    "max_images_to_click": 3,
    "scroll_positions": [0.2, 0.5, 0.8, 1.0],
    "max_wait_for_tabs": 6000,
    "tab_load_threshold": 5
}

def get_config() -> Dict[str, Any]:
    """
    Get complete configuration dictionary.
    
    Returns:
        dict: Complete configuration settings
    """
    return {
        "browser": BROWSER_CONFIG,
        "timeouts": TIMEOUTS,
        "selectors": SELECTORS,
        "navigation_tabs": NAVIGATION_TABS,
        "action_buttons": ACTION_BUTTONS,
        "output": OUTPUT_CONFIG,
        "days": DAYS_OF_WEEK,
        "regex": REGEX_PATTERNS,
        "logging": LOGGING_CONFIG,
        "photos": PHOTO_CONFIG
    }
