import hashlib
import json
import os
import shutil
import subprocess
from .runner import compile_code, run_gen, run_exec, score

EDITOR = str(os.getenv("EDITOR","gedit"))
PROBLEM_DIR = "temp/problem-data/"
GEN_DIR = PROBLEM_DIR + "generators/"
SOL_DIR = PROBLEM_DIR + "solutions/"
META_PATH = PROBLEM_DIR + "metadata.json"
GRADER_PATH = PROBLEM_DIR + "grader.cpp"
CHECKER_PATH = PROBLEM_DIR + "checker.cpp"
BF_SOLUTION_PATH = SOL_DIR + "bf.cpp"
BF_GENERATOR_PATH = GEN_DIR + "bf.cpp"
FULL_SOLUTION_PATH = SOL_DIR + "full.cpp"
_CHECKER_STUB = """#include <bits/stdc++.h>
using namespace std;

int main(int argc, char* argv[]) {
\t// (argv: input, contestant.out, official.out)
\tcout<<0.0<<'\n'; //print double between 0.0 and 1.0
\treturn 0;
}
"""

_GRADER_STUB = """#include <bits/stdc++.h>
using namespace std;

int main() {
\treturn 0;
}
"""

_BF_SOLUTION_STUB = """#include <bits/stdc++.h>
using namespace std;

int main() {
\t// Brute force solution
\treturn 0;
}
"""

_BF_GENERATOR_STUB = """#include <bits/stdc++.h>
using namespace std;

int main(int argc, char* argv[]) {
\t// Brute force generator
\treturn 0;
}
"""

_FULL_SOLUTION_STUB = """#include <bits/stdc++.h>
using namespace std;

int main() {
\t// Full solution
\treturn 0;
}
"""

_GENERATOR_STUB = """#include <bits/stdc++.h>
using namespace std;

int main(int argc, char* argv[]) {
\t// Test generator (args: argc/argv)
\treturn 0;
}
"""


def read_metadata():
	if not os.path.isfile(META_PATH):
		return {}
	with open(META_PATH, "r", encoding="utf-8") as file:
		return json.load(file)


def write_metadata(data):
	with open(META_PATH, "w", encoding="utf-8") as file:
		json.dump(data, file, indent="\t")
		file.write("\n")


def validate_generator_name(name):
	if not (name and name.strip() != ""):
		return None, "Generator name cannot be empty."
	valid = True
	clean = name.strip()
	if not (clean[0].isalpha() or clean[0] == '_'):
		valid = False
	for ch in clean:
		if not (ch.isalnum() or ch == '_'):
			valid = False
	if valid:
		return clean, None
	return None, "Use letters, digits, or underscores; start with a letter or _."


def generator_path(name):
	return GEN_DIR + name + ".cpp"


def list_generators():
	if not os.path.isdir(GEN_DIR):
		return []
	return sorted(f[:-4] for f in os.listdir(GEN_DIR) if f.endswith(".cpp"))


def write_if_missing(path, content):
	if not os.path.isfile(path):
		with open(path, "w", encoding="utf-8") as file:
			file.write(content)


def create_generator(name):
	clean, error = validate_generator_name(name)
	if error:
		return None, error
	path = generator_path(clean)
	if os.path.exists(path):
		return None, "Generator already exists."
	os.makedirs(GEN_DIR, exist_ok=True)
	write_if_missing(path, _GENERATOR_STUB)
	return path, None


def import_generator(source_path, name=None):
	if not os.path.isfile(source_path):
		return None, "Selected file does not exist."
	if name:
		clean, error = validate_generator_name(name)
	else:
		base = os.path.basename(source_path)
		if not base.endswith(".cpp"):
			return None, "Generator file must be a .cpp file."
		clean, error = validate_generator_name(base[:-4])
	if error:
		return None, error
	os.makedirs(GEN_DIR, exist_ok=True)
	dest = generator_path(clean)
	shutil.copy2(source_path, dest)
	return dest, None


