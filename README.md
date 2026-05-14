# Advanced Cloud File Storage and Sharing System using Hybrid Database Architecture

## Overview
Production-style Flask project demonstrating ADBMS concepts with **MySQL + MongoDB** hybrid architecture, replication simulation (`uploads/main` + `uploads/backup`), RBAC, audit logging, version control, and recovery workflows.

## Features
- Authentication: register/login/logout, hashed passwords, forgot/reset password token flow.
- Real RBAC: `Admin`, `User`, `Guest` with route-level role guards.
- File lifecycle: upload/download/rename/share/delete/restore.
- Versioning + checksum trail per upload revision.
- Soft delete trash and restore.
- MongoDB activity logs wired into login, failed login, upload, download, share, delete, restore, reset-password.
- Admin analytics dashboard with activity aggregation and recent logs.
- Hybrid database split: MySQL for normalized data; MongoDB for logs analytics.

## Setup
1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. Configure env vars:
   - `MYSQL_URI=mysql+pymysql://root:password@localhost:3306/advanced_cloud_storage`
   - `MONGO_URI=mongodb://localhost:27017`
   - `MONGO_DB_NAME=adbms_logs`
   - `SECRET_KEY=change-me`
4. `mysql -u root -p < database/schema.sql`
5. `python app.py`

## Demo Credentials
- Admin email seeded: `admin@cloud.local` (set a valid hash first)
- Users: self-register at `/register`

## Architecture
- Browser UI (Bootstrap 5) -> Flask Blueprints -> MySQL (core entities) + MongoDB (audit/analytics)
- File replication simulation writes each uploaded object to:
  - `uploads/main`
  - `uploads/backup`

## ER Diagram (Text)
- `users` 1---N `files`
- `files` 1---N `file_versions`
- `files` 1---N `file_shares` N---1 `users`
- `users` 1---N `password_reset_tokens`
