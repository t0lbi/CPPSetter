import subprocess
import time
import psutil
import os

MAX_RUNTIME = int(os.getenv("MAX_RUNTIME",10))
MAX_RUNTIME_SECONDS = MAX_RUNTIME
LAST_COMPILE_ERROR = ""

def get_last_compile_error():
	return LAST_COMPILE_ERROR

def compile_code(solution, grader, flag, out):
	global LAST_COMPILE_ERROR
	LAST_COMPILE_ERROR = ""
	if grader == "none":
		command = ["g++", solution, flag, "-o", out]
	else:
		command = ["g++", grader, solution, flag, "-o", out]
	command = [arg for arg in command if arg]
	try:
		result = subprocess.run(
			command,
			check=True,
			capture_output=True,
			text=True
		)
		return 1
	except subprocess.CalledProcessError as e:
		LAST_COMPILE_ERROR = e.stderr
		return 0

def run_exec(solution, program_input, program_output):
    start_time = time.perf_counter()
    memory_used_kb = 0
    try:
        with open(program_input, "r", encoding="utf-8") as input_file, \
             open(program_output, "w", encoding="utf-8") as output_file:
            process = subprocess.Popen(
                [solution],
                stdin=input_file,
                stdout=output_file,
                stderr=subprocess.PIPE,
                text=True
            )
            try:
                p = psutil.Process(process.pid)
                memory_used_kb = int(p.memory_info().rss / 1024) 
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass 

            try:
                process.wait(timeout=MAX_RUNTIME)
            except subprocess.TimeoutExpired:
                process.kill()
                runtime_ms = int((time.perf_counter() - start_time) * 1000)
                print(f"Time Limit Exceeded! Killed after {MAX_RUNTIME_SECONDS} seconds.")
                return [0, runtime_ms, memory_used_kb]
            
            runtime_ms = int((time.perf_counter() - start_time) * 1000)

            if process.returncode != 0:
                stderr_output = process.stderr.read()
                print(f"Runtime Error! Error Code: {process.returncode}")
                print(f"Error:\n{stderr_output}")
                return [0, runtime_ms, memory_used_kb]

        return [1, runtime_ms, memory_used_kb]

    except Exception as e:
        runtime_ms = int((time.perf_counter() - start_time) * 1000)
        print(f"System Error: {e}")
        return [0, runtime_ms, 0]

def run_gen(solution, args, program_output):
	try:
		with open(program_output, "w", encoding="utf-8") as output_file:
			result = subprocess.run(
				[solution]+args.split(),
				stdout=output_file,
				stderr=subprocess.PIPE,
				text=True,
				check=True,
				timeout=MAX_RUNTIME
			)
		return 1
	except subprocess.CalledProcessError as e:
		print(f"Runtime Error! Error Code: {e.returncode}")
		print(f"Error:\n{e.stderr}")
		return 0



def score(program_input, program_output1, program_output2, checker):
	if checker != "none" and not os.path.isfile(checker):
		print("Checker does not exist!")
		return 0.0
	if checker == "none":
		command = [
			"diff",
			"-q",
			program_output1,
			program_output2
		]
	else:
		command = [
			checker,
			program_input,
			program_output1,
			program_output2
		]

	try:
		result = subprocess.run(
			command,
			capture_output=True,
			text=True,
			timeout=MAX_RUNTIME,
			start_new_session=True,
		)
	except subprocess.TimeoutExpired:
		print(f"Time Limit Exceeded! (>{MAX_RUNTIME}s)")
		return 0.0

	if checker == "none":
		if result.returncode == 0:
			return 1.0
		return 0.0

	if result.returncode != 0:
		return 0.0
	try:
		return float(result.stdout)
	except ValueError:
		return 0.0