import sqlite3 as sql
from flask import g

DATABASE = 'db.sqlite'

class Database():
  def __init__(self, app):
    app.app_context().push()

    db = self.get_db()
    cur = db.cursor()

    query = """
            CREATE TABLE IF NOT EXISTS todo (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              content TEXT NOT NULL,
              duedate TEXT,
              isCompleted INTEGER(1) DEFAULT(0)
            )
            """

    cur.execute(query)
    db.commit()
    cur.close()


  def get_db(self):
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sql.connect(DATABASE)
    return db


  def add_todo(self, todo):
    query = """
            INSERT INTO todo(content, duedate)
                 VALUES(?,?)
            """

    db = self.get_db()
    cur = db.cursor()

    cur.execute(query, (todo['content'], todo['duedate']))
    newTodoId = cur.lastrowid
    db.commit()
    cur.close()

    newTodo = self.get_todo(newTodoId)
    return newTodo

  def delete_todo(self, id):
    query = """
            DELETE FROM todo
                 WHERE id = ?
            """

    db = self.get_db()
    cur = db.cursor()

    cur.execute(query, (id,))
    db.commit()
    cur.close()

  def mark_todo(self, id):
    query = """
            UPDATE todo 
            SET isCompleted = 1 - isCompleted
                 WHERE id = ?
            """

    db = self.get_db()
    cur = db.cursor()

    cur.execute(query, (id,))
    db.commit()
    cur.close()

    return self.get_todo(id)

  def get_todo(self, id):
    db = self.get_db()
    cur = db.cursor()

    query = """
            SELECT * FROM todo WHERE id = ?
            """

    cur.execute(query, (str(id),))

    todo = cur.fetchone()
    todo = {
        'id': todo[0],
        'text': todo[1],
        'duedate': todo[2],
        'isCompleted': todo[3]
      }

    cur.close()

    return todo


  def get_todos(self):
    query = """
            SELECT * FROM todo
            """
    
    db = self.get_db()
    cur = db.cursor()

    cur.execute(query)
    todosRaw = cur.fetchall()
    todos = []

    for todo in todosRaw:
      todos.append({
        'id': todo[0],
        'text': todo[1],
        'duedate': todo[2],
        'isCompleted': todo[3]
      })

    cur.close()

    return todos