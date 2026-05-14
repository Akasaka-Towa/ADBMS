CREATE DATABASE IF NOT EXISTS advanced_cloud_storage;
USE advanced_cloud_storage;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(120) NOT NULL,
  email VARCHAR(120) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('Admin','User','Guest') NOT NULL DEFAULT 'User',
  is_active_user BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE files (
  id INT AUTO_INCREMENT PRIMARY KEY,
  owner_id INT NOT NULL,
  filename VARCHAR(255) NOT NULL,
  original_name VARCHAR(255) NOT NULL,
  extension VARCHAR(20),
  size_bytes BIGINT NOT NULL,
  current_version INT DEFAULT 1,
  total_downloads INT DEFAULT 0,
  lock_owner_id INT NULL,
  lock_timestamp DATETIME NULL,
  is_deleted BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (owner_id) REFERENCES users(id),
  FOREIGN KEY (lock_owner_id) REFERENCES users(id)
);

CREATE TABLE file_versions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  file_id INT NOT NULL,
  version_number INT NOT NULL,
  stored_name VARCHAR(255) NOT NULL,
  checksum VARCHAR(128) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (file_id) REFERENCES files(id)
);

CREATE TABLE file_shares (
  id INT AUTO_INCREMENT PRIMARY KEY,
  file_id INT NOT NULL,
  shared_with_user_id INT NOT NULL,
  can_read BOOLEAN DEFAULT TRUE,
  can_edit BOOLEAN DEFAULT FALSE,
  can_download BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (file_id) REFERENCES files(id),
  FOREIGN KEY (shared_with_user_id) REFERENCES users(id)
);

CREATE TABLE password_reset_tokens (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  token VARCHAR(128) NOT NULL UNIQUE,
  expires_at DATETIME NOT NULL,
  used BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_files_search_name ON files(original_name);
CREATE INDEX idx_files_search_ext ON files(extension);
CREATE INDEX idx_files_search_date ON files(created_at);
CREATE INDEX idx_files_owner ON files(owner_id);
CREATE INDEX idx_users_role ON users(role);

INSERT INTO users(full_name,email,password_hash,role) VALUES
('System Admin','admin@cloud.local','pbkdf2:sha256:260000$demo$hash','Admin');
