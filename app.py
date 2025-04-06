from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'library.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Add this helper function right here
@app.context_processor
def utility_processor():
    def now():
        return datetime.now()
    return dict(now=now)

# Book model
class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    def __repr__(self):
        return f'<Book {self.title}>'

# Create the database tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add-book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        # Extract form data
        book_title = request.form.get('bookTitle')
        author = request.form.get('author')
        year = request.form.get('year')
        quantity = request.form.get('quantity')
        
        # Print form data to terminal
        print(f"Book Title: {book_title}")
        print(f"Author: {author}")
        print(f"Publication Year: {year}")
        print(f"Quantity: {quantity}")
        
        # Create a new book object
        new_book = Book(
            title=book_title,
            author=author,
            year=int(year),
            quantity=int(quantity)
        )
        
        # Add to database
        db.session.add(new_book)
        db.session.commit()
        
        # Redirect back to the form
        return redirect(url_for('add_book'))
    
    return render_template('add-book.html')
# Add this to your app.py file

# Transaction model i did changes here
class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    member_name = db.Column(db.String(200), nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.now)
    return_date = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='issued')  # issued, returned, overdue
    
    # Relationship to access book details
    book = db.relationship('Book', backref=db.backref('transactions', lazy=True))
    
    def __repr__(self):
        return f'<Transaction {self.id}: {self.book.title} - {self.member_name}>'

# Create the issue-book route
@app.route("/issue-book", methods=["GET", "POST"])
def issue_book():
    if request.method == "POST":
        book_id = request.form['book_id']
        member_name = request.form['member_name']

        book = Book.query.get(book_id)
        if book and book.quantity > 0:
            book.quantity -= 1

            new_transaction = Transaction(
                book_id=book.id,
                member_name=member_name,
                issue_date=datetime.now()
            )
            db.session.add(new_transaction)
            db.session.commit()

            return redirect("/")
        else:
            return "Book not available", 400

    books = Book.query.all()
    return render_template("issue_book.html", books=books)

# Route to view all transactions
@app.route('/view-transactions')
def view_transactions():
    transactions = Transaction.query.all()
    return render_template('view-transactions.html', transactions=transactions)

# Route to return a book
@app.route('/return-book/<int:transaction_id>', methods=['POST'])
def return_book(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    
    # Update transaction
    transaction.return_date = datetime.datetime.now()
    transaction.status = 'returned'
    
    # Update book quantity
    book = Book.query.get(transaction.book_id)
    book.quantity += 1
    
    db.session.commit()
    return redirect(url_for('view_transactions'))
    
@app.route('/view-books')
def view_books():
    # Query all books from the database
    books = Book.query.all()
    return render_template('view-books.html', books=books)
   
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
