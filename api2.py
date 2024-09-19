from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import InvokeAgent as agenthelper
import uuid
import redis
import time
import pytz
import datetime
import json  # Import json for serialization

# Create FastAPI app
app = FastAPI()

# Mount the static directory to serve CSS, JS, and other static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Redis connection
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)


# Define a request model for input validation
class ChatRequest(BaseModel):
    prompt: str
    session_id: str = None


# Set rate-limiting configurations
RATE_LIMIT = 2  # max requests per minute
RATE_LIMIT_TTL = 60  # time window in seconds (1 minute)


# Function to check rate limit for a specific IP
def check_rate_limit(ip: str) -> bool:
    current_time = int(time.time())  # Current Unix timestamp
    key = f"rate_limit:{ip}"  # Unique Redis key for this IP
    request_count = redis_client.get(key)  # Fetch the request count for this IP

    if request_count:
        request_count = int(request_count)
        if request_count >= RATE_LIMIT:
            return False  # Deny request if limit is exceeded
        else:
            redis_client.incr(key)  # Increment request count
    else:
        # New IP or reset after TTL
        redis_client.set(key, 1, ex=RATE_LIMIT_TTL)  # Set with TTL (Time to Live)

    return True

# Helper function to convert Unix timestamp to readable time and LA time
def convert_timestamp(timestamp):
    # Convert to UTC datetime
    readable_time = datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')

    # Convert to Los Angeles time (Pacific Time)
    la_timezone = pytz.timezone('America/Los_Angeles')
    la_time = datetime.datetime.fromtimestamp(timestamp, la_timezone).strftime('%Y-%m-%d %H:%M:%S %Z')

    return readable_time, la_time

# Main chat endpoint with rate limiting
@app.post("/chat")
async def chat(request: Request, chat_request: ChatRequest):
    ip_address = request.client.host  # Get client IP address
    session_id = chat_request.session_id or str(uuid.uuid4())
    prompt = chat_request.prompt

    # Check rate limit
    if not check_rate_limit(ip_address):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")

    # Log the incoming request data in Redis
    timestamp = time.time()
    request_log = {
        "session_id": session_id,
        "prompt": prompt,
        "timestamp": timestamp,
        "readable_time": readable_time,
        "la_time": la_time,
        "ip_address": ip_address,
        "event": "request"
    }
    redis_client.rpush("chat_logs", json.dumps(request_log))  # Push request log into Redis

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    # Call askQuestion to get the LLM response and metadata
    captured_string, llm_response, metadata_list = agenthelper.askQuestion(prompt, session_id)

    # Log response and send to client
    if llm_response:
        response = {
            "session_id": session_id,
            "response": llm_response,
            "metadata": metadata_list  # Include metadata in the response
        }

        # Log the outgoing response in Redis
        response_log = {
            "session_id": session_id,
            "response": llm_response,
            "metadata": metadata_list,
            "timestamp": time.time(),
            "readable_time": readable_time,
            "la_time": la_time,
            "ip_address": ip_address,
            "event": "response"
        }
        redis_client.rpush("chat_logs", json.dumps(response_log))  # Push response log into Redis

        return JSONResponse(content=response)
    else:
        raise HTTPException(status_code=500, detail="Failed to process the request")


# Health check endpoint (optional)
@app.get("/health")
def health_check():
    redis_client.rpush("chat_logs", json.dumps({"event": "health_check", "timestamp": time.time()}))
    return {"status": "ok"}
