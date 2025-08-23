import streamlit as st
from datetime import datetime
import time

def smart_task_selector(api_client, auto_select_first=False):
    """
    Smart task selection that can auto-select or prompt user to choose
    Based on the notebook functionality
    """
    tasks = api_client.get_tracking_tasks()
    if not tasks or len(tasks) == 0:
        st.error("No tasks found on server.")
        return None
    
    # Auto-select if only one task and auto_select_first is True
    if len(tasks) == 1 and auto_select_first:
        task = tasks[0]
        task_id = task.get('_id')
        profile = task.get('target_profile', 'unknown')
        ttype = 'Competitor' if task.get('is_competitor') else 'Own Profile'
        st.success(f"Auto-selected only available task: @{profile} ({ttype})")
        return task_id
    
    # Show available tasks
    st.markdown('<h4 class="main-header">Select a task from server:</h4>', unsafe_allow_html=True)
    st.markdown("---")
    
    task_options = {}
    for idx, task in enumerate(tasks):
        profile = task.get('target_profile', 'unknown')
        ttype = 'Competitor' if task.get('is_competitor') else 'Own Profile'
        status = task.get('status', 'unknown')
        last_scraped = task.get('last_scraped', 'Never')
        
        option_key = f"{idx+1}. @{profile} ({ttype})"
        task_options[option_key] = task['_id']
        
        st.markdown(f"**{option_key}**")
        st.caption(f"Status: {status}, Last scraped: {last_scraped}")
    
    # Get user selection
    selected_option = st.selectbox(
        f"Select task number (1-{len(tasks)}):",
        options=list(task_options.keys()),
        index=None,
        placeholder="Choose a task..."
    )
    
    if selected_option:
        task_id = task_options[selected_option]
        profile = selected_option.split('. ')[1].split(' (')[0]
        st.success(f"Selected: @{profile} (ID: {task_id})")
        return task_id
    
    return None

