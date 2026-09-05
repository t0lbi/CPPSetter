import os
import json
import threading
import requests
import tkinter as tk

def get_gemini_api_key():
    key = os.environ.get("GEMINI_API_KEY")
    if key and key.strip():
        return key.strip()
    candidates = [
        ".env",
        os.path.join(os.path.dirname(__file__), "../../.env"),
        os.path.expanduser("~/.env")
    ]
    for path in candidates:
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY="):
                            val = line.split("=", 1)[1].strip()
                            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                                val = val[1:-1]
                            if val:
                                return val
            except Exception:
                pass
    return ""

def call_gemini(prompt, api_key):
    preferred_models = [
        "gemini-3.6-flash",
        "gemini-flash-latest",
        "gemini-3.5-flash",
        "gemini-3.7-flash",
    ]
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        for m in preferred_models:
            try:
                response = client.models.generate_content(
                    model=m,
                    contents=prompt,
                )
                if response and response.text:
                    return response.text, None
            except Exception:
                continue
    except Exception:
        pass

    last_err = "No response from Gemini API"
    for model in preferred_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            resp = requests.post(
                url,
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=60
            )
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text, None
            else:
                last_err = f"API error ({resp.status_code}): {resp.text}"
        except Exception as e:
            last_err = str(e)
    return None, last_err

def strip_markdown_fences(text):
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text

def open_ai_dialog(parent, title, prompt_label_text, system_wrapper, on_success, on_error=None):
    popup = tk.Toplevel(parent, bg="#333333")
    popup.title(title)
    popup.geometry("520x340")
    popup.resizable(False, False)
    try:
        popup.transient(parent.winfo_toplevel())
    except Exception:
        pass

    lbl = tk.Label(
        popup,
        text=prompt_label_text,
        bg="#333333",
        fg="#ffffff",
        font=("Arial", 12, "bold")
    )
    lbl.pack(pady=(15, 8), padx=15, anchor="w")

    text_area = tk.Text(
        popup,
        height=8,
        width=52,
        bg="#111111",
        fg="#ffffff",
        font=("Arial", 12),
        insertbackground="#ffffff",
        wrap="word"
    )
    text_area.pack(padx=15, pady=(0, 8))
    text_area.focus()

    status_label = tk.Label(
        popup,
        text="",
        bg="#333333",
        fg="#ff5555",
        font=("Arial", 10),
        wraplength=480
    )
    status_label.pack(padx=15, pady=(0, 8))

    btn_frame = tk.Frame(popup, bg="#333333")
    btn_frame.pack(fill="x", padx=15, pady=(0, 15))

    cancel_btn = tk.Button(
        btn_frame,
        text="Cancel",
        font=("Arial", 12),
        width=10,
        bg="#3c3f41",
        fg="#ffffff",
        command=popup.destroy
    )
    cancel_btn.pack(side="left")

    def on_generate():
        user_prompt = text_area.get("1.0", "end").strip()
        if not user_prompt:
            status_label.config(text="Please enter a prompt.", fg="#ff5555")
            return

        api_key = get_gemini_api_key()
        if not api_key:
            status_label.config(text="GEMINI_API_KEY not found in .env", fg="#ff5555")
            return

        status_label.config(text="Generating with AI... please wait.", fg="#00ff00")
        gen_btn.config(state="disabled")
        cancel_btn.config(state="disabled")

        def worker():
            full_prompt = system_wrapper(user_prompt)
            res, err = call_gemini(full_prompt, api_key)
            def done():
                if not popup.winfo_exists():
                    return
                if err or res is None:
                    status_label.config(text=f"Error: {err}", fg="#ff5555")
                    gen_btn.config(state="normal")
                    cancel_btn.config(state="normal")
                    if on_error:
                        on_error(err)
                else:
                    cleaned = strip_markdown_fences(res)
                    try:
                        on_success(cleaned)
                        popup.destroy()
                    except Exception as e:
                        status_label.config(text=f"Processing error: {e}", fg="#ff5555")
                        gen_btn.config(state="normal")
                        cancel_btn.config(state="normal")
                        if on_error:
                            on_error(str(e))
            popup.after(0, done)

        threading.Thread(target=worker, daemon=True).start()

    gen_btn = tk.Button(
        btn_frame,
        text="Generate",
        font=("Arial", 12),
        width=10,
        bg="#3c3f41",
        fg="#ffffff",
        command=on_generate
    )
    gen_btn.pack(side="right")
