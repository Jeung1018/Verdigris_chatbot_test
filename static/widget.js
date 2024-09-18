document.addEventListener('DOMContentLoaded', function() {
    // Reference to the iframe in the parent page
    var parentIframe = window.parent.document.getElementById('chatWidgetFrame');
    var isExpanded = false;

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
            <img id="chatLogo" src="https://chatbot.verdigris.co/static/verdigris_logo.png" alt="Company Logo"/>
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

    // Initially hide the chat box and set minimized iframe style
    chatBox.style.display = 'none';
    parentIframe.style.width = '60px';
    parentIframe.style.height = '60px';
    parentIframe.style.pointerEvents = 'none'; // Prevent iframe from blocking other elements
    parentIframe.style.zIndex = '1';  // Set a low z-index when minimized

    // Toggle chat box visibility and iframe size
    chatButton.addEventListener('click', function() {
        if (isExpanded) {
            // Minimize the iframe size and disable interaction
            parentIframe.style.width = '60px';
            parentIframe.style.height = '60px';
            parentIframe.style.pointerEvents = 'none';  // Disable interaction to prevent blocking
            parentIframe.style.zIndex = '1';  // Lower z-index when minimized
            chatBox.style.display = 'none';  // Hide the chat box when iframe is minimized
        } else {
            // Expand the iframe size and enable interaction
            parentIframe.style.width = '450px';
            parentIframe.style.height = '600px';
            parentIframe.style.pointerEvents = 'auto';  // Enable interaction
            parentIframe.style.zIndex = '1000';  // Set high z-index when expanded
            chatBox.style.display = 'flex';  // Show the chat box when iframe is expanded
        }
        isExpanded = !isExpanded;
    });

    // Ensure iframe allows pointer-events on the button when minimized
    parentIframe.style.pointerEvents = 'none';  // Initially set to none when minimized

    // Session ID management
    var session_id = sessionStorage.getItem('session_id');  // Retrieve session_id from sessionStorage
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
            resizeButton.textContent = "><";  // Update button text when collapsed
            isLarge = false;
        } else {
            resizeChatContainer();
        }
    });

    // Send button click event handler
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

            // Send the message to the backend (POST request to /chat API)
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
                botMessageBubble.innerHTML = `<p>${data.response}</p>`;
                messagesDiv.appendChild(botMessageBubble);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;

                // Display metadata if available
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
                    botMessageBubble.appendChild(referencesContainer);
                }

                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            } catch (error) {
                // Handle errors (e.g., network or server errors)
                thinkingMessageBubble.remove();
                var errorMessageBubble = document.createElement('div');
                errorMessageBubble.classList.add('message-container', 'bot-message');
                errorMessageBubble.innerHTML = `<p>Error occurred: ${error.message}</p>`;
                messagesDiv.appendChild(errorMessageBubble);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
        }
    });
});
