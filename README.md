# 📊 Dashboard Kependudukan Kota Samarinda

Dashboard interaktif untuk visualisasi data kependudukan Kota Samarinda tahun 2022-2024.

## 🌐 Live Demo

**Dashboard:** https://dashboard-kependudukan.streamlit.app

## ✨ Fitur

### 📈 Analisis Single Tahun
- **Ringkasan Data Demografi:**
  - Total Penduduk dengan trend chart
  - Pertumbuhan Penduduk vs tahun sebelumnya
  - Usia Produktif (15-64 tahun)
  - Rasio Dependensi
  - Kecamatan Terbesar
  
- **Visualisasi:**
  - Piramida Penduduk berdasarkan kelompok umur dan gender
  - Trend Pertumbuhan Penduduk
  - Analisis per Kecamatan
  - Distribusi Gender
  - Top N Kelurahan

- **Filter:**
  - Filter Tahun (2022, 2023, 2024)
  - Filter Kecamatan
  - Filter Kelurahan (dependent pada kecamatan)
  - Filter Range Umur (0-75+)

### 📊 Perbandingan Multi Tahun
- Pilih multiple tahun untuk dibandingkan
- Trend populasi antar tahun
- Tabel perbandingan detail dengan % pertumbuhan
- Download data perbandingan

## 🚀 Deployment

### Untuk Streamlit Cloud (Gratis)

1. **Fork/Clone repository ini**

2. **Buka Streamlit Cloud:**
   - Kunjungi: https://streamlit.io/cloud
   - Sign in dengan GitHub
   - Click "New app"

3. **Konfigurasi:**
   - Repository: pilih repo ini
   - Branch: `main`
   - Main file path: `dashboard_samarinda.py`

4. **Deploy!**
   - URL akan jadi: `https://[app-name].streamlit.app`

### Embed ke Website Satudata

Tambahkan kode ini ke halaman Satudata:

```html
<!-- Full Page Embed -->
<iframe 
  src="https://[app-name].streamlit.app/?embedded=true" 
  width="100%" 
  height="800px" 
  frameborder="0"
  style="border: none;">
</iframe>
```

## 📁 Struktur File

```
samarinda-dashboard/
├── dashboard_samarinda.py    # Main dashboard
├── DATA PROJECT.xlsx          # Data kependudukan
├── requirements.txt           # Python dependencies
├── .streamlit/
│   └── config.toml           # Streamlit configuration
├── .gitignore                # Git ignore rules
└── README.md                 # Dokumentasi ini
```

## 💾 Update Data

### Untuk Tahun Baru (2025, 2026, dst)

1. **Siapkan file Excel baru** dengan format yang sama
2. **Merge dengan data lama**
3. **Upload ke GitHub**
4. **Streamlit Cloud auto-deploy!**

## 🛠️ Development Lokal

```bash
pip install -r requirements.txt
streamlit run dashboard_samarinda.py
```

## 📊 Sumber Data

**Sumber:** Dinas Kependudukan dan Pencatatan Sipil Kota Samarinda  
**Periode:** 2022 - 2024

---

**Dibuat dengan ❤️ untuk Kota Samarinda**
