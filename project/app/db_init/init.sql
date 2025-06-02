-- Ensure consistent SQL mode
SET SQL_MODE = 'STRICT_ALL_TABLES,NO_ENGINE_SUBSTITUTION';

-- Abort on errors in scripts
SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, AUTOCOMMIT = 0;
START TRANSACTION;

-- Set default character set to UTF-8 (utf8mb4 supports emojis and full Unicode)
SET NAMES 'utf8mb4' COLLATE 'utf8mb4_unicode_ci';

-- Set safe timezone (important if datetime data is involved)
SET TIME_ZONE = '+00:00';

-- Users table: stores login info
CREATE DATABASE IF NOT EXISTS pokedb;
USE pokedb;


-- Print a message to confirm the script is running
SELECT 'Creating tables and initializing database...' AS message;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Highscores table: stores quiz results
CREATE TABLE IF NOT EXISTS highscores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    score INT NOT NULL,
    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Insert a dummy user (only if not exists)
INSERT IGNORE INTO users (id, username, password_hash)
VALUES (1, 'testuser', 'dummyhash');

-- Insert 10 dummy highscore entries for the test user
INSERT INTO highscores (user_id, score)
VALUES 
(1, 10),
(1, 20),
(1, 15),
(1, 25),
(1, 30),
(1, 5),
(1, 18),
(1, 12),
(1, 22),
(1, 17);

-- Print a message after tables are created
SELECT 'Tables created successfully!' AS message;