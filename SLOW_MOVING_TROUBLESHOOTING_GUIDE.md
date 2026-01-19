# Troubleshooting: Slow-Moving Items Tracker Not Visible

## Quick Diagnosis Steps

### Step 1: Check Your Dashboard Console

1. Open your dashboard in the browser
2. Open the browser's Developer Tools (F12 or Right-click → Inspect)
3. Go to the **Console** tab
4. Look for log messages when the dashboard loads

### Step 2: Look for These Key Messages

After the dashboard loads, you should see messages like:

```
DASH UPDATE TRIGGERED
   Range: DD-MM-YYYY to DD-MM-YYYY
   ...
   Data fetched: XXX rows
   Available columns: ['SV', 'SQ', 'comp_nm', 'date', ...]
   Column mapping applied: {...}
   Date field(s) found and mapped: ['date']
   Has date data: True
   Date column sample: ...
   Valid dates: XXX out of XXX
```

### Step 3: Diagnose the Issue

#### ✅ If you see: `Has date data: True`
**Status:** Date data is available  
**Expected:** Slow-Moving Items Tracker should be visible  
**If not visible:** Scroll down - it's near the bottom of the page, after the "Funnel and Conversion Analysis" section

#### ⚠️ If you see: `Has date data: False`
**Issue:** Date data is not being recognized

Check for these specific messages:

**A) No date field found:**
```
⚠️ No date field found in API response!
```
**Solution:** Your API is not returning date fields. Check with your API provider.

**B) Date column exists but no valid dates:**
```
Date column exists but no valid dates found
```
**Solution:** The date field exists but contains invalid date formats. Check your API data format.

**C) Available columns don't include date fields:**
```
Available columns: ['SV', 'SQ', 'comp_nm', 'category_name', 'state', 'city']
```
(Notice no 'date', 'order_date', 'created_at', or 'sale_date')

**Solution:** Your API is not returning any date fields at all.

## Common Issues and Solutions

### Issue 1: API Not Returning Date Field

**Symptoms:**
- Console shows: `Available columns: [...]` without any date fields
- Console shows: `⚠️ No date field found in API response!`

**Solutions:**

1. **Check your API response format**
   - Add this to your API client to debug:
   ```python
   print(f"API Response keys: {list(response.get('data', {}).get('report_data', [{}])[0].keys())}")
   ```

2. **Verify API credentials and permissions**
   - Ensure your API account has access to date fields
   - Check if date fields require special permissions

3. **Check API documentation**
   - Verify the actual field name for dates
   - It might be named differently (e.g., 'transaction_date', 'timestamp', 'order_created')

4. **Update column mapping**
   If your API uses a different date field name, update the mapping in `app.py`:
   ```python
   column_mapping = {
       # ... existing mappings ...
       'your_actual_date_field': 'Date',  # Add this line
   }
   ```

### Issue 2: Date Format Not Recognized

**Symptoms:**
- Console shows: `Date column exists but no valid dates found`
- Has date data: False

**Solutions:**

1. **Check date format in API response**
   - Common formats: 'YYYY-MM-DD', 'DD-MM-YYYY', 'MM/DD/YYYY', timestamps
   
2. **Update date conversion**
   If your dates are in a specific format, you may need to explicitly parse them:
   ```python
   df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
   ```

### Issue 3: Tracker Visible But Empty

**Symptoms:**
- Section appears but shows "No products found with no sales..."

**Solutions:**

1. **Reduce the inactivity period**
   - Try selecting "7 Days" instead of "30 Days"
   - Your products might be selling more frequently

2. **Check date range**
   - Ensure you've selected a date range with enough historical data
   - Try selecting "Last 3 Months" from the quick select buttons

3. **Remove filters**
   - Uncheck "Hide 'Innovative Ortho Surgicals'" if checked
   - Clear any category or dealer filters

## Manual Verification

### Test 1: Check if Section is in HTML

1. Open browser Developer Tools (F12)
2. Go to **Elements** tab
3. Press Ctrl+F (or Cmd+F on Mac)
4. Search for: "Slow-Moving Items Tracker"

**If found:** Section is rendered but might be hidden by CSS or collapsed
**If not found:** Date data is not available (see solutions above)

### Test 2: Force Display (Temporary Debug)

To temporarily force the section to display (for debugging only):

1. Find this line in `app.py` (around line 1004):
   ```python
   *([] if not has_date_data else [
   ```

2. Temporarily change to:
   ```python
   *([  # Temporarily force display for debugging
   ```

3. And find the closing `]),` for this section and ensure it's not wrapped in a condition

**Note:** This is only for debugging. Remove this change once you've identified the issue.

## Getting Help

If you're still unable to see the Slow-Moving Items Tracker after trying these steps:

1. **Share Console Output**
   - Copy the relevant console messages
   - Share the "Available columns" list
   - Share any error messages

2. **Check API Response**
   - Share a sample of your API response (remove sensitive data)
   - Specifically show what fields are returned

3. **Verify Date Range**
   - Confirm you've selected a date range
   - Try different date ranges (last week, last month, last 3 months)

## Quick Fix Checklist

- [ ] Date range is selected in the sidebar
- [ ] Console shows `Has date data: True`
- [ ] No JavaScript errors in console
- [ ] Scrolled down to the bottom of the Dashboard tab
- [ ] API is returning date fields
- [ ] Date fields are in a recognized format
- [ ] Not all products are fast-moving (try reducing inactivity period)

## Expected Location

The Slow-Moving Items Tracker appears:
1. In the **Dashboard** tab (not "My Charts")
2. Below the "Funnel and Conversion Analysis" section
3. Above the "Custom Chart Builder" section
4. Near the bottom of the page

Look for the heading: **📦 Slow-Moving Items Tracker**
