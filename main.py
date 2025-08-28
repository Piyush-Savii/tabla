# main.py

import os
import io
import cProfile
import pstats
import json

from fastapi import FastAPI, Request, APIRouter, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Assuming these modules are part of your project structure
from logger_setup import logger
from core.platform import PlatformBase
from core.llm_client import LLMClient, test_llm_connections
from pkg_setup import install_missing_or_mismatched


# --- Setup and Configuration ---

def create_app() -> FastAPI:
    """
    Creates and configures the FastAPI app.
    - Loads environment variables.
    - Installs missing packages (for local/dev use).
    - Tests AI model connection.
    - Registers chatbot platform (Slack, etc.).
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
        CORSMiddleware, # type: ignore
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Register the Slack Router ---
    # This is a key change. We now create a dedicated router for Slack events.
    # This allows us to handle the URL verification challenge separately from other API endpoints.
    
    slack_router = APIRouter()
    
    # Connect the chatbot platform (Slack, etc.) to the new router
    # This assumes PlatformBase contains the logic to handle Slack events
    platform = PlatformBase(LLMClient(ai_provider))
    slack_router.include_router(platform.router)

    # Add the URL verification endpoint
    @slack_router.post("/")
    async def slack_verification_and_events(req: Request):
        """
        Handles the initial Slack URL verification and all subsequent events.
        """
        body = await req.json()
        
        # Check for the challenge parameter and respond if it's a verification request
        if "challenge" in body:
            return Response(content=body["challenge"], media_type="text/plain")
        
        # For all other events, pass the request to the PlatformBase handler
        return await req.app.router.get_route(f"{slack_router.prefix}/").body(req)

    # Include the Slack router at the /slack/events path
    # NOTE: You MUST update your Slack app's Request URL to point to this path.
    fastapi_app.include_router(slack_router, prefix="/slack/events")

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


# --- Main API Endpoints ---

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
            "slack_events": {
                "path": "/slack/events",
                "method": "POST",
                "description": "Main endpoint for Slack events and URL verification"
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
