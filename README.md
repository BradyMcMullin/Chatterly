# Chatterly 🗣️

**A Data-Centric Social Media Platform**

**Team Members:** Brandon Lewis, Brady McMullin, Dayne Wyler
**Course:** Database Systems  

## 📖 Project Overview

Chatterly is a full-stack social network built to demonstrate complex relational database design and asynchronous team collaboration. The project utilizes a robust SQLite backend with automated triggers, a Python database library (`social_db.py`), a Flask REST API (`app.py`), and a Vue.js frontend UI.

### Core Features Implemented

* **Users & Accounts:** Proper separation between human users and multiple account profiles.
* **Interactions:** Support for Posts, Comments, Likes, and Follows.
* **Automated Data Integrity:** SQLite `TRIGGERS` handle `follower_count`, `following_count`, `like_count`, and `comment_count` dynamically at the database level.
* **Additional Tables:** Includes a `direct_messages` table to support private communication between accounts.

---

## 🚀 Setup & Installation

We have automated the database setup process to ensure the environment can be rebuilt in a single command.

**1. Build the Database:**
Run the following in your terminal to delete the old database, rebuild the schema, and seed the test data:

```bash
chmod +x build.sh
./build.sh
```

*(Windows users can run: `rm -f network.db && sqlite3 network.db < schema.sql`)*

**2. Start the Backend API:**
Ensure you have the dependencies installed (`pip install Flask flask-cors`), then run:

```bash
python app.py
```

**3. Launch the UI:**
Open `index.html` in any modern web browser to interact with the Vue.js frontend.

---

## 🧪 Testing the Database & Queries

Per project requirements, all database operations are encapsulated as Python functions within `social_db.py`.

### Basic Operations

Basic CRUD operations (Creating users, accounts, posts, etc.) can be tested via the Vue.js UI or the Flask API. You can also test the library directly in a Python shell:

```python
import social_db

# Example: Create a new user
social_db.create_user(email="test@test.com", username="tester123")
```

### 🧠 "Interesting" Queries

We implemented two advanced queries that demonstrate complex relational logic:

**1. The "Catch Up" Feed**

* **Logic:** Fetches the top 10 posts from the last 7 days platform-wide, ranked by an engagement score (`like_count + comment_count`).
* **Testing:** Accessible via `GET /api/catch-up` or `social_db.get_catch_up_feed()`.

**2. "Best Follows" Analytics**

* **Logic:** Identifies which accounts a specific user interacts with most by joining follows, likes, and comments, then normalizing the result against the followed account's total post count.
* **Testing:** Accessible via `GET /api/accounts/<account_id>/best-follows` or `social_db.get_best_follows(account_id)`.
