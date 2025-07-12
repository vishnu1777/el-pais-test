import concurrent.futures
import time
import requests
import base64
from typing import List, Dict, Any
from threading import Lock

from src.models.browserstack import BrowserStackCapability, TestResult
from src.scraper.el_pais_scraper import ElPaisScraper
from src.translator.translation_service import TranslationService
from src.analyzer.text_analyzer import TextAnalyzer
from src.utils.logger import Logger
from config.settings import settings


class BrowserStackRunner:
    """Manages parallel execution of tests on BrowserStack."""
    
    def __init__(self):
        self.logger = Logger()
        self.results_lock = Lock()
        self.test_results: List[TestResult] = []
        
        # Validate BrowserStack credentials
        if not settings.browserstack_username or not settings.browserstack_access_key:
            raise ValueError("BrowserStack credentials not configured. Please set BROWSERSTACK_USERNAME and BROWSERSTACK_ACCESS_KEY environment variables.")
    
    def _update_session_status(self, driver, status: str, reason: str = "") -> None:
        """Update the session status in BrowserStack dashboard using JavaScript executor."""
        try:
            if driver and driver.session_id:
                # Use BrowserStack's JavaScript executor for more reliable status updates
                script = f'browserstack_executor: {{"action": "setSessionStatus", "arguments": {{"status":"{status}", "reason": "{reason}"}}}}'
                driver.execute_script(script)
                
                # Add a small delay to ensure the status is processed
                time.sleep(1)
                
                self.logger.info(f"Session {driver.session_id} marked as {status}: {reason}")
        except Exception as e:
            self.logger.warning(f"Failed to update session status: {str(e)}")
    
    def _update_build_status(self, build_name: str, status: str) -> None:
        """Update the build status in BrowserStack dashboard."""
        try:
            # Get all builds to find the build ID
            url = "https://api.browserstack.com/automate/builds.json"
            
            # Create basic auth header
            credentials = f"{settings.browserstack_username}:{settings.browserstack_access_key}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/json"
            }
            
            # Get builds
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                builds = response.json()
                # Find the build with matching name
                build_id = None
                for build in builds:
                    if build.get("automation_build", {}).get("name") == build_name:
                        build_id = build["automation_build"]["hashed_id"]
                        break
                
                if build_id:
                    # Update build status
                    update_url = f"https://api.browserstack.com/automate/builds/{build_id}.json"
                    data = {"status": status}
                    
                    update_response = requests.put(update_url, json=data, headers=headers, timeout=10)
                    
                    if update_response.status_code == 200:
                        self.logger.info(f"Build '{build_name}' marked as {status}")
                    else:
                        self.logger.warning(f"Failed to update build status: {update_response.status_code}")
                else:
                    self.logger.warning(f"Build '{build_name}' not found")
            else:
                self.logger.warning(f"Failed to get builds: {response.status_code}")
                
        except Exception as e:
            self.logger.warning(f"Failed to update build status: {str(e)}")

    def get_test_capabilities(self) -> List[BrowserStackCapability]:
        """Define the test capabilities for different browser/OS combinations."""
        return [
            # Desktop browsers
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
            ),
            BrowserStackCapability(
                browser="Safari",
                browser_version="latest",
                os="OS X",
                os_version="Big Sur",
                resolution="1920x1080"
            ),
            # Mobile browsers
            BrowserStackCapability(
                browser="Chrome",
                browser_version="latest",
                os="android",
                os_version="11.0",
                device="Samsung Galaxy S21",
                real_mobile=True
            ),
            BrowserStackCapability(
                browser="Safari",
                browser_version="latest",
                os="ios",
                os_version="15",
                device="iPhone 13",
                real_mobile=True
            )
        ]
    
    def run_single_test(self, capability: BrowserStackCapability) -> TestResult:
        """Run a single test on BrowserStack with given capability."""
        start_time = time.time()
        session_id = None
        scraper = None
        
        try:
            self.logger.info(f"Starting test on {capability.browser} {capability.browser_version} - {capability.os} {capability.os_version}")
            
            # Initialize scraper with BrowserStack capabilities
            scraper = ElPaisScraper(headless=False, browser=capability.browser.lower())
            
            # Scrape articles
            articles = scraper.scrape_articles(capabilities=capability.to_dict())
            
            # Get session ID for BrowserStack dashboard
            if scraper.driver:
                session_id = scraper.driver.session_id
            
            execution_time = time.time() - start_time
            
            # Determine success based on articles scraped
            success = len(articles) > 0
            
            # Update session status in BrowserStack BEFORE closing driver
            if scraper and scraper.driver:
                status = "passed" if success else "failed"
                reason = f"Scraped {len(articles)} articles successfully" if success else "No articles scraped"
                self._update_session_status(scraper.driver, status, reason)
                
                # Ensure status is sent before closing
                self.logger.info(f"Waiting for status update to be processed...")
                time.sleep(2)  # Give more time for status to be processed
            
            # Close the driver after status update
            if scraper and scraper.driver:
                scraper.close()
            
            result = TestResult(
                capability=capability,
                success=success,
                execution_time=execution_time,
                articles_scraped=len(articles),
                session_id=session_id
            )
            
            self.logger.info(f"Test completed successfully on {capability.browser} - {len(articles)} articles scraped")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_message = str(e)
            
            # Get session ID if available for error reporting
            if scraper and scraper.driver:
                try:
                    session_id = scraper.driver.session_id
                except:
                    session_id = None
            
            # Update session status as failed in BrowserStack BEFORE closing
            if scraper and scraper.driver:
                self._update_session_status(scraper.driver, "failed", f"Test failed: {error_message}")
                
                # Ensure status is sent before closing
                time.sleep(2)
            
            # Close the driver after status update
            if scraper and scraper.driver:
                try:
                    scraper.close()
                except:
                    pass
            
            result = TestResult(
                capability=capability,
                success=False,
                execution_time=execution_time,
                articles_scraped=0,
                error_message=error_message,
                session_id=session_id
            )
            
            self.logger.error(f"Test failed on {capability.browser}: {error_message}")
            return result
    
    def run_parallel_tests(self, max_workers: int = 5) -> List[TestResult]:
        """Run tests in parallel across multiple BrowserStack sessions."""
        capabilities = self.get_test_capabilities()
        
        self.logger.info(f"Starting parallel tests on {len(capabilities)} configurations with {max_workers} workers")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all test jobs
            future_to_capability = {
                executor.submit(self.run_single_test, cap): cap 
                for cap in capabilities
            }
            
            # Collect results as they complete
            results = []
            for future in concurrent.futures.as_completed(future_to_capability):
                capability = future_to_capability[future]
                try:
                    result = future.result()
                    with self.results_lock:
                        results.append(result)
                        self.test_results.append(result)
                except Exception as e:
                    self.logger.error(f"Test execution failed for {capability.browser}: {str(e)}")
                    error_result = TestResult(
                        capability=capability,
                        success=False,
                        execution_time=0.0,
                        articles_scraped=0,
                        error_message=str(e)
                    )
                    with self.results_lock:
                        results.append(error_result)
                        self.test_results.append(error_result)
        
        # Update build status based on overall results
        successful_tests = [r for r in results if r.success]
        failed_tests = [r for r in results if not r.success]
        
        # Determine overall build status
        if len(failed_tests) == 0:
            build_status = "passed"
        else:
            build_status = "failed"
        
        # Update build status in BrowserStack
        self._update_build_status("El País Scraper Build", build_status)
        
        self.logger.info(f"Tests completed: {len(successful_tests)} passed, {len(failed_tests)} failed")
        
        return results
    
    def print_test_summary(self, results: List[TestResult]) -> None:
        """Print a summary of test results."""
        print("\n" + "="*80)
        print("BROWSERSTACK TEST SUMMARY")
        print("="*80)
        
        successful_tests = [r for r in results if r.success]
        failed_tests = [r for r in results if not r.success]
        
        print(f"Total Tests: {len(results)}")
        print(f"Successful: {len(successful_tests)}")
        print(f"Failed: {len(failed_tests)}")
        print(f"Success Rate: {len(successful_tests)/len(results)*100:.1f}%")
        
        if successful_tests:
            avg_time = sum(r.execution_time for r in successful_tests) / len(successful_tests)
            total_articles = sum(r.articles_scraped for r in successful_tests)
            print(f"Average Execution Time: {avg_time:.2f} seconds")
            print(f"Total Articles Scraped: {total_articles}")
        
        print("\nDetailed Results:")
        print("-" * 80)
        
        for result in results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            device_info = f"{result.capability.browser} {result.capability.browser_version} on {result.capability.os}"
            if result.capability.device:
                device_info += f" ({result.capability.device})"
            
            print(f"{status} | {device_info}")
            print(f"      Time: {result.execution_time:.2f}s | Articles: {result.articles_scraped}")
            
            if result.error_message:
                print(f"      Error: {result.error_message}")
            
            if result.session_id:
                print(f"      Session: https://automate.browserstack.com/dashboard/v2/builds/{result.session_id}")
            
            print()


def main():
    """Main function to run BrowserStack tests."""
    try:
        print("🚀 Starting BrowserStack Cross-Browser Testing")
        print("=" * 60)
        
        # Initialize runner
        runner = BrowserStackRunner()
        
        # Run parallel tests
        results = runner.run_parallel_tests(max_workers=5)
        
        # Print summary
        runner.print_test_summary(results)
        
        print("\n🎉 BrowserStack testing completed!")
        print("Check the BrowserStack dashboard for detailed logs and videos:")
        print("https://automate.browserstack.com/dashboard")
        
    except Exception as e:
        Logger.error(f"BrowserStack testing failed: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Ensure BrowserStack credentials are set in environment variables")
        print("2. Check your BrowserStack account has active sessions available")
        print("3. Verify your internet connection")


if __name__ == "__main__":
    main()
