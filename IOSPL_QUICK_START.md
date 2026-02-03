# 🚀 Quick Start: Setting Up IOSPL API

## ⚡ TL;DR

Both Avante and IOSPL APIs currently return **the same data** because they use the **same API endpoint**. To have separate data, you need to get the correct IOSPL API configuration from your team.

---

## 📋 What You Need from IOSPL Team

Contact your IOSPL API team and ask for:

### 1. API Endpoint URL
```
Current: https://avantemedicals.com/API/api.php (same as Avante)
Needed:  https://______________________/API/api.php
```

### 2. Bearer Token
```
Current: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhdmFudGVtZWRpY2Fscy5jb20iLCJhdWQiOiJhdmFudGVtZWRpY2Fscy5jb20iLCJpYXQiOjE3Njk1ODgzOTIsImV4cCI6MTc2OTU5MTk5MiwiZGF0YSI6eyJhcGlfdXNlcl9pZCI6IjEiLCJ1c2VybmFtZSI6InUydnA4a2IifX0.SUFoKecNvls0Fc7V-iHbJrFd3U83PS2aUdgZThCjjpM

Status: ⚠️ Token expires - need refresh mechanism
```

### 3. API Action/Endpoint
```
Current: ?action=get_sales_report
Needed:  ?action=________________ (if different)
```

### 4. Request Parameters
```
Current: {"startdate": "DD-MM-YYYY", "enddate": "DD-MM-YYYY"}
Needed:  Additional parameters? (company, database, etc.)
```

---

## 🔧 Configuration File

**File to Edit:** `api_client_isopl.py`

**Lines to Update:**
```python
# Line 27-28: API URL and Bearer Token
BASE_URL = "https://your-iospl-url-here.com/API/api.php"
BEARER_TOKEN = "your-bearer-token-here"

# Line 153: API Action (if different)
url = f"{self.BASE_URL}?action=get_sales_report"

# Line 156-159: Request Payload (if additional params needed)
payload = {
    "startdate": start_date,
    "enddate": end_date,
    # Add any additional parameters here
}
```

---

## ✅ Testing Steps

### Step 1: Update Configuration
Edit `api_client_isopl.py` with correct IOSPL details

### Step 2: Run Verification
```bash
python3 verify_iospl_api.py
```

### Step 3: Check Results
Look for this output:
```
⚠️ Different number of records - Data sources may be different!
✅ IOSPL API is working! Data appears to be from a DIFFERENT source
```

### Step 4: Test Dashboard
```bash
python3 app.py
```
Then open `http://localhost:8050` and toggle between dashboards

---

## 🎯 Success Checklist

- [ ] Got IOSPL API URL from team
- [ ] Got current bearer token
- [ ] Updated `api_client_isopl.py`
- [ ] Ran `verify_iospl_api.py` - shows **different data**
- [ ] Tested dashboard toggle - shows **different data**
- [ ] Both dashboards load without errors

---

## 🐛 Common Issues

### Issue: "Both APIs return same data"
**Fix:** IOSPL URL is still pointing to Avante server. Update `BASE_URL` in `api_client_isopl.py`

### Issue: "Authentication failed"
**Fix:** Bearer token expired. Get new token from IOSPL team and update `BEARER_TOKEN`

### Issue: "Connection timeout"
**Fix:** IOSPL server URL incorrect. Verify URL with IOSPL team

---

## 📞 Who to Contact

**For API Configuration:** IOSPL Technical Team  
**For Bearer Tokens:** IOSPL Authentication/Security Team  
**For Data Questions:** IOSPL Database/ERP Team

---

## 📚 Documentation Files

- `DUAL_API_SETUP_GUIDE.md` - Complete setup guide
- `API_COMPARISON.md` - Detailed API comparison
- `verify_iospl_api.py` - Testing script
- `api_client_isopl.py` - IOSPL API client code

---

## 💡 Key Point

**The system is already built and working!** You just need the correct IOSPL API configuration from your team. Once you have:
1. The correct API URL
2. A valid bearer token
3. Any additional parameters

Simply update `api_client_isopl.py` and everything will work automatically! 🎉
