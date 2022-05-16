import json
from flask import Flask, jsonify, request, g
from flask_cors import CORS, cross_origin
from database import Database
import ctypes
import waitress
import time
import multiprocessing as mp
from multiprocessing.sharedctypes import Value, Array
import datetime
import oled

app = Flask(__name__, static_folder='./static', static_url_path='/')
CORS(app)
db = Database(app)

#lock = mp.Lock()
#current_todos = Array(ctypes.c_char_p, [], lock=lock)
#current_todo_id = Value('i', 0, lock=lock)

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

if __name__ == '__main__':
    oledProcess = mp.Process(target=oled.oled_screen);
    oledProcess.start()
    waitress.serve(app, host='0.0.0.0', port='80')
    oledProcess.join()

