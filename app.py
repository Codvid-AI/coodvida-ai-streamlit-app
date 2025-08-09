import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import time
from typing import Optional, Dict, Any, List
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="Instagram Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile-friendly design
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 3rem;
        font-size: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .profile-card {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .info-message {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
    }
    .stSelectbox > div > div > select {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'session_token' not in st.session_state:
    st.session_state.session_token = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'current_project' not in st.session_state:
    st.session_state.current_project = None
if 'current_profile' not in st.session_state:
    st.session_state.current_profile = None

# API Configuration
class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session_token = None
    
    def _make_request(self, endpoint: str, method: str = "POST", data: dict = None, stream: bool = False):
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.session_token:
            headers["Authorization"] = f"Bearer {self.session_token}"
        
        if data:
            payload = {
                "schema_version": "4.0",
                "data": data
            }
        else:
            payload = None
        
        try:
            if stream:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=payload,
                    stream=True
                )
                return response
            else:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=payload
                )
                return response
        except Exception as e:
            st.error(f"API request failed: {str(e)}")
            return None
    
    def login(self, email: str, password: str) -> bool:
        """Login user"""
        data = {
            "auth_type": "email",
            "email": email,
            "password": password
        }
        
        response = self._make_request("/codvid-ai/auth/login", "POST", data)
        if response and response.status_code == 201:
            result = response.json()
            if result.get("result"):
                self.session_token = result.get("token")
                return True
        return False
    
    def signup(self, email: str, password: str) -> bool:
        """Signup user"""
        data = {
            "auth_type": "email",
            "email": email,
            "password": password
        }
        
        response = self._make_request("/codvid-ai/auth/signup", "POST", data)
        if response and response.status_code == 201:
            result = response.json()
            if result.get("result"):
                self.session_token = result.get("token")
                return True
        return False
    
    def delete_account(self) -> bool:
        """Delete user account"""
        response = self._make_request("/codvid-ai/user/delete-account", "POST")
        if response and response.status_code == 200:
            result = response.json()
            return result.get("result", False)
        return False
    
    def get_project_list(self) -> List[str]:
        """Get user's project list"""
        response = self._make_request("/codvid-ai/project/get-project-list", "POST")
        if response and response.status_code == 200:
            result = response.json()
            if result.get("result"):
                return result["response"].get("project_list", [])
        return []
    
    def create_project(self, project_name: str) -> bool:
        """Create a new project"""
        data = {"project_name": project_name}
        response = self._make_request("/codvid-ai/project/create-project", "POST", data)
        if response and response.status_code == 200:
            result = response.json()
            return result.get("result", False)
        return False
    
    def delete_project(self, project_name: str) -> bool:
        """Delete a project"""
        data = {"project_name": project_name}
        response = self._make_request("/codvid-ai/project/delete-project", "POST", data)
        if response and response.status_code == 200:
            result = response.json()
            return result.get("result", False)
        return False
    
    def get_project_data(self, project_name: str) -> Optional[Dict]:
        """Get project data"""
        data = {"project_name": project_name}
        response = self._make_request("/codvid-ai/project/get-project-data", "POST", data)
        if response and response.status_code == 200:
            result = response.json()
            if result.get("result"):
                return result["response"]["project_data"]
        return None
    
    def ai_chat(self, project_name: str, message: str) -> str:
        """Send message to AI and get response"""
        data = {
            "project_name": project_name,
            "message": {
                "role": "user",
                "type": "text",
                "text": message
            }
        }
        
        response = self._make_request("/codvid-ai/ai/respond", "POST", data, stream=True)
        if response:
            full_response = ""
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                if chunk:
                    try:
                        chunk_data = json.loads(chunk)
                        if chunk_data.get("result"):
                            # Handle streaming response
                            if "response" in chunk_data and "text" in chunk_data["response"]:
                                full_response += chunk_data["response"]["text"]
                    except:
                        continue
            return full_response
        return "Sorry, I couldn't process your request."
    
    # Instagram Tracking Functions
    def create_tracking_task(self, target_profile: str, is_competitor: bool = False) -> Optional[str]:
        """Create Instagram tracking task"""
        data = {
            "target_profile": target_profile,
            "is_competitor": is_competitor
        }
        
        response = self._make_request("/codvid-ai/ig-tracking/create_task", "POST", data)
        if response and response.status_code == 200:
            result = response.json()
            if result.get("result"):
                return result["response"]["task_id"]
        return None
    
    def get_tracking_tasks(self) -> List[Dict]:
        """Get all tracking tasks"""
        response = self._make_request("/codvid-ai/ig-tracking/get_tasks", "GET")
        if response and response.status_code == 200:
            result = response.json()
            if result.get("result"):
                return result["response"]["tasks"]
        return []
    
    def get_task_details(self, task_id: str) -> Optional[Dict]:
        """Get task details"""
        response = self._make_request(f"/codvid-ai/ig-tracking/get_task/{task_id}", "GET")
        if response and response.status_code == 200:
            result = response.json()
            if result.get("result"):
                return result["response"]["task"]
        return None
    
    def force_scrape_task(self, task_id: str) -> bool:
        """Force scrape task"""
        response = self._make_request(f"/codvid-ai/ig-tracking/force_scrape/{task_id}", "POST")
        if response and response.status_code == 200:
            result = response.json()
            return result.get("result", False)
        return False
    
    def delete_tracking_task(self, task_id: str) -> bool:
        """Delete tracking task"""
        response = self._make_request(f"/codvid-ai/ig-tracking/delete_task/{task_id}", "DELETE")
        if response and response.status_code == 200:
            result = response.json()
            return result.get("result", False)
        return False
    
    def update_scrape_interval(self, task_id: str, interval_days: float) -> bool:
        """Update scrape interval"""
        data = {"scrape_interval_days": interval_days}
        response = self._make_request(f"/codvid-ai/ig-tracking/update_scrape_interval/{task_id}", "PUT", data)
        if response and response.status_code == 200:
            result = response.json()
            return result.get("result", False)
        return False
    
    def get_sentiment_summary(self, task_id: str) -> Optional[Dict]:
        """Get sentiment summary"""
        response = self._make_request(f"/codvid-ai/ig-tracking/sentiment_summary/{task_id}", "GET")
        if response and response.status_code == 200:
            result = response.json()
            if result.get("result"):
                return result["response"]["sentiment_summary"]
        return None
    
    # Reel Tracking Functions
    def create_reel_tracking_task(self, project_name: str, reel_url: str, scrape_interval_days: int = 2) -> Optional[str]:
        """Create reel tracking task"""
        data = {
            "project_name": project_name,
            "reel_url": reel_url,
            "scrape_interval_days": scrape_interval_days
        }
        
        response = self._make_request("/codvid-ai/ig-tracking/create_reel_task", "POST", data)
        if response and response.status_code == 200:
            result = response.json()
            if result.get("result"):
                return result["response"]["task_id"]
        return None
    
    def get_project_reel_tasks(self, project_name: str) -> List[Dict]:
        """Get project reel tasks"""
        data = {"project_name": project_name}
        response = self._make_request("/codvid-ai/ig-tracking/get_project_reel_tasks", "POST", data)
        if response and response.status_code == 200:
            result = response.json()
            if result.get("result"):
                return result["response"]["tasks"]
        return []
    
    def force_scrape_reel_task(self, task_id: str) -> bool:
        """Force scrape reel task"""
        response = self._make_request(f"/codvid-ai/ig-tracking/force_scrape_reel/{task_id}", "POST")
        if response and response.status_code == 200:
            result = response.json()
            return result.get("result", False)
        return False

