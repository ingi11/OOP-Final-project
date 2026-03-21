from datetime import datetime
from auth import hash_password


# ---------------- USER CLASSES ----------------
class User:

    def __init__(self, username, password, role):
        self.username = username
        self.password = password  # already hashed
        self.role = role

    def check_password(self, input_password):
        return self.password == hash_password(input_password)

    def get_role(self):
        return self.role


# ---------------- ADMIN ----------------
class Admin(User):
    def __init__(self):
        super().__init__("admin", hash_password("123"), "admin")

# ---------------- CUSTOMER ----------------

class Customer(User):
    def __init__(self, username, password):
        super().__init__(username, password, "customer")
        self.booking_history = []
        self.payment_history = []
        self.balance = 0.0 
        self.first_booking = True


# ---------------- MOVIE & BOOKING CLASSES ----------------
class Movie:
    # This __init__ now accepts 8 arguments (plus 'self' makes 9)
    def __init__(self, title, genre, price, rows, cols, show_times, seats=None, hall_number="1"):
        self.title = title
        self.genre = genre
        self.price = float(price)
        self.rows = int(rows)
        self.cols = int(cols)
        self.show_times = show_times  # This is a dictionary {date: [times]}
        self.seats = seats if seats else {} # This is a dictionary {date|time: {seat: status}}
        self.hall_number = hall_number

    def book_seats(self, time_slot, seats):
        for s in seats:
            if s not in self.seats[time_slot]:
                return False, f"Seat {s} does not exist"
            if self.seats[time_slot][s]:
                return False, f"Seat {s} already booked"
        for s in seats:
            self.seats[time_slot][s] = True
        return True, "Seats booked successfully"


class Booking:
    def __init__(self, username, movie_title, date, time, seats, total_price, hall_number="N/A", booking_time=None):
        self.username = username
        self.movie_title = movie_title
        self.date = date
        self.time = time
        self.seats = seats  # List of seats
        self.total_price = float(total_price)
        self.hall_number = hall_number 
        self.booking_time = booking_time if booking_time else datetime.now()