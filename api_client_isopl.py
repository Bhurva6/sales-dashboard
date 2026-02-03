"""
API Client for IOSPL ERP Integration
Handles authentication and data fetching from IOSPL ERP API
"""

import requests
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('api_client_isopl.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('api_client_iospl')

class APIClientIOSPL:
    """API Client for IOSPL ERP integration"""
    
    # IOSPL API URL - Same base URL as Avante API
    # Based on Postman collection format: https://{{localhost}}/{{erp_api_folder}}/api.php
    BASE_URL = "https://avantemedicals.com/API/api.php"
    
    # IOSPL Bearer Token (refreshes periodically)
    BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhdmFudGVtZWRpY2Fscy5jb20iLCJhdWQiOiJhdmFudGVtZWRpY2Fscy5jb20iLCJpYXQiOjE3Njk1ODgzOTIsImV4cCI6MTc2OTU5MTk5MiwiZGF0YSI6eyJhcGlfdXNlcl9pZCI6IjEiLCJ1c2VybmFtZSI6InUydnA4a2IifX0.SUFoKecNvls0Fc7V-iHbJrFd3U83PS2aUdgZThCjjpM"
    
    def __init__(self, username: str = None, password: str = None, bearer_token: str = None):
        self.username = username or "u2vp8kb"  # Default fallback
        self.password = password or "asdftuy#$%78@!"
        # Use provided bearer token or class default
        self.token = bearer_token or self.BEARER_TOKEN
        self.refresh_token = None
        self.token_expiry = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'  # Set bearer token immediately
        })
        # Disable SSL verification for development (not recommended for production)
        self.session.verify = False
        # Suppress SSL warnings
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        
    def login(self) -> bool:
        """Authenticate with IOSPL ERP API and get access token"""
        logger.info("=" * 80)
        logger.info("IOSPL LOGIN REQUEST INITIATED")
        logger.info("=" * 80)
        
        try:
            url = f"{self.BASE_URL}?action=login"
            logger.info(f"URL: {url}")
            
            payload = {
                "username": self.username,
                "password": self.password
            }
            logger.debug(f"Username: {self.username}")
            logger.debug(f"Request Payload: {json.dumps(payload, indent=2)}")
            
            response = self.session.post(url, json=payload)
            logger.info(f"Response Status Code: {response.status_code}")
            logger.debug(f"Response Headers: {dict(response.headers)}")
            
            response_text = response.text
            logger.debug(f"Raw Response Text: {response_text}")
            
            response_json = response.json()
            logger.info(f"Response JSON: {json.dumps(response_json, indent=2)}")
            
            # Check if login was successful
            success = response_json.get('status') == 'success'
            logger.debug(f"Login Success Check: {success}")
            
            if success:
                self.token = response_json.get('token')
                self.refresh_token = response_json.get('refresh_token')
                
                # Set token expiry (typically 1 hour from now, but we'll use 3 hours for safety)
                self.token_expiry = datetime.now() + timedelta(hours=3)
                
                # Update session headers with bearer token
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
                
                logger.debug(f"Token Extracted: {self.token[:30]}..." if self.token else "Token: None")
                logger.debug(f"Refresh Token Extracted: {self.refresh_token[:30]}..." if self.refresh_token else "Refresh Token: None")
                logger.info(f"✅ IOSPL LOGIN SUCCESSFUL - Token expires at: {self.token_expiry}")
            else:
                logger.error(f"❌ IOSPL LOGIN FAILED: {response_json.get('message', 'Unknown error')}")
            
            logger.info("=" * 80)
            return success
            
        except Exception as e:
            logger.error(f"❌ IOSPL LOGIN ERROR: {str(e)}")
            logger.info("=" * 80)
            return False
    
    def _ensure_token(self) -> bool:
        """Ensure we have a valid token, refresh if needed"""
        # If token is already set (from bearer token), just return True
        if self.token:
            logger.debug(f"Using existing bearer token: {self.token[:30]}...")
            return True
        
        # Otherwise, try to login to get a new token
        if not self.token or (self.token_expiry and datetime.now() >= self.token_expiry):
            logger.info("Token expired or missing, attempting login...")
            return self.login()
        return True
    
    def get_sales_report(self, start_date: str, end_date: str, period: str = "custom") -> Dict[str, Any]:
        """
        Fetch sales report data from IOSPL API
        
        Args:
            start_date: Start date in DD-MM-YYYY format
            end_date: End date in DD-MM-YYYY format
            period: Period type (custom, month, year, etc.)
        
        Returns:
            Dict with 'success' boolean and 'data' containing report data
        """
        logger.info("=" * 80)
        logger.info("IOSPL GET SALES REPORT REQUEST INITIATED")
        logger.info("=" * 80)
        
        try:
            # Ensure we have a valid token
            if not self._ensure_token():
                logger.error("Failed to obtain authentication token")
                return {"success": False, "message": "Authentication failed", "data": {}}
            
            logger.info(f"Period-based date range: {period}")
            logger.info(f"Date Range - Start: {start_date}, End: {end_date}")
            
            # Validate date format
            try:
                datetime.strptime(start_date, "%d-%m-%Y")
                datetime.strptime(end_date, "%d-%m-%Y")
                logger.debug("✅ Date format validation passed")
            except ValueError as e:
                logger.error(f"❌ Invalid date format: {str(e)}")
                return {"success": False, "message": "Invalid date format", "data": {}}
            
            url = f"{self.BASE_URL}?action=get_sales_report"
            logger.info(f"API URL: {url}")
            
            # According to Postman collection, the body should have startdate and enddate
            payload = {
                "startdate": start_date,
                "enddate": end_date
            }
            logger.debug(f"Request Payload: {json.dumps(payload, indent=2)}")
            logger.debug(f"Request Headers: {json.dumps(dict(self.session.headers), indent=2)}")
            
            response = self.session.post(url, json=payload)
            logger.info(f"Response Status Code: {response.status_code}")
            logger.debug(f"Response Headers: {dict(response.headers)}")
            
            response_json = response.json()
            
            # Check response status
            if response_json.get('status') == 'success':
                logger.info("Response Status: success")
                logger.debug(f"Response Keys: {list(response_json.keys())}")
                
                # According to Postman, report_data is at root level
                report_data = response_json.get('report_data', [])
                logger.info(f"✅ Records returned: {len(report_data)}")
                
                if report_data:
                    logger.debug(f"Sample record (first): {json.dumps(report_data[0], indent=2)}")
                
                logger.info("=" * 80)
                
                # Return in same format as original API for compatibility
                return {
                    "success": True,
                    "message": "Data fetched successfully",
                    "data": {
                        "report_data": report_data,
                        "total_records": len(report_data),
                        "period": period,
                        "date_range": {
                            "start": start_date,
                            "end": end_date
                        }
                    }
                }
            else:
                error_msg = response_json.get('message', 'Unknown error')
                logger.error(f"❌ API Error: {error_msg}")
                logger.info("=" * 80)
                
                return {
                    "success": False,
                    "message": error_msg,
                    "data": {}
                }
                
        except Exception as e:
            logger.error(f"❌ ERROR: {str(e)}")
            logger.info("=" * 80)
            
            return {
                "success": False,
                "message": str(e),
                "data": {}
            }
    
    def logout(self) -> bool:
        """Logout from the IOSPL API"""
        logger.info("=" * 80)
        logger.info("IOSPL LOGOUT REQUEST INITIATED")
        logger.info("=" * 80)
        
        try:
            url = f"{self.BASE_URL}?action=logout"
            
            response = self.session.post(url, json={})
            logger.info(f"Response Status Code: {response.status_code}")
            
            self.token = None
            self.refresh_token = None
            self.token_expiry = None
            
            logger.info("✅ IOSPL LOGOUT SUCCESSFUL")
            logger.info("=" * 80)
            return True
            
        except Exception as e:
            logger.error(f"❌ IOSPL LOGOUT ERROR: {str(e)}")
            logger.info("=" * 80)
            return False
