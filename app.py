from flask import Flask, request, jsonify
from authentication.authentication import authenticate
from scraping.connection_page import LinkedinConnectionsData
from scraping.profile_page import LinkedinProfileData
from traceback import format_exc
import time

app = Flask(__name__)


@app.route("/")
def home():
    return "LinkedIn API is running!"

@app.route('/profile', methods=['POST'])
async def profile_data():
    try:
        data = request.json
        print(data)
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        api_key = data.get("api_key")
        user_email = data.get("username")
        user_password = data.get("password")
        
        # Validate required fields
        if not api_key or not user_email or not user_password:
            return jsonify({"error": "api_key, username and password are required"}), 400
        
        # Create model-like object for authentication
        class AuthObject:
            def __init__(self, key):
                self.api_key = key
                
        # Authenticate API key
        valid_call = authenticate(AuthObject(api_key))
        if not valid_call:
            return jsonify({"error": "Invalid API Key", "status_code": 401}), 401

        # Call your parser function
        scraping = LinkedinProfileData(user_email, user_password)
        profile_data = await scraping.get_profile_data()
        return jsonify({"message": "Data processed", "data": profile_data}), 200
    
    except Exception as error:
        error = format_exc()
        print(error)
        return jsonify({"error": str(error)}), 500

@app.route('/connections', methods=['POST'])
async def get_connections():
    start = time.time()
    try:
        data = request.json
        api_key = data.get("api_key")
        user_email = data.get("username")
        user_password = data.get("password")
        pagination_id = data.get("pagination_id")
        
        # Validate required fields
        if not api_key or not user_email or not user_password:
            return jsonify({"error": "api_key, username and password are required"}), 400
        
        # Create model-like object for authentication
        class AuthObject:
            def __init__(self, key):
                self.api_key = key
                
        # Authenticate API key
        valid_call = authenticate(AuthObject(api_key))
        if not valid_call:
            return jsonify({"error": "Invalid API Key", "status_code": 401}), 401

        scraping = LinkedinConnectionsData(
            email=user_email,
            password=user_password,
            pagination_id=pagination_id
        )
        connections_data = await scraping.get_connections_data()
        end = time.time()
        print(f"Processing time: {end - start} seconds")
        return jsonify({"message": "Data processed", "connections_data": connections_data}), 200
        
    except Exception as error:
        return jsonify({"error": str(error)}), 500

if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=5000, threaded=True)
    app.run(debug=True)