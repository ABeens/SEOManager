from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class BlogPostRequest(BaseModel):
    """Request model for blog post generation"""
    topic: str = Field(..., description="The main topic for the blog post", min_length=1)
    keyword: str = Field(..., description="SEO keyword to target", min_length=1)
    tone: str = Field(default="professional", description="Writing tone (professional, casual, technical, etc.)")


class CompetitorInfo(BaseModel):
    """Competitor analysis information"""
    title: str
    snippet: str
    link: str
    position: int


class TrendingTopic(BaseModel):
    """Trending topic information"""
    title: str
    source: str
    date: str


class CompetitiveAnalysis(BaseModel):
    """Competitive analysis results"""
    top_competitors: List[CompetitorInfo]
    people_also_ask: List[str]
    related_searches: List[str]


class BlogPostResponse(BaseModel):
    """Response model for generated blog post"""
    topic: str
    keyword: str
    tone: str
    final_post: str
    outline: str
    competitive_analysis: CompetitiveAnalysis
    trending_topics: List[TrendingTopic]
    generation_id: str = Field(..., description="Unique identifier for this generation")


class BlogPostStatus(BaseModel):
    """Status of blog post generation"""
    status: str = Field(..., description="Status: pending, processing, completed, error")
    message: Optional[str] = Field(None, description="Status message or error details")
    progress: Optional[int] = Field(None, description="Progress percentage (0-100)")


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    message: str
    timestamp: str