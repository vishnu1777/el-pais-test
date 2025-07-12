#!/usr/bin/env python3
"""
Test parallel BrowserStack execution with status reporting.
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
    print("🧪 BrowserStack Parallel Test (Limited)")
    print("=" * 50)
    
    from config.settings import settings
    from src.models.browserstack import BrowserStackCapability
    from src.browserstack_runner import BrowserStackRunner
    
    # Check credentials
    if not settings.browserstack_username or not settings.browserstack_access_key:
        print("❌ BrowserStack credentials not found")
        sys.exit(1)
    
    print(f"👤 Username: {settings.browserstack_username}")
    print("🔑 Access Key: ***" + settings.browserstack_access_key[-4:])
    
    # Create a custom runner with limited capabilities for testing
    class TestRunner(BrowserStackRunner):
        def get_test_capabilities(self):
            """Return only 2 capabilities for testing."""
            return [
                BrowserStackCapability(
                    browser="Chrome",
                    browser_version="latest",
                    os="Windows",
                    os_version="10",
                    resolution="1920x1080"
                ),
                BrowserStackCapability(
                    browser="Firefox",
                    browser_version="latest",
                    os="Windows",
                    os_version="10",
                    resolution="1920x1080"
                )
            ]
    
    print("\n🚀 Running limited parallel tests (2 browsers)...")
    print("This will test if status reporting works in parallel execution.")
    
    # Initialize runner
    runner = TestRunner()
    
    # Run parallel tests with just 2 workers
    results = runner.run_parallel_tests(max_workers=2)
    
    print(f"\n📊 Test Results:")
    print(f"Total: {len(results)}")
    
    passed_count = 0
    failed_count = 0
    
    for result in results:
        status = "✅ PASSED" if result.success else "❌ FAILED"
        browser_info = f"{result.capability.browser} {result.capability.browser_version}"
        
        if result.success:
            passed_count += 1
        else:
            failed_count += 1
        
        print(f"{status} | {browser_info} | Articles: {result.articles_scraped} | Time: {result.execution_time:.1f}s")
        
        if result.session_id:
            print(f"   🔗 Session: https://automate.browserstack.com/dashboard/v2/sessions/{result.session_id}")
        
        if result.error_message:
            print(f"   💥 Error: {result.error_message}")
        
        print()
    
    print(f"📈 Summary: {passed_count} passed, {failed_count} failed")
    print("\n🎯 Check your BrowserStack dashboard to verify session statuses!")
    print("Sessions should show as 'passed' or 'failed', not 'unknown'")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    sys.exit(1)
