#!/usr/bin/env python3
"""
UI Launcher for Enhanced AI Sales Agent
Simple script to launch the web interface
"""

import sys
import os
import subprocess

def main():
    """Launch the Streamlit UI"""
    print("🚀 Launching Enhanced AI Sales Agent UI...")
    print("=" * 50)
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    ui_file = os.path.join(project_root, "ui", "streamlit_app.py")
    
    # Check if the UI file exists
    if not os.path.exists(ui_file):
        print("❌ UI file not found!")
        return
    
    print("📍 Project Root:", project_root)
    print("🎨 UI File:", ui_file)
    print("🌐 Starting web server...")
    print("⚡ This will open in your browser at http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", ui_file,
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.serverAddress", "localhost"
        ], cwd=project_root)
    
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error launching UI: {e}")

if __name__ == "__main__":
    main()
