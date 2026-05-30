from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables early
load_dotenv()

from database import init_db
from routers import agents, workflows, runs, messages, websocket
from telegram_app.bot import bot
import asyncio

# Ensure static directories exist before mounting
os.makedirs("static/generated_images", exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database on startup
    await init_db()
    
    # Start Telegram Bot in background with error handling
    bot_task = None
    try:
        print("🤖 Initializing background systems...")
        bot_task = asyncio.create_task(bot.run())
    except Exception as e:
        print(f"❌ Failed to start Telegram bot: {e}")

    yield
    
    # Clean up on shutdown
    if bot_task:
        print("🛑 Shutting down background systems...")
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass

app = FastAPI(
    title="AgentFlow Platform API",
    description="Backend for managing and orchestrating multi-agent workflows.",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(agents.router, prefix="/api")
app.include_router(workflows.router, prefix="/api")
app.include_router(runs.router, prefix="/api")
app.include_router(messages.router, prefix="/api")
app.include_router(websocket.router) # Websocket usually doesn't need /api prefix

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Welcome to AgentFlow Platform API", "status": "online"}
