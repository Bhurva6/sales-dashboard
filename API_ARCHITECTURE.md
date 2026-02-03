# 🔄 API Architecture Diagram

## Current Architecture (Both APIs → Same Data)

```
┌─────────────────────────────────────────────────────────────┐
│                    DASHBOARD                                │
│                                                             │
│  ┌──────────────────┐        ┌──────────────────┐         │
│  │ Avante Dashboard │        │ IOSPL Dashboard  │         │
│  │    (Button 1)    │        │    (Button 2)    │         │
│  └────────┬─────────┘        └────────┬─────────┘         │
│           │                           │                    │
│           ▼                           ▼                    │
│  ┌──────────────────┐        ┌──────────────────┐         │
│  │  api_client.py   │        │api_client_isopl  │         │
│  │                  │        │      .py         │         │
│  │ Login → Token    │        │ Bearer Token     │         │
│  └────────┬─────────┘        └────────┬─────────┘         │
└───────────┼────────────────────────────┼──────────────────┘
            │                            │
            │   ⚠️ SAME URL ⚠️           │
            │                            │
            └────────────┬───────────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │  avantemedicals.com    │
            │      /API/api.php      │
            │                        │
            │  Same Database         │
            │  Same Records          │
            │  823 records           │
            │  ₹24.54M              │
            └────────────────────────┘
                         ▲
                         │
                    Same Data!
```

---

## Desired Architecture (Separate APIs → Different Data)

```
┌─────────────────────────────────────────────────────────────┐
│                    DASHBOARD                                │
│                                                             │
│  ┌──────────────────┐        ┌──────────────────┐         │
│  │ Avante Dashboard │        │ IOSPL Dashboard  │         │
│  │    (Button 1)    │        │    (Button 2)    │         │
│  └────────┬─────────┘        └────────┬─────────┘         │
│           │                           │                    │
│           ▼                           ▼                    │
│  ┌──────────────────┐        ┌──────────────────┐         │
│  │  api_client.py   │        │api_client_isopl  │         │
│  │                  │        │      .py         │         │
│  │ Login → Token    │        │ Bearer Token     │         │
│  └────────┬─────────┘        └────────┬─────────┘         │
└───────────┼────────────────────────────┼──────────────────┘
            │                            │
            │   ✅ DIFFERENT URLs ✅    │
            │                            │
            ▼                            ▼
┌────────────────────────┐  ┌────────────────────────┐
│  avantemedicals.com    │  │  iospl-server.com      │
│      /API/api.php      │  │      /API/api.php      │
│                        │  │                        │
│  Avante Database       │  │  IOSPL Database        │
│  823 records           │  │  456 records           │
│  ₹24.54M              │  │  ₹12.35M              │
│                        │  │                        │
│  Dealers:              │  │  Dealers:              │
│  - Innovative Ortho    │  │  - IOSPL House         │
│  - S S Ortho Tools     │  │  - IOSPL Surgicals     │
│  - Vartika Surgical    │  │  - IOSPL Medical       │
└────────────────────────┘  └────────────────────────┘
            ▲                            ▲
            │                            │
      Different Data!              Different Data!
```

---

## Authentication Flow

### Avante API (Username/Password → Token)

```
┌──────────┐
│ Dashboard│
└────┬─────┘
     │ 1. POST /api.php?action=login
     │    {"username": "...", "password": "..."}
     ▼
┌────────────┐
│ Avante API │
└────┬───────┘
     │ 2. Returns JWT Token
     │    {"status": "success", "token": "..."}
     ▼
┌──────────┐
│ Dashboard│
└────┬─────┘
     │ 3. POST /api.php?action=get_sales_report
     │    Headers: {No auth required for now}
     │    Body: {"startdate": "...", "enddate": "..."}
     ▼
┌────────────┐
│ Avante API │ Returns sales data
└────────────┘
```

### IOSPL API (Bearer Token)

```
┌──────────┐
│ Dashboard│
└────┬─────┘
     │ 1. POST /api.php?action=get_sales_report
     │    Headers: {"Authorization": "Bearer eyJh..."}
     │    Body: {"startdate": "...", "enddate": "..."}
     ▼
┌────────────┐
│ IOSPL API  │ Returns sales data
└────────────┘
```

