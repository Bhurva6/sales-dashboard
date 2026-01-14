# My Charts Feature - Visual Guide

## User Interface Overview

### 1. Tab Navigation (Top of Page)
```
┌─────────────────────────────────────────────────────────────┐
│  [Dashboard]  [My Charts]                                   │
└─────────────────────────────────────────────────────────────┘
```

### 2. Dashboard Tab - Custom Chart Builder Section

```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│  [➕ Create Custom Chart]  ← Click to expand/collapse       │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ 🎨 Custom Chart Builder                                 ││
│  │                                                           ││
│  │  X-axis:  [Dropdown: Select X-axis          ▼]          ││
│  │  Y-axis:  [Dropdown: Select Y-axis          ▼]          ││
│  │                                                           ││
│  │  Chart Type:      [Dropdown: Select Type    ▼]          ││
│  │  Aggregation:     [Dropdown: Sum            ▼]          ││
│  │                                                           ││
│  │  Top N Items:     [10                       ]            ││
│  │  ☑ Sort Descending                                       ││
│  │  [Generate Chart]                                        ││
│  │                                                           ││
│  │  Chart Name:      [Enter chart name...      ]            ││
│  │  [💾 Save Chart]                                         ││
│  │                                                           ││
│  │  ✅ Chart "My Chart" saved successfully!                ││
│  │     Switch to "My Charts" tab to view it.               ││
│  │                                                           ││
│  │  ┌───────────────────────────────────────────────────┐  ││
│  │  │ Generated Chart Preview                           │  ││
│  │  │ [Your chart appears here after clicking Generate]│  ││
│  │  └───────────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### 3. My Charts Tab - Saved Charts Display

#### When No Charts Are Saved:
```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│                          📊                                  │
│                                                               │
│              No Saved Charts Yet                             │
│                                                               │
│   Create and save custom charts from the Dashboard tab      │
│              to see them here!                               │
│                                                               │
│   Saved charts will automatically update with the            │
│              current date range.                             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

#### When Charts Are Saved:
```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│  📊 My Saved Charts (3)                                      │
│  Showing data from 01-01-2026 to 14-01-2026                 │
│                                                               │
│  ┌──────────────────────────┐  ┌──────────────────────────┐│
│  │ Top Dealers by Revenue   │  │ Orders by City           ││
│  │ Saved on 14-01-2026 10:30│  │ Saved on 14-01-2026 10:45││
│  │                          │  │                          ││
│  │ ┌──────────────────────┐ │  │ ┌──────────────────────┐ ││
│  │ │                      │ │  │ │                      │ ││
│  │ │   [Bar Chart]        │ │  │ │  [Horizontal Bar]    │ ││
│  │ │                      │ │  │ │                      │ ││
│  │ └──────────────────────┘ │  │ └──────────────────────┘ ││
│  │                          │  │                          ││
│  │  [🗑️ Delete]            │  │  [🗑️ Delete]            ││
│  └──────────────────────────┘  └──────────────────────────┘│
│                                                               │
│  ┌──────────────────────────┐                               │
│  │ Top Products by Quantity │                               │
│  │ Saved on 14-01-2026 11:00│                               │
│  │                          │                               │
│  │ ┌──────────────────────┐ │                               │
│  │ │                      │ │                               │
│  │ │    [Pie Chart]       │ │                               │
│  │ │                      │ │                               │
│  │ └──────────────────────┘ │                               │
│  │                          │                               │
│  │  [🗑️ Delete]            │                               │
│  └──────────────────────────┘                               │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 4. Sidebar (Available on Both Tabs)

```
┌──────────────────────────┐
│  🔐 Login                │
│  Username: [u2vp8kb    ] │
│  Password: [**********  ] │
├──────────────────────────┤
│  ⚡ Quick Select:        │
│  [Today] [Yesterday]     │
│  [This Week]             │
│  [This Month]            │
│  [Last 3 Months]         │
├──────────────────────────┤
│  📅 Date Range           │
│  From: [01-01-2026 📅]  │
│  To:   [14-01-2026 📅]  │
├──────────────────────────┤
│  🔧 Controls             │
│  ☐ Hide 'Innovative'     │
│  [🔄 Refresh Data]      │
├──────────────────────────┤
│  Data Status:            │
│  ✅ 1,234 records       │
│  Last updated: 10:30:45  │
└──────────────────────────┘
```

## User Journey Diagrams

### Journey 1: Creating and Saving a Chart

```
Start
  ↓
1. User on Dashboard Tab
  ↓
