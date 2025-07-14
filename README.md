# Google Maps Business Profile Scraper

A comprehensive, modular web scraper for extracting business information from Google Maps. Built with Playwright for reliable automation and data extraction.

## 🚀 Features

- **Tab Navigation**: Seamlessly navigates between Overview, Reviews, and About tabs to gather comprehensive data.
- **Comprehensive Data Extraction**: Extracts business name, rating, reviews, contact info, services URLs, hours, and detailed "About" tab information.
- **Media URL Extraction**: Extracts actual photo and video URLs from each photo category tab (All, Inside, Videos, By owner, Street View & 360°).
- **Advanced Review Analysis**:
    - Extracts all reviews by dynamically scrolling and clicking "More" buttons.
    - Utilizes a multi-pass strategy to expand and capture full review text and owner responses.
    - Gathers detailed data for each review: reviewer info, rating, full text, photos, and owner's reply.
- **Popular Times Analysis**: Extracts busy times data for all days of the week.
- **Photo Category Screenshots**: Captures screenshots of all photo category tabs.
- **Modular Architecture**: Clean, maintainable code structure with specialized extractors.
- **Robust Error Handling**: Graceful handling of various edge cases.
- **Windows Compatible**: Optimized for Windows console output.
- **Detailed Logging**: Comprehensive logging with visual indicators.
- **Python 3.13 Compatible**: Fully tested with the latest Python version.

## 📊 Data Extracted

The scraper outputs a single JSON file organized by tabs, mirroring the structure of a Google Maps business page.

### `overview`

Contains all data from the main "Overview" tab.

- **`basic_info`**:
    - Business name (English & Hindi if available)
    - Hero image URL
    - Rating and review count
    - Business type/category
- **`contact_info`**:
    - Full address
    - Phone number
    - Services URL (links to additional business services)
    - Website URL
    - Plus code
- **`operational_info`**:
    - Current status (Open/Closed)
    - Weekly operating hours
- **`additional_info`**:
    - Special features (e.g., "LGBTQ+ friendly")
    - Popular times (hourly busy percentages for all days)

### `reviews`

- **`available`**: A boolean indicating if the "Reviews" tab is present.
- **`data`**: Contains detailed information about the reviews.
    - **`total_reviews`**: The total number of reviews found.
    - **`reviews`**: A list of review objects, each containing:
        - **`reviewer_photo_url`**: URL of the reviewer's profile picture.
        - **`reviewer_name`**: Name of the reviewer.
        - **`reviewer_details`**: Additional details like "Local Guide" or number of reviews.
        - **`rating`**: The star rating given by the reviewer.
        - **`review_time`**: When the review was posted (e.g., "a year ago").
        - **`review_text`**: The full text of the review.
        - **`review_photos`**: A list of URLs for photos attached to the review.
        - **`owner_response`**: An object containing the business owner's reply.
            - **`response_text`**: The full text of the owner's response.
            - **`response_time`**: When the owner responded.

### `about`

Contains detailed business attributes from the "About" tab, categorized for clarity.

- **`accessibility_features`**:
    - `available`: List of available accessibility features.
    - `unavailable`: List of unavailable accessibility features.
- **`service_options`**: List of service options (e.g., "In-store shopping").
- **`amenities`**: List of available amenities (e.g., "Mechanic", "Wi-Fi").
- **`crowd_info`**: Information about the typical crowd (e.g., "LGBTQ+ friendly").
- **`planning_info`**: Details for planning a visit (e.g., "Good for quick visit").
    - Payment methods: Accepted payment types (e.g., "Credit cards", "Google Pay").
    - Parking options: Available parking options (e.g., "Free street parking").

### `photos_videos`

Contains actual media URLs extracted from each photo category tab:

