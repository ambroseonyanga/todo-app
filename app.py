from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env file

app = Flask(__name__)

# Database connection using environment variable
database_url = os.getenv('DATABASE_URL', 'sqlite:///todos.db')

# Fix Railway's postgres:// to postgresql:// (SQLAlchemy requirement)
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# --- Database Model ---
class Todo(db.Model):
    id   = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)
    tag  = db.Column(db.String(50), default='personal')

    def __repr__(self):
        return f'<Todo {self.task}>'


# Create tables on startup - must be after the model definition
# This works with both gunicorn (Railway) and flask (local)
with app.app_context():
    db.create_all()


# --- Routes ---

# READ - Show all tasks
@app.route('/')
def index():
    todos = Todo.query.all()
    return render_template('index.html', todos=todos)


# CREATE - Add a new task
@app.route('/add', methods=['POST'])
def add():
    task_text = request.form.get('task')
    tag       = request.form.get('tag', 'personal')
    if task_text:
        new_todo = Todo(task=task_text, tag=tag)
        db.session.add(new_todo)
        db.session.commit()
    return redirect(url_for('index'))


# UPDATE - Mark task as done / undone
@app.route('/toggle/<int:id>', methods=['POST'])
def toggle(id):
    todo = Todo.query.get_or_404(id)
    todo.done = not todo.done
    db.session.commit()
    return redirect(url_for('index'))


# DELETE - Remove a task
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
