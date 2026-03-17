from flask import Flask, request, jsonify
from flask_cors import CORS
import social_db

app = Flask(__name__)
CORS(app)


@app.route("/api/users", methods=["POST"])
def api_create_user():
    data = request.get_json()
    result = social_db.create_user(
        email=data["email"],  # <-- Added comma
        username=data["username"],  # <-- Added comma
        first_name=data.get("first_name", ""),  # <-- Added comma
        last_name=data.get("last_name", ""),
    )

    if result["success"]:
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@app.route("/api/feed/<int:account_id>", methods=["GET"])
def api_get_feed(account_id):
    feed = social_db.get_feed(account_id)
    return jsonify(feed), 200


@app.route("/api/catchup", methods=["GET"])
def api_get_catchup_feed():
    feed = social_db.get_catch_up_feed()
    return jsonify(feed), 200


@app.route("/api/ghosts/<int:account_id>", methods=["GET"])
def api_get_ghost_followers(account_id):
    limit = request.args.get("limit", default=10, type=int)
    ghosts = social_db.get_ghost_followers(account_id, limit)
    return jsonify(ghosts), 200


@app.route("/api/posts", methods=["POST"])
@app.route("/api/posts", methods=["POST"])
def api_create_post():
    data = request.get_json()
    raw_account_data = data.get("account_id")

    # If the data is that big Vue object you see in the logs:
    if isinstance(raw_account_data, dict) and "_value" in raw_account_data:
        account_id = raw_account_data["_value"]
    else:
        account_id = raw_account_data

    # Now we have the raw number (1), we can proceed safely
    content = data.get("content")

    conn = social_db.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO posts (account_id, content) VALUES (?, ?)",
            (account_id, content),
        )
        conn.commit()
        return jsonify({"success": True, "post_id": cursor.lastrowid}), 201
    except Exception as e:
        print(f"DATABASE ERROR: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