- **`all`**: List of photo/video URLs from "All" tab
- **`inside`**: List of photo URLs from "Inside" tab  
- **`videos`**: List of video data with URLs, poster images, and metadata from "Videos" tab
- **`by_owner`**: List of photo URLs from "By owner" tab
- **`street_view_360`**: List of photo URLs from "Street View & 360°" tab

Each photo entry contains:
- `photo_index`: Index of the photo
- `description`: Photo description from aria-label
- `high_quality_url`: High-resolution image URL (when loaded)
- `thumbnail_url`: Thumbnail image URL

Each video entry contains:
- `video_url`: Direct video file URL
- `poster_url`: Video thumbnail/poster image URL
- `format`: Video format information
- `docid`: Document ID
- `cpn`: Content playback nonce

### Photo Categories
- Screenshots of each photo category tab (All, Inside, Videos, By owner, Street View & 360°)
- Visual capture of all available photo sections

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher (tested with Python 3.13)
- Windows 10/11 (optimized for Windows)

### Quick Setup

1. **Clone or download the project**
```bash
git clone "https://github.com/alokumarjaiswal/gmaps_scraper.git"
cd gmaps_scraper
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Playwright browsers**
```bash
playwright install
```

## 🎯 Usage

### Basic Usage

1. **Update the target URL** in `main.py`:
```python
business_url = "YOUR_GOOGLE_MAPS_BUSINESS_URL_HERE"
```

2. **Run the scraper**:
```bash
python main.py
```

### Advanced Usage

```python
from core.extractors.data_extractor import DataExtractor

# Create extractor instance (now uses modular architecture)
extractor = DataExtractor(page)

# Each method delegates to specialized extractors
basic_info = extractor.extract_basic_info()        # → BasicInfoExtractor
contact_info = extractor.extract_contact_info()    # → ContactExtractor
reviews = extractor.extract_reviews_tab_info()     # → ReviewsExtractor
```

### Configuration

Edit `config.py` to customize all aspects of the scraper:
- **Browser settings**: Headless mode, viewport size, user agent, launch arguments
- **Timeout values**: Page load, element wait, screenshots, navigation
- **CSS selectors**: All Google Maps elements (centrally managed for easy updates)
- **Output configuration**: File names and directory structure
- **Photo extraction settings**: Delays, thresholds, load times
- **Logging configuration**: Level, format, output

#### Selector Management
All CSS selectors are now centrally managed in `config.py` under the `SELECTORS` dictionary:
```python
SELECTORS = {
    # Basic business info
    "business_name_en": "h1.DUwDvf",
    "rating": '.F7nice span[aria-hidden="true"]',
    
    # Review extraction
    "review_container": 'div.jftiEf[data-review-id]',
    "review_more_button": 'button.w8nwRe.kyuRq[aria-label="See more"]',
    "reviewer_name_div": 'div.d4r55',
    
    # And many more...
}
```

This centralized approach makes it easy to update selectors when Google Maps changes their HTML structure.

## 📁 Project Structure

```
gmaps_scraper/
├── main.py                 # Main entry point
├── scraper.py             # Main scraper orchestration
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
│
├── core/                 # Core scraping modules
│   ├── __init__.py
│   ├── browser_manager.py    # Browser lifecycle management
│   ├── navigator.py          # Google Maps navigation
│   ├── photo_extractor.py    # Photo category screenshot capture
│   │
│   └── extractors/          # Modular data extraction components
│       ├── __init__.py
│       ├── data_extractor.py       # Main extraction orchestrator
│       ├── base_extractor.py       # Base class for all extractors
│       ├── basic_info_extractor.py # Basic business information
│       ├── contact_extractor.py    # Contact and location details
│       ├── operational_extractor.py # Hours, status, special features
│       ├── popular_times_extractor.py # Popular times data
│       ├── about_extractor.py      # About tab detailed information
│       ├── reviews_extractor.py    # Reviews extraction with full text expansion
│       └── media_extractor.py      # Photo and video URL extraction
│
├── models/               # Data models
│   ├── __init__.py
│   └── business_profile.py   # Business profile data structure
│
├── utils/                # Utility functions
│   ├── __init__.py
│   ├── helpers.py           # Helper functions
│   └── logging_config.py    # Logging configuration
│
└── output/               # Output directory (created during run)
    ├── {business_name}.json  # Business profile data
    └── photo_tab_*.png       # Screenshot of each photo category
