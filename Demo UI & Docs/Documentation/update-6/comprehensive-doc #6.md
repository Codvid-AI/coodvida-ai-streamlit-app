# Comprehensive Server-Client Documentation - Update #6

## Overview

This comprehensive documentation covers the complete Codvid AI Backend system architecture, including all features and updates from version 2 through the latest **Immediate Response Endpoints** and **Task Status Monitoring** system. The system has evolved from a local storage model to a hybrid local/cloud architecture with MongoDB backend, JWT authentication, Instagram profile tracking, Instagram reel tracking, and now **real-time task monitoring capabilities**.

## Table of Contents

1. [Authentication System](#authentication-system)
2. [Core Architecture](#core-architecture)
3. [Project Management](#project-management)
4. [AI Endpoints](#ai-endpoints)
5. [Instagram Profile Tracking](#instagram-profile-tracking)
6. [Instagram Reel Tracking](#instagram-reel-tracking)
7. [Task Status Monitoring](#task-status-monitoring)
8. [Client Integration](#client-integration)
9. [Error Handling](#error-handling)
10. [Migration Guide](#migration-guide)

---

## What's New in Update #6

### 🚀 **Immediate Response Endpoints**
- **Profile Force Scrape**: Now returns immediate response before processing
- **Reel Force Scrape**: Now returns immediate response before processing
- **Background Processing**: All scraping operations run in background threads
- **Non-blocking API**: Users get instant feedback while processing continues

### 📊 **Task Status Monitoring**
- **Real-time Status**: Monitor task processing in real-time
- **Event Streaming**: Track scraping progress through event logs
- **Processing Registry**: Centralized task state management
- **Status Endpoints**: Dedicated endpoints for monitoring task progress

---

## Authentication System

All protected endpoints require JWT authentication. The authentication system uses JSON Web Tokens (JWT) for secure communication.

### Public vs Protected Endpoints

**Public Endpoints (No Authentication Required):**
- `GET/POST /codvid-ai/ping` - Health check
- `POST /codvid-ai/auth/signup` - User registration
- `POST /codvid-ai/auth/login` - User authentication
- `GET /codvid-ai/auth/get_uuid` - Get user UUID

**Protected Endpoints (Authentication Required):**
- All `/codvid-ai/ai/*` endpoints
- All `/codvid-ai/project/*` endpoints
- All `/codvid-ai/user/*` endpoints
- All `/codvid-ai/ig-tracking/*` endpoints

### Authentication Flow
1. **Sign Up**: A new user registers with an email and password. The server creates an account and returns a JWT.
2. **Log In**: An existing user logs in with their credentials. The server verifies the credentials and returns a JWT.
3. **Authenticated Requests**: For subsequent requests to protected endpoints, the client must include the received JWT in the `Authorization` header.

---

## Instagram Profile Tracking

The Instagram Profile Tracking service monitors Instagram profiles and analyzes their content for insights and competitive analysis.

### Key Features
- **Profile Monitoring**: Track specific Instagram profiles automatically
- **Content Analysis**: Analyze posts, reels, and engagement metrics
- **Competitor Analysis**: Monitor competitor profiles and content strategies
- **Scheduled Scraping**: Automatic updates at configurable intervals
- **Real-time Processing**: Immediate response with background processing

### API Endpoints

#### 1. **Create Profile Tracking Task**
**Endpoint:** `POST /codvid-ai/ig-tracking/create_task`

**Request:**
```json
{
  "schema_version": "4.0",
  "data": {
    "target_profile": "instagram_username",
    "is_competitor": false,
    "scrape_interval_days": 2
  }
}
```

**Response:**
```json
{
  "result": true,
  "response": {
    "task_id": "uuid-string",
    "message": "Instagram tracking task created successfully"
  }
}
```

#### 2. **Get User Tasks**
**Endpoint:** `GET /codvid-ai/ig-tracking/get_tasks`

**Response:**
```json
{
  "result": true,
  "response": {
    "tasks": [
      {
        "_id": "task-uuid",
        "target_profile": "instagram_username",
        "is_competitor": false,
        "status": "active",
        "created_at": 1754654044,
        "last_scraped": 1754654979,
        "next_scrape_due": 1754827779,
        "scrape_interval_days": 2
      }
    ]
  }
}
```

#### 3. **Force Scrape Profile Task** ⭐ **UPDATED**
**Endpoint:** `POST /codvid-ai/ig-tracking/force_scrape/<task_id>`

**Description:** Forces immediate scraping of a profile tracking task with **immediate response** and background processing.

**Response (Immediate):**
```json
{
  "result": true,
  "message": "Task scraping initiated successfully",
  "task_id": "task-uuid",
  "status": "processing"
}
```

**Key Changes:**
- **Before**: Endpoint waited for scraping to complete (could take 30+ seconds)
- **After**: Returns immediate response and processes scraping in background
- **Background Thread**: Uses daemon threads for non-blocking operation
- **Processing Registry**: Tracks task status for monitoring

**Client Usage:**
```python
# Initiate scraping
response = force_scrape_task(task_id)
if response:
    print("✅ Scraping initiated! Monitor progress with task status endpoint.")
    
    # Monitor progress
    while True:
        status = get_task_status(task_id)
        if not status.get("is_processing"):
            break
        time.sleep(2)  # Check every 2 seconds
```

#### 4. **Get Task Details**
**Endpoint:** `GET /codvid-ai/ig-tracking/get_task/<task_id>`

**Response:**
```json
{
  "result": true,
  "response": {
    "target_profile": "instagram_username",
    "is_competitor": false,
    "status": "active",
    "target_profile_data": {
      "username": "instagram_username",
      "followers": 15000,
      "posts_count": 450,
      "scraped_posts": [...],
      "icon_pic_url": "https://...",
      "biography": "Profile bio...",
      "follows_count": 1200,
      "igtv_video_count": 25
    }
  }
}
```

#### 5. **Update Task**
**Endpoint:** `PUT /codvid-ai/ig-tracking/update_task/<task_id>`

**Request:**
```json
{
  "schema_version": "4.0",
  "data": {
    "is_competitor": true,
    "status": "active"
  }
}
```

#### 6. **Delete Task**
**Endpoint:** `DELETE /codvid-ai/ig-tracking/delete_task/<task_id>`

#### 7. **Update Scrape Interval**
**Endpoint:** `PUT /codvid-ai/ig-tracking/update_scrape_interval/<task_id>`

**Request:**
```json
{
  "schema_version": "4.0",
  "data": {
    "scrape_interval_days": 3
  }
}
```

---

## Instagram Reel Tracking

The Instagram Reel Tracking service monitors individual Instagram reels within projects, providing granular insights into specific video performance.

### Key Features
- **Project-Based Organization**: Each reel tracking task belongs to a specific project
- **Individual Reel Monitoring**: Track specific Instagram reel URLs
- **Performance Metrics**: Monitor likes, comments, views, and engagement
- **AI-Powered Sentiment Analysis**: Analyze comment sentiment automatically
- **Background Processing**: Immediate response with background scraping

### API Endpoints

#### 1. **Create Reel Tracking Task**
**Endpoint:** `POST /codvid-ai/ig-tracking/create_reel_task`

**Request:**
```json
{
  "schema_version": "4.0",
  "data": {
    "project_name": "your_project_name",
    "reel_url": "https://www.instagram.com/reels/REEL_ID/",
    "scrape_interval_days": 2
  }
}
```

#### 2. **Get Project Reel Tasks**
**Endpoint:** `POST /codvid-ai/ig-tracking/get_project_reel_tasks`

**Request:**
```json
{
  "schema_version": "4.0",
  "data": {
    "project_name": "your_project_name"
  }
}
```

#### 3. **Force Scrape Reel Task** ⭐ **UPDATED**
**Endpoint:** `POST /codvid-ai/ig-tracking/force_scrape_reel/<task_id>`

**Description:** Forces immediate scraping of a reel tracking task with **immediate response** and background processing.

**Response (Immediate):**
```json
{
  "result": true,
  "message": "Reel tracking task scraping initiated successfully",
  "task_id": "task-uuid",
  "status": "processing"
}
```

**Key Changes:**
- **Before**: Endpoint waited for scraping to complete
- **After**: Returns immediate response and processes scraping in background
- **Background Thread**: Uses daemon threads for non-blocking operation
- **Processing Registry**: Tracks task status for monitoring

#### 4. **Delete Reel Tracking Task**
**Endpoint:** `DELETE /codvid-ai/ig-tracking/delete_reel_task/<task_id>`

---

## Task Status Monitoring ⭐ **NEW FEATURE**

The Task Status Monitoring system provides real-time visibility into the progress of Instagram tracking tasks, allowing clients to monitor scraping operations without blocking the main application flow.

### Key Features
- **Real-time Status Updates**: Monitor task processing in real-time
- **Event Logging**: Track detailed progress through event logs
- **Processing Registry**: Centralized task state management
- **Non-blocking Monitoring**: Check status without affecting performance
- **Background Processing**: All scraping operations run in background threads

### How It Works

1. **Task Initiation**: Client calls force scrape endpoint
2. **Immediate Response**: Server returns success response immediately
3. **Background Processing**: Scraping runs in background thread
4. **Status Monitoring**: Client can poll status endpoint for progress
5. **Event Streaming**: Real-time updates through processing registry
6. **Completion Notification**: Status endpoint shows when processing is done

### API Endpoints

#### 1. **Get Task Status** ⭐ **NEW**
**Endpoint:** `GET /codvid-ai/ig-tracking/task_status/<task_id>`

**Description:** Get current processing status and latest event for a task. Returns processing data only if the task is currently being processed.

**Response - Not Processing:**
```json
{
  "result": true,
  "response": {
    "task_id": "task-uuid",
    "is_processing": false,
    "latest_event": null
  }
}
```

**Response - Currently Processing:**
```json
{
  "result": true,
  "response": {
    "task_id": "task-uuid",
    "is_processing": true,
    "status": "processing",
    "started_at": 1754654044,
    "updated_at": 1754654979,
    "logs_count": 5,
    "latest_event": {
      "timestamp": 1754654979,
      "event_type": "profile_data_updated",
      "scraped_posts_count": 12
    }
  }
}
```

**Event Types:**
- `scrape_started`: Scraping process initiated
- `account_fetched`: Instagram account data retrieved
- `reels_filtered`: Reels filtered from posts
- `processing_reels`: Reel processing started
- `reels_processed`: Reel processing completed
- `profile_data_updated`: Profile data updated in database

**Client Usage Example:**
```python
def monitor_task_progress(task_id):
    """Monitor task progress until completion"""
    print(f"🔄 Monitoring task {task_id}...")
    
    while True:
        status = get_task_status(task_id)
        
        if not status.get("is_processing"):
            print("✅ Task completed!")
            break
            
        latest_event = status.get("latest_event")
        if latest_event:
            event_type = latest_event.get("event_type")
            print(f"📊 Progress: {event_type}")
            
        time.sleep(2)  # Check every 2 seconds

# Usage
task_id = "your-task-uuid"
force_scrape_task(task_id)  # Gets immediate response
monitor_task_progress(task_id)  # Monitor until completion
```

### 2. **Sentiment Analysis Summary**
**Endpoint:** `GET /codvid-ai/ig-tracking/sentiment_summary/<task_id>`

**Response:**
```json
{
  "result": true,
  "response": {
    "sentiment_summary": {
      "total_comments": 45,
      "sentiment_distribution": {
        "positive": 28,
        "negative": 5,
        "neutral": 12
      },
      "sentiment_percentages": {
        "positive": 62.2,
        "negative": 11.1,
        "neutral": 26.7
      },
      "overall_sentiment": "positive"
    }
  }
}
```

---

## Client Integration

### Authentication Setup
```python
import requests

class CodvidAIClient:
    def __init__(self, base_url, email, password):
        self.base_url = base_url
        self.session_token = self._authenticate(email, password)
    
    def _authenticate(self, email, password):
        response = requests.post(f"{self.base_url}/codvid-ai/auth/login", json={
            "schema_version": "4.0",
            "data": {
                "auth_type": "email",
                "email": email,
                "password": password
            }
        })
        
        if response.status_code == 201:
            return response.json()["token"]
        else:
            raise Exception("Authentication failed")
    
    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.session_token}",
            "Content-Type": "application/json"
        }
```

### Profile Tracking Workflow
```python
# 1. Create tracking task
task_id = create_tracking_task("instagram_username", is_competitor=False)

# 2. Force scrape with immediate response
success = force_scrape_task(task_id)
if success:
    print("✅ Scraping initiated! Monitoring progress...")
    
    # 3. Monitor progress
    while True:
        status = get_task_status(task_id)
        if not status.get("is_processing"):
            break
        time.sleep(2)
    
    # 4. Get results
    task_details = get_task_details(task_id)
    print(f"📊 Scraped {len(task_details['target_profile_data']['scraped_posts'])} posts")
```

### Reel Tracking Workflow
```python
# 1. Create reel tracking task
task_id = create_reel_tracking_task("project_name", "https://instagram.com/reels/...")

# 2. Force scrape with immediate response
success = force_scrape_reel_task(task_id)
if success:
    print("✅ Reel scraping initiated! Monitoring progress...")
    
    # 3. Monitor progress
    while True:
        status = get_task_status(task_id)
        if not status.get("is_processing"):
            break
        time.sleep(2)
    
    # 4. Get results
    project_tasks = get_project_reel_tasks("project_name")
    print(f"📊 Reel tracking updated")
```

---

## Error Handling

### Common Error Responses

#### Authentication Errors (401)
```json
{
  "result": false,
  "message": "Unauthorized: invalid or expired token"
}
```

#### Validation Errors (400)
```json
{
  "result": false,
  "message": "Missing required field: target_profile"
}
```

#### Not Found Errors (404)
```json
{
  "result": false,
  "message": "Task not found or access denied"
}
```

#### Conflict Errors (409)
```json
{
  "result": false,
  "message": "Task is already being processed"
}
```

#### Server Errors (500)
```json
{
  "result": false,
  "message": "Error initiating task scraping: Connection timeout"
}
```

### Error Handling Best Practices

1. **Always Check Response Status**: Verify `result` field before processing
2. **Handle Authentication Errors**: Implement token refresh logic
3. **Validate Input Data**: Check required fields before sending requests
4. **Implement Retry Logic**: For transient errors like network timeouts
5. **Monitor Task Status**: Use status endpoints to track long-running operations

---

## Migration Guide

### From Update #5 to Update #6

#### Breaking Changes
- **None**: All existing endpoints maintain backward compatibility

#### New Features
- **Immediate Response**: Force scrape endpoints now return immediately
- **Task Status Monitoring**: New endpoint for monitoring task progress
- **Background Processing**: All scraping operations run in background

#### Client Updates Required
- **Optional**: Update client code to use new status monitoring
- **Recommended**: Implement progress tracking for better user experience
- **Backward Compatible**: Existing code continues to work unchanged

#### Migration Steps
1. **No Code Changes Required**: Existing implementations continue to work
2. **Optional Enhancement**: Add status monitoring for better UX
3. **Test New Features**: Verify immediate response behavior
4. **Update Documentation**: Reference new endpoint capabilities

---

## Performance Improvements

### Update #6 Performance Enhancements

#### 1. **Non-blocking API Responses**
- **Before**: Force scrape endpoints blocked for 30+ seconds
- **After**: Immediate response (< 100ms) with background processing
- **Improvement**: 300x faster API response time

#### 2. **Background Threading**
- **Daemon Threads**: Non-blocking background processing
- **Processing Registry**: Centralized state management
- **Error Handling**: Robust error handling in background operations

#### 3. **Real-time Monitoring**
- **Status Endpoints**: Real-time task progress tracking
- **Event Logging**: Detailed progress information
- **Non-blocking Queries**: Status checks without performance impact

---

## System Requirements

### Server Requirements
- **Python**: 3.8+
- **MongoDB**: 4.4+
- **Memory**: 2GB+ RAM recommended
- **Storage**: 10GB+ available space
- **Network**: Stable internet connection for Instagram scraping

### Client Requirements
- **Python**: 3.8+
- **Dependencies**: requests, json, time
- **Network**: Stable internet connection
- **Authentication**: Valid JWT token

---

## Troubleshooting

### Common Issues

#### 1. **Task Already Processing Error**
```json
{
  "result": false,
  "message": "Task is already being processed"
}
```
**Solution**: Wait for current processing to complete or check task status

#### 2. **Authentication Token Expired**
```json
{
  "result": false,
  "message": "Unauthorized: invalid or expired token"
}
```
**Solution**: Re-authenticate and get new token

#### 3. **Task Not Found**
```json
{
  "result": false,
  "message": "Task not found or access denied"
}
```
**Solution**: Verify task ID and user permissions

#### 4. **Scraping Timeout**
**Solution**: Check Instagram accessibility and network connectivity

### Debug Information

#### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Check Task Status
```python
status = get_task_status(task_id)
print(f"Task Status: {status}")
```

#### Monitor Processing Registry
```python
# Check if task is in processing state
if processing_registry.is_processing(task_id):
    print("Task is currently being processed")
```

---

## Conclusion

Update #6 introduces significant improvements to the Codvid AI Backend system:

1. **Immediate Response Endpoints**: Force scrape operations now return instantly
2. **Background Processing**: All scraping runs in non-blocking background threads
3. **Task Status Monitoring**: Real-time progress tracking for better user experience
4. **Performance Improvements**: 300x faster API response times
5. **Backward Compatibility**: All existing functionality continues to work

These enhancements provide a more responsive and user-friendly experience while maintaining the robust functionality of the Instagram tracking system. The new architecture allows clients to initiate operations quickly and monitor progress in real-time, making the system more suitable for production environments and user-facing applications.

For questions or support, refer to the comprehensive API documentation and client integration examples provided in this document.
