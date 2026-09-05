import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog
from src.core import *
from src.ui.llm_api_tab import open_ai_dialog

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
        tk.Button(gen_frame_top, text="Edit", bg="#3c3f41", fg="#ffffff", command=self.edit_bf_gen).pack(side="left", padx=5)
        tk.Button(gen_frame_top, text="Upload", bg="#3c3f41", fg="#ffffff", command=self.upload_bf_gen).pack(side="left", padx=5)
        tk.Button(gen_frame_top, text="AI", bg="#3c3f41", fg="#ffffff", command=self.ask_ai_bf_gen).pack(side="left", padx=5)
        tk.Label(self.gen_frame, text="Arguments", bg="#333333", fg="#ffffff").pack(anchor="w", padx=5)
        self.args = tk.Text(self.gen_frame, height=1, width=30, bg="#111111", fg="#ffffff")
        self.args.pack(fill="x", padx=5, pady=5)
        gen_frame_low = tk.Frame(self.gen_frame, bg="#333333")
        gen_frame_low.pack(fill="x", pady=5)
        tk.Button(gen_frame_low, text="Run", bg="#3c3f41", fg="#ffffff", command=self.run_bf_gen_btn).pack(side="left", padx=5)
        tk.Button(gen_frame_low, text="View Input", bg="#3c3f41", fg="#ffffff", command=self.view_bf_gen_input).pack(side="left", padx=5)


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
        tk.Button(sol_frame_top, text="Edit", bg="#3c3f41", fg="#ffffff", command=self.edit_bf_sol).pack(side="left", padx=5)
        tk.Button(sol_frame_top, text="Upload", bg="#3c3f41", fg="#ffffff", command=self.upload_bf_sol).pack(side="left", padx=5)
        tk.Button(sol_frame_top, text="AI", bg="#3c3f41", fg="#ffffff", command=self.ask_ai_bf_sol).pack(side="left", padx=5)
        grader_header = tk.Frame(self.sol_frame, bg="#333333")
        grader_header.pack(fill="x", pady=2)
        tk.Label(grader_header, text="Grader", bg="#333333", fg="#ffffff").pack(side="left", padx=5)
        self.grader_var = tk.BooleanVar()
        tk.Checkbutton(grader_header, variable=self.grader_var, bg="#333333").pack(side="left")
        sol_grader_frame = tk.Frame(self.sol_frame, bg="#333333")
        sol_grader_frame.pack(fill="x", pady=5)
        self.grader_buttons = [
            tk.Button(sol_grader_frame, text="Edit", bg="#3c3f41", fg="#ffffff", command=self.edit_grader, state="disabled"),
            tk.Button(sol_grader_frame, text="Upload", bg="#3c3f41", fg="#ffffff", command=self.upload_grader, state="disabled"),
            tk.Button(sol_grader_frame, text="AI", bg="#3c3f41", fg="#ffffff", command=self.ask_ai_grader, state="disabled")
        ]
        for button in self.grader_buttons:
            button.pack(side="left", padx=5)
        self.grader_var.trace_add("write", self.update_buttons)
        sol_frame_low = tk.Frame(self.sol_frame, bg="#333333")
        sol_frame_low.pack(fill="x", pady=5)
        tk.Button(sol_frame_low, text="Run", bg="#3c3f41", fg="#ffffff", command=self.run_bf_sol_btn).pack(side="left", padx=5)
        tk.Button(sol_frame_low, text="View Output", bg="#3c3f41", fg="#ffffff", command=self.view_bf_sol_output).pack(side="left", padx=5)


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
            tk.Button(checker_frame, text="Edit", bg="#3c3f41", fg="#ffffff", command=self.edit_checker, state="disabled"),
            tk.Button(checker_frame, text="Upload", bg="#3c3f41", fg="#ffffff", command=self.upload_checker, state="disabled"),
            tk.Button(checker_frame, text="AI", bg="#3c3f41", fg="#ffffff", command=self.ask_ai_checker, state="disabled")
        ]
        for button in self.checker_buttons:
            button.pack(side="left", padx=5)
        self.checker_var.trace_add("write", self.update_buttons)
        scr_frame_low = tk.Frame(self.scr_frame, bg="#333333")
        scr_frame_low.pack(fill="x", pady=5)
        self.brute_score = tk.Label(scr_frame_low, text="", bg="#333333", fg="#ffffff")
        self.brute_score.pack(side="left", padx=5)
        tk.Button(scr_frame_low, text="Score", bg="#3c3f41", fg="#ffffff", command=self.run_score_btn).pack(side="left", padx=20)


        tests_cnt_frame = tk.Frame(self.runner_frame, bg="#333333")
        tests_cnt_frame.pack()
        tk.Label(tests_cnt_frame, text="# Tests", bg="#333333", fg="#ffffff", font=("TkDefaultFont",12)).pack(side="left", padx=5)
        self.test_cnt = tk.Text(tests_cnt_frame, height=1, width=5, bg="#111111", fg="#ffffff", font=("TkDefaultFont",12))
        self.test_cnt.pack(padx=5)
        bf_buttons_frame = tk.Frame(self.runner_frame, bg="#333333")
        bf_buttons_frame.pack(pady=10)
        self.bf_buttons = [
            tk.Button(bf_buttons_frame, text="Generate All", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont", 12), command=self.run_bf_all),
            tk.Button(bf_buttons_frame, text="Generate Inputs", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont", 12), command=self.run_bf_inputs),
            tk.Button(bf_buttons_frame, text="Generate Outputs", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont", 12), command=self.run_bf_outputs),
            tk.Button(bf_buttons_frame, text="Score", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont", 12), command=self.run_bf_runner_score)
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
        tree.pack(padx=20, pady=20, fill="both", expand=True)
        self.tree = tree
        error_area = tk.Label(self.runner_frame,font=("Arial", 11), bg="#111111",fg="#ff0000",text="Errors will be shown here.", anchor="nw")
        error_area.pack(padx=20, pady=20, fill="both", expand=True)
        self.error_area = error_area

    def clear_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def edit_bf_gen(self):
        open_in_gnome_text_editor(BF_GENERATOR_PATH)

    def upload_bf_gen(self):
        path = filedialog.askopenfilename(filetypes=[("C++ files", "*.cpp"), ("All files", "*.*")])
        if not path:
            return
        shutil.copy2(path, BF_GENERATOR_PATH)
        self.error_area.config(text=f"Imported {os.path.basename(path)} as BF generator.")

    def run_bf_gen_btn(self):
        args = self.args.get("1.0", "end")[:-1].strip()
        res = run_bf_generator(args)
        if not res["ok"]:
            self.error_area.config(text=res["message"])
        else:
            self.error_area.config(text="BF Generator OK")

    def view_bf_gen_input(self):
        if os.path.isfile("temp/bf_gen.out"):
            open_in_gnome_text_editor("temp/bf_gen.out")
        else:
            self.error_area.config(text="Input file not found.")

    def edit_bf_sol(self):
        open_in_gnome_text_editor(BF_SOLUTION_PATH)

    def upload_bf_sol(self):
        path = filedialog.askopenfilename(filetypes=[("C++ files", "*.cpp"), ("All files", "*.*")])
        if not path:
            return
        shutil.copy2(path, BF_SOLUTION_PATH)
        self.error_area.config(text=f"Imported {os.path.basename(path)} as BF solution.")

    def edit_grader(self):
        open_in_gnome_text_editor(GRADER_PATH)

    def upload_grader(self):
        path = filedialog.askopenfilename(filetypes=[("C++ files", "*.cpp"), ("All files", "*.*")])
        if not path:
            return
        shutil.copy2(path, GRADER_PATH)
        self.error_area.config(text=f"Imported {os.path.basename(path)} as grader.")

    def run_bf_sol_btn(self):
        meta = read_metadata()
        meta["grader"] = self.grader_var.get()
        meta["checker"] = self.checker_var.get()
        write_metadata(meta)
        res = run_bf_solution("temp/bf_gen.out")
        if not res["ok"]:
            self.error_area.config(text=res["message"])
        else:
            self.error_area.config(text="BF Solution OK")

    def view_bf_sol_output(self):
        if os.path.isfile("temp/bf_sol.out"):
            open_in_gnome_text_editor("temp/bf_sol.out")
        else:
            self.error_area.config(text="Output file not found.")

    def edit_checker(self):
        open_in_gnome_text_editor(CHECKER_PATH)

    def upload_checker(self):
        path = filedialog.askopenfilename(filetypes=[("C++ files", "*.cpp"), ("All files", "*.*")])
        if not path:
            return
        shutil.copy2(path, CHECKER_PATH)
        self.error_area.config(text=f"Imported {os.path.basename(path)} as checker.")

    def run_score_btn(self):
        meta = read_metadata()
        meta["grader"] = self.grader_var.get()
        meta["checker"] = self.checker_var.get()
        write_metadata(meta)
        checker_exe, checker_err = compile_checker_executable(meta)
        if checker_err:
            self.error_area.config(text=checker_err)
            return
        if checker_exe is None:
            checker_exe = "none"
        if not os.path.isfile("temp/bf_gen.out") or not os.path.isfile("temp/bf_sol.out"):
            self.error_area.config(text="Run BF Generator and Solution first.")
            return
        s = score("temp/bf_gen.out", "temp/bf_sol.out", "temp/bf_sol.out", checker_exe)
        self.brute_score.config(text=str(s))

    def run_bf_all(self):
        cnt_str = self.test_cnt.get("1.0", "end")[:-1].strip()
        if not cnt_str:
            self.error_area.config(text="Please specify number of tests.")
            return
        try:
            count = int(cnt_str)
        except ValueError:
            self.error_area.config(text="Invalid test count.")
            return
        self.clear_list()
        io_dir = "temp/io"
        if os.path.exists(io_dir):
            shutil.rmtree(io_dir)
        os.makedirs(io_dir, exist_ok=True)
        if compile_code(BF_GENERATOR_PATH, "none", "", "temp/bf_generator") != 1:
            err = get_last_compile_error()
            self.error_area.config(text=err if err else "Generator compilation failed (CE).")
            return
        meta = read_metadata()
        meta["grader"] = self.grader_var.get()
        meta["checker"] = self.checker_var.get()
        meta["test_cnt"] = count
        meta["bf_args"] = self.args.get("1.0", "end")[:-1].strip()
        write_metadata(meta)
        grader_cpp, grader_err = grader_compile_arg(meta)
        if grader_err:
            self.error_area.config(text=grader_err)
            return
        if compile_code(BF_SOLUTION_PATH, grader_cpp, "", "temp/bf_solution") != 1:
            err = get_last_compile_error()
            self.error_area.config(text=err if err else "Solution compilation failed (CE).")
            return
        checker_exe, checker_err = compile_checker_executable(meta)
        if checker_err:
            self.error_area.config(text=checker_err)
            return
        if checker_exe is None:
            checker_exe = "none"
        args = self.args.get("1.0", "end")[:-1].strip()
        for i in range(count):
            in_file = f"{io_dir}/{i+1}.in"
            out_file = f"{io_dir}/{i+1}.out"
            if run_gen("temp/bf_generator", args, in_file) != 1:
                self.tree.insert("", tk.END, values=(i+1, "FAIL", "Skipped", "-", "-", "-", "Generator RE"))
                continue
            run_res = run_exec("temp/bf_solution", in_file, out_file)
            st = "OK" if run_res[0] == 1 else "FAIL"
            s = score(in_file, out_file, out_file, checker_exe)
            self.tree.insert("", tk.END, values=(i+1, "OK", st, run_res[1], run_res[2], s, st))
        self.error_area.config(text="Run All completed.")

    def run_bf_inputs(self):
        cnt_str = self.test_cnt.get("1.0", "end")[:-1].strip()
        if not cnt_str:
            self.error_area.config(text="Please specify number of tests.")
            return
        try:
            count = int(cnt_str)
        except ValueError:
            self.error_area.config(text="Invalid test count.")
            return
        meta = read_metadata()
        meta["test_cnt"] = count
        meta["bf_args"] = self.args.get("1.0", "end")[:-1].strip()
        write_metadata(meta)
        self.clear_list()
        io_dir = "temp/io"
        if os.path.exists(io_dir):
            shutil.rmtree(io_dir)
        os.makedirs(io_dir, exist_ok=True)
        if compile_code(BF_GENERATOR_PATH, "none", "", "temp/bf_generator") != 1:
            err = get_last_compile_error()
            self.error_area.config(text=err if err else "Generator compilation failed (CE).")
            return
        args = self.args.get("1.0", "end")[:-1].strip()
        for i in range(count):
            in_file = f"{io_dir}/{i+1}.in"
            out_file = f"{io_dir}/{i+1}.out"
            if run_gen("temp/bf_generator", args, in_file) != 1:
                self.tree.insert("", tk.END, values=(i+1, "FAIL", "-", "-", "-", "-", "Generator RE"))
                continue
            if os.path.isfile(out_file):
                self.tree.insert("", tk.END, values=(i+1, "OK", "OK", "-", "-", "-", "OK"))
            else:
                self.tree.insert("", tk.END, values=(i+1, "OK", "-", "-", "-", "-", "-"))
        self.error_area.config(text=f"Generated {count} inputs in temp/io.")

    def run_bf_outputs(self):
        cnt_str = self.test_cnt.get("1.0", "end")[:-1].strip()
        count = 0
        if cnt_str:
            try:
                count = int(cnt_str)
            except ValueError:
                self.error_area.config(text="Invalid test count.")
                return
        self.clear_list()
        io_dir = "temp/io"
        os.makedirs(io_dir, exist_ok=True)
        meta = read_metadata()
        meta["grader"] = self.grader_var.get()
        meta["checker"] = self.checker_var.get()
        write_metadata(meta)
        grader_cpp, grader_err = grader_compile_arg(meta)
        if grader_err:
            self.error_area.config(text=grader_err)
            return
        if compile_code(BF_SOLUTION_PATH, grader_cpp, "", "temp/bf_solution") != 1:
            err = get_last_compile_error()
            self.error_area.config(text=err if err else "Solution compilation failed (CE).")
            return
        in_files = [f for f in os.listdir(io_dir) if f.endswith(".in")]
        test_count = count if count > 0 else len(in_files)
        for i in range(test_count):
            in_file = f"{io_dir}/{i+1}.in"
            out_file = f"{io_dir}/{i+1}.out"
            if not os.path.isfile(in_file):
                continue
            run_res = run_exec("temp/bf_solution", in_file, out_file)
            st = "OK" if run_res[0] == 1 else "FAIL"
            self.tree.insert("", tk.END, values=(i+1, "OK", st, run_res[1], run_res[2], "-", st))
        self.error_area.config(text="Outputs generated in temp/io.")

    def run_bf_runner_score(self):
        cnt_str = self.test_cnt.get("1.0", "end")[:-1].strip()
        count = 0
        if cnt_str:
            try:
                count = int(cnt_str)
            except ValueError:
                self.error_area.config(text="Invalid test count.")
                return
        meta = read_metadata()
        checker_exe, checker_err = compile_checker_executable(meta)
        if checker_err:
            self.error_area.config(text=checker_err)
            return
        if checker_exe is None:
            checker_exe = "none"
        io_dir = "temp/io"
        if not os.path.isdir(io_dir):
            self.error_area.config(text="temp/io directory not found.")
            return
        self.clear_list()
        in_files = [f for f in os.listdir(io_dir) if f.endswith(".in")]
        test_count = count if count > 0 else len(in_files)
        for i in range(test_count):
            in_file = f"{io_dir}/{i+1}.in"
            out_file = f"{io_dir}/{i+1}.out"
            if not os.path.isfile(in_file):
                continue
            if not os.path.isfile(out_file):
                self.tree.insert("", tk.END, values=(i+1, "OK", "-", "-", "-", "-", "-"))
                continue
            s = score(in_file, out_file, out_file, checker_exe)
            st = "OK" if s == 1.0 else "FAIL"
            self.tree.insert("", tk.END, values=(i+1, "OK", "OK", "-", "-", s, st))
        self.error_area.config(text="Scoring completed.")

    def update_buttons(self, *args):
        for button in self.checker_buttons:
            button["state"] = "normal" if self.checker_var.get() else "disabled"
        for button in self.grader_buttons:
            button["state"] = "normal" if self.grader_var.get() else "disabled"
        meta = read_metadata()
        meta["checker"] = self.checker_var.get()
        meta["grader"] = self.grader_var.get()
        write_metadata(meta)

    def update_ui(self):
        meta = read_metadata()
        is_grader = meta.get("grader", False)
        is_checker = meta.get("checker", False)
        if self.grader_var.get() != is_grader:
            self.grader_var.set(is_grader)
        if self.checker_var.get() != is_checker:
            self.checker_var.set(is_checker)
        for button in self.checker_buttons:
            button["state"] = "normal" if self.checker_var.get() else "disabled"
        for button in self.grader_buttons:
            button["state"] = "normal" if self.grader_var.get() else "disabled"
        if meta.get("bf_args"):
            self.args.delete("1.0", tk.END)
            self.args.insert("1.0", str(meta.get("bf_args")))
        if meta.get("test_cnt"):
            self.test_cnt.delete("1.0", tk.END)
            self.test_cnt.insert("1.0", str(meta.get("test_cnt")))

    def ask_ai_bf_gen(self):
        def wrapper(user_prompt):
            meta = read_metadata()
            ctx = (
                f"Problem Title: {meta.get('title', '')}\n"
                f"Description: {meta.get('description', '')}\n"
                f"Input Format: {meta.get('input', '')}\n"
                f"Constraints: {meta.get('constraints', '')}\n"
            )
            return (
                "You are an assistant for competitive programming problem setters.\n"
                "Problem Information:\n" + ctx + "\n"
                "User Request:\n" + user_prompt + "\n\n"
                "Write a C++ test generator that accepts command line arguments (argc, argv) and prints the test input to stdout.\n"
                "Output ONLY valid C++ code, without markdown code fences."
            )

        def on_success(res_text):
            os.makedirs(os.path.dirname(BF_GENERATOR_PATH), exist_ok=True)
            with open(BF_GENERATOR_PATH, "w", encoding="utf-8") as f:
                f.write(res_text)
            self.error_area.config(text="BF Generator generated via AI.")

        open_ai_dialog(
            self.frame,
            "AI BF Generator",
            "Enter prompt for Brute Force Generator (C++):",
            wrapper,
            on_success
        )

    def ask_ai_bf_sol(self):
        def wrapper(user_prompt):
            meta = read_metadata()
            ctx = (
                f"Problem Title: {meta.get('title', '')}\n"
                f"Description: {meta.get('description', '')}\n"
                f"Input Format: {meta.get('input', '')}\n"
                f"Output Format: {meta.get('output', '')}\n"
                f"Constraints: {meta.get('constraints', '')}\n"
            )
            return (
                "You are an assistant for competitive programming problem setters.\n"
                "Problem Information:\n" + ctx + "\n"
                "User Request:\n" + user_prompt + "\n\n"
                "Write a simple, correct Brute Force C++ solution to serve as an oracle for small test cases.\n"
                "Output ONLY valid C++ code, without markdown code fences."
            )

        def on_success(res_text):
            os.makedirs(os.path.dirname(BF_SOLUTION_PATH), exist_ok=True)
            with open(BF_SOLUTION_PATH, "w", encoding="utf-8") as f:
                f.write(res_text)
            self.error_area.config(text="BF Solution generated via AI.")

        open_ai_dialog(
            self.frame,
            "AI BF Solution",
            "Enter prompt for Brute Force Solution (C++):",
            wrapper,
            on_success
        )

    def ask_ai_grader(self):
        def wrapper(user_prompt):
            meta = read_metadata()
            ctx = (
                f"Problem Title: {meta.get('title', '')}\n"
                f"Description: {meta.get('description', '')}\n"
                f"Input Format: {meta.get('input', '')}\n"
                f"Output Format: {meta.get('output', '')}\n"
            )
            return (
                "You are an assistant for competitive programming problem setters.\n"
                "Problem Information:\n" + ctx + "\n"
                "User Request:\n" + user_prompt + "\n\n"
                "Write a C++ grader implementation for this interactive / function problem.\n"
                "Output ONLY valid C++ code, without markdown code fences."
            )

        def on_success(res_text):
            os.makedirs(os.path.dirname(GRADER_PATH), exist_ok=True)
            with open(GRADER_PATH, "w", encoding="utf-8") as f:
                f.write(res_text)
            self.error_area.config(text="Grader generated via AI.")

        open_ai_dialog(
            self.frame,
            "AI Grader",
            "Enter prompt for Grader (C++):",
            wrapper,
            on_success
        )

    def ask_ai_checker(self):
        def wrapper(user_prompt):
            meta = read_metadata()
            ctx = (
                f"Problem Title: {meta.get('title', '')}\n"
                f"Description: {meta.get('description', '')}\n"
                f"Input Format: {meta.get('input', '')}\n"
                f"Output Format: {meta.get('output', '')}\n"
            )
            return (
                "You are an assistant for competitive programming problem setters.\n"
                "Problem Information:\n" + ctx + "\n"
                "User Request:\n" + user_prompt + "\n\n"
                "Write a C++ checker (accepting argc, argv: input, contestant.out, official.out, printing a score between 0.0 and 1.0 to stdout).\n"
                "Output ONLY valid C++ code, without markdown code fences."
            )

        def on_success(res_text):
            os.makedirs(os.path.dirname(CHECKER_PATH), exist_ok=True)
            with open(CHECKER_PATH, "w", encoding="utf-8") as f:
                f.write(res_text)
            self.error_area.config(text="Checker generated via AI.")

        open_ai_dialog(
            self.frame,
            "AI Checker",
            "Enter prompt for Checker (C++):",
            wrapper,
            on_success
        )