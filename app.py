from flask import Flask, render_template, request, send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from deep_translator import GoogleTranslator
from datetime import datetime
import os, random, string

app = Flask(__name__)

# ── Font setup: all fonts live in a "fonts/" folder next to app.py ──
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR  = os.path.join(BASE_DIR, 'fonts')

LANG_FONT_FILES = {
    'en': 'NotoSans-Regular.ttf',
    'hi': 'NotoSansDevanagari-Regular.ttf',
    'ta': 'NotoSansTamil-Regular.ttf',
    'te': 'NotoSansTelugu-Regular.ttf',
    'ml': 'NotoSansMalayalam-Regular.ttf',
    'kn': 'NotoSansKannada-Regular.ttf',
}

REGISTERED = {}
for lang, fname in LANG_FONT_FILES.items():
    font_name  = f'Noto_{lang}'
    font_path  = os.path.join(FONTS_DIR, fname)
    # Fallback to the base Latin font if a script font is missing
    if not os.path.exists(font_path):
        font_path = os.path.join(FONTS_DIR, 'NotoSans-Regular.ttf')
    pdfmetrics.registerFont(TTFont(font_name, font_path))
    REGISTERED[lang] = font_name

# ── Static labels — all 6 languages, no internet needed ──
LANG_LABELS = {
    "en": {"invoice":"GST INVOICE",               "customer":"Customer",
           "sno":"S.No",                           "item":"Item",
           "amount":"Amount (Rs.)",                "subtotal":"Subtotal",
           "gst":"GST",                            "total":"TOTAL",
           "date":"Date",                          "inv_no":"Invoice No",
           "thank":"Thank you for your business!"},
    "hi": {"invoice":"जीएसटी चालान",              "customer":"ग्राहक",
           "sno":"क्र.",                           "item":"वस्तु",
           "amount":"राशि (रु.)",                  "subtotal":"उप-योग",
           "gst":"जीएसटी",                        "total":"कुल",
           "date":"तारीख",                        "inv_no":"चालान नं.",
           "thank":"आपके व्यवसाय के लिए धन्यवाद!"},
    "ta": {"invoice":"ஜிஎஸ்டி விலைப்பட்டியல்",   "customer":"வாடிக்கையாளர்",
           "sno":"வ.எண்",                          "item":"பொருள்",
           "amount":"தொகை (ரூ.)",                  "subtotal":"கூட்டுத்தொகை",
           "gst":"ஜிஎஸ்டி",                      "total":"மொத்தம்",
           "date":"தேதி",                         "inv_no":"விலைப்பட்டியல் எண்",
           "thank":"உங்கள் வணிகத்திற்கு நன்றி!"},
    "te": {"invoice":"జిఎస్టి ఇన్వాయిస్",         "customer":"కస్టమర్",
           "sno":"క్ర.సం",                         "item":"వస్తువు",
           "amount":"మొత్తం (రూ.)",                "subtotal":"ఉప మొత్తం",
           "gst":"జిఎస్టి",                       "total":"మొత్తం",
           "date":"తేదీ",                         "inv_no":"ఇన్వాయిస్ నం.",
           "thank":"మీ వ్యాపారానికి ధన్యవాదాలు!"},
    "ml": {"invoice":"ജിഎസ്ടി ഇന്‍വോയ്സ്",        "customer":"ഉപഭോക്താവ്",
           "sno":"ക്ര.നം",                         "item":"ഉല്‍പ്പന്നം",
           "amount":"തുക (രൂ.)",                   "subtotal":"ഉപ-ആകെ",
           "gst":"ജിഎസ്ടി",                      "total":"ആകെ",
           "date":"തീയതി",                       "inv_no":"ഇന്‍വോയ്സ് നം.",
           "thank":"നിങ്ങളുടെ ബിസിനസ്സിന് നന്ദി!"},
    "kn": {"invoice":"ಜಿಎಸ್ಟಿ ಇನ್ವಾಯ್ಸ್",          "customer":"ಗ್ರಾಹಕ",
           "sno":"ಕ್ರ.ಸಂ",                         "item":"ವಸ್ತು",
           "amount":"ಮೊತ್ತ (ರೂ.)",                "subtotal":"ಉಪ-ಮೊತ್ತ",
           "gst":"ಜಿಎಸ್ಟಿ",                      "total":"ಒಟ್ಟು",
           "date":"ದಿನಾಂಕ",                      "inv_no":"ಇನ್ವಾಯ್ಸ್ ಸಂ.",
           "thank":"ನಿಮ್ಮ ವ್ಯವಹಾರಕ್ಕೆ ಧನ್ಯವಾದಗಳು!"},
}


