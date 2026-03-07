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

def get_profile(account_id):
    conn = get_db_connection()
    query = """
        SELECT u.username, u.first_name, u.last_name, pi.bio, pi.age
        FROM accounts a
        JOIN users u ON a.user_id = u.user_id
        LEFT JOIN profiles p ON a.account_id = p.account_id
        LEFT JOIN profile_info pi ON p.info_id = pi.info_id
        WHERE a.account_id = ?
    """
    profile = conn.execute(query, (account_id,)).fetchone()
    conn.close()
    return dict(profile) if profile else None

def update_profile(account_id, bio, age):
    conn = get_db_connection()
    try:
        # 1. Check if a profile link already exists
        res = conn.execute("SELECT info_id FROM profiles WHERE account_id = ?", (account_id,)).fetchone()
        
        if res:
            # 2. Update existing info
            conn.execute("UPDATE profile_info SET bio = ?, age = ? WHERE info_id = ?", (bio, age, res['info_id']))
        else:
            # 3. Create new info entry and link it
            cursor = conn.execute("INSERT INTO profile_info (bio, age) VALUES (?, ?)", (bio, age))
            new_info_id = cursor.lastrowid
            conn.execute("INSERT INTO profiles (account_id, info_id) VALUES (?, ?)", (account_id, new_info_id))
            
        conn.commit()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()