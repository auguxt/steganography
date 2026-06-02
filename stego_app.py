"""
StegoVault — Steganography Tool
Usage: python3 stego_new.py  →  open http://localhost:5000
"""

from flask import Flask, request, jsonify, send_file, render_template_string
from PIL import Image
import io
import uuid

app = Flask(__name__)

# ─────────────────────────────────────────────────────────────────────────

def encode_message(img: Image.Image, message: str) -> Image.Image:
    img = img.convert("RGB")
    pixels = list(img.getdata())
    message += "$$END$$"
    bits = ''.join(format(ord(c), '08b') for c in message)
    if len(bits) > len(pixels) * 3:
        raise ValueError(f"Message too long! Max {len(pixels) * 3 // 8} characters.")
    new_pixels = []
    bit_idx = 0
    for r, g, b in pixels:
        if bit_idx < len(bits): r = (r & ~1) | int(bits[bit_idx]); bit_idx += 1
        if bit_idx < len(bits): g = (g & ~1) | int(bits[bit_idx]); bit_idx += 1
        if bit_idx < len(bits): b = (b & ~1) | int(bits[bit_idx]); bit_idx += 1
        new_pixels.append((r, g, b))
    result = Image.new("RGB", img.size)
    result.putdata(new_pixels)
    return result

def decode_message(img: Image.Image) -> str:
    img = img.convert("RGB")
    bits = ''.join(str(c & 1) for px in img.getdata() for c in px)
    message = ""
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8: break
        message += chr(int(byte, 2))
        if message.endswith("$$END$$"):
            return message[:-7]
    return None

# ─────────────────────────────────────────────────────────────────────────

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>StegoVault — Hide & Reveal</title>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {
  --bg:       #080c14;
  --surface:  #0d1320;
  --card:     #111827;
  --border:   #1e293b;
  --border2:  #243044;
  --cyan:     #06d6c7;
  --cyan-dim: #06d6c720;
  --cyan-mid: #06d6c740;
  --violet:   #818cf8;
  --violet-dim:#818cf815;
  --amber:    #fbbf24;
  --red:      #f87171;
  --green:    #34d399;
  --text:     #e2e8f0;
  --text-muted:#64748b;
  --text-dim: #94a3b8;
  --glow:     0 0 30px #06d6c730;
  --glow-sm:  0 0 12px #06d6c720;
}

*, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }

html { scroll-behavior: smooth; }

body {
  font-family: 'Outfit', sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  overflow-x: hidden;
}

/* ── Animated background grid ── */
body::before {
  content: '';
  position: fixed; inset: 0; z-index: 0;
  background-image:
    linear-gradient(var(--border) 1px, transparent 1px),
    linear-gradient(90deg, var(--border) 1px, transparent 1px);
  background-size: 44px 44px;
  opacity: 0.35;
  pointer-events: none;
}

