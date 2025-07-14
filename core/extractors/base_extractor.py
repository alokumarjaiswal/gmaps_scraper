"""
Base extractor class with shared functionality.
"""

import logging
from typing import Any
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
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from utils.helpers import (
        format_time, parse_busy_time, safe_extract_text, 
        safe_extract_attribute, clean_address_text, 
        clean_phone_text, clean_plus_code_text, 
        get_day_order_from_current
    )
    from config import SELECTORS, TIMEOUTS


class BaseExtractor:
    """Base class for all data extractors."""
    
    def __init__(self, page: Page):
        """
        Initialize extractor with page instance.
        
        Args:
            page: Playwright page instance
        """
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)
