import streamlit as st
import json
from datetime import datetime

# DUPLICATE MESSAGE PREVENTION IMPLEMENTED
# 
# The following measures prevent duplicate messages from appearing in the chat:
# 1. Single source of truth: Only local_user_data cache is used, no fallback chat_history
# 2. Backend deduplication: process_streaming_response tracks yielded text pieces to prevent duplicates
# 3. Frontend deduplication: apply_user_data_mods checks for existing messages before appending
# 4. Display deduplication: Frontend removes any duplicate messages before displaying
# 5. User message handling: Only added to local cache, not to fallback history
# 
# This ensures that:
# - AI responses are only added once via data_mods from the backend
# - User messages are only stored in one location
# - No duplicate text chunks are yielded during streaming
# - Display always shows unique messages even if duplicates somehow exist in data

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
    
    # Use only local cache chats - single source of truth
    local_chats = None
    try:
        local_chats = st.session_state.local_user_data["projects"][project]["chats"]
    except Exception:
        local_chats = []

    with chat_container:
        # Use only local cache chats to prevent duplicates
        messages_src = local_chats if isinstance(local_chats, list) and local_chats else []
        
        if not messages_src:
            st.info("No messages yet. Start a conversation!")
        else:
            # Remove any duplicate messages that might have slipped through
            seen_messages = set()
            unique_messages = []
            
            for message in messages_src:
                # Create a unique identifier for each message that includes all relevant properties
                role = message.get('role', '')
                msg_type = message.get('type', '')
                text = message.get('text', '') or message.get('content', '')
                event_type = message.get('event_type', '')
                
                # Create a more comprehensive unique identifier
                if msg_type == 'event':
                    msg_id = f"{role}:{msg_type}:{event_type}:{text}"
                else:
                    msg_id = f"{role}:{msg_type}:{text}"
                
                if msg_id not in seen_messages:
                    seen_messages.add(msg_id)
                    unique_messages.append(message)
            
            # Display unique messages
            for i, message in enumerate(unique_messages):
                role = message.get('role')
                msg_type = message.get('type', 'text')
                content = message.get('content') or message.get('text') or ''
                
                # Handle different message types with appropriate formatting
                if role == 'user':
                    st.markdown(f"**👤 You:** {content}")
                
                elif role == 'assistant':
                    if msg_type == 'event':
                        # Handle event messages with special formatting
                        event_type = message.get('event_type', 'unknown')
                        if event_type == 'tool_calling':
                            st.markdown(f"**🔧 AI Tool Calling:** {content}")
                            st.info("AI is calling external tools to process your request...")
                        elif event_type == 'loading':
                            st.markdown(f"**⏳ AI Processing:** {content}")
                            st.info("AI is working on your request...")
                        elif event_type == 'info':
                            st.markdown(f"**ℹ️ AI Info:** {content}")
                            st.info(content)
                        elif event_type == 'show_reel_options':
                            st.markdown(f"**🎬 AI Found Reels:** {content}")
                            # Display reel options if available
                            options = message.get('options', [])
                            if options:
                                st.markdown("**Available Reels:**")
                                for option in options:
                                    st.markdown(f"- `{option}`")
                        else:
                            st.markdown(f"**🤖 AI Event ({event_type}):** {content}")
                    else:
                        # Regular text message
                        st.markdown(f"**🤖 AI:** {content}")
                
                elif role == 'tool':
                    # Tool result messages
                    st.markdown(f"**⚙️ Tool Result:**")
                    st.markdown(f"```\n{content}\n```")
                    st.success("Tool execution completed")
                
                elif role == 'system':
                    st.markdown(f"**🔧 System:** {content}")
                
                else:
                    # Unknown role/type
                    st.markdown(f"**{role or 'unknown'} ({msg_type}):** {content}")

                # Add visual separation between messages
                if i < len(unique_messages) - 1:
                    st.markdown("---")
        
        # Create a streaming area within the chat container for real-time AI responses
        # This will appear in the chat board area, not under the input field
        streaming_area = st.empty()
        # Store the streaming area reference in session state so we can access it during streaming
        st.session_state.streaming_area = streaming_area
    
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
            # Clear only local cache to prevent duplicates
            try:
                st.session_state.local_user_data["projects"][project]["chats"] = []
                st.success("Chat history cleared successfully!")
            except Exception as e:
                st.error(f"Failed to clear chat history: {e}")
            st.rerun()
        

        
        if submit and message:
            # Add user message to local cache only (no fallback history to prevent duplicates)
            try:
                st.session_state.local_user_data["projects"][project]["chats"].append({
                    'role': 'user', 'type': 'text', 'text': message
                })
            except Exception as e:
                st.error(f"Failed to add user message: {e}")
                return

            if hasattr(st.session_state, 'example_message'):
                del st.session_state.example_message

            # Get AI response (streaming)
            with st.spinner("AI is thinking..."):
                streaming_response = api_client.ai_chat(project, message)
                
                if streaming_response:
                    # Add a typing indicator
                    typing_placeholder = st.empty()
                    typing_placeholder.markdown("🔄 *AI is typing...*")
                    
                    # Add a progress bar for streaming
                    progress_bar = st.progress(0)
                    progress_text = st.empty()
                    progress_text.text("Starting AI response...")
                    
                    try:
                        # Use the streaming area that's already positioned in the chat board
                        streaming_placeholder = st.session_state.get('streaming_area')
                        if streaming_placeholder:
                            streaming_placeholder.markdown("**🤖 AI:** ")
                        
                        # Process streaming response in real-time - display each chunk immediately in chat
                        chunk_count = 0
                        current_response_text = ""
                        
                        for text_chunk, is_final, data_mods in api_client.process_streaming_response(streaming_response, project):
                            if text_chunk:
                                chunk_count += 1
                                current_response_text += text_chunk
                                
                                # Update the streaming placeholder in the chat board with each new chunk
                                if streaming_placeholder:
                                    streaming_placeholder.markdown(f"**🤖 AI:** {current_response_text}")
                                
                                # Update progress
                                progress_value = min(0.9, chunk_count * 0.1)
                                progress_bar.progress(progress_value)
                                progress_text.text(f"Receiving response... ({chunk_count} chunks)")
                            
                            # Check if this was added via data_mods
                            if data_mods:
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
                                                    # Message already added via data_mods, no need to add manually
                                                    pass
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
                        st.success("✅ AI response complete!")
                                
                    except Exception as e:
                        st.error(f"Error processing streaming response: {e}")
                        typing_placeholder.empty()
                        progress_bar.progress(0)
                        progress_text.text("❌ Error occurred")
                    
                    # Note: AI response is automatically added to chat history via data_mods
                    # No need to manually append it here
                    
                    # Add debug logging if enabled
                    if st.session_state.get('debug_mode', False):
                        st.session_state.api_logs.append({
                            'timestamp': datetime.now().isoformat(),
                            'endpoint': "/codvid-ai/ai/respond",
                            'method': 'POST',
                            'stream': True,
                            'request': {'project': project, 'message': message},
                            'response': {'aggregated_text': current_response_text, 'assistant_message_added_via_mods': False}, # Changed to current_response_text
                        })
                else:
                    st.error("Failed to get AI response")

            st.rerun()
    
    # Add project information
    st.sidebar.subheader("📁 Project Info")
    st.sidebar.markdown(f"**Project:** {project}")
    
    # Get message count from local cache only
    try:
        message_count = len(st.session_state.local_user_data["projects"][project]["chats"])
        st.sidebar.markdown(f"**Messages:** {message_count}")
        
        # Show message type breakdown
        if message_count > 0:
            st.sidebar.markdown("**Message Types:**")
            type_counts = {}
            for msg in st.session_state.local_user_data["projects"][project]["chats"]:
                role = msg.get('role', 'unknown')
                msg_type = msg.get('type', 'text')
                
                if role == 'assistant' and msg_type == 'event':
                    event_type = msg.get('event_type', 'unknown')
                    key = f"AI {event_type}"
                else:
                    key = f"{role} {msg_type}"
                
                type_counts[key] = type_counts.get(key, 0) + 1
            
            for msg_type, count in type_counts.items():
                st.sidebar.markdown(f"- {msg_type}: {count}")
                
    except Exception:
        st.sidebar.markdown("**Messages:** 0")
    
    # Add chat tips
    st.sidebar.subheader("💡 Chat Tips")
    st.sidebar.markdown("""
    - Use `sudo123 fetch the profile @username` to get profile data
    - Ask for analytics insights and recommendations
    - Request content strategy advice
    - Get sentiment analysis summaries
    """)
    
    # Add message type explanation
    st.sidebar.subheader("📝 Message Types")
    st.sidebar.markdown("""
    **👤 User:** Your messages
    
    **🤖 AI:** AI responses and analysis
    
    **🔧 AI tool_calling:** AI is using external tools
    
    **⏳ AI loading:** AI is processing your request
    
    **ℹ️ AI info:** Important information from AI
    
    **🎬 AI show_reel_options:** Reel suggestions found
    
    **⚙️ Tool Result:** Results from tool execution
    
    **🔧 System:** System messages and notifications
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
        
        st.sidebar.markdown("**Fallback messages:** Disabled (prevented duplicates)") 