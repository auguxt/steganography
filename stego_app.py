"""
Steganography Tool - Simplified Version
Usage: python3 stego_app_improved.py  →  open http://localhost:5000
"""

from flask import Flask, request, jsonify, send_file, render_template_string
from PIL import Image
import io
import base64

app = Flask(__name__)

# ─────────────────────────────────────────────────────────────────────────

def encode_message(img: Image.Image, message: str) -> Image.Image:
    """Hide a message in image using LSB technique"""
    img = img.convert("RGB")
    pixels = list(img.getdata())
    
    # Add delimiter to mark end of message
    message += "$$END$$"
    bits = ''.join(format(ord(c), '08b') for c in message)
    
    # Check if message fits
    if len(bits) > len(pixels) * 3:
        raise ValueError(f"Message too long! Max {len(pixels) * 3 // 8} characters.")
    
    # Encode bits into LSB of pixels
    new_pixels = []
    bit_idx = 0
    for r, g, b in pixels:
        if bit_idx < len(bits): 
            r = (r & ~1) | int(bits[bit_idx])
            bit_idx += 1
        if bit_idx < len(bits): 
            g = (g & ~1) | int(bits[bit_idx])
            bit_idx += 1
        if bit_idx < len(bits): 
            b = (b & ~1) | int(bits[bit_idx])
            bit_idx += 1
        new_pixels.append((r, g, b))
    
    result = Image.new("RGB", img.size)
    result.putdata(new_pixels)
    return result

def decode_message(img: Image.Image) -> str:
    """Extract hidden message from image"""
    img = img.convert("RGB")
    bits = ''.join(str(c & 1) for px in img.getdata() for c in px)
    
    message = ""
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8:
            break
        message += chr(int(byte, 2))
        if message.endswith("$$END$$"):
            return message[:-7]  # Remove delimiter
    
    return None  # No message found

