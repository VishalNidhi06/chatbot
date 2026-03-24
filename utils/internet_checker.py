import requests
import logging
import socket
from config import Config

logger = logging.getLogger(__name__)

class InternetChecker:
    """Check internet connectivity with multiple methods"""
    
    def __init__(self):
        self.check_url = Config.INTERNET_CHECK_URL
        self.timeout = Config.INTERNET_CHECK_TIMEOUT
    
    def is_connected(self):
        """Check if internet is available using multiple methods"""
        # Method 1: Try HTTP request
        try:
            response = requests.get(self.check_url, timeout=self.timeout)
            if response.status_code == 200:
                return True
        except requests.RequestException as e:
            logger.debug(f"HTTP internet check failed: {e}")
        
        # Method 2: Try DNS resolution
        try:
            socket.gethostbyname('www.google.com')
            return True
        except socket.gaierror:
            logger.debug("DNS resolution failed")
        
        # Method 3: Try a different URL
        try:
            response = requests.get('https://www.cloudflare.com', timeout=self.timeout)
            if response.status_code == 200:
                return True
        except:
            pass
        
        return False
    
    def check_and_log(self):
        """Check internet and log status"""
        status = self.is_connected()
        logger.info(f"Internet connection: {'Available' if status else 'Not Available'}")
        return status