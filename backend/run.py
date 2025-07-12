#!/usr/bin/env python3
"""
Main entry point for the El País News Scraper application.
This script provides a CLI interface to run various operations.
"""

import sys
import os
import argparse
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import MainApplication
from src.browserstack_runner import main as browserstack_main
from src.api_server import app
from src.utils.logger import Logger


def run_scraping():
    """Run the complete scraping workflow."""
    print("🚀 Starting El País News Scraper")
    print("=" * 50)
    
    # Suppress Selenium and urllib3 warnings
    import warnings
    import logging
    import os
    
    warnings.filterwarnings("ignore")
    
    # Suppress specific loggers
    logging.getLogger("selenium").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("requests").setLevel(logging.ERROR)
    
    # Suppress Chrome GPU warnings
    os.environ["PYTHONWARNINGS"] = "ignore"
    
    try:
        app = MainApplication()
        result = app.run_complete_workflow()
        
        if result.success_count > 0:
            print("\n✅ Scraping completed successfully!")
            print(f"📊 Results: {result.success_count} articles processed")
            if result.error_count > 0:
                print(f"⚠️  Warnings: {result.error_count} minor issues encountered")
        else:
            print("\n❌ Scraping completed with errors")
            
    except Exception as e:
        Logger().error(f"Scraping failed: {str(e)}")
        print(f"\n💥 Error: {str(e)}")
        sys.exit(1)


def run_browserstack():
    """Run BrowserStack cross-browser tests."""
    print("🌐 Starting BrowserStack Tests")
    print("=" * 50)
    
    try:
        browserstack_main()
    except Exception as e:
        Logger.error(f"BrowserStack tests failed: {str(e)}")
        print(f"\n💥 Error: {str(e)}")
        sys.exit(1)


def run_api_server():
    """Start the API server."""
    print("🚀 Starting API Server")
    print("=" * 50)
    
    try:
        import uvicorn
        from config.settings import settings
        
        print(f"📡 Server starting at: http://localhost:{settings.api_port}")
        print(f"📖 API Documentation: http://localhost:{settings.api_port}/docs")
        print("\nPress Ctrl+C to stop the server")
        
        uvicorn.run(
            "src.api_server:app",
            host=settings.api_host,
            port=settings.api_port,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n⏹️  Server stopped by user")
    except Exception as e:
        Logger.error(f"API server failed: {str(e)}")
        print(f"\n💥 Error: {str(e)}")
        sys.exit(1)


def setup_environment():
    """Set up the environment and install dependencies."""
    print("🔧 Setting up environment...")
    
    try:
        # Create necessary directories
        os.makedirs("scraped_images", exist_ok=True)
        os.makedirs("scraped_data", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        # Copy .env.example to .env if it doesn't exist
        if not os.path.exists(".env"):
            if os.path.exists(".env.example"):
                import shutil
                shutil.copy(".env.example", ".env")
                print("📝 Created .env file from .env.example")
                print("⚠️  Please update .env with your API keys and credentials")
            else:
                print("⚠️  .env.example not found. Please create .env manually")
        
        print("✅ Environment setup complete!")
        
    except Exception as e:
        print(f"❌ Environment setup failed: {str(e)}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="El País News Scraper & Analyzer",
        epilog="Example usage: python run.py scrape"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scraping command
    subparsers.add_parser('scrape', help='Run the complete scraping workflow')
    
    # BrowserStack command
    subparsers.add_parser('browserstack', help='Run BrowserStack cross-browser tests')
    
    # API server command
    subparsers.add_parser('serve', help='Start the API server')
    
    # Setup command
    subparsers.add_parser('setup', help='Set up the environment')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    if args.command == 'scrape':
        run_scraping()
    elif args.command == 'browserstack':
        run_browserstack()
    elif args.command == 'serve':
        run_api_server()
    elif args.command == 'setup':
        setup_environment()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
