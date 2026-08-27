import tkinter as tk
from tkinter import ttk

class IOTab:
    def __init__(self, parent, main):
        self.main = main
        self.frame = tk.Frame(parent)
        self._build_ui()
        
    def _build_ui(self):
        self.button_frame = tk.Frame(self.frame, bg="#333333")
        self.list_frame = tk.Frame(self.frame, bg="#333333")
        self.button_frame.pack(side="left", fill="y")
        self.list_frame.pack(side="right", fill="both", expand=True)


        tk.Button(self.button_frame, text="Generate Inputs", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.yap).pack(padx=10, pady=5)
        tk.Button(self.button_frame, text="Generate Outputs", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.yap).pack(padx=10, pady=5)
        tk.Button(self.button_frame, text="Generate Both", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.yap).pack(padx=10, pady=5)
        tk.Button(self.button_frame, text="Save I/O Package", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.yap).pack(padx=10, pady=5)
        
        style = ttk.Style()
        style.configure(
            "Treeview",
            background="#111111",
            foreground="#ffffff",
            rowheight=20,
            fieldbackground="#111111",
            bordercolor="#333333",
            borderwidth=1,
            lightcolor="#333333",
            darkcolor="#333333"
        )
        style.configure(
            "Treeview.Heading",
            background="#333333",
            foreground="#ffffff",
            bordercolor="#3c3f41",
            relief="flat",
            font=("TkDefaultFont", 10, "bold")
        )
        columns = (
            "id",
            "subtask",
            "in_state",
            "out_state",
            "time",
            "mem",
            "status",
        )
        headings = (
            "#", 
            "Subtask",
            "Input",
            "Output",
            "Time (ms)",
            "Memory (KB)",
            "Status"
        )
        tree = ttk.Treeview(
            self.list_frame,
            columns=columns,
            show="headings",
            height=25
        )
        for i in range(len(columns)):
            tree.heading(columns[i], text=headings[i])
            tree.column(columns[i], width=len(headings[i])*15+5, anchor="center", stretch=False)
        tree.pack(pady=20, padx=20, fill="both", expand=True)
        error_area = tk.Label(self.button_frame,font=("Arial", 11), bg="#111111",fg="#ff0000",text="Errors will be shown here.", anchor="nw")
        error_area.pack(padx=20, pady=20, fill="both", expand=True)

    def update_buttons(self, *args):
        for button in self.checker_buttons:
            button["state"] = "normal" if self.checker_var.get() else "disabled"
        for button in self.grader_buttons:
            button["state"] = "normal" if self.grader_var.get() else "disabled"
    def yap(*args):
        print("hicbir ise yaramiyorum :(")
    def update_ui(self):
        print("IO Dab")