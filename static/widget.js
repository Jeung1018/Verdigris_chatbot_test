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
            <img id="chatLogo" src="/static/verdigris_logo.png" alt="Company Logo"/>
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

