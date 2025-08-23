# Update #7: Enhanced Task Status Endpoint

**Date**: January 2025  
**Version**: 7.0  
**Type**: API Enhancement  

## Overview

This update significantly enhances the `/task_status/<task_id>` endpoint to provide better visibility into Instagram tracking task processing by returning an array of logs instead of just the latest event, and allowing clients to specify how many logs they want to retrieve.

## What Changed

### Before (Update #6)
- Endpoint returned only `latest_event` 
- Limited visibility into task processing progress
- No control over log quantity

### After (Update #7)
- Endpoint returns `logs` array with configurable count
- Full visibility into processing pipeline
- Client-controlled log retrieval (1-100 logs)
- Backward compatibility maintained

## Technical Details

### Endpoint
```
GET /codvid-ai/ig-tracking/task_status/<task_id>
```

### Query Parameters
- `logs_count` (optional): Number of latest logs to return
  - **Default**: 10
  - **Minimum**: 1
  - **Maximum**: 100
  - **Type**: Integer

### Response Format

#### New Enhanced Response
```json
{
  "result": true,
  "response": {
    "task_id": "task_123",
    "is_processing": true,
    "status": "processing",
    "started_at": 1703123456,
    "updated_at": 1703123457,
    "logs_count": 50,
    "requested_logs_count": 10,
    "logs": [
      {
        "timestamp": 1703123456,
        "message": "Starting Instagram profile analysis"
      },
      {
        "timestamp": 1703123457,
        "message": "Fetching profile data from Instagram API"
      },
      {
        "timestamp": 1703123458,
        "message": "Profile data retrieved: @username with 150 posts"
      }
    ],
    "latest_event": {
      "timestamp": 1703123458,
      "message": "Profile data retrieved: @username with 150 posts"
    }
  }
}
```

#### Backward Compatible Response (when no logs available)
```json
{
  "result": true,
  "response": {
    "task_id": "task_123",
    "is_processing": false,
    "logs": [],
    "logs_count": 0
  }
}
```

### Code Changes

#### Backend (`ig_tracking_routes.py`)
```python
@blueprint.route("/task_status/<task_id>", methods=["GET"])
def get_task_status(task_id):
    """
    Get current processing status and logs for a task.
    Returns processing data only if the task is currently being processed.
    
    Query Parameters:
    - logs_count: Number of latest logs to return (default: 10, max: 100)
    """
    try:
        # Get query parameters
        logs_count = request.args.get('logs_count', 10, type=int)
        
        # Validate logs_count parameter
        if logs_count < 1:
            logs_count = 1
        elif logs_count > 100:
            logs_count = 100

        state = processing_registry.get_state(task_id)
        if state is None:
            return jsonify({
                "result": True,
                "response": {
                    "task_id": task_id,
                    "is_processing": False,
                    "logs": [],
                    "logs_count": 0
                }
            }), 200

        # Get the requested number of latest logs
        if state.logs:
            requested_logs = state.logs[-logs_count:] if logs_count <= len(state.logs) else state.logs
        else:
            requested_logs = []

        return jsonify({
            "result": True,
            "response": {
                "task_id": state.task_id,
                "is_processing": True,
                "status": state.status,
                "started_at": state.started_at,
                "updated_at": state.updated_at,
                "logs_count": len(state.logs),
                "requested_logs_count": len(requested_logs),
                "logs": requested_logs,
                "latest_event": requested_logs[-1] if requested_logs else None,
            }
        }), 200

    except Exception as e:
        return jsonify({
            "result": False,
            "message": f"Error retrieving task status: {str(e)}"
        }), 500
```

## Client Usage Examples

### Get Default Logs (10)
```python
# Basic usage - gets 10 latest logs
response = requests.get(f"/task_status/{task_id}")
```

### Get Specific Number of Logs
```python
# Get 5 latest logs
response = requests.get(f"/task_status/{task_id}?logs_count=5")

# Get all available logs (up to 100)
response = requests.get(f"/task_status/{task_id}?logs_count=100")

# Get just 1 log
response = requests.get(f"/task_status/{task_id}?logs_count=1")
```

### Jupyter Notebook Integration

