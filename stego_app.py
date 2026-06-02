"""
Steganography Tool - Web Version (Flask)
Runs in your browser — no display issues!
Usage: python3 stego_app.py  →  open http://localhost:5000
"""

from flask import Flask, request, send_file, render_template_string
from PIL import Image
import io, os, base64

app = Flask(__name__)

# ── Core LSB logic ──────────────────────────────────────────────────────────

def encode_message(img: Image.Image, message: str) -> Image.Image:
    img = img.convert("RGB")
    pixels = list(img.getdata())
    message += "$$END$$"
    bits = ''.join(format(ord(c), '08b') for c in message)
    if len(bits) > len(pixels) * 3:
        raise ValueError("Message too long for this image!")
    new_pixels, idx = [], 0
    for r, g, b in pixels:
        if idx < len(bits): r = (r & ~1) | int(bits[idx]); idx += 1
        if idx < len(bits): g = (g & ~1) | int(bits[idx]); idx += 1
        if idx < len(bits): b = (b & ~1) | int(bits[idx]); idx += 1
        new_pixels.append((r, g, b))
    out = Image.new("RGB", img.size)
    out.putdata(new_pixels)
    return out

def decode_message(img: Image.Image) -> str:
    img = img.convert("RGB")
    bits = ''.join(str(c & 1) for px in img.getdata() for c in px)
    msg = ""
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8: break
        msg += chr(int(byte, 2))
        if msg.endswith("$$END$$"):
            return msg[:-7]
    return "⚠️ No hidden message found."

