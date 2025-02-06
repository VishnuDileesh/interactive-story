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
    data = request.get_json()
    user_input = data.get('user_input')

    if not user_input:
        return jsonify({'error': 'No user input provided'}), 400

    # Get conversation history from session or initialize an empty list
    history = session.get('history', [])
    
    # If the user chooses to exit, clear history and stop further interaction
    if user_input.lower() == 'exit':
        session['history'] = []
        return jsonify({
            'story': 'You have exited the story. Thank you for playing!',
            'choices': []
        })

    # Generate the story content based on user input
    ai_response, updated_history = generate_story_logic(user_input, history)
    
    # Parse the response to separate story and choices
    try:
        # Split the response at "CHOICES:" if present
        if "CHOICES:" in ai_response:
            story_part, choices_part = ai_response.split("CHOICES:")
            choices = [choice.strip() for choice in choices_part.split("\n") if choice.strip()]
        else:
            story_part = ai_response
            choices = ['Continue', 'Change direction', 'Exit']
    except Exception:
        story_part = ai_response
        choices = ['Continue', 'Change direction', 'Exit']

    # Update session history
    session['history'] = updated_history

    # Return the AI-generated story content
    return jsonify({
        'story': story_part.strip(),
        'choices': choices
    })


# Function to generate a story based on user input and choices
def generate_story_logic(user_input, history=None):
    if history is None:
        history = []
        # Initial story prompt when starting fresh
        system_prompt = """You are an interactive storyteller. Create engaging, family-friendly stories 
        with clear choices for the reader. Each response should:
        1. Be 2-3 paragraphs long
        2. End with 3 clear choices for what could happen next
        3. Keep the story coherent with previous choices
        
        Format your response like this:
        [Story content here]
        
        CHOICES:
        1. [First choice]
        2. [Second choice]
        3. [Third choice]"""
        
        initial_prompt = f"{system_prompt}\n\nCreate the beginning of a story based on: {user_input}"
        response = model.generate_content(initial_prompt)
    else:
        # For continuing the story, include context and previous choices
        context = "\n".join(history)
        continuation_prompt = f"""Previous story context:
        {context}
        
        User's choice: {user_input}
        
        Continue the story based on this choice. Remember to end with 3 new choices."""
        
        response = model.generate_content(continuation_prompt)

    # Add the AI's response to the history
    ai_response = response.text
    history.append(f"AI: {ai_response}")

    return ai_response, history


if __name__ == '__main__':
    app.run(debug=True)