"""
API Client for Avante Medicals ERP
Handles authentication and data fetching from the ERP API
"""
import requests
import streamlit as st
from datetime import datetime, timedelta
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('api_client.log')
    ]
)
logger = logging.getLogger(__name__)

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
        logger.info("=" * 80)
        logger.info("LOGIN REQUEST INITIATED")
        logger.info("=" * 80)
        logger.info(f"URL: {API_BASE_URL}?action=login")
        logger.debug(f"Username: {username}")
        
        try:
            url = f"{API_BASE_URL}?action=login"
            payload = {"username": username, "password": password}
            
            logger.debug(f"Request Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
                allow_redirects=False,
                verify=False
            )
            
            logger.info(f"Response Status Code: {response.status_code}")
            logger.debug(f"Response Headers: {dict(response.headers)}")
            
            # Check if there's a redirect
            if response.status_code in [301, 302, 303, 307, 308]:
                redirect_url = response.headers.get('Location', 'Unknown')
                logger.warning(f"API redirected to: {redirect_url}")
                return {"success": False, "message": f"API redirected to: {redirect_url}", "raw_response": None}
            
            response.raise_for_status()
            
            # Get raw response text for debugging
            raw_text = response.text
            logger.debug(f"Raw Response Text: {raw_text[:500]}")
            
            try:
                data = response.json()
                logger.info(f"Response JSON: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON response: {raw_text[:200]}")
                return {"success": False, "message": f"Invalid JSON response: {raw_text[:200]}", "raw_response": raw_text}
            
            # Check for successful login - handle multiple response formats
            is_success = (
                data.get("status") == "success" or 
                data.get("success") == True or
                data.get("token") is not None
            )
            
            logger.debug(f"Login Success Check: {is_success}")
            
            if is_success:
                # Extract token from different possible locations
                self.token = data.get("token") or (data.get("data", {}).get("token") if isinstance(data.get("data"), dict) else None)
                self.refresh_token = data.get("refresh_token") or (data.get("data", {}).get("refresh_token") if isinstance(data.get("data"), dict) else None)
                
                logger.debug(f"Token Extracted: {self.token[:20] if self.token else 'None'}...")
                logger.debug(f"Refresh Token Extracted: {self.refresh_token[:20] if self.refresh_token else 'None'}...")
                
                if self.token:
                    # Set token expiry (assuming 1 hour validity, adjust as needed)
                    self.token_expiry = datetime.now() + timedelta(hours=1)
                    logger.info(f"✅ LOGIN SUCCESSFUL - Token expires at: {self.token_expiry}")
                    logger.info("=" * 80)
                    return {"success": True, "message": "Login successful", "raw_response": data}
                else:
                    logger.error("No token received from server")
                    logger.info("=" * 80)
                    return {"success": False, "message": "No token received from server", "raw_response": data}
            else:
                error_msg = data.get("message") or data.get("error") or "Login failed - Invalid credentials"
                logger.error(f"❌ LOGIN FAILED: {error_msg}")
                logger.info("=" * 80)
                return {"success": False, "message": error_msg, "raw_response": data}
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Connection error: {str(e)}", exc_info=True)
            logger.info("=" * 80)
            return {"success": False, "message": f"Connection error: {str(e)}", "raw_response": None}
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid response from server: {str(e)}", exc_info=True)
            logger.info("=" * 80)
            return {"success": False, "message": f"Invalid response from server: {str(e)}", "raw_response": None}
    
    def refresh_access_token(self) -> bool:
        """
        Refresh the access token using the refresh token
        """
        logger.info("=" * 80)
        logger.info("REFRESH ACCESS TOKEN INITIATED")
        logger.info("=" * 80)
        
        if not self.refresh_token:
            logger.error("❌ No refresh token available")
            logger.info("=" * 80)
            return False
        
        try:
            logger.debug("Refresh token request: action=refresh_token")
            
            response = requests.post(
                f"{API_BASE_URL}?action=refresh_token",
                json={"refresh_token": self.refresh_token},
                headers={"Content-Type": "application/json"},
                timeout=30,
                verify=False
            )
            response.raise_for_status()
            logger.info(f"Response Status Code: {response.status_code}")
            
            data = response.json()
            logger.debug(f"Response JSON: {json.dumps(data, indent=2)}")
            
            if data.get("status") == "success" or data.get("token"):
                self.token = data.get("token")
                logger.debug(f"Token Extracted: {self.token[:20] if self.token else 'None'}...")
                
                if data.get("refresh_token"):
                    self.refresh_token = data.get("refresh_token")
                    logger.debug("Refresh token updated")
                
                self.token_expiry = datetime.now() + timedelta(hours=1)
                logger.info(f"✅ TOKEN REFRESH SUCCESSFUL - New expiry: {self.token_expiry}")
                logger.info("=" * 80)
                return True
            
            logger.error(f"❌ Token refresh failed - Unexpected response: {data}")
            logger.info("=" * 80)
            return False
        except Exception as e:
            logger.error(f"❌ Exception during token refresh: {str(e)}", exc_info=True)
            logger.info("=" * 80)
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
        logger.info("=" * 80)
        logger.info("GET PROTECTED DATA INITIATED")
        logger.info("=" * 80)
        logger.info(f"Action: {action}")
        
        if not self.ensure_valid_token():
            logger.error("❌ Authentication required - Invalid or expired token")
            logger.info("=" * 80)
            return {"success": False, "message": "Authentication required"}
        
        try:
            headers_display = {
                "Content-Type": "application/json",
                "Authorization": "Bearer [MASKED]"
            }
            logger.debug(f"Request Headers: {json.dumps(headers_display, indent=2)}")
            
            body = {"action": action}
            if additional_params:
                body.update(additional_params)
            
            logger.debug(f"Request Body: {json.dumps(body, indent=2)}")
            
            response = requests.post(
                f"{API_BASE_URL}?action={action}",
                json=body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.token}"
                },
                timeout=60,
                verify=False
            )
            response.raise_for_status()
            logger.info(f"Response Status Code: {response.status_code}")
            
            data = response.json()
            logger.debug(f"Response JSON: {json.dumps(data, indent=2)}")
            
            logger.info("✅ PROTECTED DATA CALL SUCCESSFUL")
            logger.info("=" * 80)
            return {"success": True, "data": data}
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request error: {str(e)}", exc_info=True)
            logger.info("=" * 80)
            return {"success": False, "message": f"Request error: {str(e)}"}
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid response from server: {str(e)}", exc_info=True)
            logger.info("=" * 80)
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
        logger.info("=" * 80)
        logger.info("GET SALES REPORT REQUEST INITIATED")
        logger.info("=" * 80)
        
        from datetime import datetime
        
        # If period is provided, calculate dates from it
        if period:
            start_date, end_date = self.get_date_range(period)
            logger.info(f"Period-based date range: {period}")
        # Default date range: start of year to today
        else:
            if not start_date:
                start_date = f"01-01-{datetime.now().year}"
            if not end_date:
                end_date = datetime.now().strftime("%d-%m-%Y")
        
        logger.info(f"Date Range - Start: {start_date}, End: {end_date}")
        
        # Validate date format
        try:
            datetime.strptime(start_date, "%d-%m-%Y")
            datetime.strptime(end_date, "%d-%m-%Y")
            logger.debug("✅ Date format validation passed")
        except ValueError as e:
            logger.error(f"❌ Invalid date format: {str(e)}")
            logger.info("=" * 80)
            return {"success": False, "message": f"Invalid date format: {str(e)}. Use DD-MM-YYYY"}
        
        try:
            url = f"{API_BASE_URL}?action=get_sales_report"
            body = {
                "action": "get_sales_report",
                "startdate": start_date,
                "enddate": end_date
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            logger.info(f"API URL: {url}")
            logger.debug(f"Request Payload: {json.dumps(body, indent=2)}")
            logger.debug(f"Request Headers: {json.dumps(headers, indent=2)}")
            
            response = requests.post(
                url,
                json=body,
                headers=headers,
                timeout=60,
                verify=False
            )
            
            logger.info(f"Response Status Code: {response.status_code}")
            logger.debug(f"Response Headers: {dict(response.headers)}")
            
            response.raise_for_status()
            data = response.json()
            
            # Debug logging
            logger.info(f"Response Status: {data.get('status', 'unknown')}")
            logger.debug(f"Response Keys: {list(data.keys())}")
            
            if isinstance(data, dict):
                if 'report_data' in data:
                    records_count = len(data.get('report_data', []))
                    logger.info(f"✅ Records returned: {records_count}")
                    logger.debug(f"Sample record (first): {json.dumps(data['report_data'][0] if records_count > 0 else {}, indent=2)}")
                else:
                    logger.warning("No 'report_data' key in response")
                    logger.debug(f"Full response: {json.dumps(data, indent=2)[:500]}")
            
            logger.info("=" * 80)
            return {"success": True, "data": data}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request error: {str(e)}", exc_info=True)
            logger.info("=" * 80)
            return {"success": False, "message": f"Request error: {str(e)}"}
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error: {str(e)}", exc_info=True)
            logger.info("=" * 80)
            return {"success": False, "message": "Invalid response from server"}
    
    def logout(self) -> dict:
        """
        Logout and invalidate tokens
        """
        logger.info("=" * 80)
        logger.info("LOGOUT INITIATED")
        logger.info("=" * 80)
        
        try:
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
                logger.debug("Authorization header set with token [MASKED]")
            
            logger.info(f"Sending logout request to: {API_BASE_URL}?action=logout")
            
            requests.post(
                f"{API_BASE_URL}?action=logout",
                headers=headers,
                timeout=30,
                verify=False
            )
            logger.info("Logout request sent to API")
            
            # Clear tokens regardless of response
            self.token = None
            self.refresh_token = None
            self.token_expiry = None
            logger.info("✅ All tokens cleared locally")
            logger.info("=" * 80)
            
            return {"success": True, "message": "Logged out successfully"}
        except Exception as e:
            # Clear tokens even on error
            logger.warning(f"Exception during logout: {str(e)}", exc_info=True)
            self.token = None
            self.refresh_token = None
            self.token_expiry = None
            logger.info("All tokens cleared locally despite error")
            logger.info("=" * 80)
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


def fetch_dashboard_data(period: str = "year", start_date: str = None, end_date: str = None, force_refresh: bool = False):
    """
    Fetch data from the API for the dashboard based on time period or date range
    Returns a pandas DataFrame
    
    Args:
        period: One of 'today', 'week', 'month', 'year' (ignored if start_date and end_date are provided)
        start_date: Start date in DD-MM-YYYY format (optional)
        end_date: End date in DD-MM-YYYY format (optional)
        force_refresh: If True, bypass cache and fetch fresh data from API
    """
    import pandas as pd
    import json
    import os
    from datetime import datetime
    
    # Force unique cache key based on dates to prevent Streamlit's implicit caching
    cache_bust_key = f"{start_date}_{end_date}_{period}"
    
    logger.info("=" * 80)
    logger.info("FETCH DASHBOARD DATA INITIATED")
    logger.info("=" * 80)
    logger.info(f"Parameters - Period: {period}, Start Date: {start_date}, End Date: {end_date}, Force Refresh: {force_refresh}")
    logger.info(f"📊 KEY METRICS: Using data for range {start_date} to {end_date}")
    logger.info(f"Cache Buster Key: {cache_bust_key}")
    
    if not st.session_state.authenticated:
        logger.error("❌ User not authenticated")
        logger.info("=" * 80)
        return None
    
    # Create cache key based on dates or period
    if start_date and end_date:
        cache_key = f"api_data_{start_date}_{end_date}"
    else:
        cache_key = f"api_data_{period}"
    
    logger.debug(f"Cache Key: {cache_key}")
    
    # Check if we already have cached data for this period (skip if force_refresh is True)
    if not force_refresh and cache_key in st.session_state and st.session_state.get(cache_key) is not None:
        logger.info(f"✅ Using cached data for: {cache_key}")
        cached_df = st.session_state.get(cache_key)
        logger.info(f"   Cached records: {len(cached_df)} rows")
        
        # VALIDATION: Verify cached data matches the requested date range
        # This prevents stale cache from being returned
        if start_date and end_date:
            try:
                start_datetime = datetime.strptime(start_date, "%d-%m-%Y")
                end_datetime = datetime.strptime(end_date, "%d-%m-%Y")
                
                # Try to find a date column
                date_columns = [col for col in cached_df.columns if 'date' in col.lower() or 'time' in col.lower()]
                
                if date_columns:
                    date_col = date_columns[0]
                    cached_df[date_col] = pd.to_datetime(cached_df[date_col], errors='coerce')
                    min_date = cached_df[date_col].min()
                    max_date = cached_df[date_col].max()
                    
                    # Check if cached data is within the requested range
                    if pd.notna(min_date) and pd.notna(max_date):
                        if min_date.date() >= start_datetime.date() and max_date.date() <= end_datetime.date():
                            logger.info(f"   ✅ Cache validation passed (date range: {min_date.date()} to {max_date.date()})")
                            logger.info("=" * 80)
                            return cached_df
                        else:
                            logger.warning("   ⚠️ Cache validation FAILED:")
                            logger.warning(f"      Requested: {start_date} to {end_date}")
                            logger.warning(f"      Cached:    {min_date.date()} to {max_date.date()}")
                            logger.warning("      Fetching fresh data...")
                    else:
                        # No valid dates found, use cache anyway
                        logger.info("   (No date validation possible - using cache)")
                        logger.info("=" * 80)
                        return cached_df
                else:
                    # No date column, use cache
                    logger.info("   (No date column for validation - using cache)")
                    logger.info("=" * 80)
                    return cached_df
            except Exception as e:
                logger.warning(f"   Cache validation error: {str(e)} - using cache anyway")
                logger.info("=" * 80)
                return cached_df
        else:
            logger.info("=" * 80)
            return cached_df
    
    if force_refresh:
        logger.info("🔄 Force refresh enabled - bypassing cache and fetching from API")
    
    logger.debug("Fetching from API...")
    
    # Convert date strings to datetime objects for client-side filtering if needed
    start_datetime = None
    end_datetime = None
    if start_date and end_date:
        try:
            start_datetime = datetime.strptime(start_date, "%d-%m-%Y")
            end_datetime = datetime.strptime(end_date, "%d-%m-%Y")
            logger.debug(f"Date range converted: {start_datetime} to {end_datetime}")
        except ValueError:
            logger.error(f"❌ Invalid date format: {start_date} to {end_date}")
            st.error("Invalid date format. Please use DD-MM-YYYY format.")
            logger.info("=" * 80)
            return None
    
    # Fetch from API with the appropriate date range
    with st.spinner("Fetching data from API..."):
        logger.debug("Making API call...")
        result = st.session_state.api_client.get_sales_report(period=period, start_date=start_date, end_date=end_date)
        
        data = None
        records = None
        
        if result["success"] and result.get("data"):
            data = result["data"]
            logger.debug("API Response received successfully")
            
            # Check for API error in response (token issue)
            if isinstance(data, dict) and data.get("status") == "error":
                error_msg = data.get("message", "Unknown API error")
                logger.warning(f"API Error in response: {error_msg}")
                
                # If token error, try loading from local sample file
                if "token" in error_msg.lower():
                    sample_file = "sales_data_sample.json"
                    if os.path.exists(sample_file):
                        logger.info(f"Loading fallback data from: {sample_file}")
                        st.info("Loading data from local sample file (API token issue detected)")
                        with open(sample_file, 'r') as f:
                            data = json.load(f)
                    else:
                        logger.error(f"❌ API Error: {error_msg} and no sample file found")
                        st.error(f"API Error: {error_msg}")
                        st.warning("⚠️ **Server Configuration Issue Detected**")
                        logger.info("=" * 80)
                        return None
                else:
                    logger.error(f"❌ API Error: {error_msg}")
                    st.error(f"API Error: {error_msg}")
                    logger.info("=" * 80)
                    return None
        else:
            # API call failed, try loading from local sample file
            sample_file = "sales_data_sample.json"
            if os.path.exists(sample_file):
                logger.warning(f"API call failed, loading fallback from: {sample_file}")
                logger.debug(f"Error: {result.get('message', 'Unknown error')}")
                st.info("Loading data from local sample file")
                with open(sample_file, 'r') as f:
                    data = json.load(f)
            else:
                logger.error(f"❌ Failed to fetch data: {result.get('message', 'Unknown error')}")
                st.error(f"Failed to fetch data: {result.get('message', 'Unknown error')}")
                logger.info("=" * 80)
                return None
        
        # Handle different response structures
        if isinstance(data, dict):
            if "report_data" in data:
                records = data["report_data"]
                logger.debug(f"Using 'report_data' key - {len(records)} records")
            elif "data" in data:
                records = data["data"]
                logger.debug(f"Using 'data' key - {len(records)} records")
            elif "records" in data:
                records = data["records"]
                logger.debug(f"Using 'records' key - {len(records)} records")
            else:
                records = [data]
                logger.debug("Using wrapped data - 1 record")
        elif isinstance(data, list):
            records = data
            logger.debug(f"Data is list - {len(records)} records")
        else:
            logger.error(f"❌ Unexpected data format: {type(data)}")
            st.error("Unexpected data format from API")
            logger.info("=" * 80)
            return None
        
        # Convert to DataFrame
        if records:
            logger.info(f"Converting {len(records)} records to DataFrame...")
            df = pd.DataFrame(records)
            df.columns = df.columns.str.strip()
            logger.debug(f"DataFrame shape: {df.shape}")
            logger.debug(f"Column names: {list(df.columns)}")
            
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
            logger.debug(f"After column mapping: {list(df.columns)}")
            
            # Convert numeric columns
            numeric_cols = ['Qty', 'Value']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    logger.debug(f"Converted {col} to numeric")
            
            # Apply client-side date filtering if we have date bounds
            # This ensures data is correctly filtered even if API doesn't apply filters
            if start_datetime and end_datetime:
                # Try to find and filter by date column if it exists
                date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
                
                if date_columns:
                    # Use the first date column found
                    date_col = date_columns[0]
                    logger.info(f"Found date column: '{date_col}'")
                    try:
                        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                        original_count = len(df)
                        # Filter data within the date range
                        df = df[(df[date_col] >= start_datetime) & (df[date_col] <= end_datetime)]
                        filtered_count = len(df)
                        logger.info(f"✅ Date filtering applied: {original_count} → {filtered_count} records")
                    except Exception as e:
                        logger.warning(f"Could not apply date filter: {str(e)}")
                else:
                    # No date column found - add one by distributing records across the date range
                    logger.info(f"No date column found. Generating dates from {start_date} to {end_date}")
                    
                    # Create a date range and distribute records evenly across it
                    num_records = len(df)
                    num_days = (end_datetime - start_datetime).days + 1
                    
                    # Generate dates by distributing records across the range
                    generated_dates = pd.date_range(start=start_datetime, end=end_datetime, periods=num_records)
                    df['Date'] = generated_dates
                    
                    logger.info(f"✅ Generated {num_records} dates across {num_days} days")
                    st.info(f"ℹ️ Generated dates for records based on selected range ({start_date} to {end_date})")
            
            # Cache the data for this period
            cache_key = f"api_data_{start_date}_{end_date}" if start_date and end_date else f"api_data_{period}"
            st.session_state[cache_key] = df
            logger.info(f"✅ Data cached with key: {cache_key}")
            logger.info(f"Final DataFrame shape: {df.shape}")
            logger.info("=" * 80)
            return df
        else:
            logger.warning("No records returned from API")
            st.warning("No records returned from API")
            logger.info("=" * 80)
            return None


def clear_cached_data():
    """
    Clear cached API data to force a refresh
    """
    st.session_state.api_data = None
