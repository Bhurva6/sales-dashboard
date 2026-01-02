# Date-Based API Request Examples

## Quick Reference

### Dashboard Sidebar Selection → API Request

When a user selects a time period from the sidebar, here's what happens:

---

## Example 1: "Today" Selection

**User Action:** Selects "Today" from sidebar

**Current Date:** January 2, 2026

**Dates Calculated:**
- Start: 02-01-2026
- End: 02-01-2026

**API Request Body:**
```json
{
    "action": "get_sales_report",
    "startdate": "02-01-2026",
    "enddate": "02-01-2026"
}
```

**What API Returns:** All transactions from January 2, 2026 only

---

## Example 2: "This Week" Selection

**User Action:** Selects "This Week" from sidebar

**Current Date:** January 2, 2026 (Thursday)

**Dates Calculated:**
- Start: 30-12-2025 (Monday)
- End: 02-01-2026 (Today)

**API Request Body:**
```json
{
    "action": "get_sales_report",
    "startdate": "30-12-2025",
    "enddate": "02-01-2026"
}
```

**What API Returns:** All transactions from Monday Dec 30 through today

---

## Example 3: "This Month" Selection

**User Action:** Selects "This Month" from sidebar

**Current Date:** January 2, 2026

**Dates Calculated:**
- Start: 01-01-2026 (1st of month)
- End: 02-01-2026 (Today)

**API Request Body:**
```json
{
    "action": "get_sales_report",
    "startdate": "01-01-2026",
    "enddate": "02-01-2026"
}
```

**What API Returns:** All transactions from Jan 1 through today

---

## Example 4: "This Year" Selection

**User Action:** Selects "This Year" from sidebar

**Current Date:** January 2, 2026

**Dates Calculated:**
- Start: 01-01-2026 (Jan 1)
- End: 02-01-2026 (Today)

**API Request Body:**
```json
{
    "action": "get_sales_report",
    "startdate": "01-01-2026",
    "enddate": "02-01-2026"
}
```

**What API Returns:** All transactions from Jan 1, 2026 through today

---

## Python Code Implementation

### From the APIClient class:

```python
# Method 1: Using period parameter
result = api_client.get_sales_report(period="month")

# This internally:
# 1. Calls get_date_range("month")
# 2. Sends request with calculated dates
# 3. Returns filtered data
```

### Getting date range directly:

```python
# Get start and end dates for a period
start_date, end_date = api_client.get_date_range("week")
# Returns: ("30-12-2025", "02-01-2026")

# Then you can use these dates in other API calls
result = api_client.get_sales_report(start_date=start_date, end_date=end_date)
```

---

## Dashboard Usage

### From dashboard.py:

```python
# User selects period from sidebar
selected_period = st.sidebar.selectbox(
    "Select Time Period",
    ["Today", "This Week", "This Month", "This Year"],
    index=2
)

# Map to period code
period_map = {
    "Today": "today",
    "This Week": "week",
    "This Month": "month",
    "This Year": "year"
}

period_code = period_map[selected_period]

# Fetch data with automatic date filtering
df = load_data_by_period(period_code)

# Which calls:
# fetch_dashboard_data(period=period_code)
# Which calls:
# api_client.get_sales_report(period=period_code)
```

---

## Request Headers

All requests include:
```
Content-Type: application/json
```

---

## Response Format

API returns data in one of these formats (all handled automatically):

```json
{
    "status": "success",
    "report_data": [
        {
            "comp_nm": "Dealer Name",
            "city": "City",
            "state": "State",
            "SQ": 100,
            "SV": 50000
        }
    ]
}
```

OR

```json
{
    "success": true,
    "data": [...]
}
```

---

## Debug Mode

To see the actual API requests being sent, check:
1. **Terminal/Console:** Look for `Fetching sales report: DD-MM-YYYY to DD-MM-YYYY`
2. **Network Tab:** Check browser DevTools Network tab for the POST request to `avantemedicals.com/API/api.php`

---

## Common Issues & Solutions

### Issue: Getting data from wrong period
**Solution:** Check the dates in the API request - verify they match the selected time period

### Issue: No data returned
**Solution:** 
- Verify the date range contains actual transaction data
- Check API logs to confirm request was received
- Ensure API's date filtering logic is correct

### Issue: Data not updating when switching periods
**Solution:** Click "Refresh Data" button - clears caches and fetches fresh data

---

## Date Format Important Notes

✅ **Format Used:** DD-MM-YYYY
- January 2, 2026 = 02-01-2026
- December 31, 2025 = 31-12-2025

❌ **NOT used:**
- YYYY-MM-DD (ISO format)
- MM-DD-YYYY (US format)
- DD/MM/YYYY (with slashes)

---

## Caching Strategy

Each time period is cached separately:
- `api_data_today` → Today's data
- `api_data_week` → This week's data
- `api_data_month` → This month's data
- `api_data_year` → This year's data

This ensures switching between periods is instant without refetching from API.

Click "Refresh Data" to clear all caches and fetch fresh data.

---

## Testing Checklist

- [ ] "Today" shows only today's transactions
- [ ] "This Week" shows Monday to today's transactions
- [ ] "This Month" shows Jan 1 to today's transactions
- [ ] "This Year" shows Jan 1, 2026 to today's transactions
- [ ] Metrics update correctly when switching periods
- [ ] Charts reflect period-specific data
- [ ] Refresh button clears cache and fetches new data
- [ ] No errors in browser console or terminal
