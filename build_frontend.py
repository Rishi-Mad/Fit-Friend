#!/usr/bin/env python3
"""
Build script for the React frontend
This script builds the React application and moves the built files to the Flask static directory
"""

import os
import subprocess
import shutil
import sys
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✅ {command}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {command}")
        print(f"Error: {e.stderr}")
        return None

def main():
    """Main build function"""
    print("🚀 Building AI Fitness Coach Frontend...")
    
    # Get the project root directory
    project_root = Path(__file__).parent
    frontend_dir = project_root / "frontend"
    static_dir = project_root / "static"
    
    # Check if frontend directory exists
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        sys.exit(1)
    
    # Check if Node.js is installed
    if not run_command("node --version"):
        print("❌ Node.js is not installed. Please install Node.js first.")
        sys.exit(1)
    
    # Check if npm is installed
    if not run_command("npm --version"):
        print("❌ npm is not installed. Please install npm first.")
        sys.exit(1)
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    if not run_command("npm install", cwd=frontend_dir):
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Build the React app
    print("\n🔨 Building React application...")
    if not run_command("npm run build", cwd=frontend_dir):
        print("❌ Failed to build React application")
        sys.exit(1)
    
    # Create static directory if it doesn't exist
    static_dir.mkdir(exist_ok=True)
    
    # Remove old dist directory if it exists
    old_dist = static_dir / "dist"
    if old_dist.exists():
        print("\n🗑️  Removing old build...")
        shutil.rmtree(old_dist)
    
    # Move the built files to static directory
    print("\n📁 Moving built files...")
    frontend_dist = frontend_dir / "dist"
    if frontend_dist.exists():
        shutil.move(str(frontend_dist), str(old_dist))
        print("✅ Build files moved to static/dist/")
    else:
        print("❌ Build directory not found!")
        sys.exit(1)
    
    print("\n🎉 Frontend build completed successfully!")
    print("📁 Built files are now in static/dist/")
    print("🌐 You can now run the Flask application with: python app.py")

if __name__ == "__main__":
    main()
