from flask import Flask, render_template

# Initialize Flask app
app = Flask(__name__)

# Define route for homepage
@app.route('/')
def home():
    return render_template('index.html')  # loads the HTML page

# Run the server
if __name__ == '__main__':
    app.run(debug=True)
