from abc import ABC, abstractmethod


class AbstractRequest(ABC):
    """
    Abstract base class for making asynchronous HTTP requests.
    
    This class defines the interface that must be implemented by any subclass.
    """
    
    @abstractmethod
    async def fetch_data(
        self,
        method: str = "GET",
        url: str = None,
        params: dict = None,
        data: dict = None,
        headers: dict = None,
        cookies: dict = None,
    ):
        """
        Abstract method for making an HTTP request.
        
        Args:
            method (str): HTTP method (GET, POST, etc.). Defaults to "GET".
            url (str): Target URL for the request.
            params (dict, optional): Query parameters for the request. Defaults to None.
            data (dict, optional): Data payload for POST requests. Defaults to None.
            headers (dict, optional): Headers for the request. Defaults to None.
            cookies (dict, optional): Cookies for authentication. Defaults to None.
        
        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("`fetch_data` Not implemented")