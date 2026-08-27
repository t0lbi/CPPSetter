import tkinter as tk
from tkinter import ttk

class SubtaskTab:
    def __init__(self, parent, main):
        self.main = main
        self.frame = tk.Frame(parent)
        self._build_ui()
        
    def _build_ui(self):
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
        self.main_frame = tk.Frame(self.frame, bg="#333333", width=800)
        self.debug_frame = tk.Frame(self.frame, bg="#333333")
        self.main_frame.pack_propagate(False)
        self.main_frame.pack(side="left", fill="both")
        self.debug_frame.pack(side="right", fill="both", expand=True)


        tk.Label(self.main_frame, text="Name:", bg="#333333", fg="#ffffff", font=("TkDefaultFont",12)).pack(anchor="w", padx=5)
        self.subtask_name = tk.Text(self.main_frame, height=1, width=20, bg="#111111", fg="#ffffff", font=("TkDefaultFont",12))
        self.subtask_name.pack(padx=5, pady=5, anchor="w")
        tk.Button(self.main_frame, text="Create New Subtask", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.yap).pack(anchor="w", padx=5)


        subtasks=[]
        self.subtasks_combo = ttk.Combobox(self.main_frame, values=subtasks, state="readonly")
        self.subtasks_combo.pack(pady=10, padx=5, anchor="w")
        self.subtasks_combo.bind("<<ComboboxSelected>>", self.yap)

        tk.Button(self.main_frame, text="Delete Subtask", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.yap).pack(anchor="w", padx=5)
        tk.Label(self.main_frame, text="Generator:", bg="#333333", fg="#ffffff", font=("TkDefaultFont",12)).pack(anchor="w", padx=5)

        generators=[]
        self.generators_combo = ttk.Combobox(self.main_frame, values=generators, state="readonly")
        self.generators_combo.pack(pady=10, padx=5, anchor="w")
        self.generators_combo.bind("<<ComboboxSelected>>", self.yap)

        tk.Label(self.main_frame, text="Arguments:", bg="#333333", fg="#ffffff", font=("TkDefaultFont",12)).pack(anchor="w", padx=5)
        self.gen_args = tk.Text(self.main_frame, height=1, width=20, bg="#111111", fg="#ffffff", font=("TkDefaultFont",12))
        self.gen_args.pack(padx=5, pady=5, anchor="w")
        
        gen_runner_frame = tk.Frame(self.main_frame, bg="#333333")
        gen_runner_frame.pack(fill="x", pady=5)
        tk.Button(gen_runner_frame, text="Run", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.yap).pack(side="left", padx=5)
        tk.Button(gen_runner_frame, text="View Input", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.yap).pack(side="left", padx=5)
        tk.Button(self.main_frame, text="Add Generator", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.yap).pack(anchor="w", padx=5)

        columns = (
            "name",
            "args",
        )
        headings = (
            "Generator Name",
            "Arguments",
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

        tk.Button(self.main_frame, text="Delete Generator", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.yap).pack(side="left", padx=5)
        input_area = tk.Label(self.debug_frame,font=("Arial", 11), bg="#111111",fg="#ffffff",text="Errors will be shown here.", anchor="nw")
        input_area.pack(padx=20, pady=20, fill="both", expand=True)

    def update_buttons(self, *args):
        for button in self.checker_buttons:
            button["state"] = "normal" if self.checker_var.get() else "disabled"
        for button in self.grader_buttons:
            button["state"] = "normal" if self.grader_var.get() else "disabled"
    def yap(*args):
        print("hicbir ise yaramiyorum :(")
    def update_ui(self):
        print("Subdask Dab")