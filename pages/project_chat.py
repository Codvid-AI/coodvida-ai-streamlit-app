import streamlit as st
import json

# FIXED: Duplicate AI response issue
# The problem was that AI responses were being added twice:
# 1. Once via data_mods from the backend (which automatically updates the local cache)
# 2. Once manually in the frontend code
# 
# Solution: Modified ai_chat() to return None when message is already added via data_mods

def show_project_chat(api_client):
    """Show project chat interface with improved functionality"""
    if not st.session_state.current_project:
        st.error("No project selected")
        st.button("Back to Projects", on_click=lambda: setattr(st.session_state, 'current_page', 'projects'))
        return
    
    project = st.session_state.current_project
    
    st.title(f"💬 {project} - AI Chat")
    
    # Navigation buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Back to Projects"):
            st.session_state.current_page = 'projects'
            st.rerun()
    with col2:
        # Use session state to track delete confirmation
        if "delete_confirm_chat" not in st.session_state:
            st.session_state["delete_confirm_chat"] = False
        
        if not st.session_state["delete_confirm_chat"]:
            if st.button("🗑️ Delete Project", type="secondary"):
                st.session_state["delete_confirm_chat"] = True
                st.rerun()
        else:
            # Show confirmation dialog
            st.warning(f"⚠️ Are you sure you want to delete project '{project}'? This action cannot be undone!")
            col_confirm1, col_confirm2 = st.columns(2)
            with col_confirm1:
                if st.button("✅ Yes, Delete", key="confirm_delete_chat"):
                    st.info(f"🗑️ Deleting project '{project}'...")
                    if api_client.delete_project(project):
                        st.success(f"✅ Project '{project}' deleted successfully!")
                        # Remove from local cache if it exists
                        try:
                            if project in st.session_state.local_user_data.get("projects", {}):
                                del st.session_state.local_user_data["projects"][project]
                        except Exception:
                            pass
                        # Clear current project and go back to projects
                        st.session_state.current_project = None
                        st.session_state.current_page = 'projects'
                        # Clear the delete confirmation state
                        if "delete_confirm_chat" in st.session_state:
                            del st.session_state["delete_confirm_chat"]
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to delete project '{project}'")
                        st.session_state["delete_confirm_chat"] = False
                        st.rerun()
            with col_confirm2:
                if st.button("❌ Cancel", key="cancel_delete_chat"):
                    st.session_state["delete_confirm_chat"] = False
                    st.rerun()
    
    st.markdown("---")
    
    # Initialize chat history (fallback only)
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Ensure local cache is properly initialized for this project
    if project not in st.session_state.local_user_data.get("projects", {}):
        st.session_state.local_user_data.setdefault("projects", {})[project] = {}
    if "chats" not in st.session_state.local_user_data["projects"][project]:
        st.session_state.local_user_data["projects"][project]["chats"] = []
    
    # Display chat history with better formatting
    st.subheader("Chat History")
    
    # Create a container for chat messages
    chat_container = st.container()
    
    # Prefer chats from local user data cache if available
    local_chats = None
    try:
        local_chats = st.session_state.local_user_data["projects"][project]["chats"]
    except Exception:
        local_chats = None

    with chat_container:
        # Always prefer local cache chats if available, as they're more up-to-date
        messages_src = local_chats if isinstance(local_chats, list) and local_chats else st.session_state.chat_history
        
        if not messages_src:
            st.info("No messages yet. Start a conversation!")
        else:
            for i, message in enumerate(messages_src):
                role = message.get('role')
                content = message.get('content') or message.get('text') or ''
                if role == 'user':
                    st.markdown(f"**👤 You:** {content}")
                elif role == 'assistant':
                    st.markdown(f"**🤖 AI:** {content}")
                else:
                    st.markdown(f"**{role or 'system'}:** {content}")

                if i < len(messages_src) - 1:
                    st.markdown("---")
    
    # Chat input with improved interface
    st.subheader("Send Message")
    
    # Add some example prompts
    st.markdown("**💡 Quick Prompts:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 Analyze Profile", key="prompt_analyze"):
            example_message = "sudo123 fetch the profile @foodxtaste"
            st.session_state.example_message = example_message
    
    with col2:
        if st.button("📈 Get Insights", key="prompt_insights"):
            example_message = "What are the key insights from my Instagram data?"
            st.session_state.example_message = example_message
    
    with col3:
        if st.button("🎯 Strategy", key="prompt_strategy"):
            example_message = "What content strategy should I follow based on my analytics?"
            st.session_state.example_message = example_message
    
    with st.form("chat_form"):
        # Pre-fill with example message if selected
        default_message = getattr(st.session_state, 'example_message', '')
        message = st.text_area(
            "Your message", 
            value=default_message,
            placeholder="Type your message here... (e.g., 'sudo123 fetch the profile @username')", 
            height=100
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submit = st.form_submit_button("Send Message")
        with col2:
            clear_chat = st.form_submit_button("Clear Chat History")
        
        if clear_chat:
            # Clear both local cache and fallback history
            try:
                st.session_state.local_user_data["projects"][project]["chats"] = []
            except Exception:
                pass
            st.session_state.chat_history = []
            st.rerun()
        

        
        if submit and message:
            # Add user message to local cache and fallback history
            try:
                st.session_state.local_user_data["projects"][project]["chats"].append({
                    'role': 'user', 'type': 'text', 'text': message
                })
            except Exception:
                st.session_state.chat_history.append({'role': 'user', 'text': message})

            if hasattr(st.session_state, 'example_message'):
                del st.session_state.example_message

            # Get AI response (streaming aggregation)
            with st.spinner("AI is thinking..."):
                ai_response = api_client.ai_chat(project, message)
                # If ai_chat returns None, it means the message was already added via data_mods
                # If it returns empty text but debug logs show chunks, fall back to showing a generic acknowledgment
                if ai_response is None:
                    # Message was already added via data_mods, no need to add again
                    pass
                elif not ai_response:
                    ai_response = "(received streaming chunks, see debug logs)"
                    try:
                        st.session_state.local_user_data["projects"][project]["chats"].append({
                            'role': 'assistant', 'type': 'text', 'text': ai_response
                        })
                    except Exception:
                        st.session_state.chat_history.append({'role': 'assistant', 'text': ai_response})
                else:
                    # Only add the message if it wasn't already added via data_mods
                    try:
                        st.session_state.local_user_data["projects"][project]["chats"].append({
                            'role': 'assistant', 'type': 'text', 'text': ai_response
                        })
                    except Exception:
                        st.session_state.chat_history.append({'role': 'assistant', 'text': ai_response})

            st.rerun()
    
    # Add project information
    st.sidebar.subheader("📁 Project Info")
    st.sidebar.markdown(f"**Project:** {project}")
    st.sidebar.markdown(f"**Messages:** {len(st.session_state.chat_history)}")
    
    # Add chat tips
    st.sidebar.subheader("💡 Chat Tips")
    st.sidebar.markdown("""
    - Use `sudo123 fetch the profile @username` to get profile data
    - Ask for analytics insights and recommendations
    - Request content strategy advice
    - Get sentiment analysis summaries
    """)
    
    # Debug information (only show in debug mode)
    if st.session_state.get('debug_mode', False):
        st.sidebar.markdown("---")
        st.sidebar.subheader("🐛 Debug Info")
        try:
            local_chat_count = len(st.session_state.local_user_data["projects"][project]["chats"])
            st.sidebar.markdown(f"**Local cache messages:** {local_chat_count}")
        except Exception:
            st.sidebar.markdown("**Local cache messages:** Error")
        
        fallback_count = len(st.session_state.chat_history)
        st.sidebar.markdown(f"**Fallback messages:** {fallback_count}") 