from typing import List, Dict, Counter as CounterType
from collections import Counter
import re
import string

from src.models.article import TranslatedArticle, WordAnalysis
from src.utils.logger import Logger


class TextAnalyzer:
    """Text analysis service for translated articles."""
    
    def __init__(self):
        self.logger = Logger()
        
        # Common English stop words to filter out
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
            'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 
            'their', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'among', 'against'
        }
    
    def clean_word(self, word: str) -> str:
        """Clean and normalize a word."""
        # Remove punctuation and convert to lowercase
        word = word.lower().strip()
        word = word.translate(str.maketrans('', '', string.punctuation))
        return word
    
    def extract_words(self, text: str) -> List[str]:
        """Extract and clean words from text."""
        if not text:
            return []
        
        # Split text into words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Clean and filter words
        cleaned_words = []
        for word in words:
            cleaned = self.clean_word(word)
            # Filter out stop words, short words, and numbers
            if (cleaned and 
                len(cleaned) > 2 and 
                cleaned not in self.stop_words and 
                not cleaned.isdigit()):
                cleaned_words.append(cleaned)
        
        return cleaned_words
    
    def analyze_word_frequency(self, translated_articles: List[TranslatedArticle]) -> List[WordAnalysis]:
        """
        Analyze word frequency across translated article titles.
        
        Args:
            translated_articles: List of translated articles
            
        Returns:
            List of WordAnalysis objects for words that appear more than twice
        """
        try:
            self.logger.info("Analyzing word frequency in translated titles...")
            
            word_counter = Counter()
            word_to_articles = {}  # Track which articles contain each word
            
            for article in translated_articles:
                title = article.translated_title
                words = self.extract_words(title)
                
                for word in set(words):  # Use set to count each word once per article
                    word_counter[word] += 1
                    
                    if word not in word_to_articles:
                        word_to_articles[word] = []
                    word_to_articles[word].append(title)
            
            # Filter words that appear more than twice
            repeated_words = []
            for word, count in word_counter.items():
                if count > 2:
                    word_analysis = WordAnalysis(
                        word=word,
                        count=count,
                        articles_appeared_in=word_to_articles[word]
                    )
                    repeated_words.append(word_analysis)
            
            # Sort by count (descending)
            repeated_words.sort(key=lambda x: x.count, reverse=True)
            
            self.logger.info(f"Found {len(repeated_words)} words repeated more than twice")
            
            # Print results as required
            print("\n--- Word Frequency Analysis ---")
            print("Words that appear more than twice across all translated headers:")
            
            if repeated_words:
                for analysis in repeated_words:
                    print(f"'{analysis.word}': {analysis.count} occurrences")
            else:
                print("No words found that repeat more than twice.")
            
            return repeated_words
            
        except Exception as e:
            self.logger.error(f"Error during word frequency analysis: {str(e)}")
            return []
    
    def get_statistics(self, translated_articles: List[TranslatedArticle]) -> Dict[str, int]:
        """Get general statistics about the translated articles."""
        try:
            total_articles = len(translated_articles)
            total_words = 0
            unique_words = set()
            
            for article in translated_articles:
                words = self.extract_words(article.translated_title)
                total_words += len(words)
                unique_words.update(words)
            
            return {
                'total_articles': total_articles,
                'total_words': total_words,
                'unique_words': len(unique_words),
                'avg_words_per_title': total_words / total_articles if total_articles > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating statistics: {str(e)}")
            return {}
    
    def find_common_themes(self, translated_articles: List[TranslatedArticle]) -> List[str]:
        """Identify common themes or topics from the translated titles."""
        try:
            # Common theme-related words
            theme_words = {
                'politics': ['government', 'political', 'policy', 'election', 'democracy', 'vote'],
                'economy': ['economic', 'financial', 'market', 'business', 'trade', 'money'],
                'society': ['social', 'community', 'people', 'public', 'society', 'citizen'],
                'international': ['international', 'global', 'world', 'foreign', 'country'],
                'culture': ['cultural', 'art', 'education', 'media', 'technology']
            }
            
            theme_counts = Counter()
            
            for article in translated_articles:
                words = self.extract_words(article.translated_title)
                
                for theme, keywords in theme_words.items():
                    if any(keyword in words for keyword in keywords):
                        theme_counts[theme] += 1
            
            # Return themes that appear in at least 2 articles
            common_themes = [theme for theme, count in theme_counts.items() if count >= 2]
            
            return common_themes
            
        except Exception as e:
            self.logger.error(f"Error finding common themes: {str(e)}")
            return []
