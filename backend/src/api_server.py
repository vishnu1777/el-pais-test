from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from src.main import MainApplication
from src.browserstack_runner import BrowserStackRunner
from src.models.article import ScrapingResult
from src.utils.logger import Logger
from config.settings import settings

app = FastAPI(
    title="El País News Scraper API",
    description="API for scraping and analyzing El País opinion articles",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for images
if os.path.exists(settings.images_dir):
    app.mount("/images", StaticFiles(directory=settings.images_dir), name="images")

# Global state
current_scraping_task = None
latest_results = None
logger = Logger()


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "El País News Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "scrape": "/scrape",
            "status": "/status",
            "results": "/results",
            "browserstack": "/browserstack",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "scraper": "available",
            "translator": "available",
            "analyzer": "available"
        }
    }


@app.post("/scrape")
async def start_scraping(background_tasks: BackgroundTasks):
    """Start the scraping workflow in the background."""
    global current_scraping_task
    
    if current_scraping_task and not current_scraping_task.done():
        raise HTTPException(status_code=409, detail="Scraping is already in progress")
    
    async def scraping_workflow():
        global latest_results
        try:
            logger.info("Starting background scraping task")
            app_instance = MainApplication()
            result = app_instance.run_complete_workflow()
            latest_results = result
            logger.info("Background scraping task completed")
        except Exception as e:
            logger.error(f"Background scraping task failed: {str(e)}")
            raise
    
    current_scraping_task = asyncio.create_task(scraping_workflow())
    background_tasks.add_task(lambda: current_scraping_task)
    
    return {
        "message": "Scraping started",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/status")
async def get_scraping_status():
    """Get the current status of the scraping process."""
    global current_scraping_task, latest_results
    
    if current_scraping_task is None:
        return {
            "status": "not_started",
            "message": "No scraping task has been started"
        }
    
    if current_scraping_task.done():
        if current_scraping_task.exception():
            return {
                "status": "failed",
                "error": str(current_scraping_task.exception()),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "completed",
                "message": "Scraping completed successfully",
                "timestamp": datetime.now().isoformat(),
                "has_results": latest_results is not None
            }
    else:
        return {
            "status": "running",
            "message": "Scraping is in progress",
            "timestamp": datetime.now().isoformat()
        }


@app.get("/results")
async def get_latest_results():
    """Get the latest scraping results."""
    global latest_results
    
    if latest_results is None:
        # Try to load from the most recent file
        try:
            data_files = [f for f in os.listdir(settings.data_dir) if f.startswith("scraping_results_") and f.endswith(".json")]
            if data_files:
                latest_file = max(data_files)
                with open(os.path.join(settings.data_dir, latest_file), 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load results from file: {str(e)}")
        
        raise HTTPException(status_code=404, detail="No results available")
    
    # Convert ScrapingResult to JSON format
    return {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_articles_scraped": len(latest_results.articles),
            "successful_translations": len(latest_results.translated_articles),
            "words_analyzed": len(latest_results.word_analysis),
            "processing_time_seconds": latest_results.total_processing_time,
            "success_count": latest_results.success_count,
            "error_count": latest_results.error_count
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
            for article in latest_results.articles
        ],
        "translated_articles": [
            {
                "original_title": ta.original_article.title,
                "translated_title": ta.translated_title,
                "translation_service": ta.translation_service,
                "translated_at": ta.translated_at.isoformat() if ta.translated_at else None
            }
            for ta in latest_results.translated_articles
        ],
        "word_analysis": [
            {
                "word": wa.word,
                "count": wa.count,
                "articles_appeared_in": wa.articles_appeared_in
            }
            for wa in latest_results.word_analysis
        ],
        "errors": latest_results.errors
    }


@app.post("/browserstack")
async def run_browserstack_tests(background_tasks: BackgroundTasks):
    """Run BrowserStack cross-browser tests."""
    try:
        # Validate BrowserStack credentials
        if not settings.browserstack_username or not settings.browserstack_access_key:
            raise HTTPException(
                status_code=400, 
                detail="BrowserStack credentials not configured. Please set BROWSERSTACK_USERNAME and BROWSERSTACK_ACCESS_KEY environment variables."
            )
        
        async def browserstack_workflow():
            try:
                logger.info("Starting BrowserStack tests")
                runner = BrowserStackRunner()
                results = runner.run_parallel_tests(max_workers=5)
                logger.info("BrowserStack tests completed")
                return results
            except Exception as e:
                logger.error(f"BrowserStack tests failed: {str(e)}")
                raise
        
        background_tasks.add_task(browserstack_workflow)
        
        return {
            "message": "BrowserStack tests started",
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "dashboard_url": "https://automate.browserstack.com/dashboard"
        }
        
    except Exception as e:
        logger.error(f"Failed to start BrowserStack tests: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files")
async def list_data_files():
    """List available data files."""
    try:
        files = []
        
        # List JSON data files
        if os.path.exists(settings.data_dir):
            for filename in os.listdir(settings.data_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(settings.data_dir, filename)
                    stat = os.stat(filepath)
                    files.append({
                        "name": filename,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "type": "data"
                    })
        
        # List image files
        images_subdir = os.path.join(settings.images_dir, "images")
        if os.path.exists(images_subdir):
            for filename in os.listdir(images_subdir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                    filepath = os.path.join(images_subdir, filename)
                    stat = os.stat(filepath)
                    files.append({
                        "name": filename,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "type": "image",
                        "url": f"/images/images/{filename}"
                    })
        
        return {"files": files}
        
    except Exception as e:
        logger.error(f"Failed to list files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download a specific data file."""
    try:
        filepath = os.path.join(settings.data_dir, filename)
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            filepath,
            media_type='application/json',
            filename=filename
        )
        
    except Exception as e:
        logger.error(f"Failed to download file {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting El País Scraper API Server")
    print(f"📡 Server will be available at: http://localhost:{settings.api_port}")
    print(f"📖 API Documentation: http://localhost:{settings.api_port}/docs")
    
    uvicorn.run(
        "api_server:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level="info"
    )
