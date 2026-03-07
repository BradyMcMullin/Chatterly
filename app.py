from flask import Flask, request, jsonify
from flask_cors import CORS
import social_db

app = Flask(__name__)
CORS(app)

@app.route('/api/users', methods=['POST'])
def api_create_user():
    data = request.get_json()
    result = social_db.create_user(
        email = data['email'],
        username = data['username'], 
        first_name = data.get('first_name', ''),
        last_name = data.get('last_name','')
    )

    if result["success"]:
        return jsonify(result), 201
    else:
        return jsonify(result), 400

@app.route('/api/feed/<int:account_id>', methods=['GET'])
def api_get_feed(account_id):
    feed = social_db.get_profile(account_id) 
    return jsonify(feed), 200

@app.route('api/users/<int:account_id>', methods=['GET'])
def api_get_account_info(account_id):
    account = social_db.get_profile(account_id)
    return jsonify(account), 200

@app.route('api/users/<int:account_id', methods=['POST'])
def api_add_profile_info(account_id, body):
    account_info = {"first_name":"", "last_name":"", "creation_date":"", "bio":"", "age":""}
    result = social_db.create_profile(
        account_info
    )
    if result["success"]:
        return jsonify(result), 201
    else:
        return jsonify(result), 400

@app.route('api/account/<int:account_id', methods=['PUT'])
def api_update_account_info(account_id, body):
    current_info = api_get_account_info(account_id)
    account_info = {"first_name":"", "last_name":"", "creation_date":"", "bio":"", "age":""}
    



@app.route('/api/catchup', methods=['GET'])
def api_get_catchup_feed():
	feed = social_db.get_catch_up_feed()
	return jsonify(feed), 200


@app.route('/api/posts', methods=['POST'])
def api_create_post():
    data = request.get_json()
    raw_account_data = data.get('account_id')

    # If the data is that big Vue object you see in the logs:
    if isinstance(raw_account_data, dict) and '_value' in raw_account_data:
        account_id = raw_account_data['_value']
    else:
        account_id = raw_account_data

    # Now we have the raw number (1), we can proceed safely
    content = data.get('content')

    conn = social_db.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO posts (account_id, content) VALUES (?, ?)",
            (account_id, content)
        )
        conn.commit()
        return jsonify({"success": True, "post_id": cursor.lastrowid}), 201
    except Exception as e:
        print(f"DATABASE ERROR: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
