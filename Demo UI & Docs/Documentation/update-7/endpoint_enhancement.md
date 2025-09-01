# Update 7: Enhanced Task Status Endpoint

## Overview
Enhanced the `/task_status/<task_id>` endpoint to return multiple logs instead of just the latest event, allowing better monitoring of task progress.

## Changes Made

### Backend Changes
- **File**: `back_end/api/ig_tracking_routes.py`
- **Endpoint**: `GET /codvid-ai/ig-tracking/task_status/<task_id>`
- **Added**: Query parameter `logs_count` to specify number of logs to return

### New Query Parameters
- `logs_count`: Number of latest logs to return (default: 10, max: 100)

## API Response Format

### Before
```json
{
  "result": true,
  "response": {
    "task_id": "123",
    "is_processing": true,
    "latest_event": {"timestamp": 123, "message": "..."}
  }
}
```

### After
```json
{
  "result": true,
  "response": {
    "task_id": "123",
    "is_processing": true,
    "logs": [
      {"timestamp": 123, "message": "Starting analysis..."},
      {"timestamp": 124, "message": "Fetching data..."},
      {"timestamp": 125, "message": "Processing complete"}
    ],
    "logs_count": 50,
    "requested_logs_count": 3,
    "latest_event": {"timestamp": 125, "message": "Processing complete"}
  }
}
```

## Usage Examples

### Get 5 Latest Logs
```
GET /codvid-ai/ig-tracking/task_status/123?logs_count=5
```

### Get All Logs (up to 100)
```
GET /codvid-ai/ig-tracking/task_status/123?logs_count=100
```

### Default (10 logs)
```
GET /codvid-ai/ig-tracking/task_status/123
```

## Frontend Implementation Notes

- **Backward Compatible**: `latest_event` still available for existing code
- **Log Array**: New `logs` field contains array of log objects
- **Log Counts**: `logs_count` (total available) vs `requested_logs_count` (returned)
- **Real-time Updates**: Use `logs` array to show progress during task processing

## Log Object Structure
```json
{
  "timestamp": 1703123456,
  "message": "Human readable log message"
}
```

## Benefits
- Better task progress visibility
- Configurable log depth
- Real-time monitoring capabilities
- Consistent with both profile and reel tracking tasks