def safe_translate(text, language):
    """Translate via Google; silently return original on any failure."""
    if language == 'en' or not text.strip():
        return text
    try:
        result = GoogleTranslator(source='auto', target=language).translate(text)
        return result if result and result.strip() else text
    except Exception:
        return text          # no internet → keep original, still readable


def pick_font(text, script_font, latin_font):
    """Route to script font if text has non-ASCII glyphs, else Latin font.
    Prevents blank boxes when translation fails and text stays in English."""
    return script_font if any(ord(c) > 127 for c in text) else latin_font


def make_invoice_number():
    tag = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"INV-{datetime.now().strftime('%Y%m')}-{tag}"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    # ── Read form ──────────────────────────────────────────────
    name     = request.form.get('name', '').strip()
    gst_pct  = float(request.form.get('gst', 0))
    language = request.form.get('language', 'en')
    products = request.form.getlist('product')
    amounts  = request.form.getlist('amount')

    items, total = [], 0.0
    for p, a in zip(products, amounts):
        p = p.strip()
        if not p:
            continue
        try:
            amt = float(a)
        except ValueError:
            amt = 0.0
        items.append([p, amt])
        total += amt

    # ── Translate ───────────────────────────────────────────────
    t_name  = safe_translate(name, language)
    t_items = [[safe_translate(p, language), a] for p, a in items]

    # ── Maths ───────────────────────────────────────────────────
    gst_amt   = round(total * gst_pct / 100, 2)
    final_tot = round(total + gst_amt, 2)

    # ── Layout helpers ──────────────────────────────────────────
    lbl       = LANG_LABELS.get(language, LANG_LABELS['en'])
    s_font    = REGISTERED.get(language, REGISTERED['en'])   # script font
    e_font    = REGISTERED['en']                              # Latin font
    now       = datetime.now()
    date_str  = now.strftime('%d %B %Y   %I:%M %p')
    inv_no    = make_invoice_number()

    PURPLE  = colors.HexColor('#6b21a8')
    LPURPLE = colors.HexColor('#f3e8ff')
    DARK    = colors.HexColor('#1e1b4b')
    GRAY    = colors.HexColor('#6b7280')
    ALT     = colors.HexColor('#faf5ff')

    _cache = {}
    def mkstyle(fn, size, color, align):
        key = (fn, size, id(color), align)
        if key not in _cache:
            _cache[key] = ParagraphStyle(f'ps_{key}',
                fontName=fn, fontSize=size, textColor=color,
                leading=size * 1.5,
                alignment={'LEFT':0, 'CENTER':1, 'RIGHT':2}[align])
        return _cache[key]

    def S(size=10, color=colors.black, align='LEFT'):
        """Script font — for labels and translated text."""
        return mkstyle(s_font, size, color, align)

    def E(size=10, color=colors.black, align='LEFT'):
        """English/Latin font — for numbers, dates, invoice no."""
        return mkstyle(e_font, size, color, align)

    def A(text, size=10, color=colors.black, align='LEFT'):
        """Auto font — picks script or Latin based on actual characters."""
        fn = pick_font(str(text), s_font, e_font)
        return mkstyle(fn, size, color, align)

    M = 20 * mm
    els = []

    # ── HEADER ─────────────────────────────────────────────────
    h = Table([[
        Paragraph(f'<b>{lbl["invoice"]}</b>', S(18, colors.white)),
        Paragraph(
            f'<b>{lbl["inv_no"]}:</b>  {inv_no}<br/>'
            f'<b>{lbl["date"]}:</b>  {date_str}',
            E(9, colors.white, 'RIGHT')),
    ]], colWidths=[95*mm, 80*mm])
    h.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,-1), PURPLE),
        ('VALIGN',       (0,0),(-1,-1), 'MIDDLE'),
        ('TOPPADDING',   (0,0),(-1,-1), 14),
        ('BOTTOMPADDING',(0,0),(-1,-1), 14),
        ('LEFTPADDING',  (0,0),(-1,-1), 14),
        ('RIGHTPADDING', (0,0),(-1,-1), 14),
    ]))
    els += [h, Spacer(1, 14)]

    # ── CUSTOMER ───────────────────────────────────────────────
    c = Table([[
        Paragraph(f'<b>{lbl["customer"]}:</b>', S(10, GRAY)),
        Paragraph(f'<b>{t_name}</b>', A(t_name, 13, DARK)),
    ]], colWidths=[42*mm, 133*mm])
    c.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,-1), LPURPLE),
        ('VALIGN',       (0,0),(-1,-1), 'MIDDLE'),
        ('TOPPADDING',   (0,0),(-1,-1), 10),
        ('BOTTOMPADDING',(0,0),(-1,-1), 10),
        ('LEFTPADDING',  (0,0),(-1,-1), 14),
        ('RIGHTPADDING', (0,0),(-1,-1), 14),
    ]))
    els += [c, Spacer(1, 18)]

    # ── ITEMS TABLE ────────────────────────────────────────────
    td = [[
        Paragraph(f'<b>{lbl["sno"]}</b>',    S(10, colors.white, 'CENTER')),
        Paragraph(f'<b>{lbl["item"]}</b>',   S(10, colors.white)),
        Paragraph(f'<b>{lbl["amount"]}</b>', S(10, colors.white, 'RIGHT')),
    ]]
    for i, (p, a) in enumerate(t_items, 1):
        td.append([
            Paragraph(str(i),           E(10, align='CENTER')),
            Paragraph(str(p),           A(str(p), 10)),
            Paragraph(f'Rs. {a:,.2f}',  E(10, align='RIGHT')),
        ])

    it = Table(td, colWidths=[15*mm, 120*mm, 35*mm])
    sc = [
        ('BACKGROUND',   (0,0),(-1,0),  PURPLE),
        ('LINEBELOW',    (0,0),(-1,0),  2, PURPLE),
        ('GRID',         (0,0),(-1,-1), 0.5, colors.HexColor('#e5e7eb')),
        ('VALIGN',       (0,0),(-1,-1), 'MIDDLE'),
        ('TOPPADDING',   (0,0),(-1,-1), 9),
        ('BOTTOMPADDING',(0,0),(-1,-1), 9),
        ('LEFTPADDING',  (0,0),(-1,-1), 8),
        ('RIGHTPADDING', (0,0),(-1,-1), 8),
    ]
    for i in range(1, len(td)):
        sc.append(('BACKGROUND', (0,i),(-1,i), ALT if i%2==0 else colors.white))
    it.setStyle(TableStyle(sc))
    els += [it, Spacer(1, 20)]

    # ── TOTALS ─────────────────────────────────────────────────
    tt = Table([
        [Paragraph(f'{lbl["subtotal"]}:',          S(10, GRAY, 'RIGHT')),
         Paragraph(f'Rs. {total:,.2f}',             E(10, align='RIGHT'))],
        [Paragraph(f'{lbl["gst"]} ({gst_pct}%):',  S(10, GRAY, 'RIGHT')),
         Paragraph(f'Rs. {gst_amt:,.2f}',           E(10, align='RIGHT'))],
        [Paragraph(f'<b>{lbl["total"]}:</b>',        S(14, PURPLE, 'RIGHT')),
         Paragraph(f'<b>Rs. {final_tot:,.2f}</b>',   E(14, PURPLE, 'RIGHT'))],
    ], colWidths=[120*mm, 55*mm], hAlign='RIGHT')
    tt.setStyle(TableStyle([
        ('TOPPADDING',   (0,0),(-1,-1), 6),
        ('BOTTOMPADDING',(0,0),(-1,-1), 6),
        ('LEFTPADDING',  (0,0),(-1,-1), 8),
        ('RIGHTPADDING', (0,0),(-1,-1), 8),
        ('LINEABOVE',    (0,2),(-1,2),  1.5, PURPLE),
        ('BACKGROUND',   (0,2),(-1,2),  LPURPLE),
    ]))
    els += [tt, Spacer(1, 28)]

    # ── FOOTER ─────────────────────────────────────────────────
    els += [
        HRFlowable(width='100%', thickness=1, color=LPURPLE),
        Spacer(1, 8),
        Paragraph(lbl['thank'], S(10, GRAY, 'CENTER')),
        Paragraph(f'Generated on {now.strftime("%d %B %Y at %I:%M %p")}',
                  E(8, colors.HexColor('#9ca3af'), 'CENTER')),
    ]

    # ── BUILD ───────────────────────────────────────────────────
    out = os.path.join(BASE_DIR, 'invoice.pdf')
    SimpleDocTemplate(out, pagesize=A4,
        leftMargin=M, rightMargin=M, topMargin=M, bottomMargin=M
    ).build(els)
    return send_file(out, as_attachment=True, download_name=f'{inv_no}.pdf')


if __name__ == '__main__':
    app.run(debug=True)
