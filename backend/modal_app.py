"""
Deploy Ask Me First on Modal (public HTTPS URL, kept warm for the demo).

    pip install modal
    modal setup                 # one-time login
    modal serve modal_app.py    # dev URL, hot reload
    modal deploy modal_app.py   # stable public URL

Keys are read from backend/.env at deploy time and stored as a Modal secret.
They are never sent to the browser.
"""
from pathlib import Path

import modal

HERE = Path(__file__).resolve().parent

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("fastapi[standard]", "openai>=1.40", "python-dotenv", "python-multipart",
                 "pangram-sdk", "reductoai")
    .add_local_file(HERE / "main.py", "/root/main.py")
    .add_local_file(HERE / "fallbacks.py", "/root/fallbacks.py")
    .add_local_file(HERE / "demo_cache.json", "/root/demo_cache.json")
    .add_local_dir(HERE.parent / "frontend", "/root/frontend")
)

app = modal.App("ask-me-first", image=image)


@app.function(secrets=[modal.Secret.from_dotenv(HERE)], min_containers=1, timeout=120)
@modal.concurrent(max_inputs=20)
@modal.asgi_app()
def web():
    import sys
    sys.path.insert(0, "/root")
    from main import app as fastapi_app
    return fastapi_app
