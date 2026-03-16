PRAGMA foreign_keys = ON;

-- 1. Base Users Table
CREATE TABLE users(
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  username TEXT NOT NULL UNIQUE,
  first_name TEXT,
  last_name TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Accounts Table (Must be before Profiles and Triggers)
CREATE TABLE accounts(
  account_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  handle TEXT NOT NULL UNIQUE, -- Add this column
  follower_count INTEGER DEFAULT 0,
  following_count INTEGER DEFAULT 0,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 3. Normalized Profile Info Table
CREATE TABLE profile_info (
  info_id INTEGER PRIMARY KEY AUTOINCREMENT,
  bio TEXT DEFAULT '',
  age INTEGER,
  last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 4. Profile Link Table (Links Accounts to Info)
CREATE TABLE profiles (
  profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
  account_id INTEGER NOT NULL UNIQUE,
  info_id INTEGER NOT NULL UNIQUE, -- This enforces the 1:1 relationship
  FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
  FOREIGN KEY (info_id) REFERENCES profile_info(info_id) ON DELETE CASCADE
);

CREATE TABLE followers(
  followed_id INTEGER NOT NULL,
  follower_id INTEGER NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (follower_id, followed_id),
  FOREIGN KEY (follower_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
  FOREIGN KEY (followed_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
  CHECK (follower_id <> followed_id)
);

CREATE TABLE posts(
  post_id INTEGER PRIMARY KEY AUTOINCREMENT,
  account_id INTEGER NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  content TEXT NOT NULL,
  like_count INTEGER DEFAULT 0,
  comment_count INTEGER DEFAULT 0,
  FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
);

CREATE TABLE likes(
  post_id INTEGER NOT NULL,
  account_id INTEGER NOT NULL,
  PRIMARY KEY (post_id, account_id),
  FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
  FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
);

CREATE TABLE comments(
  comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_id INTEGER NOT NULL,
  account_id INTEGER NOT NULL,
  content TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
  FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
);

--I found triggers which we can use for follower, comment and like counts!
--I thought this would be better than using more python code, plus more SQL fun!

CREATE TRIGGER increment_like_count
AFTER INSERT ON likes
BEGIN
  UPDATE posts
  SET like_count = like_count + 1
  WHERE post_id = NEW.post_id;
END;

CREATE TRIGGER decrement_like_count
AFTER DELETE ON likes
BEGIN
  UPDATE posts
  SET like_count = like_count - 1
  WHERE post_id = OLD.post_id;
END;

CREATE TRIGGER increment_comment_count
AFTER INSERT ON comments
BEGIN 
  UPDATE posts
  SET comment_count = comment_count + 1
  WHERE post_id = NEW.post_id;
END;

CREATE TRIGGER decrement_comment_count
AFTER DELETE ON comments
BEGIN 
  UPDATE posts
  SET comment_count = comment_count - 1
  WHERE post_id = OLD.post_id;
END;

CREATE TRIGGER increment_follower_count
AFTER INSERT ON followers
BEGIN
  UPDATE accounts
  SET follower_count = follower_count + 1
  WHERE account_id = NEW.followed_id;
END;

CREATE TRIGGER decrement_follower_count
AFTER DELETE ON followers
BEGIN
  UPDATE accounts
  SET follower_count = follower_count - 1
  WHERE account_id = OLD.followed_id;
END;

CREATE TRIGGER increment_following_count
AFTER INSERT ON followers
BEGIN 
  UPDATE accounts
  SET following_count = following_count + 1
  WHERE account_id = NEW.follower_id;
END;

CREATE TRIGGER decrement_following_count
AFTER DELETE ON followers
BEGIN
  UPDATE accounts
  SET following_count = following_count - 1
  WHERE account_id = OLD.follower_id;
END;


--Fake data that Gemini made!


-------------------------------------------------
-- SEED DATA (Test Data)
-------------------------------------------------

-- 1. Create 3 Users
INSERT INTO users (user_id, email, username, first_name, last_name) VALUES 
(1, 'alice@example.com', 'alice_wonder', 'Alice', 'Smith'),
(2, 'bob@example.com', 'builder_bob', 'Bob', 'Jones'),
(3, 'charlie@example.com', 'chuck_norris', 'Charlie', 'Brown');

-- 2. Create 4 Accounts (Alice has two: 1 and 4)
INSERT INTO accounts (account_id, user_id, handle) VALUES 
(1, 1, 'alice_main'),
(2, 2, 'bob_builds'),
(3, 3, 'charlie_prime'),
(4, 1, 'alice_business');

-- 3. Create 4 UNIQUE Profile Info rows (One for each account)
INSERT INTO profile_info (info_id, bio, age) VALUES 
(1, 'Personal account of Alice', 25),
(2, 'Bob the Builder official', 30),
(3, 'Charlie’s thoughts', 22),
(4, 'Alice Business Inquiry', 25);

-- 4. Link them 1-to-1 (Ensure no info_id is repeated)
INSERT INTO profiles (account_id, info_id) VALUES 
(1, 1), 
(2, 2), 
(3, 3), 
(4, 4);

-- 5. Create Posts (Ensure account_id exists in the accounts table above)
INSERT INTO posts (account_id, content) VALUES 
(1, 'Hello world, this is my first post!'),
(2, 'Can we fix it? Yes we can!'),
(4, 'Open for business inquiries.');

-- 6. Create Comments
-- (Because of your triggers, this will auto-update the comment_count in posts!)
INSERT INTO comments (post_id, account_id, content) VALUES 
(1, 2, 'Welcome to the platform, Alice!'),
(2, 3, 'Check out the SQLite documentation, it is great.');

INSERT INTO profile_info (bio, age) VALUES 
('Adventurer and tea drinker.', 25),
('I like building things with code!', 30);