```

### 🏗️ Modular Extractor Architecture

The scraper now features a **modular extractor architecture** with single responsibility principle:

- **`DataExtractor`**: Main orchestrator that coordinates all specialized extractors
- **`BaseExtractor`**: Common base class providing shared functionality and imports
- **`BasicInfoExtractor`**: Extracts hero image, business names, rating, reviews, business type, accessibility
- **`ContactExtractor`**: Handles address, phone, website, plus code, services URL extraction
- **`OperationalExtractor`**: Manages status, weekly hours, and special features extraction
- **`PopularTimesExtractor`**: Specialized extraction of busy times data with day navigation
- **`AboutExtractor`**: Comprehensive About tab information categorization and extraction
- **`ReviewsExtractor`**: Advanced review extraction with multi-pass expansion and owner responses
- **`MediaExtractor`**: Extracts actual photo and video URLs from all photo category tabs

This architecture provides:
- ✅ **Better maintainability**: Each extractor focuses on one responsibility
- ✅ **Easier testing**: Individual components can be tested in isolation
- ✅ **Enhanced extensibility**: New extractors can be added without affecting existing ones
- ✅ **Cleaner code**: Logical separation of concerns

## 📤 Output Files

The scraper generates several output files in the `output/` directory:

### 1. `{business_name}.json`
Complete business data in tab-organized JSON format:
```json
{
  "overview": {
    "basic_info": {
      "hero_image_url": "https://example.com/image.jpg",
      "business_name_en": "Business Name",
      "business_name_hi": "व्यापार का नाम",
      "rating": "4.5",
      "review_count": "(123)",
      "business_type": "Restaurant"
    },
    "contact_info": {
      "address": "123 Main St, City, State 12345",
      "phone": "+1 234-567-8900",
      "services_url": "https://example.com/services",
      "website": "https://example.com",
      "plus_code": "ABCD+12 City, State"
    },
    "operational_info": {
      "status": "Open ⋅ Closes 9 pm",
      "weekly_hours": {
        "Monday": "9:00 AM – 9:00 PM",
        "Tuesday": "9:00 AM – 9:00 PM"
      }
    },
    "additional_info": {
      "special_features": ["Wheelchair accessible entrance"],
      "popular_times": {
        "Monday": [
          {"time": "9 AM", "busy_percentage": 25},
          {"time": "10 AM", "busy_percentage": 45}
        ]
      }
    }
  },
  "reviews": {
    "available": true,
    "data": {
      "total_reviews": 41,
      "reviews": [
        {
          "reviewer_photo_url": "https://lh3.googleusercontent.com/...",
          "reviewer_name": "John Doe",
          "reviewer_details": "Local Guide · 25 reviews · 15 photos",
          "rating": "5",
          "review_time": "2 months ago",
          "review_text": "Excellent service! The staff was very helpful and knowledgeable...",
          "review_photos": [
            "https://lh3.googleusercontent.com/photo1.jpg",
            "https://lh3.googleusercontent.com/photo2.jpg"
          ],
          "owner_response": {
            "response_text": "Thank you for your kind words! We appreciate your business...",
            "response_time": "2 months ago"
          }
        }
      ]
    }
  },
  "about": {
    "accessibility_features": {
      "available": ["Has wheelchair-accessible entrance"],
      "unavailable": ["No wheelchair-accessible parking"]
    },
    "service_options": ["In-store shopping", "Delivery"],
    "amenities": ["Wi-Fi", "Restroom"],
    "payment_methods": ["Credit cards", "Cash", "Mobile payments"]
  },
  "photos_videos": {
    "all": [
      {
        "photo_index": "0",
        "description": "Photo of restaurant interior",
        "high_quality_url": "https://lh3.googleusercontent.com/photo_hq.jpg",
        "thumbnail_url": "https://lh3.googleusercontent.com/photo_thumb.jpg"
      }
    ],
    "inside": [
      {
        "photo_index": "1", 
        "description": "Interior dining area",
        "high_quality_url": "https://lh3.googleusercontent.com/inside_hq.jpg",
        "thumbnail_url": "https://lh3.googleusercontent.com/inside_thumb.jpg"
      }
    ],
    "videos": [
      {
        "video_url": "https://lh3.googleusercontent.com/video.mp4",
        "poster_url": "https://lh3.googleusercontent.com/video_poster.jpg",
        "format": "18",
        "docid": "",
        "cpn": "abc123"
      }
    ],
    "by_owner": [],
    "street_view_360": []
  }
}
```

### 2. Photo Category Screenshots
- `photo_tab_all.png`: Screenshot of "All" photos tab
- `photo_tab_inside.png`: Screenshot of "Inside" photos tab
- `photo_tab_videos.png`: Screenshot of "Videos" tab
- `photo_tab_by_owner.png`: Screenshot of "By owner" photos tab
- `photo_tab_street_view_&_360°.png`: Screenshot of "Street View & 360°" tab

## ⚙️ Configuration Options

### Browser Settings
```python
BROWSER_CONFIG = {
    "headless": False,          # Run browser visibly
    "slow_mo": 50,             # Delay between actions (ms)
    "viewport": {"width": 1280, "height": 800}
}
```

### Timeout Settings
```python
TIMEOUTS = {
    "page_load": 60000,        # Page load timeout
    "element_wait": 30000,     # Element wait timeout
    "action_wait": 5000        # Action timeout
}
```

### Media Extraction Settings
```python
MEDIA_CONFIG = {
    "max_media_per_tab": 50,    # Maximum number of media items to extract per tab
    "scroll_wait": 1000,        # Wait time between scrolls (ms)
    "lazy_load_wait": 2000,     # Wait for lazy loading content (ms)
    "container_scroll_step": 300 # Pixels to scroll each step
}