body::after {
  content: '';
  position: fixed; inset: 0; z-index: 0;
  background: radial-gradient(ellipse 70% 50% at 20% 10%, #06d6c710 0%, transparent 60%),
              radial-gradient(ellipse 60% 50% at 80% 90%, #818cf810 0%, transparent 60%);
  pointer-events: none;
}

.page-wrap {
  position: relative; z-index: 1;
  max-width: 860px;
  margin: 0 auto;
  padding: 40px 24px 80px;
}

/* ── Header ── */
.hero {
  text-align: center;
  padding: 60px 0 52px;
  animation: fadeDown 0.7s ease both;
}

.hero-badge {
  display: inline-flex; align-items: center; gap: 8px;
  background: var(--cyan-dim);
  border: 1px solid var(--cyan-mid);
  color: var(--cyan);
  font-size: 0.75rem; font-weight: 600;
  letter-spacing: 0.12em; text-transform: uppercase;
  padding: 5px 14px; border-radius: 100px;
  margin-bottom: 22px;
}

.hero-badge span { width:6px; height:6px; border-radius:50%; background:var(--cyan); animation: pulse 2s infinite; }

.hero h1 {
  font-size: clamp(2.4rem, 5vw, 3.6rem);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.03em;
  background: linear-gradient(135deg, #e2e8f0 30%, var(--cyan) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 16px;
}

.hero p {
  color: var(--text-muted);
  font-size: 1.05rem; font-weight: 300;
  max-width: 420px; margin: 0 auto 0;
  line-height: 1.65;
}

/* ── Tab switcher ── */
.tabs {
  display: flex; gap: 6px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 5px;
  margin-bottom: 32px;
  animation: fadeUp 0.6s 0.15s ease both;
}

.tab-btn {
  flex: 1; padding: 13px;
  border: none; border-radius: 10px;
  background: transparent;
  color: var(--text-muted);
  font-family: 'Outfit', sans-serif;
  font-size: 0.95rem; font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  display: flex; align-items: center; justify-content: center; gap: 8px;
}

.tab-btn:hover { color: var(--text); background: var(--border); }

.tab-btn.active {
  background: linear-gradient(135deg, #0f2027, #0d1f2d);
  color: var(--cyan);
  border: 1px solid var(--cyan-mid);
  box-shadow: var(--glow-sm);
}

/* ── Cards ── */
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 36px;
  display: none;
  animation: fadeUp 0.4s ease both;
}

.card.active { display: block; }

.card-header {
  display: flex; align-items: center; gap: 14px;
  margin-bottom: 32px;
}

.card-icon {
  width: 46px; height: 46px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.icon-encode { background: linear-gradient(135deg, #06d6c720, #06d6c710); border: 1px solid var(--cyan-mid); }
.icon-decode { background: linear-gradient(135deg, #818cf820, #818cf810); border: 1px solid #818cf840; }

.card-header h2 { font-size: 1.3rem; font-weight: 700; }
.card-header p  { color: var(--text-muted); font-size: 0.875rem; margin-top: 2px; }

/* ── Field labels ── */
.field { margin-bottom: 24px; }

.field-label {
  display: flex; align-items: center; gap: 8px;
  font-size: 0.8rem; font-weight: 600;
  letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--text-dim);
  margin-bottom: 10px;
}

.field-label::before {
  content: '';
  display: block; width: 3px; height: 14px;
  border-radius: 2px;
}

.field-label.lc::before { background: var(--cyan); }
.field-label.lv::before { background: var(--violet); }

/* ── Drop zone ── */
input[type="file"] { display: none; }

.drop-zone {
  border: 2px dashed var(--border2);
  border-radius: 14px;
  padding: 36px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s ease;
  background: var(--surface);
  position: relative;
  overflow: hidden;
}

.drop-zone::before {
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(ellipse at 50% 0%, var(--cyan-dim), transparent 70%);
  opacity: 0; transition: opacity 0.3s;
}

.drop-zone:hover::before,
.drop-zone.drag-over::before { opacity: 1; }

.drop-zone:hover { border-color: var(--cyan); transform: translateY(-2px); }
.drop-zone.drag-over { border-color: var(--cyan); border-style: solid; transform: scale(1.01); }

.drop-icon {
  width: 52px; height: 52px; border-radius: 14px;
  background: var(--cyan-dim); border: 1px solid var(--cyan-mid);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.4rem; margin: 0 auto 14px;
}

.drop-zone h3 { font-size: 0.95rem; font-weight: 600; color: var(--text); margin-bottom: 5px; }
.drop-zone p  { font-size: 0.82rem; color: var(--text-muted); }

/* ── File pill (selected file indicator) ── */
.file-pill {
  display: none; align-items: center; gap: 10px;
  margin-top: 12px;
  background: var(--surface);
  border: 1px solid var(--border2);
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 0.85rem;
}

.file-pill.show { display: flex; }

.file-pill-icon {
  width: 30px; height: 30px; border-radius: 8px;
  background: var(--cyan-dim); border: 1px solid var(--cyan-mid);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.9rem; flex-shrink: 0;
}

.file-pill-name { color: var(--text); font-weight: 500; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.file-pill-size { color: var(--text-muted); font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; flex-shrink: 0; }

.file-pill-remove {
  width: 24px; height: 24px; border-radius: 6px;
  background: #f8717120; border: 1px solid #f8717140;
  color: var(--red); font-size: 0.8rem; font-weight: 700;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; transition: all 0.2s;
}
.file-pill-remove:hover { background: #f8717130; transform: scale(1.1); }

/* ── Preview image ── */
.preview-wrap {
  display: none; position: relative;
  margin-top: 14px; text-align: center;
}
.preview-wrap.show { display: block; }

.preview-img {
  max-width: 100%; max-height: 220px;
  border-radius: 12px;
  border: 1px solid var(--border2);
  box-shadow: 0 4px 20px #00000050;
}

/* ── Textarea ── */
textarea {
  width: 100%;
  background: var(--surface);
  border: 1.5px solid var(--border2);
  border-radius: 12px;
  padding: 14px 16px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9rem;
  color: var(--text);
  resize: vertical; min-height: 100px;
  transition: border-color 0.2s, box-shadow 0.2s;
  outline: none;
}

textarea:focus {
  border-color: var(--cyan);
  box-shadow: 0 0 0 3px var(--cyan-dim);
}

textarea::placeholder { color: var(--text-muted); }

.char-row {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 8px;
}

.char-count { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: var(--text-muted); }
.char-warn  { color: var(--amber); }

/* ── Buttons ── */
.btn-row { display: flex; gap: 10px; margin-top: 28px; }

.btn {
  padding: 14px 22px; border-radius: 11px; border: none;
  font-family: 'Outfit', sans-serif; font-size: 0.95rem; font-weight: 600;
  cursor: pointer; transition: all 0.25s ease;
  display: flex; align-items: center; gap: 8px; justify-content: center;
}

.btn-primary-cyan {
  flex: 1;
  background: linear-gradient(135deg, #06d6c7, #05b8aa);
  color: #080c14;
  box-shadow: 0 4px 18px #06d6c730;
}
.btn-primary-cyan:hover { transform: translateY(-2px); box-shadow: 0 8px 28px #06d6c745; }
.btn-primary-cyan:disabled { opacity: 0.45; cursor: not-allowed; transform: none; box-shadow: none; }

.btn-primary-violet {
  flex: 1;
  background: linear-gradient(135deg, #818cf8, #6366f1);
  color: #fff;
  box-shadow: 0 4px 18px #818cf830;
}
.btn-primary-violet:hover { transform: translateY(-2px); box-shadow: 0 8px 28px #818cf845; }
.btn-primary-violet:disabled { opacity: 0.45; cursor: not-allowed; transform: none; box-shadow: none; }

.btn-ghost {
  background: var(--surface); color: var(--text-muted);
  border: 1px solid var(--border2);
  padding: 14px 18px;
}
.btn-ghost:hover { color: var(--text); border-color: var(--border); background: var(--border); }

/* ── Result panels ── */
.result {
  display: none; margin-top: 24px;
  border-radius: 14px; padding: 18px 20px;
  border: 1px solid;
  animation: fadeUp 0.3s ease;
}
.result.show { display: block; }

.result-success { background: #05271e; border-color: #34d39940; color: var(--green); }
.result-error   { background: #2d0f0f; border-color: #f8717140; color: var(--red); }
.result-info    { background: #0f1a2d; border-color: #818cf840; color: var(--violet); }

/* ── Download button ── */
.btn-download {
  display: inline-flex; align-items: center; gap: 8px;
  margin-top: 14px;
  padding: 12px 22px; border-radius: 10px; border: none;
  background: linear-gradient(135deg, var(--green), #059669);
  color: #fff; font-family: 'Outfit', sans-serif;
  font-size: 0.9rem; font-weight: 600;
  text-decoration: none; cursor: pointer;
  box-shadow: 0 4px 14px #34d39930;
  transition: all 0.25s;
}
.btn-download:hover { transform: translateY(-2px); box-shadow: 0 8px 22px #34d39940; }

/* ── Decoded message box ── */
.decoded-box {
  background: var(--surface);
  border: 1px solid var(--border2);
  border-radius: 10px;
  padding: 16px;
  margin-top: 14px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.875rem;
  color: var(--text);
  word-break: break-all; white-space: pre-wrap;
  line-height: 1.6;
  max-height: 200px; overflow-y: auto;
}

.btn-copy {
  display: inline-flex; align-items: center; gap: 8px;
  margin-top: 12px;
  padding: 10px 18px; border-radius: 9px; border: 1px solid var(--cyan-mid);
  background: var(--cyan-dim); color: var(--cyan);
  font-family: 'Outfit', sans-serif; font-size: 0.875rem; font-weight: 600;
  cursor: pointer; transition: all 0.2s;
}
.btn-copy:hover { background: var(--cyan-mid); }

/* ── Info tip ── */
.tip {
  display: flex; gap: 12px; align-items: flex-start;
  margin-top: 24px; padding: 14px 16px;
  background: #0f1a10; border: 1px solid #34d39925;
  border-radius: 12px;
  font-size: 0.85rem; color: #6ee7b7;
  line-height: 1.55;
}
.tip-icon { font-size: 1rem; flex-shrink: 0; margin-top: 1px; }

/* ── Spinner ── */
.spinner {
  width: 16px; height: 16px;
  border: 2.5px solid rgba(0,0,0,0.25);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

/* ── Footer ── */
.footer {
  text-align: center; margin-top: 60px;
  color: var(--text-muted); font-size: 0.82rem;
  animation: fadeUp 0.6s 0.4s ease both;
}

.footer a { color: var(--cyan); text-decoration: none; }
.footer a:hover { text-decoration: underline; }

/* ── Animations ── */
@keyframes fadeDown { from { opacity:0; transform:translateY(-18px); } to { opacity:1; transform:none; } }
@keyframes fadeUp   { from { opacity:0; transform:translateY(14px);  } to { opacity:1; transform:none; } }
@keyframes spin     { to   { transform: rotate(360deg); } }
@keyframes pulse    { 0%,100%{ opacity:1; } 50%{ opacity:0.35; } }
</style>
</head>
<body>

<div class="page-wrap">

  <!-- Hero -->
  <div class="hero">
    <div class="hero-badge"><span></span> LSB Steganography</div>
    <h1>StegoVault</h1>
    <p>Invisibly embed secret messages inside ordinary images — no trace, no noise, no suspicion.</p>
  </div>

  <!-- Tabs -->
  <div class="tabs">
    <button class="tab-btn active" id="tabEncode" onclick="switchTab('encode')">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
      Hide a Message
    </button>
    <button class="tab-btn" id="tabDecode" onclick="switchTab('decode')">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 9.9-1"/><line x1="12" y1="15" x2="12" y2="18"/></svg>
      Reveal a Message
    </button>
  </div>

  <!-- ── ENCODE CARD ── -->
  <div class="card active" id="cardEncode">
    <div class="card-header">
      <div class="card-icon icon-encode">🔒</div>
      <div>
        <h2>Hide Your Secret</h2>
        <p>Your message is written into the image's least-significant bits — invisible to the naked eye.</p>
      </div>
    </div>

    <!-- Image upload -->
    <div class="field">
      <div class="field-label lc">Cover Image</div>
      <input type="file" id="encodeFile" accept="image/*">
      <div class="drop-zone" id="encodeDropZone">
        <div class="drop-icon">🖼️</div>
        <h3>Drop image here or click to browse</h3>
        <p>PNG recommended · JPG also works · BMP supported</p>
      </div>
      <div class="file-pill" id="encodeFilePill">
        <div class="file-pill-icon">🖼️</div>
        <span class="file-pill-name" id="encodeFileName">—</span>
        <span class="file-pill-size" id="encodeFileSize">—</span>
        <button class="file-pill-remove" id="encodeRemoveBtn" title="Remove">✕</button>
      </div>
      <div class="preview-wrap" id="encodePreviewWrap">
        <img class="preview-img" id="encodePreview" alt="">
      </div>
    </div>

    <!-- Message -->
    <div class="field">
      <div class="field-label lc">Secret Message</div>
      <textarea id="encodeMessage" placeholder="Type your secret message here…" rows="4"></textarea>
      <div class="char-row">
        <span class="char-count" id="charCount">0 characters</span>
        <span class="char-count">PNG supports millions of chars</span>
      </div>
    </div>

    <div class="btn-row">
      <button class="btn btn-primary-cyan" id="encodeBtn">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
        Hide Message
      </button>
      <button class="btn btn-ghost" id="encodeClearBtn">Reset</button>
    </div>

    <div id="encodeResult" class="result"></div>

    <div class="tip">
      <span class="tip-icon">💡</span>
      <span><strong>Pro tip:</strong> Always save the output as PNG. JPEG re-compression destroys the hidden bits and your message will be lost.</span>
    </div>
  </div>

  <!-- ── DECODE CARD ── -->
  <div class="card" id="cardDecode">
    <div class="card-header">
      <div class="card-icon icon-decode">🔓</div>
      <div>
        <h2>Reveal the Secret</h2>
        <p>Upload any image encoded with StegoVault and extract the hidden message instantly.</p>
      </div>
    </div>

    <!-- Image upload -->
    <div class="field">
      <div class="field-label lv">Stego Image</div>
      <input type="file" id="decodeFile" accept="image/*">
      <div class="drop-zone" id="decodeDropZone">
        <div class="drop-icon" style="background:var(--violet-dim);border-color:#818cf840;">🔍</div>
        <h3>Drop your stego image here</h3>
        <p>Any image that was encoded with StegoVault</p>
      </div>
      <div class="file-pill" id="decodeFilePill">
        <div class="file-pill-icon">🔍</div>
        <span class="file-pill-name" id="decodeFileName">—</span>
        <span class="file-pill-size" id="decodeFileSize">—</span>
        <button class="file-pill-remove" id="decodeRemoveBtn" title="Remove">✕</button>
      </div>
      <div class="preview-wrap" id="decodePreviewWrap">
        <img class="preview-img" id="decodePreview" alt="">
      </div>
    </div>

    <div class="btn-row">
      <button class="btn btn-primary-violet" id="decodeBtn">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        Reveal Message
      </button>
      <button class="btn btn-ghost" id="decodeClearBtn">Reset</button>
    </div>

    <div id="decodeResult" class="result"></div>
  </div>

  <!-- Footer -->
  <div class="footer">
    <p>StegoVault · LSB Image Steganography · <a href="https://github.com/auguxt/steganography" target="_blank">GitHub ↗</a></p>
  </div>

</div><!-- /page-wrap -->

<script>
// ── Tab switching ──────────────────────────────────────────────────────────

function switchTab(tab) {
  document.getElementById('cardEncode').classList.toggle('active', tab === 'encode');
  document.getElementById('cardDecode').classList.toggle('active', tab === 'decode');
  document.getElementById('tabEncode').classList.toggle('active', tab === 'encode');
  document.getElementById('tabDecode').classList.toggle('active', tab === 'decode');
}

// ── Helpers ───────────────────────────────────────────────────────────────

function esc(t) {
  const d = document.createElement('div');
  d.textContent = t;
  return d.innerHTML;
}

function showResult(el, type, html) {
  el.className = 'result show result-' + type;
  el.innerHTML = html;
}

// ── File upload setup ──────────────────────────────────────────────────────

function setupUpload(cfg) {
  const dz    = document.getElementById(cfg.dropZone);
  const input = document.getElementById(cfg.input);
  const pill  = document.getElementById(cfg.pill);
  const fname = document.getElementById(cfg.name);
  const fsize = document.getElementById(cfg.size);
  const wrap  = document.getElementById(cfg.wrap);
  const img   = document.getElementById(cfg.img);
  const rmBtn = document.getElementById(cfg.remove);

  dz.addEventListener('click', function(e) { e.preventDefault(); e.stopPropagation(); input.click(); });

  dz.addEventListener('dragover',  function(e) { e.preventDefault(); e.stopPropagation(); dz.classList.add('drag-over'); });
  dz.addEventListener('dragleave', function(e) { e.preventDefault(); dz.classList.remove('drag-over'); });
  dz.addEventListener('drop', function(e) {
    e.preventDefault(); e.stopPropagation();
    dz.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    if (files && files.length) {
      try { const dt = new DataTransfer(); dt.items.add(files[0]); input.files = dt.files; } catch(_) {}
      showFile(files[0], pill, fname, fsize, wrap, img);
    }
  });

  input.addEventListener('change', function() {
    if (input.files && input.files.length) showFile(input.files[0], pill, fname, fsize, wrap, img);
  });

  rmBtn.addEventListener('click', function(e) {
    e.stopPropagation();
    clearUpload(input, pill, wrap, img);
    if (cfg.onClear) cfg.onClear();
  });
}

function showFile(file, pill, fname, fsize, wrap, img) {
  fname.textContent = file.name;
  fsize.textContent = (file.size / 1024).toFixed(1) + ' KB';
  pill.classList.add('show');
  const reader = new FileReader();
  reader.onload = function(e) {
    img.src = e.target.result;
    wrap.classList.add('show');
  };
  reader.readAsDataURL(file);
}

function clearUpload(input, pill, wrap, img) {
  input.value = '';
  pill.classList.remove('show');
  wrap.classList.remove('show');
  img.src = '';
}

// ── Init uploads ───────────────────────────────────────────────────────────

setupUpload({
  dropZone: 'encodeDropZone', input: 'encodeFile',
  pill: 'encodeFilePill', name: 'encodeFileName', size: 'encodeFileSize',
  wrap: 'encodePreviewWrap', img: 'encodePreview', remove: 'encodeRemoveBtn',
  onClear: function() { document.getElementById('encodeResult').classList.remove('show'); }
});

setupUpload({
  dropZone: 'decodeDropZone', input: 'decodeFile',
  pill: 'decodeFilePill', name: 'decodeFileName', size: 'decodeFileSize',
  wrap: 'decodePreviewWrap', img: 'decodePreview', remove: 'decodeRemoveBtn',
  onClear: function() { document.getElementById('decodeResult').classList.remove('show'); }
});

// ── Char count ─────────────────────────────────────────────────────────────

document.getElementById('encodeMessage').addEventListener('input', function() {
  const n = this.value.length;
  const el = document.getElementById('charCount');
  el.textContent = n.toLocaleString() + ' character' + (n !== 1 ? 's' : '');
  el.className = 'char-count' + (n > 5000 ? ' char-warn' : '');
});

// ── Encode ─────────────────────────────────────────────────────────────────

document.getElementById('encodeBtn').addEventListener('click', function() {
  const input   = document.getElementById('encodeFile');
  const message = document.getElementById('encodeMessage').value.trim();
  const resultEl = document.getElementById('encodeResult');
  const btn = this;

  if (!input.files || !input.files.length) {
    showResult(resultEl, 'error', '⚠ Please choose a cover image first.');
    return;
  }
  if (!message) {
    showResult(resultEl, 'error', '⚠ Your secret message is empty!');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Hiding…';

  const fd = new FormData();
  fd.append('image', input.files[0]);
  fd.append('message', message);

  fetch('/api/encode', { method: 'POST', body: fd })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        showResult(resultEl, 'success',
          '✓ Message hidden successfully! Your image looks identical to the original.' +
          '<br><a class="btn-download" href="' + data.download_url + '" download>⬇ Download Stego Image</a>'
        );
      } else {
        showResult(resultEl, 'error', '✕ ' + data.error);
      }
    })
    .catch(e => showResult(resultEl, 'error', '✕ Network error: ' + e.message))
    .finally(() => {
      btn.disabled = false;
      btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg> Hide Message';
    });
});

document.getElementById('encodeClearBtn').addEventListener('click', function() {
  clearUpload(
    document.getElementById('encodeFile'),
    document.getElementById('encodeFilePill'),
    document.getElementById('encodePreviewWrap'),
    document.getElementById('encodePreview')
  );
  document.getElementById('encodeMessage').value = '';
  document.getElementById('charCount').textContent = '0 characters';
  document.getElementById('encodeResult').classList.remove('show');
});

// ── Decode ─────────────────────────────────────────────────────────────────

document.getElementById('decodeBtn').addEventListener('click', function() {
  const input   = document.getElementById('decodeFile');
  const resultEl = document.getElementById('decodeResult');
  const btn = this;

  if (!input.files || !input.files.length) {
    showResult(resultEl, 'error', '⚠ Please choose an image to decode.');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Scanning…';

  const fd = new FormData();
  fd.append('image', input.files[0]);

  fetch('/api/decode', { method: 'POST', body: fd })
    .then(r => r.json())
    .then(data => {
      if (data.success && data.message) {
        const msgId = 'msg-' + Date.now();
        showResult(resultEl, 'success',
          '✓ Hidden message found!' +
          '<div class="decoded-box" id="' + msgId + '">' + esc(data.message) + '</div>' +
          '<button class="btn-copy" id="copyBtn-' + msgId + '">📋 Copy to clipboard</button>'
        );
        document.getElementById('copyBtn-' + msgId).addEventListener('click', function() {
          const text = document.getElementById(msgId).textContent;
          navigator.clipboard.writeText(text).then(() => {
            this.textContent = '✓ Copied!';
            setTimeout(() => { this.innerHTML = '📋 Copy to clipboard'; }, 2000);
          });
        });
      } else if (data.error) {
        showResult(resultEl, 'error', '✕ ' + data.error);
      } else {
        showResult(resultEl, 'info', '🔍 No hidden message found in this image.');
      }
    })
    .catch(e => showResult(resultEl, 'error', '✕ Network error: ' + e.message))
    .finally(() => {
      btn.disabled = false;
      btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg> Reveal Message';
    });
});

document.getElementById('decodeClearBtn').addEventListener('click', function() {
  clearUpload(
    document.getElementById('decodeFile'),
    document.getElementById('decodeFilePill'),
    document.getElementById('decodePreviewWrap'),
    document.getElementById('decodePreview')
  );
  document.getElementById('decodeResult').classList.remove('show');
});
</script>

</body>
</html>
"""

# ─────────────────────────────────────────────────────────────────────────

encoded_images = {}

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/encode", methods=["POST"])
def api_encode():
    try:
        file    = request.files.get("image")
        message = request.form.get("message", "").strip()
        if not file or not message:
            return jsonify({"success": False, "error": "Image and message required"})
        img    = Image.open(file.stream)
        result = encode_message(img, message)
        buf    = io.BytesIO()
        result.save(buf, format="PNG")
        buf.seek(0)
        img_id = str(uuid.uuid4())[:8]
        encoded_images[img_id] = buf.getvalue()
        return jsonify({"success": True, "download_url": f"/download/{img_id}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/decode", methods=["POST"])
def api_decode():
    try:
        file = request.files.get("image")
        if not file:
            return jsonify({"success": False, "error": "Image required"})
        img     = Image.open(file.stream)
        message = decode_message(img)
        return jsonify({"success": True, "message": message})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/download/<img_id>")
def download(img_id):
    if img_id not in encoded_images:
        return "Image not found", 404
    return send_file(
        io.BytesIO(encoded_images[img_id]),
        mimetype="image/png",
        as_attachment=True,
        download_name="stego_image.png"
    )

if __name__ == "__main__":
    print("\n🔐 StegoVault is running!")
    print("👉 Open: http://localhost:5000\n")
    app.run(debug=False, port=5000)
