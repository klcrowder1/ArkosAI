"""
Main client for the Arkos API.
"""

from .auth import Auth, ApiKeyAuth, JwtAuth
from .resources.cameras import CamerasResource
from .resources.events import EventsResource
from .resources.recordings import RecordingsResource
from .resources.health import HealthResource
from .resources.storage import StorageResource
from .resources.system import SystemResource


class ArkosClient:
    """Client for the Arkos API."""

    def __init__(
        self,
        host,
        api_key=None,
        username=None,
        password=None,
        timeout=30,
    ):
        """
        Initialize the client.

        Args:
            host (str): API host
            api_key (str, optional): API key for authentication
            username (str, optional): Username for JWT authentication
            password (str, optional): Password for JWT authentication
            timeout (int, optional): Request timeout in seconds
        """
        self.host = host.rstrip("/")
        self.timeout = timeout

        # Set up authentication
        if api_key:
            self.auth = ApiKeyAuth(api_key)
        elif username and password:
            self.auth = JwtAuth(self.host, username, password)
        else:
            self.auth = Auth()

        # Initialize resources
        self.cameras = CamerasResource(self)
        self.events = EventsResource(self)
        self.recordings = RecordingsResource(self)
        self.health = HealthResource(self)
        self.storage = StorageResource(self)
        self.system = SystemResource(self)
