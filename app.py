import google.generativeai as genai
from flask import Flask, jsonify, render_template, request, session
import os

genai.configure(api_key=os.environ.get('GENAI_API_KEY'))

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')  # For session management


@app.route('/')
def index():
    return render_template('index.html')


# Initialize the model
model = genai.GenerativeModel("gemini-1.5-flash")


@app.route('/get_ai_story', methods=['POST'])
def generate_story():
    # Get the JSON data from the request body
    data = request.get_json()
    
    # Extract user input from the JSON data
    user_input = data.get('user_input')

    if not user_input:
        return jsonify({'error': 'No user input provided'}), 400

    # Get conversation history from session or initialize an empty list
    history = session.get('history', [])
    
    # If the user chooses to exit, clear history and stop further interaction
    if user_input.lower() == 'exit':
        session['history'] = []  # Clear history to stop the conversation
        return jsonify({
            'story': 'You have exited the story. Thank you for playing!',
            'choices': []
        })

    # Generate the story content based on user input
    ai_response, updated_history = generate_story_logic(user_input, history)

    # Update session history
    session['history'] = updated_history

    # Return the AI-generated story content
    return jsonify({
        'story': ai_response,
        'choices': ['Continue', 'Change action', 'Exit']  # Choices to show
    })


# Function to generate a story based on user input and choices
def generate_story_logic(user_input, history=None):
    if history is None:
        history = []

    # Add the current user input to the history
    history.append(f"User: {user_input}")

    # Generate story content based on the user's input and history
    prompt = "\n".join(history)  # Combine history to maintain context

    # Call the Gemini model to generate the next part of the story
    response = model.generate_content(prompt)

    # Add the AI's response to the history
    ai_response = response.text
    history.append(f"AI: {ai_response}")

    return ai_response, history


if __name__ == '__main__':
    app.run(debug=True)