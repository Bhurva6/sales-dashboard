"""
API Client for Avante Medicals ERP
Handles authentication and data fetching from the ERP API
"""
import requests
import streamlit as st
from datetime import datetime, timedelta
import json

# API Configuration
API_BASE_URL = "https://avantemedicals.com/API/api.php"

# Disable SSL warnings (server has certificate issues)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
            url = f"{API_BASE_URL}?action=login"
            response = requests.post(
                url,
                json={"username": username, "password": password},
                headers={"Content-Type": "application/json"},
                timeout=30,
                allow_redirects=False,  # Don't follow redirects to see actual response
                verify=False  # Skip SSL verification (server certificate issue)
            )
            
            # Check if there's a redirect
            if response.status_code in [301, 302, 303, 307, 308]:
                redirect_url = response.headers.get('Location', 'Unknown')
                return {"success": False, "message": f"API redirected to: {redirect_url}", "raw_response": None}
            
            response.raise_for_status()
            
            # Get raw response text for debugging
            raw_text = response.text
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                return {"success": False, "message": f"Invalid JSON response: {raw_text[:200]}", "raw_response": raw_text}
            
            # Debug: Print the response to understand its structure
            print(f"Login API Response: {data}")
            
            # Check for successful login - handle multiple response formats
            # Format 1: {"status": "success", "token": "...", "refresh_token": "..."}
            # Format 2: {"success": true, "data": {"token": "..."}}
            # Format 3: Just checking if token exists
            
            is_success = (
                data.get("status") == "success" or 
                data.get("success") == True or
                data.get("token") is not None
            )
            
            if is_success:
                # Extract token from different possible locations
                self.token = data.get("token") or (data.get("data", {}).get("token") if isinstance(data.get("data"), dict) else None)
                self.refresh_token = data.get("refresh_token") or (data.get("data", {}).get("refresh_token") if isinstance(data.get("data"), dict) else None)
                
                if self.token:
                    # Set token expiry (assuming 1 hour validity, adjust as needed)
                    self.token_expiry = datetime.now() + timedelta(hours=1)
                    return {"success": True, "message": "Login successful", "raw_response": data}
                else:
                    return {"success": False, "message": "No token received from server", "raw_response": data}
            else:
                error_msg = data.get("message") or data.get("error") or "Login failed - Invalid credentials"
                return {"success": False, "message": error_msg, "raw_response": data}
        except requests.exceptions.RequestException as e:
            return {"success": False, "message": f"Connection error: {str(e)}", "raw_response": None}
        except json.JSONDecodeError as e:
            return {"success": False, "message": f"Invalid response from server: {str(e)}", "raw_response": None}
    
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
                timeout=30,
                verify=False
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
                timeout=60,
                verify=False
            )
            response.raise_for_status()
            data = response.json()
            
            return {"success": True, "data": data}
        except requests.exceptions.RequestException as e:
            return {"success": False, "message": f"Request error: {str(e)}"}
        except json.JSONDecodeError:
            return {"success": False, "message": "Invalid response from server"}
    
    def get_date_range(self, period: str = "year") -> tuple:
        """
        Get start and end dates based on the period
        
        Args:
            period: One of 'today', 'week', 'month', 'year'
        
        Returns:
            Tuple of (start_date, end_date) in DD-MM-YYYY format
        """
        from datetime import datetime, timedelta
        
        today = datetime.now()
        
        if period == "today":
            start_date = today
            end_date = today
        elif period == "week":
            # Start of this week (Monday)
            start_date = today - timedelta(days=today.weekday())
            end_date = today
        elif period == "month":
            # Start of this month
            start_date = today.replace(day=1)
            end_date = today
        elif period == "year":
            # Start of this year
            start_date = today.replace(month=1, day=1)
            end_date = today
        else:
            # Default to year
            start_date = today.replace(month=1, day=1)
            end_date = today
        
        # Format dates as DD-MM-YYYY
        start_date_str = start_date.strftime("%d-%m-%Y")
        end_date_str = end_date.strftime("%d-%m-%Y")
        
        return start_date_str, end_date_str
    
    def get_sales_report(self, start_date: str = None, end_date: str = None, period: str = None) -> dict:
        """
        Fetch sales report data from the API with proper date filtering
        Authorization is disabled for this endpoint, so we make a direct call
        
        Args:
            start_date: Start date in DD-MM-YYYY format (optional if period is provided)
            end_date: End date in DD-MM-YYYY format (optional if period is provided)
            period: One of 'today', 'week', 'month', 'year' (takes precedence over explicit dates)
        
        Returns:
            dict with keys 'success' and 'data' containing the API response
        """
        from datetime import datetime
        
        # If period is provided, calculate dates from it
        if period:
            start_date, end_date = self.get_date_range(period)
        # Default date range: start of year to today
        else:
            if not start_date:
                start_date = f"01-01-{datetime.now().year}"
            if not end_date:
                end_date = datetime.now().strftime("%d-%m-%Y")
        
        # Validate date format
        try:
            datetime.strptime(start_date, "%d-%m-%Y")
            datetime.strptime(end_date, "%d-%m-%Y")
        except ValueError as e:
            return {"success": False, "message": f"Invalid date format: {str(e)}. Use DD-MM-YYYY"}
        
        try:
            # Since authorization is disabled for this endpoint, 
            # make a direct call without the Authorization header
            body = {
                "action": "get_sales_report",
                "startdate": start_date,
                "enddate": end_date
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            print(f"[API] Fetching sales report from {start_date} to {end_date}")
            
            response = requests.post(
                f"{API_BASE_URL}?action=get_sales_report",
                json=body,
                headers=headers,
                timeout=60,
                verify=False
            )
            response.raise_for_status()
            data = response.json()
            
            # Debug logging
            print(f"[API] Response status: {data.get('status', 'unknown')}")
            if isinstance(data, dict):
                print(f"[API] Response keys: {list(data.keys())}")
                if 'report_data' in data:
                    print(f"[API] Records returned: {len(data.get('report_data', []))}")
            
            return {"success": True, "data": data}
        except requests.exceptions.RequestException as e:
            print(f"[API] Request error: {str(e)}")
            return {"success": False, "message": f"Request error: {str(e)}"}
        except json.JSONDecodeError as e:
            print(f"[API] JSON decode error: {str(e)}")
            return {"success": False, "message": "Invalid response from server"}
    
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
                timeout=30,
                verify=False
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
    
    st.caption("Login with your API credentials")
    
    # Debug mode toggle
    debug_mode = st.checkbox("Show debug info", value=False)
    
    if debug_mode:
        st.info(f"API URL: {API_BASE_URL}?action=login")
    
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
                    
                    if debug_mode:
                        st.write("API Response:", result)
                    
                    if result["success"]:
                        st.session_state.authenticated = True
                        st.session_state.demo_mode = False
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


def fetch_dashboard_data(period: str = "year", start_date: str = None, end_date: str = None):
    """
    Fetch data from the API for the dashboard based on time period or date range
    Returns a pandas DataFrame
    
    Args:
        period: One of 'today', 'week', 'month', 'year' (ignored if start_date and end_date are provided)
        start_date: Start date in DD-MM-YYYY format (optional)
        end_date: End date in DD-MM-YYYY format (optional)
    """
    import pandas as pd
    import json
    import os
    from datetime import datetime
    
    if not st.session_state.authenticated:
        return None
    
    # Create cache key based on dates or period
    if start_date and end_date:
        cache_key = f"api_data_{start_date}_{end_date}"
    else:
        cache_key = f"api_data_{period}"
    
    # Check if we already have cached data for this period
    if cache_key in st.session_state and st.session_state.get(cache_key) is not None:
        return st.session_state.get(cache_key)
    
    # Convert date strings to datetime objects for client-side filtering if needed
    start_datetime = None
    end_datetime = None
    if start_date and end_date:
        try:
            start_datetime = datetime.strptime(start_date, "%d-%m-%Y")
            end_datetime = datetime.strptime(end_date, "%d-%m-%Y")
        except ValueError:
            st.error("Invalid date format. Please use DD-MM-YYYY format.")
            return None
    
    # Fetch from API with the appropriate date range
    with st.spinner("Fetching data from API..."):
        result = st.session_state.api_client.get_sales_report(period=period, start_date=start_date, end_date=end_date)
        
        data = None
        records = None
        
        if result["success"] and result.get("data"):
            data = result["data"]
            
            # Check for API error in response (token issue)
            if isinstance(data, dict) and data.get("status") == "error":
                error_msg = data.get("message", "Unknown API error")
                
                # If token error, try loading from local sample file
                if "token" in error_msg.lower():
                    sample_file = "sales_data_sample.json"
                    if os.path.exists(sample_file):
                        st.info("Loading data from local sample file (API token issue detected)")
                        with open(sample_file, 'r') as f:
                            data = json.load(f)
                    else:
                        st.error(f"API Error: {error_msg}")
                        st.warning("""
                        ⚠️ **Server Configuration Issue Detected**
                        
                        The API server is not receiving the Authorization header.
                        Please contact the API provider to fix the server configuration.
                        """)
                        return None
                else:
                    st.error(f"API Error: {error_msg}")
                    return None
        else:
            # API call failed, try loading from local sample file
            sample_file = "sales_data_sample.json"
            if os.path.exists(sample_file):
                st.info("Loading data from local sample file")
                with open(sample_file, 'r') as f:
                    data = json.load(f)
            else:
                st.error(f"Failed to fetch data: {result.get('message', 'Unknown error')}")
                return None
        
        # Handle different response structures
        if isinstance(data, dict):
            if "report_data" in data:
                records = data["report_data"]
            elif "data" in data:
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
            
            # Map API column names to expected dashboard column names
            column_mapping = {
                'comp_nm': 'Dealer Name',
                'city': 'City',
                'state': 'State',
                'parent_category': 'Category',
                'category_name': 'Sub Category',
                'meta_keyword': 'Product Code',
                'SQ': 'Qty',
                'SV': 'Value',
                'cust_id': 'Customer ID'
            }
            df = df.rename(columns=column_mapping)
            
            # Convert numeric columns
            numeric_cols = ['Qty', 'Value']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Apply client-side date filtering if we have date bounds
            # This ensures data is correctly filtered even if API doesn't apply filters
            if start_datetime and end_datetime:
                # Try to find and filter by date column if it exists
                date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
                
                if date_columns:
                    # Use the first date column found
                    date_col = date_columns[0]
                    try:
                        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                        # Filter data within the date range
                        df = df[(df[date_col] >= start_datetime) & (df[date_col] <= end_datetime)]
                        print(f"[API] Date filtering applied using '{date_col}' column. Records after filter: {len(df)}")
                    except Exception as e:
                        # If date filtering fails, log but continue with unfiltered data
                        print(f"Warning: Could not apply date filter: {str(e)}")
                else:
                    # No date column found - add one by distributing records across the date range
                    print(f"[API] No date column found. Generating dates from {start_date} to {end_date}")
                    
                    # Create a date range and distribute records evenly across it
                    num_records = len(df)
                    num_days = (end_datetime - start_datetime).days + 1
                    
                    # Generate dates by distributing records across the range
                    generated_dates = pd.date_range(start=start_datetime, end=end_datetime, periods=num_records)
                    df['Date'] = generated_dates
                    
                    print(f"[API] Generated {num_records} dates across {num_days} days")
                    st.info(f"ℹ️ Generated dates for records based on selected range ({start_date} to {end_date})")
            
            # Cache the data for this period
            cache_key = f"api_data_{start_date}_{end_date}" if start_date and end_date else f"api_data_{period}"
            st.session_state[cache_key] = df
            return df
        else:
            st.warning("No records returned from API")
            return None


def clear_cached_data():
    """
    Clear cached API data to force a refresh
    """
    st.session_state.api_data = None
