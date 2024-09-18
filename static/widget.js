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
            <img id="chatLogo" src="https://chatbot.verdigris.co/static/verdigris_logo.png" alt="Company Logo"/>
            <div style="display: flex; flex-direction: column; align-items: flex-start;">
                <span>Ask anything to Verdigris AI</span>
                <span style="font-size: 12px;">powered by Claude3</span>
            </div>
            <button id="resizeButton">Resize</button>
        </div>
        <div id="chatMessages"></div>
        <div id="chatInputContainer">
            <input id="chatPrompt" type="text" placeholder="Enter your message" />
            <button id="sendChat">Send</button>
        </div>
    `;
    document.body.appendChild(chatBox);

    var session_id = sessionStorage.getItem('session_id');

    // If no session_id exists, generate a new one
    if (!session_id) {
        session_id = generateSessionId();
        sessionStorage.setItem('session_id', session_id);
    }

    var chatContainer = document.getElementById('chatBox');
    var resizeButton = document.getElementById('resizeButton');
    var isLarge = false;

    // Function to generate a unique session ID
    function generateSessionId() {
        return 'sess-' + Math.random().toString(36).substr(2, 9);
    }

    // Handle resizing
    resizeButton.addEventListener('click', function() {
        if (isLarge) {
            chatContainer.style.width = '450px';
            chatContainer.style.height = '60vh';
            resizeButton.textContent = "Expand";
            isLarge = false;
        } else {
            chatContainer.style.width = '600px';
            chatContainer.style.height = '80vh';
            resizeButton.textContent = "Shrink";
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

    // Send chat message to backend
    document.getElementById('sendChat').addEventListener('click', async function() {
        var prompt = document.getElementById('chatPrompt').value;
        var messagesDiv = document.getElementById('chatMessages');

        if (prompt) {
            var userMessageBubble = document.createElement('div');
            userMessageBubble.classList.add('message-container', 'user-message');
            userMessageBubble.innerHTML = '<p><strong>You:</strong> ' + prompt + '</p>';
            messagesDiv.appendChild(userMessageBubble);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;

            document.getElementById('chatPrompt').value = '';

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
                    body: JSON.stringify({ prompt: prompt, session_id: session_id })
                });
                let data = await res.json();

                thinkingMessageBubble.remove();

                var botMessageBubble = document.createElement('div');
                botMessageBubble.classList.add('message-container', 'bot-message');
                botMessageBubble.innerHTML = `<p>${data.response}</p>`;
                messagesDiv.appendChild(botMessageBubble);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;

                // Add metadata if available
                if (data.metadata && data.metadata.length > 0) {
                    let referencesContainer = document.createElement('div');
                    referencesContainer.classList.add('references-container');
                    let foldableReferences = `
                        <details>
                            <summary>References</summary>
                            <div style="display: flex; flex-wrap: wrap;">`;

                    data.metadata.forEach(function(item) {
                        foldableReferences += '<a href="' + item.url + '" class="reference-button" target="_blank">' + item.title + '</a>';
                    });

                    foldableReferences += '</details>';
                    referencesContainer.innerHTML = foldableReferences;
                    botMessageBubble.appendChild(referencesContainer);
                }
            } catch (error) {
                thinkingMessageBubble.remove();
                var errorMessageBubble = document.createElement('div');
                errorMessageBubble.classList.add('message-container', 'bot-message');
                errorMessageBubble.innerHTML = '<p>Error occurred: ' + error.message + '</p>';
                messagesDiv.appendChild(errorMessageBubble);
            }
        }
    });
});
