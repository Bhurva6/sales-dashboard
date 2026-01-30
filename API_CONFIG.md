# API Configuration Guide

## Setting Up ISOPL API Integration

### Step 1: Update the API URL

Open `api_client_isopl.py` and find this line (around line 26):

```python
BASE_URL = "https://your-isopl-domain.com/api.php"  # Update this with actual URL
```

Replace it with your actual ISOPL API URL. For example:

```python
BASE_URL = "https://isopl.avantemedicals.com/API/api.php"
```

Or if using the variables from your Postman collection:

```python
BASE_URL = "https://{{localhost}}/{{erp_api_folder}}/api.php"
```

Replace `{{localhost}}` and `{{erp_api_folder}}` with actual values.

### Step 2: Update Credentials (Optional)

If ISOPL uses different credentials, you can update the defaults in `api_client_isopl.py` (around line 29-30):

```python
self.username = username or "your_isopl_username"  # Update default
self.password = password or "your_isopl_password"  # Update default
```

### Step 3: Test the Integration

1. **Start the dashboard:**
   ```bash
   python app.py
   ```

2. **Open your browser:**
   ```
   http://localhost:8050
   ```

3. **Test both dashboards:**
   - Click "Overall Dashboard" button (top right) to use the original API
   - Click "ISOPL Dashboard" button (top right) to use the new ISOPL API

### Step 4: Verify API Response Structure

The ISOPL API should return data in this format (as shown in Postman collection):

```json
{
  "status": "success",
  "report_data": [
    {
      "cust_id": "38",
      "comp_nm": "ALTIVATE MEDICARE",
      "city": "VADODARA",
      "state": "GUJARAT",
      "parent_category": "Bone Screw",
      "category_name": "3.5mm Cortical Screw",
      "meta_keyword": "ASC.101-E",
      "SQ": "56",
      "SV": "1412.13"
    }
  ]
}
```

### Field Mapping

The dashboard automatically maps these fields:

| API Field | Dashboard Column |
|-----------|-----------------|
| `SV` | Value (Revenue) |
| `SQ` | Qty (Quantity) |
| `comp_nm` | Dealer Name |
| `category_name` | Category |
| `state` | State |
| `city` | City |
| `meta_keyword` | Product Name |
| `parent_category` | Sub Category |
| `cust_id` | Customer ID |
| `id` | Order ID |

### Troubleshooting

#### Issue: Connection Error
**Solution:** Check that the `BASE_URL` is correct and the server is accessible.

#### Issue: Authentication Failed
**Solution:** Verify the username and password are correct for the ISOPL API.

#### Issue: No Data Returned
**Solution:** 
1. Check the API logs in `api_client_isopl.log`
2. Verify the date range has data
3. Confirm the API endpoint is working (test in Postman)

#### Issue: Different Response Structure
**Solution:** If the ISOPL API returns data in a different format than expected, you may need to adjust the response parsing in `api_client_isopl.py` at the `get_sales_report` method.

### Logs

- **Overall API logs:** `api_client.log`
- **ISOPL API logs:** `api_client_isopl.log`
- **Dashboard logs:** Check console output

### Advanced Configuration

#### Using Environment Variables

For better security, you can use environment variables:

```python
import os

BASE_URL = os.getenv('ISOPL_API_URL', 'https://default-url.com/api.php')
username = os.getenv('ISOPL_USERNAME', 'default_user')
password = os.getenv('ISOPL_PASSWORD', 'default_pass')
```

Then set them in your environment:

```bash
export ISOPL_API_URL="https://your-isopl-domain.com/api.php"
export ISOPL_USERNAME="your_username"
export ISOPL_PASSWORD="your_password"
```

## Features

### Dashboard Toggle
- **Overall Dashboard Button:** Shows data from the original Avante Medicals API
- **ISOPL Dashboard Button:** Shows data from the ISOPL API
- Both dashboards use the exact same UI, charts, and features
- Data is cached separately for each dashboard to optimize performance

### Data Caching
- Each dashboard's data is cached for 5 minutes
- Switching between dashboards retrieves cached data if available
- Click "Refresh Data" to force a new API call

### Status Indicator
The status bar shows:
- Number of records
- Dashboard name (Overall or ISOPL)
- Last updated timestamp

Example: `1,234 records (ISOPL) | Last updated: 14:30:25`

## Need Help?

Check the log files for detailed information about API calls and responses.
