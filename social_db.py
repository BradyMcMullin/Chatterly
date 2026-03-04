import sqlite3


def get_db_connection():
    conn = sqlite3.conect("network.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_user(email, username, first_name="", last_name=""):
    # creates a user and returns their new id.
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, username, first_name, last_name) VALUES (?,?,?,?)",
            (email, username, first_name, last_name),
        )
        conn.commit()
        return {"success": True, "user_id": cursor.lastrowid}
    except sqlite3.IntegrityError:
        return {"success": False, "error": "Email or Username already exists"}
    finally:
        conn.close()


def get_feed(account_id):
    # get te most recent post from followed accounts
    conn = get_db_connection()
    query = """
        SELECT p.*, a.user_id
        FROM posts p
        JOIN followers f ON p.account_id = f.followed_id
        JOIN accounts a ON p.account_id = a.account_id
        WHERE f.follower_id = ?
        ORDER BY p.created_at DESC
        LIMIT 50;
    """
    posts = conn.execute(query, (account_id,)).fetchall()
    conn.close()
    return [dict(post) for post in posts]
