from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import (HexColor, white, black)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics import renderPDF
from reportlab.graphics.widgets.markers import makeMarker
from io import BytesIO
import datetime

# ── Palet warna ───────────────────────────────────────────────────────────────
C_DARK   = HexColor("#1A3A2A")
C_GREEN  = HexColor("#0F6E56")
C_BLUE   = HexColor("#185FA5")
C_AMBER  = HexColor("#854F0B")
C_RED    = HexColor("#A32D2D")
C_LIGHT  = HexColor("#E8F5EE")
C_BGPAGE = HexColor("#F7F6F2")
C_GRAY   = HexColor("#888780")
C_BORDER = HexColor("#D3D1C7")
C_WHITE  = white
C_PESIMIS= HexColor("#E24B4A")
C_MODERAT= HexColor("#BA7517")
C_OPTIMIS= HexColor("#0F6E56")

W, H = A4  # 595.27 x 841.89

def fmt(n):
    """Format angka dengan pemisah titik gaya Indonesia."""
    try:
        return f"{int(round(abs(n))):,}".replace(",", ".")
    except:
        return str(n)

def fmt_rp(n):
    if abs(n) >= 1_000_000:
        return f"Rp {n/1_000_000:.1f} jt"
    return f"Rp {fmt(n)}"

def pct(n):
    return f"{n:.1f}%"


# ── Styles ────────────────────────────────────────────────────────────────────
def make_styles():
    base = getSampleStyleSheet()
    s = {}

    s["title"] = ParagraphStyle("title",
        fontName="Helvetica-Bold", fontSize=26, textColor=C_WHITE,
        alignment=TA_LEFT, leading=32, spaceAfter=4)
    s["subtitle"] = ParagraphStyle("subtitle",
        fontName="Helvetica", fontSize=12, textColor=HexColor("#B0CFBE"),
        alignment=TA_LEFT, leading=16)
    s["cover_meta"] = ParagraphStyle("cover_meta",
        fontName="Helvetica", fontSize=10, textColor=HexColor("#B0CFBE"),
        alignment=TA_LEFT, leading=14)

    s["section"] = ParagraphStyle("section",
        fontName="Helvetica-Bold", fontSize=13, textColor=C_DARK,
        spaceBefore=14, spaceAfter=6, borderPad=4,
        borderColor=C_GREEN, borderWidth=0,
        leftIndent=0)
    s["subsection"] = ParagraphStyle("subsection",
        fontName="Helvetica-Bold", fontSize=10, textColor=C_GREEN,
        spaceBefore=8, spaceAfter=4)
    s["body"] = ParagraphStyle("body",
        fontName="Helvetica", fontSize=9.5, textColor=HexColor("#333330"),
        alignment=TA_JUSTIFY, leading=14, spaceAfter=4)
    s["body_sm"] = ParagraphStyle("body_sm",
        fontName="Helvetica", fontSize=8.5, textColor=HexColor("#555552"),
        alignment=TA_LEFT, leading=12, spaceAfter=2)
    s["caption"] = ParagraphStyle("caption",
        fontName="Helvetica-Oblique", fontSize=8, textColor=C_GRAY,
        alignment=TA_CENTER, leading=10, spaceAfter=2)
    s["note"] = ParagraphStyle("note",
        fontName="Helvetica-Oblique", fontSize=8.5, textColor=C_AMBER,
        alignment=TA_LEFT, leading=12,
        backColor=HexColor("#FAEEDA"), borderPad=6,
        leftIndent=6, rightIndent=6, spaceBefore=4, spaceAfter=4)
    s["bullet"] = ParagraphStyle("bullet",
        fontName="Helvetica", fontSize=9.5, textColor=HexColor("#333330"),
        alignment=TA_LEFT, leading=14, leftIndent=12,
        firstLineIndent=-12, spaceAfter=2)
    s["tbl_hdr"] = ParagraphStyle("tbl_hdr",
        fontName="Helvetica-Bold", fontSize=8.5, textColor=C_WHITE,
        alignment=TA_CENTER, leading=11)
    s["tbl_cell"] = ParagraphStyle("tbl_cell",
        fontName="Helvetica", fontSize=8.5, textColor=HexColor("#222220"),
        alignment=TA_LEFT, leading=11)
    s["tbl_num"] = ParagraphStyle("tbl_num",
        fontName="Helvetica", fontSize=8.5, textColor=HexColor("#222220"),
        alignment=TA_RIGHT, leading=11)
    s["tbl_num_g"] = ParagraphStyle("tbl_num_g",
        fontName="Helvetica-Bold", fontSize=8.5, textColor=C_GREEN,
        alignment=TA_RIGHT, leading=11)
    s["tbl_num_r"] = ParagraphStyle("tbl_num_r",
        fontName="Helvetica-Bold", fontSize=8.5, textColor=C_RED,
        alignment=TA_RIGHT, leading=11)
    return s

S = make_styles()


