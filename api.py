from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import InvokeAgent as agenthelper
import uuid
import logging
import os

app = FastAPI()

# Define a request model for input validation
class ChatRequest(BaseModel):
    prompt: str
    session_id: str = None

# Set up logging
logging.basicConfig(level=logging.INFO)
@app.get("/debug-env")
async def debug_env():
    try:
        region = os.getenv("AWS_REGION")
        agent_id = os.getenv("AGENT_ID")

        # Log the retrieved values
        logging.info(f"Retrieved AWS_REGION: {region}")
        logging.info(f"Retrieved AGENT_ID: {agent_id}")

        if not region or not agent_id:
            raise HTTPException(status_code=500, detail="Environment variables not loaded properly")

        return {"AWS_REGION": region, "AGENT_ID": agent_id}
    except Exception as e:
        logging.error(f"Error in /debug-env: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving environment variables")

@app.post("/chat")
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    prompt = request.prompt

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    captured_string, llm_response, metadata_list = agenthelper.askQuestion(prompt, session_id)

    if llm_response:
        response = {
            "session_id": session_id,
            "response": llm_response,
            "metadata": metadata_list
        }
        return response
    else:
        raise HTTPException(status_code=500, detail="Failed to process the request")

# Health check endpoint (optional)
@app.get("/health")
def health_check():
    return {"status": "ok"}
