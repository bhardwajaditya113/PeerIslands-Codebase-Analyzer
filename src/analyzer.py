"""
Code analyzer module for extracting knowledge from codebase.
Combines code complexity analysis with LLM-based insights.
"""
import re
from typing import Dict, List, Any
from pathlib import Path
from radon.complexity import cc_visit
from radon.metrics import h_visit, mi_visit
from src.repository_manager import CodeFile
from src.llm_provider import LLMProvider
from src.chunker import CodeChunker
from tqdm import tqdm


class CodeAnalyzer:
    """Analyzes codebase and extracts structured knowledge."""
    
    def __init__(self):
        self.llm_provider = LLMProvider()
        self.chunker = CodeChunker()
    
    def analyze_complexity(self, code_files: List[CodeFile]) -> Dict[str, Any]:
        """
        Analyze code complexity using Radon for applicable files.
        
        Args:
            code_files: List of code files to analyze
            
        Returns:
            Dictionary with complexity metrics
        """
        complexity_results = {
            "files": [],
            "summary": {
                "total_files": len(code_files),
                "analyzed_files": 0,
                "high_complexity_files": [],
                "average_complexity": 0
            }
        }
        
        total_complexity = 0
        analyzed_count = 0
        
        for file in code_files:
            # Only analyze supported languages (Python, Java-like syntax)
            if file.extension not in ['.py', '.java']:
                continue
            
            try:
                # Calculate cyclomatic complexity
                cc_results = cc_visit(file.content)
                
                file_complexity = {
                    "path": file.relative_path,
                    "functions": []
                }
                
                max_complexity = 0
                for item in cc_results:
                    complexity_score = item.complexity
                    max_complexity = max(max_complexity, complexity_score)
                    
                    file_complexity["functions"].append({
                        "name": item.name,
                        "complexity": complexity_score,
                        "type": item.letter,
                        "line": item.lineno,
                        "complexity_level": self._classify_complexity(complexity_score)
                    })
                
                file_complexity["max_complexity"] = max_complexity
                file_complexity["complexity_level"] = self._classify_complexity(max_complexity)
                
                complexity_results["files"].append(file_complexity)
                
                if max_complexity > 10:
                    complexity_results["summary"]["high_complexity_files"].append({
                        "path": file.relative_path,
                        "max_complexity": max_complexity
                    })
                
                total_complexity += max_complexity
                analyzed_count += 1
                
            except Exception as e:
                # Skip files that can't be analyzed
                pass
        
        complexity_results["summary"]["analyzed_files"] = analyzed_count
        if analyzed_count > 0:
            complexity_results["summary"]["average_complexity"] = round(
                total_complexity / analyzed_count, 2
            )
        
        return complexity_results
    
    def _classify_complexity(self, score: int) -> str:
        """Classify complexity score into categories."""
        if score <= 5:
            return "low"
        elif score <= 10:
            return "medium"
        else:
            return "high"
    
    def extract_method_signatures(self, code_files: List[CodeFile]) -> Dict[str, List[Dict]]:
        """
        Extract method signatures using regex patterns.
        
        Args:
            code_files: List of code files
            
        Returns:
            Dictionary mapping file paths to method signatures
        """
        methods_by_file = {}
        
        # Regex patterns for different languages
        java_method_pattern = r'(public|private|protected|static|\s)+[\w\<\>\[\]]+\s+(\w+)\s*\([^\)]*\)\s*\{'
        python_method_pattern = r'def\s+(\w+)\s*\([^\)]*\):'
        
        for file in code_files:
            methods = []
            
            if file.extension == '.java':
                matches = re.finditer(java_method_pattern, file.content)
                for match in matches:
                    methods.append({
                        "signature": match.group(0).strip().rstrip('{'),
                        "name": match.group(2),
                        "type": "java_method"
                    })
            elif file.extension == '.py':
                matches = re.finditer(python_method_pattern, file.content)
                for match in matches:
                    methods.append({
                        "signature": match.group(0).strip(),
                        "name": match.group(1),
                        "type": "python_function"
                    })
            
            if methods:
                methods_by_file[file.relative_path] = methods
        
        return methods_by_file
    
    def analyze_with_llm(self, code_files: List[CodeFile], repo_info: Dict) -> Dict[str, Any]:
        """
        Analyze codebase using LLM for deep insights.
        
        Args:
            code_files: List of code files
            repo_info: Repository information
            
        Returns:
            Complete analysis results
        """
        print("\n=== Starting LLM Analysis ===")
        
        # Step 1: Generate project overview
        print("\nGenerating project overview...")
        overview_text = self.chunker.create_project_overview_chunk(code_files)
        project_overview = self.llm_provider.generate_project_overview(overview_text, repo_info)
        
        # Step 2: Create chunks
        chunks = self.chunker.create_chunks(code_files)
        
        # Step 3: Analyze each chunk
        print(f"\nAnalyzing {len(chunks)} chunks with LLM...")
        chunk_analyses = []
        
        for i, chunk in enumerate(tqdm(chunks, desc="Analyzing chunks")):
            chunk_text = chunk.to_text()
            analysis = self.llm_provider.analyze_code_chunk(chunk_text, i, len(chunks))
            chunk_analyses.append(analysis)
        
        # Step 4: Combine with complexity analysis
        print("\nCalculating code complexity metrics...")
        complexity_results = self.analyze_complexity(code_files)
        
        # Step 5: Extract method signatures
        print("Extracting method signatures...")
        method_signatures = self.extract_method_signatures(code_files)
        
        # Compile complete results
        results = {
            "project_overview": project_overview,
            "chunk_analyses": chunk_analyses,
            "complexity_analysis": complexity_results,
            "method_signatures": method_signatures,
            "statistics": {
                "total_files": len(code_files),
                "total_chunks": len(chunks),
                "total_lines": sum(len(f.content.split('\n')) for f in code_files),
                "total_size_bytes": sum(f.size for f in code_files),
                "files_by_extension": self._count_files_by_extension(code_files)
            }
        }
        
        return results
    
    def _count_files_by_extension(self, code_files: List[CodeFile]) -> Dict[str, int]:
        """Count files by extension."""
        counts = {}
        for file in code_files:
            ext = file.extension or "no_extension"
            counts[ext] = counts.get(ext, 0) + 1
        return counts