# ── Header & Footer ───────────────────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    # Footer bar
    canvas.setFillColor(C_DARK)
    canvas.rect(0, 0, W, 1.2*cm, fill=1, stroke=0)
    canvas.setFillColor(C_WHITE)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(1.5*cm, 0.42*cm, "GREKO Golden Age Center — GGAC ROI Calculator")
    canvas.drawRightString(W - 1.5*cm, 0.42*cm,
        f"Laporan dihasilkan: {datetime.date.today().strftime('%d %B %Y')}  |  Hal. {doc.page}")
    # Top line accent
    canvas.setFillColor(C_GREEN)
    canvas.rect(0, H - 3*mm, W, 3*mm, fill=1, stroke=0)
    canvas.restoreState()


# ── Helpers ───────────────────────────────────────────────────────────────────
def section_rule(title):
    """Garis hijau + judul section."""
    return [
        HRFlowable(width="100%", thickness=2, color=C_GREEN, spaceAfter=4),
        Paragraph(title, S["section"]),
    ]

def metric_table(items):
    """
    items = [(label, value, color), ...]
    Render sebagai tabel metric card 2 kolom.
    """
    rows = []
    for i in range(0, len(items), 2):
        row = []
        for item in items[i:i+2]:
            label, value, color = item
            col_content = Table(
                [[Paragraph(label, S["caption"])],
                 [Paragraph(f'<font color="{color.hexval()}" size="16"><b>{value}</b></font>', S["subsection"])]],
                colWidths=["100%"]
            )
            col_content.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,-1), HexColor("#FFFFFF")),
                ("BOX",        (0,0), (-1,-1), 0.5, C_BORDER),
                ("TOPPADDING", (0,0), (-1,-1), 6),
                ("BOTTOMPADDING", (0,0), (-1,-1), 6),
                ("LEFTPADDING", (0,0), (-1,-1), 10),
                ("RIGHTPADDING", (0,0), (-1,-1), 10),
                ("ROUNDEDCORNERS", (0,0), (-1,-1), [4,4,4,4]),
            ]))
            row.append(col_content)
        if len(row) == 1:
            row.append("")
        rows.append(row)

    t = Table(rows, colWidths=[(W - 3*cm)/2 - 3]*2, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("VALIGN",      (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 3),
        ("RIGHTPADDING",(0,0), (-1,-1), 3),
        ("TOPPADDING",  (0,0), (-1,-1), 3),
        ("BOTTOMPADDING",(0,0),(-1,-1), 3),
    ]))
    return t

def data_table(headers, rows_data, col_widths, stripe=True):
    """Generic styled data table."""
    tbl_rows = [[Paragraph(h, S["tbl_hdr"]) for h in headers]]
    for i, row in enumerate(rows_data):
        cells = []
        for j, cell in enumerate(row):
            if isinstance(cell, tuple):
                val, style = cell
                cells.append(Paragraph(str(val), S[style]))
            else:
                cells.append(Paragraph(str(cell), S["tbl_cell"]))
        tbl_rows.append(cells)

    t = Table(tbl_rows, colWidths=col_widths, hAlign="LEFT", repeatRows=1)
    style = [
        ("BACKGROUND",    (0,0), (-1,0), C_DARK),
        ("TEXTCOLOR",     (0,0), (-1,0), C_WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1), (-1,-1),
         [HexColor("#F5F4F0"), HexColor("#FFFFFF")] if stripe else [C_WHITE]),
        ("GRID",          (0,0), (-1,-1), 0.3, C_BORDER),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("RIGHTPADDING",  (0,0), (-1,-1), 6),
    ]
    t.setStyle(TableStyle(style))
    return t


# ── Bar chart helper ──────────────────────────────────────────────────────────
def simple_bar_chart(labels, values, colors, width=460, height=140, title=""):
    drawing = Drawing(width, height + 20)
    bc = VerticalBarChart()
    bc.x = 30; bc.y = 20
    bc.width = width - 40; bc.height = height - 20
    bc.data = [values]
    bc.bars[0].fillColor = colors[0] if len(colors)==1 else C_GREEN
    # Per-bar color
    for i, c in enumerate(colors):
        bc.bars[(0, i)].fillColor = c
    bc.categoryAxis.categoryNames = labels
    bc.categoryAxis.labels.fontSize = 7.5
    bc.categoryAxis.labels.angle = 0
    bc.valueAxis.labels.fontSize = 7.5
    bc.valueAxis.labelTextFormat = lambda v: f"Rp{v/1e6:.1f}jt" if abs(v)>=1e6 else f"Rp{v:,.0f}"
    bc.valueAxis.valueMin = min(0, min(values)) * 1.1
    bc.valueAxis.valueMax = max(values) * 1.15
    bc.barWidth = 14
    bc.groupSpacing = 8
    if title:
        drawing.add(String(width/2, height+5, title,
                    fontSize=8, fillColor=black, textAnchor="middle"))
    drawing.add(bc)
    return drawing