def show_dashboard(api_client):
    """Show the main dashboard with user profile and competitor tracking"""
    
    # Page header
    st.markdown('<h1 class="brand-title">CodVid.AI</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="brand-subtitle">Instagram Analytics Dashboard</h2>', unsafe_allow_html=True)
    
    # Get tracking tasks
    tasks = api_client.get_tracking_tasks()
    
    # Top section: Left (Your Profile) and Right (Quick Actions)
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Your Profile Section (Left)
        st.markdown('<h3 class="main-header">Your Profile</h3>', unsafe_allow_html=True)
        
        # Find own profile (non-competitor)
        own_profile = None
        if tasks:
            own_profile = next((task for task in tasks if not task.get('is_competitor', False)), None)
        
        if own_profile:
            # Display own profile information
            st.markdown(f"**Username:** @{own_profile['target_profile']}")
            st.markdown(f"**Status:** {own_profile.get('status', 'Active')}")
            
            if own_profile.get('last_scraped'):
                last_scraped = datetime.fromtimestamp(own_profile['last_scraped'])
                st.markdown(f"**Last Updated:** {last_scraped.strftime('%Y-%m-%d %H:%M')}")
            else:
                st.markdown("**Last Updated:** Never")
            
            # Add View Details and Delete buttons for own profile
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button(
                    "View Details", 
                    key="own_profile_view", 
                    use_container_width=True,
                    help="Click to view your profile analytics"
                ):
                    st.session_state.current_profile = own_profile
                    st.session_state.current_page = 'profile_details'
                    st.rerun()
            
            with col_btn2:
                if st.button(
                    "Delete Task", 
                    key="own_profile_delete", 
                    use_container_width=True,
                    help="Delete your profile tracking task"
                ):
                    if api_client.delete_tracking_task(own_profile['_id']):
                        st.success("Own profile task deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete own profile task")
        else:
            st.info("No own profile found. Create one below.")
    
    with col2:
        # Quick Actions Section (Right)
        st.markdown('<h3 class="main-header">Quick Actions</h3>', unsafe_allow_html=True)
        
        # Button 1: Project Chat
        if st.button("Project Chat", use_container_width=True, key="quick_chat"):
            # Get projects and go directly to the latest one
            projects = api_client.get_project_list()
            if projects:
                # Use the last project as the latest (most recently created)
                latest_project = projects[-1]
                
                # Ensure project data is loaded into cache before navigating
                if api_client.ensure_project_loaded(latest_project):
                    st.session_state.current_project = latest_project
                    st.session_state.current_page = 'project_chat'
                    st.rerun()
                else:
                    st.error(f"Failed to load project data for '{latest_project}'. Please try again.")
            else:
                st.error("No projects found. Please create a project first.")
        
        # Button 2: Add Task
        if st.button("Add Task", use_container_width=True, key="quick_add"):
            st.session_state.show_add_task = True
            st.rerun()
        
        # Button 3: Logout
        if st.button("Logout", use_container_width=True, key="quick_logout"):
            st.session_state.authenticated = False
            st.session_state.session_token = None
            st.session_state.current_page = 'login'
            st.rerun()
    
    # Show add task form directly under Quick Actions if requested
    if st.session_state.get('show_add_task', False):
        st.markdown("---")
        st.markdown('<h4 class="main-header">Create New Tracking Task</h4>', unsafe_allow_html=True)
        
        with st.form("create_task_form"):
            profile_name = st.text_input("Instagram Username", placeholder="e.g., foodxtaste")
            is_competitor = st.checkbox("Track as Competitor (uncheck for Own Profile)")
            
            # Add scraping interval settings
            st.markdown('<h5 class="main-header">Scraping Settings</h5>', unsafe_allow_html=True)
            scrape_interval = st.number_input(
                "Scrape Interval (days)", 
                min_value=0.5, 
                max_value=30.0, 
                value=2.0,
                step=0.5,
                help="How often to automatically scrape this profile (0.5 = 12 hours, 1 = daily, 7 = weekly)"
            )
            
            st.caption(f"Profile will be scraped every {scrape_interval} days")
            
            col_submit, col_cancel = st.columns(2)
            with col_submit:
                submit = st.form_submit_button("Create Task", use_container_width=True)
            with col_cancel:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.show_add_task = False
                    st.rerun()
            
            if submit:
                if profile_name:
                    task_id = api_client.create_tracking_task(profile_name, is_competitor)
                    if task_id:
                        # Update the scrape interval after creation
                        if api_client.update_scrape_interval(task_id, scrape_interval):
                            st.success(f"Created tracking task for @{profile_name} with {scrape_interval}-day interval")
                        else:
                            st.success(f"Created tracking task for @{profile_name} (using default interval)")
                        st.session_state.show_add_task = False
                        st.rerun()
                    else:
                        st.error("Failed to create tracking task")
                else:
                    st.error("Please enter a profile name")
    
    st.markdown("---")
    
    # Environment selector (based on notebooks)
    st.sidebar.subheader("Environment Settings")
    from config import Config
    current_env = Config.get_environment()
    new_env = st.sidebar.selectbox(
        "API Environment:",
        options=["development", "local", "production", "betamale"],
        index=["development", "local", "production", "betamale"].index(current_env) if current_env in ["development", "local", "production", "betamale"] else 0
    )
    
    if new_env != current_env:
        if st.sidebar.button("Update Environment"):
            Config.set_environment(new_env)
            st.sidebar.success(f"Environment updated to: {new_env}")
            st.rerun()
    
    st.sidebar.markdown(f"**Current API:** {Config.get_api_url()}")
    
    # Competitor Profiles Grid
    if tasks:
        competitor_profiles = [task for task in tasks if task.get('is_competitor', False)]
        if competitor_profiles:
            st.markdown('<h2 class="main-header">Competitor Profiles</h2>', unsafe_allow_html=True)
            
            # Create 2-column grid for competitor profiles
            cols = st.columns(2)
            for idx, task in enumerate(competitor_profiles):
                col_idx = idx % 2
                with cols[col_idx]:
                    # Create detailed profile card
                    with st.container():
                        st.markdown(f"**@{task['target_profile']}**")
                        st.caption(f"Status: {task.get('status', 'Active')}")
                        
                        if task.get('last_scraped'):
                            last_scraped = datetime.fromtimestamp(task['last_scraped'])
                            st.caption(f"Last Updated: {last_scraped.strftime('%Y-%m-%d %H:%M')}")
                        else:
                            st.caption("Last Updated: Never")
                        
                        # Add View Details and Delete buttons
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button(
                                "View Details", 
                                key=f"profile_{task['_id']}", 
                                use_container_width=True,
                                help=f"Click to view analytics for @{task['target_profile']}"
                            ):
                                # Handle click to view profile details
                                st.session_state.current_profile = task
                                st.session_state.current_page = 'profile_details'
                                st.rerun()
                        
                        with col_btn2:
                            if st.button(
                                "Delete Task", 
                                key=f"delete_{task['_id']}", 
                                use_container_width=True,
                                help=f"Delete tracking task for @{task['target_profile']}"
                            ):
                                if api_client.delete_tracking_task(task['_id']):
                                    st.success(f"Deleted tracking task for @{task['target_profile']}")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to delete tracking task for @{task['target_profile']}")
        else:
            st.info("No competitor profiles found. Add some above!")
    else:
        st.info("No tracking tasks found. Create your first task above!")
    
    # Task Monitoring Section
    if tasks:
        st.markdown("---")
        st.markdown('<h2 class="main-header">Task Monitoring</h2>', unsafe_allow_html=True)
        
        # Task selector
        task_labels = []
        id_to_label = {}
        current_idx = 0
        
        for idx, task in enumerate(tasks):
            profile = task.get('target_profile', 'Unknown')
            task_type = '🏢 Competitor' if task.get('is_competitor') else '👤 Own Profile'
            label = f"@{profile} ({task_type})"
            task_labels.append(label)
            id_to_label[task.get('_id')] = label
            
            # Set current index if this is the monitored task
            if st.session_state.get('monitor_profile_task_id') == task.get('_id'):
                current_idx = idx
        
        if task_labels:
            choice = st.selectbox("Choose a task to monitor:", options=task_labels, index=current_idx)
            for tid, lbl in id_to_label.items():
                if lbl == choice:
                    st.session_state.monitor_profile_task_id = tid
                    selected_profile_task_id = tid
                    break
            
            # Show enhanced status with logs
            st.subheader("📊 Task Processing Status")
            
            # Add logs count selector
            col1, col2 = st.columns([1, 3])
            with col1:
                logs_to_show = st.selectbox(
                    "Logs to show:",
                    options=[5, 10, 20, 50, 100],
                    index=1,  # Default to 10
                    key=f"logs_count_{selected_profile_task_id}"
                )
            with col2:
                if st.button("🔄 Refresh Status", key=f"refresh_status_{selected_profile_task_id}", type="primary"):
                    st.rerun()
            
            # Get enhanced status with selected logs count
            status = api_client.get_task_status(selected_profile_task_id, logs_count=logs_to_show)
            
            if status:
                # Show task summary at the top
                st.markdown('<h4 class="main-header">Task Summary</h4>', unsafe_allow_html=True)
                
                # Get task details for display
                task_details = None
                for task in tasks:
                    if task['_id'] == selected_profile_task_id:
                        task_details = task
                        break
                
                if task_details:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**Profile:** @{task_details.get('target_profile', 'Unknown')}")
                    with col2:
                        task_type = '🏢 Competitor' if task_details.get('is_competitor') else '👤 Own Profile'
                        st.markdown(f"**Type:** {task_type}")
                    with col3:
                        status_text = "⏳ Processing" if status.get('is_processing') else "✅ Idle/Completed"
                        st.markdown(f"**Status:** {status_text}")
                    
                    # Show additional task information
                    col1, col2 = st.columns(2)
                    with col1:
                        if task_details.get('last_scraped'):
                            last_scraped = datetime.fromtimestamp(task_details['last_scraped'])
                            st.markdown(f"**Last Scraped:** {last_scraped.strftime('%Y-%m-%d %H:%M')}")
                        else:
                            st.markdown("**Last Scraped:** Never")
                        
                        # Show scrape interval
                        interval = task_details.get('scrape_interval_days', 2)
                        interval_text = f"Every {interval} days"
                        if interval == 1:
                            interval_text = "Daily"
                        elif interval == 0.5:
                            interval_text = "Every 12 hours"
                        elif interval == 7:
                            interval_text = "Weekly"
                        st.markdown(f"**Scrape Interval:** {interval_text}")
                    
                    with col2:
                        # Calculate next scrape time
                        if task_details.get('last_scraped'):
                            next_scrape = task_details['last_scraped'] + (interval * 24 * 3600)
                            next_scrape_dt = datetime.fromtimestamp(next_scrape)
                            now = datetime.now()
                            
                            if next_scrape_dt > now:
                                time_until = next_scrape_dt - now
                                if time_until.days > 0:
                                    st.markdown(f"**Next Scrape:** {next_scrape_dt.strftime('%Y-%m-%d %H:%M')} (in {time_until.days} days)")
                                else:
                                    hours = time_until.seconds // 3600
                                    st.markdown(f"**Next Scrape:** {next_scrape_dt.strftime('%Y-%m-%d %H:%M')} (in {hours} hours)")
                            else:
                                st.warning("⚠️ **Next Scrape:** Overdue!")
                        else:
                            st.info("ℹ️ **Next Scrape:** Will be scheduled after first scrape")
                
                st.markdown("---")
                
                if status.get('is_processing'):
                    st.info("⏳ Task is processing...")
                    
                    # Display enhanced logs array
                    if status.get('logs'):
                        logs = status['logs']
                        st.success(f"📊 Showing {len(logs)} latest logs (Total available: {status.get('logs_count', 0)})")
                        
                        # Display logs in a nice format
                        for i, log in enumerate(reversed(logs)):  # Show newest first
                            timestamp = datetime.fromtimestamp(log.get('timestamp', 0)).strftime('%H:%M:%S')
                            message = log.get('message', 'No message')
                            
                            # Create a nice log entry display
                            with st.container():
                                col1, col2 = st.columns([1, 4])
                                with col1:
                                    st.markdown(f"**{timestamp}**")
                                with col2:
                                    st.markdown(message)
                            
                            # Add separator between logs (except for last one)
                            if i < len(logs) - 1:
                                st.markdown("---")
                        
                        # Show latest event summary
                        latest_event = status.get('latest_event')
                        if latest_event:
                            st.markdown("---")
                            st.markdown('<h4 class="main-header">Latest Event Summary</h4>', unsafe_allow_html=True)
                            
                            # Show current processing stage with visual indicator
                            event_type = latest_event.get('event_type', 'Unknown')
                            stage_emoji = {
                                'scrape_started': '🚀',
                                'account_fetched': '👤',
                                'reels_filtered': '🎬',
                                'processing_reels': '⚙️',
                                'reels_processed': '✅',
                                'profile_data_updated': '💾'
                            }.get(event_type, '📊')
                            
                            st.markdown(f"**Current Stage:** {stage_emoji} {event_type.replace('_', ' ').title()}")
                            
                            # Create columns for better layout
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown(f"**Event Type:** {latest_event.get('event_type', 'Unknown')}")
                                st.markdown(f"**Timestamp:** {datetime.fromtimestamp(latest_event.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')}")
                                
                                # Show processing stats if available
                                if 'started_at' in status:
                                    started_time = datetime.fromtimestamp(status['started_at'])
                                    st.markdown(f"**Started:** {started_time.strftime('%Y-%m-%d %H:%M:%S')}")
                                
                                if 'updated_at' in status:
                                    updated_time = datetime.fromtimestamp(status['updated_at'])
                                    st.markdown(f"**Last Updated:** {updated_time.strftime('%Y-%m-%d %H:%M:%S')}")
                            
                            with col2:
                                if 'logs_count' in status:
                                    st.markdown(f"**Total Log Entries:** {status['logs_count']}")
                                if 'requested_logs_count' in status:
                                    st.markdown(f"**Showing:** {status['requested_logs_count']} logs")
                                
                                # Show specific event data based on event type
                                event_type = latest_event.get('event_type', '')
                                if 'scraped_posts_count' in latest_event:
                                    st.markdown(f"**Posts Scraped:** {latest_event['scraped_posts_count']}")
                                if 'reels_count' in latest_event:
                                    st.markdown(f"**Reels Found:** {latest_event['reels_count']}")
                                if 'processing_progress' in latest_event:
                                    st.markdown(f"**Progress:** {latest_event['processing_progress']}")
                                
                                # Show event-specific information based on event type
                                if event_type == 'scrape_started':
                                    st.success("🚀 Scraping process initiated")
                                elif event_type == 'account_fetched':
                                    st.success("👤 Instagram account data retrieved")
                                elif event_type == 'reels_filtered':
                                    st.success("🎬 Reels filtered from posts")
                                elif event_type == 'processing_reels':
                                    st.success("⚙️ Processing reels data")
                                elif event_type == 'reels_processed':
                                    st.success("✅ Reel processing completed")
                                elif event_type == 'profile_data_updated':
                                    st.success("💾 Profile data updated in database")
                                elif event_type:
                                    st.info(f"📊 Event: {event_type}")
                            
                            # Show all event data in an expandable section
                            with st.expander("🔍 View All Event Data", expanded=False):
                                st.json(latest_event)
                    else:
                        st.info("📝 No processing logs available yet")
                        
                        # Fallback to basic status display
                        latest_event = status.get('latest_event')
                        if latest_event:
                            st.markdown('<h4 class="main-header">Latest Event Details</h4>', unsafe_allow_html=True)
                            st.markdown(f"**Event:** {latest_event.get('event_type', 'Unknown')}")
                            st.markdown(f"**Time:** {datetime.fromtimestamp(latest_event.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')}")
                            st.markdown(f"**Message:** {latest_event.get('message', 'No message')}")
                    
                    # Show processing history summary
                    if 'logs_count' in status and status['logs_count'] > 0:
                        st.markdown("---")
                        st.markdown('<h4 class="main-header">Processing Summary</h4>', unsafe_allow_html=True)
                        st.info(f"📊 Total log entries: {status['logs_count']}")
                        
                        # Note: Full logs would require additional API endpoint
                        # For now, show what we can from the current status
                        if 'started_at' in status and 'updated_at' in status:
                            duration = status['updated_at'] - status['started_at']
                            st.caption(f"⏱️ Processing duration: {duration:.1f} seconds")
                            st.caption("ℹ️ This shows how long the task has been running since it started")
                        
                        st.caption("💡 Use the logs selector above to see detailed processing history")
                        
                        # Add information about what's available and what isn't
                        st.info("ℹ️ **Information Available:**")
                        st.caption("• Current processing stage and event type")
                        st.caption("• Timestamp of latest event")
                        st.caption("• Processing duration and log count")
                        st.caption("• Event-specific data (posts scraped, reels found, etc.)")
                        
                        st.warning("⚠️ **Limitations:**")
                        st.caption("• No estimated completion time (varies by profile size and network)")
                        st.caption("• No progress percentage (depends on Instagram's response time)")
                        st.caption("• Refresh manually to see updates (no auto-refresh)")
                        
                else:
                    st.success("✅ Task is idle/completed")
                    
                    # Show last event if available (for completed tasks)
                    latest_event = status.get('latest_event')
                    if latest_event:
                        st.info("📋 Last Processing Event:")
                        st.caption(f"{latest_event.get('event_type', 'event')} at {datetime.fromtimestamp(latest_event.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        # Show completion summary
                        if 'scraped_posts_count' in latest_event:
                            st.success(f"✅ Successfully scraped {latest_event['scraped_posts_count']} posts")
                        if 'reels_count' in latest_event:
                            st.success(f"🎬 Found {latest_event['reels_count']} reels")
                    
                    # Show next steps for completed tasks
                    st.markdown('<h4 class="main-header">Next Steps</h4>', unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("📊 View Profile Details", key=f"view_details_completed_{selected_profile_task_id}"):
                            # Find the task in the list
                            selected_task = None
                            for task in tasks:
                                if task['_id'] == selected_profile_task_id:
                                    selected_task = task
                                    break
                            
                            if selected_task:
                                st.session_state.current_profile = selected_task
                                st.session_state.current_page = 'profile_details'
                                st.rerun()
                        
                        if st.button("🔄 Force New Scrape", key=f"force_scrape_completed_{selected_profile_task_id}"):
                            with st.spinner("Initiating new scrape..."):
                                if api_client.force_scrape_task(selected_profile_task_id):
                                    st.success("✅ New scraping initiated!")
                                    st.session_state.monitor_profile_task_id = selected_profile_task_id
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to initiate scraping")
                    
                    with col2:
                        st.info("💡 **Available Actions:**")
                        st.caption("• View detailed profile analytics")
                        st.caption("• Force immediate re-scraping")
                        st.caption("• Update scraping interval")
                        st.caption("• Monitor competitor performance")
            else:
                st.warning("⚠️ Unable to fetch task status.")
        
        # Smart task selector section
        st.markdown('<h3 class="main-header">Quick Task Actions</h3>', unsafe_allow_html=True)
        st.markdown("Select a task for quick actions:")
        
        selected_task_id = smart_task_selector(api_client)
        
        if selected_task_id:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("🔄 Force Scrape", key=f"force_scrape_{selected_task_id}"):
                    with st.spinner("Scraping profile data..."):
                        if api_client.force_scrape_task(selected_task_id):
                            st.success("Scraping initiated successfully!")
                            st.session_state.monitor_profile_task_id = selected_task_id
                            st.rerun()
                        else:
                            st.error("Failed to initiate scraping")
            
            with col2:
                if st.button("📊 View Details", key=f"view_details_{selected_task_id}"):
                    # Find the task in the list
                    selected_task = None
                    for task in tasks:
                        if task['_id'] == selected_task_id:
                            selected_task = task
                            break
                    
                    if selected_task:
                        st.session_state.monitor_profile_task_id = selected_task_id
                        st.session_state.current_profile = selected_task
                        st.session_state.current_page = 'profile_details'
                        st.rerun()
            
            with col3:
                if st.button("⚙️ Update Interval", key=f"update_interval_{selected_task_id}"):
                    st.info("Use the profile details page to update scraping intervals")
            
            with col4:
                if st.button("🗑️ Delete Task", key=f"delete_task_{selected_task_id}"):
                    # Find the task in the list
                    selected_task = None
                    for task in tasks:
                        if task['_id'] == selected_task_id:
                            selected_task = task
                            break
                    
                    if selected_task:
                        profile_name = selected_task.get('target_profile', 'Unknown')
                        if st.button(f"Confirm Delete @{profile_name}", key=f"confirm_delete_{selected_task_id}"):
                            if api_client.delete_tracking_task(selected_task_id):
                                st.success(f"Deleted tracking task for @{profile_name}")
                                st.rerun()
                            else:
                                st.error(f"Failed to delete tracking task for @{profile_name}") 