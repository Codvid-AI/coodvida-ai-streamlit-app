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
            with st.spinner("Scraping profile data..."):
                if api_client.force_scrape_task(profile['_id']):
                    st.success("Scraping initiated successfully!")
                    time.sleep(2)
                    st.rerun()
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
    
    # Get detailed task data
    task_details = api_client.get_task_details(profile['_id'])
    
    if task_details and task_details.get('posts'):
        st.subheader("📈 Recent Posts Analysis")
        
        posts = task_details['posts']
        
        # Create metrics
        total_likes = sum(post.get('likes', 0) for post in posts)
        total_comments = sum(post.get('comments_count', 0) for post in posts)
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
            posts_data.append({
                'Caption': post.get('caption', '')[:100] + '...' if len(post.get('caption', '')) > 100 else post.get('caption', ''),
                'Likes': post.get('likes', 0),
                'Comments': post.get('comments_count', 0),
                'Date': datetime.fromtimestamp(post.get('timestamp', 0)).strftime('%Y-%m-%d') if post.get('timestamp') else 'Unknown'
            })
        
        if posts_data:
            df = pd.DataFrame(posts_data)
            st.dataframe(df, use_container_width=True)
        
        # Sentiment analysis with improved visualization
        sentiment_summary = api_client.get_sentiment_summary(profile['_id'])
        if sentiment_summary:
            display_sentiment_analysis(sentiment_summary)
    else:
        st.info("No scraped data available. Click 'Force Scrape Now' to get the latest data.") 