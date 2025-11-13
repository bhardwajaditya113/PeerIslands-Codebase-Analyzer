"""
Output formatter module for generating structured JSON output.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from src.config import config


class OutputFormatter:
    """Formats and saves analysis results in structured JSON format."""
    
    def __init__(self):
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def format_results(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format analysis results into a well-structured JSON document.
        
        Args:
            analysis_results: Raw analysis results from CodeAnalyzer
            
        Returns:
            Formatted results dictionary
        """
        formatted = {
            "metadata": {
                "analysis_date": datetime.now().isoformat(),
                "analyzer_version": "1.0.0",
                "llm_provider": config.llm_provider,
                "repository": analysis_results["project_overview"].get("repository_info", {})
            },
            "project_overview": {
                "name": analysis_results["project_overview"].get("project_name", "Unknown"),
                "purpose": analysis_results["project_overview"].get("purpose", ""),
                "domain": analysis_results["project_overview"].get("domain", ""),
                "architecture": analysis_results["project_overview"].get("architecture_style", ""),
                "key_technologies": analysis_results["project_overview"].get("key_technologies", []),
                "main_components": analysis_results["project_overview"].get("main_components", []),
                "estimated_complexity": analysis_results["project_overview"].get("estimated_complexity", ""),
                "notable_features": analysis_results["project_overview"].get("notable_features", [])
            },
            "statistics": analysis_results.get("statistics", {}),
            "code_structure": self._format_code_structure(analysis_results),
            "complexity_analysis": self._format_complexity_analysis(
                analysis_results.get("complexity_analysis", {})
            ),
            "detailed_analysis": self._format_detailed_analysis(
                analysis_results.get("chunk_analyses", [])
            )
        }
        
        return formatted
    
    def _format_code_structure(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Format code structure information."""
        method_sigs = analysis_results.get("method_signatures", {})
        
        # Organize by file
        files_info = []
        for file_path, methods in method_sigs.items():
            files_info.append({
                "path": file_path,
                "method_count": len(methods),
                "methods": [
                    {
                        "name": m["name"],
                        "signature": m["signature"],
                        "type": m["type"]
                    }
                    for m in methods[:20]  # Limit to first 20 methods per file
                ]
            })
        
        return {
            "total_files_with_methods": len(files_info),
            "files": files_info
        }
    
    def _format_complexity_analysis(self, complexity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format complexity analysis results."""
        if not complexity_data:
            return {
                "summary": "No complexity analysis available",
                "high_complexity_files": []
            }
        
        summary = complexity_data.get("summary", {})
        
        return {
            "summary": {
                "total_files_analyzed": summary.get("analyzed_files", 0),
                "average_complexity": summary.get("average_complexity", 0),
                "high_complexity_count": len(summary.get("high_complexity_files", []))
            },
            "high_complexity_files": summary.get("high_complexity_files", []),
            "detailed_metrics": [
                {
                    "file": f["path"],
                    "max_complexity": f["max_complexity"],
                    "complexity_level": f["complexity_level"],
                    "complex_functions": [
                        {
                            "name": func["name"],
                            "complexity": func["complexity"],
                            "line": func["line"]
                        }
                        for func in f["functions"]
                        if func["complexity"] > 5
                    ][:10]  # Top 10 complex functions per file
                }
                for f in complexity_data.get("files", [])
                if f.get("max_complexity", 0) > 5
            ][:20]  # Top 20 complex files
        }
    
    def _format_detailed_analysis(self, chunk_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format detailed LLM analysis results."""
        all_classes = []
        all_key_functions = []
        
        for chunk in chunk_analyses:
            if "files" in chunk:
                for file_analysis in chunk["files"]:
                    file_path = file_analysis.get("path", "unknown")
                    
                    # Extract classes
                    for cls in file_analysis.get("classes", []):
                        class_info = {
                            "name": cls.get("name", ""),
                            "file": file_path,
                            "purpose": cls.get("purpose", ""),
                            "method_count": len(cls.get("methods", [])),
                            "key_methods": [
                                {
                                    "name": m.get("name", ""),
                                    "signature": m.get("signature", ""),
                                    "description": m.get("description", ""),
                                    "complexity": m.get("complexity", "unknown")
                                }
                                for m in cls.get("methods", [])[:5]  # Top 5 methods per class
                            ],
                            "relationships": cls.get("relationships", [])
                        }
                        all_classes.append(class_info)
                    
                    # Extract key functions
                    for func in file_analysis.get("key_functions", []):
                        all_key_functions.append({
                            "name": func.get("name", ""),
                            "file": file_path,
                            "description": func.get("description", "")
                        })
        
        return {
            "total_classes_identified": len(all_classes),
            "total_key_functions_identified": len(all_key_functions),
            "classes": all_classes,
            "key_functions": all_key_functions[:50]  # Limit to 50 key functions
        }
    
    def save_results(self, formatted_results: Dict[str, Any], filename: str = None) -> str:
        """
        Save formatted results to JSON file.
        
        Args:
            formatted_results: Formatted analysis results
            filename: Optional filename (default: analysis_results_TIMESTAMP.json)
            
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_results_{timestamp}.json"
        
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(formatted_results, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to: {output_path}")
        return str(output_path)
    
    def save_summary(self, formatted_results: Dict[str, Any]) -> str:
        """
        Save a human-readable summary of the analysis.
        
        Args:
            formatted_results: Formatted analysis results
            
        Returns:
            Path to saved summary file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_summary_{timestamp}.txt"
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("CODEBASE ANALYSIS SUMMARY\n")
            f.write("=" * 80 + "\n\n")
            
            # Project Overview
            overview = formatted_results.get("project_overview", {})
            f.write(f"Project: {overview.get('name', 'Unknown')}\n")
            f.write(f"Purpose: {overview.get('purpose', 'N/A')}\n")
            f.write(f"Domain: {overview.get('domain', 'N/A')}\n")
            f.write(f"Architecture: {overview.get('architecture', 'N/A')}\n")
            f.write(f"Complexity: {overview.get('estimated_complexity', 'N/A')}\n\n")
            
            # Statistics
            stats = formatted_results.get("statistics", {})
            f.write("Statistics:\n")
            f.write(f"  Total Files: {stats.get('total_files', 0)}\n")
            f.write(f"  Total Lines: {stats.get('total_lines', 0)}\n")
            f.write(f"  Total Size: {stats.get('total_size_bytes', 0):,} bytes\n\n")
            
            # Complexity
            complexity = formatted_results.get("complexity_analysis", {})
            comp_summary = complexity.get("summary", {})
            f.write("Complexity Analysis:\n")
            f.write(f"  Files Analyzed: {comp_summary.get('total_files_analyzed', 0)}\n")
            f.write(f"  Average Complexity: {comp_summary.get('average_complexity', 0)}\n")
            f.write(f"  High Complexity Files: {comp_summary.get('high_complexity_count', 0)}\n\n")
            
            # Detailed Analysis
            detailed = formatted_results.get("detailed_analysis", {})
            f.write("Detailed Analysis:\n")
            f.write(f"  Classes Identified: {detailed.get('total_classes_identified', 0)}\n")
            f.write(f"  Key Functions: {detailed.get('total_key_functions_identified', 0)}\n\n")
            
            f.write("=" * 80 + "\n")
            f.write(f"Analysis completed: {formatted_results['metadata']['analysis_date']}\n")
            f.write("=" * 80 + "\n")
        
        print(f"Summary saved to: {output_path}")
        return str(output_path)
