"""
Entry point for local development and Vercel deployment.

All routes and configuration live in the app/ package.
"""
from app import app
from fasthtml.common import serve

if __name__ == '__main__':
    serve(port=5002)
