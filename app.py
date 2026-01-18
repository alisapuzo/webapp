from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/list/')
def lists():
    return "TODO: This is the list page"

@app.route('/list/<int:id>')
def list(id):
    return f"TODO: This is the list page for list with id {id}"

