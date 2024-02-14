import datetime
import os

from dotenv import load_dotenv
from flask import Blueprint, Flask, jsonify, redirect, request

from extensions.shortened_url import ShortenedURL

# Load environment variables from the .env file for configuration purposes
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)

# Define Blueprints for API and URL forwarding functionality
api_blueprint = Blueprint("api", __name__, url_prefix="/api")
forwarding_blueprint = Blueprint("forward", __name__, url_prefix="/f")

# Configuration dictionary assembling database connection parameters from environment variables
config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_DATABASE"),
    "port": int(
        os.getenv("DB_PORT", 3306)
    ),  # Defaults to 3306 if DB_PORT is not specified
}

# Base URL for constructing shortened URLs, defaulting to http://localhost:5000 if not specified in the environment
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")


@api_blueprint.route("/time")
def get_current_time():
    """
    Endpoint to return the current server time in ISO 8601 format.

    Returns:
        A JSON response containing the current UTC time.
    """
    return jsonify(
        {"time": datetime.datetime.now(tz=datetime.timezone.utc).isoformat()}
    )


@api_blueprint.route("/shorten", methods=["POST"])
def shorten_url():
    """
    Endpoint to shorten a given URL. Expects a JSON payload with a "url" key and an optional "ttl" (time to live) key.

    Returns:
        A JSON response containing the shortened URL or an error message.
    """
    data = request.json
    original_url = data.get("url")
    if not original_url:
        return jsonify({"error": "URL is required"}), 400

    ttl = data.get("ttl", 300)  # Default TTL is 300 minutes
    short_code = ShortenedURL(config=config, url=original_url).shorten(ttl=ttl)
    shortened_url = f"{BASE_URL}/f/{short_code}"

    return jsonify({"short_url": shortened_url}), 201


@api_blueprint.route("/code_info/", methods=["POST"])
def get_url_info():
    """
    Endpoint to retrieve information about a shortened URL based on its short code.
    Expects a JSON payload with a "short_code" key.

    Returns:
        A JSON response containing the original URL and additional information, or an error message if not found.
    """
    data = request.json
    short_code = data.get("short_code")
    if not short_code:
        return jsonify({"error": "Short code is required"}), 400

    url_info = ShortenedURL(config=config).get_by_short_code(short_code)
    if url_info is None:
        return jsonify({"error": "URL not found"}), 404

    return jsonify(url_info)


@forwarding_blueprint.route("/<short_code>")
def redirect_to_original(short_code):
    """
    Endpoint that redirects to the original URL based on the provided short code.

    Args:
        short_code (str): The short code of the shortened URL.

    Returns:
        A redirection to the original URL, or a JSON error message if the URL is not found.
    """
    url_info = ShortenedURL(config=config).get_by_short_code(short_code)
    original_url = url_info.get("original_url") if url_info else None
    if original_url is None:
        return jsonify({"error": "URL not found"}), 404

    return redirect(original_url)


# Register the defined Blueprints with the Flask application
app.register_blueprint(api_blueprint)
app.register_blueprint(forwarding_blueprint)

if __name__ == "__main__":
    # Start the Flask application
    app.run()
