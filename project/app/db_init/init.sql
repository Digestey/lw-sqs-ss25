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

-- Print a message after tables are created
SELECT 'Tables created successfully!' AS message;