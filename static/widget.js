document.addEventListener('DOMContentLoaded', function() {

    // Check if session_id exists in sessionStorage, if not generate one
    if (!sessionStorage.getItem('session_id')) {
        const sessionId = generateUUID();
        sessionStorage.setItem('session_id', sessionId);
        console.log("Generated session ID:", sessionId); // Debugging info
    }

    // Retrieve the chat box and resize button
    var chatBox = document.getElementById('chatBox');
    var resizeButton = document.getElementById('resizeButton');
    var sendButton = document.getElementById('sendChat');
    var isLarge = false;

    // Send a message to the parent window on resize button click
    resizeButton.addEventListener('click', function() {
        window.parent.postMessage('toggleResize', '*');
    });

    // Disable send button if input is empty
    document.getElementById('chatPrompt').addEventListener('input', function() {
        sendButton.disabled = !this.value.trim();
    });

    // Send chat message to backend
    sendButton.addEventListener('click', async function() {
        var prompt = document.getElementById('chatPrompt').value.trim();
        var messagesDiv = document.getElementById('chatMessages');

        if (prompt) {
            // Display user's message
            var userMessageBubble = document.createElement('div');
            userMessageBubble.classList.add('message-container', 'user-message');
            userMessageBubble.innerHTML = '<p><strong>You:</strong> ' + prompt + '</p>';
            messagesDiv.appendChild(userMessageBubble);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;

            // Clear the input field
            document.getElementById('chatPrompt').value = '';
            sendButton.disabled = true; // Disable until next input

            // Show thinking spinner
            var thinkingMessageBubble = document.createElement('div');
            thinkingMessageBubble.classList.add('message-container', 'bot-message');
            thinkingMessageBubble.innerHTML = '<div class="spinner"></div><p>Thinking...</p>';
            messagesDiv.appendChild(thinkingMessageBubble);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;

            // Send message to backend
            try {
                let res = await fetch("https://chatbot.verdigris.co/chat", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ prompt: prompt, session_id: sessionStorage.getItem('session_id') })
                });

                if (!res.ok) {
                    throw new Error(`Server error: ${res.statusText}`);
                }

                let data = await res.json();

                // Remove the thinking spinner
                thinkingMessageBubble.remove();

                // Display bot's response
                var botMessageBubble = document.createElement('div');
                botMessageBubble.classList.add('message-container', 'bot-message');
                botMessageBubble.innerHTML = `<p>${data.response}</p>`;
                messagesDiv.appendChild(botMessageBubble);

                // Add references if available
                if (data.metadata && data.metadata.length > 0) {
                    let referencesContainer = document.createElement('div');
                    referencesContainer.classList.add('references-container');

                    let foldableReferences = `
                        <details>
                            <summary>References</summary>
                            <p>This answer is generated by referring to the documentation below:</p>
                            <div style="display: flex; flex-wrap: wrap;">
                    `;

                    // Create clickable reference buttons
                    data.metadata.forEach(function(item) {
                        if (item.url) {
                            foldableReferences += `<a href="${item.url}" class="reference-button" target="_blank">${item.title}</a>`;
                        }
                    });

                    foldableReferences += '</div></details>';
                    referencesContainer.innerHTML = foldableReferences;
                    botMessageBubble.appendChild(referencesContainer);
                }

                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            } catch (error) {
                // Remove the thinking spinner in case of an error
                thinkingMessageBubble.remove();

                // Show error message
                var errorMessageBubble = document.createElement('div');
                errorMessageBubble.classList.add('message-container', 'bot-message');
                errorMessageBubble.innerHTML = '<p>Error occurred: ' + error.message + '</p>';
                messagesDiv.appendChild(errorMessageBubble);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;

                console.error("Error during fetch:", error); // Log for debugging
            }
        }
    });
});

// Helper function to generate a unique session ID
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}
