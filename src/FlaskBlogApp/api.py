# api.py

from flask import Blueprint, request, jsonify

api = Blueprint('api', __name__)

# Example API key; in production, store securely in environment variables or a database
API_KEYS = {
    "my_secret_api_key": "User1",
    "another_api_key": "User2"
}

def require_api_key(func):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if api_key and api_key in API_KEYS:
            # Optionally, you can also set the user context if needed
            return func(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized access"}), 403
    wrapper.__name__ = func.__name__
    return wrapper

# Example secured endpoint
@api.route('/secure-data', methods=['GET'])
@require_api_key
def secure_data():
    return jsonify({"message": "This is secured data, accessible only with a valid API key"}), 200

# Another secured endpoint with personalized response based on API key
@api.route('/user-info', methods=['GET'])
@require_api_key
def user_info():
    api_key = request.headers.get('x-api-key')
    user = API_KEYS.get(api_key)
    return jsonify({"message": f"Hello, {user}! You have access to this information."}), 200



#from flask import Blueprint, request, jsonify

## Create a Blueprint for your API routes
#api = Blueprint('api', __name__)

@api.route('/data', methods=['GET', 'POST'])
def data():
    if request.method == 'POST':
        data = request.get_json()
        return jsonify({"message": "Data received", "data": data}), 201
    else:
        return jsonify({"key1": "value1", "key2": "value2"}), 200

@api.route('/update', methods=['PUT'])
def update_data():
    data = request.get_json()
    return jsonify({"message": "Data updated", "data": data}), 200

@api.route('/delete', methods=['DELETE'])
def delete_data():
    data = request.get_json()
    return jsonify({"message": "Data deleted", "data": data}), 200