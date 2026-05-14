from datetime import datetime, timezone
from pymongo import MongoClient


class MongoLogger:
    def __init__(self, uri, db_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.logs = self.db.activity_logs
        self.logs.create_index([("timestamp", -1)])
        self.logs.create_index([("username", 1), ("action", 1)])

    def log(self, username, action, status="success", metadata=None):
        self.logs.insert_one(
            {
                "username": username,
                "action": action,
                "status": status,
                "metadata": metadata or {},
                "timestamp": datetime.now(timezone.utc),
            }
        )

    def recent(self, limit=20):
        return list(self.logs.find().sort("timestamp", -1).limit(limit))

    def analytics(self):
        pipeline = [{"$group": {"_id": "$action", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}]
        return list(self.logs.aggregate(pipeline))
