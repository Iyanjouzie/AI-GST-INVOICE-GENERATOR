# 🧾 AI GST Invoice Generator

A multilingual GST Invoice Generator built with **Flask** and **ReportLab** that auto-translates invoice content into 6 Indian regional languages and exports a styled PDF — all from a simple web form.

---

## ✨ Features

- 🌐 **Multilingual Support** — Generate invoices in English, Hindi, Tamil, Telugu, Malayalam, and Kannada
- 🤖 **AI-Powered Translation** — Uses `deep-translator` (Google Translate API) to auto-translate customer names and product items
- 📄 **PDF Generation** — Produces a clean, styled A4 PDF invoice via ReportLab
- 🔢 **Auto GST Calculation** — Computes subtotal, GST amount, and final total automatically
- 🎫 **Unique Invoice Numbers** — Generates random invoice IDs (e.g. `INV-202506-AB3X1Z`)
- 🎨 **Styled Output** — Purple-themed invoice with alternating row colors, header band, and footer

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| PDF Engine | ReportLab |
| Translation | deep-translator (Google Translate) |
| Fonts | Noto Sans (multi-script) |
| Frontend | HTML, CSS |

---

## 📁 Project Structure

```
AI-GST-Invoice/
├── app.py               # Main Flask application
├── requirements.txt     # Python dependencies
├── fonts/               # Noto Sans fonts for 6 languages
│   ├── NotoSans-Regular.ttf
│   ├── NotoSansDevanagari-Regular.ttf
│   ├── NotoSansTamil-Regular.ttf
│   └── ...
├── templates/
│   └── index.html       # Invoice form UI
├── static/
│   └── style.css        # Stylesheet
└── sample_invoice.pdf   # Sample output
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/AI-GST-Invoice.git
cd AI-GST-Invoice

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Then open your browser at `http://127.0.0.1:5000`

---

## 📦 Dependencies

```
flask
reportlab
deep-translator
```

---

## 📸 Sample Output

The generated invoice includes:
- Invoice number and date in the header
- Customer name (translated to the selected language)
- Itemized product table with amounts
- GST breakdown and final total
- A thank-you footer in the selected language

---

## 🌍 Supported Languages

| Code | Language |
|------|----------|
| `en` | English |
| `hi` | Hindi (हिन्दी) |
| `ta` | Tamil (தமிழ்) |
| `te` | Telugu (తెలుగు) |
| `ml` | Malayalam (മലയാളം) |
| `kn` | Kannada (ಕನ್ನಡ) |

---

## 🧑‍💻 How It Works

1. User fills in the web form — customer name, products, amounts, GST %, and language
2. Flask receives the POST request and translates text using `deep-translator`
3. ReportLab builds a styled A4 PDF with the translated content and correct Unicode fonts
4. The PDF is sent back to the browser as a download

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
