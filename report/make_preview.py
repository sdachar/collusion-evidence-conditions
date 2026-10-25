"""Preview PDF of SUBMISSION.md, for a length and layout check only. The submitted PDF comes from the
official template (SUBMIT-CHECKLIST.md, step 3).
  python make_preview.py      -> preview.html, preview.pdf (headless Edge)
"""
import subprocess
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CSS = """body{font-family:Georgia,serif;font-size:10.5pt;line-height:1.35;max-width:7in;margin:0.6in auto;color:#111}
table{border-collapse:collapse;font-size:8.5pt;margin:6px 0}td,th{border:1px solid #bbb;padding:2px 4px;vertical-align:top}
img{max-width:100%}blockquote{border-left:3px solid #c33;margin:0;padding:4px 10px;background:#fff4f4}
h1{font-size:16pt}h2{font-size:12.5pt;margin-top:14px}h3{font-size:11pt}code{font-size:9pt}"""


def main():
    md = (HERE / "SUBMISSION.md").read_text(encoding="utf-8")
    body = markdown.markdown(md, extensions=["tables"])
    html = HERE / "preview.html"
    html.write_text(f"<!doctype html><meta charset='utf-8'><style>{CSS}</style>{body}", encoding="utf-8")
    subprocess.run([EDGE, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={HERE / 'preview.pdf'}", html.as_uri()], check=True, timeout=120)
    print("wrote preview.pdf")


if __name__ == "__main__":
    main()
