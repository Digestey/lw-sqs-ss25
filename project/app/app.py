# app.py
from flask import Flask, render_template, request

# Initialize Flask application
app = Flask(__name__)

# Route for the homepage
@app.route('/')
def home():
    user_name = "John Doe"
    return render_template('index.html', user_name=user_name)

@app.route('/submit', methods=['POST'])
def submit():
    user_name = request.form['name']
    return f"Hello, {user_name}!"


if __name__ == '__main__':
    app.run(debug=True)  # Run the app in debug mode (auto-reload and better error messages)
