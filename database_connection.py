import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

#This block establishes the foundational relational database schema by creating tables for authors,
#categories, members, books, and loans
connection = sqlite3.connect('library_project.db')
cursor = connection.cursor()

cursor.executescript("""
CREATE TABLE IF NOT EXISTS authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE
);

CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    author_id INTEGER,
    category_id INTEGER,
    stock_count INTEGER DEFAULT 0,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER,
    member_id INTEGER,
    loan_date DATE DEFAULT (DATE('now')),
    return_date DATE,
    is_returned INTEGER DEFAULT 0,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
);
""")
connection.commit()

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

from datetime import datetime

def list_overdue_books(days_limit=15):
    """Lists books that have been borrowed for more than the allowed days."""
    conn = sqlite3.connect('library_project.db')
    cursor = conn.cursor()
    
    # SQL query to join loans, books, and members
    query = """
    SELECT 
        loans.id, 
        books.title, 
        members.name || ' ' || members.surname AS member_name,
        loans.loan_date
    FROM loans
    JOIN books ON loans.book_id = books.id
    JOIN members ON loans.member_id = members.id
    WHERE loans.is_returned = 0
    """
    
    cursor.execute(query)
    active_loans = cursor.fetchall()
    
    print(f"\nOverdue Books Report (Limit: {days_limit} days)")
    found_overdue = False
    
    for loan in active_loans:
        loan_id, title, member, loan_date_str = loan
        
        # Convert string date from DB to Python datetime object
        loan_date = datetime.strptime(loan_date_str, '%Y-%m-%d')
        today = datetime.now()
        
        # Calculate the difference in days
        diff = (today - loan_date).days
        
        if diff > days_limit:
            print(f"LOAN ID: {loan_id} | BOOK: {title} | MEMBER: {member} | DAYS LATE: {diff - days_limit}")
            found_overdue = True
            
    if not found_overdue:
        print("No overdue books found. Everything is on schedule")
        
    conn.close()

from datetime import datetime

def list_overdue_with_fines(days_limit=15, fine_per_day=5):
    """Lists overdue books and calculates the total fine for each."""
    conn = sqlite3.connect('library_project.db')
    cursor = conn.cursor()
    
    query = """
    SELECT 
        loans.id, 
        books.title, 
        members.name || ' ' || members.surname AS member_name,
        loans.loan_date
    FROM loans
    JOIN books ON loans.book_id = books.id
    JOIN members ON loans.member_id = members.id
    WHERE loans.is_returned = 0
    """
    
    cursor.execute(query)
    active_loans = cursor.fetchall()
    
    print(f"\n" + "="*75)
    print(f"{'LOAN ID':<8} | {'BOOK TITLE':<25} | {'MEMBER':<15} | {'FINE (TL)':<10}")
    print("-" * 75)
    
    found_overdue = False
    total_expected_fine = 0
    
    for loan in active_loans:
        loan_id, title, member, loan_date_str = loan
        
        # SQLite format: YYYY-MM-DD
        loan_date = datetime.strptime(loan_date_str, '%Y-%m-%d')
        today = datetime.now()
        
        diff_days = (today - loan_date).days
        
        # Calculate overdue days
        if diff_days > days_limit:
            overdue_days = diff_days - days_limit
            total_fine = overdue_days * fine_per_day
            total_expected_fine += total_fine
            
            print(f"{loan_id:<8} | {title[:25]:<25} | {member[:15]:<15} | {total_fine:<10.2f} TL")
            found_overdue = True
            
    if not found_overdue:
        print("No overdue books. No fines to collect")
    else:
        print("-" * 75)
        print(f"Total Collectable Fines: {total_expected_fine:.2f} TL")
        
    print("="*75)
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

