"""
Configuration management module for the codebase analyzer.
Loads and validates configuration from environment variables.
"""
import os
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator

# Load environment variables
load_dotenv()


class Config(BaseModel):
    """Configuration settings for the codebase analyzer."""
    
    # LLM Provider Configuration
    llm_provider: str = Field(default="github", description="LLM provider to use")
    github_token: Optional[str] = Field(default=None, description="GitHub Personal Access Token")
    github_model: str = Field(default="gpt-4o-mini", description="GitHub Models model name")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-4-turbo-preview", description="OpenAI model name")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    anthropic_model: str = Field(default="claude-3-sonnet-20240229", description="Anthropic model name")
    
    # Repository Configuration
    repo_url: str = Field(
        default="https://github.com/janjakovacevic/SakilaProject",
        description="GitHub repository URL"
    )
    repo_local_path: str = Field(
        default="./data/SakilaProject",
        description="Local path to clone repository"
    )
    
    # Token Limits
    max_tokens_per_chunk: int = Field(
        default=6000,
        description="Maximum tokens per chunk for LLM processing"
    )
    max_output_tokens: int = Field(
        default=2000,
        description="Maximum output tokens from LLM"
    )
    
    # File Processing Configuration
    include_file_extensions: List[str] = Field(
        default=[".java", ".xml", ".properties", ".md"],
        description="File extensions to include in analysis"
    )
    exclude_directories: List[str] = Field(
        default=[".git", "target", "bin", ".idea", ".vscode", "node_modules"],
        description="Directories to exclude from analysis"
    )
    
    # Output Configuration
    output_dir: str = Field(default="./output", description="Output directory for results")
    
    @validator("llm_provider")
    def validate_llm_provider(cls, v):
        """Validate LLM provider is supported."""
        if v not in ["github", "openai", "anthropic"]:
            raise ValueError("LLM provider must be 'github', 'openai', or 'anthropic'")
        return v
    
    @validator("github_token", always=True)
    def validate_github_token(cls, v, values):
        """Validate GitHub token if GitHub is the provider."""
        if values.get("llm_provider") == "github" and not v:
            raise ValueError("GitHub token is required when using GitHub provider")
        return v
    
    @validator("openai_api_key", always=True)
    def validate_openai_key(cls, v, values):
        """Validate OpenAI API key if OpenAI is the provider."""
        if values.get("llm_provider") == "openai" and not v:
            raise ValueError("OpenAI API key is required when using OpenAI provider")
        return v
    
    @validator("anthropic_api_key", always=True)
    def validate_anthropic_key(cls, v, values):
        """Validate Anthropic API key if Anthropic is the provider."""
        if values.get("llm_provider") == "anthropic" and not v:
            raise ValueError("Anthropic API key is required when using Anthropic provider")
        return v
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            llm_provider=os.getenv("LLM_PROVIDER", "github"),
            github_token=os.getenv("GITHUB_TOKEN"),
            github_model=os.getenv("GITHUB_MODEL", "gpt-4o-mini"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
            repo_url=os.getenv("REPO_URL", "https://github.com/janjakovacevic/SakilaProject"),
            repo_local_path=os.getenv("REPO_LOCAL_PATH", "./data/SakilaProject"),
            max_tokens_per_chunk=int(os.getenv("MAX_TOKENS_PER_CHUNK", "6000")),
            max_output_tokens=int(os.getenv("MAX_OUTPUT_TOKENS", "2000")),
            include_file_extensions=os.getenv(
                "INCLUDE_FILE_EXTENSIONS", 
                ".java,.xml,.properties,.md"
            ).split(","),
            exclude_directories=os.getenv(
                "EXCLUDE_DIRECTORIES",
                ".git,target,bin,.idea,.vscode,node_modules"
            ).split(","),
            output_dir=os.getenv("OUTPUT_DIR", "./output")
        )


# Global configuration instance
config = Config.from_env()
