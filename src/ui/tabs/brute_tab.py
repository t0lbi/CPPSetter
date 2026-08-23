import tkinter as tk
from tkinter import ttk

class BruteTab:
    def __init__(self, parent, main):
        self.main = main
        self.frame = tk.Frame(parent)
        self._build_ui()
        
    def _build_ui(self):
        self.files_frame = tk.Frame(self.frame, bg="#333333")
        self.runner_frame = tk.Frame(self.frame, bg="#333333")
        self.files_frame.pack(side="left", fill="y")
        self.runner_frame.pack(side="right", fill="both", expand=True)
        self.gen_frame = tk.LabelFrame(
            self.files_frame,
            text="Brute Force Generator",
            bg="#333333",
            fg="#ffffff",
            padx=10,
            pady=5
        )
        self.gen_frame.pack(fill="x", padx=10, pady=10)
        gen_frame_top = tk.Frame(self.gen_frame, bg="#333333")
        gen_frame_top.pack(fill="x", pady=5)
        tk.Button(gen_frame_top, text="Edit", bg="#3c3f41", fg="#ffffff", command=self.yap).pack(side="left", padx=5)
        tk.Button(gen_frame_top, text="Upload", bg="#3c3f41", fg="#ffffff", command=self.yap).pack(side="left", padx=5)
        tk.Button(gen_frame_top, text="AI", bg="#3c3f41", fg="#ffffff", command=self.yap).pack(side="left", padx=5)
        tk.Label(self.gen_frame, text="Arguments", bg="#333333", fg="#ffffff").pack(anchor="w", padx=5)
        self.args = tk.Text(self.gen_frame, height=1, width=30, bg="#111111", fg="#ffffff")
        self.args.pack(fill="x", padx=5, pady=5)
        gen_frame_low = tk.Frame(self.gen_frame, bg="#333333")
        gen_frame_low.pack(fill="x", pady=5)
        tk.Button(gen_frame_low, text="Run", bg="#3c3f41", fg="#ffffff", command=self.yap).pack(side="left", padx=5)
        tk.Button(gen_frame_low, text="View Input", bg="#3c3f41", fg="#ffffff", command=self.yap).pack(side="left", padx=5)


        self.sol_frame = tk.LabelFrame(
            self.files_frame,
            text="Brute Force Solution",
            bg="#333333",
            fg="#ffffff",
            padx=10,
            pady=5
        )
        self.sol_frame.pack(fill="x", padx=10, pady=10)
        sol_frame_top = tk.Frame(self.sol_frame, bg="#333333")
        sol_frame_top.pack(fill="x", pady=5)
        tk.Button(sol_frame_top, text="Edit", bg="#3c3f41", fg="#ffffff", command=self.yap).pack(side="left", padx=5)
        tk.Button(sol_frame_top, text="Upload", bg="#3c3f41", fg="#ffffff", command=self.yap).pack(side="left", padx=5)
        tk.Button(sol_frame_top, text="AI", bg="#3c3f41", fg="#ffffff", command=self.yap).pack(side="left", padx=5)
        grader_header = tk.Frame(self.sol_frame, bg="#333333")
        grader_header.pack(fill="x", pady=2)
        tk.Label(grader_header, text="Grader", bg="#333333", fg="#ffffff").pack(side="left", padx=5)
        self.grader_var = tk.BooleanVar()
        tk.Checkbutton(grader_header, variable=self.grader_var, bg="#333333").pack(side="left")
        sol_grader_frame = tk.Frame(self.sol_frame, bg="#333333")
        sol_grader_frame.pack(fill="x", pady=5)
        self.grader_buttons = [
            tk.Button(sol_grader_frame, text="Edit", bg="#3c3f41", fg="#ffffff", command=self.yap, state="disabled"),
            tk.Button(sol_grader_frame, text="Upload", bg="#3c3f41", fg="#ffffff", command=self.yap, state="disabled"),
            tk.Button(sol_grader_frame, text="AI", bg="#3c3f41", fg="#ffffff", command=self.yap, state="disabled")
        ]
        for button in self.grader_buttons:
            button.pack(side="left", padx=5)
        self.grader_var.trace_add("write", self.update_buttons)
        sol_frame_low = tk.Frame(self.sol_frame, bg="#333333")
        sol_frame_low.pack(fill="x", pady=5)
        tk.Button(sol_frame_low, text="Run", bg="#3c3f41", fg="#ffffff", command=self.yap).pack(side="left", padx=5)
        tk.Button(sol_frame_low, text="View Output", bg="#3c3f41", fg="#ffffff", command=self.yap).pack(side="left", padx=5)


        self.scr_frame = tk.LabelFrame(
            self.files_frame,
            text="Scorer",
            bg="#333333",
            fg="#ffffff",
            padx=10,
            pady=5
        )
        self.scr_frame.pack(fill="x", padx=10, pady=10)
        checker_header = tk.Frame(self.scr_frame, bg="#333333")
        checker_header.pack(fill="x", pady=5)
        tk.Label(checker_header, text="Checker", bg="#333333", fg="#ffffff").pack(side="left", padx=5)
        self.checker_var = tk.BooleanVar()
        tk.Checkbutton(checker_header, variable=self.checker_var, bg="#333333").pack(side="left")
        checker_frame = tk.Frame(self.scr_frame, bg="#333333")
        checker_frame.pack(fill="x", pady=5)
        self.checker_buttons = [
            tk.Button(checker_frame, text="Edit", bg="#3c3f41", fg="#ffffff", command=self.yap, state="disabled"),
            tk.Button(checker_frame, text="Upload", bg="#3c3f41", fg="#ffffff", command=self.yap, state="disabled"),
            tk.Button(checker_frame, text="AI", bg="#3c3f41", fg="#ffffff", command=self.yap, state="disabled")
        ]
        for button in self.checker_buttons:
            button.pack(side="left", padx=5)
        self.checker_var.trace_add("write", self.update_buttons)
        scr_frame_low = tk.Frame(self.scr_frame, bg="#333333")
        scr_frame_low.pack(fill="x", pady=5)
        self.brute_score = tk.Label(scr_frame_low, text="", bg="#333333", fg="#ffffff")
        self.brute_score.pack(side="left", padx=5)
        tk.Button(scr_frame_low, text="Score", bg="#3c3f41", fg="#ffffff", command=self.yap).pack(side="left", padx=20)


        tests_cnt_frame = tk.Frame(self.runner_frame, bg="#333333")
        tests_cnt_frame.pack()
        tk.Label(tests_cnt_frame, text="# Tests", bg="#333333", fg="#ffffff", font=("TkDefaultFont",12)).pack(side="left", padx=5)
        self.test_cnt = tk.Text(tests_cnt_frame, height=1, width=5, bg="#111111", fg="#ffffff", font=("TkDefaultFont",12))
        self.test_cnt.pack(padx=5)
        bf_buttons_frame = tk.Frame(self.runner_frame, bg="#333333")
        bf_buttons_frame.pack(pady=10)
        self.bf_buttons = [
            tk.Button(bf_buttons_frame, text="Generate All", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont", 12), command=self.yap),
            tk.Button(bf_buttons_frame, text="Generate Inputs", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont", 12), command=self.yap),
            tk.Button(bf_buttons_frame, text="Generate Outputs", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont", 12), command=self.yap),
            tk.Button(bf_buttons_frame, text="Score", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont", 12), command=self.yap)
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
        columns = ("id", "in_state", "out_state", "time", "mem", "score", "status")
        headings = ("#", "Input", "Output", "Time (ms)", "Memory (KB)", "Score", "Status")
        tree = ttk.Treeview(
            self.runner_frame,
            columns=columns,
            show="headings",
            height=25
        )
        for i in range(len(columns)):
            tree.heading(columns[i], text=headings[i])
            tree.column(columns[i], width=len(headings[i])*15+5, anchor="center", stretch=False)
        tree.pack(pady=20)
        error_area = tk.Label(self.runner_frame,font=("Arial", 11), bg="#111111",fg="#ff0000",text="Errors will be shown here.", anchor="nw")
        error_area.pack(padx=20, pady=20, fill="both", expand=True)

    def update_buttons(self, *args):
        for button in self.checker_buttons:
            button["state"] = "normal" if self.checker_var.get() else "disabled"
        for button in self.grader_buttons:
            button["state"] = "normal" if self.grader_var.get() else "disabled"
    def yap(*args):
        print("hicbir ise yaramiyorum :(")