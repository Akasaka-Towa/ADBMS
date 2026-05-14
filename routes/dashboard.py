from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from models.file import StoredFile, FileShare
from models.user import User

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def home():
    files = StoredFile.query.filter_by(owner_id=current_user.id, is_deleted=False).all()
    usage = sum(f.size_bytes for f in files)
    total_downloads = sum(f.total_downloads for f in files)
    shared_count = FileShare.query.join(StoredFile, FileShare.file_id == StoredFile.id).filter(StoredFile.owner_id == current_user.id).count()
    active_users = User.query.filter_by(is_active_user=True).count()
    recent_logs = current_app.mongo_logger.recent(10)
    return render_template("dashboard.html", files=files, usage=usage, total_downloads=total_downloads, shared_count=shared_count, active_users=active_users, recent_logs=recent_logs)