MEDIA_SELECTORS = {
    "photo_gallery_container": '[data-photo-index="0"]',  # Gallery container for scrolling
    "photo_container": 'div[data-photo-index]',           # Individual photo containers
    "video_iframe": 'iframe.widget-scene-imagery-iframe', # Video iframe selector
    "video_element": 'video'                              # Video element inside iframe
}
```

## 🔧 Troubleshooting

### Common Issues

1. **"No such element" errors**
   - Google Maps layout may have changed
   - Update selectors in `config.py` under the `SELECTORS` dictionary
   - All selectors are now centrally managed for easy maintenance
   - Check if business page loaded correctly

2. **Browser crashes**
   - Increase timeout values in `config.py`
   - Run in headless mode by modifying browser settings
   - Check available system memory

3. **Empty data extraction**
   - Verify the Google Maps URL is correct
   - Check if business page is publicly accessible
   - Review console logs for specific errors

4. **Photo extraction fails**
   - Some businesses may have limited photo categories
   - Check network connectivity
   - Verify photo tab navigation is working

5. **Media URL extraction issues**
   - Some photo categories may be empty for certain businesses
   - Video extraction requires iframe content access which may be restricted
   - Check logs for "Found X photos/videos" messages
   - Verify that photo gallery containers are properly detected

6. **Review extraction incomplete**
   - Some reviews may have collapsed text that requires multiple "More" button clicks
   - The scraper uses a multi-pass strategy to expand all content
   - Check logs for "More button" click attempts and success rates

6. **Services URL not extracted**
   - Not all businesses have services URLs
   - Check if the business has a "Services" link on their Google Maps page
   - Look for "Services URL extracted: [URL or Not found]" in the logs

7. **Python 3.13 Compatibility Issues**
   - Use: `pip install playwright==1.40.0` for best compatibility
   - Ensure all dependencies are up to date

### Debugging

Enable detailed logging by modifying the `LOGGING_CONFIG` in `config.py`:
```python
LOGGING_CONFIG = {
    "level": "DEBUG",  # Change from "INFO" to "DEBUG"
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "encoding": "utf-8"
}
```

## 📝 Development

### Adding New Features

1. **New data extraction**: 
   - Create a new specialized extractor in `core/extractors/`
   - Inherit from `BaseExtractor` for shared functionality
   - Add to `DataExtractor` orchestrator for integration
2. **New navigation**: Add methods to `core/navigator.py`  
3. **New data fields**: Update `models/business_profile.py`
4. **New configuration**: Add to `config.py`
5. **New selectors**: Add CSS selectors to the `SELECTORS` dictionary in `config.py`

### Creating Custom Extractors

To add a new extractor module:

```python
# core/extractors/custom_extractor.py
from .base_extractor import BaseExtractor

