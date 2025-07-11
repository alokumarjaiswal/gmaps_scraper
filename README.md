# Google Maps Business Profile Scraper

A comprehensive, modular web scraper for extracting business information from Google Maps. Built with Playwright for reliable automation and data extraction.

## 🚀 Features

- **Tab Navigation**: Seamlessly navigates between Overview, Reviews, and About tabs to gather comprehensive data.
- **Comprehensive Data Extraction**: Extracts business name, rating, reviews, contact info, services URLs, hours, and detailed "About" tab information.
- **Popular Times Analysis**: Extracts busy times data for all days of the week.
- **Photo Category Screenshots**: Captures screenshots of all photo category tabs.
- **Modular Architecture**: Clean, maintainable code structure.
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
- `available`: A boolean indicating if the "Reviews" tab is present.
- `data`: Placeholder for future review data extraction.

### `about`

Contains detailed business attributes from the "About" tab, categorized for clarity.

- **`accessibility_features`**:
    - `available`: List of available accessibility features.
    - `unavailable`: List of unavailable accessibility features.
- **`service_options`**: List of service options (e.g., "In-store shopping").
- **`amenities`**: List of available amenities (e.g., "Mechanic", "Wi-Fi").
- **`crowd_info`**: Information about the typical crowd (e.g., "LGBTQ+ friendly").
- **`planning_info`**: Details for planning a visit (e.g., "Good for quick visit").
- **`payment_methods`**: Accepted payment types (e.g., "Credit cards", "Google Pay").
- **`parking_options`**: Available parking options (e.g., "Free street parking").

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
from scraper import GoogleMapsBusinessScraper

# Create scraper instance
scraper = GoogleMapsBusinessScraper(
    output_dir="custom_output"  # Custom output directory
)

# Scrape business data
business_profile = scraper.scrape_business("https://maps.google.com/...")

# Print summary
scraper.print_scraping_summary(business_profile)
```

### Configuration

Edit `config.py` to customize:
- Browser settings (headless mode, viewport size)
- Timeout values
- CSS selectors
- Output file names
- Photo extraction settings

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
│   ├── data_extractor.py     # Data extraction logic
│   └── photo_extractor.py    # Photo category screenshot capture
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
    "data": {}
  },
  "about": {
    "accessibility_features": {
      "available": ["Has wheelchair-accessible entrance"],
      "unavailable": ["No wheelchair-accessible parking"]
    },
    "service_options": ["In-store shopping", "Delivery"],
    "amenities": ["Wi-Fi", "Restroom"],
    "payment_methods": ["Credit cards", "Cash", "Mobile payments"]
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

### Photo Extraction
```python
PHOTO_CONFIG = {
    "screenshot_delay": 2000,   # Delay before taking screenshot (ms)
    "tab_click_delay": 1000    # Delay between tab clicks (ms)
}
```

## 🔧 Troubleshooting

### Common Issues

1. **"No such element" errors**
   - Google Maps layout may have changed
   - Update selectors in `config.py`
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

5. **Services URL not extracted**
   - Not all businesses have services URLs
   - Check if the business has a "Services" link on their Google Maps page
   - Look for "Services URL extracted: [URL or Not found]" in the logs

6. **Python 3.13 Compatibility Issues**
   - Use: `pip install playwright==1.40.0` for best compatibility
   - Ensure all dependencies are up to date

### Debugging

Enable detailed logging by modifying `utils/logging_config.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Development

### Adding New Features

1. **New data extraction**: Add methods to `core/data_extractor.py`
2. **New navigation**: Add methods to `core/navigator.py`  
3. **New data fields**: Update `models/business_profile.py`
4. **New configuration**: Add to `config.py`

### Code Style

The project follows Python best practices:
- Type hints for all functions
- Comprehensive error handling
- Modular, reusable components
- Clear logging and documentation

## 🏃‍♂️ Recent Updates

### Version 3.0.0 (Latest)
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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues, questions, or contributions:
- Check the troubleshooting section
- Review the logs in `gmaps_scraper.log`
- Open an issue with detailed error information

---

**Author**: GitHub Copilot & Development Team  
**Version**: 3.0.0  
**Last Updated**: July 2025  
**Python Compatibility**: 3.8+ (Tested with 3.13)