---

## Data Flow Comparison

### Current State (Same Data)

```
User clicks "IOSPL Dashboard"
    ↓
Dashboard sets: dashboard_mode = 'iospl'
    ↓
fetch_sales_data_cached(use_iospl=True)
    ↓
Creates APIClientIOSPL instance
    ↓
Calls: https://avantemedicals.com/API/api.php  ⚠️
    ↓
Returns: 823 records (Same as Avante!)
    ↓
Dashboard shows: Same data as Avante ❌
```

### Desired State (Different Data)

```
User clicks "IOSPL Dashboard"
    ↓
Dashboard sets: dashboard_mode = 'iospl'
    ↓
fetch_sales_data_cached(use_iospl=True)
    ↓
Creates APIClientIOSPL instance
    ↓
Calls: https://iospl-server.com/API/api.php  ✅
    ↓
Returns: 456 records (Different from Avante!)
    ↓
Dashboard shows: IOSPL-specific data ✅
```

---

## Configuration Locations

```
Project Structure:
├── app.py                          ← Dashboard (don't edit)
├── api_client.py                   ← Avante API (don't edit)
├── api_client_isopl.py            ← ⚠️ EDIT THIS FILE!
│   ├── Line 27: BASE_URL          ← Change URL here
│   ├── Line 28: BEARER_TOKEN      ← Update token here
│   └── Line 153: API action       ← Change if needed
├── verify_iospl_api.py            ← Run this to test
└── Documentation Files:
    ├── IOSPL_QUICK_START.md       ← Quick reference
    ├── DUAL_API_SETUP_GUIDE.md    ← Complete guide
    ├── API_COMPARISON.md          ← Detailed comparison
    └── API_ARCHITECTURE.md        ← This file
```

---

## Token Management

### Bearer Token Lifecycle

```
┌─────────────────────────────────────────────────────┐
│                  Token Lifecycle                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. Get Token from IOSPL Team                      │
│     eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...        │
│                                                     │
│  2. Add to api_client_isopl.py                     │
│     BEARER_TOKEN = "paste-here"                    │
│                                                     │
│  3. Token is valid for ~X hours                    │
│     (ask IOSPL team for expiry time)               │
│                                                     │
│  4. When expired:                                  │
│     ├─→ Dashboard shows "Authentication Failed"    │
│     ├─→ Get new token from IOSPL                   │
│     └─→ Update BEARER_TOKEN again                  │
│                                                     │
│  5. Future: Auto-refresh mechanism                 │
│     (call login API to get new token)              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Request/Response Flow

### Avante API Request

```http
POST https://avantemedicals.com/API/api.php?action=get_sales_report
Content-Type: application/json

{
  "action": "get_sales_report",
  "startdate": "01-01-2026",
  "enddate": "31-01-2026"
}
```

**Response:**
```json
{
  "status": "success",
  "report_data": [
    {
      "cust_id": "49",
      "comp_nm": "S S ORTHO TOOLS",
      "city": "BANGALORE",
      "state": "KARNATAKA",
      "SQ": "130",
      "SV": "18132.66"
    }
  ]
}
```

### IOSPL API Request (Current)

```http
POST https://avantemedicals.com/API/api.php?action=get_sales_report
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "startdate": "01-01-2026",
  "enddate": "31-01-2026"
}
```

**Response:** ⚠️ Same as Avante (needs different URL)

### IOSPL API Request (Desired)

```http
POST https://iospl-server.com/API/api.php?action=get_iospl_sales
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "startdate": "01-01-2026",
  "enddate": "31-01-2026",
  "company": "IOSPL"  ← Possible additional parameter
}
```

**Response:** ✅ Different IOSPL data

---

## Summary

**Problem:** Both APIs use the same URL → Same Data  
**Solution:** Get correct IOSPL API URL from team → Different Data  
**File to Edit:** `api_client_isopl.py` (Lines 27-28, 153)  
**Test Command:** `python3 verify_iospl_api.py`  

---

See `IOSPL_QUICK_START.md` for immediate next steps!
