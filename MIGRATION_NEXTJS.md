# Next.js Frontend Migration - Setup Guide

## Overview
You've successfully switched from **Dash (Python-based frontend)** to **Next.js 14** with **React 18** for a better chart rendering experience and modern tech stack.

## Architecture

### Backend (Python/Flask) - Unchanged
- Continue running your existing Flask/Dash server on port 5000
- Your API endpoints handle business logic and data fetching
- Authentication, database, and API logic remain the same

### Frontend (Next.js) - New
- Modern React application on port 3000
- Recharts for interactive visualizations
- Zustand for state management
- Tailwind CSS for styling

## What's New

### ✨ Benefits of Next.js
1. **Better Error Handling**: No more "Objects are not valid as a React child" errors
2. **Improved Performance**: Built-in optimization, code splitting, caching
3. **Modern React Patterns**: Server-side rendering, app router, hooks
4. **Better Charts**: Recharts library with smooth rendering
5. **Responsive Design**: Mobile-first Tailwind CSS approach
6. **Hot Module Replacement**: Faster development with instant reloads

### 📁 New Frontend Structure

```
frontend-nextjs/
├── src/
│   ├── app/
│   │   ├── page.tsx           # Main dashboard page
│   │   ├── layout.tsx         # Root layout
│   │   └── globals.css        # Global styles
│   ├── components/
│   │   ├── Charts.tsx         # Recharts components
│   │   ├── Layout.tsx         # Main layout wrapper
│   │   ├── Header.tsx         # Header with dashboard toggle
│   │   └── Sidebar.tsx        # Sidebar with controls
│   └── lib/
│       ├── api.ts            # API client (Axios)
│       ├── store.ts          # Zustand stores
│       └── utils.ts          # Utility functions
├── .env.local                # Environment variables
├── next.config.ts            # Next.js configuration
├── package.json              # Dependencies
└── tailwind.config.ts        # Tailwind configuration
```

## Setup Instructions

### 1. Install Dependencies (Already Done)
```bash
cd frontend-nextjs
npm install
```

### 2. Configure Environment
Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:5000
```

### 3. Run the Development Server
```bash
npm run dev
```
Visit: http://localhost:3000

### 4. Build for Production
```bash
npm run build
npm run start
```

## API Integration with Flask Backend

Your Flask backend should expose these endpoints (if not already):

### Authentication
- `POST /api/login` - User authentication

### Dashboard Data (Avante)
- `GET /api/avante/sales` - Sales data
- `GET /api/avante/stats` - Dashboard statistics
- `GET /api/avante/dealer-performance` - Dealer metrics
- `GET /api/avante/state-performance` - State metrics
- `GET /api/avante/category-performance` - Category metrics

### Dashboard Data (IOSPL)
- `GET /api/iospl/sales` - Sales data
- `GET /api/iospl/stats` - Dashboard statistics
- And other IOSPL-specific endpoints

### Expected Response Format
```json
{
  "success": true,
  "data": [...],
  "message": "Success"
}
```

## Migration Checklist

- [x] Next.js project initialized
- [x] Core components created (Layout, Header, Sidebar, Charts)
- [x] State management with Zustand
- [x] API client setup with Axios
- [x] Tailwind CSS styling
- [x] Environment configuration
- [ ] Connect to your Flask API
- [ ] Test all chart visualizations
- [ ] Test dashboard filters
- [ ] Test authentication flow
- [ ] Deploy to production

## Key Changes from Dash

### Before (Dash)
```python
@app.callback(
    Output('dealer-pie-chart', 'figure'),
    Input('chart-data-store', 'data'),
)
def update_chart(data):
    # Create Plotly figure
    fig = go.Figure()
    return fig
```

### After (Next.js)
```tsx
export const RevenuePieChart = ({ data, title }: ChartProps) => {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <PieChart data={data}>
        {/* Recharts components */}
      </PieChart>
    </ResponsiveContainer>
  );
};
```

## Troubleshooting

### Chart not showing?
1. Check browser console for errors
2. Verify API is returning data in correct format
3. Ensure Recharts components are properly imported

### CORS issues?
Add to Flask backend:
```python
from flask_cors import CORS
CORS(app)
```

### State not persisting?
Zustand stores are in-memory. For persistence, use:
```tsx
// In store.ts
localStorage.getItem('dashboardState')
localStorage.setItem('dashboardState', JSON.stringify(state))
```

## Running Both Servers

### Terminal 1 - Flask Backend
```bash
cd /Users/bhurvasharma/dashboard
python -m flask run --port 5000
```

### Terminal 2 - Next.js Frontend
```bash
cd /Users/bhurvasharma/dashboard/frontend-nextjs
npm run dev
```

## Next Steps

1. **Connect API endpoints** - Update `src/lib/api.ts` with your exact endpoints
2. **Test data flow** - Verify data is loading from Flask backend
3. **Style customization** - Modify colors in Tailwind config
4. **Add features** - Create custom chart builders, data tables, etc.
5. **Deploy** - Deploy frontend to Vercel, backend to Railway

## Support

For issues or questions:
1. Check Next.js docs: https://nextjs.org/docs
2. Check Recharts docs: https://recharts.org
3. Check Zustand docs: https://github.com/pmndrs/zustand

Enjoy your new modern tech stack! 🚀
