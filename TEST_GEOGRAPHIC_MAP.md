# 🧪 Geographic Map - Quick Test Guide

## Prerequisites
- Dashboard running (`python app.py`)
- Logged in with valid credentials
- Sample data loaded

## Quick Test Scenarios

### Test 1: Basic Map Display ⭐
**Steps:**
1. Navigate to dashboard
2. Scroll to "Geographic Distribution" section
3. Verify map displays with default settings

**Expected:**
- ✅ Map shows India with state-level choropleth
- ✅ States colored by Revenue (blue gradient)
- ✅ Map controls visible (Metric, Level, Toggle)

**Time:** 30 seconds

---

### Test 2: Metric Switching 📊
**Steps:**
1. Default: Revenue metric (blue)
2. Click "Quantity" radio button
3. Click "Orders" radio button
4. Return to "Revenue"

**Expected:**
- ✅ Revenue: Blue gradient colors
- ✅ Quantity: Green gradient colors
- ✅ Orders: Orange gradient colors
- ✅ Map updates smoothly
- ✅ Hover shows correct metric values

**Time:** 1 minute

---

### Test 3: State vs City View 🗺️
**Steps:**
1. Default: State level view
2. Click "City" radio button
3. Observe city-level bubbles/colors
4. Return to "State" view

**Expected:**
- ✅ State view: Shows ~23 states
- ✅ City view: Shows 50+ cities
- ✅ Smooth transition between views
- ✅ Hover tooltips work in both views

**Time:** 1 minute

---

### Test 4: Choropleth vs Bubble Toggle 🎨
**Steps:**
1. Default: Choropleth view (toggle OFF)
2. Turn toggle ON for Bubble view
3. Compare visualizations
4. Toggle back to Choropleth

**Expected:**
- ✅ Choropleth: Filled colors on map
- ✅ Bubble: Circles at location coordinates
- ✅ Bubble size reflects metric value
- ✅ Both show hover details

**Time:** 1 minute

---

### Test 5: Hover Interaction 🖱️
**Steps:**
1. Hover over different states/cities
2. Check tooltip information
3. Move quickly between locations

**Expected:**
- ✅ Tooltip shows location name
- ✅ Shows metric value (formatted as INR or count)
- ✅ Shows percentage of total
- ✅ Tooltip follows cursor smoothly

**Time:** 1 minute

---

### Test 6: Click to Filter 🎯
**Steps:**
1. Click on "Maharashtra" state
2. Observe dashboard update
3. Check location display under map
4. Verify other metrics update

**Expected:**
- ✅ Dashboard filters by Maharashtra
- ✅ Location display shows "States: Maharashtra"
- ✅ All metrics update (Revenue, Quantity, Orders cards)
- ✅ Charts update to show only Maharashtra data

**Time:** 1 minute

---

### Test 7: Reset View 🔄
**Steps:**
1. Click on a state to filter
2. Click "Reset View" button
3. Verify dashboard returns to full view

**Expected:**
- ✅ Location filter cleared
- ✅ Location display empty
- ✅ Dashboard shows all data again
- ✅ Map shows all states/cities

**Time:** 30 seconds

---

### Test 8: Date Filter Integration 📅
**Steps:**
1. Change date range using date picker
2. Observe map update
3. Try quick filters (Today, This Week, etc.)
4. Verify map reflects date filter

**Expected:**
- ✅ Map data updates with date filter
- ✅ Colors change based on filtered data
- ✅ Quick date filters work
- ✅ Hover values match filtered period

**Time:** 2 minutes

---

### Test 9: State/City Filter Integration 🔍
**Steps:**
1. Use State dropdown to select multiple states
2. Observe map shows only selected states
3. Switch to City view
4. Use City dropdown
5. Clear filters

**Expected:**
- ✅ Map highlights selected states
- ✅ Other states dimmed or hidden
- ✅ City filter works in City view
- ✅ Filters sync properly

**Time:** 2 minutes

---

