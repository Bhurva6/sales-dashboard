# 🔄 Dual API Setup Guide - Avante & IOSPL

This guide explains how to configure **two separate APIs** for the dashboard - one for **Avante** and one for **IOSPL**.

---

## 📋 Overview

The dashboard supports **two independent API sources**:

1. **Avante API** - Original ERP system
2. **IOSPL API** - Secondary/alternative ERP system

Users can switch between these dashboards using the toggle buttons in the header.

---

## 🔧 Current Configuration

### ✅ Avante API (Original)
- **File**: `api_client.py`
- **Endpoint**: `https://avantemedicals.com/API/api.php`
- **Authentication**: Username/Password → JWT Token
- **Status**: ✅ **Fully Configured & Working**

### 🔵 IOSPL API (New)
- **File**: `api_client_isopl.py`
- **Endpoint**: `https://avantemedicals.com/API/api.php` (⚠️ Currently same as Avante)
- **Authentication**: Bearer Token (Pre-configured)
- **Current Bearer Token**: 
  ```
  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhdmFudGVtZWRpY2Fscy5jb20iLCJhdWQiOiJhdmFudGVtZWRpY2Fscy5jb20iLCJpYXQiOjE3Njk1ODgzOTIsImV4cCI6MTc2OTU5MTk5MiwiZGF0YSI6eyJhcGlfdXNlcl9pZCI6IjEiLCJ1c2VybmFtZSI6InUydnA4a2IifX0.SUFoKecNvls0Fc7V-iHbJrFd3U83PS2aUdgZThCjjpM
  ```
- **Status**: ⚠️ **Same data source as Avante (needs different endpoint if separate data is required)**

---

## 🎯 Verification Results

Based on testing (see `verify_iospl_api.py`), both APIs currently return **identical data**:

```
IOSPL API:  823 records, ₹24,540,472.15
Avante API: 823 records, ₹24,540,472.15
Difference: ₹0.00 (0.00%)
```

**Conclusion**: Both APIs are pointing to the **same database/endpoint**.

---

## 🔄 How to Configure Separate APIs

### Option 1: Different API Endpoints (Most Common)

If IOSPL should use a **different server or database**, update the endpoint:

#### Step 1: Edit `api_client_isopl.py`

```python
# Line 27-28
BASE_URL = "https://iospl-erp-server.com/API/api.php"  # Change this!
BEARER_TOKEN = "your-iospl-specific-bearer-token-here"
```

#### Step 2: Get IOSPL API Details

Ask your IOSPL team for:
- ✅ API Base URL
- ✅ Bearer Token (or authentication method)
- ✅ API endpoints (e.g., `/get_sales_report`)
- ✅ Request/Response format

---

### Option 2: Different Database Parameters

If both APIs use the same endpoint but **different databases**, you might need to add database parameters:

#### Edit `api_client_isopl.py`:

```python
def get_sales_report(self, start_date: str, end_date: str, period: str = "custom") -> Dict[str, Any]:
    # Add database parameter
    payload = {
        "startdate": start_date,
        "enddate": end_date,
        "database": "iospl_db"  # Add this if needed
    }
```

---

### Option 3: Different API Actions

If the same server has **different API actions** for each system:

#### Edit `api_client_isopl.py`:

```python
# Change the action parameter
url = f"{self.BASE_URL}?action=get_iospl_sales_report"  # Different action
```

---

## 🧪 Testing Your Configuration

### Test Script

Run the verification script to compare both APIs:

```bash
python3 verify_iospl_api.py
```

This will show you:
- ✅ Record counts from each API
- ✅ Total revenue comparison
- ✅ Whether data is identical or different
- ✅ Sample records from both sources

### Expected Results for Separate APIs:

```
IOSPL API:  1,234 records, ₹45,678,901.23
Avante API: 823 records, ₹24,540,472.15
Difference: ₹21,138,429.08 (46.15%)

⚠️ Data appears to be from DIFFERENT sources ✓
```

---

## 🔐 Bearer Token Management

### Current Setup

The IOSPL API uses a **Bearer Token** for authentication:

