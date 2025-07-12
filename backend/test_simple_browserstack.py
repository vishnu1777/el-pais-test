#!/usr/bin/env python3
"""
Simple BrowserStack connection test with minimal capabilities.
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
    print("🧪 BrowserStack Simple Test")
    print("=" * 40)
    
    from config.settings import settings
    from selenium.webdriver import Remote
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    
    # Check credentials
    if not settings.browserstack_username or not settings.browserstack_access_key:
        print("❌ BrowserStack credentials not found")
        sys.exit(1)
    
    print(f"👤 Username: {settings.browserstack_username}")
    print("🔑 Access Key: ***" + settings.browserstack_access_key[-4:])
    
    # Create minimal capabilities
    options = ChromeOptions()
    
    # Set basic capabilities
    options.set_capability('browserName', 'Chrome')
    options.set_capability('browserVersion', 'latest')
    options.set_capability('os', 'Windows')
    options.set_capability('osVersion', '10')
    
    # Set BrowserStack options (minimal set)
    bstack_options = {
        'projectName': 'El País Scraper Test',
        'buildName': 'Simple Test Build',
        'sessionName': 'Simple Connection Test',
        'userName': settings.browserstack_username,
        'accessKey': settings.browserstack_access_key,
        'debug': True
    }
    options.set_capability('bstack:options', bstack_options)
    
    print("\n🚀 Connecting to BrowserStack...")
    
    # Initialize WebDriver
    driver = Remote(
        command_executor=f"https://{settings.browserstack_username}:{settings.browserstack_access_key}@hub-cloud.browserstack.com/wd/hub",
        options=options
    )
    
    print("✅ Connection successful!")
    print(f"📱 Session ID: {driver.session_id}")
    
    # Test basic navigation
    print("🌐 Testing navigation...")
    driver.get("https://www.google.com")
    print(f"📄 Page title: {driver.title}")
    
    print("✅ Navigation successful!")
    print(f"🔗 View session: https://automate.browserstack.com/dashboard/v2/sessions/{driver.session_id}")
    
    # Mark session as passed
    driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": "Simple test completed successfully"}}')
    print("✅ Session marked as passed")
    
    driver.quit()
    print("\n🎉 Test completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    if "driver" in locals():
        try:
            # Mark session as failed
            driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": "Test failed with error"}}')
            driver.quit()
        except:
            pass
    sys.exit(1)
