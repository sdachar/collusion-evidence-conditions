"""Wait for the Modal vLLM server to come up, then check the one thing every arm depends on: a game
prompt returns short, parseable JSON with thinking off. Prints no URL or key.

  python smoke_endpoint.py            # polls /health for up to 40 min (first boot downloads ~56 GB)
"""
import json
import os
import time
import urllib.error
import urllib.request

from leniency import REGIMES, Obs, VLLMAgent, build_prompt, parse_reply, proxy_headers

HOME = os.path.expanduser("~")


def wait_healthy(base: str, limit_s: int = 2400) -> float:
    key = open(os.path.join(HOME, ".track3_vllm_key"), encoding="utf-8").read().strip()
    req = urllib.request.Request(base + "/health", headers={"Authorization": f"Bearer {key}", **proxy_headers()})
    t0 = time.time()
    while time.time() - t0 < limit_s:
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                if r.status == 200:
                    return time.time() - t0
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(20)
    raise SystemExit(f"server not healthy after {limit_s} s")


def main():
    base = open(os.path.join(HOME, ".track3_vllm_url"), encoding="utf-8").read().strip().rstrip("/")
    print(f"healthy after {wait_healthy(base):.0f} s")
    log: list = []
    agent = VLLMAgent(log)
    rg = REGIMES["R3"]
    hist = [(1.9, 1.9, 36.0, 32.7)] * 9
    checks = [("A act, pre", Obs("A", 2, 16, hist[:2]), "act"),
              ("B price, regime on", Obs("B", 9, 16, hist, "Let us both price at 1.90 again.", regime_on=True), "price")]
    for name, obs, phase in checks:
        t = time.time()
        text, fin = agent._call(build_prompt(obs, rg, phase, info=True))
        u = log[-1].get("usage") or {}
        try:
            parsed, ok = parse_reply(text), True
        except ValueError:
            parsed, ok = None, False
        print(json.dumps({"check": name, "seconds": round(time.time() - t, 1), "finish": fin, "parsed": ok,
                          "completion_tokens": u.get("completion_tokens"), "prompt_tokens": u.get("prompt_tokens"),
                          "has_think_tag": "<think>" in text, "reply": parsed}))


if __name__ == "__main__":
    main()
