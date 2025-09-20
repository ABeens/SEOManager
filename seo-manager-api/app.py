import uuid
import asyncio
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
import os

from models import (
    BlogPostRequest,
    BlogPostResponse,
    BlogPostStatus,
    HealthCheck,
    CompetitiveAnalysis,
    TrendingTopic
)
from agents.manager_agent import ManagerAgent

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="SEO Blog Post Generator API",
    description="Multi-agent system for generating competitive, SEO-optimized blog posts",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the manager agent
manager = ManagerAgent()

# In-memory storage for job status (use Redis/DB for production)
job_status = {}


async def generate_blog_post_task(job_id: str, request: BlogPostRequest):
    """Background task for blog post generation"""
    try:
        job_status[job_id] = {"status": "processing", "progress": 10}

        # Generate blog post using the manager agent
        result = manager.generate_blog_post(
            topic=request.topic,
            keyword=request.keyword,
            tone=request.tone
        )

        job_status[job_id] = {
            "status": "completed",
            "progress": 100,
            "result": result
        }

    except Exception as e:
        job_status[job_id] = {
            "status": "error",
            "message": str(e),
            "progress": 0
        }


@app.get("/", response_model=HealthCheck)
async def root():
    """Health check endpoint"""
    return HealthCheck(
        status="healthy",
        message="SEO Blog Post Generator API is running",
        timestamp=datetime.now().isoformat()
    )


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Detailed health check"""
    try:
        # Check environment variables
        google_key = os.getenv('GOOGLE_API_KEY')
        serpapi_key = os.getenv('SERPAPI_KEY')

        if not google_key:
            raise Exception("GOOGLE_API_KEY not configured")
        if not serpapi_key:
            raise Exception("SERPAPI_KEY not configured")

        return HealthCheck(
            status="healthy",
            message="All systems operational",
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate", response_model=dict)
async def generate_blog_post(request: BlogPostRequest, background_tasks: BackgroundTasks):
    """
    Start blog post generation process
    Returns a job ID to track progress
    """
    job_id = str(uuid.uuid4())

    # Initialize job status
    job_status[job_id] = {"status": "pending", "progress": 0}

    # Start background task
    background_tasks.add_task(generate_blog_post_task, job_id, request)

    return {
        "job_id": job_id,
        "status": "started",
        "message": "Blog post generation started",
        "check_status_url": f"/status/{job_id}"
    }


@app.get("/status/{job_id}", response_model=BlogPostStatus)
async def get_job_status(job_id: str):
    """Get the status of a blog post generation job"""
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")

    job = job_status[job_id]
    return BlogPostStatus(
        status=job["status"],
        message=job.get("message"),
        progress=job.get("progress")
    )


@app.get("/result/{job_id}", response_model=BlogPostResponse)
async def get_blog_post_result(job_id: str):
    """Get the completed blog post result"""
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")

    job = job_status[job_id]

    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job not completed. Current status: {job['status']}"
        )

    result = job["result"]

    # Transform competitive analysis
    competitive_analysis = CompetitiveAnalysis(
        top_competitors=result["competitive_analysis"]["top_competitors"],
        people_also_ask=result["competitive_analysis"]["people_also_ask"],
        related_searches=result["competitive_analysis"]["related_searches"]
    )

    # Transform trending topics
    trending_topics = [
        TrendingTopic(**topic) for topic in result["trending_topics"]
    ]

    return BlogPostResponse(
        topic=result["topic"],
        keyword=result["keyword"],
        tone=result["tone"],
        final_post=result["final_post"],
        outline=result["outline"],
        competitive_analysis=competitive_analysis,
        trending_topics=trending_topics,
        generation_id=job_id
    )


@app.post("/generate-sync", response_model=BlogPostResponse)
async def generate_blog_post_sync(request: BlogPostRequest):
    """
    Synchronous blog post generation (for testing/development)
    Warning: This may take several minutes to complete
    """
    try:
        job_id = str(uuid.uuid4())

        # Generate blog post synchronously
        result = manager.generate_blog_post(
            topic=request.topic,
            keyword=request.keyword,
            tone=request.tone
        )

        # Transform and return result
        competitive_analysis = CompetitiveAnalysis(
            top_competitors=result["competitive_analysis"]["top_competitors"],
            people_also_ask=result["competitive_analysis"]["people_also_ask"],
            related_searches=result["competitive_analysis"]["related_searches"]
        )

        trending_topics = [
            TrendingTopic(**topic) for topic in result["trending_topics"]
        ]

        return BlogPostResponse(
            topic=result["topic"],
            keyword=result["keyword"],
            tone=result["tone"],
            final_post=result["final_post"],
            outline=result["outline"],
            competitive_analysis=competitive_analysis,
            trending_topics=trending_topics,
            generation_id=job_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)