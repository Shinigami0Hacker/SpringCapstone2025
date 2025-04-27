import subprocess

def run_script():
    cmd = ["python", "./ai/inferences/script.py", "--model", "tiny", "--device", "cpu"]
    result = subprocess.run(
        cmd,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    transcript = result.stdout.strip()
    if transcript:
        return transcript
    return "No speech detected"