# Initialize API client
api_client = APIClient("https://codvid-ai-backend-development.up.railway.app")

# Navigation functions
def show_login_page():
    """Show login/signup page"""
    st.title("📊 Instagram Analytics Dashboard")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        st.header("Login to Your Account")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if email and password:
                    if api_client.login(email, password):
                        st.session_state.authenticated = True
                        st.session_state.session_token = api_client.session_token
                        st.session_state.current_page = 'dashboard'
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Login failed. Please check your credentials.")
                else:
                    st.error("Please fill in all fields.")
    
    with tab2:
        st.header("Create New Account")
        
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", key="signup_password", placeholder="Choose a password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            submit = st.form_submit_button("Sign Up")
            
            if submit:
                if email and password and confirm_password:
                    if password != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        if api_client.signup(email, password):
                            st.session_state.authenticated = True
                            st.session_state.session_token = api_client.session_token
                            st.session_state.current_page = 'dashboard'
                            st.success("Account created successfully!")
                            st.rerun()
                        else:
                            st.error("Signup failed. Please try again.")
                else:
                    st.error("Please fill in all fields.")

def show_dashboard():
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
    
    # Get tracking tasks
    tasks = api_client.get_tracking_tasks()
    
    # Create new tracking task
    st.header("➕ Create New Tracking Task")
    with st.expander("Add Instagram Profile to Track", expanded=False):
        with st.form("create_task_form"):
            profile_name = st.text_input("Instagram Username", placeholder="e.g., foodxtaste")
            is_competitor = st.checkbox("Track as Competitor (uncheck for Own Profile)")
            submit = st.form_submit_button("Create Tracking Task")
            
            if submit:
                if profile_name:
                    task_id = api_client.create_tracking_task(profile_name, is_competitor)
                    if task_id:
                        st.success(f"✅ Created tracking task for @{profile_name}")
                        st.rerun()
                    else:
                        st.error("❌ Failed to create tracking task")
                else:
                    st.error("Please enter a profile name")
    
    # Display existing tasks
    st.header("📱 Your Instagram Tracking Tasks")
    
    if not tasks:
        st.info("No tracking tasks found. Create your first task above!")
    else:
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

