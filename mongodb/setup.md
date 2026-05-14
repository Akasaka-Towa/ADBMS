# MongoDB Setup

- Database: `adbms_logs`
- Collection: `activity_logs`
- Indexes:
  - `timestamp` descending
  - compound (`username`, `action`)

Sample document:
```json
{
  "username": "admin@cloud.local",
  "action": "UPLOAD",
  "status": "success",
  "metadata": {"file": "report.pdf"},
  "timestamp": "2026-05-14T00:00:00Z"
}
```
