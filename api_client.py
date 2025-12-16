"""
API Client for Avante Medicals ERP
Handles authentication and data fetching from the ERP API
"""
import requests
import streamlit as st
from datetime import datetime, timedelta
import json

# API Configuration
API_BASE_URL = "http://avantemedicals.com/API/api.php"

class APIClient:
    def __init__(self):
        self.token = None
        self.refresh_token = None
        self.token_expiry = None
    
    def login(self, username: str, password: str) -> dict:
        """
        Authenticate user and obtain access tokens
        """
        try:
            response = requests.post(
                f"{API_BASE_URL}?action=login",
                json={"username": username, "password": password},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "success":
                self.token = data.get("token")
                self.refresh_token = data.get("refresh_token")
                # Set token expiry (assuming 1 hour validity, adjust as needed)
                self.token_expiry = datetime.now() + timedelta(hours=1)
                return {"success": True, "message": "Login successful"}
            else:
                return {"success": False, "message": data.get("message", "Login failed")}
        except requests.exceptions.RequestException as e:
            return {"success": False, "message": f"Connection error: {str(e)}"}
        except json.JSONDecodeError:
            return {"success": False, "message": "Invalid response from server"}
    
    def refresh_access_token(self) -> bool:
        """
        Refresh the access token using the refresh token
        """
        if not self.refresh_token:
            return False
        
        try:
            response = requests.post(
                f"{API_BASE_URL}?action=refresh_token",
                json={"refresh_token": self.refresh_token},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "success" or data.get("token"):
                self.token = data.get("token")
                if data.get("refresh_token"):
                    self.refresh_token = data.get("refresh_token")
                self.token_expiry = datetime.now() + timedelta(hours=1)
                return True
            return False
        except:
            return False
    
    def is_token_valid(self) -> bool:
        """
        Check if the current token is valid
        """
        if not self.token or not self.token_expiry:
            return False
        return datetime.now() < self.token_expiry
    
    def ensure_valid_token(self) -> bool:
        """
        Ensure we have a valid token, refreshing if necessary
        """
        if self.is_token_valid():
            return True
        if self.refresh_token:
            return self.refresh_access_token()
        return False
    
    def get_protected_data(self, action: str = "protected", additional_params: dict = None) -> dict:
        """
        Make a protected API call
        """
        if not self.ensure_valid_token():
            return {"success": False, "message": "Authentication required"}
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            }
            
            body = {"action": action}
            if additional_params:
                body.update(additional_params)
            
            response = requests.post(
                f"{API_BASE_URL}?action={action}",
                json=body,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            return {"success": True, "data": data}
        except requests.exceptions.RequestException as e:
            return {"success": False, "message": f"Request error: {str(e)}"}
        except json.JSONDecodeError:
            return {"success": False, "message": "Invalid response from server"}
    
    def get_sales_report(self) -> dict:
        """
        Fetch sales report data from the API
        """
        return self.get_protected_data("get_sales_report")
    
    def logout(self) -> dict:
        """
        Logout and invalidate tokens
        """
        try:
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            
            response = requests.post(
                f"{API_BASE_URL}?action=logout",
                headers=headers,
                timeout=30
            )
            
            # Clear tokens regardless of response
            self.token = None
            self.refresh_token = None
            self.token_expiry = None
            
            return {"success": True, "message": "Logged out successfully"}
        except:
            # Clear tokens even on error
            self.token = None
            self.refresh_token = None
            self.token_expiry = None
            return {"success": True, "message": "Logged out"}


def init_session_state():
    """
    Initialize session state for API client
    """
    if 'api_client' not in st.session_state:
        st.session_state.api_client = APIClient()
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'api_data' not in st.session_state:
        st.session_state.api_data = None


def login_form():
    """
    Display login form and handle authentication
    """
    st.title("Login to Dashboard")
    st.markdown("---")
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit:
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                with st.spinner("Authenticating..."):
                    result = st.session_state.api_client.login(username, password)
                    if result["success"]:
                        st.session_state.authenticated = True
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(f"Login failed: {result['message']}")


def logout_button():
    """
    Display logout button in sidebar
    """
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.api_client.logout()
        st.session_state.authenticated = False
        st.session_state.api_data = None
        st.rerun()


def fetch_dashboard_data():
    """
    Fetch data from the API for the dashboard
    Returns a pandas DataFrame
    """
    import pandas as pd
    
    if not st.session_state.authenticated:
        return None
    
    # Check if we already have cached data
    if st.session_state.api_data is not None:
        return st.session_state.api_data
    
    with st.spinner("Fetching data from API..."):
        result = st.session_state.api_client.get_sales_report()
        
        if result["success"] and result.get("data"):
            data = result["data"]
            
            # Handle different response structures
            if isinstance(data, dict):
                if "data" in data:
                    # Nested data structure
                    records = data["data"]
                elif "records" in data:
                    records = data["records"]
                else:
                    records = [data]
            elif isinstance(data, list):
                records = data
            else:
                st.error("Unexpected data format from API")
                return None
            
            # Convert to DataFrame
            if records:
                df = pd.DataFrame(records)
                df.columns = df.columns.str.strip()
                st.session_state.api_data = df
                return df
            else:
                st.warning("No records returned from API")
                return None
        else:
            st.error(f"Failed to fetch data: {result.get('message', 'Unknown error')}")
            return None


def clear_cached_data():
    """
    Clear cached API data to force a refresh
    """
    st.session_state.api_data = None
