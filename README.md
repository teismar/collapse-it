# Collapse it

This is a minimal url shortener service. It is a simple web application that allows users to shorten long URLs. It is built with Python, Flask, and MariaDB.

## Concept
At the core, the application is a simple REST API that allows users to create, read, update, and delete shortened URLs. The application also provides a simple web interface to interact with the API.

## Features
- Shorten long URLs
- Retrieve original URLs from shortened URLs
- Custom TTL for shortened URLs

## Installation
1. Clone the repository
2. Edit the `example.env` file and save it as `.env`
3. Run `docker compose up` to start the application
4. Access the web interface at `https://example.com:80`
5. Access the API at `https://example.com:80/api`

## API
The API is a simple REST API that allows users to create, read, update, and delete shortened URLs.