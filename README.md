
---

### Web Page Screenshot Service

This repository contains a Python service built with Flask that enables capturing screenshots of web pages using Selenium. The service supports multiple endpoints for managing and retrieving screenshots based on user requests.

#### Features

- **GET /isalive**
   - Endpoint for checking server health.

- **POST /screenshots**
   - Initiates the process of crawling a web page starting from a given URL and capturing screenshots.
   - **Parameters**:
      - `start_url`: The URL of the webpage to start crawling from.
      - `num_links`: Number of links to follow from the initial page.
   - **Response**:
      - Unique `run_id` representing the crawling session.

- **GET /screenshots/:id**
   - Retrieves screenshots collected during a specific crawling session identified by `run_id`.

#### Requirements

To run this application locally or in a Docker container, ensure you have the following installed:

- Python 3.9+
- Docker (optional, for containerized deployment)
- Git

#### Installation and Setup

1. **Clone the Repository**
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Environment Variables**
   - Create a `.env` file in the root directory (if necessary) to configure environment variables. Example:
     ```plaintext
     SCREENSHOT_DIR=/app/screenshots
     DATABASE_URL=sqlite:///screenshots.db
     ```

#### Running the Application

**Local Development**

- Run the Flask application:
  ```bash
  python screenshot_service/screenshot_service_app.py
  ```
- The service will be accessible at `http://localhost:5001`.

**Docker**

1. **Build Docker Image**
   ```bash
   docker build -t web-screenshot-service .
   ```

2. **Run Docker Container**
   ```bash
   docker run -p 5001:5001 web-screenshot-service
   ```
   - The service will be available at `http://localhost:5001`.

#### Usage

1. **Check Server Health**
   ```bash
   GET http://localhost:5001/isalive
   ```

2. **Start Crawling and Capture Screenshots**
   ```bash
   POST http://localhost:5001/screenshots
   Content-Type: application/json

   {
       "start_url": "https://edited.com",
       "num_links": 5
   }
   ```
   - Retrieves a `run_id` which can be used to fetch screenshots later.

   **Using curl:**
   ```bash
   curl -X POST http://localhost:5001/screenshots -H "Content-Type: application/json" -d '{"start_url": "https://edited.com", "num_links": 5}'
   ```

3. **Retrieve Screenshots**
   ```bash
   GET http://localhost:5001/screenshots/<run_id>
   ```
   - Returns screenshots captured during the specified crawling session identified by `<run_id>`.

#### Database

- **SQLite** is used by default for storing `Screenshot` metadata.

#### Running the Database

To manage the SQLite database (`screenshots.db`):

1. **Access SQLite Shell**
   ```bash
   sqlite3 screenshots.db
   ```

2. **Perform Database Operations**
   - Execute SQL commands to query or modify the database schema and data.

#### Monitoring and Optimization

- **Performance**: Optimizations include efficient crawling and screenshot capturing using Selenium.
- **Storage Optimization**: Implementing strategies like storing screenshots in cloud storage for scalability.
- **Monitoring**: Implement monitoring for server health, request/response times, and resource utilization.

#### Bonus Points

- The service is designed to run inside Docker for portability and scalability.
- Continuous optimization and monitoring ensure high performance under load.
