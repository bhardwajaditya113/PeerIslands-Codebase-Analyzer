# ?? Codebase Analysis Tool using LLM

A sophisticated Python-based tool for analyzing codebases using Large Language Models (LLMs). This tool extracts structured knowledge from code repositories, including project overviews, method signatures, complexity metrics, and architectural insights.

## ?? Overview

This project was developed as part of the **PeerIslands coding assignment**. It analyzes GitHub repositories (demonstrated on [SakilaProject](https://github.com/janjakovacevic/SakilaProject)) using LLM-powered analysis combined with traditional code metrics to provide comprehensive insights into codebase structure and complexity.

## ? Features

- **?? FREE GitHub Models Support**: Uses GitHub Models API (free for GitHub Copilot users!)
- **?? Multi-Provider LLM Support**: Works with GitHub Models, OpenAI GPT-4, and Anthropic Claude
- **?? Automated Repository Cloning**: Automatically clones and updates target repositories
- **?? Smart Code Chunking**: Intelligently splits code into chunks that respect token limits
- **?? Comprehensive Analysis**:
  - Project overview and purpose identification
  - Method signature extraction with descriptions
  - Cyclomatic complexity analysis using Radon
  - Class and function documentation
  - Architecture pattern detection
  - Dependency relationship mapping
- **?? Structured JSON Output**: Well-organized, machine-readable results
- **?? Human-Readable Summary**: Text-based summary for quick review

## ?? Quick Start

See **[QUICK_START_GITHUB.md](QUICK_START_GITHUB.md)** for detailed setup instructions.

### Prerequisites
- Python 3.8+
- GitHub Personal Access Token (free with GitHub Copilot!)

### Installation
```bash
git clone <your-repo-url>
cd PeerIslands
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
cp .env.example .env
# Add your GitHub token to .env
python test_github_models.py  # Test connection
python main.py                # Run analysis
```

## ?? Demo Results

**Analysis of SakilaProject:**
- ? 46 files analyzed
- ? 42 classes identified  
- ? 2,916 lines of code
- ? Complete method signatures extracted
- ? Complexity metrics calculated
- ? Architecture: MVC with Spring Framework

## ?? Documentation

- **[QUICK_START_GITHUB.md](QUICK_START_GITHUB.md)** - 3-minute setup guide
- **[GITHUB_MODELS_SETUP.md](GITHUB_MODELS_SETUP.md)** - Detailed GitHub Models setup
- **[TECHNICAL_DESIGN.md](TECHNICAL_DESIGN.md)** - Technical architecture
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues

## ??? Architecture

```
PeerIslands/
+-- main.py                    # Main entry point
+-- src/
¦   +-- config.py              # Configuration management
¦   +-- repository_manager.py  # Git operations
¦   +-- chunker.py             # Smart code chunking
¦   +-- llm_provider.py        # LLM integration
¦   +-- analyzer.py            # Analysis coordination
¦   +-- output_formatter.py    # Output generation
+-- output/                    # Analysis results
+-- requirements.txt           # Dependencies
```

## ?? Author

Created for **PeerIslands Coding Assignment** - November 2025

---

For help: See documentation or run `python test_github_models.py`