```python
# api_client_isopl.py (Line 30)
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Token Refresh Strategy

The token **expires periodically**. The system handles this in two ways:

1. **Automatic Login Fallback**: If token expires, system automatically calls login API
2. **Manual Token Update**: Update the `BEARER_TOKEN` constant when you get a new token

### How to Update Token

#### Method 1: Edit the File (Quick)

```python
# api_client_isopl.py
BEARER_TOKEN = "paste-new-token-here"
```

#### Method 2: Environment Variable (Production)

```bash
export IOSPL_BEARER_TOKEN="paste-new-token-here"
```

Then update `api_client_isopl.py`:

```python
import os
BEARER_TOKEN = os.getenv('IOSPL_BEARER_TOKEN', 'default-token-here')
```

#### Method 3: Pass at Runtime

```python
# When initializing
api_client = APIClientIOSPL(
    username="u2vp8kb",
    password="asdftuy#$%78@!",
    bearer_token="new-token-here"  # Pass new token
)
```

---

## 📊 Dashboard Toggle Feature

### How It Works

Users can switch between APIs using header buttons:

```
┌─────────────────────────────────────────────┐
│  [Avante Dashboard] [IOSPL Dashboard]       │
│       Active          Inactive              │
└─────────────────────────────────────────────┘
```

### Behind the Scenes

```python
# app.py - Line 1062
use_iospl = (dashboard_mode == 'iospl')

if use_iospl:
    api_client = APIClientIOSPL(username, password)
else:
    api_client = APIClient(username, password)
```

---

## 🐛 Common Issues & Solutions

### Issue 1: Both Dashboards Show Same Data

**Cause**: Both APIs pointing to same endpoint/database

**Solution**: 
1. Verify IOSPL should have different data
2. Update `BASE_URL` in `api_client_isopl.py`
3. Confirm with IOSPL team about separate API endpoint

---

### Issue 2: IOSPL Returns "Authentication Failed"

**Cause**: Bearer token expired or invalid

**Solution**:
1. Get new bearer token from IOSPL API
2. Update `BEARER_TOKEN` in `api_client_isopl.py`
3. Restart dashboard

---

### Issue 3: Connection Timeout

**Cause**: IOSPL server unavailable or URL incorrect

**Solution**:
1. Verify `BASE_URL` is correct
2. Test URL in browser or Postman
3. Check network/firewall settings

---

## 📞 Getting Help

### IOSPL API Team Contact Info

Contact your IOSPL team to get:
- ✅ Correct API endpoint URL
- ✅ Current bearer token
- ✅ API documentation
- ✅ Difference between Avante and IOSPL data sources

### Quick Questions Checklist

Ask the IOSPL team:

1. **"What is the correct API base URL for IOSPL?"**
   - Is it the same as Avante or different?

2. **"How do I get a bearer token?"**
   - Do I need to call `/login` or is it provided?

3. **"What's the difference between Avante and IOSPL data?"**
   - Different products?
   - Different dealers?
   - Different time periods?

4. **"How often does the bearer token expire?"**
   - Do I need to refresh it daily/hourly?

---

## ✅ Verification Checklist

Before going live, verify:

- [ ] IOSPL API URL is correct in `api_client_isopl.py`
- [ ] Bearer token is valid and up-to-date
- [ ] Test script shows **different data** from both APIs (if expected)
- [ ] Dashboard toggle buttons work correctly
- [ ] Both dashboards display data without errors
- [ ] Token refresh mechanism works when token expires

---

## 📝 Summary

| Feature | Avante API | IOSPL API |
|---------|-----------|-----------|
| **File** | `api_client.py` | `api_client_isopl.py` |
| **URL** | `avantemedicals.com/API/api.php` | ⚠️ Needs update |
| **Auth** | Username/Password | Bearer Token |
| **Status** | ✅ Working | ⚠️ Same as Avante |
| **Data** | Full ERP data | ⚠️ Should be different |

**Next Steps:**
1. Contact IOSPL team for correct API endpoint
2. Update `BASE_URL` in `api_client_isopl.py`
3. Get fresh bearer token if needed
4. Run verification script to confirm separate data
5. Test dashboard toggle feature

---

**Need help?** Run `python3 verify_iospl_api.py` to see current API status.
