import gradio as gr
import subprocess
import tempfile
import os
from gemini import get_gemini_fix, analyze_code_quality  # ✅ Import both functions

# Function to run the uploaded Python script
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

# Process uploaded file and return all outputs
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

    # Quality analysis
    quality = analyze_code_quality(code)
    score = quality.get("score", 0)
    good = quality.get("good_practices", "N/A")
    bad = quality.get("bad_practices", "N/A")
    summary = quality.get("summary", "N/A")

    return code, stdout, stderr, explanation, suggested_fix, suggested_fix, score, good, bad, summary

# Rerun user-edited fixed code
def rerun_fixed_code(code_text):
    stdout, stderr = run_python_script(code_text)
    return stderr or stdout

# Save user-edited fixed code to a file
def save_fixed_code(code_text):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(code_text)
        return tmp.name

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## 🐞 Code Debugging Assistant")
    gr.Markdown("Upload a `.py` file to analyze, debug using Gemini, and improve your code!")

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

        with gr.Tab("🧠 Gemini Suggested Fix"):
            suggested_fix_output = gr.Code(label="Suggested Fix (Read-Only)", language="python", interactive=False)

        with gr.Tab("✍️ Editable Fixed Code"):
            fix_output = gr.Code(label="Edit and Fix Code", language="python", interactive=True)
            with gr.Row():
                rerun_button = gr.Button("▶️ Run Fixed Code")
                revert_button = gr.Button("↩️ Revert to Suggested Fix")

        with gr.Tab("🧪 Fixed Code Output"):
            fixed_output = gr.Textbox(label="Fixed Code Output", lines=10)

        with gr.Tab("⬇️ Download Fix"):
            download_button = gr.Button("💾 Download Fixed Code")
            download_file = gr.File(label="Download")

        with gr.Tab("📊 Code Quality Analysis"):
            score_slider = gr.Slider(minimum=0, maximum=10, step=1, label="Code Score (out of 10)")
            good_points_output = gr.Textbox(label="✅ Good Practices", lines=4)
            bad_points_output = gr.Textbox(label="❌ Areas to Improve", lines=4)
            summary_output = gr.Textbox(label="📌 Summary", lines=4)

    # Button triggers
    run_button.click(
        fn=process_file,
        inputs=file_input,
        outputs=[
            code_output,
            stdout_output,
            error_output,
            explanation_output,
            suggested_fix_output,
            fix_output,
            score_slider,
            good_points_output,
            bad_points_output,
            summary_output
        ]
    )

    rerun_button.click(
        fn=rerun_fixed_code,
        inputs=fix_output,
        outputs=fixed_output
    )

    revert_button.click(
        fn=lambda suggested: suggested,
        inputs=suggested_fix_output,
        outputs=fix_output
    )

    download_button.click(
        fn=save_fixed_code,
        inputs=fix_output,
        outputs=download_file
    )

# Launch the app
if __name__ == "__main__":
    demo.launch(share=True)
