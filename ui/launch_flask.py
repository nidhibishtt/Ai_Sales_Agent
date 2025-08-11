#!/usr/bin/env python3
"""
Launch script for Flask-based AI Sales Agent UI
"""

import sys
import os

# Add project root to path
sys.path.append('/Users/vidhusinha/Desktop/Project')

from ui.flask_app import app, socketio

if __name__ == '__main__':
    print("🚀 Starting Flask AI Sales Agent UI...")
    print("📊 Features: Real-time chat, WebSocket support, Modern UI")
    print("🌐 Access at: http://localhost:5000")
    print("🔗 Network access: http://0.0.0.0:5000")
    print("-" * 50)
    
    try:
        socketio.run(
            app, 
            debug=True, 
            host='0.0.0.0', 
            port=5000,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
