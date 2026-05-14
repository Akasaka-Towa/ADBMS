import os
from flask import Flask
from config import Config
from models import db, login_manager
from mongodb.logger import MongoLogger
from routes import auth_bp, dashboard_bp, files_bp, admin_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_MAIN"], exist_ok=True)
    os.makedirs(app.config["UPLOAD_BACKUP"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    app.mongo_logger = MongoLogger(app.config["MONGO_URI"], app.config["MONGO_DB_NAME"])

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {"now": datetime.utcnow()}

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
