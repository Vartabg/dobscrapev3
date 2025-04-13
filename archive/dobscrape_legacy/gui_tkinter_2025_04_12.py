# Copilot: Summarize what this file does and why it may have been replaced or archived.


import tkinter as tk
from tkinter import ttk

class DOBGuiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DOB Violations GUI (Tkinter)")
        self.root.geometry("800x600")
        self.root.configure(bg="white")

        self.main_frame = tk.Frame(root, bg="white")
        self.main_frame.pack(expand=True)

        self.init_ui()

    def init_ui(self):
        # Clear frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Create Start button
        self.start_button = tk.Button(
            self.main_frame,
            text="Start",
            font=("Helvetica", 20),
            bg="white",
            fg="#002B7F",
            width=10,
            height=2,
            relief="solid",
            bd=2,
            command=self.show_date_options
        )
        self.start_button.pack(expand=True)

    def show_date_options(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        options = [
            "Last 30 Days", "Last 3 Months", "Last 6 Months",
            "Past Year", "Past 2 Years", "All Since 2020"
        ]

        for label in options:
            btn = tk.Button(
                self.main_frame,
                text=label,
                font=("Helvetica", 16),
                width=25,
                height=2,
                relief="groove",
                bd=1,
                bg="white"
            )
            btn.pack(pady=8)

if __name__ == "__main__":
    root = tk.Tk()
    app = DOBGuiApp(root)
    root.mainloop()
