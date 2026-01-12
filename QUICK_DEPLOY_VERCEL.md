# 🚀 Quick Deploy to Vercel - Step by Step

## 1. Prepare Your Code

```bash
# Update requirements.txt (already done)
# Already added: gunicorn

# Verify files exist:
# ✅ app.py (main Dash application)
# ✅ api_client.py (API integration)
# ✅ requirements.txt (dependencies)
# ✅ vercel.json (deployment config)
# ✅ wsgi.py (WSGI entry point)
# ✅ .vercelignore (files to exclude)
```

## 2. Commit to GitHub

```bash
cd /Users/bhurvasharma/dashboard

# Stage all changes
git add .

# Commit
git commit -m "feat: Add Vercel deployment configuration"

# Push to GitHub
git push origin main
```

## 3. Deploy to Vercel

### Option A: Via Vercel Web (Easiest)

1. Go to **https://vercel.com**
2. Sign in with GitHub
3. Click **"Add New"** → **"Project"**
4. Select your repository: **dashboard**
5. Framework: Select **"Other"**
6. Click **"Deploy"**
7. Wait for deployment to complete (~2-3 minutes)
8. You'll get a URL like: `https://your-dashboard.vercel.app`

### Option B: Via Vercel CLI

```bash
# Install Vercel CLI (one-time)
npm install -g vercel

# Deploy
cd /Users/bhurvasharma/dashboard
vercel --prod

# Follow the prompts
```

## 4. Configure Environment Variables

If your API requires credentials:

1. Go to your Vercel dashboard
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add these variables:

```
API_BASE_URL=https://avantemedicals.com/API/api.php
API_USERNAME=your_username
API_PASSWORD=your_password
```

5. Redeploy: Click **"Redeploy"** or push code again

## 5. Update api_client.py (CRITICAL!)

Your `api_client.py` imports Streamlit which won't work on Vercel.

**Remove this line:**
```python
import streamlit as st  # ❌ REMOVE THIS
```

**Replace Streamlit session state calls with environment variables:**

```python
# ❌ OLD:
st.session_state.authenticated = True

# ✅ NEW:
import os
os.environ['AUTHENTICATED'] = 'true'
```

Or better yet, use `requests.Session()` for persistence.

## 6. Test Locally First (Optional)

```bash
# Install Vercel CLI
npm install -g vercel

# Run locally in Vercel environment
vercel dev

# Should start on http://localhost:3000
```

## 7. Monitor Your Deployment

```bash
# View deployment logs
vercel logs your-dashboard-name

# View real-time logs
vercel logs your-dashboard-name --follow
```

## Common Issues & Fixes

### Issue: "Module 'streamlit' not found"
**Fix**: Remove all Streamlit imports from `api_client.py`

### Issue: "API connection timeout"
**Fix**: Make sure API is accessible from external servers

### Issue: "Port 8050 already in use"
**Fix**: Vercel automatically handles port allocation - this won't happen on Vercel

### Issue: "ModuleNotFoundError: No module named 'api_client'"
**Fix**: Make sure all files are in the root directory and committed to Git

## Deployment Checklist

- [ ] All code committed and pushed to GitHub
- [ ] `vercel.json` exists in root
- [ ] `requirements.txt` includes all dependencies
- [ ] `app.py` exports `server` variable
- [ ] Removed Streamlit from `api_client.py`
- [ ] Environment variables configured in Vercel
- [ ] Tested locally with `vercel dev`
- [ ] Deployed with `vercel --prod`
- [ ] Verified live at your Vercel URL

## Next: Share Your Dashboard

Once deployed, your dashboard is live at:
```
https://<your-project>.vercel.app
```

Share this URL with your team!

---

## Support

- Vercel Docs: https://vercel.com/docs
- Dash Docs: https://dash.plotly.com/
- Python on Vercel: https://vercel.com/docs/runtimes/python

