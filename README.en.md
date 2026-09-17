**English** | [简体中文](README.md)

# Amazon Review Analysis Tool
This is a web application for analyzing Amazon product reviews.
Development team: Haiyi IDC Team
Maintainer: @Ethan
Data source: reviews exported in bulk via Shulex
Format: .XLSX

# Wishing you smooth sailing and good health

## Features
- 📊 **Data Preprocessing**: Automatically cleans and standardizes Amazon review data
- 🌐 **Review Translation**: Intelligently translates English reviews into Chinese, supporting Google Translate and the Tencent Translation API
- 💾 **Smart Caching**: Automatically caches translation results to avoid repeated translation and improve efficiency
- 🎯 **Advanced Filtering**: Filter by brand, ASIN, rating, review type, and more
- 📈 **Statistical Analysis**: Comprehensive statistical analysis of review data, including sentiment analysis
- 🎯 **Keyword Matching**: Smart keyword matching and audience segmentation
- 📝 **Automated Reports**: AI-powered, one-click generation of professional analysis reports

## Installation
1. Install the dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
streamlit run Home.py
```

## Workflow
1. **Data Preprocessing**: Upload an Excel file; the data is cleaned and standardized automatically
2. **Review Translation**: Select the columns to translate and batch-translate English reviews into Chinese
3. **Statistical Analysis**: In-depth analysis of review data with visualizations
4. **Keyword Matching**: Segment audiences and analyze characteristics based on keywords
5. **Report Generation**: Automatically generate professional analysis reports and export data

## Translation Features
- Supports Google Translate (free) and the Tencent Translation API (more accurate)
- **Smart caching system**: Automatically caches translation results to avoid repeated translation, greatly improving efficiency
- **Advanced filtering**: Precisely filter reviews by brand, ASIN, rating, review type, and other dimensions
- **Row range control**: Set the start and end rows for translation to precisely control the scope
- Supports batch translation of multiple text columns
- Automatically splits long texts into segments for translation
- Smart error retry mechanism
- Real-time progress monitoring and cache hit statistics
- Supports Excel and TXT export

### Smart Caching
- **Automatic caching**: Translation results are saved to a local cache automatically
- **Cache expiration**: Entries expire automatically after 30 days, keeping cache usage under control
- **Cache statistics**: Real-time display of cache file count and size
- **Cache cleanup**: One-click cleanup of expired cache files
- **Cache hits**: Cached results are used first when translating, greatly improving speed

### Advanced Filtering
- **Brand filter**: Translate product reviews for selected brands
- **ASIN filter**: Translate reviews for selected products
- **Rating filter**: Filter reviews by rating level (1-5 stars)
- **Review type filter**: Filter by review type (positive/neutral/negative)
- **Row range filter**: Set the start and end rows for translation
- **Combined filters**: Multiple filter conditions can be used together
- **Filter statistics**: Real-time statistics for the filtered data

### Tencent Translation API Configuration
To use the Tencent Translation API for more accurate translation results:

1. **Get API keys**:
   - Sign in to the [Tencent Cloud console](https://console.cloud.tencent.com/)
   - Go to "Access Management" → "API Key Management"
   - Create a new API key
   - Copy the SecretId and SecretKey

2. **Enable the service**:
   - Make sure the Machine Translation service is enabled
   - Select "Tencent Translation API" on the translation page
   - Enter the SecretId and SecretKey

## Version History
- v1.3.0: Added smart caching and advanced filtering, greatly improving translation efficiency
- v1.2.0: Added review translation with support for Google Translate and the Tencent Translation API
- v1.1.2: Improved data processing and visualization
- v1.1.0: Initial feature implementation
