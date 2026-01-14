# 🎨 Design System Quick Reference

## Color Palette

### Primary Colors
| Color | Hex | Usage |
|-------|-----|-------|
| **Primary** | `#6366f1` | Main actions, links, brand |
| **Secondary** | `#8b5cf6` | Accents, secondary actions |
| **Success** | `#10b981` | Positive feedback, growth |
| **Danger** | `#ef4444` | Errors, warnings, decline |
| **Warning** | `#f59e0b` | Caution, pending states |
| **Info** | `#3b82f6` | Information, neutral actions |

### Neutral Colors
| Color | Hex | Usage |
|-------|-----|-------|
| **Background** | `#f9fafb` | Page background |
| **Card BG** | `#ffffff` | Card backgrounds |
| **Sidebar BG** | `#f8fafc` | Sidebar, secondary areas |
| **Dark Text** | `#1f2937` | Primary text |
| **Muted Text** | `#6b7280` | Secondary text |
| **Light Text** | `#9ca3af` | Tertiary text, hints |
| **Border** | `#e5e7eb` | Borders, dividers |

## Typography

### Font Family
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

### Font Sizes
| Element | Size | Weight | Use Case |
|---------|------|--------|----------|
| **H1** | 32px | 700 | Page titles |
| **H2** | 24px | 600 | Section headers |
| **H3** | 20px | 600 | Subsections |
| **H4** | 18px | 600 | Card titles |
| **H5** | 16px | 600 | Small headings |
| **Body** | 14px | 400 | Default text |
| **Small** | 12px | 400 | Captions, meta |

### Font Weights
- **300** - Light (rarely used)
- **400** - Regular (body text)
- **500** - Medium (buttons, labels)
- **600** - Semibold (headings)
- **700** - Bold (main titles)
- **800** - Extrabold (hero text)

## Spacing Scale

### Bootstrap Spacing Classes
| Class | Rem | Pixels | Use Case |
|-------|-----|--------|----------|
| `p-1`, `m-1` | 0.25rem | 4px | Minimal spacing |
| `p-2`, `m-2` | 0.5rem | 8px | Tight spacing |
| `p-3`, `m-3` | 1rem | 16px | Default spacing |
| `p-4`, `m-4` | 1.5rem | 24px | Generous spacing |
| `p-5`, `m-5` | 3rem | 48px | Large spacing |

### Component Spacing
- **Card padding:** `p-3` or `p-4` (1-1.5rem)
- **Section margins:** `mb-4` (1.5rem)
- **Row gaps:** `g-2` or `g-3` (0.5-1rem)
- **Element gaps:** `mb-2` or `mb-3` (0.5-1rem)

## Border Radius

| Size | Pixels | Usage |
|------|--------|-------|
| **Small** | 8px | Buttons, inputs, badges |
| **Medium** | 12px | Cards, alerts, tables |
| **Large** | 16px | Sidebar, modals |
| **XLarge** | 20px | Hero sections |

## Shadows

### Box Shadow Scale
| Name | CSS Value | Usage |
|------|-----------|-------|
| **xs** | `0 1px 2px rgba(0,0,0,0.05)` | Subtle depth |
| **sm** | `0 1px 3px rgba(0,0,0,0.05)` | Cards, buttons |
| **md** | `0 4px 6px rgba(0,0,0,0.07)` | Dropdowns, popovers |
| **lg** | `0 10px 15px rgba(0,0,0,0.1)` | Modals, dialogs |
| **xl** | `0 20px 25px rgba(0,0,0,0.15)` | Large components |

### Usage Classes
```css
.shadow-sm    /* For most cards */
.shadow       /* For elevated elements */
.shadow-lg    /* For modals */
```

## Transitions

### Standard Transition
```css
transition: all 0.2s ease;
```

### Common Use Cases
| Property | Duration | Easing | Usage |
|----------|----------|--------|-------|
| `all` | 0.2s | ease | Buttons, links |
| `transform` | 0.2s | ease | Hover effects |
| `opacity` | 0.3s | ease-in | Fade in/out |
| `height` | 0.3s | ease | Expand/collapse |

## Component Classes

### Cards
```html
<dbc.Card className="shadow-sm">
  <dbc.CardHeader>Title</dbc.CardHeader>
  <dbc.CardBody>Content</dbc.CardBody>
</dbc.Card>
```

**Styles:**
- Border radius: 12px
- Shadow: sm (0 1px 3px)
- Background: white
- Hover: lift + enhanced shadow

### Buttons
```html
<dbc.Button color="primary" size="sm">Click</dbc.Button>
```

**Sizes:**
- `sm` - Small (compact)
- Default - Medium
- `lg` - Large (prominent)

**Colors:**
- `primary` - Main actions
- `success` - Confirm, positive
- `danger` - Delete, negative
- `secondary` - Cancel, neutral
- `info` - Information
- `warning` - Caution

### Badges
```html
<dbc.Badge color="success">New</dbc.Badge>
```

**Styles:**
- Border radius: 6px
- Padding: 0.35rem 0.65rem
- Font weight: 500
- Font size: 0.875rem (14px)

### Alerts
```html
<dbc.Alert color="info">Message</dbc.Alert>
```

**Features:**
- Gradient backgrounds
- No borders
- Rounded corners (12px)
- Subtle shadow

