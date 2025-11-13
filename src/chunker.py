"""
Code chunking module for splitting codebase into manageable chunks.
Implements intelligent chunking strategies to respect token limits.
"""
import tiktoken
from typing import List, Dict
from src.repository_manager import CodeFile
from src.config import config


class CodeChunk:
    """Represents a chunk of code with metadata."""
    
    def __init__(self, files: List[CodeFile], chunk_id: int):
        self.files = files
        self.chunk_id = chunk_id
        self.token_count = 0
        
    def to_text(self) -> str:
        """Convert chunk to text representation for LLM processing."""
        text_parts = []
        for file in self.files:
            text_parts.append(f"=== File: {file.relative_path} ===")
            text_parts.append(f"Extension: {file.extension}")
            text_parts.append(f"Lines: {len(file.content.split(chr(10)))}")
            text_parts.append(f"\nContent:\n{file.content}\n")
            text_parts.append("=" * 80)
        return "\n".join(text_parts)
    
    def get_file_list(self) -> List[str]:
        """Get list of file paths in this chunk."""
        return [f.relative_path for f in self.files]


class CodeChunker:
    """Handles chunking of codebase into token-limited chunks."""
    
    def __init__(self, model_name: str = "gpt-4"):
        """Initialize the chunker with token encoding."""
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # Fallback to cl100k_base encoding (used by GPT-4)
            self.encoding = tiktoken.get_encoding("cl100k_base")
        
        self.max_tokens = config.max_tokens_per_chunk
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string."""
        return len(self.encoding.encode(text))
    
    def create_chunks(self, code_files: List[CodeFile]) -> List[CodeChunk]:
        """
        Create chunks from code files, ensuring each chunk stays within token limits.
        
        Strategy:
        1. Group files by directory/type for context
        2. Add files to chunks until token limit is reached
        3. Create new chunk when limit is exceeded
        """
        chunks = []
        current_chunk_files = []
        current_tokens = 0
        chunk_id = 0
        
        # Sort files by directory for better grouping
        sorted_files = sorted(code_files, key=lambda f: f.relative_path)
        
        print(f"\nChunking {len(sorted_files)} files...")
        
        for file in sorted_files:
            # Create a temporary chunk to test token count
            test_chunk = CodeChunk(current_chunk_files + [file], chunk_id)
            test_text = test_chunk.to_text()
            test_tokens = self.count_tokens(test_text)
            
            # If adding this file exceeds limit, finalize current chunk
            if test_tokens > self.max_tokens and current_chunk_files:
                chunk = CodeChunk(current_chunk_files, chunk_id)
                chunk.token_count = current_tokens
                chunks.append(chunk)
                print(f"  Chunk {chunk_id}: {len(current_chunk_files)} files, ~{current_tokens} tokens")
                
                # Start new chunk
                chunk_id += 1
                current_chunk_files = [file]
                current_tokens = self.count_tokens(CodeChunk([file], chunk_id).to_text())
            else:
                # Add file to current chunk
                current_chunk_files.append(file)
                current_tokens = test_tokens
            
            # Handle case where single file exceeds token limit
            if test_tokens > self.max_tokens and not current_chunk_files[:-1]:
                print(f"  Warning: File {file.relative_path} exceeds token limit, chunking it separately")
                # For very large files, we'll still include them but note the warning
                chunk = CodeChunk([file], chunk_id)
                chunk.token_count = test_tokens
                chunks.append(chunk)
                print(f"  Chunk {chunk_id}: 1 file (large), ~{test_tokens} tokens")
                
                chunk_id += 1
                current_chunk_files = []
                current_tokens = 0
        
        # Add remaining files as final chunk
        if current_chunk_files:
            chunk = CodeChunk(current_chunk_files, chunk_id)
            chunk.token_count = current_tokens
            chunks.append(chunk)
            print(f"  Chunk {chunk_id}: {len(current_chunk_files)} files, ~{current_tokens} tokens")
        
        print(f"\nCreated {len(chunks)} chunks")
        return chunks
    
    def create_project_overview_chunk(self, code_files: List[CodeFile]) -> str:
        """
        Create a high-level overview chunk with file structure and README content.
        """
        overview_parts = []
        overview_parts.append("=== PROJECT STRUCTURE ===\n")
        
        # Group files by extension
        files_by_ext: Dict[str, List[str]] = {}
        readme_content = None
        
        for file in code_files:
            ext = file.extension or "no_extension"
            if ext not in files_by_ext:
                files_by_ext[ext] = []
            files_by_ext[ext].append(file.relative_path)
            
            # Capture README content
            if "readme" in file.relative_path.lower():
                readme_content = file.content
        
        # Add file structure
        for ext, files in sorted(files_by_ext.items()):
            overview_parts.append(f"\n{ext} files ({len(files)}):")
            for file in sorted(files)[:50]:  # Limit to first 50 files per type
                overview_parts.append(f"  - {file}")
            if len(files) > 50:
                overview_parts.append(f"  ... and {len(files) - 50} more")
        
        # Add README content if available
        if readme_content:
            overview_parts.append("\n\n=== README CONTENT ===\n")
            overview_parts.append(readme_content)
        
        return "\n".join(overview_parts)
