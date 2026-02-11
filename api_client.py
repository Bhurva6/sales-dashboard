"""
API Client for Avante Medicals and IOSPL endpoints
Handles authentication and data fetching from external APIs
"""
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AvanteAPIClient:
    """Client for Avante Medicals API"""
    
    BASE_URL = "http://avantemedicals.com/API/api.php"
    
    CREDENTIALS = {
        "username": "u2vp8kb",
        "password": "asdftuy#$%78@!"
    }
    
    # Default date range
    DEFAULT_START_DATE = "01-01-2025"
    DEFAULT_END_DATE = "31-12-2025"
    
    @classmethod
    def get_avante_sales(cls, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch Avante sales report
        
        Args:
            start_date: Start date in format 'DD-MM-YYYY'
            end_date: End date in format 'DD-MM-YYYY'
            
        Returns:
            Dict with sales data
        """
        start_date = start_date or cls.DEFAULT_START_DATE
        end_date = end_date or cls.DEFAULT_END_DATE
        
        try:
            # Action goes in URL, data in POST body
            url = f"{cls.BASE_URL}?action=get_sales_report"
            payload = {
                "startdate": start_date,
                "enddate": end_date,
                **cls.CREDENTIALS
            }
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Avante sales data fetched successfully for {start_date} to {end_date}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error fetching Avante sales: {str(e)}")
            return {"status": "error", "message": str(e), "report_data": []}
        except Exception as e:
            logger.error(f"❌ Unexpected error in Avante sales: {str(e)}")
            return {"status": "error", "message": str(e), "report_data": []}
    
    @classmethod
    def get_iospl_sales(cls, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch IOSPL sales report
        
        Args:
            start_date: Start date in format 'DD-MM-YYYY'
            end_date: End date in format 'DD-MM-YYYY'
            
        Returns:
            Dict with sales data
        """
        start_date = start_date or cls.DEFAULT_START_DATE
        end_date = end_date or cls.DEFAULT_END_DATE
        
        try:
            # Action goes in URL, data in POST body
            url = f"{cls.BASE_URL}?action=get_iospl_sales_report"
            payload = {
                "startdate": start_date,
                "enddate": end_date,
                **cls.CREDENTIALS
            }
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ IOSPL sales data fetched successfully for {start_date} to {end_date}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error fetching IOSPL sales: {str(e)}")
            return {"status": "error", "message": str(e), "report_data": []}
        except Exception as e:
            logger.error(f"❌ Unexpected error in IOSPL sales: {str(e)}")
            return {"status": "error", "message": str(e), "report_data": []}
    
    @classmethod
    def parse_sales_data(cls, raw_data: List[Dict]) -> Dict[str, Any]:
        """
        Parse raw sales data and calculate statistics
        
        Args:
            raw_data: Raw sales data from API (report_data field)
            
        Returns:
            Dict with parsed statistics
        """
        try:
            if not raw_data:
                return {
                    "total_revenue": 0,
                    "total_quantity": 0,
                    "total_dealers": 0,
                    "total_products": 0,
                    "data": []
                }
            
            total_revenue = 0
            total_quantity = 0
            dealers = set()
            products = set()
            
            for item in raw_data:
                try:
                    # Parse SV (Sales Value) and SQ (Sales Quantity)
                    revenue = float(item.get('SV', 0) or 0)
                    quantity = float(item.get('SQ', 0) or 0)
                    
                    total_revenue += revenue
                    total_quantity += quantity
                    
                    # Track unique dealers and products
                    if item.get('comp_nm'):
                        dealers.add(item.get('comp_nm').strip())
                    if item.get('category_name'):
                        products.add(item.get('category_name').strip())
                except (ValueError, TypeError):
                    continue
            
            return {
                "total_revenue": round(total_revenue, 2),
                "total_quantity": int(total_quantity),
                "total_dealers": len(dealers),
                "total_products": len(products),
                "data": raw_data
            }
        except Exception as e:
            logger.error(f"Error parsing sales data: {str(e)}")
            return {
                "total_revenue": 0,
                "total_quantity": 0,
                "total_dealers": 0,
                "total_products": 0,
                "data": raw_data
            }
    
    @classmethod
    def get_dealer_performance(cls, sales_data: List[Dict]) -> List[Dict]:
        """
        Extract dealer-wise performance from sales data
        
        Args:
            sales_data: List of sales records from report_data
            
        Returns:
            List of dealer performance data
        """
        dealer_stats = {}
        
        for item in sales_data:
            dealer = (item.get('comp_nm') or 'Unknown').strip()
            if dealer not in dealer_stats:
                dealer_stats[dealer] = {
                    "dealer_name": dealer,
                    "total_sales": 0,
                    "total_quantity": 0,
                    "transaction_count": 0
                }
            
            try:
                sales = float(item.get('SV', 0) or 0)
                qty = float(item.get('SQ', 0) or 0)
                dealer_stats[dealer]["total_sales"] += sales
                dealer_stats[dealer]["total_quantity"] += qty
                dealer_stats[dealer]["transaction_count"] += 1
            except (ValueError, TypeError):
                continue
        
        return sorted(
            list(dealer_stats.values()),
            key=lambda x: x['total_sales'],
            reverse=True
        )
    
    @classmethod
    def get_state_performance(cls, sales_data: List[Dict]) -> List[Dict]:
        """
        Extract state-wise performance from sales data
        
        Args:
            sales_data: List of sales records from report_data
            
        Returns:
            List of state performance data
        """
        state_stats = {}
        
        for item in sales_data:
            state = (item.get('state') or 'Unknown').strip()
            if state not in state_stats:
                state_stats[state] = {
                    "state": state,
                    "total_sales": 0,
                    "total_quantity": 0,
                    "transaction_count": 0
                }
            
            try:
                sales = float(item.get('SV', 0) or 0)
                qty = float(item.get('SQ', 0) or 0)
                state_stats[state]["total_sales"] += sales
                state_stats[state]["total_quantity"] += qty
                state_stats[state]["transaction_count"] += 1
            except (ValueError, TypeError):
                continue
        
        return sorted(
            list(state_stats.values()),
            key=lambda x: x['total_sales'],
            reverse=True
        )
    
    @classmethod
    def get_category_performance(cls, sales_data: List[Dict]) -> List[Dict]:
        """
        Extract category/product-wise performance from sales data
        
        Args:
            sales_data: List of sales records from report_data
            
        Returns:
            List of category performance data
        """
        category_stats = {}
        
        for item in sales_data:
            # Use category_name as product identifier
            product = (item.get('category_name') or 'Unknown').strip()
            if product not in category_stats:
                category_stats[product] = {
                    "product_name": product,
                    "parent_category": (item.get('parent_category') or '').strip(),
                    "total_sales": 0,
                    "total_quantity": 0,
                    "transaction_count": 0
                }
            
            try:
                sales = float(item.get('SV', 0) or 0)
                qty = float(item.get('SQ', 0) or 0)
                category_stats[product]["total_sales"] += sales
                category_stats[product]["total_quantity"] += qty
                category_stats[product]["transaction_count"] += 1
            except (ValueError, TypeError):
                continue
        
        return sorted(
            list(category_stats.values()),
            key=lambda x: x['total_sales'],
            reverse=True
        )
    
    @classmethod
    def get_city_performance(cls, sales_data: List[Dict]) -> List[Dict]:
        """
        Extract city-wise performance from sales data
        
        Args:
            sales_data: List of sales records from report_data
            
        Returns:
            List of city performance data
        """
        city_stats = {}
        
        for item in sales_data:
            city = (item.get('city') or 'Unknown').strip()
            if city not in city_stats:
                city_stats[city] = {
                    "city": city,
                    "state": (item.get('state') or '').strip(),
                    "total_sales": 0,
                    "total_quantity": 0,
                    "transaction_count": 0
                }
            
            try:
                sales = float(item.get('SV', 0) or 0)
                qty = float(item.get('SQ', 0) or 0)
                city_stats[city]["total_sales"] += sales
                city_stats[city]["total_quantity"] += qty
                city_stats[city]["transaction_count"] += 1
            except (ValueError, TypeError):
                continue
        
        return sorted(
            list(city_stats.values()),
            key=lambda x: x['total_sales'],
            reverse=True
        )
