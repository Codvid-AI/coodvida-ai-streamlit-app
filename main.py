import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import time
from typing import List, Dict, Optional
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import pages
from pages.login import show_login
from pages.dashboard import show_dashboard
from pages.profile_details import show_profile_details
from pages.projects import show_projects_page
from pages.project_chat import show_project_chat
from pages.project_tracker import show_project_tracker

# Import configuration
from config import Config

# Configure Streamlit page
st.set_page_config(
    page_title=Config.STREAMLIT_CONFIG["page_title"],
    page_icon=Config.STREAMLIT_CONFIG["page_icon"],
    layout=Config.STREAMLIT_CONFIG["layout"],
    initial_sidebar_state=Config.STREAMLIT_CONFIG["initial_sidebar_state"]
)

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
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

class APIClient:
    """API client for interacting with the backend"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session_token = None
    
    def _make_request(self, endpoint: str, method: str = "POST", data: dict = None, stream: bool = False):
        """Make HTTP request to the API"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.session_token:
            headers["Authorization"] = f"Bearer {self.session_token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=30)
            else:
                response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    def login(self, email: str, password: str) -> bool:
        """Login user"""
        data = {
            "schema_version": "4.0",
            "data": {
                "auth_type": "email",
                "email": email,
                "password": password
            }
        }
        
        result = self._make_request("/codvid-ai/auth/login", data=data)
        if result and result.get("result"):
            self.session_token = result.get("token")
            return True
        return False
    
    def signup(self, email: str, password: str) -> bool:
        """Sign up user"""
        data = {
            "schema_version": "4.0",
            "data": {
                "auth_type": "email",
                "email": email,
                "password": password
            }
        }
        
        result = self._make_request("/codvid-ai/auth/signup", data=data)
        return result and result.get("result")
    
    def delete_account(self) -> bool:
        """Delete user account"""
        data = {
            "schema_version": "4.0",
            "data": {}
        }
        
        result = self._make_request("/codvid-ai/user/delete-account", data=data)
        if result and result.get("result"):
            self.session_token = None
            return True
        return False
    
    def get_project_list(self) -> List[str]:
        """Get list of user projects"""
        data = {
            "schema_version": "4.0",
            "data": {}
        }
        
        result = self._make_request("/codvid-ai/project/get-project-list", data=data)
        if result and result.get("result"):
            return result.get("response", {}).get("project_list", [])
        return []
    
    def create_project(self, project_name: str) -> bool:
        """Create a new project"""
        data = {
            "schema_version": "4.0",
            "data": {
                "project_name": project_name
            }
        }
        
        result = self._make_request("/codvid-ai/project/create-project", data=data)
        return result and result.get("result")
    
    def delete_project(self, project_name: str) -> bool:
        """Delete a project"""
        data = {
            "schema_version": "4.0",
            "data": {
                "project_name": project_name
            }
        }
        
        result = self._make_request("/codvid-ai/project/delete-project", data=data)
        return result and result.get("result")
    
    def get_project_data(self, project_name: str) -> Optional[Dict]:
        """Get project data"""
        data = {
            "schema_version": "4.0",
            "data": {
                "project_name": project_name
            }
        }
        
        result = self._make_request("/codvid-ai/project/get-project-data", data=data)
        return result
    
    def ai_chat(self, project_name: str, message: str) -> str:
        """Send message to AI chat"""
        data = {
            "schema_version": "4.0",
            "data": {
                "project_name": project_name,
                "message": message
            }
        }
        
        result = self._make_request("/codvid-ai/ai/respond", data=data)
        if result and result.get("result"):
            return result.get("response", "No response from AI")
        return "Failed to get AI response"
    
    # Instagram Profile Tracking Methods
    def create_tracking_task(self, target_profile: str, is_competitor: bool = False) -> Optional[str]:
        """Create Instagram tracking task"""
        data = {
            "schema_version": "4.0",
            "data": {
                "target_profile": target_profile,
                "is_competitor": is_competitor
            }
        }
        
        result = self._make_request("/codvid-ai/ig-tracking/create_task", data=data)
        if result and result.get("result"):
            return result.get("task_id")
        return None
    
    def get_tracking_tasks(self) -> List[Dict]:
        """Get all tracking tasks"""
        data = {
            "schema_version": "4.0",
            "data": {}
        }
        
        result = self._make_request("/codvid-ai/ig-tracking/get_tasks", data=data)
        if result and result.get("result"):
            return result.get("tasks", [])
        return []
    
    def get_task_details(self, task_id: str) -> Optional[Dict]:
        """Get detailed task information"""
        data = {
            "schema_version": "4.0",
            "data": {}
        }
        
        result = self._make_request(f"/codvid-ai/ig-tracking/get_task/{task_id}", data=data)
        return result
    
    def force_scrape_task(self, task_id: str) -> bool:
        """Force scrape a task"""
        data = {
            "schema_version": "4.0",
            "data": {}
        }
        
        result = self._make_request(f"/codvid-ai/ig-tracking/force_scrape/{task_id}", data=data)
        return result and result.get("result")
    
    def delete_tracking_task(self, task_id: str) -> bool:
        """Delete a tracking task"""
        data = {
            "schema_version": "4.0",
            "data": {}
        }
        
        result = self._make_request(f"/codvid-ai/ig-tracking/delete_task/{task_id}", data=data)
        return result and result.get("result")
    
    def update_scrape_interval(self, task_id: str, interval_days: float) -> bool:
        """Update scrape interval for a task"""
        data = {
            "schema_version": "4.0",
            "data": {
                "scrape_interval_days": interval_days
            }
        }
        
        result = self._make_request(f"/codvid-ai/ig-tracking/update_scrape_interval/{task_id}", method="PUT", data=data)
        return result and result.get("result")
    
    def get_sentiment_summary(self, task_id: str) -> Optional[Dict]:
        """Get sentiment analysis summary"""
        data = {
            "schema_version": "4.0",
            "data": {}
        }
        
        result = self._make_request(f"/codvid-ai/ig-tracking/sentiment_summary/{task_id}", data=data)
        return result
    
    # Instagram Reel Tracking Methods
    def create_reel_tracking_task(self, project_name: str, reel_url: str, scrape_interval_days: int = 2) -> Optional[str]:
        """Create reel tracking task"""
        data = {
            "schema_version": "4.0",
            "data": {
                "project_name": project_name,
                "reel_url": reel_url,
                "scrape_interval_days": scrape_interval_days
            }
        }
        
        result = self._make_request("/codvid-ai/ig-tracking/create_reel_task", data=data)
        if result and result.get("result"):
            return result.get("task_id")
        return None
    
    def get_project_reel_tasks(self, project_name: str) -> List[Dict]:
        """Get reel tracking tasks for a project"""
        data = {
            "schema_version": "4.0",
            "data": {
                "project_name": project_name
            }
        }
        
        result = self._make_request("/codvid-ai/ig-tracking/get_project_reel_tasks", data=data)
        if result and result.get("result"):
            return result.get("tasks", [])
        return []
    
    def force_scrape_reel_task(self, task_id: str) -> bool:
        """Force scrape a reel task"""
        data = {
            "schema_version": "4.0",
            "data": {}
        }
        
        result = self._make_request(f"/codvid-ai/ig-tracking/force_scrape_reel/{task_id}", data=data)
        return result and result.get("result")

def main():
    """Main application"""
    # Get API configuration
    api_url = Config.get_api_url()
    api_client = APIClient(api_url)
    
    # Set session token if available
    if st.session_state.session_token:
        api_client.session_token = st.session_state.session_token
    
    # Page routing
    if not st.session_state.authenticated:
        show_login(api_client)
    else:
        # Update session token
        st.session_state.session_token = api_client.session_token
        
        # Route to appropriate page
        if st.session_state.current_page == 'dashboard':
            show_dashboard(api_client)
        elif st.session_state.current_page == 'profile_details':
            show_profile_details(api_client)
        elif st.session_state.current_page == 'projects':
            show_projects_page(api_client)
        elif st.session_state.current_page == 'project_chat':
            show_project_chat(api_client)
        elif st.session_state.current_page == 'project_tracker':
            show_project_tracker(api_client)
        else:
            st.session_state.current_page = 'dashboard'
            show_dashboard(api_client)

if __name__ == "__main__":
    main() 