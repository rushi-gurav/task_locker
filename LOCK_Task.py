import psutil
import time
import tkinter as tk
from tkinter import simpledialog, messagebox
import threading

# Global variables
locked_apps = {}
lock_duration = 0

def get_running_apps():
    """Returns a list of currently running apps."""
    apps = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            apps.append(proc.info['name'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return list(set(apps))  # Remove duplicates

def monitor_apps():
    """Monitors and terminates locked apps during the lock duration."""
    global locked_apps
    end_time = time.time() + lock_duration * 60  # Convert minutes to seconds

    while time.time() < end_time:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] in locked_apps:
                try:
                    proc.terminate()  # Terminate the app
                    print(f"Terminated: {proc.info['name']}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        time.sleep(1)  # Check every second
    locked_apps.clear()
    print("Lock duration ended.")

def lock_apps(selected_apps, duration):
    """Locks the selected apps for the specified duration."""
    global locked_apps, lock_duration
    locked_apps = {app: True for app in selected_apps}
    lock_duration = duration

    # Start monitoring apps in a separate thread
    threading.Thread(target=monitor_apps, daemon=True).start()
    messagebox.showinfo("Success", "Selected apps are locked!")

def main():
    """Main function to run the GUI."""
    def on_submit():
        selected_apps = [apps_listbox.get(i) for i in apps_listbox.curselection()]
        if not selected_apps:
            messagebox.showwarning("Warning", "Please select at least one app.")
            return

        try:
            duration = int(simpledialog.askstring("Input", "Enter lock duration (minutes):"))
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Invalid duration input.")
            return

        if duration <= 0:
            messagebox.showerror("Error", "Duration must be greater than 0.")
            return

        lock_apps(selected_apps, duration)
        root.destroy()

    # GUI Setup
    root = tk.Tk()
    root.title("App Locker By Rushikesh Gurav")
    root.geometry("400x400")

    tk.Label(root, text="Select Apps to Lock", font=("Arial", 14)).pack(pady=10)

    # Get running apps and display in listbox
    running_apps = get_running_apps()
    apps_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=50, height=15)
    for app in running_apps:
        apps_listbox.insert(tk.END, app)
    apps_listbox.pack(pady=10)

    tk.Button(root, text="Submit", command=on_submit).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
