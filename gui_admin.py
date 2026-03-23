import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import json
from database import save_movies
from models import Movie



        
class Adminmixin:
    # ---------------- MAIN ADMIN DASHBOARD ----------------
    def admin_frame(self):
        self.clear()
        tk.Label(self.root, text="Admin Control Panel", font=("Arial", 40, "bold"), fg="white", bg="#1e1e1e").pack(pady=30)
        
        self.create_button("🎬 Manage Movies & Halls", lambda: self.show_movies_admin(""), "#2196f3")
        self.create_button("📊 View Sales Reports", self.show_sales_report, "#4caf50")
        self.create_button("Logout", self.main_frame, "#f44336")

    # ---------------- MOVIE MANAGEMENT LIST ----------------
    def show_movies_admin(self, search_query=""):
        self.clear()
        tk.Label(self.root, text="Movie Management", font=("Arial", 30, "bold"), fg="white", bg="#1e1e1e").pack(pady=10)
        
        # Top Controls
        top_controls = tk.Frame(self.root, bg="#1e1e1e")
        top_controls.pack(pady=10)
        
        tk.Label(top_controls, text="Search:", fg="white", bg="#1e1e1e", font=("Arial", 12)).pack(side="left")
        search_entry = tk.Entry(top_controls, font=("Arial", 14))
        search_entry.insert(0, search_query)
        search_entry.pack(side="left", padx=10)
        
        tk.Button(top_controls, text="Filter", command=lambda: self.show_movies_admin(search_entry.get())).pack(side="left", padx=5)
        tk.Button(top_controls, text="+ Add New Movie", bg="#4caf50", fg="white", font=("Arial", 12, "bold"), 
                  command=self.add_movie_form).pack(side="left", padx=20)

        # Movie List Container
        container = tk.Frame(self.root, bg="#1e1e1e")
        container.pack(pady=10, fill="both", expand=True)

        filtered_movies = [m for m in self.movies if m.title.lower().startswith(search_query.lower())]

        if not filtered_movies:
            tk.Label(container, text="--- No Movies Found ---", font=("Arial", 14), fg="gray", bg="#1e1e1e").pack(pady=20)

        for m in filtered_movies:
            m_frame = tk.Frame(container, bg="#333", pady=5, padx=20, highlightbackground="#555", highlightthickness=1)
            m_frame.pack(fill="x", pady=2, padx=50)
            
            # Show Hall Number and Price in the list
            tk.Label(m_frame, text=f"{m.title} (Hall {m.hall_number}) - ${m.price:.2f}", 
                     font=("Arial", 12, "bold"), fg="white", bg="#333").pack(side="left")
            
            tk.Button(m_frame, text="Delete", bg="#f44336", fg="white", 
                      command=lambda movie=m: self.confirm_delete_movie(movie)).pack(side="right", padx=5)
            
            tk.Button(m_frame, text="Edit Info", bg="#2196f3", fg="white", 
                      command=lambda movie=m: self.edit_movie_form(movie)).pack(side="right", padx=5)
            
            tk.Button(m_frame, text="Schedule", bg="#ff9800", fg="white", 
                      command=lambda movie=m: self.manage_movie_times(movie)).pack(side="right", padx=5)

        self.create_button("Back", self.admin_frame, "#9c27b0")

    # ---------------- ADD MOVIE FORM ----------------
    def add_movie_form(self):
        form = tk.Toplevel(self.root)
        form.title("Add New Movie")
        form.geometry("450x700")
        form.configure(bg="#2e2e2e")

        label_style = {"fg": "white", "bg": "#2e2e2e", "font": ("Arial", 11, "bold")}
        tk.Label(form, text="New Movie Details", font=("Arial", 18, "bold"), fg="#4caf50", bg="#2e2e2e").pack(pady=15)

        self.entries = {} 
        fields = [("Title:", "title"), ("Hall Number:", "hall"), ("Price ($):", "price"), ("Rows:", "rows"), ("Cols:", "cols")]

        for lbl, key in fields:
            tk.Label(form, text=lbl, **label_style).pack(anchor="w", padx=50)
            entry = tk.Entry(form, font=("Arial", 12), width=30)
            entry.pack(pady=5)
            self.entries[key] = entry 

        # Date & Times
        tk.Label(form, text="Date (DD-MM-YYYY):", **label_style).pack(anchor="w", padx=50)
        date_ent = tk.Entry(form, font=("Arial", 12), width=30)
        date_ent.insert(0, datetime.now().strftime("%d-%m-2026"))
        date_ent.pack(pady=5)
        
        tk.Label(form, text="Times (Comma separated):", **label_style).pack(anchor="w", padx=50)
        times_ent = tk.Entry(form, font=("Arial", 12), width=30)
        times_ent.pack(pady=5)

        def save_logic():
            try:
                title = self.entries["title"].get().strip()
                hall = self.entries["hall"].get().strip()
                price = float(self.entries["price"].get().strip())
                rows = int(self.entries["rows"].get().strip())
                cols = int(self.entries["cols"].get().strip())
                date = date_ent.get().strip()
                times_list = [t.strip() for t in times_ent.get().split(",") if t.strip()]

                if not title or not hall or not date or not times_list:
                    messagebox.showerror("Error", "All fields are required!", parent=form)
                    return

                new_movie = Movie(title, "General", price, rows, cols, {date: times_list}, {}, hall)
                
                for t in times_list:
                    slot_key = f"{date}|{t}"
                    new_movie.seats[slot_key] = {f"{chr(65+r)}{c}": False for r in range(rows) for c in range(1, cols + 1)}

                self.movies.append(new_movie)
                save_movies(self.movies)
                form.destroy()
                self.show_movies_admin("")
                
            except ValueError:
                messagebox.showerror("Error", "Check your numbers (Price/Rows/Cols)!", parent=form)

        tk.Button(form, text="Save Movie", bg="#4caf50", fg="white", font=("Arial", 12, "bold"), command=save_logic).pack(pady=20)

    # ---------------- EDIT MOVIE FORM ----------------
    def edit_movie_form(self, movie):
        form = tk.Toplevel(self.root)
        form.title(f"Edit {movie.title}")
        form.geometry("400x500")
        form.configure(bg="#2e2e2e")

        tk.Label(form, text=f"Update Details", font=("Arial", 18, "bold"), fg="#2196f3", bg="#2e2e2e").pack(pady=15)

        edit_entries = {}
        fields = [("Title:", "title", movie.title), ("Hall:", "hall", movie.hall_number), ("Price:", "price", str(movie.price))]

        for lbl, key, val in fields:
            tk.Label(form, text=lbl, fg="white", bg="#2e2e2e").pack(anchor="w", padx=50)
            entry = tk.Entry(form, font=("Arial", 12), width=25)
            entry.insert(0, val)
            entry.pack(pady=5)
            edit_entries[key] = entry

        def update_logic():
            try:
                movie.title = edit_entries["title"].get().strip()
                movie.hall_number = edit_entries["hall"].get().strip()
                movie.price = float(edit_entries["price"].get().strip())
                save_movies(self.movies)
                form.destroy()
                self.show_movies_admin("")
                messagebox.showinfo("Success", "Updated!")
            except ValueError:
                messagebox.showerror("Error", "Invalid Price!")

        tk.Button(form, text="Save Changes", bg="#4caf50", command=update_logic).pack(pady=20)
    

    def manage_movie_times(self, movie):
        """View and edit showtimes grouped by Date."""
        self.clear()
        tk.Label(self.root, text=f"Schedule: {movie.title}", font=("Arial", 25, "bold"), fg="#ff9800", bg="#1e1e1e").pack(pady=10)

        # --- ADD NEW DATE/TIME SECTION ---
        add_frame = tk.Frame(self.root, bg="#2e2e2e", pady=10)
        add_frame.pack(fill="x", padx=50)
        
        tk.Label(add_frame, text="Date (DD-MM-YYYY):", fg="white", bg="#2e2e2e").grid(row=0, column=0, padx=5)
        d_entry = tk.Entry(add_frame, width=12)
        d_entry.insert(0, datetime.now().strftime("%d-%m-2026"))
        d_entry.grid(row=0, column=1, padx=5)

        tk.Label(add_frame, text="New Time Slot:", fg="white", bg="#2e2e2e").grid(row=0, column=2, padx=5)
        t_entry = tk.Entry(add_frame, width=20)
        t_entry.grid(row=0, column=3, padx=5)

        def add_slot():
            d, t = d_entry.get().strip(), t_entry.get().strip()
            if d and t:
                if d not in movie.show_times: movie.show_times[d] = []
                if t not in movie.show_times[d]:
                    movie.show_times[d].append(t)
                    # Initialize seats for this specific Date|Time combo
                    movie.seats[f"{d}|{t}"] = {f"{chr(65+r)}{c}": False for r in range(movie.rows) for c in range(1, movie.cols + 1)}
                    save_movies(self.movies)
                    self.manage_movie_times(movie)
                else: messagebox.showwarning("Error", "Slot already exists")

        tk.Button(add_frame, text="Add Slot", bg="#4caf50", fg="white", command=add_slot).grid(row=0, column=4, padx=10)

        # --- SCROLLABLE LIST OF DATES ---
        canvas = tk.Canvas(self.root, bg="#1e1e1e", highlightthickness=0)
        vsb = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scroll_container = tk.Frame(canvas, bg="#1e1e1e")

        canvas.create_window((0, 0), window=scroll_container, anchor="nw", width=700)
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True, padx=50)
        vsb.pack(side="right", fill="y")

        # Sort dates so they appear in order
        for date in sorted(movie.show_times.keys()):
            date_box = tk.LabelFrame(scroll_container, text=f" Date: {date} ", fg="#2196f3", bg="#1e1e1e", font=("Arial", 12, "bold"))
            date_box.pack(fill="x", pady=10, padx=10)

            tk.Button(date_box, text="Delete All for this Date", bg="#f44336", fg="white", font=("Arial", 8),
                      command=lambda d=date: self.delete_entire_date(movie, d)).pack(anchor="e", padx=5)

            for slot in movie.show_times[date]:
                slot_row = tk.Frame(date_box, bg="#333", pady=2)
                slot_row.pack(fill="x", padx=5, pady=2)
                tk.Label(slot_row, text=slot, fg="white", bg="#333", width=30, anchor="w").pack(side="left", padx=10)
                tk.Button(slot_row, text="Remove", bg="#555", fg="white", 
                          command=lambda d=date, s=slot: self.remove_single_slot(movie, d, s)).pack(side="right")

        scroll_container.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        self.create_button("Back", lambda: self.show_movies_admin(""), "#f44336")

    def remove_single_slot(self, movie, date, slot):
        if messagebox.askyesno("Confirm", f"Remove {slot} on {date}?"):
            movie.show_times[date].remove(slot)
            if not movie.show_times[date]: del movie.show_times[date]
            key = f"{date}|{slot}"
            if key in movie.seats: del movie.seats[key]
            save_movies(self.movies)
            self.manage_movie_times(movie)


    def delete_entire_date(self, movie, date):
        if messagebox.askyesno("Confirm", f"Delete ALL showtimes for {date}?"):
            for slot in movie.show_times[date]:
                key = f"{date}|{slot}"
                if key in movie.seats: del movie.seats[key]
            del movie.show_times[date]
            save_movies(self.movies)
            self.manage_movie_times(movie)

    def confirm_delete_movie(self, movie):
        if messagebox.askyesno("Confirm", f"Delete '{movie.title}' entirely?"):
            self.movies.remove(movie)
            save_movies(self.movies)
            self.temporary_popup("Movie Deleted", "#f44336")
            self.show_movies_admin("")

    # ---------------- EDIT MOVIE FORM ----------------
    def edit_movie_form(self, movie):
        form = tk.Toplevel(self.root)
        form.title(f"Edit {movie.title}")
        form.geometry("400x500")
        form.configure(bg="#2e2e2e")

        tk.Label(form, text=f"Update Details", font=("Arial", 18, "bold"), fg="#2196f3", bg="#2e2e2e").pack(pady=15)

        edit_entries = {}
        fields = [("Title:", "title", movie.title), ("Hall:", "hall", movie.hall_number), ("Price:", "price", str(movie.price))]

        for lbl, key, val in fields:
            tk.Label(form, text=lbl, fg="white", bg="#2e2e2e").pack(anchor="w", padx=50)
            entry = tk.Entry(form, font=("Arial", 12), width=25)
            entry.insert(0, val)
            entry.pack(pady=5)
            edit_entries[key] = entry

        def update_logic():
            try:
                movie.title = edit_entries["title"].get().strip()
                movie.hall_number = edit_entries["hall"].get().strip()
                movie.price = float(edit_entries["price"].get().strip())
                save_movies(self.movies)
                form.destroy()
                self.show_movies_admin("")
                messagebox.showinfo("Success", "Updated!")
            except ValueError:
                messagebox.showerror("Error", "Invalid Price!")

        tk.Button(form, text="Save Changes", bg="#4caf50", command=update_logic).pack(pady=20)



    # ---------------- SALES REPORTS ----------------
    def show_sales_report(self, filter_date=None):
        self.clear()
        
        # 1. TOP NAV
        nav_bar = tk.Frame(self.root, bg="#1e1e1e")
        nav_bar.pack(fill="x", padx=20, pady=10)
        tk.Button(nav_bar, text="← Back", bg="#f44336", fg="white", command=self.admin_frame).pack(side="left")

        tk.Label(self.root, text="Sales Report", font=("Arial", 30, "bold"), fg="white", bg="#1e1e1e").pack()
        
        # 2. DATE FILTER
        filter_frame = tk.Frame(self.root, bg="#1e1e1e")
        filter_frame.pack(pady=10)
        d_entry = tk.Entry(filter_frame, width=15, font=("Arial", 12))
        d_entry.insert(0, filter_date if filter_date else datetime.now().strftime("%d-%m-2026"))
        d_entry.pack(side="left", padx=5)
        tk.Button(filter_frame, text="Filter", bg="#2196f3", fg="white", command=lambda: self.show_sales_report(d_entry.get().strip())).pack(side="left", padx=2)

        # 3. CALCULATIONS (Fixed Revenue Logic)
        # Instead of just relying on self.bookings, let's calculate from the actual seats
        total_rev = 0
        movie_stats = {} # To track which movie is popular

        for m in self.movies:
            movie_booked_count = 0
            for d, times in m.show_times.items():
                if filter_date and d != filter_date: continue
                for t in times:
                    slot_key = f"{d}|{t}"
                    if slot_key in m.seats:
                        # Count how many seats are True (Booked)
                        booked_in_slot = sum(1 for s in m.seats[slot_key].values() if s)
                        movie_booked_count += booked_in_slot
                        total_rev += (booked_in_slot * m.price)
            
            if movie_booked_count > 0:
                movie_stats[m.title] = movie_booked_count


        best_movie = max(movie_stats, key=movie_stats.get) if movie_stats else "None"

        # 4. OVERALL STATS BOX
        box = tk.Frame(self.root, bg="#333", padx=50, pady=20, highlightbackground="#4caf50", highlightthickness=2)
        box.pack(pady=10)
        tk.Label(box, text=f"Total Revenue: ${total_rev:.2f}", fg="#4caf50", bg="#333", font=("Arial", 20, "bold")).pack()
        tk.Label(box, text=f"Top Performer: {best_movie}", fg="#2196f3", bg="#333", font=("Arial", 16)).pack()

        # 5. NEW: MOVIE BREAKDOWN LIST (This shows exactly what you want)
        tk.Label(self.root, text="--- Movie Breakdown ---", fg="gray", bg="#1e1e1e", font=("Arial", 12, "italic")).pack(pady=10)
        
        breakdown_frame = tk.Frame(self.root, bg="#1e1e1e")
        breakdown_frame.pack(fill="both", expand=True, padx=50)


        for m_title, count in movie_stats.items():
            m_row = tk.Frame(breakdown_frame, bg="#2e2e2e", pady=5)
            m_row.pack(fill="x", pady=2)
            tk.Label(m_row, text=f"🎬 {m_title}", fg="white", bg="#2e2e2e", width=20, anchor="w").pack(side="left", padx=10)
            tk.Label(m_row, text=f"Tickets: {count}", fg="#ff9800", bg="#2e2e2e", width=15).pack(side="left")
            # Calculate local revenue for this movie
            for movie_obj in self.movies:
                if movie_obj.title == m_title:
                    tk.Label(m_row, text=f"Earned: ${count * movie_obj.price:.2f}", fg="#4caf50", bg="#2e2e2e").pack(side="right", padx=10)