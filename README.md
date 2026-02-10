# Library Project

## Table of Contents

- [About the Project](#about-the-project)
- [Project_Scope](#project-scope)
- [Features](#features)
- [Database Design](#database-design)
- [Interactive Menu Overview](#interactive-menu-overview)
- [Future Improvements](#future-improvements)


## About the Project

The goal of this project is to model a basic library system using a normalized relational database. The system includes core entities such as books, authors, and users, and defines their relationships using primary and foreign keys.

The project emphasizes database schema design, data integrity, and clear visualization through an Entity–Relationship (ER) diagram.

---

## Project Scope

This project focuses on database design and core library operations rather than building a full-scale application.  
The primary goal is to demonstrate how relational data models can be translated into an interactive, menu-driven system.

## Features

- Relational database schema design  
- Primary key and foreign key relationships  
- SQL scripts for table creation  
- Python script for database connection  
- ER diagram for schema visualization  

---

## Database Design

The database structure is represented using an Entity–Relationship (ER) diagram, which illustrates the relationships between tables and provides a clear overview of the data model.

<img width="1106" height="665" alt="schema" src="https://github.com/user-attachments/assets/9f0784bc-482e-4cbe-a56f-3104506a6f87" />

## Interactive Menu Overview

The system is implemented as a menu-driven console application.  
When the Python script is executed, the user interacts with the database through the following options:

1. Add a new book  
2. Update book information  
3. Delete a book  
4. List all books  
5. Search for a book by title or author  
6. Register a new member  
7. Update member information  
8. Delete a member  
9. Issue a book to a member  
10. Return a book  
11. List all issued books  
12. Exit the application

The menu guides the user through common library tasks using simple input prompts, making the application easy to interact with from the terminal.

## Future Improvements

Potential extensions of the project include:

- Implementing full CRUD operations
- Improving input validation and error handling
- Introducing authentication and user roles
- Integrating a web-based interface
- Adding automated tests

This project was developed for educational purposes to reinforce database design principles.



