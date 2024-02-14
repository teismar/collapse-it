import logging
from datetime import datetime
from typing import Dict, Optional

import mysql.connector
from mysql.connector import MySQLConnection


class Database:
    """
    This class handles database operations for a URL shortener service. It supports operations such as creating the
    database and required tables, inserting new shortened URLs, updating and deactivating URLs, and fetching URLs based
    on their short codes. It utilizes parameterized queries to safeguard against SQL injection attacks.

    Attributes:
        config (dict): Configuration parameters for connecting to the MySQL database.
        conn (MySQLConnection, optional): A connection to the MySQL database. Initially None until connected.
        cursor (MySQLCursor, optional): A cursor for executing database operations. Initially None until connected.
        logger (Logger): A logger for logging database operation messages.
    """

    def __init__(self, **config) -> None:
        """
        Initializes a new instance of the Database class, setting up the logger and attempting to establish a
        database connection.

        Args:
            **config: Arbitrary keyword arguments containing database connection parameters such as host, user,
                      password, and database name.
        """
        self.config = config
        self.conn: Optional[MySQLConnection] = None
        self.cursor = None
        self.setup_logger()
        self.connect()
        self.ensure_tables()

    def setup_logger(self) -> None:
        """Sets up a logger for logging database operations with an INFO level and a standard format."""
        self.logger = logging.getLogger("DatabaseLogger")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def connect(self) -> None:
        """
        Establishes a connection to the MySQL database using the configuration parameters provided at initialization.
        It sets up a cursor for executing SQL queries.
        """
        try:
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor()
            self.logger.info("Successfully connected to the database.")
        except mysql.connector.Error as err:
            self.logger.error(f"Database connection failed: {err}")

    def ensure_tables(self) -> None:
        """
        Ensures that the required tables for the URL shortener service exist within the database. If not, it creates
        them. This method specifically checks for the existence of a 'short_urls' table and creates it if necessary.
        """
        create_table_query = """
        CREATE TABLE IF NOT EXISTS short_urls (
            id INT AUTO_INCREMENT PRIMARY KEY,
            short_code VARCHAR(10) NOT NULL UNIQUE,
            original_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE
        );
        """
        try:
            self.cursor.execute(create_table_query)
            self.conn.commit()
            self.logger.info("Tables ensured to exist.")
        except mysql.connector.Error as err:
            self.logger.error(f"Failed to ensure tables: {err}")

    def insert_url(
        self,
        short_code: str,
        original_url: str,
        expires_at: Optional[datetime] = None,
        is_active: bool = True,
    ) -> int:
        """
        Inserts a new URL into the 'short_urls' table.

        Args:
            short_code (str): The unique short code associated with the original URL.
            original_url (str): The original URL to be shortened.
            expires_at (datetime, optional): The expiration date and time for the short URL. Defaults to None.
            is_active (bool): The active status of the short URL. Defaults to True.

        Returns:
            int: The last row ID of the inserted URL on success, or -1 if the insertion fails.
        """
        insert_query = """
        INSERT INTO short_urls (short_code, original_url, expires_at, is_active) VALUES (%s, %s, %s, %s);
        """
        try:
            self.cursor.execute(
                insert_query, (short_code, original_url, expires_at, is_active)
            )
            self.conn.commit()
            inserted_id = self.cursor.lastrowid
            self.logger.info(f"URL inserted with ID: {inserted_id}")
            return inserted_id
        except mysql.connector.Error as err:
            self.logger.error(f"Failed to insert URL: {err}")
            return -1

    def update_url(self, short_code: str, new_url: str) -> bool:
        """
        Updates the original URL for a given short code in the 'short_urls' table.

        Args:
            short_code (str): The unique short code associated with the URL to be updated.
            new_url (str): The new original URL to replace the old one.

        Returns:
            bool: True if the URL was successfully updated, False otherwise.
        """
        update_query = """
        UPDATE short_urls SET original_url = %s WHERE short_code = %s;
        """
        try:
            self.cursor.execute(update_query, (new_url, short_code))
            self.conn.commit()
            updated = self.cursor.rowcount > 0
            if updated:
                self.logger.info(f"URL updated for short_code: {short_code}")
            return updated
        except mysql.connector.Error as err:
            self.logger.error(f"Failed to update URL: {err}")
            return False

    def deactivate_url(self, short_code: str) -> bool:
        """
        Deactivates the URL associated with the given short code by setting its 'is_active' flag to False.

        Args:
            short_code (str): The unique short code of the URL to be deactivated.

        Returns:
            bool: True if the URL was successfully deactivated, False otherwise.
        """
        deactivate_query = """
        UPDATE short_urls SET is_active = FALSE WHERE short_code = %s;
        """
        try:
            self.cursor.execute(deactivate_query, (short_code,))
            self.conn.commit()
            deactivated = self.cursor.rowcount > 0
            if deactivated:
                self.logger.info(f"URL deactivated for short_code: {short_code}")
            return deactivated
        except mysql.connector.Error as err:
            self.logger.error(f"Failed to deactivate URL: {err}")
            return False

    def fetch_url(self, short_code: str) -> Optional[Dict[str, any]]:
        """
        Fetches URL details by short code, considering its active status and expiration.

        Args:
            short_code (str): The unique short code of the URL to be fetched.

        Returns:
            Optional[Dict[str, any]]: A dictionary containing 'original_url', 'is_active', and 'expires_at' if the
            URL is found. Returns None if no URL is found for the given short code.
        """
        fetch_query = """
        SELECT original_url, is_active, expires_at FROM short_urls WHERE short_code = %s;
        """
        try:
            self.cursor.execute(fetch_query, (short_code,))
            result = self.cursor.fetchone()
            if result:
                original_url, is_active, expires_at = result
                url_details = {
                    "original_url": original_url,
                    "is_active": is_active,
                    "expires_at": expires_at,
                }
                self.logger.info(f"URL fetched for short_code: {short_code}")
                return url_details
            return None
        except mysql.connector.Error as err:
            self.logger.error(f"Failed to fetch URL: {err}")
            return None

    def fetch_short_code(self, original_url: str) -> Optional[str]:
        """
        Fetches the short code for a given original URL.

        Args:
            original_url (str): The original URL whose short code needs to be fetched.

        Returns:
            Optional[str]: The short code associated with the given original URL if found, None otherwise.
        """
        fetch_query = """
        SELECT short_code FROM short_urls WHERE original_url = %s;
        """
        try:
            self.cursor.execute(fetch_query, (original_url,))
            result = self.cursor.fetchone()
            if result:
                short_code = result[0]
                self.logger.info(f"Short code fetched for original_url: {original_url}")
                return short_code
            return None
        except mysql.connector.Error as err:
            self.logger.error(f"Failed to fetch short code: {err}")
            return None

    def extend_url(self, short_code: str, new_expiration: datetime) -> bool:
        """
        Extends the expiration date of a URL based on its short code.

        Args:
            short_code (str): The unique short code of the URL whose expiration is to be extended.
            new_expiration (datetime): The new expiration date and time for the URL.

        Returns:
            bool: True if the expiration was successfully extended, False otherwise.
        """
        extend_query = """
        UPDATE short_urls SET expires_at = %s WHERE short_code = %s;
        """
        try:
            self.cursor.execute(extend_query, (new_expiration, short_code))
            self.conn.commit()
            extended = self.cursor.rowcount > 0
            if extended:
                self.logger.info(f"Expiration extended for short_code: {short_code}")
            return extended
        except mysql.connector.Error as err:
            self.logger.error(f"Failed to extend URL expiration: {err}")
            return False

    def short_code_exists(self, short_code: str) -> bool:
        """
        Checks if the given short code already exists in the database using the SQL EXISTS function.

        Args:
            short_code (str): The short code to check for existence.

        Returns:
            bool: True if the short code exists, False otherwise.
        """
        query = (
            "SELECT EXISTS(SELECT 1 FROM short_urls WHERE short_code = %s) AS exists;"
        )
        try:
            self.cursor.execute(query, (short_code,))
            (exists,) = self.cursor.fetchone()
            return bool(exists)
        except mysql.connector.Error as err:
            self.logger.error(f"Failed to check short code existence: {err}")
            return False

    def close(self) -> None:
        """
        Closes the database connection and the cursor if they are open. This should be called to free up resources
        when the Database object is no longer needed.
        """
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            self.logger.info("Database connection closed.")
