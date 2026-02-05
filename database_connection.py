import sqlite3

# Connect to the database
connection = sqlite3.connect('library_project.db')
cursor = connection.cursor()

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
    """Deletes a book from the database using its unique ID."""
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

# To add the first book
add_book("Alice in Wonderland", 1, 10)

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
print("Checking for books...")
cursor.execute("SELECT * FROM books")
results = cursor.fetchall()

if not results:
    print("Database is ready but currently empty. Let's add the first book!")
else:
    for row in results:
        print(row)

connection.close()

# Program running in a loop
while True:
    print("\nLibrary System Menu")
    print("1. Add a New Book")
    print("2. List All Books")
    print("3. Exit")
    print("4. Delete a Book")
    
    choice = input("Select an option: ")

    if choice == '1':
        name = input("Book Title: ")
        author_id = int(input("Author ID: "))
        stock = int(input("Stock Count: "))
        add_book(name, author_id, stock) 
    elif choice == '2':
        list_books() 
    elif choice == '3':
        print("Closing the system")
        break
    elif choice == '4':
        book_to_delete = int(input("Enter the ID of the book you want to delete: "))
        delete_book(book_to_delete)3