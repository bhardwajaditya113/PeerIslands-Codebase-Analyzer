"""
Test script to verify GitHub Models API connection.
Run this before running the full analysis to ensure everything is configured correctly.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 80)
print("GitHub Models Connection Test")
print("=" * 80)
print()

# Check for GitHub token
github_token = os.getenv("GITHUB_TOKEN")
if not github_token or github_token == "your_github_personal_access_token_here":
    print("❌ ERROR: GitHub token not configured!")
    print()
    print("Please follow these steps:")
    print("1. Go to: https://github.com/settings/tokens")
    print("2. Click 'Generate new token (classic)'")
    print("3. Select scopes: repo, read:user")
    print("4. Copy the token (ghp_...)")
    print("5. Update GITHUB_TOKEN in .env file")
    print()
    print("See GITHUB_MODELS_SETUP.md for detailed instructions.")
    sys.exit(1)

print(f"✓ GitHub token found: {github_token[:10]}...{github_token[-4:]}")
print()

# Test configuration loading
try:
    from src.config import config
    print(f"✓ Configuration loaded successfully")
    print(f"  Provider: {config.llm_provider}")
    print(f"  Model: {config.github_model}")
    print()
except Exception as e:
    print(f"❌ Configuration error: {e}")
    sys.exit(1)

# Test GitHub Models API connection
print("Testing GitHub Models connection...")
print()

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage
    
    # Initialize GitHub Models client
    os.environ["OPENAI_API_KEY"] = github_token
    llm = ChatOpenAI(
        model=config.github_model,
        temperature=0.1,
        base_url="https://models.inference.ai.azure.com"
    )
    
    # Test with a simple prompt
    messages = [
        SystemMessage(content="You are a helpful assistant. Respond with exactly: 'GitHub Models is working!'"),
        HumanMessage(content="Test connection")
    ]
    
    print("Sending test request...")
    response = llm.invoke(messages)
    
    print()
    print("=" * 80)
    print("✓ SUCCESS! GitHub Models is working!")
    print("=" * 80)
    print()
    print(f"Response: {response.content}")
    print()
    print("You can now run the full analysis with:")
    print("  python main.py --skip-clone")
    print()
    
except Exception as e:
    print()
    print("=" * 80)
    print("❌ Connection failed!")
    print("=" * 80)
    print()
    print(f"Error: {e}")
    print()
    print("Troubleshooting:")
    print("1. Verify your GitHub token is valid")
    print("2. Check you have GitHub Copilot access")
    print("3. Ensure token has 'repo' and 'read:user' scopes")
    print("4. Try regenerating the token")
    print()
    print("See GITHUB_MODELS_SETUP.md for detailed help.")
    sys.exit(1)
