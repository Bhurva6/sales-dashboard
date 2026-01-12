"""
WSGI entry point for Vercel deployment
Vercel requires a WSGI-compatible application for Python runtime
"""
from app import app

# Export the Dash server for Vercel
if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=3000)
