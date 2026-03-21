import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
from models import Booking, Movie, User
from database import save_movies, save_bookings, save_users


class CustomerMixin:
# ---------------- MAIN CUSTOMER DASHBOARD ----------------
    def customer_frame(self):
        self.clear()
        
        # 1. Welcome Header
        tk.Label(self.root, text=f"WELCOME, {self.current_user.username.upper()}", 
                 font=("Arial", 30, "bold"), fg="white", bg="#1e1e1e").pack(pady=20)
        
        # 2. LOW BALANCE ALERT
        if self.current_user.balance < 5.00:
            alert_frame = tk.Frame(self.root, bg="#f44336", padx=10, pady=5)
            alert_frame.pack(pady=10)
            tk.Label(alert_frame, text="⚠️ LOW BALANCE: Please top up in 'My Account' before booking!", 
                     fg="white", bg="#f44336", font=("Arial", 10, "bold")).pack()

        # 3. LOYALTY PROGRESS HINT
        bookings_count = len(self.current_user.booking_history)
        next_discount = 3 - (bookings_count % 3)
        if bookings_count > 0:
            tk.Label(self.root, text=f"🌟 Book {next_discount} more movie(s) to get 10% Loyalty Discount!", 
                     fg="#ff9800", bg="#1e1e1e", font=("Arial", 10, "italic")).pack()

        # 4. Main Navigation Buttons
        self.create_button("🎬 View & Book Movies", self.show_movies_list, "#2196f3") 
        self.create_button("Cancel Ticket", self.cancel_ticket, "#f44336")
        
        # Dynamic Account Button: Changes color/text if balance is $0
        acc_color = "#ff9800" if self.current_user.balance > 0 else "#4caf50"
        acc_text = "My Account" if self.current_user.balance > 0 else "💳 Top Up Money"
        self.create_button(acc_text, self.account_frame, acc_color)
        
        tk.Label(self.root, text="", bg="#1e1e1e", height=1).pack() 
        self.create_button("LOGOUT", self.main_frame, "#9c27b0")
        # Inside book_step_4_seats...
        tk.Label(self.root, text=f"📍 HALL: {Movie.hall_number}", 
                font=("Arial", 14, "bold"), fg="white", bg="#333").pack(pady=5)
    def show_receipt(self, booking, hall_num):
        self.clear()
        
        # Receipt Container
        receipt_bg = "#ffffff" 
        frame = tk.Frame(self.root, bg=receipt_bg, padx=40, pady=40, relief="ridge", borderwidth=5)
        frame.pack(pady=50)

        # Header
        tk.Label(frame, text="🎟️ MOVIE TICKET", font=("Courier", 25, "bold"), fg="black", bg=receipt_bg).pack()
        tk.Label(frame, text="--------------------------", fg="black", bg=receipt_bg).pack()

        # Ticket Info Table-style
        info_font = ("Courier", 14)
        details = [
            ("MOVIE:", booking.movie_title.upper()),
            ("HALL:", f"HALL {hall_num}"),
            ("DATE:", booking.date),
            ("TIME:", booking.time),
            ("SEATS:", ", ".join(booking.seats)),
            ("TOTAL:", f"${booking.total_price:.2f}")
        ]

        for label, value in details:
            row = tk.Frame(frame, bg=receipt_bg)
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label, font=info_font, fg="gray", bg=receipt_bg, width=10, anchor="w").pack(side="left")
            tk.Label(row, text=value, font=info_font, fg="black", bg=receipt_bg, anchor="w").pack(side="left")

        tk.Label(frame, text="--------------------------", fg="black", bg=receipt_bg).pack(pady=10)
        tk.Label(frame, text="THANK YOU FOR YOUR PURCHASE!", font=("Courier", 10, "italic"), fg="black", bg=receipt_bg).pack()

        # Close button
        self.create_button("Print & Finish", self.customer_frame, "#4caf50")

    # ---------------- VIEW & BOOKING SCREENS ----------------
    def show_movies_list(self, filter_date=None, search_query=""):
        if self.current_user.balance <= 0:
            messagebox.showwarning("Balance Required", "Your balance is $0.00.\nPlease top up in 'My Account' first!")
            self.account_frame()
            return

        self.clear()
        tk.Label(self.root, text="Explore & Book", font=("Arial", 35, "bold"), fg="white", bg="#1e1e1e").pack(pady=10)

        # Filter Section
        filter_frame = tk.Frame(self.root, bg="#2e2e2e", pady=15, padx=20)
        filter_frame.pack(fill="x", padx=50, pady=10)
        
        tk.Label(filter_frame, text="Search:", fg="white", bg="#2e2e2e").grid(row=0, column=0)
        search_input = tk.Entry(filter_frame, font=("Arial", 12), width=20)
        search_input.insert(0, search_query)
        search_input.grid(row=0, column=1, padx=10)

        def apply_filters():
            self.show_movies_list(None, search_input.get().strip())

        tk.Button(filter_frame, text="Search", bg="#2196f3", command=apply_filters).grid(row=0, column=2)

        # Scrollable Area
        canvas = tk.Canvas(self.root, bg="#1e1e1e", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1e1e1e")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=750)
        canvas.configure(yscrollcommand=scrollbar.set)
        

        for m in self.movies:
            if search_query.lower() in m.title.lower():
                m_card = tk.Frame(scrollable_frame, bg="#333", pady=10, padx=20)
                m_card.pack(fill="x", pady=5, padx=20)


                # Info with Price
                info_frame = tk.Frame(m_card, bg="#333")
                info_frame.pack(side="left")
                tk.Label(info_frame, text=m.title, font=("Arial", 16, "bold"), fg="#4caf50", bg="#333").pack(anchor="w")
                tk.Label(info_frame, text=f"Price: ${m.price:.2f}/seat", font=("Arial", 10), fg="white", bg="#333").pack(anchor="w")
                
                tk.Button(m_card, text="Select Date", bg="#ff9800", command=lambda movie=m: self.book_step_2_date(movie)).pack(side="right")

        canvas.pack(side="left", fill="both", expand=True); scrollbar.pack(side="right", fill="y")
        self.create_button("Back", self.customer_frame, "#f44336")

    def book_step_2_date(self, movie):
        self.clear()
        
        # 1. Get Today's Date
        today = datetime.now().date()
        
        tk.Label(self.root, text=f"Available Dates for {movie.title}", 
                 font=("Arial", 25, "bold"), fg="white", bg="#1e1e1e").pack(pady=20)

        # 2. Get dates from the movie's specific schedule
        # We sort them so they appear in order (21, 22, 23...)
        scheduled_dates = sorted(movie.show_times.keys())

        found_date = False
        for d_str in scheduled_dates:
            # Convert the string date from database to a date object for comparison
            try:
                date_obj = datetime.strptime(d_str, "%d-%m-%Y").date()
                
                # ONLY show if the date is Today (21) or Future
                if date_obj >= today:
                    self.create_button(
                        d_str, 
                        lambda dt=d_str: self.book_step_3_time(movie, dt), 
                        "#ff9800"
                    )
                    found_date = True
            except ValueError:
                # If a date format in your database is wrong, skip it to prevent a crash
                continue

        # 3. Handle case where no future movies are scheduled
        if not found_date:
            tk.Label(self.root, text="No upcoming showtimes available.", 
                     fg="gray", bg="#1e1e1e").pack(pady=10)

        self.create_button("Back", self.show_movies_list, "#f44336")


    def book_step_3_time(self, movie, date):
        self.clear()
        tk.Label(self.root, text=f"{movie.title} | {date}", font=("Arial", 20, "bold"), fg="white", bg="#1e1e1e").pack(pady=20)
        for t in movie.show_times.get(date, []):
            self.create_button(t, lambda tm=t: self.book_step_4_seats(movie, date, tm), "#4caf50")
        self.create_button("Back", lambda: self.book_step_2_date(movie), "#f44336")

    def book_step_4_seats(self, movie, date, time):
        self.clear()
        slot_key = f"{date}|{time}"
        
        # 1. HEADER WITH HALL NUMBER
        # We fetch movie.hall (ensure this exists in Movie class)
        hall_info = getattr(movie, 'hall_number', 'N/A') 
        
        header_text = f"{movie.title}\nDate: {date} | Time: {time}"
        tk.Label(self.root, text=header_text, font=("Arial", 18, "bold"), fg="#4caf50", bg="#1e1e1e").pack(pady=5)
        
        # Display the Hall Number prominently
        tk.Label(self.root, text=f"📍 HALL: {hall_info}", font=("Arial", 14, "bold"), fg="white", bg="#333", padx=10).pack(pady=5)
        
        tk.Label(self.root, text=f"Price per seat: ${movie.price:.2f}", font=("Arial", 10), fg="white", bg="#1e1e1e").pack()

        # 2. SCREEN VISUAL
        # Making the screen look a bit more like a cinema screen
        tk.Label(self.root, text="__________________________________\nSCREEN", 
                 font=("Arial", 12, "bold"), bg="#1e1e1e", fg="gray", width=40).pack(pady=15)

        if slot_key not in movie.seats:
            movie.seats[slot_key] = {f"{chr(65+r)}{c}": False for r in range(movie.rows) for c in range(1, movie.cols + 1)}

        self.selected_seats = []
        seat_frame = tk.Frame(self.root, bg="#1e1e1e")
        seat_frame.pack(pady=10)

        def toggle(s_id, btn):
            if s_id in self.selected_seats:
                self.selected_seats.remove(s_id)
                btn.config(bg="#4caf50")
            else:
                self.selected_seats.append(s_id)
                btn.config(bg="yellow", fg="black")

        for r in range(movie.rows):
            for c in range(1, movie.cols + 1):
                s_id = f"{chr(65+r)}{c}"
                is_booked = movie.seats[slot_key].get(s_id, False)
                btn = tk.Button(seat_frame, text=s_id, width=4, 
                                bg="#f44336" if is_booked else "#4caf50", fg="white")
                if not is_booked: 
                    btn.config(command=lambda s=s_id, b=btn: toggle(s, b))
                else: 
                    btn.config(state="disabled")
                btn.grid(row=r, column=c, padx=3, pady=3)

        self.create_button("Confirm Booking", lambda: self.finalize_booking(movie, date, time), "#2196f3")
        self.create_button("Back", lambda: self.book_step_3_time(movie, date), "#f44336")

    

    def finalize_booking(self, movie, date, time):
        # 1. Check if seats are selected
        if not self.selected_seats: 
            messagebox.showwarning("Warning", "Please select at least one seat!")
            return
            
        # 2. we calculate the total price with potential discounts BEFORE confirming the booking
        base_total = len(self.selected_seats) * movie.price
        num_prev = len(self.current_user.booking_history)
        
        discount_rate = 0.0
        promo_name = "Standard"

        if num_prev == 0:
            discount_rate = 0.15
            promo_name = "New User (15% OFF)"
        elif (num_prev + 1) % 3 == 0:
            discount_rate = 0.10
            promo_name = "Loyalty Reward (10% OFF)"
        
        discount_amount = base_total * discount_rate
        final_price = base_total - discount_amount

        # 3. Check Balance
        if self.current_user.balance < final_price:
            messagebox.showerror("Balance Error", f"Total: ${final_price:.2f}\nBalance: ${self.current_user.balance:.2f}")
            return

        summary = (
            f"Movie: {movie.title}\nSeats: {', '.join(self.selected_seats)}\n"
            f"--------------------------\n"
            f"Original Total:  ${base_total:.2f}\n"
            f"Promo: {promo_name}\n"
            f"Discount:     -${discount_amount:.2f}\n"
            f"--------------------------\n"
            f"FINAL PRICE:    ${final_price:.2f}"
        )

        # 4. Confirm and Save
        if messagebox.askyesno("Confirm Purchase", summary):
            # Update values in memory
            self.current_user.balance -= final_price
            self.current_user.first_booking = False 
            
            slot_key = f"{date}|{time}"
            for s in self.selected_seats: 
                movie.seats[slot_key][s] = True
            
            # NOW create the booking,that final_price is defined!
            new_booking = Booking(
                self.current_user.username, 
                movie.title, 
                date, 
                time, 
                self.selected_seats, 
                final_price,
                movie.hall_number  
            )

            self.bookings.append(new_booking)
            self.current_user.booking_history.append(new_booking)
            self.current_user.payment_history.append(f"Paid ${final_price:.2f} for {movie.title}")
            
            # Save to files
            save_movies(self.movies)
            save_bookings(self.bookings)
            save_users(self.users)
            
            # Show Receipt
            self.show_receipt(new_booking, movie.hall_number)


    # ---------------- ACCOUNT & TOP-UP ----------------
    def account_frame(self):
        self.clear()
        tk.Label(self.root, text="YOUR ACCOUNT", font=("Arial", 30, "bold"), fg="white", bg="#1e1e1e").pack(pady=20)
        tk.Label(self.root, text=f"Current Balance: ${self.current_user.balance:.2f}", 
                 font=("Arial", 25, "bold"), fg="lightgreen", bg="#1e1e1e").pack(pady=10)

        topup_frame = tk.Frame(self.root, bg="#2e2e2e", pady=10, padx=20)
        topup_frame.pack(pady=20)
        tk.Label(topup_frame, text="Amount ($):", fg="white", bg="#2e2e2e").grid(row=0, column=0)
        amt_ent = tk.Entry(topup_frame, width=10)
        amt_ent.grid(row=0, column=1, padx=10)

        def do_topup():
            try:
                amt = float(amt_ent.get())
                if amt <= 0: raise ValueError
                self.current_user.balance += amt
                self.current_user.payment_history.append(f"Top-up: +${amt:.2f}")
                messagebox.showinfo("Success", f"Added ${amt:.2f}")
                self.account_frame()
            except ValueError: messagebox.showerror("Error", "Enter a valid amount")

        tk.Button(topup_frame, text="Top Up Now", bg="#4caf50", fg="white", command=do_topup).grid(row=0, column=2)

        self.create_button("Booking History", self.show_booking_history, "#2196f3")
        self.create_button("Payment History", self.show_payment_history, "#2196f3")
        self.create_button("Back", self.customer_frame, "#f44336")

    # ---------------- HISTORY & CANCEL ----------------
    def cancel_ticket(self):
        self.clear()
        tk.Label(self.root, text="Cancel Booking", font=("Arial", 25, "bold"), fg="white", bg="#1e1e1e").pack(pady=20)
        for i, b in enumerate(self.current_user.booking_history):
            self.create_button(f"Cancel {b.movie_title} ({b.date})", lambda idx=i: self.do_cancel(idx), "#f44336")
        self.create_button("Back", self.customer_frame, "#9c27b0")


    def do_cancel(self, index):
        booking = self.current_user.booking_history[index]
        
        # --- 2 MINUTE VALIDATION ---
        now = datetime.now()
        time_diff = (now - booking.booking_time).total_seconds()
        
        if time_diff > 120:  
            messagebox.showerror("Timeout", "Cancellations are only allowed within 2 minutes of booking.")
            return 

        # 1. Remove from User's history and Global list
        b = self.current_user.booking_history.pop(index)
        
        # This removes the exact same booking object from the global list
        if b in self.bookings:
            self.bookings.remove(b)
        # ---------------------------

        self.current_user.balance += b.total_price
        self.current_user.payment_history.append(f"Refund: +${b.total_price:.2f}")

        # 2. Update Seat Availability
        slot_key = f"{b.date}|{b.time}"
        for m in self.movies:
            if m.title == b.movie_title:
                if slot_key in m.seats:
                    for s in b.seats: 
                        m.seats[slot_key][s] = False 

        # 3. SAVE EVERYTHING 
        save_movies(self.movies)
        save_users(self.users)
        save_bookings(self.bookings)
        
        messagebox.showinfo("Cancelled", "Refunded successfully!")
        self.customer_frame()
        
    def show_booking_history(self):
        self.clear()
        tk.Label(self.root, text="My Tickets", font=("Arial", 25), fg="white", bg="#1e1e1e").pack(pady=20)
        
        # Show the last 5 bookings
        for b in self.current_user.booking_history[-5:]:
            # Displaying Hall Number in the summary list
            history_text = f"🎬 {b.movie_title} | 📍 Hall {b.hall_number}\n📅 {b.date} at {b.time} | 💰 ${b.total_price:.2f}"
            
            tk.Label(self.root, text=history_text, fg="white", bg="#333", 
                    width=60, pady=10, justify="left").pack(pady=5)
                    
        self.create_button("Back", self.account_frame, "#f44336")

    def show_payment_history(self):
        self.clear()
        tk.Label(self.root, text="Transaction Log", font=("Arial", 25), fg="white", bg="#1e1e1e").pack(pady=20)
        for p in self.current_user.payment_history[-5:]:
            tk.Label(self.root, text=p, fg="lightgreen", bg="#333", width=50).pack(pady=2)
        self.create_button("Back", self.account_frame, "#f44336")
