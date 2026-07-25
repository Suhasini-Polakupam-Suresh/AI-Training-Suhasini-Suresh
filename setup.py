"""
Automated Setup Script for Health Insurance AI Assistant
Runs all initialization steps
"""

import subprocess
import sys
from pathlib import Path
import time


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(text)
    print("="*60 + "\n")


def run_command(description, command):
    """Run a command and report status"""
    print(f"→ {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"  ✓ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ {description} failed")
        print(f"     Error: {e.stderr}")
        return False


def check_ollama():
    """Check if Ollama is installed and running"""
    print("→ Checking Ollama status...")
    try:
        subprocess.run(
            "ollama list",
            shell=True,
            check=True,
            capture_output=True
        )
        print("  ✓ Ollama is running")
        return True
    except subprocess.CalledProcessError:
        print("  ❌ Ollama is not running or not installed")
        print("     Please install Ollama from https://ollama.ai")
        print("     Then run: ollama serve")
        return False


def main():
    """Main setup function"""
    print_header("Health Insurance AI Assistant - Setup")
    
    print("This script will set up your capstone project environment.\n")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    if sys.version_info < (3, 10):
        print("⚠️  Warning: Python 3.10+ recommended")
    
    # Check Ollama
    print_header("Step 1: Check Ollama")
    if not check_ollama():
        print("\n⚠️  Setup cannot continue without Ollama")
        print("   Please install and start Ollama, then run this script again")
        return
    
    # List available models
    print("\n→ Checking installed models...")
    subprocess.run("ollama list", shell=True)
    
    # Install dependencies
    print_header("Step 2: Install Python Dependencies")
    success = run_command(
        "Installing dependencies from requirements.txt",
        f"{sys.executable} -m pip install -r requirements.txt"
    )
    
    if not success:
        print("\n❌ Failed to install dependencies")
        return
    
    # Process data
    print_header("Step 3: Process Health Insurance Documents")
    success = run_command(
        "Processing documents and creating chunks",
        f"{sys.executable} src/data_processing.py"
    )
    
    if not success:
        print("\n⚠️  Data processing failed, but continuing...")
    
    # Initialize vector store
    print_header("Step 4: Initialize Vector Store")
    success = run_command(
        "Creating embeddings and vector database",
        f"{sys.executable} src/vector_store.py"
    )
    
    if not success:
        print("\n⚠️  Vector store initialization failed, but continuing...")
    
    # Run tests
    print_header("Step 5: Run Tests (Optional)")
    response = input("Run unit tests? (y/n): ").strip().lower()
    if response == 'y':
        run_command(
            "Running unit tests",
            f"{sys.executable} -m pytest tests/ -v -m \"not slow\""
        )
    
    # Success summary
    print_header("Setup Complete! 🎉")
    
    print("Your Health Insurance AI Assistant is ready!")
    print("\nNext steps:\n")
    print("1. Make sure Ollama is running: ollama serve")
    print("2. Download models if not already done:")
    print("   ollama pull llama3")
    print("   ollama pull mistral")
    print("   ollama pull phi3")
    print("\n3. Run the web demo:")
    print("   streamlit run src/app.py")
    print("\n4. Or try the command line:")
    print("   python src/rag_pipeline.py")
    print("\n5. View documentation:")
    print("   - README.md - Project overview")
    print("   - QUICKSTART.md - Quick start guide")
    print("   - docs/CAPSTONE_REPORT.md - Full report")
    print("   - docs/DEMO_GUIDE.md - Demo instructions")
    
    print("\n" + "="*60)
    print("Happy coding! 🚀")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
