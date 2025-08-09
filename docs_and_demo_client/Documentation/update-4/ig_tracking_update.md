# Instagram Tracking Service Update - August 2025

This update introduces a new endpoint for dynamically adjusting the scraping interval of existing Instagram tracking tasks and clarifies the data format for task information.

## New Endpoint: Update Scraping Interval

A new endpoint has been added to allow users to modify the frequency at which Instagram profiles are scraped. This provides greater flexibility in managing tracking tasks.

**Endpoint:** `PUT /ig-tracking/update_scrape_interval/{task_id}` or `POST /ig-tracking/update_scrape_interval/{task_id}`
**Description:** Updates the `scrape_interval_days` for a given tracking task.
**Method:** `PUT` or `POST`
**Request Body Example:**
```json
{
    "schema_version": "4.0",
    "data": {
        "scrape_interval_days": 0.5
    }
}
```
**Parameters:**
- `task_id` (path parameter): The unique identifier of the tracking task.
- `user_id` (from authentication context): The ID of the user who owns the task.
- `scrape_interval_days` (request body): The new interval in days (integer or float, must be > 0).

**Behavior:**
- If `last_scraped` exists for the task, `next_scrape_due` will be recalculated based on `last_scraped + new_interval_days`.
- If `last_scraped` does not exist, `next_scrape_due` will be set based on `current_time + new_interval_days`.

## Instagram Tracking Task Information Format Update

To standardize time-related data and improve consistency, the following fields in the Instagram tracking task information format have been updated to use **Unix epoch timestamps in seconds (integer)**:

- `created_at`: The timestamp when the tracking task was initially created.
- `last_scraped`: The timestamp of the last successful scrape for this task. This field will be `None` if the task has not been scraped yet.
- `next_scrape_due`: The timestamp indicating when the next scrape for this task is scheduled.

This snippet illustrates the structure of a single Instagram tracking task object as returned by the API (e.g., from `/api/ig_tracking/get_tasks` or `/api/ig_tracking/get_task/{task_id}`).

**Example Task Info Snippet:**
```json
{
    "schema_version": "4.0",
    "data": {
        "_id": "your_task_id_here",
        "user_id": "user123",
        "target_profile": "instagram_profile_name",
        "is_competitor": false,
        "created_at": 1678886400,
        "last_scraped": 1679059200,
        "next_scrape_due": 1679232000,
        "scrape_interval_days": 2,
        "status": "active",
        "scraped_posts": []
    }
}