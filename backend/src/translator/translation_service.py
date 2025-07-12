from abc import ABC, abstractmethod
from typing import List, Optional
import time

from src.models.article import Article, TranslatedArticle
from src.utils.logger import Logger
from src.utils.helpers import retry_on_failure


class BaseTranslator(ABC):
    """Abstract base class for translation services."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = Logger()
    
    @abstractmethod
    def translate_text(self, text: str, source_lang: str = "es", target_lang: str = "en") -> Optional[str]:
        """Translate text from source language to target language."""
        pass
    
    def translate_article_title(self, article: Article) -> Optional[TranslatedArticle]:
        """Translate an article title."""
        try:
            translated_title = self.translate_text(article.title)
            if translated_title:
                return TranslatedArticle(
                    original_article=article,
                    translated_title=translated_title,
                    translation_service=self.service_name
                )
            return None
        except Exception as e:
            self.logger.error(f"Failed to translate article title: {str(e)}")
            return None


class GoogleTranslator(BaseTranslator):
    """Google Translate API integration."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("Google Translate")
        self.api_key = api_key
    
    @retry_on_failure(max_attempts=3, delay=1.0)
    def translate_text(self, text: str, source_lang: str = "es", target_lang: str = "en") -> Optional[str]:
        """Translate text using Google Translate API."""
        try:
            # Try using googletrans library (free version)
            from googletrans import Translator
            
            translator = Translator()
            result = translator.translate(text, src=source_lang, dest=target_lang)
            
            if result and result.text:
                self.logger.info(f"Successfully translated text with Google Translate")
                return result.text
            
            return None
            
        except Exception as e:
            self.logger.error(f"Google Translate error: {str(e)}")
            return None


class DeepTranslator(BaseTranslator):
    """Alternative translator using deep-translator library."""
    
    def __init__(self):
        super().__init__("Deep Translator")
    
    @retry_on_failure(max_attempts=3, delay=1.0)
    def translate_text(self, text: str, source_lang: str = "es", target_lang: str = "en") -> Optional[str]:
        """Translate text using deep-translator library."""
        try:
            from deep_translator import GoogleTranslator
            
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            translated = translator.translate(text)
            
            if translated:
                self.logger.info(f"Successfully translated text with Deep Translator")
                return translated
            
            return None
            
        except Exception as e:
            self.logger.error(f"Deep Translator error: {str(e)}")
            return None


class RapidTranslator(BaseTranslator):
    """RapidAPI Multi Translation service."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("Rapid Translate")
        self.api_key = api_key
    
    @retry_on_failure(max_attempts=3, delay=1.0)
    def translate_text(self, text: str, source_lang: str = "es", target_lang: str = "en") -> Optional[str]:
        """Translate text using RapidAPI translation service."""
        if not self.api_key:
            self.logger.warning("RapidAPI key not provided, skipping translation")
            return None
        
        try:
            import requests
            
            url = "https://rapid-translate-multi-traduction.p.rapidapi.com/t"
            
            payload = {
                "from": source_lang,
                "to": target_lang,
                "q": text
            }
            
            headers = {
                "content-type": "application/json",
                "X-RapidAPI-Key": self.api_key,
                "X-RapidAPI-Host": "rapid-translate-multi-traduction.p.rapidapi.com"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data and isinstance(data, list) and len(data) > 0:
                translated_text = data[0]
                self.logger.info(f"Successfully translated text with RapidAPI")
                return translated_text
            
            return None
            
        except Exception as e:
            self.logger.error(f"RapidAPI Translator error: {str(e)}")
            return None


class TranslationService:
    """Main translation service that manages multiple translators."""
    
    def __init__(self, google_api_key: Optional[str] = None, rapid_api_key: Optional[str] = None):
        self.logger = Logger()
        
        # Initialize translators in order of preference
        self.translators = []
        
        # Add Google Translator (free version)
        try:
            google_translator = GoogleTranslator(google_api_key)
            self.translators.append(google_translator)
        except Exception as e:
            self.logger.warning(f"Could not initialize Google Translator: {str(e)}")
        
        # Add Deep Translator (backup)
        try:
            deep_translator = DeepTranslator()
            self.translators.append(deep_translator)
        except Exception as e:
            self.logger.warning(f"Could not initialize Deep Translator: {str(e)}")
        
        # Add RapidAPI Translator if key provided
        if rapid_api_key:
            try:
                rapid_translator = RapidTranslator(rapid_api_key)
                self.translators.append(rapid_translator)
            except Exception as e:
                self.logger.warning(f"Could not initialize RapidAPI Translator: {str(e)}")
        
        if not self.translators:
            raise RuntimeError("No translation services available")
    
    def translate_articles(self, articles: List[Article]) -> List[TranslatedArticle]:
        """Translate a list of articles using available translators."""
        translated_articles = []
        
        self.logger.info(f"Translating {len(articles)} article titles...")
        
        for i, article in enumerate(articles, 1):
            self.logger.info(f"Translating article {i}/{len(articles)}: {article.title[:50]}...")
            
            translated_article = None
            
            # Try each translator until one succeeds
            for translator in self.translators:
                try:
                    translated_article = translator.translate_article_title(article)
                    if translated_article:
                        break
                except Exception as e:
                    self.logger.warning(f"Translator {translator.service_name} failed: {str(e)}")
                    continue
            
            if translated_article:
                translated_articles.append(translated_article)
                print(f"\nOriginal: {article.title}")
                print(f"Translated: {translated_article.translated_title}")
            else:
                self.logger.error(f"Failed to translate article: {article.title}")
            
            # Small delay between translations to avoid rate limits
            time.sleep(0.5)
        
        self.logger.info(f"Successfully translated {len(translated_articles)} articles")
        return translated_articles
