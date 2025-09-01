# Comprehensive Documentation: Instagram Tracking Service

## Overview
Complete documentation covering all updates and features of the Instagram Tracking Service, including profile tracking, reel tracking, and enhanced monitoring capabilities.

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Authentication & User Management](#authentication--user-management)
3. [Profile Tracking](#profile-tracking)
4. [Reel Tracking](#reel-tracking)
5. [Enhanced Task Monitoring](#enhanced-task-monitoring)
6. [AI Chat Endpoints](#ai-chat-endpoints)
7. [API Endpoints Reference](#api-endpoints-reference)
8. [Data Models](#data-models)
9. [Error Handling](#error-handling)
10. [Usage Examples](#usage-examples)

---

## System Architecture

### Core Components
- **IGTrackingService**: Main service for Instagram data processing
- **ProcessingRegistry**: In-memory task state management
- **Task Modules**: Profile and reel tracking implementations
- **Scheduler**: Background processing for scheduled tasks

### Database Structure
- **Users Collection**: User accounts and project data
- **IG Tracking Tasks**: Profile monitoring tasks
- **Project-based Tasks**: Reel tracking within projects

---

## Authentication & User Management

### User Registration & Login
```json
POST /codvid-ai/auth/signup
{
  "schema_version": "4.0",
  "data": {
    "auth_type": "email",
    "email": "user@example.com",
    "password": "password123"
  }
}
```

**Response:**
```json
{
  "result": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

```json
POST /codvid-ai/auth/login
{
  "schema_version": "4.0",
  "data": {
    "auth_type": "email",
    "email": "user@example.com",
    "password": "password123"
  }
}
```

**Response:**
```json
{
  "result": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Project Management
```json
POST /codvid-ai/project/create-project
{
  "schema_version": "4.0",
  "data": {
    "project_name": "my_project"
  }
}
```

**Response:**
```json
{
  "result": true
}
```

---

## Profile Tracking

### Create Profile Tracking Task
```json
POST /codvid-ai/ig-tracking/create_task
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
    "task_id": "463c3473-d439-446c-89f6-f8d4d299fad3",
    "message": "Instagram tracking task created successfully"
  }
}
```

### Update Scrape Interval
```json
PUT /codvid-ai/ig-tracking/update_scrape_interval/{task_id}
{
  "scrape_interval_days": 3
}
```

**Response:**
```json
{
  "result": true,
  "response": {
    "message": "Scrape interval for task 463c3473-d439-446c-89f6-f8d4d299fad3 updated to 3 days."
  }
}
```

### Force Scrape Profile
```json
POST /codvid-ai/ig-tracking/force_scrape/{task_id}
```

**Response:**
```json
{
  "result": true,
  "message": "Task scraping initiated successfully",
  "task_id": "463c3473-d439-446c-89f6-f8d4d299fad3",
  "status": "processing"
}
```

### Get Profile Tasks
```json
GET /codvid-ai/ig-tracking/get_tasks
```

**Response:**
```json
{
  "result": true,
  "response": {
    "tasks": [
      {
        "_id": "463c3473-d439-446c-89f6-f8d4d299fad3",
        "target_profile": "instagram_username",
        "is_competitor": false,
        "status": "active",
        "created_at": 1703123456,
        "last_scraped": 1703123456,
        "next_scrape_due": 1703209856,
        "scrape_interval_days": 2
      }
    ]
  }
}
```

### Get Task Details
```json
GET /codvid-ai/ig-tracking/get_task/{task_id}
```

**Response:**
```json
{
  "result": true,
  "response": {
    "task": {
      "_id": "463c3473-d439-446c-89f6-f8d4d299fad3",
      "target_profile": "instagram_username",
      "is_competitor": false,
      "status": "active",
      "created_at": 1703123456,
      "last_scraped": 1703123456,
      "next_scrape_due": 1703209856,
      "scrape_interval_days": 2,
      "target_profile_data": {
        "scraped_posts": [
          {
            "post_id": "ABC123",
            "caption": "Sample post caption",
            "likes": 150,
            "comments": 25,
            "timestamp": 1703123456
          }
        ],
        "icon_pic_url": "https://example.com/profile.jpg",
        "username": "instagram_username",
        "full_name": "Full Name",
        "biography": "User bio",
        "followers": 1000,
        "following": 500,
        "posts_count": 50,
        "ig_tv_video_count": null
      }
    }
  }
}
```

### Delete Profile Task
```json
DELETE /codvid-ai/ig-tracking/delete_task/{task_id}
```

**Response:**
```json
{
  "result": true,
  "response": {
    "message": "Tracking task deleted successfully"
  }
}
```

### Get Project List
```json
POST /codvid-ai/project/get-project-list
{
  "schema_version": "4.0",
  "data": {}
}
```

**Response:**
```json
{
  "result": true,
  "response": {
    "project_list": ["project1", "project2", "my_project"]
  }
}
```

### Get Project Modification Count
```json
POST /codvid-ai/project/get-project-mod-count
{
  "schema_version": "4.0",
  "data": {
    "project_name": "my_project"
  }
}
```

**Response:**
```json
{
  "result": true,
  "response": {
    "mod_count": 5
  }
}
```

### Delete Project
```json
DELETE /codvid-ai/project/delete-project
{
  "schema_version": "4.0",
  "data": {
    "project_name": "my_project"
  }
}
```

**Response:**
```json
{
  "result": true
}
```

---

## Reel Tracking

### Create Reel Tracking Task
```json
POST /codvid-ai/ig-tracking/create_reel_task
{
  "schema_version": "4.0",
  "data": {
    "project_name": "my_project",
    "reel_url": "https://www.instagram.com/reels/ABC123/",
    "reel_id": "ABC123",
    "scrape_interval_days": 2
  }
}
```

**Response:**
```json
{
  "result": true,
  "response": {
    "task_id": "7a809618-8939-4979-b72f-9b9f4bea137f",
    "message": "Instagram reel tracking task created successfully in project my_project"
  }
}
```

### Get Project Data (Including Reel Tasks)
```json
POST /codvid-ai/project/get-project-data
{
  "schema_version": "4.0",
  "data": {
    "project_name": "my_project"
  }
}
```

**Response:**
```json
{
  "result": true,
  "response": {
    "project_data": {
      "schema_version": "1.0",
      "mod_count": 1,
      "date": "18-7-2025",
      "project_info": {
        "description": "",
        "keywords": []
      },
      "ai_memory": {},
      "chats": [],
      "reel_tracking_tasks": [
        {
          "_id": "7a809618-8939-4979-b72f-9b9f4bea137f",
          "reel_url": "https://www.instagram.com/reels/ABC123/",
          "reel_id": "ABC123",
          "created_at": 1703123456,
          "last_scraped": 1703123456,
          "next_scrape_due": 1703209856,
          "scrape_interval_days": 2,
          "status": "active",
          "reel_data": {
            "caption": "Sample reel caption",
            "likes": 250,
            "comments": 15,
            "views": 1000,
            "timestamp": 1703123456,
            "hashtags": ["#sample", "#reel"],
            "mentions": [],
            "top_comments": [],
            "sentiment_analysis": {
              "positive": 10,
              "negative": 2,
              "neutral": 3,
              "overall_sentiment": "positive"
            }
          }
        }
      ]
    }
  }
}
```

### Force Scrape Reel
```json
POST /codvid-ai/ig-tracking/force_scrape_reel/{task_id}
```

**Response:**
```json
{
  "result": true,
  "message": "Reel tracking task scraping initiated successfully",
  "task_id": "7a809618-8939-4979-b72f-9b9f4bea137f",
  "status": "processing"
}
```

---

## Enhanced Task Monitoring

### Task Status Endpoint
```json
GET /codvid-ai/ig-tracking/task_status/{task_id}?logs_count=10
```

#### Query Parameters
- `logs_count`: Number of latest logs to return (default: 10, max: 100)

#### Response Format
```json
{
  "result": true,
  "response": {
    "task_id": "123",
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
      }
    ],
    "latest_event": {
      "timestamp": 1703123457,
      "message": "Fetching profile data from Instagram API"
    }
  }
}
```

---

## AI Chat Endpoints

### AI Response (Streaming)
```json
POST /codvid-ai/ai/respond
{
  "schema_version": "4.0",
  "data": {
    "project_name": "my_project",
    "message": {
      "role": "user",
      "type": "text",
      "text": "Hello, how are you?"
    }
  }
}
```

**Response (streamed):**
Returns a **stream** of JSON objects, **each** containing data modifications:

```json
{
  "result": true,
  "response": {
    "data_mods": [
      {
        "key_path": ["projects", "my_project", "chats"],
        "mode": "append",
        "value": {
          "role": "assistant",
          "type": "text",
          "text": "Hello! I'm doing well, thank you for asking."
        }
      }
    ]
  }
}
```

### AI Response Test (Streaming)
```json
POST /codvid-ai/ai/respond-stream-test
{
  "schema_version": "4.0",
  "data": {}
}
```

### Data Modifications System

The AI endpoints use a data modification system to update the client's local cache in real-time:

#### Data Mod Structure
```json
{
  "key_path": ["projects", "project_name", "chats"],
  "mode": "append",
  "value": {
    "role": "assistant",
    "type": "text",
    "text": "AI response content"
  }
}
```

#### Modification Modes
- **`create`**: Create that key path and assign the value
- **`edit`**: Edit the value at that key path
- **`del`**: Delete the key-value pair
- **`append`**: Append the value to the list expressed by the key_path

#### Message Types

**Text Messages:**
```json
{
  "role": "user",
  "type": "text",
  "text": "Hello, how are you?"
}
```

**Event Messages:**
```json
{
  "role": "assistant",
  "type": "event",
  "event_type": "tool_calling",
  "text": "Searching reels related to food restaurant"
}
```

**Tool Messages:**
```json
{
  "role": "tool",
  "type": "text",
  "text": "--- results --- \nSearch results data"
}
```

#### Event Types
- **`loading`**: Processing indicator
- **`info`**: Informational messages
- **`show_reel_options`**: Display reel selection options
- **`tool_calling`**: AI tool usage notifications

### Complete Chat Flow

1. **User sends a message** through the client
2. **Client appends** the message to local cache
3. **Client sends** project name and message to `/codvid-ai/ai/respond`
4. **Server retrieves** full user context from database
5. **Server responds** with AI's reply via streaming data modifications
6. **Client applies** the modifications to local cache in real-time
7. **Client validates** synchronization with server
8. **UI updates** to show the new chat history

### Stream Response Format

The AI response endpoint returns a stream of JSON objects:

```json
{"result": true, "response": {"data_mods": [...]}}
{"result": true, "response": {"data_mods": [...]}}
{"result": true, "response": {"data_mods": [...]}}
```

Each chunk should be parsed individually by the client to:
1. Parse each JSON chunk as it arrives
2. Apply the `data_mods` to the local cache
3. Update the UI to show progress
4. Handle any errors in individual chunks

---

## API Endpoints Reference

### Base URL
- **Development**: `https://codvid-ai-backend-development.up.railway.app`
- **Local**: `http://localhost:8080`

### Authentication Endpoints
| Method | Endpoint | Description | Response Example |
|--------|----------|-------------|------------------|
| POST | `/codvid-ai/auth/signup` | User registration | `{"result": true, "response": {"message": "User registered successfully"}}` |
| POST | `/codvid-ai/auth/login` | User authentication | `{"result": true, "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}` |
| DELETE | `/codvid-ai/user/delete_account` | Account deletion | `{"result": true, "response": {"message": "Account deleted successfully"}}` |

### User Management Endpoints
| Method | Endpoint | Description | Response Example |
|--------|----------|-------------|------------------|
| DELETE | `/codvid-ai/user/delete-account` | Delete user account | `{"result": true}` |

### Project Management Endpoints
| Method | Endpoint | Description | Response Example |
|--------|----------|-------------|------------------|
| POST | `/codvid-ai/project/create-project` | Create new project | `{"result": true}` |
| POST | `/codvid-ai/project/get-project-data` | Load project data | `{"result": true, "response": {"project_data": {...}}}` |
| POST | `/codvid-ai/project/get-project-list` | Get all user projects | `{"result": true, "response": {"project_list": ["project1", "project2"]}}` |
| POST | `/codvid-ai/project/get-project-mod-count` | Get project modification count | `{"result": true, "response": {"mod_count": 5}}` |
| DELETE | `/codvid-ai/project/delete-project` | Delete project | `{"result": true}` |

### AI Chat Endpoints
| Method | Endpoint | Description | Response Example |
|--------|----------|-------------|------------------|
| POST | `/codvid-ai/ai/respond` | AI chat response (streaming) | `{"result": true, "response": {"data_mods": [{"key_path": ["projects", "my_project", "chats"], "mode": "append", "value": {...}}]}}` |
| POST | `/codvid-ai/ai/respond-stream-test` | AI streaming test endpoint | `{"a": "0\n"}` |

### Profile Tracking Endpoints
| Method | Endpoint | Description | Response Example |
|--------|----------|-------------|------------------|
| POST | `/codvid-ai/ig-tracking/create_task` | Create profile tracking task | `{"result": true, "response": {"task_id": "uuid", "message": "Instagram tracking task created successfully"}}` |
| GET | `/codvid-ai/ig-tracking/get_tasks` | Get all profile tasks | `{"result": true, "response": {"tasks": [{"_id": "uuid", "target_profile": "username", ...}]}}` |
| GET | `/codvid-ai/ig-tracking/get_task/{id}` | Get task details | `{"result": true, "response": {"task": {"_id": "uuid", "target_profile": "username", "target_profile_data": {...}}}}` |
| PUT | `/codvid-ai/ig-tracking/update_scrape_interval/{id}` | Update scrape interval | `{"result": true, "response": {"message": "Scrape interval updated to X days"}}` |
| POST | `/codvid-ai/ig-tracking/force_scrape/{id}` | Force immediate scrape | `{"result": true, "message": "Task scraping initiated successfully", "task_id": "uuid", "status": "processing"}` |
| DELETE | `/codvid-ai/ig-tracking/delete_task/{id}` | Delete tracking task | `{"result": true, "response": {"message": "Tracking task deleted successfully"}}` |
| GET | `/codvid-ai/ig-tracking/task_status/{id}` | Get task processing status | `{"result": true, "response": {"is_processing": true, "logs": [...], "latest_event": {...}}}` |

### Reel Tracking Endpoints
| Method | Endpoint | Description | Response Example |
|--------|----------|-------------|------------------|
| POST | `/codvid-ai/ig-tracking/create_reel_task` | Create reel tracking task | `{"result": true, "response": {"task_id": "uuid", "message": "Instagram reel tracking task created successfully"}}` |
| POST | `/codvid-ai/ig-tracking/force_scrape_reel/{id}` | Force reel scrape | `{"result": true, "message": "Reel tracking task scraping initiated successfully", "task_id": "uuid", "status": "processing"}` |

---

## Data Models

### Profile Tracking Task
```json
{
  "_id": "uuid",
  "user_id": "user_uuid",
  "target_profile": "instagram_username",
  "is_competitor": false,
  "status": "active",
  "created_at": 1703123456,
  "last_scraped": 1703123456,
  "next_scrape_due": 1703209856,
  "scrape_interval_days": 2,
  "target_profile_data": {
    "scraped_posts": [],
    "icon_pic_url": "",
    "username": "",
    "full_name": "",
    "biography": "",
    "followers": null,
    "following": null,
    "posts_count": null,
    "ig_tv_video_count": null
  }
}
```

### Reel Tracking Task
```json
{
  "_id": "uuid",
  "reel_url": "https://www.instagram.com/reels/ABC123/",
  "reel_id": "ABC123",
  "created_at": 1703123456,
  "last_scraped": 1703123456,
  "next_scrape_due": 1703209856,
  "scrape_interval_days": 2,
  "status": "active",
      "reel_data": {
      "caption": "",
      "likes": null,
      "comments": null,
      "views": null,
      "timestamp": null,
      "hashtags": [],
      "mentions": [],
      "top_comments": [],
      "sentiment_analysis": {
        "positive": null,
        "negative": null,
        "neutral": null,
        "overall_sentiment": "neutral"
      }
    }
}
```

### Processing Log Entry
```json
{
  "timestamp": 1703123456,
  "message": "Human readable log message"
}
```

### Client-Side Local Cache Structure

The system uses a hybrid architecture where the client maintains a local cache (`local_user_data`) synchronized with the server database.

```json
local_user_data = {
  "global_data": {
    "ai_memory": {},
    "video_reflections": {
      "DEMO-REEL-ID": {
        "comments": ["hihihi"],
        "reflection": "DEMO-REFLECTION"
      }
    }
  },
  "projects": {
    "DEMO_PROJECT_NAME": {
      "schema_version": "1.0",
      "mod_count": 1,
      "date": "18-7-2025",
      "project_info": {
        "description": "DEMO",
        "keywords": ["DEMO", "DEMO"]
      },
      "ai_memory": {
        "DEMO_MEMORY_NAME1": "DEMO_TEXT",
        "DEMO_MEMORY_NAME2": "DEMO_TEXT"
      },
      "chats": [
        {
          "role": "user",
          "type": "text",
          "text": "blablablablabla"
        },
        {
          "role": "assistant",
          "type": "text",
          "text": "blablablablabla"
        }
      ],
      "reel_tracking_tasks": [
        {
          "_id": "uuid",
          "reel_url": "https://www.instagram.com/reels/ABC123/",
          "reel_id": "ABC123",
          "created_at": 1703123456,
          "last_scraped": 1703123456,
          "next_scrape_due": 1703209856,
          "scrape_interval_days": 2,
          "status": "active",
          "reel_data": {...}
        }
      ]
    }
  }
}
```

**Key Architecture Features:**
- **Hybrid Architecture**: Client maintains local cache, server maintains database
- **Synchronization**: `mod_count` field tracks changes for sync validation
- **Authentication**: User data wrapped in database document with UUID and auth methods
- **Sync Mechanism**: `check_and_reload_project_data()` validates and syncs local cache with server

**Cache Management:**
- Local cache provides performance optimization for frequent access
- Server database maintains authoritative data state
- Data modifications (`data_mods`) keep client and server synchronized
- `mod_count` validation ensures cache consistency

---

## Error Handling

### Standard Error Response
```json
{
  "result": false,
  "message": "Error description"
}
```

### Common HTTP Status Codes
- **200**: Success
- **201**: Created
- **400**: Bad Request (validation errors)
- **401**: Unauthorized
- **404**: Not Found
- **500**: Internal Server Error

### Error Messages
- Missing required fields
- Invalid Instagram username format
- Invalid scrape interval
- Task not found or access denied
- Invalid Instagram reel URL format

---

## Usage Examples

### Complete Profile Tracking Workflow
```python
# 1. Login
login_response = client.login(email, password)

# 2. Create tracking task
task_data = {
    "target_profile": "instagram_username",
    "is_competitor": false,
    "scrape_interval_days": 2
}
task_response = client.create_tracking_task(task_data)

# 3. Force scrape
scrape_response = client.force_scrape_task(task_id)

# 4. Monitor progress
status_response = client.get_task_status(task_id, logs_count=20)

# 5. Get results
details_response = client.get_task_details(task_id)
```

### Project Management Workflow
```python
# 1. Login
login_response = client.login(email, password)

# 2. Get all projects
projects_response = client.get_project_list()

# 3. Create new project
project_response = client.create_project("new_project")

# 4. Get project data
project_data_response = client.get_project_data("new_project")

# 5. Check project modification count
mod_count_response = client.get_project_mod_count("new_project")

# 6. Delete project when done
delete_response = client.delete_project("new_project")
```

### Complete Reel Tracking Workflow
```python
# 1. Create project
project_response = client.create_project("my_project")

# 2. Create reel tracking task
reel_data = {
    "project_name": "my_project",
    "reel_url": "https://www.instagram.com/reels/ABC123/",
    "scrape_interval_days": 2
}
reel_response = client.create_reel_tracking_task(reel_data)

# 3. Force scrape
scrape_response = client.force_scrape_reel_task(task_id)

# 4. Monitor progress
status_response = client.get_task_status(task_id, logs_count=15)

# 5. Get project data with results
project_data = client.get_project_data("my_project")
```

### Real-time Task Monitoring
```python
def monitor_task_progress(task_id, logs_count=10):
    """Monitor task progress in real-time"""
    while True:
        status = client.get_task_status(task_id, logs_count)
        
        if status["response"]["is_processing"]:
            logs = status["response"]["logs"]
            print(f"Processing... {len(logs)} logs")
            
            # Show latest logs
            for log in logs[-3:]:  # Show last 3 logs
                timestamp = datetime.fromtimestamp(log["timestamp"])
                print(f"[{timestamp}] {log['message']}")
        else:
            print("Task completed!")
            break
            
        time.sleep(2)  # Poll every 2 seconds
```

### Complete AI Chat Workflow
```python
# 1. Login and create project
login_response = client.login(email, password)
project_response = client.create_project("my_project")

# 2. Send message to AI
message_data = {
    "project_name": "my_project",
    "message": {
        "role": "user",
        "type": "text",
        "text": "Hello, can you help me analyze my Instagram reels?"
    }
}

# 3. Stream AI response
response_stream = client.ai_interact("my_project", message_data["message"])

# 4. Process streaming data modifications
for chunk in response_stream:
    if chunk.get("result"):
        data_mods = chunk["response"]["data_mods"]
        for mod in data_mods:
            # Apply modification to local cache
            apply_data_mod(local_cache, mod)
            
            # Update UI with new chat content
            if mod["key_path"] == ["projects", "my_project", "chats"]:
                update_chat_ui(mod["value"])
```

### Real-time AI Chat Monitoring
```python
def stream_ai_chat(project_name, message_text):
    """Stream AI chat responses with real-time updates"""
    message = {
        "role": "user",
        "type": "text", 
        "text": message_text
    }
    
    # Send to AI endpoint
    response = requests.post(
        f"{base_url}/codvid-ai/ai/respond",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "schema_version": "4.0",
            "data": {
                "project_name": project_name,
                "message": message
            }
        },
        stream=True
    )
    
    # Process streaming response
    for line in response.iter_lines():
        if line:
            try:
                chunk = json.loads(line.decode('utf-8'))
                if chunk.get("result"):
                    data_mods = chunk["response"]["data_mods"]
                    for mod in data_mods:
                        print(f"Received mod: {mod['mode']} at {mod['key_path']}")
                        
                        # Handle different message types
                        if mod["value"].get("type") == "event":
                            event_type = mod["value"]["event_type"]
                            print(f"AI Event: {event_type} - {mod['value']['text']}")
                        elif mod["value"].get("type") == "text":
                            print(f"AI Response: {mod['value']['text']}")
                            
            except json.JSONDecodeError:
                continue
```

---

## Key Features Summary

### ✅ AI Chat System
- Real-time streaming AI responses
- Project-based conversation context
- Data modification system for live updates
- Multiple message types (text, events, tools)
- Tool calling and reel analysis capabilities

### ✅ Profile Tracking
- Monitor Instagram profiles (own or competitors)
- Scheduled automatic scraping
- Sentiment analysis of comments
- Performance metrics tracking

### ✅ Reel Tracking
- Track specific Instagram reels
- Project-based organization
- Engagement metrics analysis
- Sentiment analysis of reel comments

### ✅ Enhanced Monitoring
- Real-time task progress tracking
- Configurable log depth (1-100 logs)
- Comprehensive processing visibility
- Backward-compatible API

### ✅ User Management
- Secure authentication system
- Project-based organization
- Flexible scrape intervals
- Comprehensive task management

---

## Development Notes

### Backward Compatibility
- All existing endpoints maintain current functionality
- New features are additive, not breaking
- `latest_event` still available alongside new `logs` array

### Performance Considerations
- Log retrieval limited to 100 entries maximum
- Processing registry uses in-memory storage
- Background scheduler handles bulk processing

### Security Features
- User authentication required for all endpoints
- Task access control (users can only access their own tasks)
- Input validation and sanitization

---

*This documentation covers all updates from 1-7 and provides a complete reference for frontend development and API integration.*
