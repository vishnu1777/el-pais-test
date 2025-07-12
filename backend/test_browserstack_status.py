#!/usr/bin/env python3
"""
Test BrowserStack with proper status reporting.
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
    print("🧪 BrowserStack Status Reporting Test")
    print("=" * 50)
    
    from config.settings import settings
    from src.models.browserstack import BrowserStackCapability
    from src.browserstack_runner import BrowserStackRunner
    
    # Check credentials
    if not settings.browserstack_username or not settings.browserstack_access_key:
        print("❌ BrowserStack credentials not found in .env file")
        print("Please check BROWSERSTACK_USERNAME and BROWSERSTACK_ACCESS_KEY")
        sys.exit(1)
    
    print(f"👤 Username: {settings.browserstack_username}")
    print("🔑 Access Key: ***" + settings.browserstack_access_key[-4:])
    
    # Create test capability - just one browser for testing
    capability = BrowserStackCapability(
        browser="Chrome",
        browser_version="latest",
        os="Windows",
        os_version="10"
    )
    
    print(f"\n🚀 Running single test with {capability.browser} {capability.browser_version}...")
    
    # Initialize runner
    runner = BrowserStackRunner()
    
    # Run single test
    result = runner.run_single_test(capability)
    
    if result.success:
        print("✅ Test completed successfully!")
        print(f"📊 Articles scraped: {result.articles_scraped}")
        print(f"⏱️  Execution time: {result.execution_time:.1f} seconds")
    else:
        print("❌ Test failed!")
        print(f"💥 Error: {result.error_message}")
    
    if result.session_id:
        print(f"\n🔗 View session in BrowserStack:")
        print(f"https://automate.browserstack.com/dashboard/v2/sessions/{result.session_id}")
        print("\n✅ Session status should now show as 'passed' or 'failed' instead of 'unknown'")
    
    print("\n🎯 Check your BrowserStack dashboard - the session should have a proper status!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    sys.exit(1)
