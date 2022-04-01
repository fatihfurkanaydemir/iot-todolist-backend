import json
from flask import Flask, jsonify, request, g, render_template
from flask_cors import CORS, cross_origin
from database import Database

app = Flask(__name__, static_folder='./static', static_url_path='/')
CORS(app)
db = Database(app)

@app.route("/")
def index():
   return app.send_static_file('index.html')

@app.route('/api/v1/todos', methods=['GET'])
def get_todos():
  return jsonify(db.get_todos())

@app.route('/api/v1/todos', methods=['POST'])
def add_todo():
  todo = json.loads(request.data)

  newTodo = db.add_todo(todo)

  return jsonify(newTodo)

@app.route('/api/v1/todos', methods=['DELETE'])
def delete_todo():
  id = json.loads(request.data)

  db.delete_todo(id)
  
  return jsonify(success=True)

@app.route('/api/v1/todos', methods=['PUT'])
def mark_todo():
  id = json.loads(request.data)

  updatedTodo = db.mark_todo(id)
  
  return jsonify(updatedTodo)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def create_app():
  return app