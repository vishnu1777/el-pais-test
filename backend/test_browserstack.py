#!/usr/bin/env python3
"""
Test BrowserStack connection and WebDriver initialization.
"""

import sys
import os
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["PYTHONWARNINGS"] = "ignore"

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("🧪 BrowserStack Connection Test")
    print("=" * 40)
    
    from config.settings import settings
    from src.models.browserstack import BrowserStackCapability
    from selenium.webdriver import Remote
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    
    # Check credentials
    if not settings.browserstack_username or not settings.browserstack_access_key:
        print("❌ BrowserStack credentials not found in .env file")
        print("Please check BROWSERSTACK_USERNAME and BROWSERSTACK_ACCESS_KEY")
        sys.exit(1)
    
    print(f"👤 Username: {settings.browserstack_username}")
    print("🔑 Access Key: ***" + settings.browserstack_access_key[-4:])
    
    # Create test capability
    capability = BrowserStackCapability(
        browser="Chrome",
        browser_version="latest",
        os="Windows",
        os_version="10"
    )
    
    print(f"\n🚀 Testing connection with {capability.browser} {capability.browser_version}...")
    
    # Initialize WebDriver
    options = ChromeOptions()
    caps = capability.to_dict()
    
    # Set capabilities
    for key, value in caps.items():
        options.set_capability(key, value)
    
    # Add BrowserStack credentials
    if "bstack:options" in caps:
        bstack_options = caps["bstack:options"].copy()
        bstack_options["userName"] = settings.browserstack_username
        bstack_options["accessKey"] = settings.browserstack_access_key
        options.set_capability("bstack:options", bstack_options)
    
    driver = Remote(
        command_executor=f"https://{settings.browserstack_username}:{settings.browserstack_access_key}@hub-cloud.browserstack.com/wd/hub",
        options=options
    )
    
    print("✅ Connection successful!")
    print(f"📱 Session ID: {driver.session_id}")
    
    # Test basic navigation
    print("🌐 Testing navigation to Google...")
    driver.get("https://www.google.com")
    print(f"📄 Page title: {driver.title}")
    
    print("✅ All tests passed!")
    print(f"🔗 View session: https://automate.browserstack.com/dashboard/v2/sessions/{driver.session_id}")
    
    driver.quit()
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    if "driver" in locals():
        try:
            driver.quit()
        except:
            pass
    sys.exit(1)
