import asyncio
from copy import deepcopy

from tenacity import retry, stop_after_attempt, wait_fixed
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
        Initializes the LinkedinConnectionsData class.
        
        Args:
            email (str): LinkedIn account email.
            password (str): LinkedIn account password.
            pagination_id (str, optional): Encoded pagination ID for fetching paginated results. Defaults to None.
        """
        self.user_email = email
        self.user_password = password
        self.user_pagination_id = pagination_id
        self.user_session = LoginPage(email=self.user_email, password=self.user_password)
        self.cookies = self.user_session.get_cookie()
        self.request = Request()

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(10))
    async def fetch(self, url, params=None, headers=None, cookies=None, method="GET", data=None):
        """
        Sends an HTTP request using the provided parameters with retry mechanism.
        
        Args:
            url (str): The target URL.
            params (dict, optional): Query parameters for the request. Defaults to None.
            headers (dict, optional): Headers for the request. Defaults to None.
            cookies (dict, optional): Cookies for authentication. Defaults to None.
            method (str, optional): HTTP method (GET, POST, etc.). Defaults to "GET".
            data (dict, optional): Data payload for POST requests. Defaults to None.

        Returns:
            Response object or None if an error occurs.
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

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(10))
    async def _get_listing_data(self, page_number):
        """
        Fetches LinkedIn connections data for a given page number.
        
        Args:
            page_number (int): The page number to fetch connections from.

        Returns:
            list: List of LinkedIn profile IDs of the connections.
        """
        try:
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

            parser = DataParser(response)
            connections_profile_ids = parser.get_connections_profile_ids()
            return connections_profile_ids
        except Exception as error:
            error = format_exc()
            print(error)

    async def get_connections_data(self):
        """
        Fetches LinkedIn connections data including profile details.
        
        Returns:
            dict: Dictionary containing profile data and next pagination ID.
        """
        try:
            page_number = (
                decode_pagination_id(self.user_pagination_id)
                if self.user_pagination_id
                else 0
            )
            
            connections_profile_ids = await self._get_listing_data(page_number=page_number)
            profile_data = await self.scrape_profile_data(connections_profile_ids)
            
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
        Scrapes profile data for a given list of LinkedIn profile IDs.
        
        Args:
            connections_profile_ids (list): List of LinkedIn profile IDs to scrape.

        Returns:
            list: List of dictionaries containing profile data.
        """
        scraper = LinkedinProfileData(email=self.user_email, password=self.user_password)
        try:
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
            return []