-- SQL script to create the metadoc_db database
-- Run this in MySQL/MariaDB before running the Flask app

CREATE DATABASE IF NOT EXISTS metadoc_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant privileges to your user (replace 'your_user' and 'your_password' with actual values)
-- GRANT ALL PRIVILEGES ON metadoc_db.* TO 'your_user'@'localhost' IDENTIFIED BY 'your_password';
-- FLUSH PRIVILEGES;

USE metadoc_db;

-- The tables will be created automatically by Flask-SQLAlchemy when you run the app
-- or you can run: python reset_db.py
