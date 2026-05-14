import hashlib
import os
import shutil
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db
from models.file import StoredFile, FileVersion, FileShare
from models.user import User
from utils.audit import log_action

files_bp = Blueprint("files", __name__)


def allowed_file(filename, app):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


def can_access(file):
    if file.owner_id == current_user.id:
        return True
    share = FileShare.query.filter_by(file_id=file.id, shared_with_user_id=current_user.id).first()
    return bool(share and share.can_read)


@files_bp.route("/files")
@login_required
def list_files():
    q = StoredFile.query.filter_by(owner_id=current_user.id)
    if request.args.get("name"):
        q = q.filter(StoredFile.original_name.like(f"%{request.args['name']}%"))
    if request.args.get("ext"):
        q = q.filter_by(extension=request.args["ext"])
    files = q.order_by(StoredFile.created_at.desc()).all()
    users = User.query.filter(User.id != current_user.id).all()
    return render_template("files/list.html", files=files, users=users)


@files_bp.route('/files/upload', methods=['POST'])
@login_required
def upload_file():
    from flask import current_app
    upload = request.files.get('file')
    if not upload or not allowed_file(upload.filename, current_app):
        flash('Invalid file type.', 'danger')
        return redirect(url_for('files.list_files'))
    original = secure_filename(upload.filename)
    ext = original.rsplit('.', 1)[1].lower()
    data = upload.read()
    checksum = hashlib.sha256(data).hexdigest()
    upload.stream.seek(0)

    existing = StoredFile.query.filter_by(owner_id=current_user.id, original_name=original, is_deleted=False).first()
    if existing:
        if existing.lock_owner_id and existing.lock_owner_id != current_user.id:
            flash('File is locked by another user.', 'warning')
            return redirect(url_for('files.list_files'))
        existing.lock_owner_id = current_user.id
        existing.lock_timestamp = datetime.utcnow()
        existing.current_version += 1
        target_file = existing
    else:
        target_file = StoredFile(owner_id=current_user.id, filename=original, original_name=original, extension=ext, size_bytes=len(data))
        db.session.add(target_file)
        db.session.flush()

    stored_name = f"{target_file.id}_v{target_file.current_version}_{original}"
    main_path = os.path.join(current_app.config['UPLOAD_MAIN'], stored_name)
    backup_path = os.path.join(current_app.config['UPLOAD_BACKUP'], stored_name)
    upload.save(main_path)
    shutil.copy2(main_path, backup_path)

    target_file.filename = stored_name
    target_file.size_bytes = len(data)
    target_file.lock_owner_id = None
    target_file.lock_timestamp = None
    db.session.add(FileVersion(file_id=target_file.id, version_number=target_file.current_version, stored_name=stored_name, checksum=checksum))
    db.session.commit()
    log_action(current_user.email, "UPLOAD", metadata={"file": original, "version": target_file.current_version})
    flash('File uploaded with replication and version tracking.', 'success')
    return redirect(url_for('files.list_files'))


@files_bp.route('/files/share/<int:file_id>', methods=['POST'])
@login_required
def share_file(file_id):
    file = StoredFile.query.get_or_404(file_id)
    if file.owner_id != current_user.id:
        return "Forbidden", 403
    share = FileShare(file_id=file_id, shared_with_user_id=int(request.form['user_id']), can_read=True, can_edit='can_edit' in request.form, can_download='can_download' in request.form)
    db.session.add(share)
    db.session.commit()
    log_action(current_user.email, "SHARE", metadata={"file_id": file_id, "target_user": request.form['user_id']})
    return redirect(url_for('files.list_files'))


@files_bp.route('/files/download/<int:file_id>')
@login_required
def download_file(file_id):
    from flask import current_app
    file = StoredFile.query.get_or_404(file_id)
    if not can_access(file):
        return "Forbidden", 403
    path = os.path.join(current_app.config['UPLOAD_MAIN'], file.filename)
    if not os.path.exists(path):
        path = os.path.join(current_app.config['UPLOAD_BACKUP'], file.filename)
    file.total_downloads += 1
    db.session.commit()
    log_action(current_user.email, "DOWNLOAD", metadata={"file_id": file_id})
    return send_file(path, as_attachment=True, download_name=file.original_name)


@files_bp.route('/files/rename/<int:file_id>', methods=['POST'])
@login_required
def rename_file(file_id):
    file = StoredFile.query.get_or_404(file_id)
    if file.owner_id != current_user.id:
        return "Forbidden", 403
    file.original_name = secure_filename(request.form['new_name'])
    db.session.commit()
    log_action(current_user.email, "RENAME", metadata={"file_id": file_id})
    return redirect(url_for('files.list_files'))


@files_bp.route('/files/delete/<int:file_id>', methods=['POST'])
@login_required
def soft_delete(file_id):
    file = StoredFile.query.get_or_404(file_id)
    if file.owner_id != current_user.id:
        return "Forbidden", 403
    file.is_deleted = True
    db.session.commit()
    log_action(current_user.email, "DELETE", metadata={"file_id": file_id})
    return redirect(url_for('files.list_files'))


@files_bp.route('/trash')
@login_required
def trash():
    files = StoredFile.query.filter_by(owner_id=current_user.id, is_deleted=True).all()
    return render_template('files/trash.html', files=files)


@files_bp.route('/files/restore/<int:file_id>', methods=['POST'])
@login_required
def restore(file_id):
    file = StoredFile.query.get_or_404(file_id)
    if file.owner_id != current_user.id:
        return "Forbidden", 403
    file.is_deleted = False
    db.session.commit()
    log_action(current_user.email, "RESTORE", metadata={"file_id": file_id})
    return redirect(url_for('files.trash'))
