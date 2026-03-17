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
    user_ids = []
    account_ids = []

    for i in range(15):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        username = f"{fn.lower()}_{ln.lower()}_{random.randint(100, 999)}"
        email = f"{username}@example.com"

        try:
            # Insert User
            cursor.execute(
                "INSERT INTO users (email, username, first_name, last_name) VALUES (?, ?, ?, ?)",
                (email, username, fn, ln),
            )
            user_id = cursor.lastrowid
            user_ids.append(user_id)

            # Insert Account for User
            handle = f"{fn.lower()}{random.randint(10, 99)}"
            cursor.execute(
                "INSERT INTO accounts (user_id, handle) VALUES (?, ?)",
                (user_id, handle),
            )
            account_id = cursor.lastrowid
            account_ids.append(account_id)

            # Insert Profile Info
            bio = random.choice(BIOS)
            age = random.randint(18, 25)
            cursor.execute(
                "INSERT INTO profile_info (bio, age) VALUES (?, ?)", (bio, age)
            )
            info_id = cursor.lastrowid

            # Link Profile
            cursor.execute(
                "INSERT INTO profiles (account_id, info_id) VALUES (?, ?)",
                (account_id, info_id),
            )

        except sqlite3.IntegrityError:
            continue  # Skip if random generation causes a duplicate email/username

    print(f"✅ Created {len(account_ids)} accounts.")

    # 2. Generate Follows
    for acc_id in account_ids:
        # Each account follows 3 to 7 random people
        follows = random.sample(
            [a for a in account_ids if a != acc_id], random.randint(3, 7)
        )
        for followed_id in follows:
            try:
                cursor.execute(
                    "INSERT INTO followers (follower_id, followed_id) VALUES (?, ?)",
                    (acc_id, followed_id),
                )
            except sqlite3.IntegrityError:
                pass

    print("✅ Created follow network.")

    # 3. Generate Posts
    post_ids = []
    for _ in range(40):
        acc_id = random.choice(account_ids)
        content = random.choice(POSTS)

        # Randomize creation time over the last 7 days for the catch-up feed
        random_days_ago = random.randint(0, 6)
        random_hours_ago = random.randint(0, 23)
        created_at = (
            datetime.now() - timedelta(days=random_days_ago, hours=random_hours_ago)
        ).strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            "INSERT INTO posts (account_id, content, created_at) VALUES (?, ?, ?)",
            (acc_id, content, created_at),
        )
        post_ids.append(cursor.lastrowid)

    print(f"✅ Created {len(post_ids)} posts.")

    # 4. Generate Likes and Comments
    for post_id in post_ids:
        # Random Likes
        likers = random.sample(account_ids, random.randint(0, 8))
        for liker_id in likers:
            try:
                cursor.execute(
                    "INSERT INTO likes (account_id, post_id) VALUES (?, ?)",
                    (liker_id, post_id),
                )
            except sqlite3.IntegrityError:
                pass

        # Random Comments
        for _ in range(random.randint(0, 4)):
            commenter_id = random.choice(account_ids)
            content = random.choice(COMMENTS)
            cursor.execute(
                "INSERT INTO comments (account_id, post_id, content) VALUES (?, ?, ?)",
                (commenter_id, post_id, content),
            )

    print("✅ Added likes and comments.")

    conn.commit()
    conn.close()
    print("🎉 Database successfully seeded! You are ready to present.")


if __name__ == "__main__":
    seed_database()
