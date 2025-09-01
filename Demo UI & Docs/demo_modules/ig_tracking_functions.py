# core functions
from demo_modules import network, client

def create_tracking_task(target_profile: str, is_competitor: bool = False):
    """Create a new Instagram tracking task"""
    response = network.send(
        "/codvid-ai/ig-tracking/create_profile_tracking_task",
        content={
            "target_profile": target_profile,
            "is_competitor": is_competitor
        },
        session_token=client.session_token
    )
    
    result = response.get_dict()
    if result.get("result"):
        task_id = result["response"]["task_id"]
        print(f"✓ Created tracking task for @{target_profile}")
        print(f"  Task ID: {task_id}")
        print(f"  Type: {'Competitor' if is_competitor else 'Own Profile'}")
        return task_id
    else:
        print(f"❌ Failed to create task: {result.get('message', 'Unknown error')}")
        return None

def get_tracking_tasks(verbose=False):
    """Get all tracking tasks for the current user"""
    response = network.send(
        "/codvid-ai/ig-tracking/get_profile_tracking_tasks",
        session_token=client.session_token,
        method="GET"  # Fixed: Use GET method
    )
    
    if verbose:
        response.print()
    result = response.get_dict()
    if result and result.get("result"):
        tasks = result["response"]["tasks"]
        print(f"✓ Found {len(tasks)} tracking tasks")
        return tasks
    else:
        print(f"❌ Failed to get tasks: {result.get('message', 'Unknown error') if result else 'No response'}")
        return []

def get_task_details(task_id: str, verbose=False):
    """Get detailed information about a specific tracking task"""
    response = network.send(
        f"/codvid-ai/ig-tracking/get_profile_tracking_task/{task_id}",
        session_token=client.session_token,
        method="GET"  # Fixed: Use GET method
    )
    if verbose:
        response.print()
    result = response.get_dict()
    if result and result.get("result"):
        return result["response"]["task"]
    else:
        print(f"❌ Failed to get task details: {result.get('message', 'Unknown error') if result else 'No response'}")
        return None

def force_scrape_task(task_id: str):
    """Force immediate scraping of a tracking task"""
    print(f"🔄 Initiating scrape for task {task_id}...")
    response = network.send(
        f"/codvid-ai/ig-tracking/force_scrape_profile_tracking_task/{task_id}",
        session_token=client.session_token,
        method="POST"  # Correct: Use POST method
    )
    
    result = response.get_dict()
    if result and result.get("result"):
        print("✓ Scraping initiated successfully!")
        return True
    else:
        print(f"❌ Sever failed to initiate scraping: {result.get('message', 'Unknown error') if result else 'No response'}")
        return False

def get_sentiment_summary(task_id: str):
    """Get sentiment analysis summary for a tracking task"""
    response = network.send(
        f"/codvid-ai/ig-tracking/sentiment_summary/{task_id}",
        session_token=client.session_token,
        method="GET"  # Fixed: Use GET method
    )
    
    result = response.get_dict()
    if result and result.get("result"):
        return result["response"]["sentiment_summary"]
    else:
        print(f"❌ Failed to get sentiment summary: {result.get('message', 'Unknown error') if result else 'No response'}")
        return None

def delete_tracking_task(task_id: str):
    """Delete a tracking task"""
    response = network.send(
        f"/codvid-ai/ig-tracking/delete_profile_tracking_task/{task_id}",
        session_token=client.session_token,
        method="DELETE"  # Fixed: Use DELETE method
    )
    
    result = response.get_dict()
    if result and result.get("result"):
        print("✓ Task deleted successfully!")
        return True
    else:
        print(f"❌ Failed to delete task: {result.get('message', 'Unknown error') if result else 'No response'}")
        return False

print("✓ Instagram tracking functions loaded")





