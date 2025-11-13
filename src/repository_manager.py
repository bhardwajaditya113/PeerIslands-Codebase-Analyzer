"""
Repository management module for cloning and reading codebase files.
"""
import os
import git
from pathlib import Path
from typing import List, Dict, Optional
import chardet
from tqdm import tqdm
from src.config import config


class CodeFile:
    """Represents a single code file with metadata."""
    
    def __init__(self, path: str, relative_path: str, content: str, extension: str):
        self.path = path
        self.relative_path = relative_path
        self.content = content
        self.extension = extension
        self.size = len(content)
        
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "path": self.relative_path,
            "extension": self.extension,
            "size": self.size,
            "lines": len(self.content.split('\n'))
        }


class RepositoryManager:
    """Manages cloning and reading of GitHub repositories."""
    
    def __init__(self):
        self.repo_url = config.repo_url
        self.local_path = Path(config.repo_local_path)
        self.include_extensions = config.include_file_extensions
        self.exclude_dirs = config.exclude_directories
        self.repo = None
        
    def clone_repository(self) -> None:
        """Clone the repository if it doesn't exist locally."""
        if self.local_path.exists():
            print(f"Repository already exists at {self.local_path}")
            try:
                self.repo = git.Repo(self.local_path)
                print("Pulling latest changes...")
                origin = self.repo.remotes.origin
                origin.pull()
                print("Repository updated successfully")
            except Exception as e:
                print(f"Could not update repository: {e}")
                print("Using existing repository")
        else:
            print(f"Cloning repository from {self.repo_url}...")
            self.local_path.parent.mkdir(parents=True, exist_ok=True)
            self.repo = git.Repo.clone_from(self.repo_url, self.local_path)
            print(f"Repository cloned successfully to {self.local_path}")
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Determine if a file should be included in analysis."""
        # Check if file extension is in the include list
        if not any(str(file_path).endswith(ext) for ext in self.include_extensions):
            return False
        
        # Check if file is in an excluded directory
        parts = file_path.parts
        if any(excluded_dir in parts for excluded_dir in self.exclude_dirs):
            return False
        
        return True
    
    def _read_file_content(self, file_path: Path) -> Optional[str]:
        """Read file content with encoding detection."""
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Fallback to encoding detection
            try:
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                    detected = chardet.detect(raw_data)
                    encoding = detected['encoding'] or 'latin-1'
                    return raw_data.decode(encoding)
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")
                return None
    
    def read_codebase(self) -> List[CodeFile]:
        """Read all relevant files from the codebase."""
        code_files = []
        
        print("Scanning repository for code files...")
        all_files = []
        for root, dirs, files in os.walk(self.local_path):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                if self._should_include_file(file_path):
                    all_files.append(file_path)
        
        print(f"Found {len(all_files)} files to analyze")
        
        # Read files with progress bar
        for file_path in tqdm(all_files, desc="Reading files"):
            content = self._read_file_content(file_path)
            if content is not None:
                relative_path = file_path.relative_to(self.local_path)
                extension = file_path.suffix
                
                code_file = CodeFile(
                    path=str(file_path),
                    relative_path=str(relative_path),
                    content=content,
                    extension=extension
                )
                code_files.append(code_file)
        
        print(f"Successfully read {len(code_files)} files")
        return code_files
    
    def get_repository_info(self) -> Dict:
        """Get basic information about the repository."""
        if not self.repo:
            return {}
        
        try:
            return {
                "url": self.repo_url,
                "local_path": str(self.local_path),
                "branch": self.repo.active_branch.name,
                "last_commit": {
                    "hash": self.repo.head.commit.hexsha[:8],
                    "author": self.repo.head.commit.author.name,
                    "date": self.repo.head.commit.committed_datetime.isoformat(),
                    "message": self.repo.head.commit.message.strip()
                }
            }
        except Exception as e:
            print(f"Warning: Could not get repository info: {e}")
            return {"url": self.repo_url, "local_path": str(self.local_path)}
