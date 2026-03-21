import tkinter as tk
from database import load_bookings, load_movies, load_users, initialize_files, save_movies, save_users, save_bookings
from gui_base import MovieBookingGUI

def main():
    # 1. Prepare Folders
    initialize_files()
    
    # 2. Load Data from Files
    movies = load_movies()
    users = load_users()
    bookings = load_bookings()

    # 3. Restore Seat Logic (The "Red Seats" fix),This marks seats as 'True' if a booking exists in the file
    for b in bookings:
        movie = next((m for m in movies if m.title == b.movie_title), None)
        if movie:
            slot_key = f"{b.date}|{b.time}"
            if slot_key in movie.seats:
                for s in b.seats: 
                    movie.seats[slot_key][s] = True

    # 4. Setup Window
    root = tk.Tk()
    root.title("CinemaX")
    root.geometry("1000x700") # Slightly larger for better view
    root.configure(bg="#1e1e1e")

    # 5. Initialize the App
    # We pass the data we just loaded directly to the GUI
    app = MovieBookingGUI(root, movies, users, bookings)

    # 6. Setup the EXIT SAVE protocol
    def on_closing():
        print("Saving all data before exit...")
        try:
            save_movies(app.movies)
            save_users(app.users)
            save_bookings(app.bookings)
            print("Save successful!")
        except Exception as e:
            print(f"Error during exit save: {e}")
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()

if __name__ == "__main__":
    main()