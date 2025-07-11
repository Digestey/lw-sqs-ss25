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

ALTER TABLE highscores ADD CONSTRAINT chk_score_nonnegative CHECK (score >= 0);
ALTER TABLE highscores MODIFY COLUMN score BIGINT NOT NULL;

-- Insert a dummy user (to test the highscore functionality)
INSERT IGNORE INTO users (id, username, password_hash)
VALUES (1, 'Tester', 'canttouchthis');

-- Print a message after tables are created to signal it has finished successfully
SELECT 'Tables created successfully!' AS message;