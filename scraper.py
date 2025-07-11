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
                
                # Check tab availability
                tab_availability = self.navigator.check_tab_availability()
                
                # PHASE 1: Extract ALL data from Overview tab (default tab) - INCLUDING PHOTOS
                logger.info("🔍 PHASE 1: Extracting all data from Overview tab...")
                basic_info = self.data_extractor.extract_basic_info()
                contact_info = self.data_extractor.extract_contact_info()
                operational_info = self.data_extractor.extract_operational_info()
                special_features = self.data_extractor.extract_special_features()
                popular_times = self.data_extractor.extract_popular_times()
                
                # Extract photos (screenshots) - also from Overview tab
                self.photo_extractor.extract_photo_categories()
                
                # PHASE 2: Reload business page to get fresh state for tab navigation
                logger.info("🔄 PHASE 2: Reloading business page for fresh navigation state...")
                self.navigator.reload_business_page()
                
                # Re-check tab availability after reload
                tab_availability = self.navigator.check_tab_availability()
                
                # PHASE 3: Navigate to Reviews tab for verification
                if tab_availability.get('Reviews', False):
                    logger.info("🔍 PHASE 3: Navigating to Reviews tab for verification...")
                    if self.navigator.navigate_to_tab("Reviews"):
                        logger.info("✅ Reviews tab accessible - continuing to About tab")
                    else:
                        logger.warning("⚠️ Could not access Reviews tab")
                else:
                    logger.warning("⚠️ Reviews tab not available on this business page")
                
                # PHASE 4: Navigate to About tab and extract detailed information
                about_info = {}
                if tab_availability.get('About', False):
                    logger.info("🔍 PHASE 4: Navigating to About tab for detailed data extraction...")
                    if self.navigator.navigate_to_tab("About"):
                        about_info = self.data_extractor.extract_about_tab_info()
                    else:
                        logger.warning("⚠️ Could not access About tab")
                else:
                    logger.warning("⚠️ About tab not available on this business page")
                
                # Create business profile with tab-organized structure
                overview_data = {
                    "basic_info": {
                        "hero_image_url": basic_info.get('hero_image_url'),
                        "business_name_en": basic_info.get('business_name_en'),
                        "business_name_hi": basic_info.get('business_name_hi'),
                        "rating": basic_info.get('rating'),
                        "review_count": basic_info.get('review_count'),
                        "business_type": basic_info.get('business_type')
                    },
                    "contact_info": {
                        "address": contact_info.get('address'),
                        "phone": contact_info.get('phone'),
                        "services_url": contact_info.get('services_url'),
                        "website": contact_info.get('website'),
                        "plus_code": contact_info.get('plus_code')
                    },
                    "operational_info": {
                        "status": operational_info.get('status'),
                        "weekly_hours": operational_info.get('weekly_hours'),
                        "wheelchair_accessible": operational_info.get('wheelchair_accessible', False)
                    },
                    "additional_info": {
                        "special_features": special_features,
                        "popular_times": popular_times
                    }
                }
                
                reviews_data = {
                    "available": tab_availability.get('Reviews', False),
                    "data": {}  # Will be populated when Reviews extraction is implemented
                }
                
                business_profile = BusinessProfile(
                    overview=overview_data,
                    reviews=reviews_data,
                    about=about_info
                )
                
                
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
            overview = business_profile.overview or {}
            basic_info = overview.get('basic_info', {})
            business_name = basic_info.get('business_name_en') or "unknown_business"
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
        overview = business_profile.overview or {}
        basic_info = overview.get('basic_info', {})
        contact_info = overview.get('contact_info', {})
        operational_info = overview.get('operational_info', {})
        additional_info = overview.get('additional_info', {})
        about = business_profile.about or {}
        
        print(f"\n🎉 Scraping completed!")
        print(f"Business: {basic_info.get('business_name_en')}")
        print(f"Rating: {basic_info.get('rating')}")
        print(f"Address: {contact_info.get('address')}")
        print(f"Phone: {contact_info.get('phone')}")
        print(f"Website: {contact_info.get('website')}")
        print(f"Status: {operational_info.get('status')}")
        
        # Print hours summary
        weekly_hours = operational_info.get('weekly_hours')
        if weekly_hours:
            print(f"Hours available for {len(weekly_hours)} days")
        
        # Print features summary
        special_features = additional_info.get('special_features')
        if special_features:
            print(f"Special features: {len(special_features)} items")
        
        # Print About tab information summary
        about_summary = []
        accessibility_features = about.get('accessibility_features')
        if accessibility_features:
            available_count = len(accessibility_features.get('available', []))
            unavailable_count = len(accessibility_features.get('unavailable', []))
            about_summary.append(f"Accessibility: {available_count} available, {unavailable_count} unavailable")
        
        service_options = about.get('service_options')
        if service_options:
            about_summary.append(f"Service options: {len(service_options)} items")
        
        amenities = about.get('amenities')
        if amenities:
            about_summary.append(f"Amenities: {len(amenities)} items")
        
        payment_methods = about.get('payment_methods')
        if payment_methods:
            about_summary.append(f"Payment methods: {len(payment_methods)} items")
        
        parking_options = about.get('parking_options')
        if parking_options:
            about_summary.append(f"Parking: {len(parking_options)} items")
        
        if about_summary:
            print(f"About tab data: {', '.join(about_summary)}")
        
        # Print popular times summary
        popular_times = additional_info.get('popular_times')
        if popular_times:
            total_time_slots = sum(len(times) for times in popular_times.values())
            print(f"Popular times: {total_time_slots} time slots across {len(popular_times)} days")
        
        # Print output directory
        print(f"\n📁 Output saved to: {self.output_dir}")
        print(f"📄 Business profile: {self.output_dir / 'business_profile.json'}")
        
        # List all screenshot files
        screenshot_files = list(self.output_dir.glob("*.png"))
        if screenshot_files:
            print(f"📷 Screenshots captured: {len(screenshot_files)} files")
