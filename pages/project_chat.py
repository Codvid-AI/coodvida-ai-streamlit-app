import streamlit as st
import json
from datetime import datetime

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
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Analyze Profile", key="prompt_analyze"):
            example_message = "Please analyze the profile @foodxtaste"
            st.session_state.example_message = example_message
    
    with col2:
        if st.button("🎬 Analyze IG Reel", key="prompt_reel"):
            example_message = "Please analyse the reel content: https://www.instagram.com/reel/..."
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

            # Get AI response (streaming)
            with st.spinner("AI is thinking..."):
                streaming_response = api_client.ai_chat(project, message)
                
                if streaming_response:
                    # Create a placeholder for the streaming AI response
                    ai_message_placeholder = st.empty()
                    ai_message_placeholder.markdown("**🤖 AI:** ")
                    
                    # Add a typing indicator
                    typing_placeholder = st.empty()
                    typing_placeholder.markdown("🔄 *AI is typing...*")
                    
                    # Add a progress bar for streaming
                    progress_bar = st.progress(0)
                    progress_text = st.empty()
                    progress_text.text("Starting AI response...")
                    
                    # Process streaming response in real-time using the helper method
                    aggregated_text = ""
                    assistant_message_added_via_mods = False
                    chunk_count = 0
                    
                    try:
                        for text_chunk, is_final, data_mods in api_client.process_streaming_response(streaming_response, project):
                            if text_chunk:
                                chunk_count += 1
                                aggregated_text += text_chunk
                                # Update the placeholder in real-time with better formatting
                                ai_message_placeholder.markdown(f"**🤖 AI:** {aggregated_text}")
                                
                                # Update progress (simulate progress since we don't know total chunks)
                                progress_value = min(0.9, chunk_count * 0.1)  # Cap at 90% until complete
                                progress_bar.progress(progress_value)
                                progress_text.text(f"Receiving response... ({chunk_count} chunks)")
                            
                            # Check if this was added via data_mods
                            if data_mods and not assistant_message_added_via_mods:
                                for mod in data_mods:
                                    try:
                                        key_path = mod.get("key_path")
                                        mode = mod.get("mode")
                                        value = mod.get("value")
                                        if (
                                            isinstance(key_path, list)
                                            and len(key_path) >= 3
                                            and key_path[-2] == project
                                            and key_path[-1] == "chats"
                                            and mode in ("append", "create")
                                        ):
                                            messages = value if isinstance(value, list) else [value]
                                            for m in messages:
                                                if isinstance(m, dict) and m.get("role") == "assistant":
                                                    assistant_message_added_via_mods = True
                                                    break
                                    except Exception:
                                        continue
                            
                            # If final, break the loop
                            if is_final:
                                break
                        
                        # Complete the progress bar
                        progress_bar.progress(1.0)
                        progress_text.text("✅ Response complete!")
                        
                        # Remove typing indicator when done
                        typing_placeholder.empty()
                        
                        # Add a completion indicator
                        if aggregated_text:
                            st.success("✅ AI response complete!")
                                
                    except Exception as e:
                        st.error(f"Error processing streaming response: {e}")
                        typing_placeholder.empty()
                        progress_bar.progress(0)
                        progress_text.text("❌ Error occurred")
                    
                    # Add the complete AI response to chat history if not already added via data_mods
                    if aggregated_text and not assistant_message_added_via_mods:
                        try:
                            st.session_state.local_user_data["projects"][project]["chats"].append({
                                'role': 'assistant', 'type': 'text', 'text': aggregated_text
                            })
                        except Exception:
                            st.session_state.chat_history.append({'role': 'assistant', 'text': aggregated_text})
                    
                    # Add debug logging if enabled
                    if st.session_state.get('debug_mode', False):
                        st.session_state.api_logs.append({
                            'timestamp': datetime.now().isoformat(),
                            'endpoint': "/codvid-ai/ai/respond",
                            'method': 'POST',
                            'stream': True,
                            'request': {'project': project, 'message': message},
                            'response': {'aggregated_text': aggregated_text, 'assistant_message_added_via_mods': assistant_message_added_via_mods},
                        })
                else:
                    st.error("Failed to get AI response")

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