## Layout Grid

### Breakpoints
| Name | Min Width | Device |
|------|-----------|--------|
| **xs** | <576px | Mobile phones |
| **sm** | ≥576px | Large phones |
| **md** | ≥768px | Tablets |
| **lg** | ≥992px | Desktops |
| **xl** | ≥1200px | Large desktops |

### Column Widths
```python
# Desktop: 4 columns, Tablet: 2 columns, Mobile: 1 column
dbc.Col([...], width=3, md=6, sm=12)
```

### Common Patterns
```python
# Sidebar + Main
dbc.Row([
    dbc.Col([sidebar], width=3, lg=3, md=12),
    dbc.Col([main], width=9, lg=9, md=12)
])

# Metrics (4 per row)
dbc.Row([
    dbc.Col([metric], width=3, md=6, sm=12),
    # Repeat 4 times
])
```

## Chart Styling

### Apply Theme
```python
fig = apply_modern_chart_style(fig, "Chart Title", height=400)
```

### Color Palette (Charts)
```python
colors = [
    '#6366f1',  # Indigo
    '#8b5cf6',  # Purple  
    '#ec4899',  # Pink
    '#f59e0b',  # Amber
    '#10b981',  # Green
    '#3b82f6',  # Blue
    '#ef4444',  # Red
    '#14b8a6',  # Teal
    '#f97316',  # Orange
    '#a855f7'   # Violet
]
```

### Chart Heights
- **Small:** 300px (sparklines, mini charts)
- **Medium:** 400px (default charts)
- **Large:** 500px (feature charts)
- **XLarge:** 600px (maps, tables)

## Icons & Emojis

### Common Icons
| Emoji | Usage |
|-------|-------|
| 📊 | Dashboard, analytics |
| 💰 | Revenue, money |
| 📦 | Quantity, products |
| 🏆 | Top performers |
| 📈 | Growth, trends up |
| 📉 | Decline, trends down |
| 🗺️ | Geographic, locations |
| 🏙️ | Cities |
| 🤝 | Dealers, partners |
| 📂 | Categories |
| ⚡ | Quick actions |
| 🔐 | Authentication |
| 📅 | Dates, calendar |
| 🔧 | Settings, controls |
| 🔄 | Refresh, reload |
| 🔍 | Search |
| 📥 | Export, download |
| 📋 | Data, tables |
| 🎨 | Customization |
| 💾 | Save |
| ✅ | Success |
| ❌ | Error |
| ⚠️ | Warning |

## Accessibility

### Contrast Ratios
- **Text on white:** #1f2937 (15.8:1) ✅
- **Muted text:** #6b7280 (4.6:1) ✅
- **Primary on white:** #6366f1 (4.8:1) ✅
- **Success on white:** #10b981 (4.7:1) ✅

### Focus States
```css
:focus {
    outline: 3px solid rgba(99, 102, 241, 0.5);
    outline-offset: 2px;
}
```

### ARIA Labels
```python
dbc.Button(
    "Edit",
    id='edit-btn',
    aria_label="Edit record"
)
```

## CSS Utility Classes

### Background Colors
```css
.bg-primary { background: #6366f1; }
.bg-success { background: #10b981; }
.bg-danger { background: #ef4444; }
.bg-light { background: #f9fafb; }
```

### Text Colors
```css
.text-primary { color: #6366f1; }
.text-muted { color: #6b7280; }
.text-dark { color: #1f2937; }
```

### Gradients
```css
.gradient-primary {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
}

.gradient-success {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}
```

### Custom Classes
```css
.fade-in          /* Fade in animation */
.clickable        /* Hover pointer + scale */
.gradient-text    /* Gradient text effect */
.shadow-sm        /* Subtle shadow */
.shadow-lg        /* Large shadow */
```

## Quick Tips

### DO ✅
- Use consistent spacing (multiples of 4px)
- Apply hover states to clickable elements
- Use proper font hierarchy
- Keep animations subtle (≤0.3s)
- Test on mobile devices
- Use semantic colors (success=green, danger=red)

### DON'T ❌
- Mix different shadow styles
- Use arbitrary font sizes
- Forget responsive breakpoints
- Make animations too long
- Overcrowd layouts
- Ignore accessibility

## Code Templates

### Metric Card
```python
dbc.Card([
    dbc.CardBody([
        html.Div([
            html.Span("💰", style={'fontSize': '24px'}),
            html.Span("Revenue", className="text-muted")
        ]),
        html.H4("$123,456", className="fw-bold"),
        dbc.Badge("+12.5%", color="success")
    ], style={'background': 'linear-gradient(...)'})
], className="shadow-sm", style={'borderRadius': '12px'})
```

### Section Header
```python
html.Div([
    html.H4("📈 Analytics", className="mb-4 fw-bold"),
    dbc.Row([...])  # Content
])
```

### Modal/Alert
```python
dbc.Alert([
    html.Strong("Success!"),
    " Your changes have been saved."
], color="success", className="shadow-sm")
```

## Resources

- **Theme:** Bootstrap LUX
- **Font:** Inter (Google Fonts)
- **Icons:** Emojis (Unicode)
- **Charts:** Plotly (plotly_white template)
- **Grid:** Bootstrap 5 grid system

---

**Version:** 1.0
**Last Updated:** January 2026
**Status:** Production Ready
