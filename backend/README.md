# El País News Scraper Backend

A comprehensive web scraping application for El País news articles with BrowserStack integration, translation services, and a FastAPI backend.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Main Application](#main-application)
  - [API Server](#api-server)
  - [Test Scripts](#test-scripts)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This backend application provides:
- Web scraping of El País opinion articles
- BrowserStack cloud browser automation
- Text translation services
- Article analysis and content extraction
- RESTful API for frontend integration
- Comprehensive testing suite

## ✨ Features

- **Web Scraping**: Automated extraction of news articles from El País
- **Cross-Browser Testing**: BrowserStack integration with parallel execution
- **Translation**: Multi-language support using Google Translate and Deep Translator
- **Content Analysis**: Article text analysis and keyword extraction
- **Image Processing**: Automatic image downloading and processing
- **API Server**: FastAPI-based REST API
- **Status Reporting**: Real-time BrowserStack session status updates
- **Logging**: Comprehensive logging with file and console output

## 🔧 Prerequisites

- Python 3.8+
- BrowserStack account (for cloud testing)
- Chrome browser (for local testing)
- Git

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd project-browserStack/backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

1. **Create environment file**:
   ```bash
   copy .env.example .env  # Windows
   # cp .env.example .env  # Linux/Mac
   ```

2. **Configure environment variables** in `.env`:
   ```env
   # BrowserStack Configuration
   BROWSERSTACK_USERNAME=your_username
   BROWSERSTACK_ACCESS_KEY=your_access_key
   
   # API Keys (Optional)
   GOOGLE_TRANSLATE_API_KEY=your_google_api_key
   RAPID_API_KEY=your_rapid_api_key
   ```

3. **Verify configuration**:
   ```bash
   python -c "from config.settings import settings; print('Config loaded successfully')"
   ```

## 🚀 Usage

### Main Application

The main application provides several modes of operation:

#### 1. Complete Workflow
Run the full scraping pipeline with all features:
```bash
python run.py --mode scraping
```

#### 2. BrowserStack Mode
Run scraping using BrowserStack cloud browsers:
```bash
python run.py --mode browserstack
```

#### 3. API Server Mode
Start the FastAPI server for frontend integration:
```bash
python run.py --mode api
```

#### 4. Help
View all available options:
```bash
python run.py --help
```

### API Server

Start the FastAPI development server:
```bash
# Using run.py
python run.py --mode api

# Direct uvicorn
uvicorn src.api_server:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **Main API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

#### Available Endpoints:
- `GET /` - Health check
- `GET /articles` - Get scraped articles
- `GET /files` - List scraped files
- `GET /images` - List scraped images
- `POST /scrape` - Trigger new scraping
- `POST /scrape/browserstack` - Run BrowserStack scraping

### Test Scripts

The backend includes several test scripts for different scenarios:

#### 1. Local Scraper Test (`test_scraper.py`)
Tests the scraper functionality using local Chrome browser:
```bash
python test_scraper.py
```
- **Purpose**: Verify scraper works locally
- **Duration**: ~30 seconds
- **Requirements**: Local Chrome browser
- **Output**: Minimal console output, saves results to files

#### 2. Simple BrowserStack Test (`test_simple_browserstack.py`)
Basic BrowserStack connectivity and session test:
```bash
python test_simple_browserstack.py
```
- **Purpose**: Verify BrowserStack credentials and connectivity
- **Duration**: ~1-2 minutes
- **Requirements**: BrowserStack credentials
- **Features**: Basic navigation, status reporting
- **Output**: Session details and connection status

#### 3. BrowserStack Status Test (`test_browserstack_status.py`)
Full scraping workflow with BrowserStack and status reporting:
```bash
python test_browserstack_status.py
```
- **Purpose**: Test complete workflow on BrowserStack
- **Duration**: ~3-5 minutes
- **Requirements**: BrowserStack credentials
- **Features**: Full scraping, translation, status updates
- **Output**: Complete scraping results with session status

#### 4. Parallel BrowserStack Test (`test_parallel_browserstack.py`)
Tests parallel execution across multiple browsers:
```bash
python test_parallel_browserstack.py
```
- **Purpose**: Test concurrent BrowserStack sessions
- **Duration**: ~2-3 minutes
- **Requirements**: BrowserStack credentials (parallel testing plan)
- **Features**: Multiple browser configurations, parallel execution
- **Output**: Results from multiple sessions with status reporting

#### 5. Legacy BrowserStack Test (`test_browserstack.py`)
Original BrowserStack test (deprecated):
```bash
python test_browserstack.py
```
- **Purpose**: Legacy testing (use newer tests instead)
- **Note**: Kept for compatibility, use `test_simple_browserstack.py` instead

### Running Tests in Sequence

For comprehensive testing, run tests in this order:

1. **Local functionality**:
   ```bash
   python test_scraper.py
   ```

2. **BrowserStack connectivity**:
   ```bash
   python test_simple_browserstack.py
   ```

3. **Full BrowserStack workflow**:
   ```bash
   python test_browserstack_status.py
   ```

4. **Parallel execution** (if supported by your plan):
   ```bash
   python test_parallel_browserstack.py
   ```

## 📁 Project Structure

```
backend/
├── config/
│   ├── settings.py              # Application settings and configuration
│   └── __pycache__/
├── logs/                        # Log files
│   └── scraper_*.log
├── scraped_data/                # JSON output files
│   └── scraping_results_*.json
├── scraped_images/              # Downloaded images
│   └── images/
│       └── *.jpg
├── src/
│   ├── analyzer/
│   │   └── text_analyzer.py     # Text analysis and NLP
│   ├── models/
│   │   ├── article.py           # Article data models
│   │   └── browserstack.py      # BrowserStack configuration
│   ├── scraper/
│   │   └── el_pais_scraper.py   # Main scraping logic
│   ├── translator/
│   │   └── translation_service.py # Translation services
│   ├── utils/
│   │   ├── file_utils.py        # File operations
│   │   ├── helpers.py           # Utility functions
│   │   └── logger.py            # Logging configuration
│   ├── api_server.py            # FastAPI application
│   ├── browserstack_runner.py   # BrowserStack execution
│   └── main.py                  # Main application logic
├── tests/
│   └── test_main.py             # Unit tests
├── .env                         # Environment variables (create from .env.example)
├── requirements.txt             # Python dependencies
├── run.py                       # Main entry point
├── test_scraper.py              # Local scraper test
├── test_simple_browserstack.py  # Basic BrowserStack test
├── test_browserstack_status.py  # Full BrowserStack workflow test
├── test_parallel_browserstack.py # Parallel BrowserStack test
└── README.md                    # This file
```

## 🔍 Component Details

### Core Components

1. **El País Scraper** (`src/scraper/el_pais_scraper.py`)
   - Scrapes opinion articles from El País website
   - Handles both local and BrowserStack execution
   - Downloads and processes article images
   - Extracts article metadata and content

2. **BrowserStack Runner** (`src/browserstack_runner.py`)
   - Manages BrowserStack WebDriver sessions
   - Handles capability configuration for different browsers
   - Implements session status reporting
   - Supports both single and parallel execution

3. **Translation Service** (`src/translator/translation_service.py`)
   - Provides text translation using multiple services
   - Supports Google Translate and Deep Translator
   - Handles translation errors and fallbacks

4. **Text Analyzer** (`src/analyzer/text_analyzer.py`)
   - Analyzes article content for insights
   - Extracts keywords and themes
   - Provides content metrics

5. **API Server** (`src/api_server.py`)
   - FastAPI-based REST API
   - Serves scraped data to frontend
   - Provides endpoints for triggering scraping
   - Handles file uploads and downloads

### Data Models

1. **Article Model** (`src/models/article.py`)
   - Defines article data structure
   - Handles validation and serialization
   - Supports multiple output formats

2. **BrowserStack Model** (`src/models/browserstack.py`)
   - Defines browser capability configurations
   - Manages BrowserStack-specific settings
   - Handles capability generation for different browsers

### Utilities

1. **Logger** (`src/utils/logger.py`)
   - Configures application logging
   - Supports both file and console output
   - Provides different log levels

2. **File Utils** (`src/utils/file_utils.py`)
   - Handles file operations
   - Manages directory structure
   - Provides file validation

3. **Helpers** (`src/utils/helpers.py`)
   - Common utility functions
   - Data processing helpers
   - Validation utilities

## 🛠️ Troubleshooting

### Common Issues

1. **BrowserStack Connection Failed**
   ```
   Error: Could not connect to BrowserStack
   ```
   - **Solution**: Verify credentials in `.env` file
   - **Check**: BrowserStack account status and limits

2. **Chrome Driver Issues**
   ```
   Error: Chrome driver not found
   ```
   - **Solution**: Update Chrome browser to latest version
   - **Alternative**: Use BrowserStack mode instead

3. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'src'
   ```
   - **Solution**: Run scripts from the backend directory
   - **Check**: Python path configuration

4. **Permission Errors**
   ```
   PermissionError: [Errno 13] Permission denied
   ```
   - **Solution**: Run with appropriate permissions
   - **Check**: Directory write permissions

5. **BrowserStack Session Timeout**
   ```
   Error: Session timed out
   ```
   - **Solution**: Check network connectivity
   - **Increase**: Timeout values in settings

### Debug Mode

Enable debug logging by setting environment variable:
```bash
set LOG_LEVEL=DEBUG  # Windows
# export LOG_LEVEL=DEBUG  # Linux/Mac
```

### Verbose Output

Run scripts with Python's verbose flag:
```bash
python -v test_scraper.py
```

### Check Dependencies

Verify all dependencies are installed:
```bash
pip check
```

### Test BrowserStack Connectivity

Quick connectivity test:
```bash
python -c "from src.models.browserstack import BrowserStackCapabilities; print('BrowserStack config loaded')"
```

## 📊 Output Files

The application generates several types of output:

1. **Scraped Data**: `scraped_data/scraping_results_*.json`
2. **Images**: `scraped_images/images/*.jpg`
3. **Logs**: `logs/scraper_*.log`

### File Naming Convention

- **Data files**: `scraping_results_YYYYMMDD_HHMMSS.json`
- **Log files**: `scraper_YYYYMMDD_HHMMSS.log`
- **Image files**: `article_[id].jpg`

## 🔗 Integration with Frontend

The backend provides a REST API that integrates with the Vite.js frontend:

1. **Start the backend**:
   ```bash
   python run.py --mode api
   ```

2. **Start the frontend** (in separate terminal):
   ```bash
   cd ../frontend
   npm run dev
   ```

3. **Access the application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000

## 📝 Development Notes

- All test scripts suppress warnings for cleaner output
- BrowserStack sessions include automatic status reporting
- Parallel tests are limited to avoid plan limits
- Image downloads are handled asynchronously
- Translation services have fallback mechanisms

## 🤝 Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation as needed
4. Ensure all tests pass before submitting

---

For additional help or questions, please refer to the individual module documentation or check the logs for detailed error information.
