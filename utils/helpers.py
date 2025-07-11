"""
Utility helper functions for the Google Maps scraper.
"""

import re
import time
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
import json

logger = logging.getLogger(__name__)


def format_time(raw_time: str) -> str:
    """
    Format time string to standardized format.
    
    Args:
        raw_time: Raw time string from Google Maps
        
    Returns:
        str: Formatted time string
    """
    raw_time = raw_time.replace(" ", "")
    
    if raw_time.lower() == "closed":
        return "Closed"
    
    # Match pattern like "9am–5pm"
    match = re.match(r"(\d{1,2})(am|pm)[–\-](\d{1,2})(am|pm)", raw_time)
    if match:
        start_hour, start_ampm, end_hour, end_ampm = match.groups()
        return f"{int(start_hour)}:00 {start_ampm.upper()} – {int(end_hour)}:00 {end_ampm.upper()}"
    
    return raw_time


def extract_url_from_style(style: str) -> Optional[str]:
    """
    Extract URL from CSS background-image style.
    
    Args:
        style: CSS style string
        
    Returns:
        str or None: Extracted URL if found
    """
    if not style:
        return None
        
    url_match = re.search(r'url\("([^"]+)"\)', style)
    if url_match:
        url = url_match.group(1)
        if url.startswith("https://lh3.googleusercontent.com/"):
            return url
    return None


def parse_busy_time(aria_label: str) -> Optional[Dict[str, Any]]:
    """
    Parse busy time information from aria-label.
    
    Args:
        aria_label: Aria label containing busy time info
        
    Returns:
        dict or None: Parsed time information
    """
    if not aria_label:
        return None
        
    match = re.match(r"(\d+)% busy at (.+)", aria_label)
    if match:
        busy_percentage = int(match.group(1))
        time_slot = match.group(2)
        return {
            "time": time_slot,
            "busy_percentage": busy_percentage
        }
    return None


def remove_duplicates_preserve_order(items: List[str]) -> List[str]:
    """
    Remove duplicates from list while preserving order.
    
    Args:
        items: List of items
        
    Returns:
        list: List with duplicates removed
    """
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result


def safe_extract_text(element, default: str = "") -> str:
    """
    Safely extract text from a Playwright element.
    
    Args:
        element: Playwright element
        default: Default value if extraction fails
        
    Returns:
        str: Extracted text or default value
    """
    try:
        return element.inner_text().strip() if element else default
    except Exception:
        return default


def safe_extract_attribute(element, attribute: str, default: Optional[str] = None) -> Optional[str]:
    """
    Safely extract attribute from a Playwright element.
    
    Args:
        element: Playwright element
        attribute: Attribute name to extract
        default: Default value if extraction fails
        
    Returns:
        str or None: Extracted attribute value or default
    """
    try:
        return element.get_attribute(attribute) if element else default
    except Exception:
        return default


def clean_address_text(address_text: str) -> str:
    """
    Clean and format address text.
    
    Args:
        address_text: Raw address text
        
    Returns:
        str: Cleaned address text
    """
    if not address_text:
        return ""
        
    # Remove common prefixes
    address_text = address_text.replace("Address: ", "").strip()
    return address_text


def clean_phone_text(phone_text: str) -> str:
    """
    Clean and format phone text.
    
    Args:
        phone_text: Raw phone text
        
    Returns:
        str: Cleaned phone text
    """
    if not phone_text:
        return ""
        
    # Remove common prefixes
    phone_text = phone_text.replace("Phone: ", "").strip()
    return phone_text


def clean_plus_code_text(plus_code_text: str) -> str:
    """
    Clean and format plus code text.
    
    Args:
        plus_code_text: Raw plus code text
        
    Returns:
        str: Cleaned plus code text
    """
    if not plus_code_text:
        return ""
        
    # Remove common prefixes
    plus_code_text = plus_code_text.replace("Plus code: ", "").strip()
    return plus_code_text


def get_day_order_from_current(current_day: str) -> List[str]:
    """
    Get ordered list of days starting from current day.
    
    Args:
        current_day: Current day name
        
    Returns:
        list: Ordered list of days
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Find start index based on current day
    start_index = 0
    for i, day in enumerate(days):
        if day.startswith(current_day[:3]):
            start_index = i
            break
    
    return days[start_index:] + days[:start_index]


def calculate_media_statistics(media_data: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    Calculate statistics for extracted media data.
    
    Args:
        media_data: Dictionary mapping categories to URL lists
        
    Returns:
        dict: Media statistics
    """
    total_items = sum(len(urls) for urls in media_data.values())
    all_urls = [url for urls in media_data.values() for url in urls]
    unique_urls = list(set(all_urls))
    duplicates_removed = len(all_urls) - len(unique_urls)
    
    return {
        "total_categories": len(media_data),
        "total_media_items": total_items,
        "unique_media_items": len(unique_urls),
        "duplicates_found": duplicates_removed
    }


def save_json_file(data: Any, filepath: Path, encoding: str = "utf-8") -> bool:
    """
    Save data to JSON file safely.
    
    Args:
        data: Data to save
        filepath: Path to save file
        encoding: File encoding
        
    Returns:
        bool: True if successful
    """
    try:
        with open(filepath, "w", encoding=encoding) as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save JSON file {filepath}: {e}")
        return False


def ensure_directory_exists(directory: Path) -> bool:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        directory: Directory path
        
    Returns:
        bool: True if directory exists or was created
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory}: {e}")
        return False


def wait_with_timeout(condition_func, timeout: float = 10.0, interval: float = 0.5) -> bool:
    """
    Wait for a condition with timeout.
    
    Args:
        condition_func: Function that returns True when condition is met
        timeout: Maximum wait time in seconds
        interval: Check interval in seconds
        
    Returns:
        bool: True if condition was met within timeout
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)
    return False


def truncate_string(text: str, max_length: int = 100) -> str:
    """
    Truncate string to maximum length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def validate_url(url: str) -> bool:
    """
    Validate if string is a proper URL.
    
    Args:
        url: URL string to validate
        
    Returns:
        bool: True if valid URL
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None


def clean_filename(filename: str) -> str:
    """
    Clean filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Cleaned filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove extra spaces and limit length
    filename = ' '.join(filename.split())
    filename = filename[:100]  # Limit to 100 characters
    
    return filename
