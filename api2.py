from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import uuid
import logging
import InvokeAgent as agenthelper

app = FastAPI()

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
        return response
    else:
        raise HTTPException(status_code=500, detail="Failed to process the request")


# Health check endpoint (optional)
@app.get("/health")
def health_check():
    return {"status": "ok"}


# Serve the widget JavaScript file dynamically
@app.get("/widget.js", response_class=HTMLResponse)
async def get_widget_js():
    script_content = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

        /* Apply the Roboto font globally */
        body, #chatHeader, #chatMessages, #chatPrompt, #sendChat {
            font-family: 'Roboto', sans-serif;
        }

        /* Floating button */
        #chatButton {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: rgba(102, 224, 224, 1);
            color: white;
            border: none;
            border-radius: 50%;
            padding: 15px;
            font-size: 20px;
            cursor: pointer;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            z-index: 1000;
        }

        /* Chatbox container */
        #chatBox {
            display: none;
            position: fixed;
            bottom: 80px;
            right: 20px;
            width: 450px;
            height: 60vh;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            z-index: 1000;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: width 0.5s ease, height 0.5s ease;
        }

        /* Large chatbox */
        .large {
            width: 600px;
            height: 80vh;
        }

        /* Chatbox header with logo and resize button */
        #chatHeader {
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: white;
            color: #004A3E;
            font-size: 20px;
            font-weight: bold;
            position: relative;
            margin-top: 20px;
            margin-left: 30px;
        }

        /* Resize button */
        #resizeButton {
            background-color: rgba(102, 224, 224, 1);
            color: white;
            border: none;
            border-radius: 5px;
            position: absolute;
            right: 10px;
            transform: translateY(-50%);
            width: 30px;
            height: 24px;
            cursor: pointer;
            font-size: 12px;
            margin-top: 20px;
        }

        /* Logo image styling */
        #chatLogo {
            max-width: 120px;
            position: absolute;
            left: -35px;
            height: auto;
            margin-top: 10px;
        }

        /* Chat messages container */
        #chatMessages {
            flex-grow: 1;
            padding: 10px;
            overflow-y: auto;
            font-size: 14px;
        }

        /* Chat input area */
        #chatInputContainer {
            display: flex;
            border-top: 1px solid #ccc;
            padding: 10px;
            background-color: #f9f9f9;
        }

        #chatPrompt {
            flex-grow: 1;
            border: 1px solid #ccc;
            padding: 10px;
            border-radius: 5px;
            font-size: 14px;
            outline: none;
        }

        #sendChat {
            background-color: rgba(102, 224, 224, 1);
            color: white;
            border: none;
            padding: 10px;
            margin-left: 10px;
            border-radius: 5px;
            cursor: pointer;
        }

        #sendChat:hover {
            background-color: #0056d6;
        }

        /* Spinner style */
        .spinner {
            border: 4px solid rgba(0, 0, 0, 0.1);
            border-left-color: #0069ff;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
            display: inline-block;
            vertical-align: middle;
            margin-right: 10px;
        }

        @keyframes spin {
            0% {
                transform: rotate(0deg);
            }
            100% {
                transform: rotate(360deg);
            }
        }

        /* Bubble styling for user and bot messages */
        .message-container {
            display: flex;
            flex-direction: column;
            margin-bottom: 10px;
            align-items: flex-start;
        }

        .user-message {
            background-color: rgba(102, 224, 224, 0.1);
            border-radius: 15px;
            padding: 10px;
            padding-left: 20px;
            color: #004A3E;
            max-width: 70%;
            align-self: flex-end;
            margin-left: auto;
            margin-top: 20px;
        }

        .bot-message {
            background-color: rgba(102, 224, 224, 0.3);
            border-radius: 15px;
            padding: 20px;
            color: #004A3E;
            max-width: 80%;
            align-self: flex-start;
        }

        /* Style for the foldable references section */
        .references-container {
            margin-top: 10px;
            width: 100%;
        }
        
        details {
            margin-top: 10px;
            border: 1px solid #ccc;
            padding: 15px;
            border-radius: 5px;
            background-color: white;
        }
        
        summary {
            font-weight: bold;
            cursor: pointer;
        }
        
        summary:hover {
            color: #0069ff;
        }
        
        /* Reference bubble button styling */
        .reference-button {
            display: inline-block;
            padding: 10px 15px;
            margin: 5px;
            background-color: #66E0E0;
            color: white;
            border-radius: 20px;
            text-decoration: none;
            font-size: 14px;
            font-weight: bold;
            transition: background-color 0.3s;
        }
        
        .reference-button:hover {
            background-color: #0056d6;
            text-decoration: none;
        }


    </style>

    <script>
      document.addEventListener('DOMContentLoaded', function() {
        // Create and inject the chat button
        var chatButton = document.createElement('button');
        chatButton.id = 'chatButton';
        chatButton.innerHTML = '&#128172;';
        document.body.appendChild(chatButton);

        // Create and inject the chat box
        var chatBox = document.createElement('div');
        chatBox.id = 'chatBox';
        chatBox.innerHTML = `
            <div id="chatHeader">
                <img id="chatLogo" src="static/verdigris_logo.png" alt="Company Logo"/>
                <div style="display: flex; flex-direction: column; align-items: flex-start;">
                    <span>Ask anything to Verdigris AI</span>
                    <span style="font-size: 12px;">powered by Claude3</span>
                </div>
                <button id="resizeButton"><></button> <!-- Resize button added -->
            </div>
            <div id="chatMessages"></div>
            <div id="chatInputContainer">
                <input id="chatPrompt" type="text" placeholder="Enter your message" />
                <button id="sendChat">Send</button>
            </div>
        `;
        document.body.appendChild(chatBox);
        
        var session_id = sessionStorage.getItem('session_id');  // Retrieve session_id from sessionStorage
        
        // If no session_id exists, generate a new one
        if (!session_id) {
            session_id = generateSessionId();  // Function to generate a unique session_id
            sessionStorage.setItem('session_id', session_id);  // Store it in sessionStorage
        }
        
        var chatContainer = document.getElementById('chatBox');
        var resizeButton = document.getElementById('resizeButton');
        var isLarge = false;  // Track if the container is large

        // Function to generate a unique session ID
        function generateSessionId() {
            return 'sess-' + Math.random().toString(36).substr(2, 9);  // Simple UUID-like generator
        }

        // Handle resizing on first question submission
        function resizeChatContainer() {
          chatContainer.style.width = '600px';
          chatContainer.style.height = '80vh';
          resizeButton.textContent = "<>"; // Update button text when expanded
          isLarge = true;
        }

        // Toggle container size on resize button click
        resizeButton.addEventListener('click', function() {
          if (isLarge) {
            chatContainer.style.width = '450px';
            chatContainer.style.height = '60vh';
            resizeButton.textContent = "<>"; // Update button text when collapsed
            isLarge = false;
          } else {
            chatContainer.style.width = '600px';
            chatContainer.style.height = '80vh';
            resizeButton.textContent = "><"; // Update button text when expanded
            isLarge = true;
          }
        });

        // Toggle chat box visibility
        chatButton.addEventListener('click', function() {
          if (chatBox.style.display === 'none') {
            chatBox.style.display = 'flex';
          } else {
            chatBox.style.display = 'none';
          }
        });

        // Handle sending the chat message
        document.getElementById('sendChat').addEventListener('click', async function() {
          var prompt = document.getElementById('chatPrompt').value;
          var messagesDiv = document.getElementById('chatMessages');

          if (prompt) {
            // Immediately show the user's question in the chat window inside a bubble
            var userMessageBubble = document.createElement('div');
            userMessageBubble.classList.add('message-container', 'user-message');
            userMessageBubble.innerHTML = '<p><strong>You:</strong> ' + prompt + '</p>';
            messagesDiv.appendChild(userMessageBubble);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            // Clear the input field after sending the message
            document.getElementById('chatPrompt').value = '';  // Clear the text input

            // Resize the chat container on the first question
            if (!isLarge) {
              resizeChatContainer();
            }

            // Show the spinner and 'thinking' message inside a bot message bubble
            var thinkingMessageBubble = document.createElement('div');
            thinkingMessageBubble.classList.add('message-container', 'bot-message');
            thinkingMessageBubble.innerHTML = '<div class="spinner"></div><p>Thinking...</p>';
            messagesDiv.appendChild(thinkingMessageBubble);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;

            try {
              let res = await fetch("/chat", {
                method: "POST",
                headers: {
                  "Content-Type": "application/json"
                },
                body: JSON.stringify({ prompt: prompt, session_id: session_id })  // Send session_id with the prompt
              });
              let data = await res.json();

              // Remove the thinking message bubble after response is received
              thinkingMessageBubble.remove();

              // Create a bot message bubble for the response
              var botMessageBubble = document.createElement('div');
              botMessageBubble.classList.add('message-container', 'bot-message');
              messagesDiv.appendChild(botMessageBubble);

              // Stream response character by character
              for (let i = 0; i < data.response.length; i++) {
                await new Promise(resolve => setTimeout(resolve, 20)); // Adjust delay as needed
                botMessageBubble.innerHTML += data.response[i];
                messagesDiv.scrollTop = messagesDiv.scrollHeight; // Scroll to the bottom as it streams
              }
                      
              // Add the references directly below the last answer character
              if (data.metadata && data.metadata.length > 0) {
                let referencesContainer = document.createElement('div');
                referencesContainer.classList.add('references-container');
                
                let foldableReferences = `
                  <details>
                    <summary>References</summary>
                    <p>This answer is generated by referring to our company documentation below:</p>
                    <div style="display: flex; flex-wrap: wrap;">
                `;


                // Create bubble buttons for each reference
                data.metadata.forEach(function(item) {
                  if (item.url) {
                    foldableReferences += '<a href="' + item.url + '" class="reference-button" target="_blank">' + item.title + '</a>';
                  }
                });

                foldableReferences += '</details>';
                referencesContainer.innerHTML = foldableReferences;
                botMessageBubble.appendChild(referencesContainer); // Add the references inside the bot message
              }

              messagesDiv.scrollTop = messagesDiv.scrollHeight;
            } catch (error) {
              thinkingMessageBubble.remove();  // Remove thinking bubble in case of error
              var errorMessageBubble = document.createElement('div');
              errorMessageBubble.classList.add('message-container', 'bot-message');
              errorMessageBubble.innerHTML = '<p>Error occurred: ' + error.message + '</p>';
              messagesDiv.appendChild(errorMessageBubble);
              messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
          }
        });
      });
    </script>
    """
    return HTMLResponse(content=script_content)
