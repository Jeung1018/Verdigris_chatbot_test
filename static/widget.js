document.addEventListener('DOMContentLoaded', function() {
    // Create and inject the chat button
    var chatButton = document.createElement('button');
    chatButton.id = 'chatButton';
    chatButton.innerHTML = '&#128172;';
    document.body.appendChild(chatButton);

    // Retrieve the chat box and resize button
    var chatBox = document.getElementById('chatBox');
    var resizeButton = document.getElementById('resizeButton');
    var isLarge = false;

    // Handle resizing on resize button click
    resizeButton.addEventListener('click', function() {
        if (isLarge) {
            chatBox.style.width = '450px';
            chatBox.style.height = '60vh';
            resizeButton.textContent = "<>"; // Update button text
            isLarge = false;
        } else {
            chatBox.style.width = '600px';
            chatBox.style.height = '80vh';
            resizeButton.textContent = "><"; // Update button text
            isLarge = true;
        }
    });

    // Toggle chat box visibility
    chatButton.addEventListener('click', function() {
        if (chatBox.style.display === 'none' || chatBox.style.display === '') {
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
                    body: JSON.stringify({ prompt: prompt, session_id: sessionStorage.getItem('session_id') })
                });
                let data = await res.json();

                thinkingMessageBubble.remove();

                var botMessageBubble = document.createElement('div');
                botMessageBubble.classList.add('message-container', 'bot-message');
                botMessageBubble.innerHTML = `<p>${data.response}</p>`;
                messagesDiv.appendChild(botMessageBubble);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
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
