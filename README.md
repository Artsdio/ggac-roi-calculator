# 💪 GGAC ROI Calculator

**GREKO Golden Age Center** — Simulasi Investasi & Proyeksi Keuangan

Aplikasi interaktif untuk menghitung ROI kerjasama operasional gym lansia berdasarkan Term Sheet dan Pricelist GGAC.

## Fitur

- Kalkulator investasi & bagi hasil (Owner vs Pengelola)
- Simulasi volume kelas per bulan (Private, Couple, Group, Chair Exercise, dll.)
- **Insentif trainer dipecah per kelas** untuk akurasi lebih tinggi
- Proyeksi arus kas kumulatif 3 atau 5 tahun
- Waterfall chart biaya → laba bersih
- Tabel proyeksi tahunan
- Analisis & rekomendasi otomatis
- Upload file .xlsx untuk update data
- Laporan untuk investor dalam bentuk .pdf

## Pelaporan

Isi laporan PDF (7 halaman)

Cover — nama proyek, tanggal, 3 kotak skenario ringkas
Ringkasan Eksekutif — tabel + bar chart perbandingan 3 skenario
Struktur Modal — kontribusi owner vs pengelola + bar chart porsi
Proyeksi Keuangan — tabel tahunan + line chart arus kas kumulatif
Breakdown Pendapatan & Biaya — per kelas + per komponen biaya
ROI & Payback Period — 3 kotak skenario lengkap dengan angka kumulatif
Analisis & Rekomendasi — narasi kelayakan, 6 rekomendasi strategis, 5 risiko

## Cara Pakai

Buka aplikasi di browser, isi parameter di sidebar kiri, hasil langsung terupdate otomatis.

## Jalankan Lokal

```bash
pip install -r requirements.txt
streamlit run ggac_roi.py
```

---
*Berdasarkan Term Sheet Kerjasama Operasional & Pricelist GGAC. Proyeksi bersifat estimasi.*
