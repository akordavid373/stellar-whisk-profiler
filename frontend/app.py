"""
FastAPI application for the Stellar Whisk dashboard.
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
from pathlib import Path

from .routes import router as api_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Stellar Whisk Parallelism Profiler Dashboard",
        description="Web interface for visualizing parallelism profiling results for Stellar applications",
        version="0.1.0",
    )
    
    # Get the directory containing this file
    dashboard_dir = Path(__file__).parent
    static_dir = dashboard_dir / "static"
    templates_dir = dashboard_dir / "templates"
    
    # Create directories if they don't exist
    static_dir.mkdir(exist_ok=True)
    templates_dir.mkdir(exist_ok=True)
    
    # Mount static files
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Setup templates
    templates = Jinja2Templates(directory=str(templates_dir))
    
    # Include API routes
    app.include_router(api_router, prefix="/api")
    
    # Main dashboard route
    @app.get("/", response_class=HTMLResponse)
    async def dashboard_home(request: Request):
        """Serve the main dashboard page."""
        return templates.TemplateResponse("index.html", {"request": request})
    
    # Health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "stellar-whisk-dashboard"}
    
    return app


def main():
    """Main entry point for running the dashboard."""
    import uvicorn
    
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")


if __name__ == "__main__":
    main()
