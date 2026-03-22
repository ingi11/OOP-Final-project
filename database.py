import json
import os
from datetime import datetime
from models import Admin, Customer, Movie, Booking



# --- USER DATA ---
def save_users(users):
    with open("users.txt", "w") as f:
        for u in users.values():
            if hasattr(u, 'role') and u.role == "customer":
                # Format: Username,Password,Balance,FirstBookingStatus
                f.write(f"{u.username},{u.password},{u.balance},{u.first_booking}\n")

def load_users():
    users = {"admin": Admin()} 
    if os.path.exists("users.txt"):
        with open("users.txt", "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 4:
                    u_name, p_hash, bal, is_first = parts[0], parts[1], parts[2], parts[3]
                    customer = Customer(u_name, p_hash) 
                    customer.balance = float(bal)
                    customer.first_booking = (is_first == "True") 
                    users[u_name] = customer
    return users

# --- MOVIE DATA (Including Hall Number) ---)
def load_movies():
    movies = []
    if os.path.exists("movies.json"):
        with open("movies.json", "r") as f:
            data = json.load(f)
            for d in data:
                # Create the movie object
                m = Movie(d['title'],d['hall_number'], d['price'], d['rows'], d['cols'], d['show_times'])
                # Restore the saved seat map
                m.seats = d['seats']
                movies.append(m)
    return movies


def save_movies(movie_list):
    data = []
    for m in movie_list:
        data.append({
            "title": m.title,
            "hall_number": m.hall_number,
            "price": m.price,
            "rows": m.rows,
            "cols": m.cols,
            "show_times": m.show_times,
            "seats": m.seats  # This saves every [XX] and [Available] seat
        })
    with open("movies.json", "w") as f:
        json.dump(data, f, indent=4)

def save_bookings(bookings):
    with open("bookings.txt","w") as f:
        for b in bookings:
            f.write(f"{b.username},{b.movie_title},{b.hall_number},{b.date},{b.time},{','.join(b.seats)},{b.total_price},{b.booking_time.timestamp()}\n")
def load_bookings():
    bookings = []
    if os.path.exists("bookings.txt"):
        with open("bookings.txt", "r") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                parts = line.split(",")
                if len(parts) >= 7:
                    try:
                        # parts[4:-2] handles one or multiple seats (e.g., A1,A2)
                        seats = parts[4:-2] 
                        b = Booking(parts[0], parts[1], parts[2], parts[3], seats, float(parts[-2]))
                        b.booking_time = datetime.fromtimestamp(float(parts[-1]))
                        bookings.append(b)
                    except (ValueError, IndexError):
                        continue
    return bookings


def initialize_files():
    # Auto-create movies.json if missing
    if not os.path.exists("movies.json"):
        
        with open("movies.json", "w") as f:
            json.dump([], f)

    # Auto-create bookings.txt if missing
    if not os.path.exists("bookings.txt"):
        with open("bookings.txt", "w") as f:
            pass