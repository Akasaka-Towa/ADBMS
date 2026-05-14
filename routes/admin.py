from flask import Blueprint, render_template
from flask_login import login_required
from models.user import User
from models.file import StoredFile
from utils.security import role_required
from flask import current_app

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
@login_required
@role_required("Admin")
def panel():
    logs = current_app.mongo_logger.recent(50)
    analytics = current_app.mongo_logger.analytics()
    total_storage = sum(f.size_bytes for f in StoredFile.query.filter_by(is_deleted=False).all())
    return render_template(
        "admin/panel.html",
        users=User.query.order_by(User.created_at.desc()).all(),
        files=StoredFile.query.order_by(StoredFile.created_at.desc()).all(),
        logs=logs,
        analytics=analytics,
        total_storage=total_storage,
    )