### Test 10: Hide Innovative Filter 🚫
**Steps:**
1. Check "Hide Innovative Automobiles"
2. Observe map update
3. Uncheck filter
4. Compare values

**Expected:**
- ✅ Map values decrease when checked
- ✅ Map values increase when unchecked
- ✅ Hover tooltips show correct values
- ✅ Color intensity adjusts

**Time:** 1 minute

---

### Test 11: Empty Data Handling ❌
**Steps:**
1. Select date range with no data (e.g., future dates)
2. Observe map behavior
3. Return to valid date range

**Expected:**
- ✅ Shows "No data available" message
- ✅ Map still renders (blank)
- ✅ No errors in console
- ✅ Recovers when data available

**Time:** 1 minute

---

### Test 12: All Combinations Test 🎲
**Steps:**
1. Set Revenue + State + Choropleth
2. Set Quantity + State + Bubble
3. Set Orders + City + Choropleth
4. Set Revenue + City + Bubble
5. Test with various filters active

**Expected:**
- ✅ All 12 combinations work (3 metrics × 2 levels × 2 views)
- ✅ No errors or crashes
- ✅ Smooth transitions
- ✅ Data displays correctly

**Time:** 3 minutes

---

### Test 13: Performance Test ⚡
**Steps:**
1. Load dashboard with large date range (1+ year)
2. Switch between metrics rapidly
3. Toggle view mode multiple times
4. Switch levels quickly
5. Monitor browser performance

**Expected:**
- ✅ Map updates within 1-2 seconds
- ✅ No browser lag or freeze
- ✅ Smooth animations
- ✅ No memory leaks

**Time:** 2 minutes

---

### Test 14: Mobile Responsive (Optional) 📱
**Steps:**
1. Open dashboard in mobile browser or resize window
2. Scroll to map section
3. Try interactions (limited on mobile)

**Expected:**
- ✅ Map visible on mobile
- ✅ Controls stack vertically
- ✅ Touch interactions work (basic)
- ⚠️ Some features may be limited

**Time:** 2 minutes

---

## Quick Smoke Test (3 minutes)
1. ✅ Map displays with default settings (30s)
2. ✅ Switch metric: Revenue → Quantity → Orders (30s)
3. ✅ Switch level: State → City (30s)
4. ✅ Toggle view: Choropleth → Bubble (30s)
5. ✅ Click a state to filter (30s)
6. ✅ Reset view (15s)
7. ✅ Change date range (15s)

## Full Test Suite (20 minutes)
Run all 14 tests in sequence

## Expected Results Summary
- ✅ All interactions smooth and responsive
- ✅ No JavaScript errors in console
- ✅ No Python errors in terminal
- ✅ Data displays accurately
- ✅ Filters sync properly
- ✅ Professional appearance

## Common Issues & Fixes

### Issue: Map not showing
**Fix:** Check if data has `State` or `City` columns

### Issue: Click not filtering
**Fix:** Verify State/City filter dropdowns are enabled

### Issue: Colors not changing
**Fix:** Check metric selector is working, try different metric

### Issue: Slow performance
**Fix:** Reduce date range, clear browser cache

### Issue: Hover not working
**Fix:** Try different browser (Chrome recommended)

## Test Report Template
```
Date: [Date]
Tester: [Name]
Browser: [Chrome/Firefox/Safari]
Version: [Version]

Test Results:
- Test 1: ✅/❌
- Test 2: ✅/❌
...

Issues Found:
1. [Description]
2. [Description]

Overall Status: ✅ PASS / ❌ FAIL
```

## Browser Recommendations
- ✅ **Chrome**: Best performance (recommended)
- ✅ **Edge**: Excellent compatibility
- ✅ **Firefox**: Good performance
- ⚠️ **Safari**: Works but may be slower

## Performance Benchmarks
- Map render time: < 2 seconds
- Metric switch: < 1 second
- Level switch: < 1 second
- View toggle: < 1 second
- Click filter: < 1 second

---

**Happy Testing! 🎉**

*For issues or questions, check GEOGRAPHIC_MAP_FEATURE.md*
