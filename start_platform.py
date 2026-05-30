import subprocess
import time
import sys
import os

def start_platform():
    print("🚀 Starting AgentFlow Platform...")
    
    # Get base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, "agentflow-platform", "backend")
    frontend_dir = os.path.join(base_dir, "agentflow-platform", "frontend")

    # 1. Start Backend
    print("📡 Launching Backend server...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"],
        cwd=backend_dir
    )

    # 2. Start Frontend
    print("💻 Launching Frontend (Vite)...")
    # Detect if npm or yarn is used
    shell = True if os.name == 'nt' else False
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        shell=shell
    )

    print("\n✅ Platform is coming online!")
    print("🔗 Frontend: http://localhost:5173")
    print("🔗 API: http://127.0.0.1:8000")
    print("📱 Telegram Bot: Active in background\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down AgentFlow...")
        backend_process.terminate()
        frontend_process.terminate()
        print("👋 Goodbye!")

if __name__ == "__main__":
    start_platform()
