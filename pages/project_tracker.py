import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime

def show_project_tracker(api_client):
    """Show project reel tracking interface"""
    if not st.session_state.current_project:
        st.error("No project selected")
        st.button("Back to Projects", on_click=lambda: setattr(st.session_state, 'current_page', 'projects'))
        return
    
    project = st.session_state.current_project
    
    st.title(f"📊 {project} - Reel Tracker")
    
    # Back button
    if st.button("← Back to Projects"):
        st.session_state.current_page = 'projects'
        st.rerun()
    
    st.markdown("---")
    
    # Add new reel to track
    st.header("➕ Add Reel to Track")
    with st.expander("Add Instagram Reel", expanded=False):
        with st.form("add_reel_form"):
            reel_url = st.text_input(
                "Instagram Reel URL", 
                placeholder="https://www.instagram.com/reel/...",
                help="Paste the full Instagram reel URL here"
            )
            
            # Add scraping interval settings
            st.subheader("⚙️ Scraping Settings")
            scrape_interval = st.number_input(
                "Scrape Interval (days)", 
                min_value=0.5, 
                max_value=30.0, 
                value=2.0,
                step=0.5,
                help="How often to automatically scrape this reel (0.5 = 12 hours, 1 = daily, 7 = weekly)"
            )
            
            st.caption(f"📅 Reel will be scraped every {scrape_interval} days")
            
            submit = st.form_submit_button("Add Reel to Track")
            
            if submit:
                if reel_url:
                    task_id = api_client.create_reel_tracking_task(project, reel_url, scrape_interval)
                    if task_id:
                        st.success(f"✅ Added reel to tracking with {scrape_interval}-day interval")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add reel to tracking")
                else:
                    st.error("Please enter a reel URL")
    
    # Display existing reel tasks
    st.header("📊 Tracked Reels")
    
    reel_tasks = api_client.get_project_reel_tasks(project)
    
    if not reel_tasks:
        st.info("No reels are being tracked. Add your first reel above!")
    else:
        st.markdown(f"**Total tracked reels:** {len(reel_tasks)}")
        
        for task in reel_tasks:
            with st.container():
                st.markdown("---")
                
                # Reel info
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**🎬 Reel ID:** {task.get('reel_id', 'N/A')}")
                    st.caption(f"**URL:** {task.get('reel_url', 'N/A')}")
                    
                    # Show current interval
                    current_interval = task.get('scrape_interval_days', 2)
                    st.caption(f"**Current interval:** {current_interval} days")
                    
                    # Show last scraped
                    if task.get('last_scraped'):
                        last_scraped = datetime.fromtimestamp(task['last_scraped'])
                        st.caption(f"**Last scraped:** {last_scraped.strftime('%Y-%m-%d %H:%M')}")
                
                with col2:
                    # Actions
                    if st.button("🔄 Force Scrape", key=f"force_scrape_reel_{task['_id']}"):
                        with st.spinner("Scraping reel data..."):
                            if api_client.force_scrape_reel_task(task['_id']):
                                st.success("Scraping initiated!")
                                st.rerun()
                            else:
                                st.error("Failed to scrape")
                    
                    if st.button("⚙️ Update Interval", key=f"update_reel_interval_{task['_id']}"):
                        st.session_state.editing_reel_task_id = task['_id']
                        st.session_state.editing_reel_current_interval = current_interval
                        st.rerun()
                
                # Show reel data if available
                reel_data = task.get('reel_data', {})
                if reel_data:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Likes", f"{reel_data.get('likes', 0):,}")
                    with col2:
                        st.metric("Comments", f"{reel_data.get('comments', 0):,}")
                    with col3:
                        st.metric("Views", f"{reel_data.get('views', 0):,}")
                    with col4:
                        sentiment = reel_data.get('sentiment_analysis', {}).get('overall_sentiment', 'neutral')
                        st.metric("Sentiment", sentiment.title())
        
        # Interval update form for reels
        if hasattr(st.session_state, 'editing_reel_task_id'):
            st.subheader("⚙️ Update Reel Scraping Interval")
            with st.form("update_reel_interval_form"):
                new_interval = st.number_input(
                    "New Scrape Interval (days)",
                    min_value=0.5,
                    max_value=30.0,
                    value=st.session_state.editing_reel_current_interval,
                    step=0.5,
                    help="How often to automatically scrape this reel"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("✅ Update Interval"):
                        if api_client.update_scrape_interval(st.session_state.editing_reel_task_id, new_interval):
                            st.success(f"✅ Updated reel interval to {new_interval} days")
                            del st.session_state.editing_reel_task_id
                            del st.session_state.editing_reel_current_interval
                            st.rerun()
                        else:
                            st.error("❌ Failed to update interval")
                
                with col2:
                    if st.form_submit_button("❌ Cancel"):
                        del st.session_state.editing_reel_task_id
                        del st.session_state.editing_reel_current_interval
                        st.rerun()
        
        # Show detailed reel data
        if reel_tasks:
            st.subheader("📈 Reel Performance")
            
            # Create performance chart
            performance_data = []
            for task in reel_tasks:
                if task.get('reel_data'):
                    reel_data = task['reel_data']
                    performance_data.append({
                        'Reel ID': task.get('reel_id', 'Unknown'),
                        'Likes': reel_data.get('likes', 0),
                        'Comments': reel_data.get('comments', 0),
                        'Views': reel_data.get('views', 0)
                    })
            
            if performance_data:
                df = pd.DataFrame(performance_data)
                
                # Create performance chart
                fig = make_subplots(
                    rows=1, cols=3,
                    subplot_titles=('Likes', 'Comments', 'Views'),
                    specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]]
                )
                
                fig.add_trace(
                    go.Bar(x=df['Reel ID'], y=df['Likes'], name='Likes'),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Bar(x=df['Reel ID'], y=df['Comments'], name='Comments'),
                    row=1, col=2
                )
                fig.add_trace(
                    go.Bar(x=df['Reel ID'], y=df['Views'], name='Views'),
                    row=1, col=3
                )
                
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True) 