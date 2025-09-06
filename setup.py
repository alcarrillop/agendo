#!/usr/bin/env python3
"""
Setup script for Agendo project.
Helps with initial project setup and dependency installation.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, cwd=None, shell=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            check=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def setup_backend():
    """Set up the Python backend."""
    print("🐍 Setting up Python backend...")
    
    backend_dir = Path(__file__).parent / "backend"
    
    # Check if Python 3.9+ is available
    success, output = run_command("python3 --version")
    if not success:
        print("❌ Python 3 not found. Please install Python 3.9 or later.")
        return False
    
    print(f"✅ Found Python: {output.strip()}")
    
    # Install backend dependencies
    print("📦 Installing Python dependencies...")
    success, output = run_command("pip3 install -r requirements.txt", cwd=backend_dir)
    if not success:
        print(f"❌ Failed to install Python dependencies: {output}")
        return False
    
    print("✅ Python dependencies installed successfully")
    
    # Copy environment file
    env_example = backend_dir / ".env.example"
    env_file = backend_dir / ".env"
    
    if env_example.exists() and not env_file.exists():
        print("📝 Creating .env file from example...")
        import shutil
        shutil.copy(env_example, env_file)
        print("✅ .env file created. Please edit it with your configuration.")
    
    return True


def setup_frontend():
    """Set up the Next.js frontend."""
    print("⚛️  Setting up Next.js frontend...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Check if Node.js is available
    success, output = run_command("node --version")
    if not success:
        print("❌ Node.js not found. Please install Node.js 18 or later.")
        return False
    
    print(f"✅ Found Node.js: {output.strip()}")
    
    # Check if npm is available
    success, output = run_command("npm --version")
    if not success:
        print("❌ npm not found. Please install npm.")
        return False
    
    print(f"✅ Found npm: {output.strip()}")
    
    # Install frontend dependencies
    print("📦 Installing Node.js dependencies...")
    success, output = run_command("npm install", cwd=frontend_dir)
    if not success:
        print(f"❌ Failed to install Node.js dependencies: {output}")
        return False
    
    print("✅ Node.js dependencies installed successfully")
    
    # Copy environment file
    env_example = frontend_dir / ".env.example"
    env_local = frontend_dir / ".env.local"
    
    if env_example.exists() and not env_local.exists():
        print("📝 Creating .env.local file from example...")
        import shutil
        shutil.copy(env_example, env_local)
        print("✅ .env.local file created. Please edit it with your configuration.")
    
    return True


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print("\n📋 Next steps:")
    print("\n1. Configure your environment variables:")
    print("   • Backend: Edit backend/.env")
    print("   • Frontend: Edit frontend/.env.local")
    print("\n2. Set up external services:")
    print("   • Create a Supabase project")
    print("   • Deploy Evolution API instance")
    print("   • Set up Google Calendar API")
    print("   • Get OpenAI API key")
    print("\n3. Start the development servers:")
    print("   • Backend: cd backend && python run_dev.py")
    print("   • Frontend: cd frontend && npm run dev")
    print("\n4. Open your browser:")
    print("   • Frontend: http://localhost:3000")
    print("   • Backend API: http://localhost:8000/docs")
    print("\n📖 For detailed setup instructions, see README.md")
    print("\n🆘 Need help? Check the documentation or logs for errors.")


def main():
    """Main setup function."""
    print("🚀 Welcome to Agendo Setup!")
    print("This script will help you set up the development environment.")
    print("-" * 60)
    
    # Setup backend
    if not setup_backend():
        print("❌ Backend setup failed. Please check the errors above.")
        sys.exit(1)
    
    print()
    
    # Setup frontend
    if not setup_frontend():
        print("❌ Frontend setup failed. Please check the errors above.")
        sys.exit(1)
    
    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main()

