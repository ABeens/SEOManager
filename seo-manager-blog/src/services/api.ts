// API service for SEO blog post generation
const API_BASE_URL = 'http://localhost:8000';

export interface BlogPostRequest {
  topic: string;
  keyword: string;
  tone: string;
}

export interface CompetitorInfo {
  title: string;
  snippet: string;
  link: string;
  position: number;
}

export interface TrendingTopic {
  title: string;
  source: string;
  date: string;
}

export interface CompetitiveAnalysis {
  top_competitors: CompetitorInfo[];
  people_also_ask: string[];
  related_searches: string[];
}

export interface BlogPostResponse {
  topic: string;
  keyword: string;
  tone: string;
  final_post: string;
  outline: string;
  competitive_analysis: CompetitiveAnalysis;
  trending_topics: TrendingTopic[];
  generation_id: string;
}

export interface BlogPostStatus {
  status: string;
  message?: string;
  progress?: number;
}

export interface GenerateJobResponse {
  job_id: string;
  status: string;
  message: string;
  check_status_url: string;
}

class ApiService {
  async startBlogGeneration(request: BlogPostRequest): Promise<GenerateJobResponse> {
    const response = await fetch(`${API_BASE_URL}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async getJobStatus(jobId: string): Promise<BlogPostStatus> {
    const response = await fetch(`${API_BASE_URL}/status/${jobId}`);

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async getJobResult(jobId: string): Promise<BlogPostResponse> {
    const response = await fetch(`${API_BASE_URL}/result/${jobId}`);

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async generateBlogSync(request: BlogPostRequest): Promise<BlogPostResponse> {
    const response = await fetch(`${API_BASE_URL}/generate-sync`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async pollJobUntilComplete(
    jobId: string,
    onProgress?: (status: BlogPostStatus) => void
  ): Promise<BlogPostResponse> {
    const pollInterval = 2000; // 2 seconds
    const maxAttempts = 300; // 10 minutes max
    let attempts = 0;

    while (attempts < maxAttempts) {
      const status = await this.getJobStatus(jobId);

      if (onProgress) {
        onProgress(status);
      }

      if (status.status === 'completed') {
        return this.getJobResult(jobId);
      }

      if (status.status === 'error') {
        throw new Error(status.message || 'Blog generation failed');
      }

      await new Promise(resolve => setTimeout(resolve, pollInterval));
      attempts++;
    }

    throw new Error('Blog generation timed out');
  }

  async checkHealth(): Promise<{ status: string; message: string; timestamp: string }> {
    const response = await fetch(`${API_BASE_URL}/health`);

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }
}

export const apiService = new ApiService();