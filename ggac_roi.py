import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="GGAC ROI Calculator",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.main { background-color: #F7F6F2; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }

.metric-card {
    background: #FFFFFF; border-radius: 16px;
    padding: 1.25rem 1.5rem; border: 1px solid #E8E6DE; margin-bottom: 12px;
}
.metric-label {
    font-size: 12px; color: #888780; font-weight: 500;
    text-transform: uppercase; letter-spacing: .06em; margin-bottom: 4px;
}
.metric-value {
    font-size: 26px; font-weight: 700;
    font-family: 'DM Mono', monospace; margin-bottom: 2px;
}
.metric-sub { font-size: 12px; color: #888780; }
.green { color: #0F6E56; }
.blue  { color: #185FA5; }
.amber { color: #854F0B; }
.red   { color: #A32D2D; }

.section-header {
    font-size: 11px; font-weight: 600; color: #888780;
    text-transform: uppercase; letter-spacing: .1em;
    border-bottom: 1px solid #E8E6DE;
    padding-bottom: 8px; margin-bottom: 16px; margin-top: 24px;
}
.breakdown-table { width: 100%; border-collapse: collapse; }
.breakdown-table td {
    padding: 8px 0; border-bottom: 1px solid #F0EEE8; font-size: 14px;
}
.breakdown-table td:last-child {
    text-align: right; font-family: 'DM Mono', monospace; font-weight: 500;
}
.breakdown-table .total-row td {
    font-weight: 700; font-size: 15px;
    border-top: 2px solid #D3D1C7; border-bottom: none;
}
.breakdown-table .sub-row td {
    font-size: 12px; color: #888780; padding: 3px 0 3px 16px;
    border-bottom: none; font-style: italic;
}
.badge {
    display: inline-block; padding: 3px 10px;
    border-radius: 20px; font-size: 11px; font-weight: 600;
}
.badge-green { background: #E1F5EE; color: #0F6E56; }
.badge-red   { background: #FCEBEB; color: #A32D2D; }
.badge-amber { background: #FAEEDA; color: #854F0B; }

.written-card {
    background: #FFFFFF; border-radius: 16px;
    padding: 1.5rem 2rem; border: 1px solid #E8E6DE;
    font-size: 14px; line-height: 1.8; color: #444441;
}
.written-card h4 { color: #2C2C2A; font-size: 15px; margin-bottom: 8px; margin-top: 16px; }
.written-card h4:first-child { margin-top: 0; }

.hero-banner {
    background: linear-gradient(135deg, #0F6E56 0%, #185FA5 100%);
    border-radius: 20px; padding: 2rem 2.5rem; margin-bottom: 2rem; color: white;
}
.hero-banner h1 { font-size: 28px; font-weight: 700; margin-bottom: 4px; }
.hero-banner p  { font-size: 14px; opacity: .8; margin: 0; }
</style>
""", unsafe_allow_html=True)


# ─── HELPERS ─────────────────────────────────────────────────────────────────
def fmt_rp(n):
    if abs(n) >= 1_000_000:
        return f"Rp {n/1_000_000:.1f}jt"
    return f"Rp {int(round(n)):,}".replace(",", ".")

def fmt_full(n):
    return f"Rp {int(round(abs(n))):,}".replace(",", ".")

# Semua teks chart hitam agar terbaca di background putih
CHART_FONT   = dict(family="Plus Jakarta Sans", size=12, color="#1a1a1a")
TICK_FONT    = dict(color="#1a1a1a", size=11)
TITLE_FONT   = dict(color="#1a1a1a", size=12)


# ─── HERO ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
  <h1>💪 GGAC ROI Calculator</h1>
  <p>GREKO Golden Age Center — Simulasi Investasi &amp; Proyeksi Keuangan</p>
</div>
""", unsafe_allow_html=True)


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Parameter")

    st.markdown('<div class="section-header">Investasi &amp; Bagi Hasil</div>', unsafe_allow_html=True)
    investasi = st.number_input("Total investasi owner (Rp)", value=150_000_000, step=5_000_000, format="%d")
    omzet_min = st.number_input("Target omzet minimum BEP (Rp/bln)", value=20_000_000, step=500_000, format="%d")
    share_ii  = st.slider("Bagi hasil pengelola (%)", 50, 90, 70, 5)
    share_i   = 100 - share_ii
    st.caption(f"Pengelola: **{share_ii}%**  |  Owner: **{share_i}%**")

    st.markdown('<div class="section-header">Volume Kelas / Bulan</div>', unsafe_allow_html=True)
    q_private  = st.number_input("Private 1-on-1 (sesi/bln)",           value=40, min_value=0, step=4)
    q_couple   = st.number_input("Couple / ber-2 (sesi/bln)",            value=16, min_value=0, step=2)
    q_group    = st.number_input("Group 3-4 orang (sesi/bln)",           value=24, min_value=0, step=4)
    q_chair    = st.number_input("Chair exercise (sesi/bln)",             value=20, min_value=0, step=2)
    q_tambahan = st.number_input("Kelas tambahan taichi/yoga (sesi/bln)", value=8,  min_value=0, step=2)
    q_mandiri  = st.number_input("Mandiri tanpa PT (kunjungan/bln)",      value=30, min_value=0, step=5)

    st.markdown('<div class="section-header">Biaya Tetap / Bulan</div>', unsafe_allow_html=True)
    b_trainer = st.number_input("Gaji trainer (Rp)",             value=6_000_000, step=500_000, format="%d")
    b_admin   = st.number_input("Administrasi &amp; ATK (Rp)",   value=500_000,   step=100_000, format="%d")
    b_mkt     = st.number_input("Marketing &amp; promosi (Rp)",  value=1_500_000, step=100_000, format="%d")
    b_maint   = st.number_input("Maintenance alat (Rp)",         value=800_000,   step=100_000, format="%d")
    b_sdm     = st.number_input("Pelatihan SDM (Rp)",            value=500_000,   step=100_000, format="%d")
    b_supply  = st.number_input("Perlengkapan habis pakai (Rp)", value=400_000,   step=50_000,  format="%d")
    b_mgmt    = st.number_input("Biaya manajemen operasional (Rp)", value=1_000_000, step=100_000, format="%d")

    st.markdown('<div class="section-header">Insentif Trainer per Kelas (Rp/sesi)</div>', unsafe_allow_html=True)
    st.caption("Dihitung dari sesi aktual setelah utilisasi")
    ins_private  = st.number_input("Insentif — Private 1-on-1",   value=30_000, step=5_000, format="%d")
    ins_couple   = st.number_input("Insentif — Couple / ber-2",   value=25_000, step=5_000, format="%d")
    ins_group    = st.number_input("Insentif — Group 3-4 orang",  value=20_000, step=5_000, format="%d")
    ins_chair    = st.number_input("Insentif — Chair exercise",    value=20_000, step=5_000, format="%d")
    ins_tambahan = st.number_input("Insentif — Kelas tambahan",   value=25_000, step=5_000, format="%d")
    ins_mandiri  = st.number_input("Insentif — Mandiri tanpa PT", value=0,      step=5_000, format="%d")

    st.markdown('<div class="section-header">Asumsi Pertumbuhan</div>', unsafe_allow_html=True)
    utilitas    = st.slider("Utilisasi kelas (%)", 50, 100, 80, 5)
    growth      = st.slider("Pertumbuhan pendapatan / tahun (%)", 0, 30, 10, 1)
    cost_growth = st.slider("Kenaikan biaya / tahun (%)", 0, 20, 5, 1)
    proj_years  = st.radio("Proyeksi", [3, 5], horizontal=True)


# ─── KALKULASI ────────────────────────────────────────────────────────────────
u = utilitas / 100

s_private  = q_private  * u
s_couple   = q_couple   * u
s_group    = q_group    * u
s_chair    = q_chair    * u
s_tambahan = q_tambahan * u
s_mandiri  = q_mandiri  * u

rev_private  = s_private  * 195_000
rev_couple   = s_couple   * 2 * 160_000
rev_group    = s_group    * 3 * 110_000
rev_chair    = s_chair    * 8 * 75_000
rev_tambahan = s_tambahan * 8 * 100_000
rev_mandiri  = s_mandiri  * 50_000
total_rev    = rev_private + rev_couple + rev_group + rev_chair + rev_tambahan + rev_mandiri

ins_tot_private  = s_private  * ins_private
ins_tot_couple   = s_couple   * ins_couple
ins_tot_group    = s_group    * ins_group
ins_tot_chair    = s_chair    * ins_chair
ins_tot_tambahan = s_tambahan * ins_tambahan
ins_tot_mandiri  = s_mandiri  * ins_mandiri
total_insentif   = (ins_tot_private + ins_tot_couple + ins_tot_group
                    + ins_tot_chair + ins_tot_tambahan + ins_tot_mandiri)

b_fixed    = b_trainer + b_admin + b_mkt + b_maint + b_sdm + b_supply + b_mgmt
total_opex = b_fixed + total_insentif

laba_bersih = total_rev - total_opex
hasil_ii    = laba_bersih * (share_ii / 100) if laba_bersih > 0 else 0
hasil_i     = laba_bersih * (share_i  / 100) if laba_bersih > 0 else 0
bep_met     = total_rev >= omzet_min
roi_pct     = (hasil_i * 12 / investasi * 100) if investasi > 0 else 0
margin      = (laba_bersih / total_rev * 100) if total_rev > 0 else 0

months        = proj_years * 12
cum_owner     = [-investasi]
cum_pengelola = [0]
bep_month     = None

for m in range(1, months + 1):
    yr      = (m - 1) // 12
    rev_m   = total_rev  * ((1 + growth      / 100) ** yr)
    opex_m  = total_opex * ((1 + cost_growth / 100) ** yr)
    laba_m  = rev_m - opex_m
    earn_i  = laba_m * (share_i  / 100) if laba_m > 0 and rev_m >= omzet_min else 0
    earn_ii = laba_m * (share_ii / 100) if laba_m > 0 and rev_m >= omzet_min else 0
    cum_owner.append(cum_owner[-1] + earn_i)
    cum_pengelola.append(cum_pengelola[-1] + earn_ii)
    if bep_month is None and cum_owner[-1] >= 0:
        bep_month = m


# ─── METRIC CARDS ─────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
badge_bep = ('<span class="badge badge-green">✓ Di atas BEP</span>'
             if bep_met else '<span class="badge badge-red">✗ Belum BEP</span>')

with c1:
    cls = "green" if laba_bersih >= 0 else "red"
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Laba bersih / bulan</div>
      <div class="metric-value {cls}">{fmt_rp(laba_bersih)}</div>
      <div class="metric-sub">Margin {margin:.1f}%</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Omzet / bulan</div>
      <div class="metric-value blue">{fmt_rp(total_rev)}</div>
      <div class="metric-sub">{badge_bep}</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Bagian pengelola / bulan</div>
      <div class="metric-value green">{fmt_rp(hasil_ii)}</div>
      <div class="metric-sub">{share_ii}% dari laba bersih</div>
    </div>""", unsafe_allow_html=True)

with c4:
    bep_str = f"BEP bln ke-{bep_month}" if bep_month else "BEP belum tercapai"
    roi_cls = "green" if roi_pct >= 15 else "amber" if roi_pct >= 5 else "red"
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">ROI owner / tahun</div>
      <div class="metric-value {roi_cls}">{roi_pct:.1f}%</div>
      <div class="metric-sub">{bep_str}</div>
    </div>""", unsafe_allow_html=True)


# ─── INSENTIF EXPANDER ────────────────────────────────────────────────────────
insentif_rows = [
    ("Private 1-on-1",   s_private,  ins_private,  ins_tot_private),
    ("Couple / ber-2",   s_couple,   ins_couple,   ins_tot_couple),
    ("Group 3-4 orang",  s_group,    ins_group,    ins_tot_group),
    ("Chair exercise",   s_chair,    ins_chair,    ins_tot_chair),
    ("Kelas tambahan",   s_tambahan, ins_tambahan, ins_tot_tambahan),
    ("Mandiri tanpa PT", s_mandiri,  ins_mandiri,  ins_tot_mandiri),
]

with st.expander("📋 Rincian insentif trainer per kelas bulan ini", expanded=False):
    rows_ins_exp = "".join(
        f'<tr>'
        f'<td style="color:#444441;padding:6px 0;border-bottom:1px solid #F0EEE8">{lbl}</td>'
        f'<td style="color:#888780;text-align:center;padding:6px 4px;border-bottom:1px solid #F0EEE8">'
        f'{sesi:.1f} sesi × {fmt_rp(rate)}</td>'
        f'<td style="font-family:DM Mono,monospace;font-weight:500;color:#A32D2D;'
        f'text-align:right;padding:6px 0;border-bottom:1px solid #F0EEE8">-{fmt_full(total)}</td>'
        f'</tr>'
        for lbl, sesi, rate, total in insentif_rows
    )
    st.markdown(f"""
    <table class="breakdown-table" style="font-size:13px">
      <thead><tr>
        <th style="text-align:left;font-size:11px;color:#888780;padding-bottom:6px;
                   border-bottom:2px solid #D3D1C7;font-weight:600">Kelas</th>
        <th style="text-align:center;font-size:11px;color:#888780;padding-bottom:6px;
                   border-bottom:2px solid #D3D1C7;font-weight:600">Sesi × Tarif</th>
        <th style="text-align:right;font-size:11px;color:#888780;padding-bottom:6px;
                   border-bottom:2px solid #D3D1C7;font-weight:600">Total Insentif</th>
      </tr></thead>
      <tbody>{rows_ins_exp}</tbody>
      <tfoot><tr class="total-row">
        <td colspan="2">Total insentif trainer</td>
        <td style="color:#A32D2D">-{fmt_full(total_insentif)}</td>
      </tr></tfoot>
    </table>""", unsafe_allow_html=True)


# ─── CHARTS ───────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown('<div class="section-header">📈 Proyeksi Arus Kas Kumulatif</div>', unsafe_allow_html=True)
    months_list = list(range(0, months + 1))

    fig_cash = go.Figure()
    fig_cash.add_trace(go.Scatter(
        x=months_list, y=cum_owner,
        name="Owner (kumulatif)",
        line=dict(color="#0F6E56", width=2.5),
        fill="tozeroy", fillcolor="rgba(15,110,86,.08)"
    ))
    fig_cash.add_trace(go.Scatter(
        x=months_list, y=cum_pengelola,
        name="Pengelola (kumulatif)",
        line=dict(color="#185FA5", width=2.5),
        fill="tozeroy", fillcolor="rgba(24,95,165,.06)"
    ))
    fig_cash.add_hline(
        y=0, line_dash="dash", line_color="#E24B4A", line_width=1.5,
        annotation_text="Break-even",
        annotation_font=dict(color="#1a1a1a", size=11)
    )
    if bep_month:
        fig_cash.add_vline(
            x=bep_month, line_dash="dot", line_color="#BA7517", line_width=1.5,
            annotation_text=f"BEP bln {bep_month}",
            annotation_position="top left",
            annotation_font=dict(color="#1a1a1a", size=11)
        )
    fig_cash.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        font=CHART_FONT,
        margin=dict(l=16, r=16, t=16, b=48),
        height=320,
        xaxis=dict(
            title=dict(text="Bulan", font=TITLE_FONT),
            tickfont=TICK_FONT,
            gridcolor="#F0EEE8", linecolor="#D3D1C7"
        ),
        yaxis=dict(
            title=dict(text="Rp", font=TITLE_FONT),
            tickfont=TICK_FONT,
            gridcolor="#F0EEE8", linecolor="#D3D1C7",
            tickformat=",.0f", tickprefix="Rp "
        ),
        legend=dict(
            orientation="h", y=-0.22, x=0,
            font=dict(color="#1a1a1a", size=11)
        ),
        hovermode="x unified"
    )
    st.plotly_chart(fig_cash, use_container_width=True)

with col_right:
    st.markdown('<div class="section-header">🎯 Pendapatan per Kategori Kelas</div>', unsafe_allow_html=True)
    rev_chart_data = [
        ("Private",        rev_private),
        ("Couple",         rev_couple),
        ("Group",          rev_group),
        ("Chair exercise", rev_chair),
        ("Tambahan",       rev_tambahan),
        ("Mandiri",        rev_mandiri),
    ]
    df_rev     = (pd.DataFrame(rev_chart_data, columns=["Kategori", "Pendapatan"])
                    .sort_values("Pendapatan", ascending=True))
    bar_colors = ["#888780", "#534AB7", "#1D9E75", "#BA7517", "#0F6E56", "#185FA5"]

    fig_bar = go.Figure(go.Bar(
        x=df_rev["Pendapatan"],
        y=df_rev["Kategori"],
        orientation="h",
        marker_color=bar_colors,
        text=[fmt_rp(v) for v in df_rev["Pendapatan"]],
        textposition="outside",
        textfont=dict(size=11, color="#1a1a1a")
    ))
    fig_bar.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        font=CHART_FONT,
        margin=dict(l=16, r=90, t=16, b=16),
        height=320,
        xaxis=dict(showgrid=False, showticklabels=False, tickfont=TICK_FONT),
        yaxis=dict(gridcolor="#F0EEE8", linecolor="#D3D1C7", tickfont=TICK_FONT),
        showlegend=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)


# ─── WATERFALL ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🌊 Waterfall: Omzet → Laba Bersih</div>', unsafe_allow_html=True)

wf_labels = [
    "Omzet",
    "Gaji trainer", "Admin", "Marketing", "Maintenance", "Pelatihan SDM", "Perlengkapan", "Manajemen",
    "Insentif\nPrivate", "Insentif\nCouple", "Insentif\nGroup",
    "Insentif\nChair", "Insentif\nTambahan", "Insentif\nMandiri",
    "Laba Bersih"
]
wf_values = [
    total_rev,
    -b_trainer, -b_admin, -b_mkt, -b_maint, -b_sdm, -b_supply, -b_mgmt,
    -ins_tot_private, -ins_tot_couple, -ins_tot_group,
    -ins_tot_chair, -ins_tot_tambahan, -ins_tot_mandiri,
    laba_bersih
]
wf_measure = ["absolute"] + ["relative"] * (len(wf_labels) - 2) + ["total"]

fig_wf = go.Figure(go.Waterfall(
    orientation="v",
    measure=wf_measure,
    x=wf_labels,
    y=wf_values,
    text=[fmt_rp(abs(v)) for v in wf_values],
    textposition="outside",
    textfont=dict(size=10, color="#1a1a1a"),
    connector=dict(line=dict(color="#D3D1C7", width=1, dash="dot")),
    increasing=dict(marker_color="#0F6E56"),
    decreasing=dict(marker_color="#E24B4A"),
    totals=dict(marker_color="#185FA5")
))
fig_wf.update_layout(
    paper_bgcolor="white", plot_bgcolor="white",
    font=CHART_FONT,
    margin=dict(l=16, r=16, t=24, b=16),
    height=380,
    xaxis=dict(tickfont=dict(color="#1a1a1a", size=10), linecolor="#D3D1C7", gridcolor="#F0EEE8"),
    yaxis=dict(tickfont=TICK_FONT, gridcolor="#F0EEE8", linecolor="#D3D1C7",
               tickformat=",.0f", tickprefix="Rp "),
    showlegend=False
)
st.plotly_chart(fig_wf, use_container_width=True)


# ─── PROYEKSI TAHUNAN ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📅 Tabel Proyeksi Tahunan</div>', unsafe_allow_html=True)
yearly = []
for yr in range(1, proj_years + 1):
    rev_yr      = total_rev  * ((1 + growth      / 100) ** (yr - 1)) * 12
    opex_yr     = total_opex * ((1 + cost_growth / 100) ** (yr - 1)) * 12
    ins_yr      = total_insentif * ((1 + cost_growth / 100) ** (yr - 1)) * 12
    laba_yr     = rev_yr - opex_yr
    earn_i      = laba_yr * (share_i  / 100) if laba_yr > 0 else 0
    earn_ii     = laba_yr * (share_ii / 100) if laba_yr > 0 else 0
    yearly.append({
        "Tahun":                              f"Tahun {yr}",
        "Omzet (Rp)":                         fmt_full(rev_yr),
        "Total Biaya (Rp)":                   fmt_full(opex_yr),
        "  — Insentif (Rp)":                  fmt_full(ins_yr),
        "Laba Bersih (Rp)":                   fmt_full(laba_yr),
        f"Bagian Owner {share_i}% (Rp)":      fmt_full(earn_i),
        f"Bagian Pengelola {share_ii}% (Rp)": fmt_full(earn_ii),
    })

df_yearly = pd.DataFrame(yearly).set_index("Tahun")
st.dataframe(df_yearly, use_container_width=True)


# ─── BREAKDOWN ────────────────────────────────────────────────────────────────
col_bd1, col_bd2 = st.columns(2)

with col_bd1:
    st.markdown('<div class="section-header">💰 Breakdown Pendapatan</div>', unsafe_allow_html=True)
    rev_items = [
        ("Private 1-on-1",   rev_private),
        ("Couple / ber-2",   rev_couple),
        ("Group 3-4 orang",  rev_group),
        ("Chair exercise",   rev_chair),
        ("Kelas tambahan",   rev_tambahan),
        ("Mandiri tanpa PT", rev_mandiri),
    ]
    rows_rev = "".join(
        f'<tr><td style="color:#444441">{lbl}</td>'
        f'<td class="green">+{fmt_full(val)}</td></tr>'
        for lbl, val in rev_items
    )
    st.markdown(f"""
    <table class="breakdown-table">
      {rows_rev}
      <tr class="total-row">
        <td>Total omzet</td><td class="green">+{fmt_full(total_rev)}</td>
      </tr>
    </table>""", unsafe_allow_html=True)

with col_bd2:
    st.markdown('<div class="section-header">📊 Breakdown Biaya &amp; Bagi Hasil</div>', unsafe_allow_html=True)
    fixed_items = [
        ("Gaji trainer",    b_trainer),
        ("Administrasi",    b_admin),
        ("Marketing",       b_mkt),
        ("Maintenance alat",b_maint),
        ("Pelatihan SDM",   b_sdm),
        ("Perlengkapan",    b_supply),
        ("Manajemen",       b_mgmt),
    ]
    rows_fixed = "".join(
        f'<tr><td style="color:#444441">{lbl}</td>'
        f'<td class="red">-{fmt_full(val)}</td></tr>'
        for lbl, val in fixed_items
    )
    insentif_sub = [
        ("↳ Private 1-on-1",   ins_tot_private),
        ("↳ Couple / ber-2",   ins_tot_couple),
        ("↳ Group 3-4 orang",  ins_tot_group),
        ("↳ Chair exercise",   ins_tot_chair),
        ("↳ Kelas tambahan",   ins_tot_tambahan),
        ("↳ Mandiri tanpa PT", ins_tot_mandiri),
    ]
    rows_ins_sub = "".join(
        f'<tr class="sub-row"><td>{lbl}</td>'
        f'<td class="red" style="text-align:right;font-size:12px">-{fmt_full(val)}</td></tr>'
        for lbl, val in insentif_sub
    )
    laba_cls  = "green" if laba_bersih >= 0 else "red"
    laba_sign = "+" if laba_bersih >= 0 else "-"

    st.markdown(f"""
    <table class="breakdown-table">
      {rows_fixed}
      <tr>
        <td style="color:#444441;font-weight:500">Insentif trainer (per kelas)</td>
        <td class="red">-{fmt_full(total_insentif)}</td>
      </tr>
      {rows_ins_sub}
      <tr class="total-row">
        <td>Total biaya operasional</td><td class="red">-{fmt_full(total_opex)}</td>
      </tr>
      <tr class="total-row">
        <td>Laba bersih</td>
        <td class="{laba_cls}">{laba_sign}{fmt_full(abs(laba_bersih))}</td>
      </tr>
      <tr>
        <td style="color:#444441">Bagian pengelola ({share_ii}%)</td>
        <td class="green">+{fmt_full(hasil_ii)}</td>
      </tr>
      <tr>
        <td style="color:#444441">Bagian owner ({share_i}%)</td>
        <td class="green">+{fmt_full(hasil_i)}</td>
      </tr>
    </table>""", unsafe_allow_html=True)


# ─── WRITTEN BREAKDOWN ────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📝 Analisis &amp; Rekomendasi</div>', unsafe_allow_html=True)

viable      = total_rev >= omzet_min and laba_bersih > 0
badge_str   = ('<span class="badge badge-green">✅ Layak (Viable)</span>'
               if viable else '<span class="badge badge-red">⚠️ Perlu Penyesuaian</span>')
bep_str2    = f"bulan ke-{bep_month}" if bep_month else "belum tercapai dalam rentang proyeksi ini"
roi_rank    = "sangat menarik" if roi_pct > 20 else "menarik" if roi_pct > 10 else "perlu review"
margin_rank = "sangat sehat" if margin > 30 else "cukup baik" if margin > 15 else "tipis, perlu optimasi"
top_rev     = max(rev_items, key=lambda x: x[1])
ins_pct     = (total_insentif / total_opex * 100) if total_opex > 0 else 0
ins_top     = max(insentif_sub, key=lambda x: x[1])

st.markdown(f"""
<div class="written-card">
  <h4>Status Kelayakan {badge_str}</h4>
  <p>
    Dengan utilisasi <strong>{utilitas}%</strong>, GGAC memproyeksikan omzet bulanan sebesar
    <strong>{fmt_full(total_rev)}</strong>.
    {"Omzet ini sudah melampaui target minimum BEP sebesar <strong>" + fmt_full(omzet_min) + "</strong>, sehingga bagi hasil sudah dapat mulai diperhitungkan sesuai term sheet." if bep_met else "Omzet ini belum mencapai target minimum BEP sebesar <strong>" + fmt_full(omzet_min) + "</strong>. Bagi hasil belum dapat dibagikan."}
  </p>

  <h4>Analisis Insentif Trainer</h4>
  <p>
    Total insentif trainer per bulan sebesar <strong>{fmt_full(total_insentif)}</strong>,
    setara <strong>{ins_pct:.1f}%</strong> dari total biaya operasional.
    Insentif terbesar berasal dari kelas <strong>{ins_top[0].replace("↳ ", "")}</strong>
    sebesar <strong>{fmt_full(ins_top[1])}</strong>.
    Memecah insentif per kelas memungkinkan evaluasi mana kelas yang margin bersihnya
    paling efisien — kelas dengan insentif rendah dan harga tinggi (mis. Group) biasanya
    paling menguntungkan secara bersih.
  </p>

  <h4>Analisis Pendapatan</h4>
  <p>
    Kontribusi terbesar berasal dari <strong>{top_rev[0]}</strong> sebesar
    <strong>{fmt_full(top_rev[1])}/bulan</strong>.
    Margin laba bersih <strong>{margin:.1f}%</strong> terbilang <strong>{margin_rank}</strong>
    untuk bisnis wellness/gym lansia.
  </p>

  <h4>Return on Investment</h4>
  <p>
    Payback period investasi owner diperkirakan tercapai pada <strong>{bep_str2}</strong>.
    ROI tahunan owner sebesar <strong>{roi_pct:.1f}%</strong> tergolong <strong>{roi_rank}</strong>.
    Dalam {proj_years} tahun, kumulatif bagian owner diproyeksikan
    <strong>{fmt_full(cum_owner[-1])}</strong> dan bagian pengelola
    <strong>{fmt_full(cum_pengelola[-1])}</strong>.
  </p>

  <h4>Rekomendasi Strategis</h4>
  <ol style="padding-left:1.2rem;line-height:2">
    <li><strong>Scale chair exercise</strong> — kapasitas 10 orang, insentif per sesi kecil, margin bersih tertinggi.</li>
    <li><strong>Konversi ke paket 16x</strong> — komitmen klien lebih panjang dan pendapatan lebih predictable.</li>
    <li><strong>Review insentif per kelas secara berkala</strong> — kelas utilisasi rendah + insentif tinggi perlu dievaluasi.</li>
    <li><strong>Kelas tambahan taichi/yoga/zumba</strong> efisien jika satu trainer merangkap beberapa kelas.</li>
    <li><strong>Program mandiri tanpa PT</strong> — insentif Rp 0, pure passive revenue.</li>
    <li><strong>Evaluasi bagi hasil setelah 24 bulan</strong> sesuai klausul term sheet jika performa melebihi target.</li>
  </ol>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.caption("GGAC ROI Calculator — Berdasarkan Term Sheet Kerjasama Operasional & Pricelist GGAC. Proyeksi bersifat estimasi.")