def rename_generator(old_name, new_name):
	old_clean, error = validate_generator_name(old_name)
	if error:
		return error
	new_clean, error = validate_generator_name(new_name)
	if error:
		return error
	if old_clean == new_clean:
		return None
	old_path, new_path = generator_path(old_clean), generator_path(new_clean)
	if not os.path.isfile(old_path):
		return f"Generator not found: {old_clean}.cpp"
	if os.path.isfile(new_path):
		return f"Generator already exists: {new_clean}.cpp"
	os.rename(old_path, new_path)
	return None


def remove_generator(name):
	clean, error = validate_generator_name(name)
	if error:
		return error
	path = generator_path(clean)
	if os.path.isfile(path):
		os.remove(path)
	return None


def verify_source(meta, key, path):
	if not meta.get(key):
		return "none", None
	if not os.path.isfile(path):
		return None, f"{key.capitalize()} file not found: {path}"
	return path, None


def grader_compile_arg(meta):
	return verify_source(meta, "grader", GRADER_PATH)


def compile_checker_executable(meta):
	path, error = verify_source(meta, "checker", CHECKER_PATH)
	if error or path == "none":
		return path, error
	if compile_code(path, "none", "-static", "temp/checker") != 1:
		return None, "Checker compilation failed (CE)."
	return "temp/checker", None

def import_main_solution(source_path):
	if not os.path.isdir(PROBLEM_DIR):
		return None, "Problem workspace not found."
	if not os.path.isfile(source_path):
		return None, "Selected file does not exist."
	os.makedirs(SOL_DIR, exist_ok=True)
	shutil.copy2(source_path, FULL_SOLUTION_PATH)
	return FULL_SOLUTION_PATH, None

def run_bf_generator(args):
	os.makedirs("temp", exist_ok=True)
	if not os.path.isfile(BF_GENERATOR_PATH):
		return {"ok": False, "message": "Generator file not found.", "output": None}
	if compile_code(BF_GENERATOR_PATH, "none", "", "temp/bf_generator") != 1:
		return {"ok": False, "message": "Compilation error (CE).", "output": None}
	output_path = "temp/bf_gen.out"
	if run_gen("temp/bf_generator", args, output_path) != 1:
		return {"ok": False, "message": "Runtime error (RE).", "output": output_path}
	return {"ok": True, "message": "OK", "output": output_path}


def run_bf_solution(input_path):
	meta = read_metadata()
	os.makedirs("temp", exist_ok=True)
	grader_cpp, grader_error = grader_compile_arg(meta)
	if grader_error:
		return {"ok": False, "message": grader_error, "output": None}
	if not os.path.isfile(BF_SOLUTION_PATH):
		return {"ok": False, "message": "Brute force solution file not found.", "output": None}
	if compile_code(BF_SOLUTION_PATH, grader_cpp, "", "temp/bf_solution") != 1:
		return {"ok": False, "message": "Compilation error (CE).", "output": None}
	if not os.path.isfile(input_path):
		return {"ok": False, "message": "Input not found: "+input_path, "output": None}
	output_path = "temp/bf_sol.out"
	if run_exec("temp/bf_solution", input_path, output_path)[0] != 1:
		return {"ok": False, "message": "Runtime error (RE) or time limit exceeded.", "output": output_path}
	return {"ok": True, "message": "OK", "output": output_path}


def compile_generator_grader_checker(meta):
	result = {}
	ok = True

	if os.path.isfile(BF_GENERATOR_PATH):
		if compile_code(BF_GENERATOR_PATH, "none", "", "temp/bf_generator") == 1:
			result["generator"] = "OK"
		else:
			result["generator"] = "Compilation Error (CE)."
			ok = False
	else:
		result["generator"] = "skipped"

	grader_cpp, grader_error = grader_compile_arg(meta)
	if grader_error:
		result["grader"] = grader_error
		ok = False
	else:
		if grader_cpp == "none":
			result["grader"] = "none"
		else:
			result["grader"] = "OK"

	if os.path.isfile(BF_SOLUTION_PATH):
		if grader_cpp is None:
			result["bf"] = "Skipped (grader missing)."
			ok = False
		else:
			if compile_code(BF_SOLUTION_PATH, grader_cpp, "", "temp/bf_solution") == 1:
				result["bf"] = "OK"
			else:
				result["bf"] = "Compilation error (CE)."
				ok = False
	else:
		result["bf"] = "skipped"

	checker_exe, checker_error = compile_checker_executable(meta)
	if checker_error:
		result["checker"] = checker_error
		ok = False
	else:
		if checker_exe == "none":
			result["checker"] = "none"
		else:
			result["checker"] = "OK"

	return result, ok, grader_cpp, checker_exe


