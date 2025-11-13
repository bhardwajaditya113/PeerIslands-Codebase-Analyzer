"""
Main entry point for the codebase analyzer.
Orchestrates the entire analysis pipeline.
"""
import sys
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.config import config
from src.repository_manager import RepositoryManager
from src.analyzer import CodeAnalyzer
from src.output_formatter import OutputFormatter


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Analyze a codebase using LLM and extract structured knowledge"
    )
    parser.add_argument(
        "--skip-clone",
        action="store_true",
        help="Skip cloning/updating the repository (use existing local copy)"
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default=None,
        help="Custom output filename (default: analysis_results_TIMESTAMP.json)"
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("CODEBASE ANALYSIS TOOL")
    print("=" * 80)
    print(f"\nConfiguration:")
    print(f"  LLM Provider: {config.llm_provider}")
    print(f"  Repository: {config.repo_url}")
    print(f"  Max Tokens per Chunk: {config.max_tokens_per_chunk}")
    print(f"  Output Directory: {config.output_dir}")
    print("=" * 80)
    
    try:
        # Step 1: Clone/Update Repository
        if not args.skip_clone:
            print("\n[Step 1/5] Cloning/Updating Repository")
            print("-" * 80)
            repo_manager = RepositoryManager()
            repo_manager.clone_repository()
            repo_info = repo_manager.get_repository_info()
        else:
            print("\n[Step 1/5] Using Existing Repository")
            print("-" * 80)
            repo_manager = RepositoryManager()
            repo_info = repo_manager.get_repository_info()
        
        # Step 2: Read Codebase
        print("\n[Step 2/5] Reading Codebase")
        print("-" * 80)
        code_files = repo_manager.read_codebase()
        
        if not code_files:
            print("Error: No code files found to analyze!")
            return 1
        
        print(f"\nTotal files to analyze: {len(code_files)}")
        total_size = sum(f.size for f in code_files)
        print(f"Total size: {total_size:,} bytes ({total_size / 1024 / 1024:.2f} MB)")
        
        # Step 3: Analyze with LLM
        print("\n[Step 3/5] Analyzing Code with LLM")
        print("-" * 80)
        analyzer = CodeAnalyzer()
        analysis_results = analyzer.analyze_with_llm(code_files, repo_info)
        
        # Step 4: Format Results
        print("\n[Step 4/5] Formatting Results")
        print("-" * 80)
        formatter = OutputFormatter()
        formatted_results = formatter.format_results(analysis_results)
        
        # Step 5: Save Results
        print("\n[Step 5/5] Saving Results")
        print("-" * 80)
        json_path = formatter.save_results(formatted_results, args.output_file)
        summary_path = formatter.save_summary(formatted_results)
        
        # Final Summary
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE!")
        print("=" * 80)
        print(f"\nResults:")
        print(f"  JSON Output: {json_path}")
        print(f"  Text Summary: {summary_path}")
        print(f"\nProject: {formatted_results['project_overview']['name']}")
        print(f"Files Analyzed: {formatted_results['statistics']['total_files']}")
        print(f"Classes Identified: {formatted_results['detailed_analysis']['total_classes_identified']}")
        print(f"Complexity Level: {formatted_results['project_overview']['estimated_complexity']}")
        print("\n" + "=" * 80)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n\nError during analysis: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
