#!/usr/bin/env python3
"""
Entrypoint script for Railway deployment.
Handles PORT environment variable properly.
"""
import os
import subprocess
import sys

# Get port from environment, default to 8080
port = os.environ.get('PORT', '8080')

print(f"Starting gunicorn on port {port}")

# Run gunicorn with the port
cmd = [
    sys.executable, '-m', 'gunicorn',
    'app:app',
    '--bind', f'0.0.0.0:{port}',
    '--workers', '4',
    '--timeout', '120'
]

# Replace current process with gunicorn
os.execvp(sys.executable, cmd)