def verify_solution_compiles():
	meta = read_metadata()
	os.makedirs("temp", exist_ok=True)
	result, ok, grader_cpp, _ = compile_generator_grader_checker(meta)

	if os.path.isfile(FULL_SOLUTION_PATH):
		if grader_cpp is None:
			result["main"] = "Skipped (grader missing)."
			ok = False
		else:
			if compile_code(FULL_SOLUTION_PATH, grader_cpp, "", "temp/main_solution") == 1:
				result["main"] = "OK"
			else:
				result["main"] = "Compilation error (CE)."
				ok = False
	else:
		result["main"] = "File not found."
		ok = False

	result["ok"] = ok
	return result


def verify_bf_compiles():
	meta = read_metadata()
	os.makedirs("temp", exist_ok=True)
	result, ok, _, _ = compile_generator_grader_checker(meta)
	result["solution"] = result.pop("bf")
	result["ok"] = ok
	return result


def verify_solution_stress(count, generator_args):
	meta = read_metadata()
	compile_result = verify_solution_compiles()
	if not compile_result["ok"]:
		return {
			"ok": False,
			"passed": 0,
			"total": count,
			"failures": ["Compile step failed — run Verify CE first."],
			"details": compile_result,
			"runs": []
		}

	grader_cpp, _ = grader_compile_arg(meta)
	has_grader = grader_cpp != "none"
	checker_exe, _ = compile_checker_executable(meta)
	if checker_exe is None:
		checker_exe = "none"
	work_dir = "temp/solution_verify/"
	os.makedirs(work_dir, exist_ok=True)
	passed, failures, runs = 0, [], []

	for index in range(count):
		test_no = index + 1
		input_path = f"{work_dir}{test_no}.in"
		main_out = f"{work_dir}{test_no}.main.out"
		bf_out = f"{work_dir}{test_no}.bf.out"
		row = {
			"test": test_no,
			"status": "FAIL",
			"main_time_ms": None,
			"main_mem_kb": None,
			"bf_time_ms": None,
			"bf_mem_kb": None,
			"checker_score": None,
			"grader_score": None,
			"message": ""
		}

		if run_gen("temp/bf_generator", generator_args, input_path) != 1:
			row["message"] = "Generator RE."
			failures.append(f"Test {test_no}: generator RE.")
			runs.append(row)
			continue

		bf_run = run_exec("temp/bf_solution", input_path, bf_out)
		row["bf_time_ms"], row["bf_mem_kb"] = bf_run[1], bf_run[2]
		if bf_run[0] != 1:
			row["message"] = "Brute solution RE/TLE."
			failures.append(f"Test {test_no}: brute solution RE/TLE.")
			runs.append(row)
			continue

		main_run = run_exec("temp/main_solution", input_path, main_out)
		row["main_time_ms"], row["main_mem_kb"] = main_run[1], main_run[2]
		if main_run[0] != 1:
			row["message"] = "Full solution RE/TLE."
			failures.append(f"Test {test_no}: main solution RE/TLE.")
			runs.append(row)
			continue

		test_ok = True
		match_score = score(input_path, main_out, bf_out, checker_exe)
		row["checker_score"] = match_score
		if match_score != 1.0:
			test_ok = False
			row["message"] += (" " if row["message"] else "") + f"Checker score {match_score} (expected 1.0)."
			failures.append(f"Test {test_no}: checker score {match_score} (expected 1.0).")

		if test_ok:
			row["status"], row["message"], passed = "OK", "OK", passed + 1
		runs.append(row)

	return {
		"ok": passed == count,
		"passed": passed,
		"total": count,
		"failures": failures,
		"details": compile_result,
		"runs": runs
	}


