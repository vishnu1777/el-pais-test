from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


## use the data class for types and storage 
## better readablity brotha
@dataclass
class Article:
    """Data model for scraped articles."""
    title: str
    content: str
    url: str
    image_url: Optional[str] = None
    local_image_path: Optional[str] = None
    scraped_at: datetime = None
    
    def __post_init__(self):
        if self.scraped_at is None:
            self.scraped_at = datetime.now()


@dataclass
class TranslatedArticle:
    """Data model for translated articles."""
    original_article: Article
    translated_title: str
    translation_service: str
    translated_at: datetime = None
    
    def __post_init__(self):
        if self.translated_at is None:
            self.translated_at = datetime.now()


@dataclass
class WordAnalysis:
    """Data model for word frequency analysis."""
    word: str
    count: int
    articles_appeared_in: List[str]
@dataclass
class ScrapingResult:
    """Complete scraping result."""
    articles: List[Article]
    translated_articles: List[TranslatedArticle]
    word_analysis: List[WordAnalysis]
    total_processing_time: float
    success_count: int
    error_count: int
    errors: List[str]