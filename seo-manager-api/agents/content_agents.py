from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from typing import Dict, Any


class PlannerAgent:
    """Content planner agent with competitive intelligence"""

    def __init__(self):
        self.chain = self._build_chain()

    def _build_chain(self) -> LLMChain:
        prompt = ChatPromptTemplate.from_template(
            "You are a senior editor. Generate a competitive outline for a blog post about: {topic}.\n"
            "SEO Keyword: {keyword}. Tone: {tone}.\n\n"
            "COMPETITIVE ANALYSIS:\n"
            "Top competitors: {competitors}\n"
            "People also ask: {people_ask}\n"
            "Related searches: {related_searches}\n"
            "Trending topics: {trending}\n\n"
            "Create an outline that OUTPERFORMS the competition using these insights.\n"
            "Return JSON with title, meta_description, sections (heading+bullets)."
        )
        return LLMChain(
            llm=ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2),
            prompt=prompt,
            output_key="outline"
        )

    def generate_outline(self, data: Dict[str, Any]) -> str:
        """Generate competitive outline based on research data"""
        return self.chain.invoke(data)["outline"]


class WriterAgent:
    """Content writer agent"""

    def __init__(self):
        self.chain = self._build_chain()

    def _build_chain(self) -> LLMChain:
        prompt = ChatPromptTemplate.from_template(
            "Write a complete, detailed markdown blog post in {tone} tone.\n"
            "Main keyword: {keyword}.\n"
            "Outline: {outline}\n\n"
            "IMPORTANT REQUIREMENTS:\n"
            "- Write SPECIFIC, detailed content for each section\n"
            "- NO placeholders like '(Insert content here)' or '(Experience 1)'\n"
            "- Include real examples, facts, and actionable information\n"
            "- Write complete paragraphs with substance\n"
            "- If listing items, provide SPECIFIC details for each one\n"
            "- Make it engaging and informative\n"
            "- Use proper markdown formatting\n\n"
            "Return only the complete markdown content with no placeholders or instructions."
        )
        return LLMChain(
            llm=ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.25),
            prompt=prompt,
            output_key="draft"
        )

    def write_content(self, outline: str, keyword: str, tone: str) -> str:
        """Write content based on outline"""
        return self.chain.invoke({
            "outline": outline,
            "keyword": keyword,
            "tone": tone
        })["draft"]


class EditorAgent:
    """Content editor agent"""

    def __init__(self):
        self.chain = self._build_chain()

    def _build_chain(self) -> LLMChain:
        prompt = ChatPromptTemplate.from_template(
            "Edit and polish the following markdown for better SEO and clarity.\n"
            "Markdown: {draft}\n\n"
            "CRITICAL EDITING REQUIREMENTS:\n"
            "- Remove ALL placeholders like '(Insert content here)', '(Experience 1)', etc.\n"
            "- Replace any generic content with specific, detailed information\n"
            "- Ensure all lists have actual, specific items with details\n"
            "- Remove any instructional text or notes to editors\n"
            "- Make sure every section has substantial, useful content\n"
            "- Improve readability and SEO optimization\n"
            "- Keep only the final, publication-ready content\n\n"
            "Return only the clean, complete markdown without any placeholders or editorial notes."
        )
        return LLMChain(
            llm=ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0),
            prompt=prompt,
            output_key="final_post"
        )

    def edit_content(self, draft: str) -> str:
        """Edit and polish content"""
        return self.chain.invoke({"draft": draft})["final_post"]