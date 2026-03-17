#!/usr/bin/env python3
"""
Verify Jarvis project structure and dependencies
Run this after cloning to make sure everything is set up correctly
"""

import os
import sys
from pathlib import Path

def check_structure():
    """Check if required folders exist"""
    base_path = Path(__file__).parent
    
    required_dirs = [
        'src/core',
        'src/templates', 
        'src/data',
        'src/api',
        'config/templates',
        'tests',
        'docs',
        'frontend/src',
        'input',
        'output'
    ]
    
    required_files = [
        'src/__init__.py',
        'src/core/__init__.py',
        'src/core/calculator.py',
        'src/templates/__init__.py',
        'src/templates/engine.py',
        'config/templates/damodaran_jet.json',
        'config/.env.example',
        'main.py',
        'api.py',
        'requirements.txt',
        'docs/ROADMAP_v2.md'
    ]
    
    print("🔍 Checking Jarvis project structure...\n")
    
    # Check directories
    print("📁 Required Directories:")
    all_dirs_ok = True
    for dir_path in required_dirs:
        full_path = base_path / dir_path
        exists = full_path.exists() and full_path.is_dir()
        status = "✅" if exists else "❌"
        print(f"  {status} {dir_path}")
        all_dirs_ok = all_dirs_ok and exists
    
    print("\n📄 Required Files:")
    all_files_ok = True
    for file_path in required_files:
        full_path = base_path / file_path
        exists = full_path.exists() and full_path.is_file()
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}")
        all_files_ok = all_files_ok and exists
    
    print("\n" + "="*60)
    if all_dirs_ok and all_files_ok:
        print("✅ Project structure is VALID!")
        return True
    else:
        print("❌ Project structure has issues. See above.")
        return False

def check_dependencies():
    """Check if Python dependencies are installed"""
    print("\n📦 Checking Python Dependencies:")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'pandas',
        'numpy',
        'requests',
        'python-dotenv'
    ]
    
    all_ok = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            all_ok = False
    
    if not all_ok:
        print("\n💡 Install dependencies:")
        print("   pip install -r requirements.txt")
    
    return all_ok

def check_config():
    """Check if .env is configured"""
    print("\n⚙️  Configuration Check:")
    
    base_path = Path(__file__).parent
    env_path = base_path / '.env'
    
    if env_path.exists():
        print("  ✅ .env file exists")
        with open(env_path, 'r') as f:
            content = f.read()
            if 'FINNHUB_API_KEY' in content:
                print("  ✅ FINNHUB_API_KEY configured")
            else:
                print("  ⚠️  FINNHUB_API_KEY not found in .env")
    else:
        print("  ⚠️  .env file not found")
        print("     Copy: cp config/.env.example .env")
        print("     Then edit .env and add your API keys")

def main():
    print("🚀 Jarvis Project Verification\n")
    print("="*60)
    
    structure_ok = check_structure()
    deps_ok = check_dependencies()
    check_config()
    
    print("\n" + "="*60)
    if structure_ok and deps_ok:
        print("\n✅ All systems GO! Ready to develop.\n")
        print("Next steps:")
        print("  1. python main.py              # Start backend")
        print("  2. cd frontend && npm run dev  # Start frontend")
        print("  3. See docs/ROADMAP_v2.md for development guide")
        return 0
    else:
        print("\n❌ Please fix the issues above before continuing.\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
