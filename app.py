"""
SRM Timetable Management System - Main Application Entry Point
A complete, industry-ready timetable management system for SRM College Ramapuram
"""

import os
import sys
import threading
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.main import start_fastapi_server
from frontend.app import create_flask_app
from backend.database.init_db import initialize_database

def main():
    """Main application entry point"""
    print("🎓 Starting SRM Timetable Management System...")
    print("=" * 60)
    
    # Initialize database
    print("📊 Initializing database...")
    initialize_database()
    print("✅ Database initialized successfully!")
    
    # Start FastAPI backend in a separate thread
    print("🚀 Starting FastAPI backend server...")
    backend_thread = threading.Thread(target=start_fastapi_server, daemon=True)
    backend_thread.start()
    
    # Give backend time to start
    time.sleep(2)
    print("✅ FastAPI backend started on http://127.0.0.1:8000")
    
    # Start Flask frontend
    print("🌐 Starting Flask frontend server...")
    flask_app = create_flask_app()
    
    print("=" * 60)
    print("🎉 SRM Timetable Management System is ready!")
    print("📱 Frontend: http://127.0.0.1:5000")
    print("🔧 Backend API: http://127.0.0.1:8000")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print("=" * 60)
    print("\n🔑 Default Login Credentials:")
    print("Main Admin: admin@srmist.edu.in / admin123")
    print("=" * 60)
    
    # Run Flask app
    flask_app.run(
        host=os.getenv('FLASK_HOST', '127.0.0.1'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )

if __name__ == "__main__":
    main()