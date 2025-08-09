import streamlit as st
import json

def show_project_chat(api_client):
    """Show project chat interface with improved functionality"""
    if not st.session_state.current_project:
        st.error("No project selected")
        st.button("Back to Projects", on_click=lambda: setattr(st.session_state, 'current_page', 'projects'))
        return
    
    project = st.session_state.current_project
    
    st.title(f"💬 {project} - AI Chat")
    
    # Back button
    if st.button("← Back to Projects"):
        st.session_state.current_page = 'projects'
        st.rerun()
    
    st.markdown("---")
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history with better formatting
    st.subheader("Chat History")
    
    # Create a container for chat messages
    chat_container = st.container()
    
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message['role'] == 'user':
                st.markdown(f"**👤 You:** {message['content']}")
            else:
                st.markdown(f"**🤖 AI:** {message['content']}")
            
            # Add separator between messages
            if i < len(st.session_state.chat_history) - 1:
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
            st.session_state.chat_history = []
            st.rerun()
        
        if submit and message:
            # Add user message to history
            st.session_state.chat_history.append({'role': 'user', 'content': message})
            
            # Clear example message
            if hasattr(st.session_state, 'example_message'):
                del st.session_state.example_message
            
            # Get AI response with streaming simulation
            with st.spinner("AI is thinking..."):
                ai_response = api_client.ai_chat(project, message)
                st.session_state.chat_history.append({'role': 'assistant', 'content': ai_response})
            
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