# Quick Start Guide: Date-Based API Filtering

## 🚀 How to Use

### Step 1: Run the Dashboard
```bash
streamlit run dashboard.py
```

### Step 2: Login
Enter your API credentials to authenticate.

### Step 3: Select Time Period from Sidebar
The time period selector is in the left sidebar:
```
📅 Select Time Period
├─ Today
├─ This Week  
├─ This Month (default)
└─ This Year
```

### Step 4: View Filtered Data
The dashboard automatically:
- ✅ Sends date-filtered request to API
- ✅ Receives only relevant data for selected period
- ✅ Displays metrics and charts
- ✅ Caches data for instant switching

---

## 🎯 What Happens When You Select a Period

### Example: Select "This Month"

```
┌─ Today is January 2, 2026
├─ You click: "This Month"
├─ Dashboard calculates: Jan 1 - Jan 2, 2026
├─ Sends to API: {"startdate": "01-01-2026", "enddate": "02-01-2026"}
└─ Shows you: Revenue, Quantity, Top Dealer, etc. for Jan 1-2 only
```

---

## 📊 Metrics You See

For the selected time period, you'll see:

| Metric | Example |
|--------|---------|
| 💰 Revenue | Rs. 2.50 Lakh |
| 📦 Total Quantity | 500 units |
| 🏆 Most Sold Item | Product Name |
| 📊 Total Orders | 45 |
| 🗺️ Top State | Delhi |
| 🏙️ Top Area | New Delhi |
| 🤝 Top Dealer | Dealer A |
| 📂 Categories | 12 |

---

## 🔄 Switching Between Periods

```
Current: "This Month"     Click "This Week"     View updates instantly
        ↓                         ↓                      ↓
   (Jan 1-2)              (fetches if needed)     (filtered for Dec 30-Jan 2)
                          (or shows cached)
```

**No need to refresh!** Just click a different period.

---

## 🔃 Force Refresh Data

**Click "Refresh Data" button** to:
- ✅ Clear all caches
- ✅ Fetch fresh data from API
- ✅ Show latest metrics

---

## 📝 What's Happening Behind the Scenes

1. **You select period** → Sidebar updates
2. **Dashboard checks cache** → Data for this period loaded?
3. **If cached** → Display immediately (instant)
4. **If not cached** → Fetch from API
   - Calculate date range for period
   - Send to API with start/end dates
   - API returns filtered data
   - Dashboard displays it
5. **Cache the data** → For next time

---

## 💡 Tips

✨ **Pro Tips:**

1. **Fast Switching:** Periods are cached, so switching is instant
2. **Consistent Data:** Each period has its own data - no mixing
3. **Always Fresh:** Click refresh to get latest data
4. **Works with existing filters:** The "Hide 'Innovative'" checkbox still works

---

## 🐛 Troubleshooting

### Problem: "No data available"
**Solution:** 
- Check if API is accessible
- Verify date range has data
- Try clicking "Refresh Data"

### Problem: Data looks wrong
**Solution:**
- Check sidebar - make sure correct period is selected
- Click "Refresh Data" to get latest
- Check if you're filtering by dealer (hide Innovative checkbox)

### Problem: Same data for all periods
**Solution:**
- This might mean API has limited data
- Check API logs to confirm date filtering is working
- Or try refreshing the page

---

## 📱 Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│ SIDEBAR                 │        MAIN CONTENT           │
│                         │                               │
│ 🚪 Logout              │ 📊 Key Metrics                │
│                         │ ├─ Revenue, Qty, Orders      │
│ Refresh Data            │ ├─ Top Dealer, State, Area   │
│                         │ └─ Categories                 │
│ 📅 SELECT PERIOD ◄─────────── Currently Applied        │
│ ├─ Today               │                               │
│ ├─ This Week           │ 📊 Sales Analytics            │
│ ├─ This Month ✓        │ ├─ Revenue Distribution       │
│ └─ This Year           │ ├─ Customer Segmentation      │
│                         │ ├─ Non-Moving Items          │
│ Hide Innovative ☐      │ ├─ Cross-Selling             │
│                         │ └─ ... more tabs ...          │
│ Data loaded from API    │                               │
└─────────────────────────────────────────────────────────┘
```

---

## 🔐 Security Notes

- Dates are sent in DD-MM-YYYY format
- No sensitive data cached in session state
- Clear cache when logging out
- API handles all actual data filtering

---

## 📋 Supported Time Periods

| Period | Range | Example (Today: Jan 2, 2026) |
|--------|-------|------------------------------|
| **Today** | Current date only | Jan 2 - Jan 2 |
| **This Week** | Mon to today | Dec 30 - Jan 2 |
| **This Month** | 1st to today | Jan 1 - Jan 2 |
| **This Year** | Jan 1 to today | Jan 1 - Jan 2 |

---

## 🎓 Learning More

For detailed information, see:
- `API_DATE_FILTERING_GUIDE.md` - How it works
- `API_REQUEST_EXAMPLES.md` - API request examples
- `DATA_FLOW_DIAGRAM.md` - Visual flow diagrams
- `IMPLEMENTATION_SUMMARY.md` - What was changed

---

## ⚡ Quick Commands

**In terminal:**
```bash
# Run the dashboard
streamlit run dashboard.py

# Clear cache and restart
streamlit cache clear && streamlit run dashboard.py
```

---

## 🎯 Common Workflows

### Workflow 1: Check Daily Sales
1. Login to dashboard
2. Select "Today" from sidebar
3. View today's revenue and metrics
4. Check top dealer and state

### Workflow 2: Weekly Report
1. Select "This Week" from sidebar
2. Review weekly trends
3. Compare with previous weeks (manual check)
4. Export or screenshot metrics

### Workflow 3: Monthly Analysis
1. Select "This Month" from sidebar
2. Analyze current month metrics
3. Click tabs for detailed insights
4. Share report with team

### Workflow 4: Year-to-Date Analysis
1. Select "This Year" from sidebar
2. View entire year's performance
3. Use charts for trend analysis
4. Identify top performers

---

## 📞 Support

If something doesn't work:
1. Check the console for error messages
2. Verify API is accessible
3. Try clicking "Refresh Data"
4. Review the documentation files
5. Check browser console for JavaScript errors

---

## ✅ Checklist

Before sharing with team:
- [ ] Dashboard loads without errors
- [ ] Can select all 4 time periods
- [ ] Data updates when changing periods
- [ ] Metrics show correct values
- [ ] Refresh button works
- [ ] No console errors
- [ ] API requests are being sent with correct dates

---

**That's it!** You're ready to use date-based filtering. Happy analyzing! 🚀
