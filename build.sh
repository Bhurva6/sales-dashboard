#!/bin/bash
set -e

echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

echo "=== Building Next.js frontend ==="
cd frontend-nextjs
npm install
npm run build
cd ..

echo "=== Build complete ==="
