import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog
from src.core import (
    FULL_SOLUTION_PATH,
    BF_GENERATOR_PATH,
    BF_SOLUTION_PATH,
    open_in_gnome_text_editor,
    import_main_solution,
    compile_code,
    run_gen,
    run_exec,
    score,
    read_metadata,
    write_metadata,
    grader_compile_arg,
    compile_checker_executable,
    get_last_compile_error,
)
from src.ui.llm_api_tab import open_ai_dialog

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
        tk.Button(soln_frame, text="Edit", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.edit_full_solution).pack(side="left", padx=5)
        tk.Button(soln_frame, text="Upload", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.upload_full_solution).pack(side="left", padx=5)
        tk.Button(soln_frame, text="AI", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",12), command=self.ask_ai_solution).pack(side="left", padx=5)
        

        tests_cnt_frame = tk.Frame(self.main_frame, bg="#333333")
        tests_cnt_frame.pack(anchor="nw")
        tk.Label(tests_cnt_frame, text="# Tests", bg="#333333", fg="#ffffff", font=("TkDefaultFont",12)).pack(side="left")
        self.test_cnt = tk.Text(tests_cnt_frame, height=1, width=5, bg="#111111", fg="#ffffff", font=("TkDefaultFont",12))
        self.test_cnt.pack(side="left")
        tk.Label(tests_cnt_frame, text="Arguments", bg="#333333", fg="#ffffff", font=("TkDefaultFont",12)).pack(side="left", padx=(10, 0))
        self.args = tk.Text(tests_cnt_frame, height=1, width=20, bg="#111111", fg="#ffffff", font=("TkDefaultFont",12))
        self.args.pack(side="left", padx=5)
        self.gen_args = self.args
        sol_buttons_frame = tk.Frame(self.main_frame, bg="#333333")
        sol_buttons_frame.pack(pady=10)
        self.bf_buttons = [
            tk.Button(sol_buttons_frame, text="Run All", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont", 12), command=self.run_all_tests),
            tk.Button(sol_buttons_frame, text="Generate Inputs", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont", 12), command=self.gen_inputs),
            tk.Button(sol_buttons_frame, text="Generate BF Outputs", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont", 12), command=self.gen_bf_outputs),
            tk.Button(sol_buttons_frame, text="Generate Outputs", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont", 12), command=self.gen_main_outputs),
            tk.Button(sol_buttons_frame, text="Score", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont", 12), command=self.score_outputs)
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
        self.tree = tree
        error_area = tk.Label(self.debug_frame,font=("Arial", 11), bg="#111111",fg="#ff0000",text="Errors will be shown here.", anchor="nw")
        error_area.pack(padx=20, pady=20, fill="both", expand=True)
        self.error_area = error_area

    def clear_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def edit_full_solution(self):
        open_in_gnome_text_editor(FULL_SOLUTION_PATH)

    def upload_full_solution(self):
        path = filedialog.askopenfilename(filetypes=[("C++ files", "*.cpp"), ("All files", "*.*")])
        if not path:
            return
        shutil.copy2(path, FULL_SOLUTION_PATH)
        self.error_area.config(text=f"Imported {os.path.basename(path)} as full solution.")

    def run_all_tests(self):
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
            self.error_area.config(text=err if err else "Generator CE")
            return
        meta = read_metadata()
        grader_cpp, grader_err = grader_compile_arg(meta)
        if grader_err:
            self.error_area.config(text=grader_err)
            return
        if compile_code(BF_SOLUTION_PATH, grader_cpp, "", "temp/bf_solution") != 1:
            err = get_last_compile_error()
            self.error_area.config(text=err if err else "BF Solution CE")
            return
        if compile_code(FULL_SOLUTION_PATH, grader_cpp, "", "temp/main_solution") != 1:
            err = get_last_compile_error()
            self.error_area.config(text=err if err else "Main Solution CE")
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
            cout_file = f"{io_dir}/{i+1}.cout"
            out_file = f"{io_dir}/{i+1}.out"
            if run_gen("temp/bf_generator", args, in_file) != 1:
                self.tree.insert("", tk.END, values=(i+1, "FAIL", "-", "-", "-", "-", "-", "Generator RE"))
                continue
            bf_res = run_exec("temp/bf_solution", in_file, cout_file)
            bf_st = "OK" if bf_res[0] == 1 else "FAIL"
            main_res = run_exec("temp/main_solution", in_file, out_file)
            main_st = "OK" if main_res[0] == 1 else "FAIL"
            s = score(in_file, out_file, cout_file, checker_exe)
            st = "OK" if (bf_st == "OK" and main_st == "OK" and s == 1.0) else "FAIL"
            self.tree.insert("", tk.END, values=(i+1, "OK", bf_st, main_st, s, main_res[1], main_res[2], st))
        self.error_area.config(text="Run All completed in temp/io.")

    def gen_inputs(self):
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
        os.makedirs(io_dir, exist_ok=True)
        if compile_code(BF_GENERATOR_PATH, "none", "", "temp/bf_generator") != 1:
            err = get_last_compile_error()
            self.error_area.config(text=err if err else "Generator CE")
            return
        args = self.args.get("1.0", "end")[:-1].strip()
        for i in range(count):
            in_file = f"{io_dir}/{i+1}.in"
            cout_file = f"{io_dir}/{i+1}.cout"
            out_file = f"{io_dir}/{i+1}.out"
            if run_gen("temp/bf_generator", args, in_file) != 1:
                self.tree.insert("", tk.END, values=(i+1, "FAIL", "-", "-", "-", "-", "-", "Generator RE"))
                continue
            cout_st = "OK" if os.path.isfile(cout_file) else "-"
            out_st = "OK" if os.path.isfile(out_file) else "-"
            self.tree.insert("", tk.END, values=(i+1, "OK", cout_st, out_st, "-", "-", "-", "-"))
        self.error_area.config(text=f"Generated {count} inputs in temp/io.")

    def gen_bf_outputs(self):
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
        grader_cpp, grader_err = grader_compile_arg(meta)
        if grader_err:
            self.error_area.config(text=grader_err)
            return
        if compile_code(BF_SOLUTION_PATH, grader_cpp, "", "temp/bf_solution") != 1:
            err = get_last_compile_error()
            self.error_area.config(text=err if err else "BF Solution CE")
            return
        in_files = [f for f in os.listdir(io_dir) if f.endswith(".in")]
        test_count = count if count > 0 else len(in_files)
        for i in range(test_count):
            in_file = f"{io_dir}/{i+1}.in"
            cout_file = f"{io_dir}/{i+1}.cout"
            out_file = f"{io_dir}/{i+1}.out"
            if not os.path.isfile(in_file):
                continue
            run_res = run_exec("temp/bf_solution", in_file, cout_file)
            st = "OK" if run_res[0] == 1 else "FAIL"
            out_st = "OK" if os.path.isfile(out_file) else "-"
            self.tree.insert("", tk.END, values=(i+1, "OK", st, out_st, "-", run_res[1], run_res[2], st))
        self.error_area.config(text="BF outputs (.cout) generated in temp/io.")

    def gen_main_outputs(self):
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
        grader_cpp, grader_err = grader_compile_arg(meta)
        if grader_err:
            self.error_area.config(text=grader_err)
            return
        if compile_code(FULL_SOLUTION_PATH, grader_cpp, "", "temp/main_solution") != 1:
            err = get_last_compile_error()
            self.error_area.config(text=err if err else "Main Solution CE")
            return
        in_files = [f for f in os.listdir(io_dir) if f.endswith(".in")]
        test_count = count if count > 0 else len(in_files)
        for i in range(test_count):
            in_file = f"{io_dir}/{i+1}.in"
            cout_file = f"{io_dir}/{i+1}.cout"
            out_file = f"{io_dir}/{i+1}.out"
            if not os.path.isfile(in_file):
                continue
            run_res = run_exec("temp/main_solution", in_file, out_file)
            st = "OK" if run_res[0] == 1 else "FAIL"
            cout_st = "OK" if os.path.isfile(cout_file) else "-"
            self.tree.insert("", tk.END, values=(i+1, "OK", cout_st, st, "-", run_res[1], run_res[2], st))
        self.error_area.config(text="Main outputs (.out) generated in temp/io.")

    def score_outputs(self):
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
        if not os.path.isdir(io_dir):
            self.error_area.config(text="temp/io directory not found.")
            return
        meta = read_metadata()
        checker_exe, checker_err = compile_checker_executable(meta)
        if checker_err:
            self.error_area.config(text=checker_err)
            return
        if checker_exe is None:
            checker_exe = "none"
        in_files = [f for f in os.listdir(io_dir) if f.endswith(".in")]
        test_count = count if count > 0 else len(in_files)
        for i in range(test_count):
            in_file = f"{io_dir}/{i+1}.in"
            cout_file = f"{io_dir}/{i+1}.cout"
            out_file = f"{io_dir}/{i+1}.out"
            if not os.path.isfile(in_file):
                continue
            cout_st = "OK" if os.path.isfile(cout_file) else "-"
            out_st = "OK" if os.path.isfile(out_file) else "-"
            if not os.path.isfile(cout_file) or not os.path.isfile(out_file):
                self.tree.insert("", tk.END, values=(i+1, "OK", cout_st, out_st, "-", "-", "-", "-"))
                continue
            s = score(in_file, out_file, cout_file, checker_exe)
            st = "OK" if s == 1.0 else "FAIL"
            self.tree.insert("", tk.END, values=(i+1, "OK", "OK", "OK", s, "-", "-", st))
        self.error_area.config(text="Scoring completed.")

    def update_buttons(self, *args):
        pass

    def update_ui(self):
        meta = read_metadata()
        if meta.get("test_cnt"):
            self.test_cnt.delete("1.0", tk.END)
            self.test_cnt.insert("1.0", str(meta.get("test_cnt")))
        if meta.get("bf_args"):
            self.args.delete("1.0", tk.END)
            self.args.insert("1.0", str(meta.get("bf_args")))

    def ask_ai_solution(self):
        def wrapper(user_prompt):
            meta = read_metadata()
            ctx = (
                f"Problem Title: {meta.get('title', '')}\n"
                f"Description: {meta.get('description', '')}\n"
                f"Input: {meta.get('input', '')}\n"
                f"Output: {meta.get('output', '')}\n"
                f"Constraints: {meta.get('constraints', '')}\n"
            )
            return (
                "You are an expert competitive programming solver.\n"
                "Problem Information:\n" + ctx + "\n"
                "User Request:\n" + user_prompt + "\n\n"
                "Write a complete, optimal C++ solution.\n"
                "Output ONLY valid C++ code, without markdown code fences or other text."
            )

        def on_success(res_text):
            os.makedirs(os.path.dirname(FULL_SOLUTION_PATH), exist_ok=True)
            with open(FULL_SOLUTION_PATH, "w", encoding="utf-8") as f:
                f.write(res_text)
            self.error_area.config(text="Solution generated via AI.")

        open_ai_dialog(
            self.frame,
            "AI Solution Generator",
            "Enter prompt for C++ solution:",
            wrapper,
            on_success
        )