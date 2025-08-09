# Comprehensive Server-Client Documentation

## Overview

This comprehensive documentation covers the complete Codvid AI Backend system architecture, including all features and updates from version 2 through the latest reel tracking service. The system has evolved from a local storage model to a hybrid local/cloud architecture with MongoDB backend, JWT authentication, Instagram profile tracking, and Instagram reel tracking capabilities.

## Table of Contents

1. [Authentication System](#authentication-system)
2. [Core Architecture](#core-architecture)
3. [Project Management](#project-management)
4. [AI Endpoints](#ai-endpoints)
5. [Instagram Profile Tracking](#instagram-profile-tracking)
6. [Instagram Reel Tracking](#instagram-reel-tracking)
7. [Client Integration](#client-integration)
8. [Error Handling](#error-handling)
9. [Migration Guide](#migration-guide)

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

### Authentication Endpoints

#### User Registration (Sign Up)
**Endpoint:** `POST /codvid-ai/auth/signup`

**Request:**
```json
{
  "schema_version": "4.0",
  "data": {
    "auth_type": "email",
    "email": "user@example.com",
    "password": "securepassword123"
  }
}
```

**Success Response (201):**
```json
{
  "result": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
```

**Error Response (400):**
```json
{
  "result": false,
  "message": "Email is already linked to an account"
}
```

#### User Login
**Endpoint:** `POST /codvid-ai/auth/login`

**Request:**
```json
{
  "schema_version": "4.0",
  "data": {
    "auth_type": "email",
    "email": "user@example.com",
    "password": "securepassword123"
  }
}
```

**Success Response (201):**
```json
{
  "result": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
```

**Error Response (400):**
```json
{
  "result": false,
  "message": "Email is not linked to an account."
}
```

#### Get User UUID (Optional)
**Endpoint:** `GET /codvid-ai/auth/get_uuid?email=user@example.com`

**Success Response (200):**
```json
{
  "result": true,
  "response": {
    "uuid": "user_uuid_here"
  }
}
```

### Authorization Header
For all protected endpoints, include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## Core Architecture

### Structure of User Data

The system uses a hybrid architecture where the client maintains a local cache (`local_user_data`) synchronized with the server database.

#### Database Structure (Server)

```json
{
  "_id": "user_uuid",
  "schema_version": "1.2",
  "profile": {
    "email": "user@example.com"
  },
  "auth_methods": [
    {
      "method": "password",
      "password_hash": "hashed_password"
    }
  ],
  "data": {
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
        ]
      }
    }
  }
}
```

#### Local Cache Structure (Client)

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
      ]
    }
  }
}
```

### Server-Client Communication Rules

When client **sends** a request to server with data, the data should be in this format:

```json
{
  "schema_version": "4.0",
  "data": {
    // key-value pair data inside here depending on the request
  }
}
```

**Server Response (Success):**
```json
{
  "result": true,
  "response": {
    // key-value pair data inside here as the returned data
  }
}
```

**Server Response (Error):**
```json
{
  "result": false,
  "message": "Descriptive error message"
}
```

---

## Project Management

### Get Project List
**Endpoint:** `GET/POST /codvid-ai/project/get-project-list`

**Request:**
```json
{
  "schema_version": "4.0",
  "data": {}
}
```

**Success Response (200):**
```json
{
  "result": true,
  "response": {
    "project_list": ["my_project", "test_project", "demo_project"]
  }
}
```

### Create Project
**Endpoint:** `POST /codvid-ai/project/create-project`

**Request:**
```json
{
  "schema_version": "4.0",
  "data": {
    "project_name": "my_new_project"
  }
}
```

**Success Response (200):**
```json
{
  "result": true
}
```

### Get Project Data
**Endpoint:** `GET/POST /codvid-ai/project/get-project-data`

**Request:**
```json
{
  "schema_version": "4.0",
  "data": {
    "project_name": "my_project"
  }
}
```

**Success Response (200):**
```json
{
  "result": true,
  "response": {
    "project_data": {
      "schema_version": "1.0",
      "mod_count": 5,
      "date": "18-7-2025",
      "project_info": {
        "description": "My project description",
        "keywords": ["keyword1", "keyword2"]
      },
      "ai_memory": {
        "context": "Previous conversation context"
      },
      "chats": [
        {
          "role": "user",
          "type": "text",
          "text": "Hello, how are you?"
        },
        {
          "role": "assistant",
          "type": "text",
          "text": "I'm doing well, thank you for asking!"
        }
      ]
    }
  }
}
```

### Get Project Mod Count
**Endpoint:** `GET/POST /codvid-ai/project/get-project-mod-count`

**Request:**
```json
{
  "schema_version": "4.0",
  "data": {
    "project_name": "my_project"
  }
}
```

**Success Response (200):**
```json
{
  "result": true,
  "response": {
    "mod_count": 5
  }
}
```

### Delete Project
**Endpoint:** `POST /codvid-ai/project/delete-project`

**Request:**
```json
{
  "schema_version": "4.0",
  "data": {
    "project_name": "project_to_delete"
  }
}
```

**Success Response (200):**
```json
{
  "result": true
}
```

---

## AI Endpoints

### AI Response (Streaming)
**Endpoint:** `POST /codvid-ai/ai/respond`

**Request:**
```json
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

**Stream Response:** Returns a stream of JSON objects, each containing data modifications.

### AI Response Test (Streaming)
**Endpoint:** `POST /codvid-ai/ai/respond-stream-test`

**Request:**
```json
{
  "schema_version": "4.0",
  "data": {}
}
```

### Types of Response

#### I. Event Response

- `event_type`:
  - loading
  - info
  - show_reel_options
  - tool_calling

**Examples:**
```json
{
  "role": "assistant",
  "type": "event",
  "event_type": "tool_calling",
  "text": "searching reels related to xx food restaurant"
},
{
  "role": "assistant",
  "type": "event",
  "event_type": "show_reel_options",
  "options": ["DEMO_REEL_ID", "DEMO_REEL_ID", "DEMO_REEL_ID"]
},
{
  "role": "assistant",
  "type": "event",
  "event_type": "info",
  "text": "AI have worked for {n} extra times. You can say 'continue' to allow me to continue"
}
```

#### II. Message Types

**Text Messages:**
```json
{
  "role": "user",
  "type": "text",
  "text": "Hello, how are you?"
}
```

**Tool Messages:**
```json
{
  "role": "tool",
  "type": "text",
  "text": "--- results --- \n BLALBABLABLABLA"
}
```

**Event Messages:**
```json
{
  "role": "assistant",
  "type": "event",
  "event_type": "loading",
  "text": "Processing your request..."
}
```

---

## Instagram Profile Tracking

### Overview

The Instagram Profile Tracking system allows users to monitor Instagram profiles (both their own and competitors') for sentiment analysis and engagement insights. The system provides automated monitoring with detailed analytics through REST API endpoints.

### Key Features

1. **Profile Monitoring**: Track multiple Instagram profiles with automated processing
2. **Automated Processing**: System automatically processes the 3 most recent posts/reels every 2 days
3. **Comment Analysis**: Analyzes the top 10 comments per post for sentiment
4. **Sentiment Classification**: Comments are classified as positive, negative, or neutral

### Data Structure

**Task Overview:**
```json
{
  "_id": "uuid-task-id",
  "target_profile": "instagram_username",
  "is_competitor": true,
  "created_at": 1678886400,
  "last_scraped": 1679059200,
  "next_scrape_due": 1679232000,
  "status": "active"
}
```

**Detailed Post Data:**
```json
{
  "scraped_posts": [
    {
      "post_id": "abc123",
      "post_url": "https://instagram.com/p/abc123",
      "timestamp": 1751029635,
      "type": "reel",
      "caption": "Post caption text",
      "likes_count": 1234,
      "comments_count": 56,
      "video_view_count": 10000,
      "hashtags": ["#food", "#tasty"],
      "mentions": ["@username"],
      "top_comments": [
        {
          "text": "Amazing product!",
          "sentiment": "positive",
          "owner_username": "commenter123",
          "timestamp": 1751029635,
          "likes_count": 5
        }
      ]
    }
  ]
}
```

### API Endpoints

All endpoints require JWT authentication and use schema version "4.0".

#### 1. Create Tracking Task
**Endpoint:** `POST /codvid-ai/ig-tracking/create_task`

**Request:**
```json
{
  "schema_version": "4.0",
  "data": {
    "target_profile": "instagram_username",
    "is_competitor": true,
    "scrape_interval_days": 2
  }
}
```

#### 2. Get User Tasks
**Endpoint:** `GET /codvid-ai/ig-tracking/get_tasks`

**Response:**
```json
{
  "result": true,
  "response": {
    "tasks": [
      {
        "_id": "task-id",
        "target_profile": "instagram_username",
        "is_competitor": true,
        "created_at": 1678886400,
        "last_scraped": 1679059200,
        "next_scrape_due": 1679232000,
        "status": "active"
      }
    ]
  }
}
```

#### 3. Get Task Details
**Endpoint:** `GET /codvid-ai/ig-tracking/get_task/{task_id}`

#### 4. Update Task
**Endpoint:** `PUT /codvid-ai/ig-tracking/update_task/{task_id}`

#### 5. Delete Task
**Endpoint:** `DELETE /codvid-ai/ig-tracking/delete_task/{task_id}`

#### 6. Force Scrape Task
**Endpoint:** `POST /codvid-ai/ig-tracking/force_scrape/{task_id}`

#### 7. Get Sentiment Summary
**Endpoint:** `GET /codvid-ai/ig-tracking/sentiment_summary/{task_id}`

**Response:**
```json
{
  "result": true,
  "response": {
    "sentiment_summary": {
      "total_comments": 25,
      "sentiment_distribution": {
        "positive": 15,
        "negative": 5,
        "neutral": 5
      },
      "sentiment_percentages": {
        "positive": 60.0,
        "negative": 20.0,
        "neutral": 20.0
      },
      "overall_sentiment": "positive"
    }
  }
}
```

#### 8. Update Scraping Interval
**Endpoint:** `PUT/POST /codvid-ai/ig-tracking/update_scrape_interval/{task_id}`

**Request:**
```json
{
    "schema_version": "4.0",
    "data": {
        "scrape_interval_days": 0.5
    }
}
```

---

## Instagram Reel Tracking

### Overview

The Reel Tracking Service is a project-based Instagram monitoring system that tracks individual reels rather than entire profiles. This service provides granular insights into specific video performance, making it ideal for content creators, marketers, and businesses who want to analyze the success of particular video content.

### Key Features

1. **Project-Based Organization**: Each reel tracking task belongs to a specific project
2. **Individual Reel Monitoring**: Track specific Instagram reel URLs with performance metrics
3. **Automated Data Collection**: Scheduled scraping every 2 days with background processing
4. **AI-Powered Sentiment Analysis**: Comment sentiment analysis with percentage breakdowns

### Service Limitations

1. **Instagram API Constraints**: Rate limiting and access restrictions
2. **Scraping Limitations**: Limited comment depth and historical data access
3. **Project Dependencies**: Must have existing project to create reel tracking tasks

### API Endpoints

#### 1. Create Reel Tracking Task
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

**Response:**
```json
{
    "result": true,
    "response": {
        "task_id": "uuid-string",
        "message": "Instagram reel tracking task created successfully"
    }
}
```

#### 2. Get Project Reel Tasks
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

**Response:**
```json
{
    "result": true,
    "response": {
        "tasks": [
            {
                "_id": "task-id",
                "reel_url": "https://www.instagram.com/reels/REEL_ID/",
                "reel_id": "REEL_ID",
                "reel_data": {
                    "caption": "Reel caption text",
                    "likes": 1234,
                    "comments": 56,
                    "views": 10000,
                    "timestamp": 1751029635,
                    "hashtags": ["#food", "#tasty"],
                    "mentions": ["@username"],
                    "top_comments": [...],
                    "sentiment_analysis": {
                        "positive": 19,
                        "negative": 54,
                        "neutral": 24,
                        "overall_sentiment": "negative"
                    }
                },
                "created_at": 1754654044,
                "last_scraped": 1754654979,
                "next_scrape_due": 1754827779,
                "scrape_interval_days": 2,
                "status": "active"
            }
        ],
        "total_tasks": 1
    }
}
```

#### 3. Force Scrape Reel Task
**Endpoint:** `POST /codvid-ai/ig-tracking/force_scrape_reel/{task_id}`

**Response:**
```json
{
    "result": true,
    "message": "Reel tracking task scraping completed successfully"
}
```

#### 4. Delete Reel Tracking Task
**Endpoint:** `DELETE /codvid-ai/ig-tracking/delete_reel_task/{task_id}`

### Data Structure

**Reel Tracking Task Object:**
```json
{
    "_id": "task-uuid",
    "reel_url": "https://www.instagram.com/reels/REEL_ID/",
    "reel_id": "REEL_ID",
    "reel_data": {
        "caption": "Reel caption text",
        "likes": 1234,
        "comments": 56,
        "views": 10000,
        "timestamp": 1751029635,
        "hashtags": ["#food", "#tasty"],
        "mentions": ["@username"],
        "top_comments": [
            {
                "text": "Amazing content!",
                "sentiment": "positive",
                "owner_username": "commenter123",
                "timestamp": 1751029635,
                "likes_count": 5
            }
        ],
        "sentiment_analysis": {
            "positive": 19,
            "negative": 54,
            "neutral": 24,
            "overall_sentiment": "negative"
        }
    },
    "created_at": 1754654044,
    "last_scraped": 1754654979,
    "next_scrape_due": 1754827779,
    "scrape_interval_days": 2,
    "status": "active"
}
```

---

## Client Integration

### Core Functions

- `ai_interact(project_name, message)` - Send message to AI and handle response
- `apply_user_data_mods(data_mods)` - Apply server modifications to local cache
- `check_and_reload_project_data(project_name)` - Validate and sync with server
- `print_chats(project_name, max)` - Display chat history
- `chat(project_name)` - Interactive chat interface
- `start_chat(project_name)` - Start interactive chat session

### Authentication Functions

- `login(email, password)` - Authenticate user and get session token
- `signup(email, password)` - Register new user and get session token

### Project Management Functions

- `get_project_list()` - Retrieve user's projects
- `create_project(project_name)` - Create new project
- `delete_project(project_name)` - Remove project
- `load_project_data(project_name)` - Load project from database

### Instagram Tracking Functions

- `create_tracking_task(target_profile, is_competitor)` - Create profile tracking task
- `get_tracking_tasks()` - Get all profile tracking tasks
- `create_reel_tracking_task(project_name, reel_url)` - Create reel tracking task
- `get_project_reel_tasks(project_name)` - Get project reel tracking tasks

### Network Functions

- `network.send(route, content, session_token)` - Send HTTP request
- `network.send_and_stream(route, content, session_token)` - Send streaming request
- `network.init(base_url)` - Initialize network with server URL

### Example Usage

```python
# Initialize network
network.init("http://127.0.0.1:8080/")

# Authentication
session_token = login("user@example.com", "password123")

# Project management
projects = get_project_list()
create_project("my_new_project")
load_project_data("my_new_project")

# AI interaction
message = {"role": "user", "type": "text", "text": "Hello!"}
ai_interact("my_new_project", message)

# Instagram tracking
create_tracking_task("competitor_profile", True)
create_reel_tracking_task("my_new_project", "https://instagram.com/reels/REEL_ID/")

# Interactive chat
start_chat("my_new_project")
```

---

## Error Handling

### Common Error Messages

**Authentication Errors:**
- `"Unauthorized: missing session token while accessing non-public routes"` - Missing Authorization header
- `"Unauthorized: invalid or expired token"` - Invalid or expired JWT token
- `"Email is already linked to an account"` - Email already registered
- `"Email is not linked to an account"` - Email not found during login
- `"wrong password"` - Incorrect password during login

**Schema Validation Errors:**
- `"Schema version mismatch. Expected 4.0, got 3.0"` - Wrong schema version
- `"Invalid JSON request body"` - Malformed JSON in request
- `"Missing data field"` - Missing data field in request

**Project Errors:**
- `"Project not exists"` - Project not found
- `"Project already exists"` - Project name already taken
- `"Project not found"` - Project not found during deletion

**Instagram Tracking Errors:**
- `"Invalid Instagram username format"` - Invalid profile name
- `"Invalid Instagram reel URL format"` - Invalid reel URL
- `"Task not found or access denied"` - Task not found or unauthorized

### Error Recovery Strategies

1. **Authentication Errors**: Re-authenticate the user
2. **Schema Errors**: Update client to use correct schema version
3. **Project Errors**: Verify project exists before operations
4. **Network Errors**: Implement retry logic with exponential backoff
5. **Stream Errors**: Handle individual chunk failures gracefully

---

## Migration Guide

### For Existing Clients

1. **Update schema version to "4.0"**
2. **Implement authentication flow** (signup/login endpoints)
3. **Include JWT token in Authorization header** for all requests
4. **Update request format** to only send project name and message
5. **Handle new response format** with data modifications
6. **Implement synchronization validation** with `mod_count`

### For New Clients

1. **Follow authentication flow documentation**
2. **Use simplified request format**
3. **Implement data modification application**
4. **Handle project management operations**
5. **Implement local cache synchronization**

### Backward Compatibility

The new system is **not backward compatible** with the old local storage system. Clients must be updated to use the new authentication and database-backed architecture.

---

## Complete Workflow Example

Here's a complete example of creating a project, loading it, and starting a chat with Instagram tracking:

```python
# 1. Login (get session token)
login_data = {
    "auth_type": "email",
    "email": "user@example.com", 
    "password": "password123"
}
login_response = network.send("codvid-ai/auth/login", login_data)
session_token = login_response.get_dict().get("token")

# 2. Create a new project
create_data = {"project_name": "my_new_project"}
create_response = network.send(
    "codvid-ai/project/create-project", 
    content=create_data, 
    session_token=session_token
)

# 3. Load project data into local cache
load_data = {"project_name": "my_new_project"}
load_response = network.send(
    "codvid-ai/project/get-project-data", 
    content=load_data, 
    session_token=session_token
)
project_data = load_response.get_dict()["response"]["project_data"]

# 4. Initialize local cache
local_user_data = {
    "global_data": {"ai_memory": {}, "video_reflections": {}},
    "projects": {"my_new_project": project_data}
}

# 5. Create Instagram tracking tasks
profile_data = {
    "target_profile": "competitor_profile",
    "is_competitor": True
}
profile_response = network.send(
    "codvid-ai/ig-tracking/create_task",
    content=profile_data,
    session_token=session_token
)

reel_data = {
    "project_name": "my_new_project",
    "reel_url": "https://www.instagram.com/reels/REEL_ID/"
}
reel_response = network.send(
    "codvid-ai/ig-tracking/create_reel_task",
    content=reel_data,
    session_token=session_token
)

# 6. Start AI interaction
message = {"role": "user", "type": "text", "text": "Hello!"}
ai_response = network.send_and_stream(
    "codvid-ai/ai/respond",
    content={"project_name": "my_new_project", "message": message},
    session_token=session_token
)
```

---

## Support Resources

- **Complete Demo Notebooks**: Available in the demo_client folder
- **API Reference**: Detailed endpoint documentation in this guide
- **Error Handling**: Common issues and solutions
- **Best Practices**: Recommended usage patterns

---

## What's Next

### Immediate Actions
1. **Review API Documentation**: Understand endpoint requirements and limitations
2. **Try the Demos**: Run through the interactive demo notebooks
3. **Create Test Projects**: Start with simple projects and tracking tasks
4. **Integrate into Workflow**: Add Instagram tracking to your content analysis pipeline

### Future Enhancements
- **Batch Operations**: Create multiple tracking tasks at once
- **Advanced Analytics**: Trend analysis and performance comparisons
- **Export Features**: Data export in various formats
- **Integration APIs**: Connect with other analytics platforms

The Codvid AI Backend provides powerful content analysis and Instagram monitoring capabilities through simple REST API calls, making it easy to integrate into any client application for comprehensive content performance monitoring and sentiment analysis.