def open_in_gnome_text_editor(*paths):
	if shutil.which(EDITOR):
		for path in paths:
			subprocess.Popen([EDITOR, path], start_new_session=True)
	else:
		for path in paths:
			subprocess.Popen(["xdg-open", path], start_new_session=True)


def create_input_pack(subtask_dir):
	with open(subtask_dir + "/metadata.json", "r") as file:
		data = json.load(file)
	if os.path.exists(subtask_dir + "/input"):
		shutil.rmtree(subtask_dir + "/input")
	os.makedirs(subtask_dir + "/input", exist_ok=True)
	test = 1
	for pack in data["data"]:
		if compile_code(GEN_DIR + pack["generator"] + ".cpp", "none", "", "temp/" + pack["generator"]) != 1:
			return 0
		for flag in pack["tests"]:
			out_path = subtask_dir + "/input/" + str(test) + ".in"
			if run_gen("temp/" + pack["generator"], flag, out_path) != 1:
				print(f"Error on test {test}! generator: {pack['generator']}.cpp, args: {flag}\n")
				return 0
			test += 1
	return 1


def create_output_pack(subtask_dir):
	if os.path.exists(subtask_dir + "/output"):
		shutil.rmtree(subtask_dir + "/output")
	os.makedirs(subtask_dir + "/output", exist_ok=True)
	file_count = len(os.listdir(subtask_dir + "/input"))
	for i in range(file_count):
		run_exec("temp/main_solution", f"{subtask_dir}/input/{i+1}.in", f"{subtask_dir}/output/{i+1}.out")


def default_metadata(title):
	return {
		"title": title,
		"description": "Description",
		"input": "Input Format",
		"output": "Output Format",
		"solution": "Solution explanation (optional)",
		"constraints": "Constraints",
		"time_limit": 2.0,
		"memory_limit": 256.0,
		"grader": False,
		"checker": False,
		"subtasks": [],
	}

def valid_to_create(problemname):
	if not (problemname and problemname.strip() != ""):
		return 0
	if os.path.exists("problems/" + problemname):
		return 0
	return 1

def create_problem(problemname):
	os.makedirs(GEN_DIR, exist_ok=True)
	os.makedirs(SOL_DIR, exist_ok=True)
	write_metadata(default_metadata(problemname))
	write_if_missing(PROBLEM_DIR+"grader.cpp", _GRADER_STUB)
	write_if_missing(PROBLEM_DIR+"checker.cpp", _CHECKER_STUB)
	write_if_missing(BF_GENERATOR_PATH, _BF_GENERATOR_STUB)
	write_if_missing(BF_SOLUTION_PATH, _BF_SOLUTION_STUB)
	write_if_missing(FULL_SOLUTION_PATH, _FULL_SOLUTION_STUB)


def load_problem(problem_path):
	if not os.path.exists(problem_path):
		return 0
	os.makedirs(problem_path+"/generators", exist_ok=True)
	os.makedirs(problem_path+"/solutions", exist_ok=True)

	template = default_metadata(os.path.basename(problem_path))
	meta_path = problem_path+"/metadata.json"
	if os.path.isfile(meta_path):
		with open(meta_path, "r", encoding="utf-8") as file:
			data = json.load(file)
		missing = [key for key in template if key not in data]
		if missing:
			data.update({key: template[key] for key in missing})
			with open(meta_path, "w", encoding="utf-8") as file:
				json.dump(data, file, indent="\t")
				file.write("\n")
	else:
		with open(meta_path, "w", encoding="utf-8") as file:
			json.dump(template, file, indent="\t")
			file.write("\n")

	if os.path.exists(PROBLEM_DIR):
		shutil.rmtree(PROBLEM_DIR)
	subprocess.run(["cp", "-fr", problem_path, PROBLEM_DIR.rstrip("/")])
	return 1


def save_problem(problemname):
	if not os.path.exists(PROBLEM_DIR):
		return 0
	dest = "problems/" + problemname
	if os.path.exists(dest):
		shutil.rmtree(dest)
	subprocess.run(["cp", "-fr", PROBLEM_DIR, dest])
	return 1


