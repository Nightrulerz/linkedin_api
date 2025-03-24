from curl_cffi.requests import AsyncSession
from curl_cffi.requests.errors import CurlError, RequestsError
from request_exceptions import RequestFailedException, InvalidResponseException

class Request:
    async def fetch(
            self,
            method="GET",
            url=None,
            params=None,
            data=None,
            headers=None,
            cookies=None
    ):
        """
        Sends an asynchronous HTTP request and handles errors consistently.
        
        Args:
            method (str): HTTP method (e.g., "GET", "POST"). Defaults to "GET".
            url (str): The target URL.
            params (dict, optional): Query parameters for the request. Defaults to None.
            data (dict, optional): Data payload for POST requests. Defaults to None.
            headers (dict, optional): Headers for the request. Defaults to None.
            cookies (dict, optional): Cookies for authentication. Defaults to None.
        
        Returns:
            ResponseWrapper: A custom response object containing status_code, headers, text, content, URL, and cookies.
        
        Raises:
            RequestFailedException: If the request fails after multiple attempts.
        """
        from scraping.requests.utils import get_request_data
        
        # Set default values
        headers = headers or {}
        
        # Get random user agent data
        random_request_data = get_request_data()
        headers["user-agent"] = random_request_data["useragent"]
        
        async with AsyncSession() as session:
            for attempt in range(3):
                try:
                    response = await session.request(
                        method=method,
                        url=url,
                        data=data,
                        params=params,
                        cookies=cookies,
                        headers=headers,
                        impersonate=random_request_data["impersonate"],
                        max_redirects=5
                    )
                    
                    # Check if the response is valid
                    if response.status_code >= 400:
                        error_message = f"Request failed with status code: {response.status_code}"
                        raise RequestFailedException(error_message)
                    
                    # Create compatible response object
                    class ResponseWrapper:
                        """
                        Wrapper class for HTTP responses to provide structured access.
                        """
                        def __init__(self, http_response):
                            """
                            Initializes the ResponseWrapper.
                            
                            Args:
                                http_response: The original HTTP response object.
                            """
                            self.status_code = http_response.status_code
                            self.headers = http_response.headers
                            self.text = http_response.text
                            self._content = http_response.content
                            self.url = http_response.url
                            self.cookies = http_response.cookies
                            
                        def json(self):
                            """
                            Parses the response body as JSON.
                            
                            Returns:
                                dict: The parsed JSON data.
                            
                            Raises:
                                InvalidResponseException: If the response is not valid JSON.
                            """
                            try:
                                import json
                                return json.loads(self.text)
                            except json.JSONDecodeError:
                                raise InvalidResponseException("Failed to parse JSON response")
                                
                        @property
                        def content(self):
                            """
                            Returns the raw content of the response.
                            
                            Returns:
                                bytes: The response content.
                            """
                            return self._content
                    
                    return ResponseWrapper(response)
                    
                except (CurlError, RequestsError) as error:
                    error_message = f"Curl-CFFI request failed (attempt {attempt+1}/3): {error}"
                    if attempt == 2:  # Last attempt
                        raise RequestFailedException(error_message)
