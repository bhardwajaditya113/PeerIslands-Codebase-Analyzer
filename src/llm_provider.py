"""
LLM integration module using LangChain.
Handles interaction with different LLM providers (OpenAI, Anthropic).
"""
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.callbacks import get_openai_callback
from src.config import config


class LLMProvider:
    """Manages LLM provider initialization and interaction."""
    
    def __init__(self):
        self.provider = config.llm_provider
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the appropriate LLM based on configuration."""
        if self.provider == "github":
            # GitHub Models API (FREE for Copilot users!)
            import os
            os.environ["OPENAI_API_KEY"] = config.github_token
            return ChatOpenAI(
                model=config.github_model,
                temperature=0.1,
                base_url="https://models.inference.ai.azure.com",
                # GitHub Models uses OpenAI-compatible API
            )
        elif self.provider == "openai":
            import os
            os.environ["OPENAI_API_KEY"] = config.openai_api_key
            return ChatOpenAI(
                model=config.openai_model,
                temperature=0.1
            )
        elif self.provider == "anthropic":
            try:
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(
                    model=config.anthropic_model,
                    temperature=0.1,
                    max_tokens_to_sample=config.max_output_tokens,
                    anthropic_api_key=config.anthropic_api_key
                )
            except ImportError:
                raise ImportError("Please install langchain-anthropic package for Anthropic support")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def invoke(self, system_prompt: str, user_prompt: str) -> str:
        """
        Invoke the LLM with system and user prompts.
        
        Args:
            system_prompt: System instruction for the LLM
            user_prompt: User query or content to analyze
            
        Returns:
            LLM response as string
        """
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            if self.provider == "openai":
                with get_openai_callback() as cb:
                    response = self.llm.invoke(messages)
                    print(f"  Tokens used: {cb.total_tokens} (prompt: {cb.prompt_tokens}, completion: {cb.completion_tokens})")
                    print(f"  Cost: ${cb.total_cost:.4f}")
            else:
                response = self.llm.invoke(messages)
            
            return response.content
        except Exception as e:
            print(f"Error invoking LLM: {e}")
            raise
    
    def analyze_code_chunk(self, chunk_text: str, chunk_id: int, total_chunks: int) -> Dict[str, Any]:
        """
        Analyze a code chunk and extract structured information.
        
        Args:
            chunk_text: The code chunk to analyze
            chunk_id: ID of current chunk
            total_chunks: Total number of chunks
            
        Returns:
            Dictionary with analysis results
        """
        system_prompt = """You are an expert code analyzer. Analyze the provided code and extract structured information.
Focus on:
1. Key classes and their purposes
2. Important methods with signatures and descriptions
3. Design patterns used
4. Code complexity indicators
5. Dependencies and relationships

Return your analysis in a structured JSON format."""

        user_prompt = f"""Analyze the following code (Chunk {chunk_id + 1}/{total_chunks}):

{chunk_text}

Please provide a JSON response with the following structure:
{{
    "chunk_id": {chunk_id},
    "files": [
        {{
            "path": "file/path",
            "classes": [
                {{
                    "name": "ClassName",
                    "purpose": "Brief description",
                    "methods": [
                        {{
                            "name": "methodName",
                            "signature": "returnType methodName(params)",
                            "description": "What this method does",
                            "complexity": "low/medium/high"
                        }}
                    ],
                    "relationships": ["depends on X", "implements Y"]
                }}
            ],
            "key_functions": [],
            "complexity_notes": "Overall complexity assessment"
        }}
    ]
}}

Be concise but thorough. Focus on the most important elements."""

        response = self.invoke(system_prompt, user_prompt)
        
        # Parse JSON response
        import json
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse JSON response from LLM: {e}")
            print(f"Raw response: {response[:500]}...")
            return {
                "chunk_id": chunk_id,
                "files": [],
                "raw_response": response,
                "parse_error": str(e)
            }
    
    def generate_project_overview(self, overview_text: str, repo_info: Dict) -> Dict[str, Any]:
        """
        Generate high-level project overview.
        
        Args:
            overview_text: Project structure and README content
            repo_info: Repository metadata
            
        Returns:
            Dictionary with project overview
        """
        system_prompt = """You are an expert software architect analyzing a codebase. 
Provide a high-level overview of the project including its purpose, architecture, and key technologies."""

        user_prompt = f"""Analyze this project overview:

Repository: {repo_info.get('url', 'Unknown')}

{overview_text}

Please provide a JSON response with:
{{
    "project_name": "Name of the project",
    "purpose": "What this project does",
    "domain": "Application domain (e.g., e-commerce, data processing, web app)",
    "key_technologies": ["tech1", "tech2"],
    "architecture_style": "MVC, Microservices, Layered, etc.",
    "main_components": [
        {{
            "name": "component name",
            "description": "what it does"
        }}
    ],
    "estimated_complexity": "low/medium/high",
    "notable_features": ["feature1", "feature2"]
}}"""

        response = self.invoke(system_prompt, user_prompt)
        
        # Parse JSON response
        import json
        try:
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            
            overview = json.loads(response)
            overview["repository_info"] = repo_info
            return overview
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse JSON response: {e}")
            return {
                "project_name": "Unknown",
                "purpose": response[:500],
                "repository_info": repo_info,
                "parse_error": str(e)
            }
