# app/main.py

import gradio as gr
import subprocess
import tempfile
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Dummy Gemini function for local testing
# Replace with: from gemini import get_gemini_fix
def get_gemini_fix(error_output, code):
    return {
        "explanation": f"Simulated Gemini response: {error_output}",
        "suggested_fix": code  # Just echo back the code for now
    }

def run_python_script(code_text):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(code_text)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            ["python", tmp_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        stdout = result.stdout
        stderr = result.stderr
    except subprocess.TimeoutExpired:
        stdout = ""
        stderr = "Error: Execution timed out."
    finally:
        os.remove(tmp_path)

    return stdout, stderr

def process_file(file):
    with open(file.name, "r", encoding="utf-8") as f:
        code = f.read()

    stdout, stderr = run_python_script(code)

    if stderr:
        gemini_result = get_gemini_fix(stderr, code)
        explanation = gemini_result.get("explanation", "N/A")
        suggested_fix = gemini_result.get("suggested_fix", "N/A")
    else:
        explanation = "✅ No errors found."
        suggested_fix = code

    return code, stdout, stderr, explanation, suggested_fix

def rerun_fixed_code(code_text):
    stdout, stderr = run_python_script(code_text)
    return stderr or stdout

def save_fixed_code(code_text):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(code_text)
        return tmp.name

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## 🐞 Code Debugging Assistant")
    gr.Markdown("Upload a `.py` file to run it, debug using Gemini, and apply suggested fixes.")

    with gr.Row():
        file_input = gr.File(label="📁 Upload Python File", file_types=[".py"])
        run_button = gr.Button("🚀 Run & Debug")

    with gr.Tabs():
        with gr.Tab("📄 Uploaded Code"):
            code_output = gr.Code(label="Original Code", language="python")

        with gr.Tab("📤 Output"):
            stdout_output = gr.Textbox(label="Program Output", lines=10)

        with gr.Tab("⚠️ Error Log"):
            error_output = gr.Textbox(label="Error Output", lines=10)

        with gr.Tab("💡 Gemini Explanation"):
            explanation_output = gr.Textbox(label="Explanation", lines=10)

        with gr.Tab("🛠️ Suggested Fix"):
            fix_output = gr.Code(label="Fixed Code", language="python", interactive=True)

        with gr.Tab("🔁 Run Fixed Code"):
            rerun_button = gr.Button("▶️ Run Fixed Code")
            fixed_output = gr.Textbox(label="Fixed Code Output", lines=10)

        with gr.Tab("⬇️ Download Fix"):
            download_button = gr.Button("💾 Download Fixed Code")
            download_file = gr.File()

    run_button.click(
        fn=process_file,
        inputs=file_input,
        outputs=[code_output, stdout_output, error_output, explanation_output, fix_output]
    )

    rerun_button.click(
        fn=rerun_fixed_code,
        inputs=fix_output,
        outputs=fixed_output
    )

    download_button.click(
        fn=save_fixed_code,
        inputs=fix_output,
        outputs=download_file
    )

# FastAPI app
app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def main():
    return demo.launch(inline=True, share=False)
