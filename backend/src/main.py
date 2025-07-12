import time
import json
from datetime import datetime
from typing import List, Optional

from src.scraper.el_pais_scraper import ElPaisScraper
from src.translator.translation_service import TranslationService
from src.analyzer.text_analyzer import TextAnalyzer
from src.models.article import Article, TranslatedArticle, WordAnalysis, ScrapingResult
from src.utils.logger import Logger
from config.settings import settings


class MainApplication:
    """Main application orchestrator for the El País scraping workflow."""
    
    def __init__(self):
        self.logger = Logger()
        self.scraper: Optional[ElPaisScraper] = None
        self.translator: Optional[TranslationService] = None
        self.analyzer: Optional[TextAnalyzer] = None
    
    def initialize_services(self) -> None:
        """Initialize all required services."""
        try:
            self.logger.info("Initializing services...")
            
            # Initialize scraper
            self.scraper = ElPaisScraper(headless=True, browser="chrome")
            
            # Initialize translation service
            self.translator = TranslationService(
                google_api_key=settings.google_translate_api_key,
                rapid_api_key=settings.rapid_api_key
            )
            
            # Initialize text analyzer
            self.analyzer = TextAnalyzer()
            
            self.logger.info("All services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize services: {str(e)}")
            raise
    
    def run_complete_workflow(self) -> ScrapingResult:
        """Run the complete workflow: scrape -> translate -> analyze."""
        start_time = time.time()
        errors = []
        
        try:
            self.logger.info("Starting complete El País scraping workflow...")
            
            # Step 1: Initialize services
            self.initialize_services()
            
            # Step 2: Scrape articles
            self.logger.info("Step 1: Scraping articles from El País...")
            articles = self.scraper.scrape_articles()
            
            if not articles:
                error_msg = "No articles were scraped"
                self.logger.error(error_msg)
                errors.append(error_msg)
                return ScrapingResult(
                    articles=[],
                    translated_articles=[],
                    word_analysis=[],
                    total_processing_time=time.time() - start_time,
                    success_count=0,
                    error_count=1,
                    errors=errors
                )
            
            # Step 3: Translate articles
            self.logger.info("Step 2: Translating article titles...")
            translated_articles = self.translator.translate_articles(articles)
            
            # Step 4: Analyze translated content
            self.logger.info("Step 3: Analyzing word frequency...")
            word_analysis = self.analyzer.analyze_word_frequency(translated_articles)
            
            # Calculate execution time
            total_time = time.time() - start_time
            
            # Create result object
            result = ScrapingResult(
                articles=articles,
                translated_articles=translated_articles,
                word_analysis=word_analysis,
                total_processing_time=total_time,
                success_count=len(translated_articles),
                error_count=len(errors),
                errors=errors
            )
            
            # Save results
            self._save_results(result)
            
            # Print final summary
            self._print_final_summary(result)
            
            self.logger.info(f"Workflow completed successfully in {total_time:.2f} seconds")
            return result
            
        except Exception as e:
            error_msg = f"Workflow failed: {str(e)}"
            self.logger.error(error_msg)
            errors.append(error_msg)
            
            return ScrapingResult(
                articles=[],
                translated_articles=[],
                word_analysis=[],
                total_processing_time=time.time() - start_time,
                success_count=0,
                error_count=len(errors),
                errors=errors
            )
    
    def _save_results(self, result: ScrapingResult) -> None:
        """Save results to JSON file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraping_results_{timestamp}.json"
            filepath = f"{settings.data_dir}/{filename}"
            
            # Convert result to JSON-serializable format
            data = {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_articles_scraped": len(result.articles),
                    "successful_translations": len(result.translated_articles),
                    "words_analyzed": len(result.word_analysis),
                    "processing_time_seconds": result.total_processing_time,
                    "success_count": result.success_count,
                    "error_count": result.error_count
                },
                "articles": [
                    {
                        "title": article.title,
                        "content_preview": article.content[:200] + "..." if len(article.content) > 200 else article.content,
                        "url": article.url,
                        "image_url": article.image_url,
                        "local_image_path": article.local_image_path,
                        "scraped_at": article.scraped_at.isoformat() if article.scraped_at else None
                    }
                    for article in result.articles
                ],
                "translated_articles": [
                    {
                        "original_title": ta.original_article.title,
                        "translated_title": ta.translated_title,
                        "translation_service": ta.translation_service,
                        "translated_at": ta.translated_at.isoformat() if ta.translated_at else None
                    }
                    for ta in result.translated_articles
                ],
                "word_analysis": [
                    {
                        "word": wa.word,
                        "count": wa.count,
                        "articles_appeared_in": wa.articles_appeared_in
                    }
                    for wa in result.word_analysis
                ],
                "errors": result.errors
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Results saved to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {str(e)}")
    
    def _print_final_summary(self, result: ScrapingResult) -> None:
        """Print a comprehensive summary of the results."""
        print("\n" + "="*80)
        print("EL PAÍS SCRAPING WORKFLOW SUMMARY")
        print("="*80)
        
        print(f"📊 Processing completed in {result.total_processing_time:.2f} seconds")
        print(f"📰 Articles scraped: {len(result.articles)}")
        print(f"🌐 Successful translations: {len(result.translated_articles)}")
        print(f"📝 Words analyzed: {len(result.word_analysis)}")
        
        if result.errors:
            print(f"⚠️  Errors encountered: {len(result.errors)}")
            for error in result.errors:
                print(f"   - {error}")
        
        print(f"\n🎯 Success rate: {(result.success_count / (result.success_count + result.error_count) * 100):.1f}%")
        
        # Print article titles
        if result.articles:
            print("\n📄 SCRAPED ARTICLES:")
            print("-" * 40)
            for i, article in enumerate(result.articles, 1):
                print(f"{i}. {article.title}")
                if article.local_image_path:
                    print(f"   📸 Image saved: {article.local_image_path}")
        
        # Print translations
        if result.translated_articles:
            print("\n🌐 TRANSLATED TITLES:")
            print("-" * 40)
            for i, ta in enumerate(result.translated_articles, 1):
                print(f"{i}. {ta.translated_title}")
        
        # Print word analysis
        if result.word_analysis:
            print("\n📊 WORD FREQUENCY ANALYSIS:")
            print("-" * 40)
            for wa in result.word_analysis:
                print(f"'{wa.word}': {wa.count} occurrences")
        
        print("\n✅ Workflow completed successfully!")
        print("Data saved to JSON file for frontend integration.")


def main():
    """Main entry point for the application."""
    try:
        print("🚀 Starting El País News Scraper & Analyzer")
        print("=" * 60)
        
        app = MainApplication()
        result = app.run_complete_workflow()
        
        if result.success_count > 0:
            print("\n🎉 Application completed successfully!")
        else:
            print("\n❌ Application completed with errors. Check logs for details.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Process interrupted by user")
    except Exception as e:
        Logger.error(f"Application failed: {str(e)}")
        print(f"\n💥 Fatal error: {str(e)}")


if __name__ == "__main__":
    main()
