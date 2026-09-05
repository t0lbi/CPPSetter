# CPP Setter

A desktop IDE for competitive programming problem setters, contest organizers, and coordinators. It's meant to cover the whole process of putting a problem together: writing the statement, building test generators, checking solutions, running batch tests, judging submissions, and finally exporting everything to platforms like Algoleague, Codeforces, or CMS.

---

## Features

### 1. Problem Statement & Live LaTeX Preview
- Edit problem metadata — title, description, input/output format, constraints, solution writeup, time and memory limits — all in one place.
- A built-in LaTeX/PDF pane compiles statements with `pdflatex` and shows the rendered PDF right in the app (scrollable, with an option to open it externally via `xdg-open`).
- Optional AI assistant (Google Gemini) to help draft or clean up problem descriptions and constraints.

### 2. Generators & Subtasks
- Write, upload, and compile C++ test generators, and run them with custom command-line arguments.
- Preview generated tests inline (first 150 characters / 20 lines, truncated automatically for large files).
- Group generator commands into subtasks and set argument flags and scoring constraints per group.

### 3. Verification: Brute Force + Official Solution
- Keep a brute-force solution, brute-force generator, custom grader, and checker around to establish ground truth.
- Write, compile, and test your full optimal solution.
- Custom checkers (scores from 0.0–1.0) and interactive graders are both supported.

### 4. Test I/O Generation
- One click compiles all active generators and produces inputs for every subtask.
- Outputs can be generated from either the official solution or the brute force, so you can cross-check.

### 5. Judger & Verdict Inspection
- Add and manage multiple submissions (student solutions, benchmarks, edge cases).
- Batch-judge everything against the test suite — AC, WA, TLE, MLE, RE, CE, all tracked per submission.
- Inspect any test case side by side: contestant output vs. official output, plus runtime and peak memory.

### 6. Exporting
Pick a destination format and export a ready-to-upload archive:
- **Algoleague** – `tests.zip` with `input/01.txt` / `output/01.txt` layout, plus source, submissions, and checkers.
- **Codeforces / Polygon** – tests, solutions, and checkers packaged for Polygon import.
- **CMS** – subtask-prefixed test pairs (`subtask_01.in` / `subtask_01.out`) with metadata.

---

## Requirements

### System (Linux)
- Python 3.8+ with Tkinter
- `g++` (C++17 or C++20)
- `pdflatex` (TeX Live)
- `pdftoppm` (from `poppler-utils`)
- `xdg-open` or GNOME Text Editor (optional, for opening files externally)

On Debian/Ubuntu:
```bash
sudo apt update
sudo apt install -y g++ texlive-latex-base texlive-latex-extra poppler-utils python3-tk python3-pip
```

### Python packages
```bash
pip install -r requirements.txt
```
or manually:
```bash
pip install Pillow python-dotenv requests
```
(`google-genai` is optional, only needed for the Gemini SDK integration.)

---

## Getting Started

1. **Clone it**
   ```bash
   git clone https://github.com/t0lbi/CPPSetter.git
   cd CPPSetter
   ```

2. **Set up Gemini (optional)** — if you want the AI helpers for statements or generators, add a `.env` file in the project root:
   ```bash
   GEMINI_API_KEY="your_gemini_api_key_here"
   ```

3. **Run it**
   ```bash
   python3 main.py
   ```

---

## Suggested Workflow

1. Open an existing problem from `problems/` or start a new bundle.
2. Fill in the problem info — title, limits, statement — and hit **Refresh PDF** to see it compiled. Use the **AI** button if you want help drafting.
3. Write your C++ generators, group them into subtasks, and run them to check the sample inputs look right.
4. Go to the **I/O** tab and click **Generate Both** to build the full test suite.
5. Run both the brute-force and official solutions against the tests to confirm everything checks out.
6. In the **Judger**, add a few submissions (a correct one, a slow one, a buggy one) and run the judge to make sure subtask constraints behave as expected.
7. Head to the **Exporter**, pick Algoleague, Codeforces, or CMS, choose a destination folder, and export.

---

## Directory Structure

```text
CPPSetter/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (GEMINI_API_KEY)
├── problems/                   # Saved problem bundles
│   └── <problem_name>/
│       ├── metadata.json       # Problem configuration & limits
│       ├── solutions/          # full.cpp, bf.cpp
│       ├── generators/         # Generator source files
│       ├── subtasks/           # Subtask definitions and test cases
│       └── submissions/        # Benchmark and student submissions
├── src/
│   ├── core/
│   │   ├── manager.py          # Problem file management, hashing, exports
│   │   └── runner.py           # Execution, compilation, and scoring engine
│   └── ui/
│       ├── main_window.py      # Main GUI layout & navigation
│       ├── llm_api_tab.py      # Gemini AI integration dialogs
│       └── tabs/               # Modular UI views (Problem, I/O, Judger, etc.)
└── temp/                       # Temporary build artifacts (auto-cleaned)
```

---

## License

MIT — see the LICENSE file for details.
