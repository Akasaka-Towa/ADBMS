from flask import current_app


def log_action(username, action, status="success", metadata=None):
    logger = getattr(current_app, "mongo_logger", None)
    if logger:
        logger.log(username=username, action=action, status=status, metadata=metadata or {})