#### selector
def smart_task_selector(auto_select_first=False):
    """
    Smart task selection that can auto-select or prompt user to choose
    
    Args:
        auto_select_first (bool): If True and only one task exists, auto-select it
    
    Returns:
        str: Selected task ID or None if no selection made
    """
    tasks = get_tracking_tasks()
    if not tasks or len(tasks) == 0:
        print("❌ No tasks found on server.")
        return None
    
    # Auto-select if only one task and auto_select_first is True
    if len(tasks) == 1 and auto_select_first:
        task = tasks[0]
        task_id = task.get('_id')
        profile = task.get('target_profile', 'unknown')
        ttype = 'Competitor' if task.get('is_competitor') else 'Own Profile'
        print(f"✅ Auto-selected only available task: @{profile} ({ttype})")
        return task_id
    
    # Show available tasks
    print("🎯 Select a task from server:")
    print("-" * 40)
    for idx, task in enumerate(tasks):
        profile = task.get('target_profile', 'unknown')
        ttype = 'Competitor' if task.get('is_competitor') else 'Own Profile'
        status = task.get('status', 'unknown')
        last_scraped = task.get('last_scraped', 'Never')
        print(f"  {idx+1}. @{profile} ({ttype})")
        print(f"      Status: {status}, Last scraped: {last_scraped}")
    
    # Get user selection
    try:
        selection = int(input(f"\nSelect task number (1-{len(tasks)}): "))
        if 1 <= selection <= len(tasks):
            selected_task = tasks[selection-1]
            task_id = selected_task.get('_id')
            profile = selected_task.get('target_profile', 'unknown')
            print(f"✅ Selected: @{profile} (ID: {task_id})")
            return task_id
        else:
            print("❌ Invalid selection.")
            return None
    except (ValueError, KeyboardInterrupt):
        print("❌ Invalid input or cancelled.")
        return None

print("✓ Smart task selector function loaded")

def create_reel_tracking_task(project_name: str, reel_url: str, scrape_interval_days: int = 2):
    """Create a new Instagram reel tracking task for a project"""
    data = {
        "project_name": project_name,
        "reel_url": reel_url,
        "scrape_interval_days": scrape_interval_days
    }
    
    response = network.send(
        "/codvid-ai/ig-tracking/create_reel_task",
        content=data,
        session_token=client.session_token
    )
    
    result = response.get_dict()
    if result and result.get("result"):
        task_id = result["response"]["task_id"]
        print(f"✓ Created reel tracking task for project '{project_name}'")
        print(f"  Task ID: {task_id}")
        print(f"  Reel URL: {reel_url}")
        return task_id
    else:
        print(f"❌ Failed to create reel tracking task: {result.get('message', 'Unknown error') if result else 'No response'}")
        return None

def get_project_reel_tasks(project_name: str, verbose=False):
    """Get all reel tracking tasks for a specific project"""
    data = {"project_name": project_name}
    
    response = network.send(
        "/codvid-ai/ig-tracking/get_project_reel_tasks",
        content=data,
        session_token=client.session_token,
        method="POST"
    )
    
    if verbose:
        response.print()
    result = response.get_dict()
    if result and result.get("result"):
        tasks = result["response"]["tasks"]
        print(f"✓ Found {len(tasks)} reel tracking tasks for project '{project_name}'")
        return tasks
    else:
        print(f"❌ Failed to get project reel tasks: {result.get('message', 'Unknown error') if result else 'No response'}")
        return []

def force_scrape_reel_task(task_id: str):
    """Force immediate scraping of a reel tracking task"""
    response = network.send(
        f"/codvid-ai/ig-tracking/force_scrape_reel/{task_id}",
        session_token=client.session_token,
        method="POST"
    )
    
    result = response.get_dict()
    if result and result.get("result"):
        print(f"✓ Successfully force scraped reel tracking task {task_id}")
        return True
    else:
        print(f"❌ Failed to force scrape reel task: {result.get('message', 'Unknown error') if result else 'No response'}")
        return False
