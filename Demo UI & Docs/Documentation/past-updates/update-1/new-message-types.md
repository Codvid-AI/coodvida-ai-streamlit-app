# What's new in this backend doc update:

1. rename:
    `"type": "status"` -> `"type": "event"`
    `"status":` ->  `"event_type":`

-  original

```json
{
    // to be more responsive to client
    "role": "assistant",
    "type": "status",
    "status": "tool_calling",
    "text": "searching the xxx ..."
},
```

- now

```json
{
    // to be more responsive to client
    "role": "assistant",
    "type": "event",
    "event_type": "tool_calling",
    "text": "searching the xxx ..."
},
```

2. Event type response

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







---

## To-do:

- make memory/project editing more safe
