# app.py
import random
import os
from flask import Flask, render_template, request, session
import pokebase as pb
from dotenv import load_dotenv

load_dotenv()

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")



def fetch_pokemon():
    pokemonid = random.randrange(1, 1025, 1)
    current_pokemon = pb.pokemon(pokemonid)  # Fetch Pokémon data
    print(f"Generated Pokémon: {current_pokemon.name}")  # Debugging info
    return current_pokemon.name.lower()  # Store only the Pokémon name


# Route for the homepage
@app.route('/')
def home():

    user_name = "John Doe"
    return render_template('index.html', user_name=user_name)


@app.route('/submit', methods=['POST'])
def submit():
    user_name = request.form['name']
    return f"Hello, {user_name}!"


@app.route('/quiz', methods=["GET", "POST"])
def quiz():
    if "secret_word" not in session:
        session["secret_word"] = fetch_pokemon()
    message = ""
    if request.method == "POST":
        guess = request.form.get("guess", "").strip().lower()
        if guess == session["secret_word"]:
            message = "Your answer is correct"
            session.modified = True  # Ensure session updates
            session.pop("secret_word", None)  # Remove old word
            return render_template("quiz.html", message=message, reload=True)
        else:
            message = "Unfortunately thats incorrect you fucking donkey"
    return render_template('quiz.html', message=message, reload=False)


if __name__ == '__main__':
    # Run the app in debug mode (auto-reload and better error messages)
    app.run(debug=True)
