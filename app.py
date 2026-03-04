from flask import Flask, request, jsonify
from flask_cors import CORS
import social_db

app = Flask(__name__)
CORS(app)

@app.route('/api/users', methods=['POST'])
def api_create_user():
    data = request.get_json()
    result = social_db.create_user(
        email = data['email'],          # <-- Added comma
        username = data['username'],    # <-- Added comma
        first_name = data.get('first_name', ''), # <-- Added comma
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

@app.route('/api/posts', methods=['POST'])
def api_create_post():
    data = request.get_json()
    account_id = data.get('account_id')
    content = data.get('content')

    if not content:
        return jsonify({"success": False, "error": "Content is required"}), 400

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
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()