def get_string_sha256(text):
	return hashlib.sha256(text.encode("utf-8")).hexdigest()


def get_file_sha256(filepath):
	digest = hashlib.sha256()
	with open(filepath, "rb") as file:
		for chunk in iter(lambda: file.read(65536), b""):
			digest.update(chunk)
	return digest.hexdigest()


def tree_sha256(root):
	if root[-1] != '/':
		root = root + '/'
	if not os.path.isdir(root):
		return None

	root_len = len(root)

	sha = hashlib.sha256()

	for dirpath, dirnames, filenames in os.walk(root):
		dirnames.sort()
		filenames.sort()
		sha.update(get_string_sha256(dirpath[root_len:]).encode("utf-8"))
		for filename in filenames:
			full_path = dirpath+"/"+filename
			if not os.path.isfile(full_path):
				continue
			sha.update(get_string_sha256(filename).encode("utf-8"))
			sha.update(get_file_sha256(full_path).encode("utf-8"))
		sha.update(get_string_sha256(dirpath[root_len:]).encode("utf-8"))

	return sha.hexdigest()


def workspace_differs_from_saved(problemname):
	saved = "problems/" + problemname
	if not os.path.isdir(PROBLEM_DIR):
		return False
	if not os.path.isdir(saved):
		return True
	return tree_sha256(PROBLEM_DIR) != tree_sha256(saved)


def list_subtasks():
	return read_metadata().get("subtasks", [])


def read_subtask_metadata(subtask_name):
	meta_path = PROBLEM_DIR+subtask_name+"/metadata.json"
	if not os.path.isfile(meta_path):
		return {"constraints": "", "data": []}
	with open(meta_path, "r", encoding="utf-8") as file:
		return json.load(file)


def save_subtask_metadata(subtask_name, constraints, data):
	subtask_dir = PROBLEM_DIR+subtask_name
	if not os.path.isdir(subtask_dir):
		return "Subtask folder not found."
	with open(subtask_dir+"/metadata.json", "w", encoding="utf-8") as file:
		json.dump({"constraints": constraints, "data": data}, file, indent="\t")
		file.write("\n")
	return None


def rename_subtask(old_name, new_name):
	old_clean, error = validate_generator_name(old_name)
	if error:
		return error
	new_clean, error = validate_generator_name(new_name)
	if error:
		return error
	if old_clean == new_clean:
		return None
	old_path = PROBLEM_DIR+old_clean
	new_path = PROBLEM_DIR+new_clean
	if not os.path.isdir(old_path):
		return f"Subtask not found: {old_clean}"
	if os.path.exists(new_path):
		return f"Subtask already exists: {new_clean}"
	os.rename(old_path, new_path)
	data = read_metadata()
	nw = []
	for item in data.get("subtasks", []):
		if item == old_clean:
			nw.append(new_clean)
		else:
			nw.append(item)
	data["subtasks"] = nw
	write_metadata(data)
	return None


def remove_subtask(subtask_name):
	clean, error = validate_generator_name(subtask_name)
	if error:
		return error
	subtask_path = PROBLEM_DIR+clean
	if os.path.isdir(subtask_path):
		shutil.rmtree(subtask_path)

	data = read_metadata()
	nw = []
	for item in data.get("subtasks", []):
		if item != clean:
			nw.append(item)
	data["subtasks"] = nw
	write_metadata(data)
	return None


def create_subtask(subtaskname):
	subtask_path = PROBLEM_DIR+subtaskname
	if os.path.exists(subtask_path):
		return 0
	os.makedirs(subtask_path)
	with open(subtask_path+"/metadata.json", "w", encoding="utf-8") as file:
		json.dump({"constraints": "Additional constraint", "data": []}, file, indent="\t")
		file.write("\n")

	data = read_metadata()
	if subtaskname not in data.get("subtasks", []):
		if data.get("subtasks", []) == []:
			data["subtasks"] = []
		data["subtasks"].append(subtaskname)
	write_metadata(data)
	return 1