import tkinter as tk
from tkinter import messagebox
from gui_admin import Adminmixin
from gui_customer import CustomerMixin
from auth import hash_password, strong_password
from database import save_users
from database import initialize_files, load_users, load_movies, load_bookings
from models import Movie, Customer, Admin   


class MovieBookingGUI(Adminmixin, CustomerMixin):
    def __init__(self, root, movies, users, bookings):
        self.root = root
        
        # 1. Assign data passed from main.py
        self.movies = movies
        self.users = users
        self.bookings = bookings
        self.current_user = None

        # 2. Restore User Histories and Seat Maps
        self.restore_data_states()

        # 3. Launch Main Menu
        self.main_frame()

        # 4. Handle the "X" close button
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def restore_data_states(self):
        """Rebuilds the relationships between bookings, users, and movie seats."""
        for b in self.bookings:
            # Link booking to user object
            if b.username in self.users:
                user = self.users[b.username]
                if b not in user.booking_history:
                    user.booking_history.append(b)
                user.first_booking = False

            # Mark seats as occupied (True) in the movie objects
            movie = next((m for m in self.movies if m.title == b.movie_title), None)
            if movie:
                slot_key = f"{b.date}|{b.time}"
                if slot_key in movie.seats:
                    for seat_code in b.seats:
                        movie.seats[slot_key][seat_code] = True

    def on_closing(self):
        """Final save before exiting."""
        from database import save_movies, save_users, save_bookings
        try:
            save_movies(self.movies)
            save_users(self.users)
            save_bookings(self.bookings)
        except Exception as e:
            print(f"Error saving: {e}")
        self.root.destroy()

    def confirm_payment(self, total_price):
        """Helper to handle balance deduction and saving."""
        if self.current_user.balance >= total_price:
            self.current_user.balance -= total_price
            self.current_user.first_booking = False 
            save_users(self.users) 
            return True
        else:
            messagebox.showerror("Error", "Insufficient balance!")
            return False


    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ---------------- MAIN MENU ----------------
    def main_frame(self):
        self.clear()
        tk.Label(self.root, text="CinemaX", font=("Arial", 40, "bold"), fg="white", bg="#1e1e1e").pack(pady=150,padx=200)
        self.create_button("Login", self.login_frame, "#e77ab4")
        self.create_button("Register", self.register_frame, "#99c9ef")
        self.create_button("Exit", self.root.quit, "#f44336")

    # ---------------- BUTTON HELPER ----------------
    def create_button(self, text, command, color):
        btn = tk.Button(self.root, text=text, command=command, width=25, height=2, bg=color, fg="white", font=("Arial", 30, "bold"), relief="raised")
        btn.pack(pady=10)
        btn.bind("<Enter>", lambda e: btn.config(bg="orange"))
        btn.bind("<Leave>", lambda e: btn.config(bg=color))


# ---------------- TEMPORARY POPUP ----------------
    def temporary_popup(self, message, color, delay=1500):
            # Create a small window without title bar (overrideredirect)
            popup = tk.Toplevel(self.root)
            popup.overrideredirect(True)
            popup.configure(bg=color)
            
            # Center it on screen
            w, h = 400, 100
            x = (self.root.winfo_screenwidth() // 2) - (w // 2)
            y = (self.root.winfo_screenheight() // 2) - (h // 2)
            popup.geometry(f"{w}x{h}+{x}+{y}")
            
            tk.Label(popup, text=message, fg="white", bg=color, 
                    font=("Arial", 18, "bold")).pack(expand=True)
            self.root.after(delay, popup.destroy)

    # ---------------- LOGIN ----------------
    def login_frame(self):
        self.clear()
        tk.Label(self.root, text="Login", font=("Arial", 50, "bold"), fg="white", bg="#1e1e1e").pack(pady=15)
        tk.Label(self.root, text="Username:", font=("Arial", 30, "bold"), fg="white", bg="#1e1e1e").pack()
        username_entry = tk.Entry(self.root,width=30, font=("Arial", 20))
        username_entry.pack()
        tk.Label(self.root, text="Password:", font=("Arial", 30, "bold"), fg="white", bg="#1e1e1e").pack()
        password_entry = tk.Entry(self.root, show="*", width=30, font=("Arial", 20))
        password_entry.pack()

        def login_action():
            username = username_entry.get()
            password = password_entry.get()
            user = self.users.get(username)
            if user and user.check_password(password):
                self.current_user = user
                success_label = tk.Label(self.root, text="Login Successful!", fg="green", bg="#1e1e1e", font=("Arial", 20, "bold"))
                success_label.pack(pady=10)
                # Wait 1 second, then go to the appropriate dashboard
                if user.get_role() == "admin":
                    self.root.after(1000, self.admin_frame)
                else:
                    self.root.after(1000, self.customer_frame)
            else:
                messagebox.showerror("Login Fail1ed", "Invalid credentials")
        self.create_button("Login", login_action, "#e77ab4")
        self.create_button("Back", self.main_frame, "#f44336")


    # ---------------- REGISTER ----------------
    def register_frame(self):
        self.clear()
        tk.Label(self.root, text="Register", font=("Arial", 40, "bold"), fg="white", bg="#1e1e1e").pack(pady=15)
        tk.Label(self.root, text="Username:", font=("Arial", 30, "bold"), fg="white", bg="#1e1e1e").pack()
        username_entry = tk.Entry(self.root, font=("Arial", 20))
        username_entry.pack()
        tk.Label(self.root, text="Password:", font=("Arial", 30, "bold"), fg="white", bg="#1e1e1e").pack()
        password_entry = tk.Entry(self.root, show="*", font=("Arial", 20))
        password_entry.pack()


        def register_action():
            username = username_entry.get()
            password = password_entry.get()
            
            if not username or not password:
                messagebox.showerror("Error", "All fields are required!")
                return
            if username in self.users:
                messagebox.showerror("Error", "Username exists!")
                return
            if not strong_password(password):
                messagebox.showerror("Error", "Weak password! Use uppercase, lowercase, number, and special char.")
                return
                
            # 1. Hash the password
            hashed_password = hash_password(password)
            
            # 2. Create the Customer object
            # By default, Customer __init__ sets balance=100.0 and first_booking=True
            user = Customer(username, hashed_password)
            
            # 3. Add to the dictionary
            self.users[username] = user
            
            # 4. SAVE to users.txt (Now it saves name, hash, 100.0, True)
            save_users(self.users)
            
            self.current_user = user
            
            success_label = tk.Label(self.root, text="Registration Successful!", fg="green", bg="#1e1e1e", font=("Arial", 20, "bold"))
            success_label.pack(pady=10)
            
            # Wait 1 second before redirecting
            self.root.after(1000, self.customer_frame)

        self.create_button("Register", register_action, "#99c9ef")
        self.create_button("Back", self.main_frame, "#f44336")
