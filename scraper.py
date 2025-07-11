"""
Main scraper orchestration module.
"""

import logging
import shutil
from pathlib import Path
from dataclasses import asdict
from typing import Dict, List, Any

try:
    from core.browser_manager import BrowserManager
    from core.navigator import GoogleMapsNavigator
    from core.data_extractor import DataExtractor
    from core.photo_extractor import PhotoExtractor
    from models.business_profile import BusinessProfile
    from utils.helpers import save_json_file
    from config import OUTPUT_CONFIG, NAVIGATION_TABS, ACTION_BUTTONS
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent))
    
    from core.browser_manager import BrowserManager
    from core.navigator import GoogleMapsNavigator
    from core.data_extractor import DataExtractor
    from core.photo_extractor import PhotoExtractor
    from models.business_profile import BusinessProfile
    from utils.helpers import save_json_file
    from config import OUTPUT_CONFIG, NAVIGATION_TABS, ACTION_BUTTONS

logger = logging.getLogger(__name__)

class GoogleMapsBusinessScraper:
    """
    Main orchestrator for Google Maps business scraping operations.
    
    This class coordinates all scraping activities including browser management,
    navigation, data extraction, and photo capture.
    """
    
    def __init__(self, output_dir: str = "scraped_data"):
        """
        Initialize the Google Maps business scraper.
        
        Args:
            output_dir: Directory where scraped data will be saved
        """
        self.output_dir = Path(output_dir)
        self.browser_manager = None
        self.navigator = None
        self.data_extractor = None
        self.photo_extractor = None
        
        # Ensure output directory exists and is clean
        self._clear_output_directory()
        
        logger.info(f"🚀 GoogleMapsBusinessScraper initialized with output directory: {self.output_dir}")
    
    def _clear_output_directory(self) -> None:
        """
        Clear the output directory of any existing files.
        """
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Output directory prepared: {self.output_dir}")
    
    def scrape_business(self, google_maps_url: str) -> BusinessProfile:
        """
        Main method to scrape a Google Maps business profile.
        
        Args:
            google_maps_url: URL of the Google Maps business page
            
        Returns:
            BusinessProfile object with all scraped data
        """
        logger.info("🎯 Starting business scraping process...")
        
        try:
            # Initialize browser manager
            self.browser_manager = BrowserManager()
            
            # Use context manager for browser session
            with self.browser_manager.get_browser_context() as context:
                # Create a new page
                page = context.new_page()
                
                # Initialize all components with the page
                self.navigator = GoogleMapsNavigator(page)
                self.data_extractor = DataExtractor(page)
                self.photo_extractor = PhotoExtractor(page, self.output_dir)
                
                logger.info("✅ All components initialized successfully")
                
                # Navigate to the business page
                self.navigator.load_business_page(google_maps_url)
                
                # Extract business data components
                basic_info = self.data_extractor.extract_basic_info()
                contact_info = self.data_extractor.extract_contact_info()
                operational_info = self.data_extractor.extract_operational_info()
                special_features = self.data_extractor.extract_special_features()
                popular_times = self.data_extractor.extract_popular_times()
                
                # Create business profile
                business_profile = BusinessProfile(
                    business_name_en=basic_info.get('business_name_en'),
                    business_name_hi=basic_info.get('business_name_hi'),
                    rating=basic_info.get('rating'),
                    review_count=basic_info.get('review_count'),
                    business_type=basic_info.get('business_type'),
                    hero_image_url=basic_info.get('hero_image_url'),
                    address=contact_info.get('address'),
                    phone=contact_info.get('phone'),
                    website=contact_info.get('website'),
                    plus_code=contact_info.get('plus_code'),
                    services_url=contact_info.get('services_url'),
                    status=operational_info.get('status'),
                    weekly_hours=operational_info.get('weekly_hours'),
                    wheelchair_accessible=operational_info.get('wheelchair_accessible', False),
                    special_features=special_features,
                    popular_times=popular_times
                )
                
                # Extract photos (screenshots only)
                self.photo_extractor.extract_photo_categories()
                
                # Save business profile
                self._save_business_profile(business_profile)
                
                logger.info("✅ Scraping completed successfully!")
                
                return business_profile
            
        except Exception as e:
            logger.error(f"❌ Error during scraping: {e}")
            raise
    
    def _save_business_profile(self, business_profile: BusinessProfile) -> None:
        """
        Save the business profile to a JSON file.
        
        Args:
            business_profile: The business profile to save
        """
        try:
            # Generate filename based on business name
            business_name = business_profile.business_name_en or "unknown_business"
            output_file = self.output_dir / f"{business_name}.json"
            
            # Convert to dictionary for JSON serialization
            profile_data = asdict(business_profile)
            
            # Save to file
            success = save_json_file(profile_data, output_file)
            
            if success:
                logger.info(f"💾 Business profile saved to: {output_file}")
            else:
                logger.error(f"❌ Failed to save business profile to: {output_file}")
                
        except Exception as e:
            logger.error(f"❌ Error saving business profile: {e}")
    
    def get_output_directory(self) -> Path:
        """
        Get the current output directory path.
        
        Returns:
            Path object representing the output directory
        """
        return self.output_dir
    
    def change_output_directory(self, output_dir: str) -> None:
        """
        Change the output directory for scraped data.
        
        Args:
            output_dir: New output directory path
        """
        self.output_dir = Path(output_dir)
        self._clear_output_directory()
        logger.info(f"Output directory changed to: {self.output_dir}")
    
    def print_scraping_summary(self, business_profile: BusinessProfile) -> None:
        """
        Print a summary of the scraping results.
        
        Args:
            business_profile: Scraped business profile
        """
        print(f"\n🎉 Scraping completed!")
        print(f"Business: {business_profile.business_name_en}")
        print(f"Rating: {business_profile.rating}")
        print(f"Address: {business_profile.address}")
        print(f"Phone: {business_profile.phone}")
        print(f"Website: {business_profile.website}")
        print(f"Status: {business_profile.status}")
        
        # Print hours summary
        if business_profile.weekly_hours:
            print(f"Hours available for {len(business_profile.weekly_hours)} days")
        
        # Print features summary
        if business_profile.special_features:
            print(f"Special features: {len(business_profile.special_features)} items")
        
        # Print popular times summary
        if business_profile.popular_times:
            total_time_slots = sum(len(times) for times in business_profile.popular_times.values())
            print(f"Popular times: {total_time_slots} time slots across {len(business_profile.popular_times)} days")
        
        # Print output directory
        print(f"\n📁 Output saved to: {self.output_dir}")
        print(f"📄 Business profile: {self.output_dir / 'business_profile.json'}")
        
        # List all screenshot files
        screenshot_files = list(self.output_dir.glob("*.png"))
        if screenshot_files:
            print(f"📷 Screenshots captured: {len(screenshot_files)} files")
