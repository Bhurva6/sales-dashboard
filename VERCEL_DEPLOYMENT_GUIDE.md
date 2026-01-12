# 🚀 Dash Dashboard Deployment Guide for Vercel

## Overview
This guide covers deploying your **Dash** (not Streamlit) dashboard to Vercel. Your application uses:
- **Dash** for the web framework
- **Plotly** for interactive charts
- **Pandas** for data processing
- **API Client** for ERP backend integration

---

## Pre-Deployment Checklist

### 1. **Verify Your Application Type**
Your main application is **`app.py`** (Dash-based), not the Streamlit `dashboard.py`.

### 2. **Update api_client.py** (Important!)
Your current `api_client.py` imports Streamlit (`import streamlit as st`), which won't work in production.

**Create a new version without Streamlit dependency:**

Replace these lines in `api_client.py`:
```python
# ❌ Remove this:
import streamlit as st
```

Use environment variables or direct configuration instead for session management.

---

## Deployment Steps

### Step 1: Prepare Your GitHub Repository

```bash
# Make sure all files are committed
git add .
git commit -m "feat: Add Vercel deployment configuration"
git push origin main
```

### Step 2: Install Vercel CLI (Local Testing)

```bash
# Install Vercel CLI globally
npm install -g vercel

# Or if using Homebrew on macOS
brew install vercel-cli
```

### Step 3: Test Locally with Vercel

```bash
# Navigate to your project directory
cd /Users/bhurvasharma/dashboard

# Test the deployment locally
vercel dev

# This will start a local server similar to production
```

### Step 4: Deploy to Vercel

#### Option A: Deploy via CLI (Recommended)

```bash
vercel --prod
```

You'll be prompted to:
- Select your project scope
- Confirm project settings
- Link to your GitHub repository (optional)

#### Option B: Deploy via Web UI

1. Go to [vercel.com](https://vercel.com)
2. Sign in with your GitHub account
3. Click "Add New" → "Project"
4. Import your repository
5. Select framework: **"Other"** (since it's a custom Python app)
6. Click "Deploy"

---

## Configuration

### Environment Variables

If your API requires authentication, add these to Vercel:

1. Go to your project settings on vercel.com
2. Navigate to **Settings** → **Environment Variables**
3. Add your environment variables:

```
API_BASE_URL=https://avantemedicals.com/API/api.php
API_USERNAME=your_username
API_PASSWORD=your_password
```

Then update your `app.py` and `api_client.py` to read from environment:

```python
import os

API_BASE_URL = os.getenv('API_BASE_URL', 'https://avantemedicals.com/API/api.php')
API_USERNAME = os.getenv('API_USERNAME')
API_PASSWORD = os.getenv('API_PASSWORD')
```

### Memory & Performance

Vercel has resource limits for serverless functions:
- **Max execution time**: 60 seconds (Pro) or 10 seconds (Free)
- **Memory**: 3GB total
- **Max code size**: 50MB

For large data processing, consider:
- Caching responses
- Paginating data fetches
- Using `@app.callback(prevent_initial_call=True)` for expensive callbacks

---

## Important Changes Needed

### 1. **Remove Streamlit from api_client.py**

Your `api_client.py` currently uses Streamlit for session state. Replace it:

```python
# ❌ OLD (Streamlit-based):
import streamlit as st
st.session_state.authenticated = True

# ✅ NEW (Environment/Flask session-based):
# Use cookies or JWT tokens instead
```

### 2. **Update requirements.txt**

Remove Streamlit if it's there:

```bash
# Current requirements are already good:
pandas
plotly
openpyxl
scikit-learn
numpy
statsmodels
xgboost
requests
dash
dash-bootstrap-components
gunicorn  # Add this for production
```

Add Gunicorn:
```bash
pip install gunicorn
pip freeze > requirements.txt
```

### 3. **Add Production-Safe app.py Start**

Update your `app.py` entry point to handle Vercel:

```python
# At the end of app.py
if __name__ == '__main__':
    # Development
    app.run_server(debug=False, dev_tools_enable=False)
else:
    # Production (Vercel)
    server = app.server
```

---

## Troubleshooting

### Issue: "Module not found" Error
**Solution**: Ensure all imports in `api_client.py` are available in `requirements.txt`

```bash
pip freeze > requirements.txt
```

### Issue: "Streamlit not found" Error
**Solution**: Remove all Streamlit imports from `api_client.py` and use environment variables instead

### Issue: Timeout Error (60 seconds exceeded)
**Solution**: Implement caching for API responses:

```python
from functools import lru_cache
import time

@lru_cache(maxsize=128)
def cached_api_call(date_range):
    # Your API call here
    pass
```

### Issue: "Cannot connect to API"
**Solution**: 
- Verify API URL is accessible from Vercel servers
- Add API URL and credentials to Environment Variables
- Check if API has IP whitelist (Vercel IPs need to be whitelisted)

---

## Monitoring & Logs

After deployment, monitor your app:

1. **Vercel Dashboard**: https://vercel.com/dashboard
2. **View Logs**: 
   ```bash
   vercel logs <project-name>
   ```
3. **Real-time Logs**:
   ```bash
   vercel logs <project-name> --follow
   ```

---

## Git Workflow for Updates

After making changes locally:

```bash
# Test locally
vercel dev

# Commit and push to GitHub
git add .
git commit -m "Update dashboard features"
git push origin main

# Deploy to production
vercel --prod

# Or redeploy automatically if linked to GitHub
```

---

## Vercel Pricing

- **Free**: 1 project, limited invocations
- **Pro**: $20/month, better limits
- **Enterprise**: Custom pricing

For data-intensive dashboards, consider upgrading to Pro.

---

## Next Steps

1. ✅ Update `api_client.py` to remove Streamlit dependency
2. ✅ Test locally with `vercel dev`
3. ✅ Deploy with `vercel --prod`
4. ✅ Add environment variables in Vercel dashboard
5. ✅ Monitor logs for errors
6. ✅ Set up auto-deployment from GitHub

---

## Support Resources

- **Vercel Docs**: https://vercel.com/docs
- **Python on Vercel**: https://vercel.com/docs/runtimes/python
- **Dash Docs**: https://dash.plotly.com/
- **Your Repository**: Push this deployment guide to GitHub for reference

