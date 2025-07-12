from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum


class BrowserType(Enum):
    """Supported browser types."""
    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"
    EDGE = "edge"


class PlatformType(Enum):
    """Supported platform types."""
    WINDOWS = "Windows"
    MACOS = "OS X"
    ANDROID = "android"
    IOS = "ios"


@dataclass
class BrowserStackCapability:
    """BrowserStack test capability configuration."""
    browser: str
    browser_version: str
    os: str
    os_version: str
    device: Optional[str] = None
    real_mobile: Optional[bool] = None
    resolution: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Selenium capabilities."""
        caps = {
            'browserName': self.browser,
            'browserVersion': self.browser_version,
            'os': self.os,
            'osVersion': self.os_version,
            'bstack:options': {
                'projectName': 'El País Scraper',
                'buildName': 'El País Scraper Build',
                'sessionName': f'El País Test - {self.browser} {self.browser_version}',
                'userName': None,  # Will be set from settings
                'accessKey': None,  # Will be set from settings
                'debug': True,
                'consoleLogs': 'info',
                'networkLogs': True
            }
        }
        
        if self.device:
            caps['deviceName'] = self.device
        if self.real_mobile is not None:
            caps['realMobile'] = self.real_mobile
        if self.resolution:
            caps['resolution'] = self.resolution
            
        return caps


@dataclass
class TestResult:
    """Test execution result."""
    capability: BrowserStackCapability
    success: bool
    execution_time: float
    articles_scraped: int
    error_message: Optional[str] = None
    session_id: Optional[str] = None
