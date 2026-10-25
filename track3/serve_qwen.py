"""Serve Qwen3.8-27B (official repo, pinned revision) with vLLM on one Modal H100, OpenAI-compatible.

Pattern from Modal's vllm_inference example (modal.com/docs/examples/vllm_inference, fetched 24 Oct).
The endpoint is protected with a vLLM API key (never `unauthenticated` without one): the key lives in
~/.track3_vllm_key locally and reaches the container as a Modal secret.

  modal deploy serve_qwen.py     # prints the URL; put it in ~/.track3_vllm_url
  modal app stop track3-qwen     # stop billing when done
"""
import os
import secrets

import modal

MODEL_NAME = "Qwen/Qwen3.8-27B"
MODEL_REVISION = "1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0"  # HF api sha, 24 Oct 2026
VLLM_PORT = 8000
MINUTES = 60

KEY_FILE = os.path.join(os.path.expanduser("~"), ".track3_vllm_key")
if not os.path.exists(KEY_FILE) and modal.is_local():
    with open(KEY_FILE, "w", encoding="utf-8") as f:
        f.write(secrets.token_urlsafe(32))
_key = open(KEY_FILE, encoding="utf-8").read().strip() if modal.is_local() else ""

vllm_image = (
    modal.Image.from_registry("nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.12")
    .entrypoint([])
    .uv_pip_install("vllm==0.21.0")
    .env({"HF_XET_HIGH_PERFORMANCE": "1"})
)
hf_cache_vol = modal.Volume.from_name("huggingface-cache", create_if_missing=True)
vllm_cache_vol = modal.Volume.from_name("vllm-cache", create_if_missing=True)

app = modal.App("track3-qwen")


@app.server(
    image=vllm_image,
    gpu=os.environ.get("TRACK3_GPU", "H100:1"),   # deploy-time choice; A100-80GB also fits bf16
    # same object count locally and remotely, or hydration fails ("3 dependencies but 4 object ids")
    secrets=[modal.Secret.from_dict({"VLLM_API_KEY": _key})],
    scaledown_window=10 * MINUTES,   # idle containers stop, so a forgotten deploy costs at most ~$0.70
    startup_timeout=30 * MINUTES,    # first boot downloads ~56 GB of weights
    volumes={"/root/.cache/huggingface": hf_cache_vol, "/root/.cache/vllm": vllm_cache_vol},
    port=VLLM_PORT,
    target_concurrency=100,
    max_containers=1,                # budget guard: never more than one GPU
)
class Server:
    @modal.enter()
    def start(self):
        import json
        import subprocess

        cmd = ["vllm", "serve", MODEL_NAME, "--revision", MODEL_REVISION,
               "--served-model-name", "qwen3.8-27b",
               "--host", "0.0.0.0", "--port", str(VLLM_PORT),
               "--api-key", os.environ["VLLM_API_KEY"],
               "--max-model-len", "8192",
               "--limit-mm-per-prompt", json.dumps({"image": 0, "video": 0})]
        print(*[c if c != os.environ["VLLM_API_KEY"] else "***" for c in cmd])
        self.process = subprocess.Popen(cmd)

    @modal.exit()
    def stop(self):
        self.process.terminate()
