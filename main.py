# main.py

import os
import io
import cProfile
import pstats

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Enables browser/frontend access
from dotenv import load_dotenv

from logger_setup import logger
from core.platform import PlatformBase
from core.llm_client import LLMClient, test_llm_connections
from pkg_setup import install_missing_or_mismatched


def create_app() -> FastAPI:
    """
    Creates and configures the FastAPI app.
    - Loads environment variables
    - Installs missing packages (for local/dev use)
    - Tests AI model connection
    - Registers chatbot platform (Slack, etc.)
    Returns the configured FastAPI app instance.
    """
    func = 'create_app'
    load_dotenv()
    env = os.getenv("ENV", "local")
    logger.info(f" in {func} ENV {env} loaded\n")

    # Install Python dependencies if not in production
    if env != "production":
        install_missing_or_mismatched()

    # Check if AI model (e.g., OpenAI, Gemini) is reachable
    ai_provider = os.getenv("AI_PROVIDER")
    if ai_provider != test_llm_connections(ai_provider):
        logger.error(f" in {func} AI_PROVIDER '{ai_provider}' is not available or failed connection test\n")

    # Create the FastAPI server object
    fastapi_app = FastAPI(
        title="Virtual Assistant API\n",
        description="API for the virtual assistant that processes user queries and handles function calls\n",
        version="1.0.0"
    )

    # Allow browser-based clients to access the API
    fastapi_app.add_middleware(
        CORSMiddleware, # type: ignore  # Enables frontend-to-backend calls
        allow_origins=["*"],  # Accept requests from any frontend (can restrict later)
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Connect the chatbot platform (Slack, etc.) to the API
    platform = PlatformBase(LLMClient(ai_provider))
    fastapi_app.include_router(platform.router)

    return fastapi_app


def profile_app_setup():
    """
    Measures performance of app setup — useful for developers.
    Logs the slowest operations using Python's cProfile.
    """
    func = 'profile_app_setup'
    profiler = cProfile.Profile()
    profiler.enable()

    fastapi_app = create_app()  # Profile the full app creation

    profiler.disable()
    s = io.StringIO()
    stats = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
    stats.print_stats(20)  # Show top 20 slowest function calls

    logger.info(f" in {func} 🔍 Performance Profile:\n{s.getvalue()}\n")
    return fastapi_app


# Load environment variables once
load_dotenv()
enable_profiler = os.getenv("ENABLE_PROFILER", "false").lower() == "true"

# Create app instance (profiled if enabled)
app = profile_app_setup() if enable_profiler else create_app()


@app.get("/")
async def get_api_information():
    """
    Root URL — explains what this API does and its available endpoints.
    Good for developers or testers who open the base URL.
    """
    return {
        "message": "Virtual Assistant API\n",
        "version": "1.0.0\n",
        "description": "API for processing chat conversations with data and AI capabilities\n",
        "endpoints": {
            "chat": {
                "path": "/chat",
                "method": "POST",
                "description": "Main chat endpoint - sends messages to the AI assistant\n"
            },
            "quick_query": {
                "path": "/quick-query",
                "method": "POST",
                "description": "Simple one-shot query endpoint without chat history\n"
            },
            "health": {
                "path": "/health",
                "method": "GET",
                "description": "Basic check to ensure the API is running\n"
            }
        },
        "conversation_flow": [
            "1. Add a system prompt if not present\n",
            "2. Send conversation to AI model\n",
            "3. Handle tool/function calls (if any)\n",
            "4. Return the AI's response\n"
        ]
    }


@app.get("/health")
async def health_check():
    """
    Returns a simple status message showing that the API is working.
    Useful for uptime monitoring or debugging.
    """
    return {"status": "ok", "message": "Virtual Assistant API is healthy.\n"}


# If run directly (not via uvicorn)
if __name__ == "__main__":
    import uvicorn
    logger.info(f" in __main__ PROFILER enabled: {enable_profiler}\n")
    logger.info("Starting Virtual Assistant API server")
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)
