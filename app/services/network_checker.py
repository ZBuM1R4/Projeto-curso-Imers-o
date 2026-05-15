import os
import socket
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()


def has_network_connection(timeout: int = 5) -> bool:
    supabase_url = os.getenv("SUPABASE_URL")

    if not supabase_url:
        return False

    try:
        parsed_url = urlparse(supabase_url)
        hostname = parsed_url.hostname

        if not hostname:
            return False

        socket.create_connection((hostname, 443), timeout=timeout)
        return True

    except OSError:
        return False