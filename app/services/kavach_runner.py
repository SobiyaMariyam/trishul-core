# app/services/kavach_runner.py
import base64
import io
import shutil
import subprocess
from datetime import datetime, timezone
from typing import Tuple

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas


def _gen_pdf_bytes(target: str, summary: str) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=LETTER)
    c.setTitle("Kavach Scan Report")
    w, h = LETTER
    y = h - 72
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, y, "Kavach Scan Report")
    y -= 28
    c.setFont("Helvetica", 10)
    c.drawString(72, y, f"Target: {target}")
    y -= 16
    c.drawString(72, y, f"Generated: {datetime.now(timezone.utc).isoformat()}")
    y -= 24
    for line in summary.splitlines()[:40]:
        c.drawString(72, y, line[:90])
        y -= 14
        if y < 72:
            c.showPage()
            y = h - 72
    c.showPage()
    c.save()
    return buf.getvalue()


def run_nmap_or_mock(target: str) -> Tuple[str, str, str]:
    """
    Returns (status, raw_xml, pdf_b64)
    - status: 'completed' if real nmap ran, 'mocked' if fallback used
    """
    nmap_path = shutil.which("nmap")
    if nmap_path:
        try:
            # -oX - : write XML to stdout ; -T4 faster ; -Pn skip host discovery to avoid firewall drop
            proc = subprocess.run(
                [nmap_path, "-oX", "-", "-T4", "-Pn", target],
                capture_output=True,
                text=True,
                timeout=180,
                check=True,
            )
            raw_xml = proc.stdout
            summary = f"Nmap executed at {datetime.now(timezone.utc).isoformat()}\nTarget: {target}\nBytes: {len(raw_xml)}"
            pdf_bytes = _gen_pdf_bytes(target, summary)
            return "completed", raw_xml, base64.b64encode(pdf_bytes).decode("ascii")
        except Exception as e:
            # fall through to mock
            err = str(e)
    # mock path (no nmap available or failed)
    raw_xml = f"""<?xml version="1.0"?>
<nmaprun>
  <target>{target}</target>
  <note>mock scan</note>
  <ports><port protocol="tcp" portid="80"><state state="open"/></port></ports>
</nmaprun>"""
    summary = f"Mock scan at {datetime.now(timezone.utc).isoformat()} for {target}"
    pdf_bytes = _gen_pdf_bytes(target, summary)
    return "mocked", raw_xml, base64.b64encode(pdf_bytes).decode("ascii")
