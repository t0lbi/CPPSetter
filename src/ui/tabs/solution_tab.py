import tkinter as tk
from tkinter import ttk

class SolutionTab:
    def __init__(self, parent, main):
        self.main = main
        self.frame = tk.Frame(parent)
        self._build_ui()
        
    def _build_ui(self):
        self.main_frame = tk.Frame(self.frame, bg="#333333")
        self.debug_frame = tk.Frame(self.frame, bg="#333333")
        self.main_frame.pack(side="left", fill="y")
        self.debug_frame.pack(side="right", fill="both", expand=True)


        tk.Label(self.main_frame, text="Solution", bg="#333333", fg="#ffffff", font=("TkDefaultFont",12)).pack(anchor="w", padx=5)
        soln_frame = tk.Frame(self.main_frame, bg="#333333")
        soln_frame.pack(fill="x", pady=5)
        tk.Button(soln_frame, text="Edit", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.yap).pack(side="left", padx=5)
        tk.Button(soln_frame, text="Upload", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.yap).pack(side="left", padx=5)
        tk.Button(soln_frame, text="AI", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.yap).pack(side="left", padx=5)
        

        tests_cnt_frame = tk.Frame(self.main_frame, bg="#333333")
        tests_cnt_frame.pack(anchor="nw")
        tk.Label(tests_cnt_frame, text="# Tests", bg="#333333", fg="#ffffff", font=("TkDefaultFont",12)).pack(side="left")
        self.test_cnt = tk.Text(tests_cnt_frame, height=1, width=5, bg="#111111", fg="#ffffff", font=("TkDefaultFont",12))
        self.test_cnt.pack()
        sol_buttons_frame = tk.Frame(self.main_frame, bg="#333333")
        sol_buttons_frame.pack(pady=10)
        self.bf_buttons = [
            tk.Button(sol_buttons_frame, text="Run All", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont", 12), command=self.yap),
            tk.Button(sol_buttons_frame, text="Generate Inputs", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont", 12), command=self.yap),
            tk.Button(sol_buttons_frame, text="Generate BF Outputs", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont", 12), command=self.yap),
            tk.Button(sol_buttons_frame, text="Generate Outputs", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont", 12), command=self.yap),
            tk.Button(sol_buttons_frame, text="Score", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont", 12), command=self.yap)
        ]
        for button in self.bf_buttons:
            button.pack(side="left", padx=5)


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
            "in_state",
            "jout_state",
            "out_state",
            "score",
            "time",
            "mem",
            "status"
        )
        headings = (
            "#", 
            "Input",
            "BF Output",
            "Output",
            "Score",
            "Time (ms)",
            "Memory (KB)",
            "Status"
        )
        tree = ttk.Treeview(
            self.main_frame,
            columns=columns,
            show="headings",
            height=25
        )
        for i in range(len(columns)):
            tree.heading(columns[i], text=headings[i])
            tree.column(columns[i], width=len(headings[i])*15+5, anchor="center", stretch=False)
        tree.pack(padx=20, pady=20, fill="both", expand=True)
        error_area = tk.Label(self.debug_frame,font=("Arial", 11), bg="#111111",fg="#ff0000",text="Errors will be shown here.", anchor="nw")
        error_area.pack(padx=20, pady=20, fill="both", expand=True)

    def update_buttons(self, *args):
        for button in self.checker_buttons:
            button["state"] = "normal" if self.checker_var.get() else "disabled"
        for button in self.grader_buttons:
            button["state"] = "normal" if self.grader_var.get() else "disabled"
    def yap(*args):
        print("hicbir ise yaramiyorum :(")