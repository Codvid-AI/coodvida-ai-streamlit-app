# Server-Client Documentation for React client-side development

## Overview

This documentation covers the current system architecture with database integration, user authentication, and project management capabilities. The system has evolved from a local storage model to a hybrid local/cloud architecture with MongoDB backend and JWT authentication.

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

### Session Token Management
- Store the JWT token securely on the client side
- Include the token in all requests to protected endpoints
- Handle token expiration by re-authenticating the user
- The token contains the user's UUID and is used to identify the user on the server

---

## Structure of User Data

The system uses a hybrid architecture where the client maintains a local cache (`local_user_data`) synchronized with the server database.

### Database Structure (Server)

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
          },
          {
            "role": "assistant",
            "type": "event",
            "event_type": "tool_calling",
            "text": "searching the xxx ..."
          },
          {
            "role": "tool",
            "type": "text",
            "text": "--- results --- \n BLALBABLABLABLA"
          },
          {
            "role": "assistant",
            "type": "text",
            "text": "the tool call result is xxx."
          }
        ]
      }
    }
  }
}
```

### Local Cache Structure (Client)

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

**Key Changes from Original:**
- **Hybrid Architecture**: Client maintains local cache, server maintains database
- **Synchronization**: `mod_count` field tracks changes for sync validation
- **Authentication**: User data wrapped in database document with UUID and auth methods
- **Sync Mechanism**: `check_and_reload_project_data()` validates and syncs local cache with server

---

## Server-Client Core Communication Rules

When client **sends** a request to server with data, the data should be in this format:

```json
{
  "schema_version": "4.0",
  "data": {
    // key-value pair data inside here depending on the request
  }
}
```

This data is sent using HTTP(S) request.
Both POST and GET request methods are accepted.

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

**Key Changes:**
- Schema version updated from "3.0" to "4.0"
- Authentication token required in Authorization header for protected endpoints

---

## Server-Client Interaction Process

### 1. Request for AI Response (Chatting)

#### 1.1 Requesting from Client

When the user sends a new message, the client sends an HTTP(S) request to `{base_url}/codvid-ai/ai/respond`.

**Current Request Format:**
```json
{
  "schema_version": "4.0",
  "data": {
    "project_name": "DEMO_PROJECT_NAME",
    "message": {
      "role": "user",
      "type": "text",
      "text": "Hello, how are you?"
    }
  }
}
```

**Key Changes from Original:**
- Schema version updated to "4.0"
- Simplified data structure - only project name and message sent
- Server retrieves full user context from database
- Authentication token required in headers

#### 1.2 Receiving Data from Server

The server uses a stream to respond to the client. Every chunk of response contains data modifications that describe how to update the local `user_data`.

**Example Stream Response:**
```json
{
  "result": true,
  "response": {
    "data_mods": [
      {
        "key_path": ["projects", "demo_project", "chats"],
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

#### 1.3 How Client Works with `data_mods`

The client applies each `data_mod` to the local `user_data`. Each modification includes:

- **key_path**: Where in the data structure to update (array of keys, works like file path)
- **mode**:
  - `create`: create that key path and assign the value
  - `edit`: edit the value at that key path
  - `del`: delete the key-value pair
  - `append`: append the value to the list expressed by the key_path
- **value**: The new value (for create/edit/append)

**Synchronization Process:**
1. Client applies modifications to local cache
2. Server applies modifications to database and increments `mod_count`
3. Client validates sync using `check_and_reload_project_data()`
4. If `mod_count` mismatch detected, client reloads project data from server

#### 1.4 Complete Chat Flow Example

1. **User sends a message** (e.g., "hi")
2. **Client appends** the message to local cache
3. **Client sends** project name and message to backend
4. **Server retrieves** full user context from database
5. **Server responds** with AI's reply and data modifications stream
6. **Client applies** the modifications to local cache
7. **Client validates** synchronization with server
8. **UI updates** to show the new chat history

#### 1.5 Stream Response Format

The AI response endpoint returns a stream of JSON objects, each containing data modifications:

```json
{"result": true, "response": {"data_mods": [...]}}
{"result": true, "response": {"data_mods": [...]}}
{"result": true, "response": {"data_mods": [...]}}
```

Each chunk is a complete JSON object that should be parsed individually. The client should:
1. Parse each JSON chunk as it arrives
2. Apply the `data_mods` to the local cache
3. Update the UI to show progress
4. Handle any errors in individual chunks

---

## System Endpoints

### Health Check
**Endpoint:** `GET/POST /codvid-ai/ping`

**Description:** Simple health check endpoint to verify server connectivity.

**Request:** No request body required

**Success Response (200):**
```json
{
  "message": "pong"
}
```

**Usage:** Use this endpoint to test server connectivity before making authenticated requests.

---

## Project Management Endpoints

### Get Project List
**Endpoint:** `GET/POST /codvid-ai/project/get-project-list`

**Description:** Retrieves a list of all project names for the authenticated user.

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

**Error Response (401):**
```json
{
  "result": false,
  "message": "Unauthorized: invalid or expired token"
}
```

### Create Project
**Endpoint:** `POST /codvid-ai/project/create-project`

**Description:** Creates a new project with the specified name.

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

**Error Response (400):**
```json
{
  "result": false,
  "message": "Project already exists"
}
```

### Get Project Data
**Endpoint:** `GET/POST /codvid-ai/project/get-project-data`

**Description:** Retrieves the complete data for a specific project.

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

**Description:** Retrieves the modification count for a specific project (used for synchronization).

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

**Description:** Permanently deletes a project and all its data.

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

**Error Response (400/401):**
```json
{
  "result": false,
  "message": "Project not found"
}
```

---

## AI Endpoints

### AI Response (Streaming)
**Endpoint:** `POST /codvid-ai/ai/respond`

**Description:** Send a message to the AI and receive streaming responses with data modifications.

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

**Error Response (400/401):**
```json
{
  "result": false,
  "message": "Project not exists."
}
```

### AI Response Test (Streaming)
**Endpoint:** `POST /codvid-ai/ai/respond-stream-test`

**Description:** Test endpoint for streaming functionality (for development/testing).

**Request:**
```json
{
  "schema_version": "4.0",
  "data": {}
}
```

**Stream Response:** Returns test streaming data for development purposes.

---

## Types of Response

### I. Event Response

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

### II. Message Types

#### Text Messages
```json
{
  "role": "user",
  "type": "text",
  "text": "Hello, how are you?"
}
```

```json
{
  "role": "assistant",
  "type": "text",
  "text": "I'm doing well, thank you for asking!"
}
```

#### Tool Messages
```json
{
  "role": "tool",
  "type": "text",
  "text": "--- results --- \n BLALBABLABLABLA"
}
```

#### Event Messages
```json
{
  "role": "assistant",
  "type": "event",
  "event_type": "loading",
  "text": "Processing your request..."
}
```

```json
{
  "role": "assistant",
  "type": "event",
  "event_type": "info",
  "text": "I found 5 relevant reels for you"
}
```

```json
{
  "role": "assistant",
  "type": "event",
  "event_type": "show_reel_options",
  "options": ["REEL_ID_1", "REEL_ID_2", "REEL_ID_3"],
  "text": "Here are the reels I found:"
}
```

---

## Client-Side Functions

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

### User Management Functions
- `delete_account()` - Permanently delete user account

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

# Interactive chat
start_chat("my_new_project")
```

---

## Migration Notes

### For Existing Clients:
1. Update schema version to "4.0"
2. Implement authentication flow (signup/login endpoints)
3. Include JWT token in Authorization header for all requests
4. Update request format to only send project name and message
5. Handle new response format with data modifications
6. Implement synchronization validation with `mod_count`

### For New Clients:
1. Follow authentication flow documentation
2. Use simplified request format
3. Implement data modification application
4. Handle project management operations
5. Implement local cache synchronization

---

## Backward Compatibility

The new system is **not backward compatible** with the old local storage system. Clients must be updated to use the new authentication and database-backed architecture.

---

## Client Initialization and Setup

### Required Setup Steps

1. **Initialize Network Module:**
```python
import network
network.init("http://127.0.0.1:8080/")  # Replace with your server URL
```

2. **Import Client Functions:**
```python
from client import (
    login, signup, delete_account,
    get_project_list, create_project, delete_project, load_project_data,
    ai_interact, start_chat, print_chats
)
```

3. **Global Variables:**
```python
session_token = None  # Will be set after authentication
local_user_data = {}  # Local cache for user data
```

### Client State Management

The client maintains two key global variables:
- `session_token`: JWT token for authentication
- `local_user_data`: Local cache synchronized with server database

### Best Practices

1. **Always check authentication before making protected requests**
2. **Handle token expiration by re-authenticating**
3. **Validate project existence before operations**
4. **Use local cache for performance, but validate with server**
5. **Implement proper error handling for all network requests**

## Testing

Use the updated `client.py` in the demo client folder as a reference implementation for the new system architecture.

---

## Error Handling

### Common Error Messages

**Authentication Errors:**
- `"Unauthorized: missing session token while accessing non-public routes"` - Missing Authorization header
- `"Unauthorized: invalid or expired token"` - Invalid or expired JWT token
- `"Email is already linked to an account"` - Email already registered
- `"Email is not linked to an account"` - Email not found during login
- `"wrong password"` - Incorrect password during login
- `"missing auth_type!"` - Missing authentication type in request
- `"missing email!"` - Missing email in request
- `"missing password!"` - Missing password in request

**Schema Validation Errors:**
- `"Schema version mismatch. Expected 4.0, got 3.0"` - Wrong schema version
- `"Invalid JSON request body"` - Malformed JSON in request
- `"Missing data field"` - Missing data field in request

**Project Errors:**
- `"Project not exists"` - Project not found
- `"Project already exists"` - Project name already taken
- `"Project not found"` - Project not found during deletion

**Database Errors:**
- `"Database error: ..."` - Server-side database operation failed

**Network Errors:**
- Connection timeout - Server not reachable
- SSL certificate errors - HTTPS verification failed
- JSON parsing errors - Invalid response format

### Error Recovery Strategies

1. **Authentication Errors**: Re-authenticate the user
2. **Schema Errors**: Update client to use correct schema version
3. **Project Errors**: Verify project exists before operations
4. **Network Errors**: Implement retry logic with exponential backoff
5. **Stream Errors**: Handle individual chunk failures gracefully

## Complete Workflow Example

Here's a complete example of creating a project, loading it, and starting a chat:

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

# 5. Start AI interaction
message = {"role": "user", "type": "text", "text": "Hello!"}
ai_response = network.send_and_stream(
    "codvid-ai/ai/respond",
    content={"project_name": "my_new_project", "message": message},
    session_token=session_token
)
``` 