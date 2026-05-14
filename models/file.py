from . import db


class StoredFile(db.Model):
    __tablename__ = "files"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False, index=True)
    original_name = db.Column(db.String(255), nullable=False)
    extension = db.Column(db.String(20), index=True)
    size_bytes = db.Column(db.BigInteger, nullable=False)
    current_version = db.Column(db.Integer, default=1)
    total_downloads = db.Column(db.Integer, default=0)
    lock_owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    lock_timestamp = db.Column(db.DateTime, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), index=True)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())


class FileVersion(db.Model):
    __tablename__ = "file_versions"
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey("files.id"), nullable=False, index=True)
    version_number = db.Column(db.Integer, nullable=False)
    stored_name = db.Column(db.String(255), nullable=False)
    checksum = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class FileShare(db.Model):
    __tablename__ = "file_shares"
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey("files.id"), nullable=False, index=True)
    shared_with_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    can_read = db.Column(db.Boolean, default=True)
    can_edit = db.Column(db.Boolean, default=False)
    can_download = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
