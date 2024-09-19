from fastapi import FastAPI, HTTPException, Request
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

# Set up logging to file
logging.basicConfig(
    filename='/home/ec2-user/chatbot-test/logfile.txt',  # Log file location
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Main chat endpoint
@app.post("/chat")
async def chat(request: Request, chat_request: ChatRequest):
    # Generate or retrieve session ID
    session_id = chat_request.session_id or str(uuid.uuid4())
    prompt = chat_request.prompt

    # Log the incoming request data
    logging.info(f"Received request: session_id={session_id}, prompt={prompt}")

    if not prompt:
        logging.error("Prompt is missing in the request")
        raise HTTPException(status_code=400, detail="Prompt is required")

    # Call askQuestion to get the LLM response and metadata
    try:
        captured_string, llm_response, metadata_list = agenthelper.askQuestion(prompt, session_id)
    except Exception as e:
        logging.error(f"Error while calling agenthelper.askQuestion: {e}")
        raise HTTPException(status_code=500, detail="Failed to process the request")

    # Check if LLM response is valid
    if llm_response:
        response = {
            "session_id": session_id,
            "response": llm_response,
            "metadata": metadata_list  # Include metadata in the response
        }
        # Log the outgoing response
        logging.info(f"Response sent: session_id={session_id}, response={llm_response}, metadata={metadata_list}")
        return JSONResponse(content=response)
    else:
        logging.error(f"LLM response is empty for session_id={session_id}")
        raise HTTPException(status_code=500, detail="Failed to process the request")

# Health check endpoint (optional)
@app.get("/health")
def health_check():
    logging.info("Health check requested")
    return {"status": "ok"}
