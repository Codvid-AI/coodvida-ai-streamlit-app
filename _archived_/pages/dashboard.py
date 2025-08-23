import streamlit as st
from datetime import datetime

def smart_task_selector(api_client, auto_select_first=False):
    """
    Smart task selection that can auto-select or prompt user to choose
    Based on the notebook functionality
    """
    tasks = api_client.get_tracking_tasks()
    if not tasks or len(tasks) == 0:
        st.error("❌ No tasks found on server.")
        return None
    
    # Auto-select if only one task and auto_select_first is True
    if len(tasks) == 1 and auto_select_first:
        task = tasks[0]
        task_id = task.get('_id')
        profile = task.get('target_profile', 'unknown')
        ttype = 'Competitor' if task.get('is_competitor') else 'Own Profile'
        st.success(f"✅ Auto-selected only available task: @{profile} ({ttype})")
        return task_id
    
    # Show available tasks
    st.subheader("🎯 Select a task from server:")
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
        st.success(f"✅ Selected: @{profile} (ID: {task_id})")
        return task_id
    
    return None

def show_dashboard(api_client):
    """Show main dashboard with Instagram tracking tasks"""
    st.title("📊 Instagram Analytics Dashboard")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.current_page = 'dashboard'
            st.rerun()
    with col2:
        if st.button("📁 Projects", use_container_width=True):
            st.session_state.current_page = 'projects'
            st.rerun()
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.session_token = None
            st.session_state.current_page = 'login'
            st.rerun()
    
    st.markdown("---")
    
    # Environment selector (based on notebooks)
    st.sidebar.subheader("⚙️ Environment Settings")
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
            st.sidebar.success(f"✅ Environment updated to: {new_env}")
            st.rerun()
    
    st.sidebar.markdown(f"**Current API:** {Config.get_api_url()}")
    
    # Get tracking tasks
    tasks = api_client.get_tracking_tasks()
    
    # Create new tracking task
    st.header("➕ Create New Tracking Task")
    with st.expander("Add Instagram Profile to Track", expanded=False):
        with st.form("create_task_form"):
            profile_name = st.text_input("Instagram Username", placeholder="e.g., foodxtaste")
            is_competitor = st.checkbox("Track as Competitor (uncheck for Own Profile)")
            
            # Add scraping interval settings
            st.subheader("⚙️ Scraping Settings")
            scrape_interval = st.number_input(
                "Scrape Interval (days)", 
                min_value=0.5, 
                max_value=30.0, 
                value=2.0,
                step=0.5,
                help="How often to automatically scrape this profile (0.5 = 12 hours, 1 = daily, 7 = weekly)"
            )
            
            st.caption(f"📅 Profile will be scraped every {scrape_interval} days")
            
            submit = st.form_submit_button("Create Tracking Task")
            
            if submit:
                if profile_name:
                    task_id = api_client.create_tracking_task(profile_name, is_competitor)
                    if task_id:
                        # Update the scrape interval after creation
                        if api_client.update_scrape_interval(task_id, scrape_interval):
                            st.success(f"✅ Created tracking task for @{profile_name} with {scrape_interval}-day interval")
                        else:
                            st.success(f"✅ Created tracking task for @{profile_name} (using default interval)")
                        st.rerun()
                    else:
                        st.error("❌ Failed to create tracking task")
                else:
                    st.error("Please enter a profile name")
    
    # Current task status (always visible if tasks exist)
    if tasks:
        st.subheader("⏱️ Current Profile Task Status")
        
        # Show overall statistics
        st.markdown("📊 **Overall Task Statistics:**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_tasks = len(tasks)
            st.metric("Total Tasks", total_tasks)
        
        with col2:
            active_tasks = len([t for t in tasks if t.get('status') == 'active'])
            st.metric("Active Tasks", active_tasks)
        
        with col3:
            own_profiles = len([t for t in tasks if not t.get('is_competitor')])
            st.metric("Own Profiles", own_profiles)
        
        with col4:
            competitor_profiles = len([t for t in tasks if t.get('is_competitor')])
            st.metric("Competitors", competitor_profiles)
        
        st.markdown("---")
        
        # Show recent activity across all tasks
        st.subheader("🕐 Recent Activity")
        
        # Get recent activity from all tasks
        recent_activities = []
        for task in tasks:
            if task.get('last_scraped'):
                recent_activities.append({
                    'profile': task['target_profile'],
                    'type': 'Competitor' if task.get('is_competitor') else 'Own',
                    'last_scraped': task['last_scraped'],
                    'status': task.get('status', 'unknown')
                })
        
        if recent_activities:
            # Sort by last scraped time (most recent first)
            recent_activities.sort(key=lambda x: x['last_scraped'], reverse=True)
            
            # Show top 5 most recent activities
            for i, activity in enumerate(recent_activities[:5]):
                time_ago = datetime.now() - datetime.fromtimestamp(activity['last_scraped'])
                if time_ago.days > 0:
                    time_text = f"{time_ago.days} days ago"
                elif time_ago.seconds > 3600:
                    time_text = f"{time_ago.seconds // 3600} hours ago"
                else:
                    time_text = f"{time_ago.seconds // 60} minutes ago"
                
                status_emoji = "✅" if activity['status'] == 'active' else "⏸️"
                type_emoji = "🏢" if activity['type'] == 'Competitor' else "👤"
                
                st.caption(f"{status_emoji} @{activity['profile']} ({type_emoji} {activity['type']}) - {time_text}")
        else:
            st.info("ℹ️ No recent scraping activity. Tasks may be new or haven't been scraped yet.")
        
        st.markdown("---")
        
        # Build options mapping
        id_to_label = {t['_id']: f"@{t.get('target_profile','unknown')} ({'Competitor' if t.get('is_competitor') else 'Own'})" for t in tasks}
        ids = list(id_to_label.keys())
        labels = list(id_to_label.values())
        # Pick current selection
        selected_profile_task_id = st.session_state.get('monitor_profile_task_id')
        try:
            current_idx = ids.index(selected_profile_task_id) if selected_profile_task_id in ids else 0
        except Exception:
            current_idx = 0
        choice = st.selectbox("Choose a task to monitor:", options=labels, index=current_idx)
        for tid, lbl in id_to_label.items():
            if lbl == choice:
                st.session_state.monitor_profile_task_id = tid
                selected_profile_task_id = tid
                break
        # Show status (will be enhanced with logs in the processing section below)
        status = api_client.get_task_status(selected_profile_task_id, logs_count=10)
        if status:
            # Show task summary at the top
            st.subheader("📋 Task Summary")
            
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
                
                # Add manual refresh for processing tasks
                st.markdown("**🔄 Manual Refresh:**")
                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button("🔄 Refresh Status", key=f"refresh_status_{selected_profile_task_id}", type="primary"):
                        st.rerun()
                with col2:
                    st.caption("💡 Click this button to fetch the latest task status from the server")
                    st.caption(f"🕐 Last checked: {datetime.now().strftime('%H:%M:%S')}")
                
                st.markdown("---")
                
                # Display enhanced logs array with configurable count
                st.subheader("📊 Task Processing Logs")
                
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
                    if st.button("🔄 Refresh Logs", key=f"refresh_logs_{selected_profile_task_id}", type="secondary"):
                        st.rerun()
                
                # Get enhanced status with selected logs count
                enhanced_status = api_client.get_task_status(selected_profile_task_id, logs_count=logs_to_show)
                
                if enhanced_status and enhanced_status.get('logs'):
                    logs = enhanced_status['logs']
                    st.success(f"📊 Showing {len(logs)} latest logs (Total available: {enhanced_status.get('logs_count', 0)})")
                    
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
                    latest_event = enhanced_status.get('latest_event')
                    if latest_event:
                        st.markdown("---")
                        st.subheader("🎯 Latest Event Summary")
                        
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
                            if 'started_at' in enhanced_status:
                                started_time = datetime.fromtimestamp(enhanced_status['started_at'])
                                st.markdown(f"**Started:** {started_time.strftime('%Y-%m-%d %H:%M:%S')}")
                            
                            if 'updated_at' in enhanced_status:
                                updated_time = datetime.fromtimestamp(enhanced_status['updated_at'])
                                st.markdown(f"**Last Updated:** {updated_time.strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        with col2:
                            if 'logs_count' in enhanced_status:
                                st.markdown(f"**Total Log Entries:** {enhanced_status['logs_count']}")
                            if 'requested_logs_count' in enhanced_status:
                                st.markdown(f"**Showing:** {enhanced_status['requested_logs_count']} logs")
                            
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
                        st.subheader("📊 Latest Event Details")
                        st.markdown(f"**Event:** {latest_event.get('event_type', 'Unknown')}")
                        st.markdown(f"**Time:** {datetime.fromtimestamp(latest_event.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')}")
                        st.markdown(f"**Message:** {latest_event.get('message', 'No message')}")
                
                # Show processing history summary
                if 'logs_count' in status and status['logs_count'] > 0:
                    st.markdown("---")
                    st.subheader("📜 Processing Summary")
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
                    st.warning("⚠️ No event information available")
                    
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
                st.subheader("🚀 Next Steps")
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
    st.header("🎯 Smart Task Selection")
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
                # Find the task to get current interval
                selected_task = None
                for task in tasks:
                    if task['_id'] == selected_task_id:
                        selected_task = task
                        break
                
                if selected_task:
                    current_interval = selected_task.get('scrape_interval_days', 2)
                    st.session_state.editing_task_id = selected_task_id
                    st.session_state.editing_current_interval = current_interval
                    st.rerun()
        
        with col4:
            if st.button("🗑️ Delete Task", key=f"delete_task_{selected_task_id}"):
                if api_client.delete_tracking_task(selected_task_id):
                    st.success("Task deleted!")
                    st.rerun()
                else:
                    st.error("Failed to delete task")
    
    # Interval update form
    if hasattr(st.session_state, 'editing_task_id'):
        st.subheader("⚙️ Update Scraping Interval")
        with st.form("update_interval_form"):
            new_interval = st.number_input(
                "New Scrape Interval (days)",
                min_value=0.5,
                max_value=30.0,
                value=st.session_state.editing_current_interval,
                step=0.5,
                help="How often to automatically scrape this profile"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✅ Update Interval"):
                    if api_client.update_scrape_interval(st.session_state.editing_task_id, new_interval):
                        st.success(f"✅ Updated interval to {new_interval} days")
                        del st.session_state.editing_task_id
                        del st.session_state.editing_current_interval
                        st.rerun()
                    else:
                        st.error("❌ Failed to update interval")
            
            with col2:
                if st.form_submit_button("❌ Cancel"):
                    del st.session_state.editing_task_id
                    del st.session_state.editing_current_interval
                    st.rerun()
    
    # Display existing tasks
    st.header("📱 Your Instagram Tracking Tasks")
    
    if not tasks:
        st.info("No tracking tasks found. Create your first task above!")
    else:
        # Scraping intervals summary
        st.subheader("⏰ Scraping Intervals Summary")
        intervals_summary = {}
        for task in tasks:
            interval = task.get('scrape_interval_days', 2)
            profile = task['target_profile']
            task_type = 'Competitor' if task.get('is_competitor') else 'Own'
            
            if interval not in intervals_summary:
                intervals_summary[interval] = []
            intervals_summary[interval].append(f"@{profile} ({task_type})")
        
        # Display intervals summary
        for interval, profiles in intervals_summary.items():
            interval_text = f"Every {interval} days"
            if interval == 1:
                interval_text = "Daily"
            elif interval == 0.5:
                interval_text = "Every 12 hours"
            elif interval == 7:
                interval_text = "Weekly"
            
            st.markdown(f"**🔄 {interval_text}:** {', '.join(profiles)}")
        
        st.markdown("---")
        
        # Separate own profiles and competitors
        own_profiles = [task for task in tasks if not task.get('is_competitor', False)]
        competitor_profiles = [task for task in tasks if task.get('is_competitor', False)]
        
        # Own Profiles Section
        if own_profiles:
            st.subheader("👤 Your Own Profiles")
            for task in own_profiles:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"**@{task['target_profile']}**")
                        st.caption(f"Status: {task.get('status', 'unknown')}")
                        
                        # Show scraping interval
                        interval = task.get('scrape_interval_days', 2)
                        interval_text = f"🔄 Scraped every {interval} days"
                        if interval == 1:
                            interval_text = "🔄 Scraped daily"
                        elif interval == 0.5:
                            interval_text = "🔄 Scraped every 12 hours"
                        elif interval == 7:
                            interval_text = "🔄 Scraped weekly"
                        st.caption(interval_text)
                        
                        if task.get('last_scraped'):
                            last_scraped = datetime.fromtimestamp(task['last_scraped'])
                            st.caption(f"Last scraped: {last_scraped.strftime('%Y-%m-%d %H:%M')}")
                    with col2:
                        if st.button("📊 View", key=f"view_{task['_id']}"):
                            st.session_state.current_profile = task
                            st.session_state.current_page = 'profile_details'
                            st.rerun()
                    with col3:
                        if st.button("🗑️ Delete", key=f"delete_{task['_id']}"):
                            if api_client.delete_tracking_task(task['_id']):
                                st.success("Task deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete task")
        
        # Competitor Profiles Section
        if competitor_profiles:
            st.subheader("🏢 Competitor Profiles")
            for task in competitor_profiles:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"**@{task['target_profile']}**")
                        st.caption(f"Status: {task.get('status', 'unknown')}")
                        
                        # Show scraping interval
                        interval = task.get('scrape_interval_days', 2)
                        interval_text = f"🔄 Scraped every {interval} days"
                        if interval == 1:
                            interval_text = "🔄 Scraped daily"
                        elif interval == 0.5:
                            interval_text = "🔄 Scraped every 12 hours"
                        elif interval == 7:
                            interval_text = "🔄 Scraped weekly"
                        st.caption(interval_text)
                        
                        if task.get('last_scraped'):
                            last_scraped = datetime.fromtimestamp(task['last_scraped'])
                            st.caption(f"Last scraped: {last_scraped.strftime('%Y-%m-%d %H:%M')}")
                    with col2:
                        if st.button("📊 View", key=f"view_comp_{task['_id']}"):
                            st.session_state.current_profile = task
                            st.session_state.current_page = 'profile_details'
                            st.rerun()
                    with col3:
                        if st.button("🗑️ Delete", key=f"delete_comp_{task['_id']}"):
                            if api_client.delete_tracking_task(task['_id']):
                                st.success("Task deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete task") 