# 🔐 StegoVault — LSB Image Steganography

> **Hide secret messages invisibly inside ordinary images. No trace. No noise. No suspicion.**

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0+-lightgrey?style=flat-square&logo=flask)
![Pillow](https://img.shields.io/badge/Pillow-9.0+-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-cyan?style=flat-square)

---

## 📌 What is This Project?

**StegoVault** is a web-based steganography application that lets you:

- **🔒 Hide** a secret text message inside any image (PNG, JPG, BMP)
- **🔓 Reveal** the hidden message from a stego image instantly

The hidden message is **completely invisible to the human eye**. The image looks exactly the same as the original — only the last bit of each pixel's colour channel is changed (a change of 1 out of 255), which is imperceptible.

---

## 📂 Project Structure

```
steganography/
│
├── stego_new.py          ← Main application (Flask backend + HTML frontend)
├── README.md             ← This file
│
└── How it works:
    ├── encode_message()  ← Hides text in image using LSB technique
    └── decode_message()  ← Extracts hidden text from stego image
```

---

## 🚀 Getting Started

### Prerequisites

Make sure you have Python 3.8 or higher installed.

```bash
python --version   # Should show Python 3.8+
```

### Installation

**Step 1:** Clone or download this repository

```bash
git clone https://github.com/auguxt/steganography.git
cd steganography
```

**Step 2:** Install required Python libraries

```bash
pip install flask pillow
```

**Step 3:** Run the application

```bash
python stego_new.py
```

**Step 4:** Open your browser and go to:

```
http://localhost:5000
```

That's it! StegoVault is now running on your computer. ✅

---

## 🎯 How to Use

### Hiding a Message (Encode)

1. Click the **"Hide a Message"** tab
2. Upload or drag-and-drop a cover image (PNG recommended)
3. Type your secret message in the text box
4. Click **"Hide Message"**
5. Download the stego image — it looks identical to the original!

### Revealing a Message (Decode)

1. Click the **"Reveal a Message"** tab
2. Upload the stego image (the one downloaded from step 5 above)
3. Click **"Reveal Message"**
4. The hidden message appears instantly!

---

## 🧠 How It Works — The LSB Algorithm

### What is a Pixel?

Every digital image is made up of tiny squares called **pixels**. Each pixel has three colour values: **Red**, **Green**, and **Blue** (RGB). Each value is a number from 0 to 255, stored as **8 binary bits**.

```
Example pixel: Sky Blue
Red   = 135  →  binary: 10000111
Green = 206  →  binary: 11001110
Blue  = 235  →  binary: 11101011
```

### The Least Significant Bit (LSB)

The **last bit** (rightmost) of each colour value has the smallest effect. Changing it changes the colour by only **1 out of 255** — completely invisible to the human eye.

```
Original:  10000111  (Red = 135)
Modified:  10000110  (Red = 134)  ← only 1 changed — you can't see this!
```

### Encoding Process

```
1. Convert message to binary  →  "Hi" = 01001000 01101001
2. Add "$$END$$" terminator   →  marks where message ends
3. For each pixel (R, G, B):
      R = (R & ~1) | next_bit  ← clear LSB, then set it to our bit
      G = (G & ~1) | next_bit
      B = (B & ~1) | next_bit
4. Save as PNG (lossless!)
```

### Decoding Process

```
1. Read all pixels
2. Extract the LSB of every R, G, B value  →  collect all bits
3. Group every 8 bits into one character
4. Stop when "$$END$$" is found
5. Return the message before the terminator
```

### Capacity Formula

```
Max characters = (Image Width × Image Height × 3) ÷ 8

Example — 1920×1080 Full HD image:
  (1920 × 1080 × 3) ÷ 8 = 777,600 characters ≈ 750 KB of text
```

---

## 🛠️ Technology Stack

| Component        | Technology          | Purpose                              |
|-----------------|---------------------|--------------------------------------|
| Backend Server  | Python Flask        | HTTP routing, file handling, APIs    |
| Image Processing| Python Pillow       | Pixel-level image manipulation       |
| Frontend UI     | HTML5 + CSS3        | Responsive dark-themed web interface |
| Interactivity   | Vanilla JavaScript  | Drag-drop, API calls, real-time UI   |
| Output Format   | PNG (lossless)      | Preserves embedded bits perfectly    |

---

## 🔌 API Reference

The app exposes three endpoints:

| Method | Endpoint             | Description                                        |
|--------|---------------------|----------------------------------------------------|
| GET    | `/`                 | Serves the main web interface                      |
| POST   | `/api/encode`       | Encodes message into image; returns download URL   |
| POST   | `/api/decode`       | Decodes message from image; returns message text   |
| GET    | `/download/<id>`    | Downloads the encoded stego image by its ID        |

### POST `/api/encode`

```
Request:  multipart/form-data
  - image    : image file (PNG, JPG, BMP)
  - message  : text string (the secret message)

Response: JSON
  { "success": true,  "download_url": "/download/a1b2c3d4" }
  { "success": false, "error": "Message too long!" }
```

### POST `/api/decode`

```
Request:  multipart/form-data
  - image    : stego image file

Response: JSON
  { "success": true, "message": "Your secret message here" }
  { "success": true, "message": null }   // no message found
```

---

## ✅ Testing Results

| Test Case                      | Result    |
|-------------------------------|-----------|
| Encode short message           | ✅ PASS   |
| Encode long message (>1000 chars) | ✅ PASS |
| Decode stego image correctly   | ✅ PASS   |
| Decode normal image (no message)| ✅ PASS  |
| Message exceeds image capacity | ✅ PASS (error shown) |
| Invalid file type uploaded     | ✅ PASS (error shown) |
| JPEG encode → decode           | ⚠️ KNOWN (JPEG compression destroys LSB data) |

---

## ⚠️ Important Note — Use PNG, Not JPEG

> **Always save and use PNG images for steganography!**

JPEG uses **lossy compression** — it slightly alters pixel values to reduce file size. This destroys the carefully placed LSB data, making decoding impossible. PNG is **lossless** — every pixel is stored exactly as written.

---

## 📊 Advantages & Limitations

### ✅ Advantages
- Completely invisible to human eyes
- Simple, fast algorithm
- High capacity (up to 750KB per HD image)
- No special software required — works in any browser
- Clean, professional dark-themed interface
- Cross-platform (Windows, Mac, Linux)

### ⚠️ Limitations
- Detectable by statistical steganalysis tools
- Not compatible with JPEG compression
- No encryption (message is hidden, not encrypted)
- No password protection
- In-memory storage (restarting server clears encoded images)

---

## 🔮 Future Improvements

- [ ] Add **AES-256 encryption** before embedding
- [ ] Implement **password-protected** encoding/decoding
- [ ] Support **audio (WAV)** steganography
- [ ] Support **video** steganography
- [ ] Add resistance to steganalysis (spread-spectrum method)
- [ ] **Mobile app** using React Native
- [ ] Persistent storage with a database

---

## 📚 References

1. Johnson, N.F. & Jajodia, S. (1998). *Exploring Steganography: Seeing the Unseen.* IEEE Computer.
2. Marvel, L.M. et al. (1999). *Spread Spectrum Image Steganography.* IEEE Transactions on Image Processing.
3. [Pillow Documentation](https://pillow.readthedocs.io/)
4. [Flask Documentation](https://flask.palletsprojects.com/)
5. [GeeksForGeeks — Image Steganography](https://www.geeksforgeeks.org/steganography-hide-text-in-images/)

---

## 👨‍💻 About This Project

**StegoVault** was built as a 6th Semester Mini Project for the course *Information Security & Cryptography*, B.Tech Computer Science & Engineering.

It demonstrates a clear understanding of:
- Digital image representation and pixel manipulation
- Binary encoding and bitwise operations
- Full-stack web development with Python Flask
- REST API design and HTTP file handling
- Secure and user-friendly UI/UX design

---

> *"Steganography doesn't just hide the message — it hides the fact that a message exists."*

---

**StegoVault · LSB Image Steganography · 6th Semester Mini Project**
