import tkinter as tk
from tkinter import ttk

class JudgerTab:
    def __init__(self, parent, main):
        self.main = main
        self.frame = tk.Frame(parent)
        self._build_ui()
        
    def _build_ui(self):
        self.button_frame = tk.Frame(self.frame, bg="#333333")
        self.list_frame = tk.Frame(self.frame, bg="#333333")
        self.button_frame.pack(side="left", fill="y")
        self.list_frame.pack(side="right", fill="both", expand=True)


        tk.Button(self.button_frame, text="Create Submission", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.yap).pack(padx=10, pady=5)
        self.submission_text = tk.Text(self.button_frame, height=1, width=16, bg="#111111", fg="#ffffff", font=("TkDefaultFont",13))
        self.submission_text.pack(fill="x", padx=5, pady=5)
        tk.Button(self.button_frame, text="Rename Submission", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.yap).pack(padx=10, pady=5)
        tk.Button(self.button_frame, text="Delete Submission", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.yap).pack(padx=10, pady=5)
        tk.Button(self.button_frame, text="Edit Submission", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.yap).pack(padx=10, pady=5)
        tk.Button(self.button_frame, text="Load Submission", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.yap).pack(padx=10, pady=5)
        tk.Button(self.button_frame, text="AI", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.yap).pack(padx=10, pady=5)
        tk.Button(self.button_frame, text="Judge Selected", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.yap).pack(padx=10, pady=5)
        tk.Button(self.button_frame, text="Judge All", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.yap).pack(padx=10, pady=5)
        tk.Button(self.button_frame, text="View Details", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.yap).pack(padx=10, pady=5)
        tk.Label(self.button_frame, text="Current I/O Package SHA: 23232...", bg="#333333", fg="#999999").pack(padx=10,pady=5)
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
            "name",
            "pass_cnt",
            "total",
            "time",
            "mem",
            "last_sha",
        )
        headings = (
            "#", 
            "Name",
            "Pass #",
            "Total",
            "Time (ms)",
            "Memory (KB)",
            "Last SHA"
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
        
    def update_buttons(self, *args):
        for button in self.checker_buttons:
            button["state"] = "normal" if self.checker_var.get() else "disabled"
        for button in self.grader_buttons:
            button["state"] = "normal" if self.grader_var.get() else "disabled"
    def yap(*args):
        print("hicbir ise yaramiyorum :(")