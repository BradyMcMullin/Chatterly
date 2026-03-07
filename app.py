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
    # Change get_profile to get_feed
    feed = social_db.get_feed(account_id) 
    return jsonify(feed), 200

@app.route('/api/users/<int:account_id>', methods=['GET'])
def api_get_account_info(account_id):
    account = social_db.get_profile(account_id)
    return jsonify(account), 200


@app.route('/api/users/<int:account_id>', methods=['POST'])
def api_add_profile_info(account_id, body):
    account_info = {"first_name":"", "last_name":"", "creation_date":"", "bio":"", "age":""}
    result = social_db.create_profile(
        account_info
    )
    if result["success"]:
        return jsonify(result), 201
    else:
        return jsonify(result), 400

@app.route('/api/profile/<int:account_id>', methods=['POST'])
def api_update_profile(account_id):
    data = request.get_json()
    # Extract values from the frontend request
    result = social_db.update_profile(
        account_id, 
        data.get('bio', ''), 
        data.get('age', '')
    )
    return jsonify(result), (200 if result["success"] else 400)
    
@app.route('/api/accounts', methods=['GET'])
def api_get_all_accounts():
    conn = social_db.get_db_connection()
    # This matches the structure of your accounts/users tables
    accounts = conn.execute('''
        SELECT a.account_id, u.username, u.first_name 
        FROM accounts a 
        JOIN users u ON a.user_id = u.user_id
    ''').fetchall()
    conn.close()
    return jsonify([dict(row) for row in accounts]), 200

@app.route('/api/accounts/<int:user_id>', methods=['GET'])
def api_get_my_accounts(user_id):
    conn = social_db.get_db_connection()
    try:
        # We select 'handle' from accounts. 
        # No need to join 'users' anymore if we just want the handles!
        accounts = conn.execute('''
            SELECT account_id, handle 
            FROM accounts 
            WHERE user_id = ?
        ''', (user_id,)).fetchall()
        return jsonify([dict(row) for row in accounts]), 200
    except Exception as e:
        print(f"Database Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# Add the account creation route
@app.route('/api/accounts/create', methods=['POST'])
def api_create_account():
    data = request.get_json()
    # Logic calls the new multi-table insertion function in social_db.py
    result = social_db.create_account(data['user_id'], data['username'])
    return jsonify(result), 201 if result["success"] else 400

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
