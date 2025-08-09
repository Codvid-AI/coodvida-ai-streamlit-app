import streamlit as st

def show_projects_page(api_client):
    """Show projects page with chat and reel tracking"""
    st.title("📁 Projects")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.current_page = 'dashboard'
            st.rerun()
    with col2:
        if st.button("📁 Projects", use_container_width=True, disabled=True):
            pass
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.session_token = None
            st.session_state.current_page = 'login'
            st.rerun()
    
    st.markdown("---")
    
    # Get projects
    projects = api_client.get_project_list()
    
    # Create new project
    st.header("➕ Create New Project")
    with st.expander("Add New Project", expanded=False):
        with st.form("create_project_form"):
            project_name = st.text_input("Project Name", placeholder="Enter project name")
            submit = st.form_submit_button("Create Project")
            
            if submit:
                if project_name:
                    if api_client.create_project(project_name):
                        st.success(f"✅ Created project: {project_name}")
                        st.rerun()
                    else:
                        st.error("❌ Failed to create project")
                else:
                    st.error("Please enter a project name")
    
    # Display projects
    st.header("📋 Your Projects")
    
    if not projects:
        st.info("No projects found. Create your first project above!")
    else:
        for project in projects:
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**{project}**")
                with col2:
                    if st.button("💬 Chat", key=f"chat_{project}"):
                        st.session_state.current_project = project
                        # Ensure project loaded in cache for chat view
                        api_client.ensure_project_loaded(project)
                        st.session_state.current_page = 'project_chat'
                        st.rerun()
                with col3:
                    if st.button("📊 Tracker", key=f"tracker_{project}"):
                        st.session_state.current_project = project
                        st.session_state.current_page = 'project_tracker'
                        st.rerun() 