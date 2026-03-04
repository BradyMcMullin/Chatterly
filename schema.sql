PRAGMA foreign_keys = ON; --For whatever reason, sqlite needs this explicitly told

CREATE TABLE users(
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  username TEXT NOT NULL UNIQUE,
  first_name TEXT,
  last_name TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP --default will set the timestamp automatically :)
);

CREATE TABLE accounts(
  account_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  follower_count INTEGER DEFAULT 0,
  following_count INTEGER DEFAULT 0,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE -- delete cascade will remove any rows with account_id when account is deleted!
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
  comment_content TEXT NOT NULL,
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

-- 1. Create Users
INSERT INTO users (email, username, first_name, last_name) VALUES 
('alice@example.com', 'alice_wonder', 'Alice', 'Smith'),
('bob@example.com', 'builder_bob', 'Bob', 'Jones'),
('charlie@example.com', 'chuck_norris', 'Charlie', 'Brown');

-- 2. Create Accounts (Linking to the users we just made)
INSERT INTO accounts (user_id) VALUES 
(1), -- Account 1 belongs to Alice
(2), -- Account 2 belongs to Bob
(3); -- Account 3 belongs to Charlie

-- 3. Create Followers 
-- (Because of your triggers, this will auto-update follower/following counts in accounts!)
INSERT INTO followers (follower_id, followed_id) VALUES 
(1, 2), -- Alice follows Bob
(1, 3), -- Alice follows Charlie
(2, 1); -- Bob follows Alice

-- 3. Create Blocks
-- (Because of your triggers, this will auto-update follower/following counts in accounts!)
INSERT INTO blocks (blocker_id, blocked_id) VALUES
(1, 2); -- Alice blocked Bob

-- 4. Create Posts
INSERT INTO posts (account_id, content) VALUES 
(1, 'Hello world! This is my first post on this awesome new network.'),
(2, 'Can anyone recommend a good database tutorial?'),
(3, 'Just set up my new Flask backend. Feeling good!');

-- 5. Create Likes
-- (Because of your triggers, this will auto-update the like_count in posts!)
INSERT INTO likes (post_id, account_id) VALUES 
(1, 2), -- Bob likes Alice's post
(1, 3), -- Charlie likes Alice's post
(2, 1); -- Alice likes Bob's post

-- 6. Create Comments
-- (Because of your triggers, this will auto-update the comment_count in posts!)
INSERT INTO comments (post_id, account_id, comment_content) VALUES 
(1, 2, 'Welcome to the platform, Alice!'),
(2, 3, 'Check out the SQLite documentation, it is great.');
