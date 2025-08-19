# Reel Tracking Service Update - January 2025

This update introduces a new **Reel Tracking Service** that allows users to monitor specific Instagram reels within their projects, providing automated performance tracking and sentiment analysis for individual video content.

## Overview

The Reel Tracking Service is a project-based Instagram monitoring system that tracks individual reels rather than entire profiles. This service provides granular insights into specific video performance, making it ideal for content creators, marketers, and businesses who want to analyze the success of particular video content.

## Key Features

### 1. **Project-Based Organization**
- **Project-Specific Tasks**: Each reel tracking task belongs to a specific project
- **Organized Workflow**: Keep reel tracking separate from profile tracking
- **Project Context**: All reel data is stored within project structures

### 2. **Individual Reel Monitoring**
- **Single Reel Focus**: Track specific Instagram reel URLs
- **Performance Metrics**: Monitor likes, comments, views, and engagement
- **Content Analysis**: Analyze captions, hashtags, and mentions

### 3. **Automated Data Collection**
- **Scheduled Scraping**: Automatic updates every 2 days (configurable)
- **Background Processing**: Server handles all data collection automatically
- **Real-time Access**: Query updated data anytime via API

### 4. **AI-Powered Sentiment Analysis**
- **Comment Sentiment**: Analyzes reel comments for positive/negative/neutral sentiment
- **Percentage Breakdown**: Get exact sentiment distribution percentages
- **Overall Assessment**: Receive overall sentiment determination for each reel

## Service Limitations

### 1. **Instagram API Constraints**
- **Rate Limiting**: Instagram has strict rate limits that may affect scraping frequency
- **Access Restrictions**: Some reels may be private or have restricted access
- **Data Availability**: Not all engagement metrics may be available for every reel

### 2. **Scraping Limitations**
- **Comment Depth**: Limited to top comments due to Instagram's structure
- **Historical Data**: Can only access currently available data, not historical trends
- **Content Changes**: Reels may be deleted or modified, affecting data consistency

### 3. **Project Dependencies**
- **Project Required**: Must have an existing project to create reel tracking tasks
- **User Isolation**: Users can only access reel tracking tasks within their own projects
- **Project Lifecycle**: Deleting a project removes all associated reel tracking tasks

## API Endpoints

The Reel Tracking Service provides 4 new REST API endpoints under `/codvid-ai/ig-tracking/`:

### 1. **Create Reel Tracking Task**
**Endpoint:** `POST /codvid-ai/ig-tracking/create_reel_task`

**Request Body:**
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

### 2. **Get Project Reel Tasks**
**Endpoint:** `POST /codvid-ai/ig-tracking/get_project_reel_tasks`

**Request Body:**
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

### 3. **Force Scrape Reel Task**
**Endpoint:** `POST /codvid-ai/ig-tracking/force_scrape_reel/{task_id}`

**Description:** Manually trigger immediate scraping of a reel tracking task

**Response:**
```json
{
    "result": true,
    "message": "Reel tracking task scraping completed successfully"
}
```

### 4. **Delete Reel Tracking Task**
**Endpoint:** `DELETE /codvid-ai/ig-tracking/delete_reel_task/{task_id}`

**Description:** Remove a reel tracking task from a project

## Data Structure

### Reel Tracking Task Object
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

### Key Fields Explanation
- **`reel_id`**: Extracted Instagram reel identifier
- **`reel_data`**: Current performance metrics and content analysis
- **`timestamp`**: Unix epoch timestamp in seconds
- **`sentiment_analysis`**: AI-powered sentiment breakdown of comments
- **`top_comments`**: Analyzed comments with sentiment classification

## Authentication & Middleware

### JWT Authentication Required
All reel tracking endpoints require JWT authentication:
```
Authorization: Bearer <your_jwt_token>
```

### Schema Version Validation
All requests must use schema version "4.0":
```json
{
    "schema_version": "4.0",
    "data": { ... }
}
```

### User Data Isolation
- Users can only access reel tracking tasks within their own projects
- Project ownership is verified through JWT token validation
- Middleware automatically extracts user context from authentication

## Client Integration Guide

### 1. **Prerequisites**
- Valid user account with JWT authentication
- At least one project created
- Instagram reel URLs to track

### 2. **Implementation Steps**
1. **Create Project**: Ensure you have a project to organize reel tracking tasks
2. **Create Task**: POST to `/create_reel_task` with project name and reel URL
3. **Monitor Progress**: Use `/get_project_reel_tasks` to check task status
4. **Force Updates**: Use `/force_scrape_reel/{task_id}` for immediate data refresh
5. **Analyze Results**: Process the `reel_data` and `sentiment_analysis` fields

### 3. **Error Handling**
- **400 Bad Request**: Missing required fields or invalid data format
- **401 Unauthorized**: Invalid or expired JWT token
- **404 Not Found**: Task not found or access denied
- **500 Internal Server Error**: Server-side processing errors

## Demo Implementation

A complete interactive demo notebook is provided:
- **File**: `Demo-UI-Reel-Tracking.ipynb`
- **Features**: Step-by-step reel tracking implementation
- **Examples**: Complete API usage patterns
- **Best Practices**: Recommended integration approaches

## Performance Considerations

### 1. **Scraping Frequency**
- **Default Interval**: 2 days between automatic scrapes
- **Configurable**: Can be adjusted per task (minimum 1 day)
- **Rate Limiting**: Respects Instagram's rate limits

### 2. **Data Storage**
- **Project-Based**: Data stored within project structures
- **Efficient Queries**: Optimized for project-specific data retrieval
- **Automatic Cleanup**: Tasks removed when projects are deleted

### 3. **Scalability**
- **Background Processing**: Server handles scraping without blocking client requests
- **User Isolation**: Each user's tasks processed independently
- **Project Organization**: Efficient data organization for multiple projects

## Migration from Profile Tracking

### Key Differences
1. **Scope**: Individual reels vs. entire profiles
2. **Organization**: Project-based vs. user-level
3. **Data Structure**: Reel-specific metrics vs. profile-wide analysis
4. **Use Cases**: Content performance vs. competitor monitoring

### When to Use Each Service
- **Profile Tracking**: Monitor competitor accounts, track brand mentions
- **Reel Tracking**: Analyze specific content performance, track campaign success

## What's Next

### Immediate Actions
1. **Review API Documentation**: Understand endpoint requirements and limitations
2. **Try the Demo**: Run through the interactive demo notebook
3. **Create Test Tasks**: Start with simple reel tracking in existing projects
4. **Integrate into Workflow**: Add reel tracking to your content analysis pipeline

### Future Enhancements
- **Batch Operations**: Create multiple reel tracking tasks at once
- **Advanced Analytics**: Trend analysis and performance comparisons
- **Export Features**: Data export in various formats
- **Integration APIs**: Connect with other analytics platforms

## Support Resources

- **Complete Demo**: `Demo-UI-Reel-Tracking.ipynb` with all examples
- **API Reference**: Detailed endpoint documentation
- **Error Handling**: Common issues and solutions
- **Best Practices**: Recommended usage patterns

The Reel Tracking Service provides powerful Instagram content analysis capabilities through simple REST API calls, making it easy to integrate into any client application for content performance monitoring and sentiment analysis.