#### Profile Tracking
```python
def live_poll_task_status(task_id: str, logs_count: int = 10, interval_sec: float = 2.0):
    """Live monitor a profile tracking task until completion"""
    print(f"👀 Live status for profile task: {task_id}")
    print(f"📊 Monitoring {logs_count} latest logs per request")
    
    while True:
        status = get_task_status(task_id, logs_count)
        logs = status["response"]["logs"]
        
        # Show new logs as they appear
        if logs:
            for log in logs:
                timestamp = datetime.fromtimestamp(log["timestamp"]).strftime("%H:%M:%S")
                message = log["message"]
                print(f"   [{timestamp}] {message}")
        
        if not status["response"]["is_processing"]:
            break
        time.sleep(interval_sec)
```

#### Reel Tracking
```python
def live_poll_reel_task_status(task_id: str, logs_count: int = 10, interval_sec: float = 2.0):
    """Live monitor a reel tracking task until completion"""
    print(f"👀 Live status for reel task: {task_id}")
    print(f"📊 Monitoring {logs_count} latest logs per request")
    
    while True:
        status = get_reel_task_status(task_id, logs_count)
        logs = status["response"]["logs"]
        
        # Show new logs as they appear
        if logs:
            for log in logs:
                timestamp = datetime.fromtimestamp(log["timestamp"]).strftime("%H:%M:%S")
                message = log["message"]
                print(f"   [{timestamp}] {message}")
        
        if not status["response"]["is_processing"]:
            break
        time.sleep(interval_sec)
```

## Benefits

### For Developers
- **Better Debugging**: Full visibility into processing pipeline
- **Progress Tracking**: Monitor task progress in real-time
- **Flexible Logging**: Choose appropriate log quantity for use case
- **Performance Control**: Limit log retrieval for high-frequency monitoring

### For Users
- **Real-time Updates**: See exactly what's happening during processing
- **Better UX**: Understand task progress and estimated completion time
- **Error Visibility**: See where and why tasks might fail
- **Customizable Monitoring**: Choose level of detail needed

### For System Administrators
- **Monitoring**: Better visibility into system performance
- **Troubleshooting**: Easier to diagnose issues
- **Resource Management**: Understand processing bottlenecks

## Migration Guide

### Existing Clients
- **No changes required** - backward compatibility maintained
- `latest_event` field still available
- Existing code will continue to work

### Enhanced Clients
- Add `logs_count` query parameter for better control
- Use `logs` array instead of `latest_event` for full visibility
- Implement real-time progress monitoring

### Example Migration
```python
# Old way (still works)
status = get_task_status(task_id)
latest = status["response"]["latest_event"]

# New enhanced way
status = get_task_status(task_id, logs_count=20)
all_logs = status["response"]["logs"]
log_count = status["response"]["logs_count"]
```

## Testing

### Test Cases
1. **Default Behavior**: `GET /task_status/123` → returns 10 logs
2. **Custom Count**: `GET /task_status/123?logs_count=5` → returns 5 logs
3. **Edge Cases**: 
   - `logs_count=0` → defaults to 1
   - `logs_count=999` → caps at 100
   - `logs_count=-5` → defaults to 1
4. **No Logs**: Returns empty logs array when no processing state
5. **Backward Compatibility**: `latest_event` still present

### Test Commands
```bash
# Test default behavior
curl "http://localhost:8080/codvid-ai/ig-tracking/task_status/task_123"

# Test custom log count
curl "http://localhost:8080/codvid-ai/ig-tracking/task_status/task_123?logs_count=5"

# Test edge cases
curl "http://localhost:8080/codvid-ai/ig-tracking/task_status/task_123?logs_count=0"
curl "http://localhost:8080/codvid-ai/ig-tracking/task_status/task_123?logs_count=999"
```

## Future Enhancements

### Potential Improvements
1. **Log Filtering**: Filter logs by event type or timestamp
2. **Pagination**: Support for offset-based pagination
3. **Real-time Streaming**: WebSocket support for live updates
4. **Log Compression**: Compress older logs for storage efficiency
5. **Analytics**: Log analysis and performance metrics

### API Versioning
- Current: v1 (backward compatible)
- Future: v2 with additional features
- Deprecation timeline for v1 features

## Summary

This update significantly improves the Instagram tracking system's observability and monitoring capabilities while maintaining full backward compatibility. Users can now:

- **Monitor progress** in real-time with configurable detail levels
- **Debug issues** more effectively with full log visibility
- **Customize monitoring** based on their specific needs
- **Maintain existing** functionality without code changes

The enhanced endpoint provides a foundation for better user experience and system monitoring, making Instagram tracking tasks more transparent and manageable.
