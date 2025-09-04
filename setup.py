#!/usr/bin/env python3
"""
Setup script for AI Fitness Coach
This script sets up the entire project including backend and frontend
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=check, 
            capture_output=True, 
            text=True
        )
        print(f"✅ {command}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {command}")
        print(f"Error: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")

def check_node_version():
    """Check if Node.js is installed and compatible"""
    result = run_command("node --version", check=False)
    if not result:
        print("❌ Node.js is not installed. Please install Node.js 16+ first.")
        print("   Download from: https://nodejs.org/")
        sys.exit(1)
    
    version = result.strip().replace('v', '')
    major_version = int(version.split('.')[0])
    if major_version < 16:
        print(f"❌ Node.js {version} is too old. Please install Node.js 16+ first.")
        sys.exit(1)
    
    print(f"✅ Node.js {version}")

def setup_backend():
    """Setup Python backend"""
    print("\n🐍 Setting up Python backend...")
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt"):
        print("❌ Failed to install Python dependencies")
        sys.exit(1)
    
    # Create necessary directories
    directories = ['uploads', 'static/results', 'logs']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_frontend():
    """Setup React frontend"""
    print("\n⚛️  Setting up React frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        sys.exit(1)
    
    # Install Node.js dependencies
    if not run_command("npm install", cwd=frontend_dir):
        print("❌ Failed to install Node.js dependencies")
        sys.exit(1)
    
    # Build the React app
    if not run_command("npm run build", cwd=frontend_dir):
        print("❌ Failed to build React application")
        sys.exit(1)
    
    # Move built files to static directory
    import shutil
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    
    old_dist = static_dir / "dist"
    if old_dist.exists():
        shutil.rmtree(old_dist)
    
    frontend_dist = frontend_dir / "dist"
    if frontend_dist.exists():
        shutil.move(str(frontend_dist), str(old_dist))
        print("✅ Frontend built and moved to static/dist/")

def main():
    """Main setup function"""
    print("🚀 Setting up AI Fitness Coach...")
    print("=" * 50)
    
    # Check system requirements
    print("\n📋 Checking system requirements...")
    check_python_version()
    check_node_version()
    
    # Setup backend
    setup_backend()
    
    # Setup frontend
    setup_frontend()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📖 Next steps:")
    print("1. Run the application: python app.py")
    print("2. Open your browser: http://localhost:5000")
    print("3. Upload a workout video to test the analysis")
    print("\n💡 For development:")
    print("- Backend: python app.py")
    print("- Frontend: cd frontend && npm run dev")
    print("\n📚 Documentation: README.md")

if __name__ == "__main__":
    main()