def grouped_bar_chart(labels, series_data, series_colors, series_names,
                      width=460, height=150):
    drawing = Drawing(width, height + 20)
    bc = VerticalBarChart()
    bc.x = 40; bc.y = 25
    bc.width = width - 50; bc.height = height - 30
    bc.data = series_data
    for i, c in enumerate(series_colors):
        bc.bars[i].fillColor = c
    bc.categoryAxis.categoryNames = labels
    bc.categoryAxis.labels.fontSize = 7.5
    bc.valueAxis.labels.fontSize = 7.5
    bc.valueAxis.labelTextFormat = lambda v: f"Rp{v/1e6:.1f}jt" if abs(v)>=1e6 else f"Rp{v/1e6:.2f}jt"
    bc.valueAxis.valueMin = min(0, min(min(s) for s in series_data)) * 1.1
    bc.valueAxis.valueMax = max(max(s) for s in series_data) * 1.2
    bc.barWidth = 10
    bc.groupSpacing = 6
    drawing.add(bc)
    return drawing


def line_chart(series_list, series_colors, series_names, x_vals,
               width=460, height=160, zero_line=True):
    drawing = Drawing(width, height)
    lc = HorizontalLineChart()
    lc.x = 40; lc.y = 20
    lc.width = width - 50; lc.height = height - 30
    lc.data = series_list
    n = len(x_vals)
    lc.categoryAxis.categoryNames = [str(x) if i%(max(1,n//8))==0 else ""
                                     for i,x in enumerate(x_vals)]
    lc.categoryAxis.labels.fontSize = 7
    lc.valueAxis.labels.fontSize = 7
    lc.valueAxis.labelTextFormat = lambda v: f"Rp{v/1e6:.0f}jt"
    all_vals = [v for s in series_list for v in s]
    lc.valueAxis.valueMin = min(all_vals) * 1.05
    lc.valueAxis.valueMax = max(all_vals) * 1.1
    for i, (c, nm) in enumerate(zip(series_colors, series_names)):
        lc.lines[i].strokeColor = c
        lc.lines[i].strokeWidth = 1.8
    if zero_line:
        # Hitung posisi y=0 secara proporsional
        vmin = lc.valueAxis.valueMin
        vmax = lc.valueAxis.valueMax
        if vmin < 0 < vmax:
            y0 = lc.y + lc.height * (0 - vmin) / (vmax - vmin)
            drawing.add(Line(lc.x, y0, lc.x + lc.width, y0,
                             strokeColor=C_RED, strokeWidth=0.8,
                             strokeDashArray=[3,3]))
    drawing.add(lc)
    return drawing


# ══════════════════════════════════════════════════════════════════════════════
# FUNGSI UTAMA — generate_pdf
# ══════════════════════════════════════════════════════════════════════════════
def generate_pdf(params: dict) -> bytes:
    """
    params berisi semua data kalkulasi yang dibutuhkan.
    Return: bytes PDF.
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=1.8*cm, bottomMargin=1.8*cm,
        onPage=on_page
    )

    d_p = params["d_p"]
    d_m = params["d_m"]
    d_o = params["d_o"]
    investasi       = params["investasi"]
    modal_pengelola = params["modal_pengelola"]
    share_i         = params["share_i"]
    share_ii        = params["share_ii"]
    proj_years      = params["proj_years"]
    omzet_min       = params["omzet_min"]

    story = []

    # ══════════════════════════════════════════════════════════════════════
    # HALAMAN 1 — COVER
    # ══════════════════════════════════════════════════════════════════════
    # Background hijau gelap
    cover_bg = Table(
        [[""]], colWidths=[W - 3*cm], rowHeights=[H * 0.46]
    )
    cover_bg.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), C_DARK),
        ("LEFTPADDING",(0,0),(-1,-1), 0),
        ("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING", (0,0),(-1,-1), 0),
        ("BOTTOMPADDING",(0,0),(-1,-1),0),
    ]))

    cover_content = Table([
        [Paragraph("LAPORAN KELAYAKAN INVESTASI", S["subtitle"])],
        [Spacer(1, 6)],
        [Paragraph("GREKO Golden Age Center", S["title"])],
        [Paragraph("GGAC — Gym & Active Aging Program", S["subtitle"])],
        [Spacer(1, 16)],
        [Paragraph(
            f"Investasi Owner: <b>Rp {fmt(investasi)}</b>  ·  "
            f"Modal Pengelola: <b>Rp {fmt(modal_pengelola)}</b>  ·  "
            f"Proyeksi: <b>{proj_years} tahun</b>",
            S["cover_meta"])],
        [Paragraph(
            f"Bagi hasil: Owner {share_i}%  ·  Pengelola {share_ii}%  ·  "
            f"Target BEP: Rp {fmt(omzet_min)}/bln",
            S["cover_meta"])],
        [Spacer(1, 20)],
        [Paragraph(
            f"Tanggal laporan: {datetime.date.today().strftime('%d %B %Y')}",
            S["cover_meta"])],
    ], colWidths=[W - 3*cm])
    cover_content.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), C_DARK),
        ("LEFTPADDING",(0,0),(-1,-1), 24),
        ("TOPPADDING", (0,0),(-1,-1), 2),
        ("BOTTOMPADDING",(0,0),(-1,-1),2),
    ]))

    story.append(cover_content)
    story.append(Spacer(1, 0.5*cm))

    # Tiga kotak skenario di cover
    def cover_box(nama, d, c_accent):
        bep = f"BEP bln ke-{d['bep_month']}" if d['bep_month'] else "BEP > proyeksi"
        content = [
            [Paragraph(f"<b>{nama}</b>", ParagraphStyle("cb",
                fontName="Helvetica-Bold", fontSize=10,
                textColor=c_accent, alignment=TA_CENTER))],
            [Paragraph(f"Omzet/bln<br/><b>Rp {fmt(d['total_rev'])}</b>",
                ParagraphStyle("cv", fontName="Helvetica", fontSize=8,
                textColor=black, alignment=TA_CENTER, leading=12))],
            [Paragraph(f"ROI Owner/thn<br/><b>{pct(d['roi_pct'])}</b>",
                ParagraphStyle("cv", fontName="Helvetica", fontSize=8,
                textColor=black, alignment=TA_CENTER, leading=12))],
            [Paragraph(f"ROI Pengelola/thn<br/><b>{pct(d['roi_ii_pct'])}</b>",
                ParagraphStyle("cv", fontName="Helvetica", fontSize=8,
                textColor=black, alignment=TA_CENTER, leading=12))],
            [Paragraph(bep, ParagraphStyle("cv", fontName="Helvetica-Oblique",
                fontSize=7.5, textColor=C_GRAY, alignment=TA_CENTER))],
        ]
        t = Table(content, colWidths=[(W-3*cm)/3 - 8])
        t.setStyle(TableStyle([
            ("BOX",           (0,0),(-1,-1), 1.5, c_accent),
            ("TOPPADDING",    (0,0),(-1,-1), 5),
            ("BOTTOMPADDING", (0,0),(-1,-1), 5),
            ("LEFTPADDING",   (0,0),(-1,-1), 6),
            ("RIGHTPADDING",  (0,0),(-1,-1), 6),
            ("BACKGROUND",    (0,0),(-1,-1), HexColor("#FAFAF8")),
        ]))
        return t

    boxes = Table(
        [[cover_box("🔴  Skenario Pesimis", d_p, C_PESIMIS),
          cover_box("🟡  Skenario Moderat", d_m, C_MODERAT),
          cover_box("🟢  Skenario Optimis", d_o, C_OPTIMIS)]],
        colWidths=[(W-3*cm)/3]*3, hAlign="LEFT"
    )
    boxes.setStyle(TableStyle([
        ("LEFTPADDING", (0,0),(-1,-1), 4),
        ("RIGHTPADDING",(0,0),(-1,-1), 4),
        ("VALIGN",      (0,0),(-1,-1), "TOP"),
    ]))
    story.append(boxes)
    story.append(Spacer(1, 0.4*cm))

    # Disclaimer
    story.append(Paragraph(
        "Dokumen ini bersifat proyeksi dan estimasi. Angka aktual dapat berbeda "
        "tergantung kondisi pasar, utilisasi klien, dan faktor operasional.",
        S["note"]))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # HALAMAN 2 — RINGKASAN EKSEKUTIF
    # ══════════════════════════════════════════════════════════════════════
    story += section_rule("1.  RINGKASAN EKSEKUTIF")
    story.append(Paragraph(
        f"GGAC adalah program gym dan active aging yang beroperasi di fasilitas Greko. "
        f"Kerjasama antara Pihak I (Owner/Investor) dan Pihak II (Pengelola) dijalankan "
        f"dengan skema bagi hasil laba bersih <b>{share_i}% : {share_ii}%</b>. "
        f"Total modal kas yang ditanamkan adalah <b>Rp {fmt(investasi + modal_pengelola)}</b>, "
        f"terdiri dari investasi owner <b>Rp {fmt(investasi)}</b> dan modal pengelola "
        f"<b>Rp {fmt(modal_pengelola)}</b> (nilai buku peralatan existing).",
        S["body"]))
    story.append(Spacer(1, 6))

    # Tabel perbandingan 3 skenario
    story.append(Paragraph("Perbandingan Tiga Skenario", S["subsection"]))
    skenario_rows = []
    for nama, d, clr in [("🔴 Pesimis", d_p, "#E24B4A"),
                          ("🟡 Moderat", d_m, "#BA7517"),
                          ("🟢 Optimis", d_o, "#0F6E56")]:
        bep = f"Bln ke-{d['bep_month']}" if d['bep_month'] else "> proyeksi"
        bep2 = f"Bln ke-{d['bep_month_ii']}" if d['bep_month_ii'] else "> proyeksi"
        skenario_rows.append([
            (f'<font color="{clr}"><b>{nama}</b></font>', "tbl_cell"),
            (f"Rp {fmt(d['total_rev'])}", "tbl_num"),
            (f"Rp {fmt(d['laba_bersih'])}", "tbl_num_g" if d['laba_bersih']>0 else "tbl_num_r"),
            (f"Rp {fmt(d['hasil_i'])}", "tbl_num_g"),
            (f"Rp {fmt(d['hasil_ii'])}", "tbl_num_g"),
            (pct(d['roi_pct']), "tbl_num_g"),
            (pct(d['roi_ii_pct']), "tbl_num_g"),
            (bep, "tbl_cell"),
            (bep2, "tbl_cell"),
        ])
    cw = [2.6*cm, 2.3*cm, 2.3*cm, 2.3*cm, 2.3*cm, 1.5*cm, 1.5*cm, 1.8*cm, 1.8*cm]
    story.append(data_table(
        ["Skenario","Omzet/bln","Laba/bln",
         f"Bagian\nOwner/bln",f"Bagian\nPengelola/bln",
         "ROI\nOwner","ROI\nPengelola",
         "Payback\nOwner","Payback\nPengelola"],
        skenario_rows, cw))
    story.append(Spacer(1, 6))

    # Bar chart omzet & laba 3 skenario
    story.append(Paragraph("Grafik Omzet & Laba Bersih per Skenario (bulan 1)", S["subsection"]))
    chart = grouped_bar_chart(
        ["Pesimis","Moderat","Optimis"],
        [[d_p["total_rev"], d_m["total_rev"], d_o["total_rev"]],
         [d_p["laba_bersih"], d_m["laba_bersih"], d_o["laba_bersih"]]],
        [HexColor("#A8D8C8"), C_GREEN],
        ["Omzet/bln","Laba bersih/bln"],
        width=460, height=140
    )
    story.append(chart)
    story.append(Paragraph("Gambar 1 — Perbandingan omzet dan laba bersih tiga skenario (bulan pertama)", S["caption"]))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # HALAMAN 3 — STRUKTUR MODAL
    # ══════════════════════════════════════════════════════════════════════
    story += section_rule("2.  STRUKTUR MODAL & BAGI HASIL")

    total_modal = investasi + modal_pengelola
    pct_i  = investasi / total_modal * 100
    pct_ii = modal_pengelola / total_modal * 100

    story.append(Paragraph(
        f"Total modal kas yang terlibat dalam operasional GGAC adalah "
        f"<b>Rp {fmt(total_modal)}</b>. Owner berkontribusi <b>{pct_i:.1f}%</b> "
        f"namun mendapat <b>{share_i}% bagi hasil</b>. Pengelola berkontribusi "
        f"<b>{pct_ii:.1f}%</b> modal kas dan mendapat <b>{share_ii}% bagi hasil</b>. "
        f"Ketidakseimbangan ini dijustifikasi oleh kontribusi non-kas pengelola berupa "
        f"keahlian Active Aging, kurikulum, klien existing, dan manajemen operasional harian.",
        S["body"]))
    story.append(Spacer(1, 8))

    modal_rows = [
        [("Investasi Owner — peralatan gym baru", "tbl_cell"),
         (f"Rp {fmt(investasi)}", "tbl_num"), (f"{pct_i:.1f}%","tbl_num"), (f"{share_i}%","tbl_num_g")],
        [("Modal Pengelola — nilai buku peralatan existing", "tbl_cell"),
         (f"Rp {fmt(modal_pengelola)}", "tbl_num"), (f"{pct_ii:.1f}%","tbl_num"), (f"{share_ii}%","tbl_num_g")],
        [("Kontribusi non-kas Owner — akses lokasi", "tbl_cell"),
         ("Non-kas","tbl_cell"), ("—","tbl_cell"), ("Termasuk","tbl_cell")],
        [("Kontribusi non-kas Pengelola — keahlian & klien", "tbl_cell"),
         ("Non-kas","tbl_cell"), ("—","tbl_cell"), ("Termasuk","tbl_cell")],
    ]
    story.append(data_table(
        ["Komponen Modal", "Nilai Kas (Rp)", "% Modal Kas", "% Bagi Hasil"],
        modal_rows,
        [8*cm, 3.5*cm, 2.5*cm, 2.5*cm]
    ))
    story.append(Spacer(1, 8))

    # Bar chart porsi modal vs bagi hasil
    chart_modal = simple_bar_chart(
        ["Modal Owner","Modal Pengelola","Bagi Hasil Owner","Bagi Hasil Pengelola"],
        [pct_i, pct_ii, share_i, share_ii],
        [C_GREEN, C_BLUE, HexColor("#A8D8C8"), HexColor("#A8C0E0")],
        width=340, height=120, title=""
    )
    story.append(chart_modal)
    story.append(Paragraph("Gambar 2 — Perbandingan porsi modal kas vs porsi bagi hasil (%)", S["caption"]))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # HALAMAN 4 — PROYEKSI KEUANGAN (SKENARIO MODERAT)
    # ══════════════════════════════════════════════════════════════════════
    story += section_rule("3.  PROYEKSI KEUANGAN — SKENARIO MODERAT")
    story.append(Paragraph(
        "Proyeksi berikut menggunakan skenario moderat sebagai referensi utama. "
        "Skenario moderat mengasumsikan utilisasi kelas yang realistis dengan "
        "pertumbuhan organik yang konservatif.",
        S["body"]))
    story.append(Spacer(1, 6))

    # Tabel tahunan
    yearly_rows = []
    for yr in range(1, proj_years + 1):
        grow = params["growth_m"] / 100
        cost = params["cost_m"] / 100
        rev_yr  = d_m["total_rev"]  * ((1 + grow) ** (yr-1)) * 12
        opex_yr = d_m["total_opex"] * ((1 + cost) ** (yr-1)) * 12
        laba_yr = rev_yr - opex_yr
        earn_i  = laba_yr * (share_i/100) if laba_yr > 0 else 0
        earn_ii = laba_yr * (share_ii/100) if laba_yr > 0 else 0
        yearly_rows.append([
            (f"Tahun {yr}", "tbl_cell"),
            (f"Rp {fmt(rev_yr)}", "tbl_num"),
            (f"Rp {fmt(opex_yr)}", "tbl_num"),
            (f"Rp {fmt(laba_yr)}", "tbl_num_g" if laba_yr>0 else "tbl_num_r"),
            (f"Rp {fmt(earn_i)}", "tbl_num_g"),
            (f"Rp {fmt(earn_ii)}", "tbl_num_g"),
        ])
    story.append(data_table(
        ["Tahun","Omzet (Rp)","Total Biaya (Rp)","Laba Bersih (Rp)",
         f"Bagian Owner\n{share_i}% (Rp)",f"Bagian Pengelola\n{share_ii}% (Rp)"],
        yearly_rows,
        [1.8*cm, 3.2*cm, 3.2*cm, 3.2*cm, 3.2*cm, 3.2*cm]
    ))
    story.append(Spacer(1, 8))

    # Line chart arus kas kumulatif
    story.append(Paragraph("Proyeksi Arus Kas Kumulatif — Skenario Moderat", S["subsection"]))
    months = d_m["months"]
    # Ambil setiap bulan ke-3
    step = max(1, months // 20)
    x_idx = list(range(0, months+1, step))
    owner_vals  = [d_m["cum_owner"][i]     for i in x_idx]
    pgel_vals   = [d_m["cum_pengelola"][i] for i in x_idx]
    x_labels    = [f"B{i}" for i in x_idx]

    chart_kas = line_chart(
        [owner_vals, pgel_vals],
        [C_GREEN, C_BLUE],
        ["Owner","Pengelola"],
        x_labels, width=460, height=160, zero_line=True
    )
    story.append(chart_kas)
    story.append(Paragraph(
        "Gambar 3 — Arus kas kumulatif owner (hijau) dan pengelola (biru). "
        "Garis merah putus-putus = titik break-even.",
        S["caption"]))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # HALAMAN 5 — BREAKDOWN PENDAPATAN & BIAYA
    # ══════════════════════════════════════════════════════════════════════
    story += section_rule("4.  BREAKDOWN PENDAPATAN & BIAYA — BULAN PERTAMA")
    story.append(Paragraph(
        "Tabel berikut merinci sumber pendapatan dan komponen biaya pada bulan pertama "
        "operasional untuk skenario moderat.",
        S["body"]))
    story.append(Spacer(1, 6))

    # Pendapatan
    story.append(Paragraph("4.1  Rincian Pendapatan per Kelas", S["subsection"]))
    rev_rows = [
        [("Private 1-on-1",   "tbl_cell"),
         (f"Rp {fmt(d_m['rev_private'])}",  "tbl_num_g"),
         (pct(d_m['rev_private']/d_m['total_rev']*100 if d_m['total_rev']>0 else 0), "tbl_num")],
        [("Couple / ber-2",   "tbl_cell"),
         (f"Rp {fmt(d_m['rev_couple'])}",   "tbl_num_g"),
         (pct(d_m['rev_couple']/d_m['total_rev']*100 if d_m['total_rev']>0 else 0), "tbl_num")],
        [("Group 3-4 orang",  "tbl_cell"),
         (f"Rp {fmt(d_m['rev_group'])}",    "tbl_num_g"),
         (pct(d_m['rev_group']/d_m['total_rev']*100 if d_m['total_rev']>0 else 0), "tbl_num")],
        [("Chair exercise",   "tbl_cell"),
         (f"Rp {fmt(d_m['rev_chair'])}",    "tbl_num_g"),
         (pct(d_m['rev_chair']/d_m['total_rev']*100 if d_m['total_rev']>0 else 0), "tbl_num")],
        [("Kelas tambahan taichi/yoga","tbl_cell"),
         (f"Rp {fmt(d_m['rev_tambahan'])}", "tbl_num_g"),
         (pct(d_m['rev_tambahan']/d_m['total_rev']*100 if d_m['total_rev']>0 else 0), "tbl_num")],
        [("Mandiri tanpa PT", "tbl_cell"),
         (f"Rp {fmt(d_m['rev_mandiri'])}",  "tbl_num_g"),
         (pct(d_m['rev_mandiri']/d_m['total_rev']*100 if d_m['total_rev']>0 else 0), "tbl_num")],
        [("<b>TOTAL OMZET</b>","tbl_cell"),
         (f"<b>Rp {fmt(d_m['total_rev'])}</b>", "tbl_num_g"),
         ("<b>100%</b>","tbl_num")],
    ]
    story.append(data_table(
        ["Kategori Kelas","Pendapatan (Rp)","% Omzet"],
        rev_rows, [9*cm, 5*cm, 2.5*cm]
    ))
    story.append(Spacer(1, 8))

    # Bar chart pendapatan per kelas
    chart_rev = simple_bar_chart(
        ["Private","Couple","Group","Chair","Tambahan","Mandiri"],
        [d_m['rev_private'], d_m['rev_couple'], d_m['rev_group'],
         d_m['rev_chair'],   d_m['rev_tambahan'], d_m['rev_mandiri']],
        [C_BLUE, C_GREEN, C_AMBER, HexColor("#534AB7"),
         HexColor("#1D9E75"), C_GRAY],
        width=380, height=120
    )
    story.append(chart_rev)
    story.append(Paragraph("Gambar 4 — Distribusi pendapatan per kategori kelas (Rp/bulan)", S["caption"]))
    story.append(Spacer(1, 8))

    # Biaya
    story.append(Paragraph("4.2  Rincian Biaya Operasional", S["subsection"]))
    biaya_rows = [
        [("Gaji trainer",        "tbl_cell"), (f"Rp {fmt(d_m['b_trainer'])}", "tbl_num_r"), ("Tetap","tbl_cell")],
        [("Insentif Private",    "tbl_cell"), (f"Rp {fmt(d_m['ins_tot_private'])}", "tbl_num_r"), ("Variabel","tbl_cell")],
        [("Insentif Couple",     "tbl_cell"), (f"Rp {fmt(d_m['ins_tot_couple'])}", "tbl_num_r"), ("Variabel","tbl_cell")],
        [("Insentif Group",      "tbl_cell"), (f"Rp {fmt(d_m['ins_tot_group'])}", "tbl_num_r"), ("Variabel","tbl_cell")],
        [("Insentif Chair",      "tbl_cell"), (f"Rp {fmt(d_m['ins_tot_chair'])}", "tbl_num_r"), ("Variabel","tbl_cell")],
        [("Insentif Tambahan",   "tbl_cell"), (f"Rp {fmt(d_m['ins_tot_tambahan'])}", "tbl_num_r"), ("Variabel","tbl_cell")],
        [("Administrasi & ATK",  "tbl_cell"), (f"Rp {fmt(d_m['b_admin'])}", "tbl_num_r"), ("Tetap","tbl_cell")],
        [("Marketing & promosi", "tbl_cell"), (f"Rp {fmt(d_m['b_mkt'])}", "tbl_num_r"), ("Tetap","tbl_cell")],
        [("Maintenance alat",    "tbl_cell"), (f"Rp {fmt(d_m['b_maint'])}", "tbl_num_r"), ("Tetap","tbl_cell")],
        [("Pelatihan SDM",       "tbl_cell"), (f"Rp {fmt(d_m['b_sdm'])}", "tbl_num_r"), ("Tetap","tbl_cell")],
        [("Perlengkapan habis pakai","tbl_cell"), (f"Rp {fmt(d_m['b_supply'])}", "tbl_num_r"), ("Tetap","tbl_cell")],
        [("Manajemen operasional","tbl_cell"), (f"Rp {fmt(d_m['b_mgmt'])}", "tbl_num_r"), ("Tetap","tbl_cell")],
        [("<b>TOTAL BIAYA</b>",  "tbl_cell"), (f"<b>Rp {fmt(d_m['total_opex'])}</b>","tbl_num_r"), ("","tbl_cell")],
    ]
    story.append(data_table(
        ["Komponen Biaya","Jumlah (Rp)","Jenis"],
        biaya_rows, [8.5*cm, 5*cm, 3*cm]
    ))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # HALAMAN 6 — ROI & PAYBACK SEMUA SKENARIO
    # ══════════════════════════════════════════════════════════════════════
    story += section_rule("5.  ROI & PAYBACK PERIOD — SEMUA SKENARIO")
    story.append(Spacer(1, 4))

    for nama, d, clr in [("Skenario Pesimis", d_p, C_PESIMIS),
                          ("Skenario Moderat", d_m, C_MODERAT),
                          ("Skenario Optimis", d_o, C_OPTIMIS)]:
        bep  = f"Bulan ke-{d['bep_month']}"    if d['bep_month']    else "Belum tercapai dalam proyeksi"
        bep2 = f"Bulan ke-{d['bep_month_ii']}" if d['bep_month_ii'] else "Belum tercapai dalam proyeksi"
        cum_o = d["cum_owner"][-1]
        cum_p = d["cum_pengelola"][-1]

        box = Table([
            [Paragraph(f"<b>{nama}</b>", ParagraphStyle("bn",
                fontName="Helvetica-Bold", fontSize=11,
                textColor=clr, alignment=TA_LEFT))],
            [Table([
                [Paragraph("ROI Owner / thn",       S["caption"]),
                 Paragraph("ROI Pengelola / thn",   S["caption"]),
                 Paragraph("Payback Owner",          S["caption"]),
                 Paragraph("Payback Pengelola",      S["caption"])],
                [Paragraph(f"<b>{pct(d['roi_pct'])}</b>",    S["subsection"]),
                 Paragraph(f"<b>{pct(d['roi_ii_pct'])}</b>", S["subsection"]),
                 Paragraph(f"<b>{bep}</b>",                  S["body_sm"]),
                 Paragraph(f"<b>{bep2}</b>",                 S["body_sm"])],
                [Paragraph(f"Kumulatif {proj_years}thn: Rp {fmt(cum_o)}", S["body_sm"]),
                 Paragraph(f"Kumulatif {proj_years}thn: Rp {fmt(cum_p)}", S["body_sm"]),
                 Paragraph(f"Modal: Rp {fmt(investasi)}", S["body_sm"]),
                 Paragraph(f"Modal: Rp {fmt(modal_pengelola)}", S["body_sm"])],
            ], colWidths=[(W-3.5*cm)/4]*4,
               style=TableStyle([
                   ("TOPPADDING",    (0,0),(-1,-1), 2),
                   ("BOTTOMPADDING", (0,0),(-1,-1), 2),
                   ("LEFTPADDING",   (0,0),(-1,-1), 4),
                   ("GRID",          (0,0),(-1,-1), 0.3, C_BORDER),
               ]))],
        ], colWidths=[W - 3*cm])
        box.setStyle(TableStyle([
            ("BOX",          (0,0),(-1,-1), 1.5, clr),
            ("TOPPADDING",   (0,0),(-1,-1), 8),
            ("BOTTOMPADDING",(0,0),(-1,-1), 8),
            ("LEFTPADDING",  (0,0),(-1,-1), 10),
            ("RIGHTPADDING", (0,0),(-1,-1), 10),
            ("BACKGROUND",   (0,0),(-1,-1), HexColor("#FAFAF8")),
        ]))
        story.append(KeepTogether([box, Spacer(1, 8)]))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════
    # HALAMAN 7 — ANALISIS & REKOMENDASI
    # ══════════════════════════════════════════════════════════════════════
    story += section_rule("6.  ANALISIS & REKOMENDASI STRATEGIS")
    story.append(Spacer(1, 4))

    viable_m = d_m["total_rev"] >= omzet_min and d_m["laba_bersih"] > 0
    status   = "LAYAK (VIABLE)" if viable_m else "PERLU PENYESUAIAN"
    clr_status = C_GREEN if viable_m else C_RED

    story.append(Paragraph("6.1  Status Kelayakan", S["subsection"]))
    story.append(Paragraph(
        f'Berdasarkan skenario moderat, GGAC dinyatakan '
        f'<font color="{clr_status.hexval()}"><b>{status}</b></font>. '
        f'Omzet proyeksi Rp {fmt(d_m["total_rev"])}/bulan '
        f'{"melampaui" if d_m["bep_met"] else "belum mencapai"} '
        f'target minimum BEP Rp {fmt(omzet_min)}/bulan. '
        f'Margin laba bersih {pct(d_m["margin"])} tergolong '
        f'{"sangat sehat" if d_m["margin"]>30 else "cukup baik" if d_m["margin"]>15 else "tipis"}.',
        S["body"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("6.2  Rekomendasi Operasional", S["subsection"]))
    rekomendasi = [
        ("Scale kelas chair exercise",
         "Kapasitas 10 orang per sesi dengan insentif trainer rendah menghasilkan "
         "margin bersih tertinggi. Target 30+ sesi/bulan."),
        ("Dorong konversi ke paket 16x",
         "Komitmen klien lebih panjang meningkatkan predictability pendapatan "
         "dan mengurangi churn."),
        ("Efisiensi kelas tambahan",
         "Taichi/yoga/zumba sangat efisien jika satu trainer bisa merangkap "
         "beberapa kelas per hari."),
        ("Program mandiri tanpa PT",
         "Insentif Rp 0 dengan pendapatan Rp 50.000/kunjungan — "
         "pure passive revenue dengan beban operasional minimal."),
        ("Review insentif berkala",
         "Kelas dengan utilisasi rendah namun insentif tinggi perlu dievaluasi "
         "setiap 6 bulan."),
        ("Evaluasi bagi hasil bulan ke-24",
         "Sesuai klausul term sheet — jika performa melampaui target, "
         "negosiasi ulang skema bagi hasil dapat dilakukan."),
    ]
    for i, (judul, isi) in enumerate(rekomendasi, 1):
        story.append(Paragraph(
            f"<b>{i}.  {judul}</b><br/>{isi}", S["bullet"]))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 8))
    story.append(Paragraph("6.3  Risiko yang Perlu Diperhatikan", S["subsection"]))
    risiko = [
        "Utilisasi di bawah 55% akan menyebabkan omzet tidak mencapai BEP minimum.",
        "Kenaikan UMR/biaya trainer yang melebihi asumsi 5%/tahun akan menekan margin.",
        "Churn klien lansia lebih tinggi dari populasi umum — program retensi diperlukan.",
        "Ketergantungan pada satu trainer utama — perlu rencana backup SDM.",
        "Term sheet perlu mempertegas klausul BEP nominal, pelaporan keuangan bulanan, "
        "dan status klien existing jika kerjasama berakhir.",
    ]
    for r in risiko:
        story.append(Paragraph(f"▸  {r}", S["bullet"]))
        story.append(Spacer(1, 2))

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Laporan ini dihasilkan secara otomatis oleh GGAC ROI Calculator. "
        "Semua angka bersifat proyeksi berdasarkan asumsi yang dapat berubah. "
        "Disarankan untuk melakukan review berkala setiap 6 bulan.",
        S["caption"]))

    # ── Build ─────────────────────────────────────────────────────────────────
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    return buf.getvalue()
