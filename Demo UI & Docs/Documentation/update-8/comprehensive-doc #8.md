# Instagram Tracking Service - Complete System Documentation

## Overview
The Instagram Tracking Service provides comprehensive monitoring capabilities for Instagram profiles and reels. This service enables users to track competitor profiles, monitor specific reels, and analyze engagement patterns with automated scraping and sentiment analysis.

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Root Endpoints](#root-endpoints)
3. [Authentication & User Management](#authentication--user-management)
4. [Project Management](#project-management)
5. [Instagram Tracking](#instagram-tracking)
6. [AI Chat Integration](#ai-chat-integration)
7. [Data Models](#data-models)
8. [Error Handling](#error-handling)
9. [Real-time Monitoring](#real-time-monitoring)

## System Architecture

### Core Components
- **Profile Tracking**: Monitor Instagram profiles for posts, engagement, and growth
- **Reel Tracking**: Track specific Instagram reels for performance analysis
- **Project Management**: Organize tracking tasks within user-defined projects
- **Automated Scraping**: Scheduled data collection with configurable intervals
- **Sentiment Analysis**: AI-powered content sentiment evaluation

### Service Structure
- **REST API**: HTTP-based interface for all operations
- **JWT Authentication**: Secure user access and data isolation
- **Background Processing**: Asynchronous task execution for scraping
- **Real-time Updates**: Live progress monitoring and status tracking

## Root Endpoints

### Base URL
```
https://api.example.com/codvid-ai
```

### System Endpoints

#### Health Check
- **Endpoint**: `GET /ping`
- **Purpose**: Check if the API is running and responsive
- **Authentication**: Not required
- **Response**:
```json
{
  "message": "pong"
}
```

### Middleware Information

#### JWT Authentication Middleware
- **Public Paths** (no authentication required):
  - `/ping` - Health check endpoint
  - `/public` - Public resources
  - `/auth/login` - User login
  - `/auth/signup` - User registration
- **Protected Paths**: All other endpoints require JWT token

#### Schema Version Middleware
- **Purpose**: Validates request data schema version
- **Required Version**: Check `request_schema_version` in backend
- **Request Format**: All requests with JSON data must include schema version
```json
{
  "schema_version": "4.0",
  "data": {
    // actual request data
  }
}
```

## Authentication & User Management

### Base URL
```
https://api.example.com/codvid-ai/auth
```

### Authentication Endpoints

#### User Signup
- **Endpoint**: `POST /signup`
- **Purpose**: Create a new user account
- **Request Body**:
```json
{
  "schema_version": "4.0",
  "data": {
    "auth_type": "email",
    "email": "user@example.com",
    "password": "password123"
  }
}
```
- **Response**:
```json
{
  "result": true,
  "response": {
    "message": "User registered successfully"
  }
}
```

#### User Login
- **Endpoint**: `POST /login`
- **Purpose**: Authenticate user and obtain JWT token
- **Request Body**:
```json
{
  "schema_version": "4.0",
  "data": {
    "auth_type": "email",
    "email": "user@example.com",
    "password": "password123"
  }
}
```
- **Response**:
```json
{
  "result": true,
  "token": "jwt-token-string",
  "user_id": "uuid-string"
}
```

#### Get User UUID
- **Endpoint**: `GET /get_uuid`
- **Purpose**: Get current user's UUID (requires authentication)
- **Response**:
```json
{
  "result": true,
  "uuid": "uuid-string"
}
```

### User Management Endpoints

#### Delete Account
- **Endpoint**: `POST /codvid-ai/user/delete-account`
- **Purpose**: Delete user account and all associated data
- **Response**:
```json
{
  "result": true,
  "message": "Account deleted successfully"
}
```

## Project Management

### Base URL
```
https://api.example.com/codvid-ai/project
```

### Project Endpoints

#### Create Project
- **Endpoint**: `POST /create-project`
- **Purpose**: Create a new project
- **Request Body**:
```json
{
  "project_name": "My Project"
}
```
- **Response**:
```json
{
  "result": true,
  "message": "Project created successfully"
}
```

#### Get Project Data
- **Endpoint**: `POST /get-project-data`
- **Purpose**: Retrieve complete project data
- **Request Body**:
```json
{
  "project_name": "My Project"
}
```
- **Response**:
```json
{
  "result": true,
  "response": {
    "project_data": {
      "name": "My Project",
      "created_at": "timestamp",
      "reel_tracking_tasks": []
    }
  }
}
```

#### Get Project List
- **Endpoint**: `POST /get-project-list`
- **Purpose**: Get all user projects
- **Response**:
```json
{
  "result": true,
  "response": {
    "project_list": ["Project 1", "Project 2"]
  }
}
```

#### Get Project Modification Count
- **Endpoint**: `POST /get-project-mod-count`
- **Purpose**: Get project modification count for sync
- **Request Body**:
```json
{
  "project_name": "My Project"
}
```
- **Response**:
```json
{
  "result": true,
  "response": {
    "mod_count": 5
  }
}
```

#### Delete Project
- **Endpoint**: `POST /delete-project`
- **Purpose**: Delete a project and all its data
- **Request Body**:
```json
{
  "project_name": "My Project"
}
```
- **Response**:
```json
{
  "result": true,
  "message": "Project deleted successfully"
}
```

## Instagram Tracking

### Base URL
```
https://api.example.com/codvid-ai/ig-tracking
```

### Profile Tracking Endpoints

#### Create Profile Tracking Task
- **Endpoint**: `POST /create_profile_tracking_task`
- **Purpose**: Create a new Instagram profile monitoring task
- **Request Body**:
```json
{
  "target_profile": "instagram_username",
  "is_competitor": false,
  "scrape_interval_days": 2
}
```
- **Response**:
```json
{
  "result": true,
  "response": {
    "task_id": "uuid-string",
    "message": "Instagram tracking task created successfully"
  }
}
```

#### List Profile Tracking Tasks
- **Endpoint**: `GET /get_profile_tracking_tasks`
- **Purpose**: Retrieve all profile tracking tasks for the current user
- **Response**:
```json
{
  "result": true,
  "response": {
    "tasks": [
      {
        "task_id": "uuid-string",
        "target_profile": "username",
        "status": "active",
        "created_at": "timestamp",
        "is_competitor": false
      }
    ]
  }
}
```

#### Get Profile Tracking Task Details
- **Endpoint**: `GET /get_profile_tracking_task/<task_id>`
- **Purpose**: Retrieve detailed information about a specific task
- **Response**:
```json
{
  "result": true,
  "response": {
    "task": {
      "task_id": "uuid-string",
      "target_profile": "username",
      "status": "active",
      "created_at": "timestamp",
      "last_scraped": "timestamp",
      "next_scrape_due": "timestamp",
      "scrape_interval_days": 2,
      "is_competitor": false,
      "target_profile_data": {
        "scraped_posts": [],
        "icon_pic_url": "",
        "username": "",
        "full_name": "",
        "biography": "",
        "followers": null,
        "following": null,
        "posts_count": null
      }
    }
  }
}
```

#### Update Profile Tracking Task
- **Endpoint**: `PUT /update_profile_tracking_task/<task_id>`
- **Purpose**: Modify task properties (e.g., competitor flag)
- **Request Body**:
```json
{
  "is_competitor": true
}
```
- **Response**:
```json
{
  "result": true,
  "response": {
    "message": "Tracking task updated successfully"
  }
}
```

#### Delete Profile Tracking Task
- **Endpoint**: `DELETE /delete_profile_tracking_task/<task_id>`
- **Purpose**: Remove a tracking task
- **Response**:
```json
{
  "result": true,
  "response": {
    "message": "Tracking task deleted successfully"
  }
}
```

#### Force Scrape Profile Task
- **Endpoint**: `POST /force_scrape_profile_tracking_task/<task_id>`
- **Purpose**: Trigger immediate data collection
- **Response**:
```json
{
  "result": true,
  "message": "Task scraping initiated successfully",
  "task_id": "uuid-string",
  "status": "processing"
}
```

#### Update Scraping Interval
- **Endpoint**: `PUT /update_profile_tracking_scrape_interval/<task_id>`
- **Purpose**: Modify the frequency of data collection
- **Request Body**:
```json
{
  "scrape_interval_days": 7
}
```
- **Response**:
```json
{
  "result": true,
  "response": {
    "message": "Scrape interval updated successfully"
  }
}
```

#### Get Task Status
- **Endpoint**: `GET /profile_tracking_task_status/<task_id>`
- **Purpose**: Monitor real-time processing status and logs
- **Query Parameters**:
  - `logs_count`: Number of logs to return (default: 10, max: 100)
- **Response**:
```json
{
  "result": true,
  "response": {
    "task_id": "uuid-string",
    "is_processing": true,
    "logs": [
      {
        "timestamp": 1234567890,
        "message": "Starting profile analysis..."
      }
    ],
    "logs_count": 10,
    "requested_logs_count": 10,
    "latest_event": {
      "timestamp": 1234567890,
      "message": "Analysis complete"
    }
  }
}
```

### Reel Tracking Endpoints

#### Create Reel Tracking Task
- **Endpoint**: `POST /create_reel_task`
- **Purpose**: Create a new reel monitoring task within a project
- **Request Body**:
```json
{
  "project_name": "project_name",
  "reel_url": "https://instagram.com/reel/...",
  "scrape_interval_days": 2
}
```
- **Response**:
```json
{
  "result": true,
  "response": {
    "task_id": "uuid-string",
    "message": "Instagram reel tracking task created successfully"
  }
}
```

#### Get Reel Tracking Task Details
- **Endpoint**: `GET /get_reel_tracking_task/<task_id>`
- **Purpose**: Retrieve detailed information about a specific reel tracking task
- **Response**:
```json
{
  "result": true,
  "response": {
    "task": {
      "task_id": "uuid-string",
      "reel_url": "string",
      "reel_id": "string",
      "status": "active",
      "created_at": "timestamp",
      "project_name": "string",
      "reel_data": {
        "caption": "string",
        "likes": 1000,
        "comments": 50,
        "views": 5000
      }
    }
  }
}
```

#### Get Project Reel Tasks
- **Endpoint**: `GET /get_project_reel_tasks`
- **Purpose**: Retrieve all reel tracking tasks from a specific project
- **Request Body**:
```json
{
  "project_name": "project_name"
}
```
- **Response**:
```json
{
  "result": true,
  "response": {
    "tasks": [
      {
        "task_id": "uuid-string",
        "reel_url": "string",
        "status": "active",
        "created_at": "timestamp"
      }
    ],
    "total_tasks": 1
  }
}
```

#### Force Scrape Reel Task
- **Endpoint**: `POST /force_scrape_reel/<task_id>`
- **Purpose**: Trigger immediate reel data collection
- **Response**:
```json
{
  "result": true,
  "message": "Reel tracking task scraping initiated successfully",
  "task_id": "uuid-string",
  "status": "processing"
}
```

### Generic Endpoints

#### Sentiment Summary
- **Endpoint**: `GET /sentiment_summary/<task_id>`
- **Purpose**: Retrieve sentiment analysis results for any tracking task
- **Response**:
```json
{
  "result": true,
  "response": {
    "sentiment_summary": {
      "positive": 0.6,
      "negative": 0.2,
      "neutral": 0.2,
      "overall_sentiment": "positive"
    }
  }
}
```

## AI Chat Integration

### Base URL
```
https://api.example.com/codvid-ai/ai
```

### AI Chat Endpoints

#### AI Chat Response
- **Endpoint**: `POST /respond`
- **Purpose**: Get AI response with streaming capabilities
- **Request Body**:
```json
{
  "project_name": "My Project",
  "message": "Analyze my Instagram data",
  "stream": true
}
```
- **Response** (Streaming):
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
          "content": "AI response content",
          "timestamp": "timestamp"
        }
      }
    ]
  }
}
```

#### AI Streaming Test
- **Endpoint**: `POST /respond-stream-test`
- **Purpose**: Test endpoint for streaming functionality
- **Response**:
```json
{
  "a": "0\n"
}
```

## Data Models

### Profile Tracking Task
```json
{
  "task_id": "uuid-string",
  "user_id": "uuid-string",
  "target_profile": "string",
  "target_profile_data": {
    "scraped_posts": [],
    "icon_pic_url": "string",
    "username": "string",
    "full_name": "string",
    "biography": "string",
    "followers": "number",
    "following": "number",
    "posts_count": "number",
    "ig_tv_video_count": "number"
  },
  "is_competitor": "boolean",
  "created_at": "timestamp",
  "last_scraped": "timestamp",
  "next_scrape_due": "timestamp",
  "scrape_interval_days": "number",
  "status": "string",
  "task_type": "profile_tracking"
}
```

### Reel Tracking Task
```json
{
  "task_id": "uuid-string",
  "reel_url": "string",
  "reel_id": "string",
  "reel_data": {
    "caption": "string",
    "likes": "number",
    "comments": "number",
    "views": "number",
    "timestamp": "timestamp",
    "hashtags": ["string"],
    "mentions": ["string"],
    "top_comments": [],
    "sentiment_analysis": {
      "positive": "number",
      "negative": "number",
      "neutral": "number",
      "overall_sentiment": "string"
    }
  },
  "created_at": "timestamp",
  "last_scraped": "timestamp",
  "next_scrape_due": "timestamp",
  "scrape_interval_days": "number",
  "status": "string",
  "project_name": "string",
  "user_id": "uuid-string"
}
```

### Task Status Response
```json
{
  "task_id": "string",
  "is_processing": "boolean",
  "logs": [
    {
      "timestamp": "number",
      "message": "string"
    }
  ],
  "logs_count": "number",
  "requested_logs_count": "number",
  "latest_event": {
    "timestamp": "number",
    "message": "string"
  }
}
```

### JWT Token Requirements
All API requests (except authentication) require a valid JWT token:
```
Authorization: Bearer <jwt_token>
```

#### Token Format
- **Type**: JWT (JSON Web Token)
- **Algorithm**: HS256
- **Expiration**: Configurable (typically 24 hours)
- **Claims**: User ID, permissions, expiration time

#### Authentication Flow
1. **Signup/Login**: Obtain JWT token via authentication endpoints
2. **Include Token**: Add to all subsequent API requests
3. **Token Refresh**: Renew before expiration
4. **Logout**: Invalidate token (if supported)

## Error Handling

### Standard Error Response Format
```json
{
  "result": false,
  "message": "Error description"
}
```

### Common HTTP Status Codes

#### 200 - Success
- Request completed successfully
- Response body contains requested data

#### 201 - Created
- Resource created successfully
- Common for POST requests

#### 400 - Bad Request
- Invalid request data
- Missing required fields
- Invalid data format

#### 401 - Unauthorized
- Missing or invalid JWT token
- Token expired

#### 404 - Not Found
- Resource not found
- Task ID doesn't exist
- User doesn't have access

#### 409 - Conflict
- Resource already exists
- Task already being processed

#### 500 - Internal Server Error
- Server-side error
- Processing failure

## Real-time Monitoring

### Task Status Monitoring
The service provides real-time monitoring capabilities for tracking task progress:

#### Status Endpoints
- **Profile Tasks**: `/profile_tracking_task_status/<task_id>`
- **Reel Tasks**: Status available through project endpoints

#### Monitoring Features
- **Live Logs**: Real-time processing updates
- **Progress Tracking**: Current processing status
- **Error Reporting**: Immediate error notifications
- **Completion Events**: Task completion notifications

#### WebSocket Alternative
For real-time updates, consider implementing WebSocket connections to receive live task status updates.

### Implementation Strategies
- **Polling**: Regular status checks using GET requests to status endpoints
- **WebSocket**: Real-time updates via WebSocket connections (if available)
- **Event-Driven**: Server-sent events for live task progress updates
