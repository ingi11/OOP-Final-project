# 🎬 CinemaX - Cinema Booking System

## 📌 Project Overview

CinemaX is a GUI-based movie booking management system built using Python and Tkinter. It allows users to register, log in, browse movies, and book tickets through an interactive interface.

The system also includes an admin panel to manage movies, monitor sales, and control system data.

This project demonstrates key programming concepts such as object-oriented design, file handling, user authentication, and GUI development.

---

## ▶️ Steps to Run the Code

1. Make sure Python is installed on your computer
2. Download or clone this project
3. Open the project folder in a terminal or IDE (e.g., VS Code)
4. Run the program:

```bash
python main.py
```

5. Use the GUI interface to interact with the system

---

## ⚙️ Dependencies / Installation Instructions

* **Language:** Python 3.x
* **GUI Library:** Tkinter
* **Database:** JSON (for data storage)

Tkinter usually comes pre-installed. If not:

```bash
pip install tk
```

---

## 🚀 Features

### 👤 Customer

* Register and log in with secure password handling
* Browse and search available movies
* Book and cancel tickets (with automatic balance updates)
* View account details (balance, booking history, transactions)
* Top-up wallet balance
* Receive promo codes:

  * New users: 15% discount
  * Every 3rd booking: 10% discount

**Advanced Features:**

* Persistent accounts (data saved across sessions)
* Interactive seat selection (Available, Selected, Booked)
* Search and filter movies by title

---

### 🛠 Admin

* Secure admin login
* Add, update, and delete movies
* Manage movie details (title, price, seats, hall)
* View sales reports:

  * Total revenue
  * Popular movies
  * Seat occupancy

**Analytics Features:**

* Track total earnings and tickets sold


---

## 🧠 Concepts Used

* Object-Oriented Programming (OOP)
* File handling with JSON
* Password hashing for security
* Data structures (lists, dictionaries)
* Encapsulation and inheritance
* GUI development with Tkinter

---

## 📂 Project Structure

```bash
CinemaX/
│── main.py              # Entry point (runs the application)
│── auth.py              # Authentication and password handling
│── models.py            # User, Movie, Booking classes
│── database.py          # JSON data storage handling
│── gui_base.py          # Base GUI structure
│── gui_customer.py      # Customer interface
│── gui_admin.py         # Admin panel
```

---

## 🎁 Future Improvements

* Add online payment integration
* Improve UI/UX design
* Use a real database (e.g., MySQL)
* Enhance admin analytics and reporting

---

## 🔗 GitHub Link

https://github.com/ingi11/OOP-Final-project.git

---


