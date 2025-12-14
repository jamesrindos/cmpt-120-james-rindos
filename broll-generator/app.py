"""
Hyperlocal B-Roll Generator
A sleek web application that generates hyperlocalized B-roll footage
using Google Maps Street View, Nanobanana Pro, and Veo 3.1
"""

import os
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import uuid

from services.places_service import PlacesService
from services.streetview_service import StreetViewService
from services.nanobanana_service import NanobananService
from services.veo_service import VeoService
from services.orchestrator import BRollOrchestrator

app = FastAPI(
    title="Hyperlocal B-Roll Generator",
    description="Generate stunning B-roll footage from any location",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize services
places_service = PlacesService()
streetview_service = StreetViewService()
nanobanana_service = NanobananService()
veo_service = VeoService()
orchestrator = BRollOrchestrator(
    places_service,
    streetview_service,
    nanobanana_service,
    veo_service
)

# In-memory job storage (use Redis/DB in production)
jobs = {}


class GenerateRequest(BaseModel):
    location: str
    creative_direction: str
    num_clips: Optional[int] = 5


class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    message: str
    clips: list = []


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the main application page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/generate", response_model=JobStatus)
async def generate_broll(request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    Start B-roll generation process

    1. Find points of interest based on location and creative direction
    2. Capture Street View images
    3. Enhance images with Nanobanana Pro
    4. Generate video clips with Veo 3.1
    """
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "status": "queued",
        "progress": 0,
        "message": "Starting generation...",
        "clips": [],
        "location": request.location,
        "creative_direction": request.creative_direction
    }

    # Run generation in background
    background_tasks.add_task(
        run_generation_pipeline,
        job_id,
        request.location,
        request.creative_direction,
        request.num_clips
    )

    return JobStatus(
        job_id=job_id,
        status="queued",
        progress=0,
        message="Generation started",
        clips=[]
    )


async def run_generation_pipeline(
    job_id: str,
    location: str,
    creative_direction: str,
    num_clips: int
):
    """Execute the full B-roll generation pipeline"""
    try:
        # Update status: Finding POIs
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 10
        jobs[job_id]["message"] = "Discovering points of interest..."

        # Step 1: Find points of interest
        pois = await orchestrator.discover_pois(location, creative_direction, num_clips)

        jobs[job_id]["progress"] = 25
        jobs[job_id]["message"] = f"Found {len(pois)} locations. Capturing Street View imagery..."

        # Step 2: Capture Street View images
        raw_images = await orchestrator.capture_streetview_images(pois)

        jobs[job_id]["progress"] = 45
        jobs[job_id]["message"] = "Enhancing images with Nanobanana Pro..."

        # Step 3: Enhance images
        enhanced_images = await orchestrator.enhance_images(raw_images, creative_direction)

        jobs[job_id]["progress"] = 65
        jobs[job_id]["message"] = "Generating video clips with Veo 3.1..."

        # Step 4: Generate video clips
        clips = await orchestrator.generate_videos(enhanced_images, creative_direction)

        jobs[job_id]["progress"] = 100
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["message"] = f"Generated {len(clips)} B-roll clips!"
        jobs[job_id]["clips"] = clips

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["message"] = f"Generation failed: {str(e)}"


@app.get("/api/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get the status of a generation job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return JobStatus(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"],
        message=job["message"],
        clips=job.get("clips", [])
    )


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Hyperlocal B-Roll Generator"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
