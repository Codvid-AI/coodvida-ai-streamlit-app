import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
from config import Config

def display_sentiment_analysis(sentiment_summary):
    """Display sentiment analysis with visual bars like in the notebooks"""
    if not sentiment_summary or sentiment_summary['total_comments'] == 0:
        st.info("❌ No comments found to analyze.")
        return
    
    st.subheader("😊 Sentiment Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Overall Sentiment:** {sentiment_summary['overall_sentiment'].title()}")
        st.markdown(f"**Total Comments Analyzed:** {sentiment_summary['total_comments']}")
    
    with col2:
        if sentiment_summary['total_comments'] > 0:
            # Create sentiment chart
            sentiment_data = sentiment_summary['sentiment_distribution']
            fig = px.pie(
                values=list(sentiment_data.values()),
                names=list(sentiment_data.keys()),
                title="Sentiment Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Display sentiment distribution with visual bars (from notebooks)
    st.subheader("📋 Sentiment Distribution:")
    sentiment_config = Config.SENTIMENT_CONFIG
    max_width = sentiment_config["max_bar_width"]
    emoji_map = sentiment_config["emoji_map"]
    
    for sentiment, count in sentiment_summary['sentiment_distribution'].items():
        percentage = sentiment_summary['sentiment_percentages'][sentiment]
        emoji = emoji_map.get(sentiment, "😐")
        st.markdown(f"   {emoji} {sentiment.capitalize()}: {count} comments ({percentage:.1f}%)")
    
    # Create visual distribution bars
    st.subheader("📊 Visual Distribution:")
    for sentiment, percentage in sentiment_summary['sentiment_percentages'].items():
        bar_width = int((percentage / 100) * max_width)
        bar = "█" * bar_width + "░" * (max_width - bar_width)
        emoji = emoji_map.get(sentiment, "😐")
        st.markdown(f"   {emoji} {sentiment.capitalize():8} |{bar}| {percentage:.1f}%")

def show_profile_details(api_client):
    """Show detailed profile information and controls"""
    if not st.session_state.current_profile:
        st.error("No profile selected")
        st.button("Back to Dashboard", on_click=lambda: setattr(st.session_state, 'current_page', 'dashboard'))
        return
    
    profile = st.session_state.current_profile
    
    st.title(f"📊 @{profile['target_profile']} Analytics")
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.current_page = 'dashboard'
        st.rerun()
    
    st.markdown("---")
    
    # Profile info
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Profile Information")
        st.markdown(f"**Username:** @{profile['target_profile']}")
        st.markdown(f"**Type:** {'Competitor' if profile.get('is_competitor') else 'Own Profile'}")
        st.markdown(f"**Status:** {profile.get('status', 'unknown')}")
        
        if profile.get('last_scraped'):
            last_scraped = datetime.fromtimestamp(profile['last_scraped'])
            st.markdown(f"**Last Scraped:** {last_scraped.strftime('%Y-%m-%d %H:%M')}")
        
        if profile.get('next_scrape_due'):
            next_scrape = datetime.fromtimestamp(profile['next_scrape_due'])
            st.markdown(f"**Next Scrape:** {next_scrape.strftime('%Y-%m-%d %H:%M')}")
    
    with col2:
        st.subheader("Actions")
        
        # Force scrape button
        if st.button("🔄 Force Scrape Now", use_container_width=True):
            with st.spinner("Starting scrape in background..."):
                if api_client.force_scrape_task(profile['_id']):
                    st.success("Scraping initiated! Monitoring status...")
                    st.session_state.monitor_task_id = profile['_id']
                else:
                    st.error("Failed to initiate scraping")
        
        # Update scrape interval
        with st.expander("⚙️ Scrape Settings"):
            current_interval = profile.get('scrape_interval_days', 2)
            new_interval = st.number_input(
                "Scrape Interval (days)", 
                min_value=0.5, 
                max_value=30.0, 
                value=float(current_interval),
                step=0.5
            )
            
            if st.button("Update Interval"):
                if api_client.update_scrape_interval(profile['_id'], new_interval):
                    st.success("Interval updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update interval")
    
    st.markdown("---")

    # Always show current task status with enhanced logs (persists across reloads)
    st.subheader("📊 Task Status")
    
    # Add logs count selector
    col1, col2 = st.columns([1, 3])
    with col1:
        logs_to_show = st.selectbox(
            "Logs to show:",
            options=[5, 10, 20, 50, 100],
            index=1,  # Default to 10
            key=f"profile_logs_count_{profile['_id']}"
        )
    with col2:
        if st.button("🔄 Refresh Status", key=f"refresh_profile_status_{profile['_id']}", type="secondary"):
            st.rerun()
    
    # Get enhanced status with selected logs count
    current_status = api_client.get_task_status(profile['_id'], logs_count=logs_to_show)
    
    if current_status:
        if current_status.get('is_processing'):
            st.info("⏳ Task is processing...")
            
            # Display logs if available
            if current_status.get('logs'):
                logs = current_status['logs']
                st.success(f"📊 Showing {len(logs)} latest logs (Total available: {current_status.get('logs_count', 0)})")
                
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
                latest_event = current_status.get('latest_event')
                if latest_event:
                    st.markdown("---")
                    st.subheader("🎯 Latest Event Summary")
                    st.markdown(f"**Event:** {latest_event.get('event_type', 'Unknown')}")
                    st.markdown(f"**Time:** {datetime.fromtimestamp(latest_event.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')}")
                    st.markdown(f"**Message:** {latest_event.get('message', 'No message')}")
            else:
                # Fallback to basic display
                latest_event = current_status.get('latest_event')
                if latest_event:
                    st.caption(
                        f"Latest: {latest_event.get('event_type', 'event')} at "
                        f"{datetime.fromtimestamp(latest_event.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')}"
                    )
        else:
            st.success("✅ Task is idle/completed")
    else:
        st.warning("⚠️ Unable to fetch task status.")

    # Backward-compat monitor flag: if set and now completed, clear it
    if hasattr(st.session_state, 'monitor_task_id'):
        if not (current_status and current_status.get('is_processing')):
            del st.session_state.monitor_task_id

    # Get detailed task data
    task_details = api_client.get_task_details(profile['_id'])
    
    # Support both 'posts', 'scraped_posts', and nested 'target_profile_data.scraped_posts'
    posts_list = None
    if task_details:
        posts_list = (
            task_details.get('posts')
            or task_details.get('scraped_posts')
            or task_details.get('target_profile_data', {}).get('scraped_posts')
        )
    
    if posts_list:
        st.subheader("📈 Recent Posts Analysis")
        posts = posts_list
        
        # Create metrics
        def get_like_count(p):
            return p.get('likes', p.get('likes_count', 0))
        def get_comment_count(p):
            return p.get('comments_count', p.get('comments', 0))

        total_likes = sum(get_like_count(post) for post in posts)
        total_comments = sum(get_comment_count(post) for post in posts)
        avg_likes = total_likes / len(posts) if posts else 0
        avg_comments = total_comments / len(posts) if posts else 0
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Posts", len(posts))
        with col2:
            st.metric("Total Likes", f"{total_likes:,}")
        with col3:
            st.metric("Total Comments", f"{total_comments:,}")
        with col4:
            st.metric("Avg Likes/Post", f"{avg_likes:.0f}")
        
        # Posts table
        st.subheader("📋 Recent Posts")
        posts_data = []
        for post in posts[:10]:  # Show last 10 posts
            caption = post.get('caption', '')
            if caption and len(caption) > 100:
                caption = caption[:100] + '...'
            posts_data.append({
                'Caption': caption,
                'Likes': get_like_count(post),
                'Comments': get_comment_count(post),
                'Date': datetime.fromtimestamp(post.get('timestamp', 0)).strftime('%Y-%m-%d') if post.get('timestamp') else 'Unknown'
            })
        
        if posts_data:
            df = pd.DataFrame(posts_data)
            st.dataframe(df, use_container_width=True)

        # Per-post comments and sentiment details
        st.subheader("💬 Comments & Sentiment (per post)")
        emoji_map = Config.SENTIMENT_CONFIG["emoji_map"]
        for idx, post in enumerate(posts[:10]):
            caption_full = post.get('caption', '') or ''
            date_str = (
                datetime.fromtimestamp(post.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M')
                if post.get('timestamp') else 'Unknown'
            )
            header = f"Post {idx+1} • {date_str}"
            with st.expander(header, expanded=False):
                # Basic metrics
                colm1, colm2, colm3, colm4 = st.columns(4)
                with colm1:
                    st.metric("Likes", f"{get_like_count(post):,}")
                with colm2:
                    st.metric("Comments", f"{get_comment_count(post):,}")
                with colm3:
                    views = post.get('video_view_count', 0)
                    if views:
                        st.metric("Views", f"{views:,}")
                with colm4:
                    st.metric("Type", post.get('type', 'Unknown'))

                st.markdown("**Caption:**")
                st.write(caption_full)

                # Sentiment from top_comments
                top_comments = post.get('top_comments', []) or []
                if top_comments:
                    counts = {"positive": 0, "negative": 0, "neutral": 0}
                    for c in top_comments:
                        s = (c.get('sentiment') or 'neutral').lower()
                        if s not in counts:
                            s = 'neutral'
                        counts[s] += 1
                    total = sum(counts.values()) or 1
                    percentages = {k: (v / total) * 100 for k, v in counts.items()}

                    colc1, colc2 = st.columns([1, 1])
                    with colc1:
                        st.markdown("**Sentiment Summary:**")
                        for s in ["positive", "neutral", "negative"]:
                            emoji = emoji_map.get(s, "😐")
                            st.markdown(f"{emoji} {s.capitalize()}: {counts[s]} ({percentages[s]:.1f}%)")
                    with colc2:
                        try:
                            fig = px.pie(values=list(counts.values()), names=list(counts.keys()), title="Sentiment")
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception:
                            pass

                    st.markdown("**Top Comments:**")
                    for c in top_comments:
                        s = (c.get('sentiment') or 'neutral').lower()
                        emoji = emoji_map.get(s, "😐")
                        username = c.get('owner_username', 'unknown')
                        text = c.get('text', '')
                        likes = c.get('likes_count', 0)
                        ts = c.get('timestamp')
                        ts_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M') if ts else 'Unknown'
                        st.markdown(f"{emoji} **@{username}** ({ts_str})  |  ❤️ {likes}\n\n{text}")
                else:
                    st.info("No top comments available for this post.")
        
        # Sentiment analysis with improved visualization
        sentiment_summary = api_client.get_sentiment_summary(profile['_id'])
        if sentiment_summary:
            display_sentiment_analysis(sentiment_summary)
    else:
        st.info("No scraped data available. Click 'Force Scrape Now' to get the latest data.") 