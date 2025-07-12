from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import List, Optional, Dict, Any
import time
from bs4 import BeautifulSoup

from src.models.article import Article
from src.utils.logger import Logger
from src.utils.helpers import retry_on_failure, clean_text, validate_url
from src.utils.file_utils import FileDownloader
from config.settings import settings


class ElPaisScraper:
    """Selenium-based scraper for El País opinion articles."""
    
    def __init__(self, headless: bool = True, browser: str = "chrome"):
        self.headless = headless
        self.browser = browser.lower()
        self.driver: Optional[webdriver.Remote] = None
        self.logger = Logger()
        self.file_downloader = FileDownloader(settings.images_dir)
        self.wait_timeout = settings.implicit_wait
    
    def _get_driver_options(self) -> Any:
        """Get browser-specific options."""
        if self.browser == "chrome":
            options = ChromeOptions()
            if self.headless:
                options.add_argument("--headless")
            
            # Basic Chrome options
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            # Suppress warnings and errors
            options.add_argument("--disable-logging")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=TranslateUI")
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--disable-ipc-flooding-protection")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-client-side-phishing-detection")
            options.add_argument("--disable-sync")
            options.add_argument("--disable-default-apps")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-hang-monitor")
            options.add_argument("--disable-prompt-on-repost")
            options.add_argument("--disable-domain-reliability")
            options.add_argument("--disable-component-extensions-with-background-pages")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-background-networking")
            options.add_argument("--disable-breakpad")
            options.add_argument("--disable-component-update")
            options.add_argument("--disable-features=Translate")
            options.add_argument("--disable-software-rasterizer")
            options.add_argument("--log-level=3")  # Suppress INFO, WARNING, and ERROR logs
            
            # Suppress specific warnings
            options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            options.add_experimental_option("useAutomationExtension", False)
            
            # Suppress DevTools and other messages
            options.add_argument("--silent")
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            return options
        elif self.browser == "firefox":
            options = FirefoxOptions()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
            return options
        else:
            raise ValueError(f"Unsupported browser: {self.browser}")
    
    def _init_driver(self, capabilities: Optional[Dict] = None) -> None:
        """Initialize the WebDriver."""
        try:
            if capabilities:  # For BrowserStack
                from selenium.webdriver import Remote
                from selenium.webdriver.chrome.options import Options as ChromeOptions
                from selenium.webdriver.firefox.options import Options as FirefoxOptions
                
                # Determine browser type from capabilities
                browser_name = capabilities.get("browserName", "chrome").lower()
                
                if browser_name == "chrome":
                    options = ChromeOptions()
                elif browser_name == "firefox":
                    options = FirefoxOptions()
                else:
                    # Default to Chrome options for Safari and Edge
                    options = ChromeOptions()
                
                # Set BrowserStack capabilities
                for key, value in capabilities.items():
                    if key not in ["browserName"]:  # browserName is handled by options type
                        options.set_capability(key, value)
                
                # Add BrowserStack credentials to options if not already set
                if "bstack:options" in capabilities:
                    bstack_options = capabilities["bstack:options"].copy()
                    bstack_options["userName"] = settings.browserstack_username
                    bstack_options["accessKey"] = settings.browserstack_access_key
                    options.set_capability("bstack:options", bstack_options)
                
                self.driver = Remote(
                    command_executor=f"https://{settings.browserstack_username}:{settings.browserstack_access_key}@hub-cloud.browserstack.com/wd/hub",
                    options=options
                )
            else:  # For local testing
                if self.browser == "chrome":
                    self.driver = webdriver.Chrome(options=self._get_driver_options())
                elif self.browser == "firefox":
                    self.driver = webdriver.Firefox(options=self._get_driver_options())
            
            self.driver.implicitly_wait(self.wait_timeout)
            self.logger.info(f"WebDriver initialized successfully for {self.browser}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {str(e)}")
            raise
    
    @retry_on_failure(max_attempts=3, delay=2.0)
    def _navigate_to_opinion_section(self) -> None:
        """Navigate to the El País opinion section."""
        try:
            self.logger.info("Navigating to El País opinion section...")
            self.driver.get(settings.opinion_section_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
            
            # Check if we're on the Spanish version
            if "elpais.com" in self.driver.current_url:
                self.logger.info("Successfully navigated to El País opinion section")
            else:
                self.logger.warning("May not be on the correct Spanish version of the site")
                
        except TimeoutException:
            self.logger.error("Timeout waiting for opinion section to load")
            raise
        except Exception as e:
            self.logger.error(f"Failed to navigate to opinion section: {str(e)}")
            raise
    
    def _extract_article_links(self) -> List[str]:
        """Extract article links from the opinion section."""
        try:
            self.logger.info("Extracting article links...")
            
            # Common selectors for El País articles
            article_selectors = [
                "article a[href*='/opinion/']",
                ".articulo-titulo a",
                ".opinion a[href*='/opinion/']",
                "h2 a[href*='/opinion/']",
                ".story a[href*='/opinion/']"
            ]
            
            article_links = []
            
            for selector in article_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements[:settings.max_articles * 2]:  # Get extra to filter
                        href = element.get_attribute("href")
                        if href and validate_url(href) and href not in article_links:
                            article_links.append(href)
                            if len(article_links) >= settings.max_articles:
                                break
                    
                    if len(article_links) >= settings.max_articles:
                        break
                        
                except NoSuchElementException:
                    continue
            
            self.logger.info(f"Found {len(article_links)} article links")
            return article_links[:settings.max_articles]
            
        except Exception as e:
            self.logger.error(f"Failed to extract article links: {str(e)}")
            return []
    
    @retry_on_failure(max_attempts=2, delay=1.0)
    def _scrape_article_content(self, url: str) -> Optional[Article]:
        """Scrape content from a single article."""
        try:
            self.logger.info(f"Scraping article: {url}")
            self.driver.get(url)
            
            # Wait for article content to load
            WebDriverWait(self.driver, self.wait_timeout).until(
                EC.any_of(
                    EC.presence_of_element_located((By.TAG_NAME, "h1")),
                    EC.presence_of_element_located((By.CLASS_NAME, "articulo-titulo")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-dtm-region='articulo_titulo']"))
                )
            )
            
            # Extract title
            title = self._extract_title()
            if not title:
                self.logger.warning(f"Could not extract title from {url}")
                return None
            
            # Extract content
            content = self._extract_content()
            
            # Extract image
            image_url = self._extract_image_url()
            local_image_path = None
            
            if image_url:
                local_image_path = self.file_downloader.download_image(
                    image_url,
                    filename=f"article_{hash(url) % 10000}.jpg"
                )
            
            article = Article(
                title=clean_text(title),
                content=clean_text(content),
                url=url,
                image_url=image_url,
                local_image_path=local_image_path
            )
            
            self.logger.info(f"Successfully scraped article: {title[:50]}...")
            return article
            
        except TimeoutException:
            self.logger.error(f"Timeout while scraping article: {url}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to scrape article {url}: {str(e)}")
            return None
    
    def _extract_title(self) -> Optional[str]:
        """Extract article title using multiple selectors."""
        title_selectors = [
            "h1",
            ".articulo-titulo",
            "[data-dtm-region='articulo_titulo']",
            ".headline",
            ".entry-title",
            "header h1"
        ]
        
        for selector in title_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                title = element.text.strip()
                if title:
                    return title
            except NoSuchElementException:
                continue
        
        return None
    
    def _extract_content(self) -> str:
        """Extract article content using multiple selectors."""
        content_selectors = [
            ".articulo-cuerpo",
            ".story-body",
            ".article-body",
            ".entry-content",
            "[data-dtm-region='articulo_cuerpo']",
            ".content-body p"
        ]
        
        content_parts = []
        
        for selector in content_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.strip()
                    if text and len(text) > 50:  # Filter out short snippets
                        content_parts.append(text)
                
                if content_parts:
                    break
                    
            except NoSuchElementException:
                continue
        
        # If no content found with specific selectors, try paragraphs
        if not content_parts:
            try:
                paragraphs = self.driver.find_elements(By.CSS_SELECTOR, "p")
                for p in paragraphs:
                    text = p.text.strip()
                    if len(text) > 50:
                        content_parts.append(text)
            except NoSuchElementException:
                pass
        
        return " ".join(content_parts)
    
    def _extract_image_url(self) -> Optional[str]:
        """Extract main article image URL."""
        image_selectors = [
            ".articulo-imagen img",
            ".story-image img",
            ".featured-image img",
            "figure img",
            ".article-image img",
            "img[src*='elpais']"
        ]
        
        for selector in image_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                src = element.get_attribute("src")
                if src and self.file_downloader.is_valid_image_url(src):
                    # Convert relative URL to absolute if needed
                    if src.startswith("//"):
                        src = "https:" + src
                    elif src.startswith("/"):
                        src = self.file_downloader.get_absolute_url(settings.base_url, src)
                    return src
            except NoSuchElementException:
                continue
        
        return None
    
    def scrape_articles(self, capabilities: Optional[Dict] = None) -> List[Article]:
        """
        Main method to scrape articles from El País opinion section.
        
        Args:
            capabilities: Optional BrowserStack capabilities for remote testing
            
        Returns:
            List of scraped articles
        """
        articles = []
        is_browserstack = capabilities is not None
        
        try:
            self._init_driver(capabilities)
            self._navigate_to_opinion_section()
            
            article_links = self._extract_article_links()
            
            if not article_links:
                self.logger.warning("No article links found")
                return articles
            
            self.logger.info(f"Scraping {len(article_links)} articles...")
            
            for i, link in enumerate(article_links, 1):
                self.logger.info(f"Processing article {i}/{len(article_links)}")
                article = self._scrape_article_content(link)
                
                if article:
                    articles.append(article)
                    # Print article info as required
                    print(f"\n--- Article {i} ---")
                    print(f"Title: {article.title}")
                    print(f"Content Preview: {article.content[:200]}...")
                    print(f"Image saved: {article.local_image_path or 'No image'}")
                
                # Small delay between articles
                time.sleep(1)
            
            self.logger.info(f"Successfully scraped {len(articles)} articles")
            
        except Exception as e:
            self.logger.error(f"Error during scraping: {str(e)}")
        finally:
            # Only close driver if not using BrowserStack (let runner handle BrowserStack closure)
            if not is_browserstack:
                self.close()
        
        return articles
    
    def close(self) -> None:
        """Close the WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing WebDriver: {str(e)}")
            finally:
                self.driver = None
