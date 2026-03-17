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

CREATE TABLE blocks(
  blocker_id INTEGER NOT NULL,
  blocked_id INTEGER NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (blocker_id, blocked_id),
  FOREIGN KEY (blocker_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
  FOREIGN KEY (blocked_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
  CHECK (blocker_id <> blocked_id)
);

CREATE INDEX idx_blocks_blocker_id ON blocks(blocker_id);
CREATE INDEX idx_blocks_blocked_id ON blocks(blocked_id);

CREATE TRIGGER prevent_follow_when_blocked
BEFORE INSERT ON followers
WHEN EXISTS (
    SELECT 1
    FROM blocks
    WHERE (blocker_id = NEW.follower_id AND blocked_id = NEW.followed_id)
    OR (blocker_id = NEW.followed_id AND blocked_id = NEW.follower_id)
)
BEGIN 
    SELECT RAISE(ABORT, 'cannot follow when blocked');
END;

CREATE TRIGGER remove_follows_on_block
AFTER INSERT ON blocks
BEGIN
    DELETE FROM followers
    WHERE (follower_id = NEW.blocker_id AND followed_id = NEW.blocked_id)
    OR (follower_id = NEW.blocked_id AND followed_id = NEW.blocker_id);
END;

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