def show_profile_details():
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
        
        # Sentiment analysis
        sentiment_summary = api_client.get_sentiment_summary(profile['_id'])
        if sentiment_summary:
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
    else:
        st.info("No scraped data available. Click 'Force Scrape Now' to get the latest data.")

def show_projects_page():
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
                        st.session_state.current_page = 'project_chat'
                        st.rerun()
                with col3:
                    if st.button("📊 Tracker", key=f"tracker_{project}"):
                        st.session_state.current_project = project
                        st.session_state.current_page = 'project_tracker'
                        st.rerun()

def show_project_chat():
    """Show project chat interface"""
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
    
    # Display chat history
    st.subheader("Chat History")
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**AI:** {message['content']}")
            st.markdown("---")
    
    # Chat input
    st.subheader("Send Message")
    with st.form("chat_form"):
        message = st.text_area("Your message", placeholder="Type your message here...", height=100)
        submit = st.form_submit_button("Send")
        
        if submit and message:
            # Add user message to history
            st.session_state.chat_history.append({'role': 'user', 'content': message})
            
            # Get AI response
            with st.spinner("AI is thinking..."):
                ai_response = api_client.ai_chat(project, message)
                st.session_state.chat_history.append({'role': 'assistant', 'content': ai_response})
            
            st.rerun()

def show_project_tracker():
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
    
    # Create new reel tracking task
    st.header("➕ Add Reel to Track")
    with st.expander("Track Instagram Reel", expanded=False):
        with st.form("create_reel_task_form"):
            reel_url = st.text_input("Instagram Reel URL", placeholder="https://www.instagram.com/reel/...")
            scrape_interval = st.number_input("Scrape Interval (days)", min_value=1, max_value=30, value=2)
            submit = st.form_submit_button("Add Reel")
            
            if submit:
                if reel_url:
                    task_id = api_client.create_reel_tracking_task(project, reel_url, scrape_interval)
                    if task_id:
                        st.success(f"✅ Added reel tracking task")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add reel tracking task")
                else:
                    st.error("Please enter a reel URL")
    
    # Display existing reel tasks
    st.header("📱 Tracked Reels")
    
    reel_tasks = api_client.get_project_reel_tasks(project)
    
    if not reel_tasks:
        st.info("No reel tracking tasks found. Add your first reel above!")
    else:
        for task in reel_tasks:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**Reel ID:** {task.get('reel_id', 'Unknown')}")
                    st.caption(f"URL: {task.get('reel_url', 'N/A')}")
                    st.caption(f"Status: {task.get('status', 'unknown')}")
                    
                    if task.get('reel_data'):
                        reel_data = task['reel_data']
                        st.caption(f"Likes: {reel_data.get('likes', 0):,} | Comments: {reel_data.get('comments', 0):,} | Views: {reel_data.get('views', 0):,}")
                
                with col2:
                    if st.button("🔄 Scrape", key=f"scrape_reel_{task['_id']}"):
                        with st.spinner("Scraping reel data..."):
                            if api_client.force_scrape_reel_task(task['_id']):
                                st.success("Scraping initiated!")
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error("Failed to scrape")
                
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_reel_{task['_id']}"):
                        # Note: Delete function not implemented in original code
                        st.error("Delete function not available")
        
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

# Main app logic
def main():
    """Main app function"""
    if not st.session_state.authenticated:
        show_login_page()
    else:
        # Set API client session token
        api_client.session_token = st.session_state.session_token
        
        # Route to appropriate page
        if st.session_state.current_page == 'dashboard':
            show_dashboard()
        elif st.session_state.current_page == 'profile_details':
            show_profile_details()
        elif st.session_state.current_page == 'projects':
            show_projects_page()
        elif st.session_state.current_page == 'project_chat':
            show_project_chat()
        elif st.session_state.current_page == 'project_tracker':
            show_project_tracker()
        else:
            st.session_state.current_page = 'dashboard'
            show_dashboard()

if __name__ == "__main__":
    main() 