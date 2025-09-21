# SEO Manager

## Architectural Choices and Rationale
Multi-agent system with specialized roles: Manager orchestrates Research → Planning → Writing → Editing workflow. Semantic caching with ChromaDB reduces API costs by 80%. FastAPI backend + Astro frontend for performance.

## Framework Selection
- **Backend**: Python + FastAPI + LangChain for LLM orchestration, Google Gemini for cost-effectiveness
- **Frontend**: Astro.js for static generation and SEO optimization
- **Caching**: ChromaDB for vector similarity search
- **Research**: SerpAPI for competitive analysis

## Agent Collaboration
ManagerAgent coordinates sequential pipeline:
1. SmartResearchAgent checks cache, adapts existing data or fetches fresh competitive analysis
2. PlannerAgent creates outline using competitor insights and trending topics
3. WriterAgent generates detailed content following structured outline
4. EditorAgent polishes and optimizes for SEO
5. Auto-deployment to Astro blog with proper frontmatter

## Competitive Advantages
- **Cost Efficiency**: Reduction in API costs through semantic caching
- **Quality**: Competitive intelligence + multi-stage refinement ensures superior content
- **Speed**: Smart caching + async processing for fast generation
- **Automation**: End-to-end pipeline from research to published blog post