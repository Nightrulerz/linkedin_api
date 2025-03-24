import asyncio
from copy import deepcopy

from tenacity import retry, stop_after_attempt
from traceback import format_exc
from scraping.login_page import LoginPage
from scraping.data_parser import DataParser
from scraping.profile_page import LinkedinProfileData
from scraping.requests import Request
from scraping.utils import (decode_pagination_id,
                           encode_pagination_id, get_headers)


class LinkedinConnectionsData:
    def __init__(self, email, password, pagination_id=None):
        """
        Initialize the LinkedIn connections data scraper.
        
        Args:
            email (str): LinkedIn account email for authentication
            password (str): LinkedIn account password for authentication
            pagination_id (str, optional): Pagination identifier to resume scraping from a specific page
        """
        self.user_email = email
        self.user_password = password
        self.user_pagination_id = pagination_id
        self.user_session = LoginPage(email=self.user_email, password=self.user_password)
        self.cookies = self.user_session.get_cookie()
        self.request = Request()

    @retry(stop=stop_after_attempt(10))
    async def fetch(self, url, params=None, headers=None, cookies=None, method="GET", data=None):
        """
        Make an HTTP request with retry capability.
        
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
        try:
            response = await self.request.fetch(
                url=url, 
                params=params, 
                headers=headers, 
                cookies=cookies,
                method=method,
                data=data
            )
            return response
        except Exception as error:
            error = format_exc()
            print(error)

    @retry(stop=stop_after_attempt(10))
    async def _get_listing_data(self, page_number):
        """
        Retrieve connection listings data for a specific page.
        
        Args:
            page_number (int): The page number to retrieve data from
            
        Returns:
            list: List of connection profile IDs from the requested page
            
        Raises:
            Exception: If all retry attempts fail
        """
        try:
            # Sending API request
            api_url = "https://www.linkedin.com/voyager/api/relationships/dash/connections"
            headers = deepcopy(get_headers(header_type="profile_page"))
            headers["csrf-token"] = self.cookies["JSESSIONID"].replace('"', "").strip()
            start = 40 * page_number
            params = {
                "decorationId": "com.linkedin.voyager.dash.deco.web.mynetwork.ConnectionListWithProfile-16",
                "count": "40",
                "q": "search",
                "sortType": "RECENTLY_ADDED",
                "start": str(start),
            }
            response = await self.fetch(
                url=api_url, params=params, headers=headers, cookies=self.cookies
            )

            # Extracting profiles-ids of the connections
            parser = DataParser(response)
            connections_profile_ids = parser.get_connections_profile_ids()
            return connections_profile_ids
        except Exception as error:
            error = format_exc()
            print(error)

    async def get_connections_data(self):
        """
        Main function to retrieve connection data with pagination support.
        
        This function retrieves a list of LinkedIn connections and their profile data.
        It manages pagination to support retrieving connections across multiple pages.
        
        Returns:
            dict: Dictionary containing:
                - profiles (list): List of profile data for the connections
                - pagination_id (str): ID to use for retrieving the next page of connections
                
        Raises:
            Exception: If there's an error during the data retrieval process
        """
        try:
            # Getting pagenumber from pagination_id
            page_number = (
                decode_pagination_id(self.user_pagination_id)
                if self.user_pagination_id
                else 0
            )

            # Extracting the listings of the profiles in the connections
            connections_profile_ids = await self._get_listing_data(page_number=page_number)
            
            # Scraping all the profile data
            profile_data = await self.scrape_profile_data(connections_profile_ids)

            # Setting up next pagination ID
            next_page_number = page_number + 1
            next_pagination_id = encode_pagination_id(next_page_number)

            connections_data = {
                "profiles": profile_data,
                "pagination_id": next_pagination_id,
            }
            return connections_data
        except Exception as error:
            error = format_exc()
            print(error)

    async def scrape_profile_data(self, connections_profile_ids):
        """
        Concurrently scrape data for multiple LinkedIn profiles.
        
        This function implements a concurrency control mechanism using semaphores
        to limit the number of simultaneous requests to LinkedIn servers.
        
        Args:
            connections_profile_ids (list): List of LinkedIn profile IDs to scrape
            
        Returns:
            list: List of profile data dictionaries for each requested profile
            
        Raises:
            Exception: If there's an error during the profile data scraping process
        """
        try:
            scraper = LinkedinProfileData(email=self.user_email, password=self.user_password)
            semaphore = asyncio.Semaphore(6)
            async def worker(profile_id):
                async with semaphore:
                    profile_data = await scraper.get_profile_data(public_identifier=profile_id)
                    return profile_data
            tasks = [worker(profile_id) for profile_id in connections_profile_ids]
            all_profile_data = await asyncio.gather(*tasks)
            return all_profile_data
        except Exception as error:
            error = format_exc()
            print(error)
