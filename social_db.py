import sqlite3


def get_db_connection():
    conn = sqlite3.connect("network.db")
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
    conn = get_db_connection()
    # Updated query to include your own posts
    query = """
        SELECT p.*, u.username
        FROM posts p
        JOIN accounts a ON p.account_id = a.account_id
        JOIN users u ON a.user_id = u.user_id
        LEFT JOIN followers f ON p.account_id = f.followed_id
        WHERE f.follower_id = ? OR p.account_id = ?
        GROUP BY p.post_id
        ORDER BY p.created_at DESC
        LIMIT 50;
    """
    # Note: We pass (account_id,) twice—once for the follower check, once for the self check
    posts = conn.execute(query, (account_id, account_id)).fetchall()
    conn.close()
    return [dict(post) for post in posts]


def get_catch_up_feed(limit=10):
    conn = get_db_connection()
    query = """
	    SELECT p.*, u.username
	    FROM posts p
	    JOIN accounts a ON p.account_id = a.account_id
	    JOIN users u ON a.user_id = u.user_id
	    WHERE p.created_at >= datetime('now', '-7 days')
	    ORDER BY p.like_count DESC, p.comment_count DESC, p.created_at DESC
	    LIMIT ?;
	"""
    posts = conn.execute(query, (limit,)).fetchall()
    conn.close()
    return [dict(post) for post in posts]


def get_ghost_followers(account_id, limit=10):
    conn = get_db_connection()
    query = """
        SELECT a.account_id, u.username, MAX(p.created_at) AS last_like_at
        FROM followers f
        JOIN accounts a ON a.account_id = f.follower_id
        JOIN users u ON u.user_id = a.user_id
        LEFT JOIN likes l ON l.account_id = f.follower_id
        LEFT JOIN posts p ON p.post_id = l.post_id
        WHERE f.followed_id = ?
        GROUP BY a.account_id, u.username
        HAVING last_like_at IS NULL OR last_like_at < datetime('now', '-90 days')
        ORDER BY COALESCE(last_like_at, '1970-01-01') ASC, u.username ASC
        LIMIT ?;
    """
    followers = conn.execute(query, (account_id, limit)).fetchall()
    conn.close()
    return [dict(follower) for follower in followers]
