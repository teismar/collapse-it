# Collapse it
[![Chat on Matrix](https://matrix.to/img/matrix-badge.svg)](https://matrix.to/#/#collapse-it:matrix.org) 

> [!WARNING]
> This is still in an early Development Phase and shouldn't be used in any productive way!

This is a minimal url shortener service. It is a simple web application that allows users to shorten long URLs. It is built with Python, Flask, and MariaDB.

## Why?
I am building this URL shortener service because, despite the existence of numerous alternatives, I find that they don't fully meet my specific needs or preferences, particularly in terms of being Python-based, API-first, modular, and customizable. I aim to create a service that not only leverages the power and simplicity of Python but also prioritizes a robust API-first approach, ensuring seamless integration and automation possibilities. The modular design is intended to facilitate easy maintenance and the ability to add or modify features without disrupting the core functionality. Moreover, customization is a key focus, allowing users to tailor the service to their unique requirements, which I find lacking in existing solutions. This project is not just about offering another URL shortener; it's about providing a solution that is thoughtfully designed with flexibility, scalability, and user-centricity at its core.

## Contributing
If you would like to contribute to this project, you are welcome to do so. Currently the project is in a very early stage and I am still working on the basic functionality. If you have any ideas or suggestions, feel free to open an issue or a pull request. You can also join the Matrix Space [here](https://matrix.to/#/#collapse-it:matrix.org) to discuss the project.

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
## Roadmap
- [x] **URL Shortening:** Create a basic URL shortening service with a simple web interface and API.
- [x] **URL Redirection:** Enable the shortened URLs to redirect to the original URLs when accessed.
- [ ] **GitHub Actions:** Set up continuous integration and deployment workflows to automate Code checking.
- [ ] **URL Expiration:** Implement a time-to-live (TTL) feature to allow users to set expiration times for shortened URLs.
- [ ] **Modular Design:** Refactor the codebase to be modular, allowing for easy feature selection and maintenance.
- [ ] **Custom URL Endings:** Implement functionality for users to create personalized short URL suffixes.
- [ ] **Link Click Analytics:** Develop features to track and report on metrics like access counts, geographical data, and device types for each shortened URL.
- [ ] **Authentication System:** Introduce user account creation and login mechanisms to allow personalized management of shortened URLs.
- [ ] **Multiple URLs Shortening:** Add capability for users to shorten batches of URLs simultaneously for efficiency.
- [ ] **API Key Administration:** Create a system for users to generate, manage, and revoke API keys for secure API usage.
- [ ] **API Usage Limiting:** Implement restrictions on API calls to prevent overuse and ensure equitable service distribution.
- [ ] **Service Scalability Enhancements:** Explore and integrate scalability solutions like load balancing to support growing user demand.
- [ ] **Multilingual Support:** Expand the web interface to include multiple language options for international users.
- [ ] **URL Safety Integration:** Collaborate with URL verification services to check and flag potentially harmful original URLs.
- [ ] **Browser Extension Development:** Create extensions or plugins for major browsers to enable direct URL shortening within the browser interface.
- [ ] **Security Enhancements:** Strengthen security measures, including enforcing secure connections, to protect user data and interactions.