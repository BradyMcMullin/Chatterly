import sqlite3
import random
from datetime import datetime, timedelta

# --- MOCK DATA ---
FIRST_NAMES = [
    "Alice",
    "Bob",
    "Charlie",
    "Diana",
    "Ethan",
    "Fiona",
    "George",
    "Hannah",
    "Ian",
    "Julia",
]
LAST_NAMES = [
    "Smith",
    "Johnson",
    "Williams",
    "Brown",
    "Jones",
    "Garcia",
    "Miller",
    "Davis",
    "Rodriguez",
    "Martinez",
]
BIOS = [
    "Computer Science student.",
    "Just here for the memes.",
    "Coffee addict ☕",
    "Coding late into the night.",
    "Living life one bug at a time.",
]
POSTS = [
    "Just finished my database project! Finally!",
    "Does anyone understand how Vue reactivity actually works?",
    "I'm going to need a lot more coffee today.",
    "SQLite is honestly so underrated.",
    "Just deployed my first Flask app!",
    "Who wants to form a study group for finals?",
    "If my code compiles on the first try, I assume I did something wrong.",
    "Data-centric projects are the best projects.",
]
COMMENTS = [
    "Congratulations!",
    "Same here.",
    "I completely agree.",
    "Let me know if you figure it out.",
    "Mood.",
    "This is so true.",
    "Good luck!",
    "You've got this!",
]


def seed_database():
    print("🌱 Starting database seed...")
    conn = sqlite3.connect("network.db")
    cursor = conn.cursor()

    # 1. Generate Users & Accounts
    account_ids = []
    for i in range(25):  # Bumped up to 25 to ensure a good list of ghosts
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        username = f"{fn.lower()}_{ln.lower()}_{random.randint(100, 9999)}"
        email = f"{username}@example.com"

        try:
            cursor.execute(
                "INSERT INTO users (email, username, first_name, last_name) VALUES (?, ?, ?, ?)",
                (email, username, fn, ln),
            )
            user_id = cursor.lastrowid

            handle = f"{fn.lower()}{random.randint(10, 99)}"
            cursor.execute(
                "INSERT INTO accounts (user_id, handle) VALUES (?, ?)",
                (user_id, handle),
            )
            account_id = cursor.lastrowid
            account_ids.append(account_id)

            bio = random.choice(BIOS)
            age = random.randint(18, 25)
            cursor.execute(
                "INSERT INTO profile_info (bio, age) VALUES (?, ?)", (bio, age)
            )
            info_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO profiles (account_id, info_id) VALUES (?, ?)",
                (account_id, info_id),
            )
        except sqlite3.IntegrityError:
            continue

    print(f"✅ Created {len(account_ids)} accounts.")

    # --- GHOST FEATURE SETUP ---
    # We will make Account 1 our "Main Target". Everyone follows Account 1.
    target_account = account_ids[0]
    ghost_accounts = account_ids[1:11]  # 10 accounts will be ghosts
    active_accounts = account_ids[11:]  # The rest are active

    # 2. Generate Follows
    for acc_id in account_ids[1:]:
        # Everyone follows the target account so we have a reliable dataset to test
        cursor.execute(
            "INSERT INTO followers (follower_id, followed_id) VALUES (?, ?)",
            (acc_id, target_account),
        )

        # Plus some random follows for network realism
        follows = random.sample(
            [a for a in account_ids if a != acc_id and a != target_account],
            random.randint(1, 4),
        )
        for followed_id in follows:
            try:
                cursor.execute(
                    "INSERT INTO followers (follower_id, followed_id) VALUES (?, ?)",
                    (acc_id, followed_id),
                )
            except sqlite3.IntegrityError:
                pass

    print("✅ Created follow network (Everyone follows Account 1).")

    # 3. Generate Posts (Old vs Recent)
    old_post_ids = []
    recent_post_ids = []

    for _ in range(60):
        acc_id = random.choice(account_ids)
        content = random.choice(POSTS)

        # Flip a coin: Make an old post (> 90 days) or a recent post (< 7 days)
        is_old = random.choice([True, False])

        if is_old:
            days_ago = random.randint(100, 150)  # Definitely older than 90 days
            created_at = (datetime.now() - timedelta(days=days_ago)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            cursor.execute(
                "INSERT INTO posts (account_id, content, created_at) VALUES (?, ?, ?)",
                (acc_id, content, created_at),
            )
            old_post_ids.append(cursor.lastrowid)
        else:
            days_ago = random.randint(0, 6)  # Recent
            created_at = (datetime.now() - timedelta(days=days_ago)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            cursor.execute(
                "INSERT INTO posts (account_id, content, created_at) VALUES (?, ?, ?)",
                (acc_id, content, created_at),
            )
            recent_post_ids.append(cursor.lastrowid)

    print(
        f"✅ Created {len(old_post_ids)} old posts and {len(recent_post_ids)} recent posts."
    )

    # 4. Generate Likes (The critical part for ghosts)
    # Ghosts ONLY like old posts (or nothing at all)
    for ghost in ghost_accounts:
        if random.choice([True, False]):  # 50% chance they haven't liked ANYTHING EVER
            liked_posts = random.sample(old_post_ids, random.randint(1, 3))
            for post_id in liked_posts:
                try:
                    cursor.execute(
                        "INSERT INTO likes (account_id, post_id) VALUES (?, ?)",
                        (ghost, post_id),
                    )
                except sqlite3.IntegrityError:
                    pass

    # Active users like recent posts (preventing them from being ghosts)
    for active in active_accounts:
        liked_posts = random.sample(recent_post_ids, random.randint(3, 8))
        for post_id in liked_posts:
            try:
                cursor.execute(
                    "INSERT INTO likes (account_id, post_id) VALUES (?, ?)",
                    (active, post_id),
                )
            except sqlite3.IntegrityError:
                pass

    # Add some random comments just to flesh things out
    for post_id in recent_post_ids + old_post_ids:
        if random.random() > 0.5:
            commenter_id = random.choice(account_ids)
            content = random.choice(COMMENTS)
            cursor.execute(
                "INSERT INTO comments (account_id, post_id, content) VALUES (?, ?, ?)",
                (commenter_id, post_id, content),
            )

    print("✅ Added targeted likes to create Ghost vs Active users.")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    seed_database()
