# Chatterly 🗣️

**A Data-Centric Social Media Platform**

**Team Members:** Brandon Lewis, Brady McMullin, Dayne Wyler  
**Course:** Database Systems  

## 📖 Project Overview

Chatterly is a full-stack social network built to demonstrate complex relational database design, secure data access, and asynchronous team collaboration. The project utilizes a robust SQLite backend with automated triggers, a Python database access layer (`social_db.py`), a Flask REST API (`app.py`), and a frontend UI built with Vue.js.

### Core Features Implemented

* **Users & Accounts:** Proper 1-to-Many separation between human users and multiple account handles.
* **Profiles:** 1-to-1 relationship mapping accounts to their specific biography and age data.
* **Interactions:** Full CRUD support for Posts, Comments, Likes, Follows, and Blocks.
* **Automated Data Integrity:** SQLite `TRIGGERS` handle aggregate counts dynamically at the database level.
* **Security & Performance:** 100% parameterized queries to prevent SQL Injection.

---

## 🚀 Setup & Installation

We have automated the database setup process to ensure the environment can be rebuilt and populated with highly realistic test data in a single command.

**1. Build and Seed the Database:**
Run the following in your terminal to delete the old database, rebuild the schema, and run our Python seeder (`seed_db.py`) to generate realistic users, posts, and ghost accounts:

```bash
chmod +x build.sh
./build.sh
```
*(Windows users: You can run `bash build.sh` if using Git Bash, or manually delete `network.db`, run `sqlite3 network.db < schema.sql`, and then `python seed_db.py`)*

**2. Start the Backend API (Flask):**
Ensure you have your virtual environment activated and dependencies installed (`Flask`, `flask-cors`), then start the server. It will run on port 5000:

```bash
pip install -r requirements.txt
python app.py
```

**3. Launch the Frontend UI:**
Since the frontend consists of static files, simply open `index.html` directly in any modern web browser to interact with the platform.

---

## 🧪 Testing the Database & Queries

Per project requirements, all database operations are encapsulated as distinct Python functions within `social_db.py`.

### Basic Operations

Basic CRUD operations (Creating users, creating accounts, posting, deleting comments with permission checks, etc.) can be tested directly via the Vue.js UI or the Flask API endpoints. 

### 🧠 "Interesting" Queries

To fulfill the complex query requirements, we implemented advanced data-retrieval features that demonstrate complex relational logic, aggregation, and time-based filtering:

**1. "Ghost Followers" Analytics**
* **Logic:** Identifies "bot" or inactive accounts. It joins `followers`, `accounts`, `users`, `likes`, and `posts`, grouping by user to find accounts that follow a specific target but have either *never* liked a post, or haven't liked a post in over 90 days. 
* **Testing:** Accessible via `GET /api/ghosts/<account_id>` or `social_db.get_ghost_followers(account_id)`. *(Tip: In our seeder data, Account #1 is intentionally followed by 10 ghost accounts).*

**2. The "Catch Up" Feed**
* **Logic:** Fetches the top 10 posts from the last 7 days platform-wide, ranked dynamically by an engagement score (`like_count + comment_count`), rather than just chronological order.
* **Testing:** Accessible via `GET /api/catch-up` or `social_db.get_catch_up_feed()`.

**3. "Best Follows" Analytics**
* **Logic:** Identifies which accounts a specific user interacts with most by joining follows, likes, and comments, then normalizing the result against the followed account's total post count to find the highest engagement rate.
* **Testing:** Accessible via `GET /api/accounts/<account_id>/best-follows` or `social_db.get_best_follows(account_id)`.