# ─────────────────────────────────────────────────────────────────────────

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Steganography Tool</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #faf7f2;
            min-height: 100vh;
            padding: 24px;
            color: #3d3935;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: #fff9f5;
            border-radius: 20px;
            box-shadow: 0 4px 24px rgba(200, 130, 100, 0.08);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #d87c5c 0%, #c56a4d 100%);
            color: white;
            padding: 50px 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.2em;
            margin-bottom: 8px;
            font-weight: 600;
        }
        
        .header p {
            opacity: 0.95;
            font-size: 1em;
            font-weight: 300;
        }
        
        .content {
            padding: 45px;
        }
        
        .section {
            margin-bottom: 50px;
        }
        
        .section:last-child {
            margin-bottom: 0;
        }
        
        .section h2 {
            font-size: 1.4em;
            color: #d87c5c;
            margin-bottom: 28px;
            font-weight: 600;
        }
        
        label {
            display: block;
            margin-bottom: 12px;
            font-weight: 500;
            color: #5a5651;
            font-size: 0.95em;
        }
        
        .file-input-wrapper {
            position: relative;
            margin-bottom: 28px;
        }
        
        .file-drop-zone {
            border: 2.5px dashed #d4a896;
            border-radius: 14px;
            padding: 45px 25px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background: #fef5f0;
        }
        
        .file-drop-zone:hover {
            border-color: #d87c5c;
            background: #fef0eb;
            transform: translateY(-2px);
        }
        
        .file-drop-zone.drag-over {
            border-color: #d87c5c;
            background: #fce8e0;
            transform: scale(1.02);
        }
        
        .file-drop-zone p {
            color: #d87c5c;
            font-weight: 600;
            margin-bottom: 6px;
            font-size: 1em;
        }
        
        .file-drop-zone small {
            color: #a09691;
            font-size: 0.9em;
        }
        
        .file-name {
            margin-top: 12px;
            padding: 12px 14px;
            background: #f5e8e0;
            border-radius: 8px;
            color: #d87c5c;
            font-size: 0.9em;
            display: none;
            border: 1px solid #e8d8cc;
        }
        
        .file-name.show {
            display: block;
        }
        
        input[type="file"] {
            display: none;
        }
        
        textarea {
            width: 100%;
            padding: 14px 16px;
            border: 1.5px solid #e8d8cc;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            font-size: 0.95em;
            resize: vertical;
            min-height: 90px;
            margin-bottom: 12px;
            transition: all 0.3s ease;
            background: #fff9f5;
            color: #3d3935;
        }
        
        textarea:focus {
            outline: none;
            border-color: #d87c5c;
            background: #fffcf9;
            box-shadow: 0 0 0 3px rgba(216, 124, 92, 0.08);
        }
        
        textarea::placeholder {
            color: #a09691;
        }
        
        .char-count {
            font-size: 0.85em;
            color: #a09691;
            margin-bottom: 18px;
        }
        
        .button-group {
            display: flex;
            gap: 12px;
        }
        
        button {
            flex: 1;
            padding: 14px 24px;
            border: none;
            border-radius: 10px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.95em;
            text-transform: none;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #d87c5c 0%, #c56a4d 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(216, 124, 92, 0.2);
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(216, 124, 92, 0.3);
        }
        
        .btn-primary:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .btn-secondary {
            background: #f5e8e0;
            color: #d87c5c;
            border: 1px solid #e8d8cc;
        }
        
        .btn-secondary:hover {
            background: #eee0d5;
            border-color: #d87c5c;
        }
        
        .btn-copy {
            background: #5ca383;
            color: white;
            flex: 0.35;
            box-shadow: 0 4px 12px rgba(92, 163, 131, 0.2);
        }
        
        .btn-copy:hover {
            background: #4d8f72;
            box-shadow: 0 6px 18px rgba(92, 163, 131, 0.3);
        }
        
        .result {
            margin-top: 24px;
            padding: 18px;
            border-radius: 10px;
            display: none;
            border: 1.5px solid;
        }
        
        .result.show {
            display: block;
        }
        
        .result.success {
            background: #eaf6f0;
            border-color: #5ca383;
            color: #2d5047;
        }
        
        .result.error {
            background: #fce8e0;
            border-color: #d87c5c;
            color: #6b3f35;
        }
        
        .result.info {
            background: #e8f3f9;
            border-color: #5b8fbc;
            color: #2d4860;
        }
        
        .preview-container {
            margin-top: 16px;
            text-align: center;
        }
        
        .preview-img {
            max-width: 100%;
            max-height: 200px;
            border-radius: 10px;
            border: 1px solid #e8d8cc;
            display: none;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        
        .preview-img.show {
            display: inline-block;
        }
        
        .decoded-message {
            background: #f5ede5;
            border: 1.5px solid #e8d8cc;
            border-radius: 10px;
            padding: 16px;
            margin-top: 16px;
            font-family: 'Courier New', monospace;
            word-break: break-all;
            white-space: pre-wrap;
            color: #3d3935;
            line-height: 1.5;
        }
        
        .divider {
            height: 1px;
            background: #e8d8cc;
            margin: 45px 0;
        }
        
        .tip {
            padding: 16px;
            background: #f9f3e8;
            border-left: 4px solid #d4a896;
            border-radius: 8px;
            font-size: 0.9em;
            color: #6b5e57;
            margin-top: 24px;
            line-height: 1.5;
        }
        
        .tip strong {
            color: #5a5651;
        }
        
        .spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 3px solid rgba(255,255,255,0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin-right: 8px;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <h1>✨ Hide & Reveal</h1>
        <p>Secret messages in your images</p>
    </div>
    
    <div class="content">
        
        <!-- ENCODE SECTION -->
        <div class="section">
            <h2>🔒 Hide a Secret</h2>
            
            <label>Choose Your Image</label>
            <div class="file-input-wrapper">
                <div class="file-drop-zone" id="encodeDropZone">
                    <p>📸 Drop image here or click to browse</p>
                    <small>PNG works best • JPG also okay</small>
                </div>
                <div class="file-name" id="encodeFileName"></div>
                <input type="file" id="encodeFile" accept="image/*">
                <div class="preview-container">
                    <img class="preview-img" id="encodePreview">
                </div>
            </div>
            
            <label>Your Secret Message</label>
            <textarea id="encodeMessage" placeholder="Write something you want to keep private..."></textarea>
            <div class="char-count"><span id="charCount">0</span> characters</div>
            
            <div class="button-group">
                <button class="btn-primary" onclick="encodeMessage()" id="encodeBtn">🔒 Hide It</button>
                <button class="btn-secondary" onclick="clearEncode()">Reset</button>
            </div>
            
            <div id="encodeResult" class="result"></div>
            
            <div class="tip">
                💡 <strong>Pro Tip:</strong> PNG files preserve your secret better since they don't compress. JPG might lose some data, but it still usually works fine.
            </div>
        </div>
        
        <div class="divider"></div>
        
        <!-- DECODE SECTION -->
        <div class="section">
            <h2>🔓 Reveal a Secret</h2>
            
            <label>Upload Your Stego Image</label>
            <div class="file-input-wrapper">
                <div class="file-drop-zone" id="decodeDropZone">
                    <p>📸 Drop image here or click to browse</p>
                    <small>Any image with a hidden message</small>
                </div>
                <div class="file-name" id="decodeFileName"></div>
                <input type="file" id="decodeFile" accept="image/*">
                <div class="preview-container">
                    <img class="preview-img" id="decodePreview">
                </div>
            </div>
            
            <div class="button-group">
                <button class="btn-primary" onclick="decodeMessage()" id="decodeBtn">🔓 Reveal It</button>
                <button class="btn-secondary" onclick="clearDecode()">Reset</button>
            </div>
            
            <div id="decodeResult" class="result"></div>
        </div>
        
    </div>
</div>

<script>
    // ─── File upload handling ─────────────────────────────────────
    
    function setupFileUpload(dropZoneId, fileInputId, fileNameId, previewId) {
        const dropZone = document.getElementById(dropZoneId);
        const fileInput = document.getElementById(fileInputId);
        const fileName = document.getElementById(fileNameId);
        const preview = document.getElementById(previewId);
        
        dropZone.onclick = () => fileInput.click();
        
        dropZone.ondragover = (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        };
        
        dropZone.ondragleave = () => dropZone.classList.remove('drag-over');
        
        dropZone.ondrop = (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                showFileInfo(fileInput, fileName, preview);
            }
        };
        
        fileInput.onchange = () => showFileInfo(fileInput, fileName, preview);
    }
    
    function showFileInfo(input, nameEl, previewEl) {
        const file = input.files[0];
        if (!file) return;
        
        nameEl.textContent = `✓ ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        nameEl.classList.add('show');
        
        const reader = new FileReader();
        reader.onload = (e) => {
            previewEl.src = e.target.result;
            previewEl.classList.add('show');
        };
        reader.readAsDataURL(file);
    }
    
    // ─── Encode functionality ─────────────────────────────────────
    
    document.getElementById('encodeMessage').oninput = (e) => {
        document.getElementById('charCount').textContent = e.target.value.length;
    };
    
    function encodeMessage() {
        const file = document.getElementById('encodeFile').files[0];
        const message = document.getElementById('encodeMessage').value.trim();
        const resultEl = document.getElementById('encodeResult');
        const btn = document.getElementById('encodeBtn');
        
        if (!file) {
            showResult(resultEl, 'error', '❌ Please pick an image first');
            return;
        }
        if (!message) {
            showResult(resultEl, 'error', '❌ Don\'t forget to write your message!');
            return;
        }
        
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span>Hiding...';
        
        const formData = new FormData();
        formData.append('image', file);
        formData.append('message', message);
        
        fetch('/api/encode', { method: 'POST', body: formData })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    const link = `<a href="${data.download_url}" style="color:#5ca383;text-decoration:none;font-weight:600;">📥 Download Your Image</a>`;
                    showResult(resultEl, 'success', `✅ Done! Your secret is hidden. ${link}`);
                } else {
                    showResult(resultEl, 'error', `❌ ${data.error}`);
                }
            })
            .catch(e => showResult(resultEl, 'error', `❌ ${e.message}`))
            .finally(() => {
                btn.disabled = false;
                btn.innerHTML = '🔒 Hide It';
            });
    }
    
    // ─── Decode functionality ─────────────────────────────────────
    
    function decodeMessage() {
        const file = document.getElementById('decodeFile').files[0];
        const resultEl = document.getElementById('decodeResult');
        const btn = document.getElementById('decodeBtn');
        
        if (!file) {
            showResult(resultEl, 'error', '❌ Please pick an image with a hidden message');
            return;
        }
        
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span>Revealing...';
        
        const formData = new FormData();
        formData.append('image', file);
        
        fetch('/api/decode', { method: 'POST', body: formData })
            .then(r => r.json())
            .then(data => {
                if (data.success && data.message) {
                    const html = `
                        ✅ Found it!
                        <div class="decoded-message">${escapeHtml(data.message)}</div>
                        <button class="btn-copy" onclick="copyToClipboard('${escapeHtml(data.message).replace(/'/g, "\\'")}')">📋 Copy</button>
                    `;
                    showResult(resultEl, 'success', html);
                } else {
                    showResult(resultEl, 'info', '⚠️ Hmm, no hidden message in this image');
                }
            })
            .catch(e => showResult(resultEl, 'error', `❌ ${e.message}`))
            .finally(() => {
                btn.disabled = false;
                btn.innerHTML = '🔓 Reveal It';
            });
    }
    
    // ─── Utilities ────────────────────────────────────────────────
    
    function showResult(el, type, html) {
        el.className = `result show ${type}`;
        el.innerHTML = html;
    }
    
    function clearEncode() {
        document.getElementById('encodeFile').value = '';
        document.getElementById('encodeMessage').value = '';
        document.getElementById('charCount').textContent = '0';
        document.getElementById('encodeFileName').classList.remove('show');
        document.getElementById('encodePreview').classList.remove('show');
        document.getElementById('encodeResult').classList.remove('show');
    }
    
    function clearDecode() {
        document.getElementById('decodeFile').value = '';
        document.getElementById('decodeFileName').classList.remove('show');
        document.getElementById('decodePreview').classList.remove('show');
        document.getElementById('decodeResult').classList.remove('show');
    }
    
    function copyToClipboard(text) {
        navigator.clipboard.writeText(text);
        alert('✅ Copied! You\'re all set.');
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // ─── Initialize ───────────────────────────────────────────────
    
    setupFileUpload('encodeDropZone', 'encodeFile', 'encodeFileName', 'encodePreview');
    setupFileUpload('decodeDropZone', 'decodeFile', 'decodeFileName', 'decodePreview');
</script>

</body>
</html>
"""

# ─────────────────────────────────────────────────────────────────────────

# Store encoded images temporarily
encoded_images = {}

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/encode", methods=["POST"])
def api_encode():
    try:
        file = request.files.get("image")
        message = request.form.get("message", "").strip()
        
        if not file or not message:
            return jsonify({"success": False, "error": "Image and message required"})
        
        img = Image.open(file.stream)
        result = encode_message(img, message)
        
        # Save to buffer
        buf = io.BytesIO()
        result.save(buf, format="PNG")
        buf.seek(0)
        
        # Generate unique ID for this image
        img_id = str(hash(buf.getvalue()))[-8:]
        encoded_images[img_id] = buf.getvalue()
        
        return jsonify({
            "success": True,
            "download_url": f"/download/{img_id}"
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/decode", methods=["POST"])
def api_decode():
    try:
        file = request.files.get("image")
        if not file:
            return jsonify({"success": False, "error": "Image required"})
        
        img = Image.open(file.stream)
        message = decode_message(img)
        
        if message:
            return jsonify({"success": True, "message": message})
        else:
            return jsonify({"success": False, "message": None})
    
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
        download_name="stego_message.png"
    )

if __name__ == "__main__":
    print("\n🔐 Steganography Tool is running!")
    print("👉 Open: http://localhost:5000\n")
    app.run(debug=False, port=5000)
