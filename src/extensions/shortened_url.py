import hashlib
import random
from datetime import datetime, timedelta, timezone

from database import Database

# TODO: MYPY


def generate_unique_short_code(database: Database, url: str) -> str:
    """
    Generates a unique short code for the given URL using a BLAKE2b hash and checks for uniqueness against the database.
    This version selects characters from the hash at random positions to form the short code.

    Args:
        database (Database): An instance of the Database class to check for short code uniqueness.
        url (str): The original URL to generate a short code for.

    Returns:
        str: A unique short code for the URL.
    """
    # BLAKE2b hash of the URL with a digest size of 5 for brevity
    hash_digest = hashlib.blake2b(url.encode(), digest_size=5).hexdigest()

    # Initialize an empty short code string
    short_code = ""

    # Ensure the short code is unique
    while not short_code or database.short_code_exists(short_code):
        # Generate a new short code using random positions in the hash digest
        short_code_positions = random.sample(range(len(hash_digest)), 5)
        short_code = "".join([hash_digest[i] for i in short_code_positions])

        # If not unique, append a character to the URL to change the hash and try again
        url += "x"

        # Recalculate the hash digest with the modified URL
        hash_digest = hashlib.blake2b(url.encode(), digest_size=5).hexdigest()

    return short_code


class ShortenedURL:
    """
    Represents a shortened URL and provides functionality to shorten URLs, extend their life, and retrieve the
    original URL from a short code. It interacts with a database backend to persist URL mappings.

    Attributes:
        url (str | None): The original URL to be shortened. Can be None if not set during initialization.
        database (Database): An instance of the Database class for performing database operations.
    """

    def __init__(self, config: dict, url: str | None = None):
        """
        Initializes the ShortenedURL instance with a database connection and optionally an URL.

        Args:
            config (dict): Configuration dictionary containing database connection parameters.
            url (str, optional): The original URL to be shortened. Defaults to None.
        """
        self.url = url
        self.database = Database(**config)

    def shorten(self, ttl: int) -> str:
        """
        Shortens the provided URL with a specified time-to-live (TTL). If the URL is already present in the database,
        its expiration is extended instead.

        Args:
            ttl (int): The time-to-live (TTL) in minutes for the shortened URL.

        Returns:
            str: The short code for the shortened URL.

        Raises:
            ValueError: If the URL is not set.
        """
        if not self.url:
            raise ValueError("URL is required")

        short_code = self.database.fetch_short_code(self.url)
        if not short_code:
            short_code = generate_unique_short_code(self.database, self.url)
            self.database.insert_url(
                short_code=short_code,
                original_url=self.url,
                expires_at=datetime.now(tz=timezone.utc) + timedelta(minutes=ttl),
            )
        else:
            self.database.extend_url(
                short_code, datetime.now(tz=timezone.utc) + timedelta(minutes=ttl)
            )

        return short_code

    def get_by_shortened_url(self, short_url: str) -> str | None:
        """
        Retrieves the original URL from a shortened URL.

        Args:
            short_url (str): The full shortened URL.

        Returns:
            str | None: The original URL if found, None otherwise.
        """
        short_code = short_url.split("/")[-1]
        url_details = self.get_by_short_code(short_code)
        if url_details:
            return url_details.get("original_url")
        return None

    def get_by_short_code(self, short_code: str) -> dict | None:
        """
        Retrieves the original URL and its details based on the short code.

        Args:
            short_code (str): The short code associated with the original URL.

        Returns:
            dict | None: A dictionary containing the original URL and its details if found, None otherwise.
        """
        return self.database.fetch_url(short_code)
