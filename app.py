from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    available = db.Column(db.Boolean, default=True)

class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    issued_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    returned = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    books = Book.query.all()
    issues = db.session.query(Issue, Book).join(Book).filter(Issue.returned == False).all()
    return render_template('index.html', books=books, issues=issues)

@app.route('/add_book', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    new_book = Book(title=title, author=author)
    db.session.add(new_book)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/issue_book', methods=['POST'])
def issue_book():
    user_name = request.form['user_name']
    book_id = request.form['book_id']
    book = Book.query.get(book_id)
    if book and book.available:
        book.available = False
        issue = Issue(user_name=user_name, book_id=book_id)
        db.session.add(issue)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/return_book/<int:issue_id>')
def return_book(issue_id):
    issue = Issue.query.get(issue_id)
    if issue and not issue.returned:
        issue.returned = True
        book = Book.query.get(issue.book_id)
        book.available = True
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)