def list_categories():
    """Fetches and displays all available categories."""
    conn = sqlite3.connect('library_project.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, category_name FROM categories")
    categories = cursor.fetchall()
    
    if not categories:
        print("\nNo categories found. Please add a category first")
        return False
    
    print("\n--- Available Categories ---")
    for cat_id, name in categories:
        print(f"ID: {cat_id} | Name: {name}")
    conn.close()
    return True

def add_category(name):
    """Adds a new category to the database."""
    conn = sqlite3.connect('library_project.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categories (category_name) VALUES (?)", (name,))
        conn.commit()
        print(f"Category '{name}' added successfully")
    except sqlite3.Error as e:
        print(f"Error adding category: {e}")
    finally:
         def safe_int_input(prompt):
              while True:
                   try:
                        return int(input(prompt))
                   except ValueError:
                        print("Invalid input. Please enter a numeric ID.")

def run_analysis():
    conn = sqlite3.connect('library_project.db')
    
    # Importing data into Pandas DataFrame
    query = """
    SELECT books.title, categories.category_name, loans.loan_date 
    FROM loans
    JOIN books ON loans.book_id = books.id
    JOIN categories ON books.category_id = categories.id
    """
    df = pd.read_sql_query(query, conn)
    
    if df.empty:
        print("\nNot enough data in the database to perform analysis.")
        conn.close()
        return

    # 1. Density Analysis: Distribution by Day of the Week
    df['loan_date'] = pd.to_datetime(df['loan_date'])
    df['day_name'] = df['loan_date'].dt.day_name()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_counts = df['day_name'].value_counts().reindex(day_order).fillna(0)

    # Visualization
    plt.figure(figsize=(10, 5))
    day_counts.plot(kind='bar', color='teal', edgecolor='black')
    plt.title('Daily Loan Density (Staffing Optimization Insight)')
    plt.xlabel('Day of the Week')
    plt.ylabel('Total Loans')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()
    
    # 2. ABC Analysis (Popularity/Cumulative Portion)
    print("\n" + "="*40)
    print(" ABC ANALYSIS (Book Popularity) ")
    print("="*40)
    
    book_stats = df['title'].value_counts().to_frame('loan_count')
    book_stats['cumulative_share'] = (book_stats['loan_count'].cumsum() / book_stats['loan_count'].sum()) * 100
    
    def classify_abc(row):
        if row['cumulative_share'] <= 70: return 'A (Very Popular)'
        elif row['cumulative_share'] <= 90: return 'B (Moderate)'
        else: return 'C (Slow Moving)'
        
    book_stats['class'] = book_stats.apply(classify_abc, axis=1)
    print(book_stats[['loan_count', 'class']])
    print("="*40)
    
    conn.close()

# Program running in a loop
while True:
    print(" Library Management System ")
    print("-"*30)
    print("1. List All Categories")
    print("2. List All Books")
    print("3. Add New Member")
    print("4. Add New Book")
    print("5. Delete Book ")
    print("6. Loan a Book")
    print("7. Return a Book")
    print("8. Show Active Loans")
    print("9. Low Stock Report")
    print("10. Show the Fine")
    print("11. Add New Category")
    print("12. Execute Engineering Analysis")
    print("0. Exit")
    
    choice = input("\nSelect an option: ")

    if choice == '1':
            # List All Categories
            list_categories()

    elif choice == '2':
            # List All Books
            list_books()

    elif choice == '3':
            # Add New Member
            m_name = input("Member Name: ")
            m_surname = input("Member Surname: ")
            m_email = input("Email: ")
            add_member(m_name, m_surname, m_email)

    elif choice == '4':
            # Add New Book
            print("\n--- Add New Book ---")
            title = input("Book Title: ")
            a_id = safe_int_input("Author ID: ")
            c_id = safe_int_input("Category ID: ")
            stock = safe_int_input("Initial Stock: ")
            add_book(title, a_id, c_id, stock)

    elif choice == '5':
            # Delete Book
            b_id = safe_int_input("Enter the ID of the book to delete: ")
            delete_book(b_id)

    elif choice == '6':
            # Loan a Book
            b_id = safe_int_input("Enter Book ID to loan: ")
            m_id = safe_int_input("Enter Member ID: ")
            loan_book(b_id, m_id)

    elif choice == '7':
            # Return a Book
            l_id = safe_int_input("Enter Loan ID to return: ")
            return_book(l_id)

    elif choice == '8':
            # Show Active Loans
            list_active_loans()

    elif choice == '9':
            # Low Stock Report
            low_stock_alert()

    elif choice == '10':
            # Show the Fine 
            limit_input = input("Enter day limit (default 15): ")
            limit = int(limit_input) if limit_input else 15
            fine_input = input("Enter daily fine amount (default 5 TL): ")
            daily_fine = float(fine_input) if fine_input else 5
            list_overdue_with_fines(limit, daily_fine)

    elif choice == '11':
            cat_name = input("Enter new Category Name : ")
            add_category(cat_name)

    elif choice == '12':
            print("\n[Executing Engineering Analytics...]")
            run_analysis()

    elif choice == '0':
            print("\nDatabase connection closed. Exiting the system...")
            connection.close()
            break

    else:
            print("\nInvalid selection. Please choose between 0 and 10.")


