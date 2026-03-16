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

def create_account(user_id, handle):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Insert the handle into the accounts table
        cursor.execute(
            "INSERT INTO accounts (user_id, handle) VALUES (?, ?)",
            (user_id, handle)
        )
        account_id = cursor.lastrowid

        # Create the associated profile info
        cursor.execute("INSERT INTO profile_info (bio) VALUES (?)", (f"Welcome to @{handle}!",))
        info_id = cursor.lastrowid
        
        conn.execute("INSERT INTO profiles (account_id, info_id) VALUES (?, ?)", (account_id, info_id))
        
        conn.commit()
        return {"success": True, "account_id": account_id}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def get_feed(account_id):
    conn = get_db_connection()
    # 1. Get the posts
    posts_rows = conn.execute("""
        SELECT p.*, a.handle as username 
        FROM posts p 
        JOIN accounts a ON p.account_id = a.account_id 
        ORDER BY p.created_at DESC
    """).fetchall()
    
    posts = [dict(row) for row in posts_rows]

    # 2. Attach comments to EACH post
    for post in posts:
        comment_rows = conn.execute("""
            SELECT c.*, a.handle as username 
            FROM comments c 
            JOIN accounts a ON c.account_id = a.account_id 
            WHERE c.post_id = ? 
            ORDER BY c.created_at ASC
        """, (post['post_id'],)).fetchall()
        
        # This creates the 'comments' key that Vue is looking for
        post['comments'] = [dict(row) for row in comment_rows]

    conn.close()
    return posts
    
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

def get_account_activity(account_id):
    conn = get_db_connection()
    # Use UNION to find posts that are either liked OR commented on
    query = """
        SELECT DISTINCT p.post_id, p.content, p.created_at, a.handle as username
        FROM posts p
        JOIN accounts a ON p.account_id = a.account_id
        WHERE p.post_id IN (
            SELECT post_id FROM likes WHERE account_id = ?
        )
        OR p.post_id IN (
            SELECT post_id FROM comments WHERE account_id = ?
        )
        ORDER BY p.created_at DESC
    """
    activity = conn.execute(query, (account_id, account_id)).fetchall()
    conn.close()
    return [dict(row) for row in activity]

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

def toggle_like(account_id, post_id):
    conn = get_db_connection()
    # Check if like exists
    liked = conn.execute(
        "SELECT 1 FROM likes WHERE account_id = ? AND post_id = ?",
        (account_id, post_id)
    ).fetchone()
    
    if liked:
        conn.execute("DELETE FROM likes WHERE account_id = ? AND post_id = ?", (account_id, post_id))
        status = "unliked"
    else:
        conn.execute("INSERT INTO likes (account_id, post_id) VALUES (?, ?)", (account_id, post_id))
        status = "liked"
    
    conn.commit()
    conn.close()
    return {"success": True, "status": status}

def add_comment(account_id, post_id, content):
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO comments (account_id, post_id, content) VALUES (?, ?, ?)",
            (account_id, post_id, content)
        )
        conn.commit()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()