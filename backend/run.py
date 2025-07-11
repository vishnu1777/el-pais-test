import argparse
import sys
from src.main import MainApplication
import os
# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from src.utils.logger import Logger


def run_scraping():
    """Run the complete scraping workflow."""
    print("🚀 Starting El País News Scraper")
    print("=" * 50)
    
    try:
        app = MainApplication()
        result = app.run_complete_workflow()
        
        if result.success_count > 0:
            print("\n✅ Scraping completed successfully!")
            print(f"📊 Results: {result.success_count} articles processed")
        else:
            print("\n❌ Scraping completed with errors")
            
    except Exception as e:
        Logger.error(f"Scraping failed: {str(e)}")
        print(f"\n💥 Error: {str(e)}")
        sys.exit(1)

def main():
    """Main CLI entry point or Server entry point"""
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
        ## create appropriate scaping function
        run_scraping()
    elif args.command == 'browserstack':
        ## create appropriate BrowserStack function
        pass
    elif args.command == 'serve':
        ## function to run server
        pass
    else:
        ## show user data in arg parser
        parser.print_help()


if __name__ == "__main__":
    main()
