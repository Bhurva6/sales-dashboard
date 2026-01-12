"""
WSGI entry point for Vercel and production servers
Gunicorn and other WSGI servers will use this
"""
import os
import sys

# Ensure the app module can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

# Create the WSGI application
application = app.server

if __name__ == '__main__':
    # Development only
    app.run_server(debug=False, host='0.0.0.0', port=3000)

