"""
Main entry point for the Google Maps Business Profile Scraper.

A comprehensive, modular web scraper for extracting business information from Google Maps.
Built with Playwright for reliable automation and data extraction.

Author: Alok Kumar Jaiswal
Version: 3.0.0
"""

import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from scraper import GoogleMapsBusinessScraper
    from utils.logging_config import setup_logging
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the project directory and all modules are present")
    sys.exit(1)

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)


def main():
    """Main execution function."""
    # Example Google Maps business URL
    business_url = "https://www.google.com/maps/place/Tej+Tyre+Agencies/@29.6906,76.9879,17z/data=!3m1!4b1!4m6!3m5!1s0x390e7018855cc87b:0xfe8b2dadb10ca085!8m2!3d29.6906!4d76.9879!16s%2Fg%2F11dx9dp2p2?entry=ttu"
    
    try:
        # Create scraper instance
        logger.info("🚀 Initializing Google Maps Business Scraper...")
        scraper = GoogleMapsBusinessScraper(output_dir="output")
        
        # Scrape the business
        logger.info(f"📍 Starting scrape for business URL: {business_url}")
        business_profile = scraper.scrape_business(business_url)
        
        # Print detailed summary
        scraper.print_scraping_summary(business_profile)
        
        logger.info("✅ Script completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("⏹️ Script interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error during scraping: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
