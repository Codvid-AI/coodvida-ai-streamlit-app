

# Server-Client Documentation for React client-side development

## Structure of User-data 

The client.ipynb maintains a user data object, stored as `user_data`.
Here is a demo user data format expressed in json,  with some comments.

```json
user_data = {
  // projcet structure version
  "version": "2.0",
  
  // global part of user data
  "global_data": {
      // memory controlled by AI
      "ai_memory": {},
      
      // reflections stored after AI scrapping the ig comments and see
      "video_reflections": {
          
          // ... reflections ...
          "DEMO-REEL-ID": {
              "comments": [
                  "hihihi"
              ],
              "reflection": "DEMO-REFLECTION"
          },
          "DEMO-REEL-ID": {
              "comments": [
                  "hehehe"
              ],
              "reflection": "DEMO-REFLECTION"
          }
          // ... reflections ...
          
      }
  },// (end of global data)
    
  // project specific data of the user
  "projects": {
    // ... projects ...
    
    "DEMO_PROJECT_NAME": {
      // Structure version of the project
      "version": "1.0",
        
      // Creation date
      "date": "18-7-2025",
        
      // project info. Can act like a stable notebook,
      // or as an info for searching.
      "project_info": {
          "description": "DEMO",
          "keywords": ["DEMO", "DEMO"]
      },
      // memory controlled by AI (project-specific)
      "ai_memory": {
          "DEMO_MEMORY_NAME1": "DEMO_TEXT",
          "DEMO_MEMORY_NAME2": "DEMO_TEXT"
      },
      // list of chats of different roles(msg types)
      "chats": [
          // ... chats ...
          {
              "role": "user", // user
              "type": "text",
              "text": "blablablablabla",
          },
          {
              "role": "assistant", // ai
              "type": "text",
              "text": "blablablablabla",
          },
          {
              // to be more responsive to client
              "role": "assistant",
              "type": "event",
              "event_type": "tool_calling",
              "text": "searching the xxx ..."
          },
          {
              "role": "tool", // hidden for now.
              "type": "text",
              "text": "--- results --- \n BLALBABLABLABLA"
          },
          {
              "role": "assistant",
              "type": "text",
              "text": "the tool call result is xxx."
          }
          // ... chats ...
      ]

    }// (end of this demo project)
    
    // ... projects ...

  } // (end of global data)
}
```

An empty user data example is shown in the client.ipynb

---

## Server-Client core communication rules

Went client **send** a request to server with a data, the data should be in this format:

```json
{
  // 1. json schema version
  // this is to ensure server and client are using
  // the same version of request structure, same language
  "schema_version": "3.0",
  
  // 2. key-value pair data inside here depending on the request
  "data": {
      // "aaa": "aaa"
  }
}
```

This data is sent using http(s) request.
Both POST and GET request methods are accepted.

Server response:

```json
{
  // indicate whether the request is successful
  "result": true,
  
  // key-value pair data inside here as the returned data
  "response": {
      // "xxx": "xxx"
  }
}
```

Server response when smthing goes wrong:

```json
{
  // indicate whether the request is successful
  "result": false,
  
  // key-value pair data inside here as the returned data
  "message": "Request schema version is invalid. Please update the app."
}
```



---

## Server-client interaction process:

### 1. Request for AI response (chatting)

1. **Requesting from client**

- When the user click to sends a new message, the client sends an http(s) request to
    `{base_url}/codvid-ai/ai/respond`.
    The base url is shown in the .ipynb

- And the request data will be sent like this,
    following the core communication rules mentioned above:

```json
{

  "schema_version": "3.0",
  
  // its just like a user data dict but with uneccessary parts cropped out
  "data": {
    "global_data": { "ai_memory": {} },
    "projects": {
      "DEMO_PROJECT_NAME_1": {
        "version": "1.0",
        "ai_memory": {},
        "chats": [ ... ],
        "project_info": { ... }
      }
      // other unrelated projects are not included here
    }
  }

}
```

2. **Receiving Data from the Server**

- The server will use a stream to respond to the client. Every chunk of response returned from the stream has a list of data modifications that describe how to update the local `user_data`.

- The  `network.py` >> `send_and_stream()` function send requests to server and return a stream of server response.
    The  `client.ipynb` >> `ai_interact()` function handles the stream and pass every streamed json response into the `client.ipynb` >> `apply_user_data_mods()` function to apply change on the user/project data and reprint the chat.

- Example of a single response returned from the stream:

```json
{
  "result": true,
  "response": {
      // here is the data modification list
      // user data should be modified according to the commands
    "data_mods": [
      {
        "key_path": ["projects", "demo_project", "chats"],
        "mode": "append",
        // appending the whole dictionary (value) to the "chats"
        "value": { "role": "assistant", "type": "text", "text": "Hello!" }
        
        // see how it works in the following paragraph
      },
      // ... other mods ...
    ]
  }
}
```

3. **How does the client work with the `data_mods`?**

- The client applies each `data_mod` to the local `user_data`. Each modification includes:

    - **key_path**: Where in the data structure to update (array of keys, works like file path / node path)
        - **mode**:
            - `create`: create that key path and assigned the value to there
            - `edit`: edit the value at that key path
            - `del`: delete the key-value pair
                - if path is "a", "b", "c", then c is deleted

            - `append`: append the value to the list expressed by the key_path
                - Ie, the path is "path", "to", "list", then the value is appended to the list.


    - **value**: The new value (for create/edit/append)


- **=== A Compact Chat Flow Example ===**
    1. **User sends a message** (e.g., "hi")

    2. **Client appends** the message to `user_data["projects"]["demo_project"]["chats"]`

    3. **Client sends** the updated context to the backend

    4. **Server responds** with AI's reply and any data modifications stream

    5. **Client applies** the modifications (e.g., appends the assistant's reply to the chat)

    6. **UI updates** to show the new chat history


<blockquote class="instagram-media" data-instgrm-captioned data-instgrm-permalink="https://www.instagram.com/reel/DMShe2_zyeH/?utm_source=ig_embed&amp;utm_campaign=loading" data-instgrm-version="14" style=" background:#FFF; border:0; border-radius:3px; box-shadow:0 0 1px 0 rgba(0,0,0,0.5),0 1px 10px 0 rgba(0,0,0,

---



## Types of response

### I. Event response

- `event_type`:
    - loading
    - info
    - show_reel_options
- Examples:

```json
{
    "role": "assistant",
    "type": "event",
    "event_type": "tool_calling",
    "text": "searching reels related to xx food restaurant"
},
{
    // for client side to show ig reels options after searching
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

