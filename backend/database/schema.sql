-- Run this in MySQL Workbench / CLI before starting the backend:
--   mysql -u root -p < backend/database/schema.sql

CREATE DATABASE IF NOT EXISTS book_recommender;
USE book_recommender;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    authors VARCHAR(500),
    categories VARCHAR(255),
    average_rating FLOAT DEFAULT 0,
    description TEXT
);

CREATE TABLE IF NOT EXISTS user_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    preferred_genre VARCHAR(255),
    liked_book_title VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Optional: a default guest user so the chatbot works out of the box
INSERT INTO users (username) VALUES ('guest') ON DUPLICATE KEY UPDATE username = username;