# ── HTML template ────────────────────────────────────────────────────────────

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🔐 Steganography Tool</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #090c10;
    color: #c9d1d9;
    font-family: 'Rajdhani', sans-serif;
    min-height: 100vh;
    background-image: radial-gradient(ellipse at 20% 50%, #0d2137 0%, transparent 60%),
                      radial-gradient(ellipse at 80% 20%, #0a1f0a 0%, transparent 50%);
  }
  .header {
    text-align: center;
    padding: 40px 20px 20px;
    border-bottom: 1px solid #21262d;
  }
  .header h1 {
    font-family: 'Share Tech Mono', monospace;
    font-size: 2.2rem;
    color: #58a6ff;
    letter-spacing: 3px;
  }
  .header p { color: #8b949e; margin-top: 8px; font-size: 1rem; letter-spacing: 1px; }

  .container { max-width: 860px; margin: 40px auto; padding: 0 20px; }

  .tabs { display: flex; gap: 4px; margin-bottom: 0; }
  .tab-btn {
    flex: 1; padding: 14px; border: none; cursor: pointer;
    font-family: 'Share Tech Mono', monospace; font-size: 1rem;
    letter-spacing: 2px; transition: all 0.2s;
    background: #161b22; color: #8b949e;
    border-radius: 8px 8px 0 0;
  }
  .tab-btn.active { background: #1f2937; color: #58a6ff; border-bottom: 2px solid #58a6ff; }

  .card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 0 0 12px 12px;
    padding: 32px;
  }

  .tab-content { display: none; }
  .tab-content.active { display: block; }

  label { display: block; margin-bottom: 6px; color: #8b949e;
          font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; letter-spacing: 1px; }

  .file-row { display: flex; gap: 10px; align-items: center; margin-bottom: 20px; }
  .file-name {
    flex: 1; padding: 10px 14px; background: #21262d;
    border: 1px solid #30363d; border-radius: 6px;
    color: #8b949e; font-family: 'Share Tech Mono', monospace; font-size: 0.85rem;
  }
  input[type="file"] { display: none; }
  .browse-btn {
    padding: 10px 20px; background: #238636; color: white; border: none;
    border-radius: 6px; cursor: pointer; font-family: 'Rajdhani', sans-serif;
    font-weight: 700; font-size: 0.95rem; letter-spacing: 1px; transition: background 0.2s;
  }
  .browse-btn:hover { background: #2ea043; }

  textarea {
    width: 100%; padding: 12px 14px; background: #21262d;
    border: 1px solid #30363d; border-radius: 6px;
    color: #c9d1d9; font-family: 'Share Tech Mono', monospace;
    font-size: 0.9rem; resize: vertical; min-height: 100px;
    outline: none; margin-bottom: 20px;
  }
  textarea:focus { border-color: #58a6ff; }

  .action-btn {
    width: 100%; padding: 16px; border: none; border-radius: 8px;
    font-family: 'Share Tech Mono', monospace; font-size: 1.1rem;
    letter-spacing: 3px; cursor: pointer; transition: all 0.2s;
    background: #58a6ff; color: #090c10; font-weight: bold;
  }
  .action-btn:hover { background: #79b8ff; transform: translateY(-1px); }
  .action-btn:active { transform: translateY(0); }

  .result-box {
    margin-top: 20px; padding: 16px; background: #0d1117;
    border: 1px solid #3fb950; border-radius: 8px;
    font-family: 'Share Tech Mono', monospace; font-size: 0.95rem;
    color: #3fb950; display: none; word-break: break-all;
  }
  .error-box {
    margin-top: 20px; padding: 16px; background: #0d1117;
    border: 1px solid #f85149; border-radius: 8px;
    font-family: 'Share Tech Mono', monospace; font-size: 0.9rem;
    color: #f85149; display: none;
  }
  .preview-img {
    max-width: 100%; max-height: 200px; border-radius: 8px;
    margin-top: 12px; border: 1px solid #30363d; display: none;
  }
  .download-btn {
    display: none; margin-top: 14px; padding: 12px 24px;
    background: #238636; color: white; border: none; border-radius: 6px;
    font-family: 'Share Tech Mono', monospace; font-size: 0.9rem;
    cursor: pointer; letter-spacing: 1px; text-decoration: none;
    transition: background 0.2s;
  }
  .download-btn:hover { background: #2ea043; }

  {% if flash %}.flash {
    padding: 12px 16px; border-radius: 6px; margin-bottom: 20px;
    font-family: 'Share Tech Mono', monospace; font-size: 0.9rem;
    background: #{{ 'f85149' if flash_type == 'error' else '3fb950' }}22;
    border: 1px solid #{{ 'f85149' if flash_type == 'error' else '3fb950' }};
    color: #{{ 'f85149' if flash_type == 'error' else '3fb950' }};
  }{% endif %}

  .divider { border: none; border-top: 1px solid #21262d; margin: 24px 0; }
  .tip { color: #8b949e; font-size: 0.85rem; margin-top: 10px; font-family: 'Share Tech Mono', monospace; }
</style>
</head>
<body>

<div class="header">
  <h1>🔐 STEGANOGRAPHY TOOL</h1>
  <p>Hide secret messages inside images using LSB Technique</p>
</div>

<div class="container">
  <div class="tabs">
    <button class="tab-btn active" onclick="switchTab('encode')">🔒 ENCODE</button>
    <button class="tab-btn" onclick="switchTab('decode')">🔓 DECODE</button>
  </div>

  <div class="card">

    <!-- ENCODE TAB -->
    <div id="encode" class="tab-content active">
      {% if encode_error %}
      <div style="padding:12px 16px;border-radius:6px;margin-bottom:20px;background:#f8514922;border:1px solid #f85149;color:#f85149;font-family:'Share Tech Mono',monospace;font-size:0.9rem;">
        ❌ {{ encode_error }}
      </div>
      {% endif %}
      {% if encode_success %}
      <div style="padding:12px 16px;border-radius:6px;margin-bottom:20px;background:#3fb95022;border:1px solid #3fb950;color:#3fb950;font-family:'Share Tech Mono',monospace;font-size:0.9rem;">
        ✅ Message hidden! Download your stego image below.
      </div>
      {% endif %}

      <form method="POST" action="/encode" enctype="multipart/form-data">
        <label>COVER IMAGE (PNG/JPG)</label>
        <div class="file-row">
          <span class="file-name" id="enc-name">No image selected...</span>
          <label for="enc-file" class="browse-btn">Browse</label>
          <input type="file" id="enc-file" name="image" accept="image/*" onchange="showName(this,'enc-name')" required>
        </div>

        <label>SECRET MESSAGE</label>
        <textarea name="message" placeholder="Type your secret message here..." required></textarea>

        <button type="submit" class="action-btn">🔒 HIDE MESSAGE IN IMAGE</button>
      </form>

      {% if encode_success %}
      <a href="/download" class="download-btn" style="display:inline-block;">⬇ Download Stego Image</a>
      {% endif %}

      <p class="tip">💡 Tip: Use PNG for best results. JPEG compression may corrupt hidden data.</p>
    </div>

    <!-- DECODE TAB -->
    <div id="decode" class="tab-content">
      <form method="POST" action="/decode" enctype="multipart/form-data">
        <label>STEGO IMAGE (image with hidden message)</label>
        <div class="file-row">
          <span class="file-name" id="dec-name">No image selected...</span>
          <label for="dec-file" class="browse-btn">Browse</label>
          <input type="file" id="dec-file" name="image" accept="image/*" onchange="showName(this,'dec-name')" required>
        </div>
        <button type="submit" class="action-btn">🔓 REVEAL HIDDEN MESSAGE</button>
      </form>

      {% if decoded_message %}
      <div style="margin-top:20px;padding:16px;background:#0d1117;border:1px solid #3fb950;border-radius:8px;font-family:'Share Tech Mono',monospace;font-size:0.95rem;color:#3fb950;">
        🔓 {{ decoded_message }}
      </div>
      {% endif %}
      {% if decode_error %}
      <div style="margin-top:20px;padding:16px;background:#0d1117;border:1px solid #f85149;border-radius:8px;font-family:'Share Tech Mono',monospace;font-size:0.9rem;color:#f85149;">
        ❌ {{ decode_error }}
      </div>
      {% endif %}
    </div>

  </div>
</div>

<script>
  function switchTab(tab) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(tab).classList.add('active');
    event.target.classList.add('active');
  }
  function showName(input, targetId) {
    document.getElementById(targetId).textContent = input.files[0]?.name || 'No image selected...';
  }
</script>
</body>
</html>
"""

# ── Routes ───────────────────────────────────────────────────────────────────

stego_image_buffer = None

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/encode", methods=["POST"])
def encode_route():
    global stego_image_buffer
    try:
        file = request.files["image"]
        message = request.form["message"].strip()
        if not message:
            return render_template_string(HTML, encode_error="Message cannot be empty.")
        img = Image.open(file.stream)
        result = encode_message(img, message)
        buf = io.BytesIO()
        result.save(buf, format="PNG")
        buf.seek(0)
        stego_image_buffer = buf.read()
        return render_template_string(HTML, encode_success=True)
    except Exception as e:
        return render_template_string(HTML, encode_error=str(e))

@app.route("/decode", methods=["POST"])
def decode_route():
    try:
        file = request.files["image"]
        img = Image.open(file.stream)
        msg = decode_message(img)
        return render_template_string(HTML, decoded_message=msg, active_tab="decode")
    except Exception as e:
        return render_template_string(HTML, decode_error=str(e), active_tab="decode")

@app.route("/download")
def download():
    global stego_image_buffer
    if not stego_image_buffer:
        return "No image available", 404
    return send_file(
        io.BytesIO(stego_image_buffer),
        mimetype="image/png",
        as_attachment=True,
        download_name="stego_output.png"
    )

if __name__ == "__main__":
    print("\n🔐 Steganography Tool is running!")
    print("👉 Open your browser and go to: http://localhost:5000\n")
    app.run(debug=False, port=5000)
