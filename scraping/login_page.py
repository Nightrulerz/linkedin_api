import os
import json
from base64 import b64encode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium_stealth import stealth

class LoginPage:
    """
    A class to handle LinkedIn authentication and cookie management.
    
    This class provides methods to authenticate with LinkedIn using Selenium WebDriver,
    retrieve authentication cookies, and manage cookie caching for subsequent use.
    
    Attributes:
        user_email_id (str): LinkedIn account email address
        user_password (str): LinkedIn account password
    """
    
    def __init__(self, email, password):
        """
        Initialize the LoginPage with user credentials.
        
        Args:
            email (str): LinkedIn account email address
            password (str): LinkedIn account password
        """
        self.user_email_id = email
        self.user_password = password
        
    def get_cookie(self):
        """
        Retrieve LinkedIn authentication cookies.
        
        This method first checks for cached cookies associated with the user credentials.
        If valid cached cookies exist, they are returned. Otherwise, it launches a browser
        session to authenticate with LinkedIn and obtain fresh cookies.
        
        Returns:
            dict: A dictionary of cookie name-value pairs for LinkedIn authentication
        """
        # Try to load cached cookies
        credential_id = self._encrypt_credential()
        cache_dir = os.path.join(os.path.dirname(__file__), ".user")
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            
        cache_file = os.path.join(cache_dir, f"{credential_id}.json")
        
        # Check if cached cookies exist and return them
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as file:
                    cookies = json.load(file)
                    return cookies
            except Exception:
                # If any error occurs with cached cookies, get fresh ones
                pass
        
        # If no cached cookies or error, get fresh cookies
        driver = self._launch_browser()
        try:
            cookies = self._authenticate(driver)
            return cookies
        finally:
            # Always close the browser
            driver.quit()

    def _launch_browser(self):
        """
        Launch a Chrome browser with stealth settings.
        
        This method configures and launches a Chrome WebDriver instance with settings
        to avoid detection as an automated browser. It uses selenium-stealth to bypass
        common anti-bot measures.
        
        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance
        """
        options = webdriver.ChromeOptions()
        options.binary_location = "/usr/bin/google-chrome"
        # options.add_argument("--headless")  # Run headless for server environments
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        driver = webdriver.Chrome(options=options)
        stealth(driver, languages=["en-US", "en"], platform="Linux")
        return driver

    def _authenticate(self, driver):
        """
        Perform LinkedIn authentication using the provided WebDriver.
        
        This method navigates to the LinkedIn login page, enters user credentials,
        waits for successful authentication, and retrieves the resulting cookies.
        
        Args:
            driver (webdriver.Chrome): Chrome WebDriver instance
            
        Returns:
            dict: A dictionary of cookie name-value pairs for LinkedIn authentication
        """
        driver.get("https://www.linkedin.com/login")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        email_element = driver.find_element(By.ID, "username")
        email_element.send_keys(self.user_email_id)
        password_element = driver.find_element(By.ID, "password")
        password_element.send_keys(self.user_password)
        password_element.submit()
        
        # Wait for login to complete (look for navigation element)
        for _ in range(3):
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "global-nav__primary-link"))
                )
                break
            except Exception:
                pass
                
        # Get cookies and process them
        raw_cookies = driver.get_cookies()
        cookies = self._clean_cookies(raw_cookies)
        self._cache_cookies(cookies)
        return cookies

    def _clean_cookies(self, raw_cookies):
        """
        Convert Selenium cookie format to a simple dictionary.
        
        Args:
            raw_cookies (list): List of cookie dictionaries from Selenium
            
        Returns:
            dict: A dictionary of cookie name-value pairs
        """
        cookies = {}
        for cookie in raw_cookies:
            cookies[cookie['name']] = cookie['value']
        return cookies
        
    def _cache_cookies(self, cookies):
        """
        Save cookies to a cache file for future use.
        
        The cache file is named using an encoded version of the user credentials
        and stored in the .user directory relative to the script location.
        
        Args:
            cookies (dict): Dictionary of cookie name-value pairs to cache
        """
        credential_id = self._encrypt_credential()
        cache_dir = os.path.join(os.path.dirname(__file__), ".user")
        
        # Ensure directory exists
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            
        cache_file = os.path.join(cache_dir, f"{credential_id}.json")
        
        with open(cache_file, "w") as file:
            json.dump(cookies, file, indent=4)

    def _encrypt_credential(self):
        """
        Create a unique identifier from user credentials.
        
        This method creates a base64-encoded string from the combined email and password
        to use as a unique identifier for caching purposes.
        
        Returns:
            str: Base64-encoded string of combined credentials
        """
        credentials = f"{self.user_email_id}|{self.user_password}"
        encoded_bytes = b64encode(credentials.encode('utf-8'))
        return encoded_bytes.decode('utf-8')