#!/usr/bin/env python3
"""
Quick test script for the El País scraper with minimal output.
"""

import sys
import os
import warnings

# Suppress all warnings
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["PYTHONWARNINGS"] = "ignore"

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("🚀 El País Scraper - Quick Test")
    print("=" * 40)
    print("⏳ Initializing scraper...")
    
    from src.main import MainApplication
    
    print("⏳ Starting scraping workflow...")
    app = MainApplication()
    result = app.run_complete_workflow()
    
    print(f"\n✅ Complete! Processed {result.success_count} articles")
    if result.error_count > 0:
        print(f"⚠️  {result.error_count} warnings/errors")
    
    print(f"⏱️  Total time: {result.total_processing_time:.1f} seconds")
    print("\n📊 Check the 'scraped_data' folder for results!")
    
except KeyboardInterrupt:
    print("\n\n⏹️  Stopped by user")
except Exception as e:
    print(f"\n💥 Error: {str(e)}")
    sys.exit(1)
