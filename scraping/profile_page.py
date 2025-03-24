from copy import deepcopy

from tenacity import retry, stop_after_attempt

from scraping.login_page import LoginPage
from scraping.data_parser import DataParser
from scraping.requests import Request
from scraping.utils import (extract_public_identifier,
                           get_headers)
from traceback import format_exc

class LinkedinProfileData:
    def __init__(self, email, password):
        """
        Initialize the LinkedIn profile data scraper.
        
        Args:
            email (str): LinkedIn account email for authentication
            password (str): LinkedIn account password for authentication
        """
        self.user_email = email
        self.user_password = password
        self.user_session = LoginPage(
            email=self.user_email,
            password=self.user_password
        )
        self.cookies = self.user_session.get_cookie()
        self.request = Request()

    @retry(stop=stop_after_attempt(10))
    async def fetch(self, url, params=None, headers=None, cookies=None, method="GET", data=None):
        """
        Make an HTTP request with retry capability.
        
        Wrapper for the request.fetch method with proper error handling.
        
        Args:
            url (str): The URL to request
            params (dict, optional): Query parameters to include in the request
            headers (dict, optional): HTTP headers to include in the request
            cookies (dict, optional): Cookies to include in the request
            method (str, optional): HTTP method to use (default: "GET")
            data (dict, optional): Data to include in the request body
            
        Returns:
            dict: Response data from the request
            
        Raises:
            Exception: If all retry attempts fail
        """
        response = await self.request.fetch(
            url=url, 
            params=params, 
            headers=headers, 
            cookies=cookies,
            method=method,
            data=data
        )
        return response

    @retry(stop=stop_after_attempt(10))
    async def get_profile_data(self, public_identifier=None, uri=None):
        """
        Extract comprehensive profile data for a LinkedIn user.
        
        Main function to extract the profile data:
        - If public_id/uri not given, assumes it should scrape the logged-in user's profile
        - In this case, it will send a homepage request to extract the public-id
        - Scrapes basic details and contact details and returns them combined in a dictionary
        
        Args:
            public_identifier (str, optional): LinkedIn profile ID to scrape
            uri (str, optional): LinkedIn profile URI to scrape
            
        Returns:
            dict: Combined profile and contact data for the requested profile
            
        Raises:
            Exception: If all retry attempts fail
        """
        if not public_identifier and not uri:
            # If public id is not provided, Assume that
            # It should scrape the profile of the logged in user.
            public_identifier = await self._get_public_identifier()

        api_profile_url = f"https://www.linkedin.com/voyager/api/identity/profiles/{public_identifier}/profileView"

        # Sending the Voyager API requests to get the profile details
        headers = deepcopy(get_headers(header_type="profile_page"))
        headers["csrf-token"] = self.cookies.get("JSESSIONID", "").replace('"', "").strip()
        
        response = await self.fetch(
            url=api_profile_url,
            headers=headers,
            cookies=self.cookies
        )

        # Extracting necessary Data
        parser = DataParser(response)
        profile_data = parser.get_profile_data()
        contact_details = await self._get_contact_details(public_identifier)
        profile_data.update(contact_details)
        return profile_data

    @retry(stop=stop_after_attempt(10))
    async def _get_contact_details(self, public_identifier):
        """
        Retrieve contact information for a LinkedIn profile.
        
        Makes an API request to fetch detailed contact information including
        email addresses, phone numbers, websites, etc. for a specific profile.
        
        Args:
            public_identifier (str): LinkedIn profile ID to get contact details for
            
        Returns:
            dict: Contact details for the requested profile
            
        Raises:
            Exception: If all retry attempts fail
        """
        api_profile_url = (
            "https://www.linkedin.com/voyager/api/identity"
            f"/profiles/{public_identifier}/profileContactInfo"
        )
        headers = deepcopy(get_headers(header_type="profile_page"))
        headers["csrf-token"] = self.cookies.get("JSESSIONID", "").replace('"', "").strip()
        
        response = await self.fetch(
            url=api_profile_url,
            headers=headers,
            cookies=self.cookies
        )
        
        parser = DataParser(response)
        contact_details = parser.get_contact_details()
        return contact_details

    async def _get_public_identifier(self):
        """
        Determine the public identifier for the logged-in user.
        
        Sends a request to the LinkedIn homepage with authenticated cookies
        and extracts the public identifier of the currently logged-in user.
        
        Returns:
            str: Public identifier of the logged-in user
            
        Raises:
            Exception: If the public identifier cannot be extracted
        """
        homepage_url = "https://www.linkedin.com"
        headers = deepcopy(get_headers(header_type="homepage"))
        
        response = await self.fetch(
            method="GET",
            url=homepage_url,
            headers=headers,
            cookies=self.cookies
        )
        
        public_identifier = extract_public_identifier(response)
        return public_identifier