2. Clicks "➕ Create Custom Chart"
  ↓
3. Selects X-axis (e.g., "State")
  ↓
4. Selects Y-axis (e.g., "Sum of Revenue")
  ↓
5. Selects Chart Type (e.g., "Bar Chart")
  ↓
6. Clicks "Generate Chart" → Chart Preview Appears
  ↓
7. Types Chart Name: "Revenue by State"
  ↓
8. Clicks "💾 Save Chart"
  ↓
9. Sees Success Message: "✅ Chart 'Revenue by State' saved successfully!"
  ↓
End
```

### Journey 2: Viewing and Deleting Saved Charts

```
Start
  ↓
1. User clicks "My Charts" Tab
  ↓
2. Sees list of saved charts with live data
  ↓
3. Changes date range in sidebar
  ↓
4. All charts auto-update with new data
  ↓
5. Decides to delete one chart
  ↓
6. Clicks "🗑️ Delete" button
  ↓
7. Chart immediately disappears
  ↓
8. Other charts remain visible
  ↓
End
```

### Journey 3: Persistence Test

```
Start
  ↓
1. User has 3 charts saved on "My Charts" tab
  ↓
2. User refreshes browser (Ctrl+R)
  ↓
3. Page reloads
  ↓
4. User navigates to "My Charts" tab
  ↓
5. All 3 charts are still there! ✅
  ↓
6. User closes browser completely
  ↓
7. User reopens browser and goes to dashboard
  ↓
8. User clicks "My Charts" tab
  ↓
9. All 3 charts are STILL there! ✅
  ↓
End
```

## Interactive Elements

### Clickable Elements

1. **Tabs**
   - `[Dashboard]` - Shows main dashboard
   - `[My Charts]` - Shows saved charts

2. **Dashboard Tab Buttons**
   - `[➕ Create Custom Chart]` - Expands/collapses builder
   - `[Generate Chart]` - Creates preview
   - `[💾 Save Chart]` - Saves configuration

3. **My Charts Tab Buttons**
   - `[🗑️ Delete]` - Removes chart from storage

4. **Sidebar Controls** (Available on both tabs)
   - Quick date buttons
   - Date picker
   - Refresh button
   - Filter checkbox

### Form Fields

1. **Custom Chart Builder**
   - X-axis dropdown (8 options)
   - Y-axis dropdown (5 options)
   - Chart Type dropdown (6 types)
   - Aggregation dropdown (5 methods)
   - Top N number input
   - Sort Descending checkbox
   - Chart Name text input

## Visual Feedback

### Success States
```
✅ Chart "My Chart Name" saved successfully!
   Switch to "My Charts" tab to view it.
```

### Warning States
```
⚠️ Please fill in chart name and all required fields
```

### Error States
```
❌ Error saving chart: [error message]
```

### Info States
```
📊 My Saved Charts (3)
Showing data from 01-01-2026 to 14-01-2026
```

### Empty States
```
           📊
   No Saved Charts Yet
   
Create and save custom charts from
  the Dashboard tab to see them here!
```

## Color Scheme

- **Primary Actions:** Blue buttons (Save, Generate)
- **Destructive Actions:** Red buttons (Delete)
- **Success Messages:** Green background
- **Warning Messages:** Yellow background
- **Error Messages:** Red background
- **Info Messages:** Blue background
- **Card Headers:** Light gray background
- **Timestamps:** Muted gray text

## Responsive Behavior

### Desktop (Large Screens)
- Sidebar: 3 columns (25%)
- Main Content: 9 columns (75%)
- Chart Grid: 2 columns (50% each)

### Tablet (Medium Screens)
- Sidebar: 3 columns (25%)
- Main Content: 9 columns (75%)
- Chart Grid: 2 columns (50% each)

### Mobile (Small Screens)
- Sidebar: Full width (stacked)
- Main Content: Full width (stacked)
- Chart Grid: 1 column (100%)

## Keyboard Shortcuts

While no specific keyboard shortcuts are implemented, standard browser shortcuts work:

- `Ctrl/Cmd + R` - Refresh page (charts persist!)
- `Tab` - Navigate between form fields
- `Enter` - Submit form (when in text input)
- `Ctrl/Cmd + F` - Find text on page

## Animation/Transitions

- Chart builder expand/collapse - Smooth slide animation
- Chart deletion - Immediate removal (no animation)
- Tab switching - Instant switch
- Chart generation - Loading spinner during API call

---

**Note:** All visual elements use Bootstrap 5 styling for consistent, professional appearance across all browsers and devices.