class CustomExtractor(BaseExtractor):
    """Extract custom business information."""
    
    def extract_custom_data(self) -> Dict[str, Any]:
        """Extract custom data from the page."""
        logger.info("Extracting custom data...")
        
        try:
            # Use inherited helper methods and imports
            element = self.page.locator(self.selectors["custom_selector"]).first
            data = self.safe_extract_text(element)
            
            logger.info("✅ Custom data extracted successfully")
            return {"custom_field": data}
            
        except Exception as e:
            logger.error(f"❌ Error extracting custom data: {e}")
            return {}
```

Then integrate it into the main `DataExtractor`:

```python
# core/extractors/data_extractor.py
from .custom_extractor import CustomExtractor

class DataExtractor:
    def __init__(self, page: Page):
        # ...existing extractors...
        self.custom_extractor = CustomExtractor(page)
    
    def extract_custom_data(self) -> Dict[str, Any]:
        return self.custom_extractor.extract_custom_data()
```

### Updating Selectors

When Google Maps changes their HTML structure:
1. Open `config.py`
2. Locate the `SELECTORS` dictionary
3. Update the relevant CSS selector
4. All modules will automatically use the updated selector

### Code Style

## 🏃‍♂️ Recent Updates

### Version 5.1.0 (Latest - Media URL Extraction)
- ✅ **New Media Extractor**: Added dedicated `MediaExtractor` for extracting actual photo and video URLs
- ✅ **Photo URL Extraction**: Extracts high-quality and thumbnail URLs from all photo category tabs
- ✅ **Video URL Extraction**: Extracts video URLs, poster images, and metadata from Videos tab using iframe content access
- ✅ **Container-Specific Scrolling**: Implemented proper gallery container scrolling to trigger lazy loading
- ✅ **Comprehensive Media Coverage**: Supports All, Inside, Videos, By owner, and Street View & 360° tabs
- ✅ **Enhanced Data Structure**: Added `photos_videos` section to output with organized media URLs
- ✅ **Simplified Video Logic**: Streamlined video extraction following iframe → content frame → video element pattern
- ✅ **Media Configuration**: Added `MEDIA_CONFIG` and `MEDIA_SELECTORS` for easy customization

### Version 5.0.0 (Modular Architecture)
- Modular, reusable components
- Clear logging and documentation

## 🏃‍♂️ Recent Updates

### Version 5.0.0 (Latest - Modular Architecture)
- ✅ **Specialized Extractors**: 
  - `BasicInfoExtractor` - Business names, rating, type, accessibility
  - `ContactExtractor` - Address, phone, website, services URL
  - `OperationalExtractor` - Hours, status, special features
  - `PopularTimesExtractor` - Busy times with day navigation
  - `AboutExtractor` - Comprehensive About tab categorization
  - `ReviewsExtractor` - Advanced review processing with expansion
  - `MediaExtractor` - Photo and video URL extraction from all tabs
  - `BasicInfoExtractor` - Business names, rating, type, accessibility
  - `ContactExtractor` - Address, phone, website, services URL
  - `OperationalExtractor` - Hours, status, special features
  - `PopularTimesExtractor` - Busy times with day navigation
  - `AboutExtractor` - Comprehensive About tab categorization
  - `ReviewsExtractor` - Advanced review processing with expansion

### Version 4.1.0
- ✅ **Centralized Selector Management**: All CSS selectors moved to `config.py` for improved maintainability
- ✅ **Enhanced Configuration Architecture**: Complete elimination of hardcoded selectors from data extraction modules
- ✅ **Better Code Organization**: 18+ new selector definitions added to centralized configuration
- ✅ **Improved Maintainability**: Easy updates when Google Maps changes their HTML structure
- ✅ **Developer-Friendly**: All selectors now documented and organized by functionality

### Version 4.0.0
- ✅ **Complete Review Extraction**: Fully implemented review data extraction with dynamic loading and multi-pass expansion strategy
- ✅ **Advanced Text Expansion**: Multi-pass "More" button clicking to ensure complete review text and owner response extraction
- ✅ **Comprehensive Review Data**: Extracts reviewer info, ratings, full text, photos, and owner responses for all reviews
- ✅ **Dynamic Review Loading**: Automatically scrolls and loads all available reviews without hardcoded limits
- ✅ **Intelligent Deduplication**: Uses unique data-review-id attributes to prevent duplicate review extraction

### Version 3.1.0
- ✅ **Enhanced Configuration System**: Fully integrated centralized configuration system with all components using `config.py`
- ✅ **Improved Modularity**: Browser, logging, and photo extraction now use consistent configuration values
- ✅ **Type-Safe Parameter Handling**: Added robust type handling and defaults for all configurable parameters
- ✅ **Better Developer Experience**: Easier customization through a single configuration file

### Version 3.0.0
- ✅ **Tab-Organized JSON Output**: Complete restructure of output format organized by Google Maps tabs (Overview, Reviews, About)
- ✅ **Enhanced About Tab Extraction**: Comprehensive extraction of accessibility features, service options, amenities, and payment methods
- ✅ **Advanced Tab Navigation**: Intelligent navigation between Overview, Reviews, and About tabs with robust detection
- ✅ **Improved Data Structure**: More logical organization mirroring the actual Google Maps interface
- ✅ **Services URL Positioning**: Properly positioned services_url above website in contact information

### Version 2.2.0
- ✅ **Services URL Extraction Fix**: Fixed missing services_url in business profile output
- ✅ **Enhanced Data Completeness**: Now properly captures and saves all contact information
- ✅ **Improved Logging**: Added detailed logging for services URL extraction
- ✅ **Bug Fixes**: Resolved issue where services_url was extracted but not saved to JSON output

### Key Improvements
- **Photo screenshots** instead of URL extraction (more reliable)
- **Synchronous execution** throughout (no async/await complexity)
- **Better Windows compatibility** with proper path handling
- **Comprehensive logging** with visual status indicators

## 📄 License

This project is for educational and research purposes. Please respect Google's Terms of Service and use responsibly.

**Author**: Alok Kumar Jaiswal  
**Version**: 5.1.0  
**Last Updated**: July 2025  
**Python Compatibility**: 3.8+ (Tested with 3.13)
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues, questions, or contributions:
- Check the troubleshooting section
- Review the logs in `gmaps_scraper.log`
- Open an issue with detailed error information

---

**Author**: Alok Kumar Jaiswal  
**Version**: 5.0.0  
**Last Updated**: July 2025  
**Python Compatibility**: 3.8+ (Tested with 3.13)
