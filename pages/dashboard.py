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
        # Show status
        status = api_client.get_task_status(selected_profile_task_id)
        if status:
            if status.get('is_processing'):
                st.info("⏳ Task is processing...")
                latest_event = status.get('latest_event')
                if latest_event:
                    st.caption(f"Latest: {latest_event.get('event_type','event')} at {datetime.fromtimestamp(latest_event.get('timestamp',0)).strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                st.success("✅ Task is idle/completed")
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