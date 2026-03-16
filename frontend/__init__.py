"""
Web dashboard for Stellar Whisk Parallelism Profiler.
"""

from .app import create_app
from .routes import dashboard_api

__all__ = ["create_app", "dashboard_api"]
