import requests

class BaseAPIClient:
    """A base client for making API requests."""
    def __init__(self, base_url, api_key=None, timeout=10):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout

    def _request(self, method, endpoint, params=None):
        """Makes a request to the API."""
        url = f"{self.base_url}{endpoint}"
        
        if params is None:
            params = {}
        
        if self.api_key:
            params['api_key'] = self.api_key

        try:
            response = requests.request(method, url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.RequestException as e:
            return None, str(e)

    def get(self, endpoint, params=None):
        """Performs a GET request."""
        return self._request("GET", endpoint, params)
