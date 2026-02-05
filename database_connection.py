import sqlite3

# Connect to the database
connection = sqlite3.connect('library_project.db')
cursor = connection.cursor()
import os
import sqlite3

connection = sqlite3.connect('library_project.db')
# Dosyanın tam yolunu terminale yazdırır
print("Current database path:", os.path.abspath('library_project.db'))
def add_book(title, author_id, stock_count):
    connection = sqlite3.connect('library_project.db')
    cursor = connection.cursor()
    
    # SQL INSERT command
    query = "INSERT INTO books (title, author_id, stock_count) VALUES (?, ?, ?)"
    
    try:
        cursor.execute(query, (title, author_id, stock_count))
        connection.commit()
        print(f"'{title}' has been added to the inventory.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        connection.close()

def delete_book(book_id):
    connection = sqlite3.connect('library_project.db')
    cursor = connection.cursor()
    
    try:
        cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        connection.commit()
        if cursor.rowcount > 0:
            print(f"Success: Book with ID {book_id} has been deleted.")
        else:
            print(f"Error: No book found with ID {book_id}.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        connection.close()

def loan_book(book_id, member_id):
    conn = sqlite3.connect('library_project.db')
    cursor = conn.cursor()
    
    # Check if the book is in stock
    cursor.execute("SELECT stock_count FROM books WHERE id = ?", (book_id,))
    result = cursor.fetchone()
    
    if result and result[0] > 0:
        # Add to loans table
        cursor.execute("INSERT INTO loans (book_id, member_id, is_returned) VALUES (?, ?, 0)", 
                       (book_id, member_id))
        # Update stock count
        cursor.execute("UPDATE books SET stock_count = stock_count - 1 WHERE id = ?", (book_id,))
        conn.commit()
        print(f"Success: Book ID {book_id} loaned to Member ID {member_id}.")
    else:
        print("Error: Out of stock or book not found.")
    
    conn.close()

def return_book(loan_id):
    conn = sqlite3.connect('library_project.db')
    cursor = conn.cursor()
    
    # Get the book_id associated with this loan before closing it
    cursor.execute("SELECT book_id, is_returned FROM loans WHERE id = ?", (loan_id,))
    loan_record = cursor.fetchone()
    
    if loan_record and loan_record[1] == 0:
        book_id = loan_record[0]
        # Mark as returned
        cursor.execute("UPDATE loans SET is_returned = 1, return_date = DATE('now') WHERE id = ?", (loan_id,))
        # Increase stock back
        cursor.execute("UPDATE books SET stock_count = stock_count + 1 WHERE id = ?", (book_id,))
        conn.commit()
        print(f"Success: Loan ID {loan_id} returned. Stock updated.")
    else:
        print("Error: Loan record not found or already returned.")
        
    conn.close()

def add_member(name, surname, email):
    """Registers a new member to the library."""
    conn = sqlite3.connect('library_project.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO members (name, surname, email) VALUES (?, ?, ?)", 
                       (name, surname, email))
        conn.commit()
        print(f"Member {name} {surname} added successfully.")
    except sqlite3.IntegrityError:
        print("Error: This email is already registered.")
    finally:
        conn.close()

def low_stock_alert(threshold=3):
    """Lists books that have stock levels below the given threshold."""
    conn = sqlite3.connect('library_project.db')
    cursor = conn.cursor()
    cursor.execute("SELECT title, stock_count FROM books WHERE stock_count <= ?", (threshold,))
    results = cursor.fetchall()
    
    print(f"\n--- Low Stock Alert (Threshold: {threshold}) ---")
    if not results:
        print("All books have sufficient stock.")
    else:
        for title, count in results:
            print(f"WARNING: '{title}' only has {count} items left")
    conn.close()

#To show the list of books
def list_books():
    connection = sqlite3.connect('library_project.db')
    cursor = connection.cursor()
    
    # SQL SELECT command to join books and authors for a better report
    query = """
    SELECT books.id, books.title, authors.name, authors.surname, books.stock_count 
    FROM books 
    LEFT JOIN authors ON books.author_id = authors.id
    """
    
    cursor.execute(query)
    books = cursor.fetchall()
    
    if not books:
        print("\nNo books found in the library.")
    else:
        print("\n" + "="*60)
        print(f"{'ID':<3} | {'Title':<25} | {'Author':<15} | {'Stock':<5}")
        print("-" * 60)
        for b in books:
            author_full_name = f"{b[2]} {b[3]}" if b[2] else "Unknown"
            print(f"{b[0]:<3} | {b[1]:<25} | {author_full_name:<15} | {b[4]:<5}")
        print("="*60)
    
    connection.close()

# Create tables 
cursor.executescript("""
CREATE TABLE IF NOT EXISTS authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    surname TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author_id INTEGER,
    stock_count INTEGER DEFAULT 0,
    FOREIGN KEY (author_id) REFERENCES authors(id)
);
""")
connection.commit()

# Now try to fetch data
print("The database consist of these books:")
cursor.execute("SELECT * FROM books")
results = cursor.fetchall()

if not results:
    print("Database is ready but currently empty. Let's add the first book")
else:
    for row in results:
        print(row)

connection.close()

# Program running in a loop
while True:
    print(" Library Management System ")
    print("-"*30)
    print("1. Add Book")
    print("2. List All Books")
    print("3. Delete Book 0")
    print("4. Add New Member")
    print("5. Loan a Book")
    print("6. Return a Book")
    print("7. Show Active Loans")
    print("8. Low Stock Report")
    print("0. Exit")
    
    choice = input("\nSelect an option: ")

    if choice == '1':
        title = input("Title: ")
        a_id = int(input("Author ID: "))
        stock = int(input("Initial Stock: "))
        add_book(title, a_id, stock)
    elif choice == '2':
        list_books()
    elif choice == '4':
        m_name = input("Member Name: ")
        m_surname = input("Member Surname: ")
        m_email = input("Email: ")
        add_member(m_name, m_surname, m_email)
    elif choice == '5':
        b_id = int(input("Book ID to loan: "))
        m_id = int(input("Member ID: "))
        loan_book(b_id, m_id)
    elif choice == '6':
        l_id = int(input("Loan ID to return: "))
        return_book(l_id)
    elif choice == '8':
        low_stock_alert()
    elif choice == '0':
        break