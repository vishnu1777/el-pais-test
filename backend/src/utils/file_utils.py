import os
import requests
from typing import Optional
from pathlib import Path
from urllib.parse import urlparse, urljoin
from src.utils.logger import Logger


class FileDownloader:
    """Utility class for downloading and saving files."""
    
    def __init__(self, base_dir: str = "downloads"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.logger = Logger()
    
    def download_image(
        self, 
        image_url: str, 
        filename: Optional[str] = None,
        subfolder: str = "images"
    ) -> Optional[str]:
        """
        Download an image from URL and save to local storage.
        
        Args:
            image_url: URL of the image to download
            filename: Optional custom filename
            subfolder: Subfolder to save the image in
            
        Returns:
            Local file path if successful, None otherwise
        """
        try:
            if not image_url:
                return None
                
            # Create subfolder
            save_dir = self.base_dir / subfolder
            save_dir.mkdir(exist_ok=True)
            
            # Generate filename if not provided
            if not filename:
                parsed_url = urlparse(image_url)
                filename = os.path.basename(parsed_url.path)
                if not filename or '.' not in filename:
                    filename = f"image_{hash(image_url) % 10000}.jpg"
            
            file_path = save_dir / filename
            
            # Download image
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(image_url, headers=headers, timeout=30, stream=True)
            response.raise_for_status()
            
            # Save image
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.logger.info(f"Successfully downloaded image: {filename}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Failed to download image {image_url}: {str(e)}")
            return None
    
    def get_absolute_url(self, base_url: str, relative_url: str) -> str:
        """Convert relative URL to absolute URL."""
        return urljoin(base_url, relative_url)
    
    def is_valid_image_url(self, url: str) -> bool:
        """Check if URL points to a valid image."""
        if not url:
            return False
            
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
        parsed = urlparse(url)
        path_lower = parsed.path.lower()
        
        return any(path_lower.endswith(ext) for ext in image_extensions)
