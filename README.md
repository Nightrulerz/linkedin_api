# LinkedIn API Scraper (Flask & Selenium)

This project provides a Flask-based API for logging into a LinkedIn user profile, retrieving profile details, and fetching first-page connections data.

## Features
- Login to LinkedIn using Selenium automation.
- Retrieve LinkedIn profile details (name, company, title, email).
- Fetch first-page connection data with pagination support.
- API key-based authentication.
- Caching system for session reuse.

## Prerequisites
Ensure you have the following installed:

- Python 3.8+
- Google Chrome (Installed at `/usr/bin/google-chrome` or specify the correct path)
- ChromeDriver (Ensure it matches your Chrome version)

## Installation
1. **Clone the Repository**
   ```sh
   git clone https://github.com/your-repo/linkedin-api.git
   cd linkedin-api
   ```

2. **Create a Virtual Environment & Install Dependencies**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Download & Set Up ChromeDriver**
   ```sh
   wget "https://storage.googleapis.com/chrome-for-testing-public/120.0.6099.71/linux64/chromedriver-linux64.zip" -O chromedriver.zip
   unzip chromedriver.zip
   chmod +x chromedriver-linux64/chromedriver
   sudo mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
   ```

## Running the API
Start the Flask server:
```sh
python app.py
```

By default, it will run on `http://127.0.0.1:5000`.

## API Endpoints

### 1. Login & Fetch Profile Data
**Endpoint:** `POST /profile`

**Request Body (JSON):**
```json
{
  "username": "your_email@example.com",
  "password": "your_password",
  "api_key": "your_api_key"
}
```

**Response (JSON):**
```json
{
  "name": "John Doe",
  "company": "TechCorp",
  "title": "Software Engineer",
  "email": "johndoe@example.com"
}
```

### 2. Fetch Profile Connections (1st Page)
**Endpoint:** `POST /connections`

**Request Body (JSON):**
```json
{
  "username": "your_email@example.com",
  "password": "your_password",
  "api_key": "your_api_key",
  "connections": true
}
```

**Response (JSON):**
```json
{
  "profile": { "name": "John Doe", "company": "TechCorp" },
  "connections": [
    { "name": "Alice", "company": "ABC Corp", "title": "Manager" },
    { "name": "Bob", "company": "XYZ Inc", "title": "Developer" }
  ],
  "pagination_id": "encrypted_page_1"
}
```

### 3. Fetch Next Page of Connections
**Endpoint:** `POST /connections`

**Request Body (JSON):**
```json
{
  "username": "your_email@example.com",
  "password": "your_password",
  "api_key": "your_api_key",
  "pagination_id": "encrypted_page_1"
}
```

## Troubleshooting
### 1. **ChromeDriver Not Found Error**
- Ensure ChromeDriver is installed and matches your Chrome version.
- Verify the binary location using:
  ```sh
  which chromedriver
  ```

### 2. **Session Not Created: No Chrome Binary Found**
- Ensure Google Chrome is installed at `/usr/bin/google-chrome`.
- If it's installed elsewhere, update `login_page.py` to specify the correct path:
  ```python
  options.binary_location = "/path/to/google-chrome"
  ```

### 3. **Failed to Decode JSON Object**
- Ensure you're sending a valid JSON request with `Content-Type: application/json`.
- Use `Postman` or `curl` to test requests.

## License
This project is licensed under the MIT License.

