// Function to handle user input and send it to Flask API
async function sendUserInput() {
    const userInput = document.getElementById("user-input").value;

    if (userInput.trim()) {
        // Clear the input field
        document.getElementById("user-input").value = "";

        // Send the user input to the backend
        const response = await fetch('/get_ai_story', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_input: userInput }) // Send userInput here
        });

        const data = await response.json();
        
        if (data.text) {  // Check for 'text' instead of 'story'
            const chatBox = document.getElementById("chat-box");
            chatBox.innerHTML += `<p><strong>You:</strong> ${userInput}</p>`;
            chatBox.innerHTML += `<p><strong>AI:</strong> ${data.text}</p>`;  // Use data.text here
            chatBox.scrollTop = chatBox.scrollHeight;  // Scroll to the bottom
        } else {
            console.error("Error generating story:", data.error);
        }
    }
}