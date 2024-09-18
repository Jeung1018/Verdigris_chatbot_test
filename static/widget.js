document.addEventListener('DOMContentLoaded', function() {
    // Create and inject the chat button
    var chatButton = document.createElement('button');
    chatButton.id = 'chatButton';
    chatButton.innerHTML = '&#128172;';  // Chat icon
    document.body.appendChild(chatButton);

    // Retrieve the chat box and resize button
    var chatBox = document.getElementById('chatBox');
    var resizeButton = document.getElementById('resizeButton');
    var isLarge = false;

    // Add event listener for showing the chat box when clicked
    chatButton.addEventListener('click', function() {
        chatBox.style.display = (chatBox.style.display === 'none' || chatBox.style.display === '') ? 'flex' : 'none';
    });

    // Handle resizing on resize button click
    resizeButton.addEventListener('click', function() {
        if (isLarge) {
            chatBox.style.width = '450px';
            chatBox.style.height = '60vh';
            resizeButton.textContent = "<>"; // Update button text when minimized
            isLarge = false;
        } else {
            chatBox.style.width = '600px';
            chatBox.style.height = '80vh';
            resizeButton.textContent = "><"; // Update button text when expanded
            isLarge = true;
        }
    });

    // Send chat message to backend
    document.getElementById('sendChat').addEventListener('click', async function() {
        var prompt = document.getElementById('chatPrompt').value;
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

            // Show thinking spinner
            var thinkingMessageBubble = document.createElement('div');
            thinkingMessageBubble.classList.add('message-container', 'bot-message');
            thinkingMessageBubble.innerHTML = '<div class="spinner"></div><p>Thinking...</p>';
            messagesDiv.appendChild(thinkingMessageBubble);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;

            // Send message to backend
            try {
                let res = await fetch("/chat", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ prompt: prompt, session_id: sessionStorage.getItem('session_id') })
                });
                let data = await res.json();

                // Remove the thinking spinner
                thinkingMessageBubble.remove();

                // Display bot's response
                var botMessageBubble = document.createElement('div');
                botMessageBubble.classList.add('message-container', 'bot-message');
                botMessageBubble.innerHTML = `<p>${data.response}</p>`;
                messagesDiv.appendChild(botMessageBubble);
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
            }
        }
    });
});
