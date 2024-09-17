from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import uuid
import logging
import InvokeAgent as agenthelper

# Create FastAPI app
app = FastAPI()

# Mount the static directory to serve CSS, JS, and other static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Define a request model for input validation
class ChatRequest(BaseModel):
    prompt: str
    session_id: str = None

# Set up logging
logging.basicConfig(level=logging.INFO)

# Main chat endpoint
@app.post("/chat")
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    prompt = request.prompt

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    # Call askQuestion to get the LLM response and metadata
    captured_string, llm_response, metadata_list = agenthelper.askQuestion(prompt, session_id)

    if llm_response:
        response = {
            "session_id": session_id,
            "response": llm_response,
            "metadata": metadata_list  # Include metadata in the response
        }
        return JSONResponse(content=response)
    else:
        raise HTTPException(status_code=500, detail="Failed to process the request")


# Health check endpoint (optional)
@app.get("/health")
def health_check():
    return {"status": "ok"}
