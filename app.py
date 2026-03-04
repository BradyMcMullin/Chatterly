from flask import Flask, request, jsonify
from flask_cors import CORS
import social_db

app = Flask(__name__)
CORS(app)

@app.route('/api/users', methods=['POST'])
def api_create_user():
    data = request.get_json()
    result = social_db.create_user(
        email = data['email']
        username = data['username']
        first_name = data.get('first_name', ''), # get() is used for saftey, since names arent required
        last_name = data.get('last_name','')
    )
    
    if result["success"]:
        return jsonify(result), 201
    else:
        return jsonify(result), 400

@app.route('/api/feed/<int:account_id>', methods=['GET'])
def api_get_feed(account_id):
    feed = social_db.get_feed(account_id) 
    return jsonify(feed), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    
