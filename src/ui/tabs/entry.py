import tkinter as tk
from tkinter import filedialog
from src.core import create_problem, valid_to_create, load_problem

class EntryTab:
    def __init__(self, parent, main):
        self.main = main
        self.parent = parent
        self.frame = tk.Frame(parent, bg="#333333")
        self._build_ui()
        
    def _build_ui(self):
        label = tk.Label(
            self.frame,
            text="Welcome to CPP Setter",
            bg="#333333",
            fg="#ffffff",
            font=("Arial", 30)
        )
        label.pack(pady=(50,0))
        subtitle_label = tk.Label(self.frame,
            text="Get started by selecting an action below.",
            font=("Arial", 14),
            bg="#333333",
            fg="#888888"
        )
        subtitle_label.pack(pady=(10, 40))
        self.create_button = tk.Button(
            self.frame,
            text="Create New Problem",
            font=("Arial",16),
            width=25,
            bg="#3c3f41",
            fg="#ffffff",
            command=self.open_create_problem_popup
        )
        self.create_button.pack(pady=(0,20))

        self.import_button = tk.Button(
            self.frame,
            text="Import Existing Problem",
            font=("Arial",16),
            width=25,
            bg="#3c3f41",
            fg="#ffffff",
            command=self.import_problem
        )
        self.import_button.pack()


    def open_create_problem_popup(self):
        popup = tk.Toplevel(self.parent, bg="#aaaaaa")
        popup.title("New Problem")
        popup.geometry("280x130")
        popup.resizable(False, False)

        text = tk.Label(popup, text="Problem Name:", bg="#aaaaaa")
        text.pack()
        text_var = tk.StringVar()
        text_area = tk.Entry(popup, width=20, font=("Arial", 14), textvariable=text_var)
        text_area.pack(padx=10,pady=6)
        text_area.focus()
        cancel_btn = tk.Button(
            popup,
            text="Cancel",
            command=popup.destroy
        )
        cancel_btn.pack(side="left", padx=10,pady=10)
        create_btn = tk.Button(
            popup,
            text="Create",
            command=lambda: self.new_problem(text_area.get(), popup)
        )
        create_btn.pack(side="right", padx=10,pady=10)

        def on_text_change(*args):
            if valid_to_create(text_var.get()):
                create_btn.config(state="normal")
            else:
                create_btn.config(state="disabled")
        text_var.trace_add("write", on_text_change)
        on_text_change()

    def new_problem(self, problem_name, popup):
        create_problem(problem_name)
        self.main.current_problem_name = problem_name
        self.main.update_nav()
        popup.destroy()

    def import_problem(self):
        path = filedialog.askdirectory()
        if not path:
            return
        load_problem(path)
        self.main.current_problem_name = path.split("/")[-1]
        self.main.update_nav()