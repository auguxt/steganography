# 🔐 Steganography Tool — Hide Secret Messages in Images
**Mini Project | III Year | Department of Cyber Security**

---

## 📌 What is this?
This tool hides secret text messages inside images using the **LSB (Least Significant Bit)** technique. The output image looks identical to the original — but contains a hidden message only your tool can reveal.

---

## 📁 Files
| File | Description |
|------|-------------|
| `stego.py` | Command-line version |
| `stego_gui.py` | GUI version (recommended for demo) |
| `requirements.txt` | Dependencies |

---

## ⚙️ Installation

```bash
pip install Pillow
```

---

## ▶️ Run GUI Version
```bash
python stego_gui.py
```

## ▶️ Run CLI Version
```bash
python stego.py
```

---

## 🧠 How It Works (LSB Technique)
1. Every pixel has 3 color channels: **R, G, B** (0–255)
2. We change only the **last bit** of each channel (imperceptible to human eye)
3. These bits store the binary of your secret message
4. To decode — read those last bits and reconstruct the message

---

## 🎓 Key Concepts Covered
- Image Steganography
- LSB (Least Significant Bit) Algorithm
- Data Hiding & Confidentiality
- Python PIL/Pillow Image Processing

---

## 📦 Requirements
```
Pillow>=9.0.0
```
