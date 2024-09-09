import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from threading import Thread
from plyer import notification
from datetime import datetime, timedelta
import time

# Create or connect to the database
connectdb = sqlite3.connect('habits.db')
c = connectdb.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY,
                name TEXT,
                description TEXT,
                frequency TEXT,
                last_notified TIMESTAMP
            )''')
connectdb.commit()
connectdb.close()

star_count = 0
current_habit_id = None

def update_star_display():
    star_label.config(text=f"⭐ Stars: {star_count}")

def reset_stars():
    global star_count
    star_count = 0
    update_star_display()

def add_star():
    global star_count
    star_count += 1
    update_star_display()

def add_habit():
    global current_habit_id
    name = name_entry.get()
    description = description_entry.get()
    frequency = frequency_combobox.get()

    if current_habit_id:
        conn = sqlite3.connect('habits.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE habits SET name = ?, description = ?, frequency = ? WHERE id = ?",
                       (name, description, frequency, current_habit_id))
        conn.commit()
        conn.close()
        current_habit_id = None
        messagebox.showinfo("Habit Tracker", "Habit updated successfully!")
    else:
        conn = sqlite3.connect('habits.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO habits (name, description, frequency, last_notified) VALUES (?, ?, ?, NULL)",
                       (name, description, frequency))
        conn.commit()
        conn.close()
        messagebox.showinfo("Habit Tracker", "Habit added successfully!")

    clear_entries()
    update_habit_list()  # Refresh the habit list after adding/updating

def clear_entries():
    global current_habit_id
    name_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)
    frequency_combobox.set('')  # Clear combobox selection
    current_habit_id = None

def delete_habit(habit_id):
    connectdb = sqlite3.connect('habits.db')
    cursor = connectdb.cursor()
    cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    connectdb.commit()
    connectdb.close()
    messagebox.showinfo("Habit Tracker", "Habit deleted successfully!")
    update_habit_list()

def update_habit(habit_id):
    global current_habit_id
    current_habit_id = habit_id

    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute("SELECT name, description, frequency FROM habits WHERE id = ?", (habit_id,))
    habit = c.fetchone()
    conn.close()

    name_entry.delete(0, tk.END)
    name_entry.insert(0, habit[0])

    description_entry.delete(0, tk.END)
    description_entry.insert(0, habit[1])

    frequency_combobox.set(habit[2])

    messagebox.showinfo("Habit Tracker", "Edit the habit details and click 'Update Habit' to save changes.")

def update_habit_list():
    for widget in habit_frame.winfo_children():
        widget.destroy()

    connectdb = sqlite3.connect('habits.db')
    c = connectdb.cursor()
    c.execute("SELECT id, name, description, frequency FROM habits")
    rows = c.fetchall()
    connectdb.close()

    for row in rows:
        habit_id = row[0]
        habit_text = f"{row[1]} - {row[2]} ({row[3]})"

        habit_item_frame = tk.Frame(habit_frame, bd=1, relief=tk.SOLID, padx=5, pady=5)
        habit_item_frame.pack(fill=tk.X, padx=5, pady=2)

        habit_label = tk.Label(habit_item_frame, text=habit_text, anchor="w")
        habit_label.pack(side=tk.LEFT, padx=5)

        delete_button = ttk.Button(habit_item_frame, text="🗑", width=2, command=lambda r=habit_id: delete_habit(r))
        delete_button.pack(side=tk.RIGHT, padx=5)

        update_button = ttk.Button(habit_item_frame, text="✏️", width=2, command=lambda r=habit_id: update_habit(r))
        update_button.pack(side=tk.RIGHT, padx=5)

def check_and_send_notifications():
    while True:
        current_time = datetime.now()

        conn = sqlite3.connect('habits.db')
        c = conn.cursor()
        c.execute("SELECT id, name, frequency, last_notified FROM habits")
        habits = c.fetchall()
        conn.close()

        for habit in habits:
            habit_id = habit[0]
            name = habit[1]
            frequency = habit[2].lower()
            last_notified = habit[3]

            if last_notified is None:
                notify = True
            else:
                last_notified_time = datetime.strptime(last_notified, '%Y-%m-%d %H:%M:%S')
                if "hourly" in frequency:
                    next_notify_time = last_notified_time + timedelta(hours=1)
                elif "twice" in frequency:
                    next_notify_time = last_notified_time + timedelta(hours=12)
                elif "daily" in frequency:
                    next_notify_time = last_notified_time + timedelta(days=1)
                elif "weekly" in frequency:
                    next_notify_time = last_notified_time + timedelta(weeks=1)

                notify = current_time >= next_notify_time

            if notify:
                notification.notify(
                    title="Habit Reminder",
                    message=f"follow your habit: {name}",
                    timeout=8
                )

                conn = sqlite3.connect('habits.db')
                c = conn.cursor()
                c.execute("UPDATE habits SET last_notified = ? WHERE id = ?",
                          (current_time.strftime('%Y-%m-%d %H:%M:%S'), habit_id))
                conn.commit()
                conn.close()

                ask_if_followed_habit(name)

        time.sleep(120)

def ask_if_followed_habit(habit_name):
    answer = messagebox.askyesno("Habit Tracker", f"Did you follow your habit '{habit_name}' today?")
    if answer:
        add_star()
        messagebox.showinfo("Great Job!", "You earned a star!")
    else:
        reset_stars()
        messagebox.showinfo("Keep Going!", "Keep trying and you'll get better!")

root = tk.Tk()
root.title("Habit Tracker")
root.geometry('400x450')

habit_frame = tk.Frame(root)
habit_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

# Star label
star_label = tk.Label(root, text="⭐ Stars: 0", font=("Helvetica", 14))
star_label.pack(pady=10)

add_button_frame = tk.Frame(root)
add_button_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=20, pady=10)

add_button = ttk.Button(add_button_frame, text="Add/Update Habit", command=add_habit)
add_button.pack(side=tk.RIGHT)

entry_frame = tk.Frame(root)
entry_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=20, pady=10)

tk.Label(entry_frame, text="Habit Name").grid(row=0, column=0)
tk.Label(entry_frame, text="Description").grid(row=1, column=0)
tk.Label(entry_frame, text="Frequency").grid(row=2, column=0)

name_entry = ttk.Entry(entry_frame)
description_entry = ttk.Entry(entry_frame)

frequency_combobox = ttk.Combobox(entry_frame, values=["Hourly", "Twice a Day", "Daily", "Weekly"], state="readonly")
frequency_combobox.set("Daily")

name_entry.grid(row=0, column=1)
description_entry.grid(row=1, column=1)
frequency_combobox.grid(row=2, column=1)

update_habit_list()

notification_thread = Thread(target=check_and_send_notifications, daemon=True)
notification_thread.start()

root.mainloop()