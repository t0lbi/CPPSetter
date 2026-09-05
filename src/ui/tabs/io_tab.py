import os
import shutil
import tkinter as tk
from tkinter import ttk
from src.core import *

class IOTab:
    def __init__(self, parent, main):
        self.main = main
        self.frame = tk.Frame(parent)
        self.stats = {}
        self._build_ui()
        
    def _build_ui(self):
        self.button_frame = tk.Frame(self.frame, bg="#333333")
        self.list_frame = tk.Frame(self.frame, bg="#333333")
        self.button_frame.pack(side="left", fill="y")
        self.list_frame.pack(side="right", fill="both", expand=True)


        tk.Button(self.button_frame, text="Generate Inputs", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.generate_inputs).pack(padx=10, pady=5)
        tk.Button(self.button_frame, text="Generate Outputs", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.generate_outputs).pack(padx=10, pady=5)
        tk.Button(self.button_frame, text="Generate Both", bg="#3c3f41", fg="#ffffff", font=("TkDefaultFont",16), width=15, command=self.generate_both).pack(padx=10, pady=5)
        
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
        self.tree = tree
        error_area = tk.Label(self.button_frame,font=("Arial", 11), bg="#111111",fg="#ff0000",text="Errors will be shown here.", anchor="nw")
        error_area.pack(padx=20, pady=20, fill="both", expand=True)
        self.error_area = error_area

    def clear_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def generate_inputs(self):
        self.clear_list()
        self.stats = {}
        subtasks = list_subtasks()
        if not subtasks:
            self.error_area.config(text="No subtasks found.")
            return False
        io_dir = "temp/io"
        if os.path.exists(io_dir):
            shutil.rmtree(io_dir)
        os.makedirs(io_dir, exist_ok=True)
        test_id = 1
        for subtask in subtasks:
            dest_dirs = [f"{PROBLEM_DIR}{subtask}"]
            if hasattr(self.main, "current_problem_name") and self.main.current_problem_name:
                dest_dirs.append(f"temp/{self.main.current_problem_name}/{subtask}")
            dest_dirs.append(f"temp/{subtask}")
            for d in dest_dirs:
                d_in = f"{d}/input"
                if os.path.exists(d_in):
                    shutil.rmtree(d_in)
                os.makedirs(d_in, exist_ok=True)
            sub_in_dir = f"{io_dir}/{subtask}/input"
            sub_out_dir = f"{io_dir}/{subtask}/output"
            os.makedirs(sub_in_dir, exist_ok=True)
            os.makedirs(sub_out_dir, exist_ok=True)
            sub_meta = read_subtask_metadata(subtask)
            sub_test = 1
            for pack in sub_meta.get("data", []):
                gen_name = pack.get("generator")
                gen_cpp = GEN_DIR + gen_name + ".cpp"
                exe_path = f"temp/gen_{gen_name}"
                if os.path.isdir(exe_path):
                    shutil.rmtree(exe_path)
                if compile_code(gen_cpp, "none", "", exe_path) != 1:
                    err = get_last_compile_error()
                    self.error_area.config(text=err if err else f"Generator CE: {gen_name}")
                    return False
                for flag in pack.get("tests", []):
                    flat_in = f"{io_dir}/{test_id}.in"
                    sub_in = f"{sub_in_dir}/{sub_test}.in"
                    if run_gen(exe_path, flag, flat_in) != 1:
                        self.error_area.config(text=f"Error generating test {test_id} for {subtask}")
                        return False
                    shutil.copy2(flat_in, sub_in)
                    for d in dest_dirs:
                        shutil.copy2(flat_in, f"{d}/input/{sub_test}.in")
                    sub_test += 1
                    test_id += 1
        self.update_ui()
        self.error_area.config(text="Generated all inputs.")
        return True

    def generate_outputs(self):
        meta = read_metadata()
        grader_cpp, grader_err = grader_compile_arg(meta)
        if grader_err:
            self.error_area.config(text=grader_err)
            return False
        if compile_code(FULL_SOLUTION_PATH, grader_cpp, "", "temp/main_solution") != 1:
            err = get_last_compile_error()
            self.error_area.config(text=err if err else "Main solution CE")
            return False
        subtasks = list_subtasks()
        if not subtasks:
            self.error_area.config(text="No subtasks found.")
            return False
        io_dir = "temp/io"
        os.makedirs(io_dir, exist_ok=True)
        for subtask in subtasks:
            dest_dirs = [f"{PROBLEM_DIR}{subtask}"]
            if hasattr(self.main, "current_problem_name") and self.main.current_problem_name:
                dest_dirs.append(f"temp/{self.main.current_problem_name}/{subtask}")
            dest_dirs.append(f"temp/{subtask}")
            for d in dest_dirs:
                d_out = f"{d}/output"
                if os.path.exists(d_out):
                    shutil.rmtree(d_out)
                os.makedirs(d_out, exist_ok=True)
            sub_io_out = f"{io_dir}/{subtask}/output"
            if os.path.exists(sub_io_out):
                shutil.rmtree(sub_io_out)
            os.makedirs(sub_io_out, exist_ok=True)
        test_id = 1
        ran_any = False
        for subtask in subtasks:
            dest_dirs = [f"{PROBLEM_DIR}{subtask}"]
            if hasattr(self.main, "current_problem_name") and self.main.current_problem_name:
                dest_dirs.append(f"temp/{self.main.current_problem_name}/{subtask}")
            dest_dirs.append(f"temp/{subtask}")
            sub_in_dir = f"{PROBLEM_DIR}{subtask}/input"
            sub_io_in = f"{io_dir}/{subtask}/input"
            sub_io_out = f"{io_dir}/{subtask}/output"
            os.makedirs(sub_io_out, exist_ok=True)
            if not os.path.isdir(sub_in_dir) or not [f for f in os.listdir(sub_in_dir) if f.endswith(".in")]:
                if os.path.isdir(sub_io_in) and [f for f in os.listdir(sub_io_in) if f.endswith(".in")]:
                    sub_in_dir = sub_io_in
                elif hasattr(self.main, "current_problem_name") and self.main.current_problem_name and os.path.isdir(f"temp/{self.main.current_problem_name}/{subtask}/input") and [f for f in os.listdir(f"temp/{self.main.current_problem_name}/{subtask}/input") if f.endswith(".in")]:
                    sub_in_dir = f"temp/{self.main.current_problem_name}/{subtask}/input"
                elif os.path.isdir(f"temp/{subtask}/input") and [f for f in os.listdir(f"temp/{subtask}/input") if f.endswith(".in")]:
                    sub_in_dir = f"temp/{subtask}/input"
                else:
                    continue
            in_files = [f for f in os.listdir(sub_in_dir) if f.endswith(".in")]
            count = len(in_files)
            for i in range(count):
                sub_test = i + 1
                flat_in = f"{io_dir}/{test_id}.in"
                flat_out = f"{io_dir}/{test_id}.out"
                sub_in = f"{sub_in_dir}/{sub_test}.in"
                src_in = flat_in if os.path.isfile(flat_in) else sub_in
                if os.path.isfile(sub_in) and not os.path.isfile(flat_in):
                    shutil.copy2(sub_in, flat_in)
                    src_in = flat_in
                run_res = run_exec("temp/main_solution", src_in, flat_out)
                if os.path.isfile(flat_out):
                    shutil.copy2(flat_out, f"{sub_io_out}/{sub_test}.out")
                    for d in dest_dirs:
                        shutil.copy2(flat_out, f"{d}/output/{sub_test}.out")
                self.stats[(subtask, sub_test)] = run_res
                test_id += 1
                ran_any = True
        if not ran_any:
            self.error_area.config(text="No inputs found to generate outputs.")
            return False
        self.update_ui()
        self.error_area.config(text="Generated all outputs.")
        return True

    def generate_both(self):
        if self.generate_inputs():
            self.generate_outputs()

    def save_io_package(self):
        pass

    def update_buttons(self, *args):
        pass

    def update_ui(self):
        self.clear_list()
        subtasks = list_subtasks()
        test_id = 1
        io_dir = "temp/io"
        for subtask in subtasks:
            prob_in = f"{PROBLEM_DIR}{subtask}/input"
            sub_io_in = f"{io_dir}/{subtask}/input"
            prob_out = f"{PROBLEM_DIR}{subtask}/output"
            sub_io_out = f"{io_dir}/{subtask}/output"

            curr_in = f"temp/{self.main.current_problem_name}/{subtask}/input" if hasattr(self.main, "current_problem_name") and self.main.current_problem_name else ""
            curr_out = f"temp/{self.main.current_problem_name}/{subtask}/output" if hasattr(self.main, "current_problem_name") and self.main.current_problem_name else ""
            temp_in = f"temp/{subtask}/input"
            temp_out = f"temp/{subtask}/output"
            in_dir = prob_in
            if os.path.isdir(prob_in) and [f for f in os.listdir(prob_in) if f.endswith(".in")]:
                in_dir = prob_in
            elif os.path.isdir(sub_io_in) and [f for f in os.listdir(sub_io_in) if f.endswith(".in")]:
                in_dir = sub_io_in
            elif curr_in and os.path.isdir(curr_in) and [f for f in os.listdir(curr_in) if f.endswith(".in")]:
                in_dir = curr_in
            elif os.path.isdir(temp_in) and [f for f in os.listdir(temp_in) if f.endswith(".in")]:
                in_dir = temp_in
            out_dir = prob_out
            if os.path.isdir(prob_out) and [f for f in os.listdir(prob_out) if f.endswith(".out")]:
                out_dir = prob_out
            elif os.path.isdir(sub_io_out) and [f for f in os.listdir(sub_io_out) if f.endswith(".out")]:
                out_dir = sub_io_out
            elif curr_out and os.path.isdir(curr_out) and [f for f in os.listdir(curr_out) if f.endswith(".out")]:
                out_dir = curr_out
            elif os.path.isdir(temp_out) and [f for f in os.listdir(temp_out) if f.endswith(".out")]:
                out_dir = temp_out

            if os.path.isdir(in_dir):
                in_files = [f for f in os.listdir(in_dir) if f.endswith(".in")]
                count = len(in_files)
                for i in range(count):
                    in_state = "OK"
                    out_state = "OK" if os.path.isdir(out_dir) and os.path.isfile(f"{out_dir}/{i+1}.out") else "-"
                    status = "OK" if out_state == "OK" else "READY"
                    time_val = "-"
                    mem_val = "-"
                    if (subtask, i+1) in self.stats:
                        st_info = self.stats[(subtask, i+1)]
                        time_val = str(st_info[1])
                        mem_val = str(st_info[2])
                        if st_info[0] != 1:
                            status = "FAIL"
                    self.tree.insert("", tk.END, values=(test_id, subtask, in_state, out_state, time_val, mem_val, status))
                    test_id += 1