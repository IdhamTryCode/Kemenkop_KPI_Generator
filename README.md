# 🚀 Kemenkop KPI Generator

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7+-blue?style=for-the-badge&logo=python)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-green?style=for-the-badge&logo=pandas)
![Status](https://img.shields.io/badge/Status-Ready%20to%20Use-success?style=for-the-badge)

**Generate KPI data untuk Kementerian Koperasi dengan mudah dan cepat! 📊✨**

</div>

---

## 📖 Apa Sih Ini Sebenarnya?

Jadi, proyek ini adalah **data generator** yang super keren untuk menghasilkan data KPI (Key Performance Indicator) koperasi di Indonesia! 🇮🇩

### 🎯 Intinya:
- **Input**: Data mentah koperasi (CSV files) 📁
- **Process**: Script Python yang ngolah data pake pandas 🐼
- **Output**: Data KPI yang sudah di-aggregate dan siap pakai! 📈

### 🧩 Yang Dibuat:

1. **DIM_GEOGRAPHY.csv** 🗺️
   - Dimensi geografi hierarkis (Provinsi → Kabupaten → Kecamatan → Desa)
   - Setiap level punya `geo_key` sendiri-sendiri
   - Total ada ribuan record untuk semua level!

2. **DIM_PERIOD.csv** 📅
   - Dimensi waktu hierarkis (Tahun → Quarter → Bulan → Minggu)
   - Period 2022-2025 (cakep kan? 😎)
   - Setiap level punya `date_key` sendiri

3. **FACT_KPI.csv** 📊
   - **THE MAIN OUTPUT!** 🎉
   - 56 kolom KPI yang dihitung dari data source
   - 1 row per desa per periode
   - Semua KPI dihitung dari data real, bukan random! ✅

### 📊 KPI yang Dihasilkan:

- **Koperasi**: Total, per provinsi, modal, rasio baru, dll
- **Anggota**: Total anggota, rasio gender, simpanan, BI checking
- **Pengurus**: Total pengurus/pengawas, rasio gender, struktur lengkap
- **Gerai**: Total gerai, per koperasi, sebaran provinsi
- **KLU**: Total KLU, top 10, diversifikasi
- **Kemitraan**: Total aplikasi, verified rate, growth rate
- **UPKDK**: Total aktif, akses internet, kondisi bangunan
- **Domain**: Total domain, verifikasi rate
- **Geografi**: Koperasi per desa, penggabungan desa, completeness score

---

## 📁 Struktur Proyek

```
Kemenkop_KPI_Generator/
│
├── 📂 data_source/              # Data mentah (CSV files)
│   ├── cooperative.csv          # Data koperasi
│   ├── cooperative_members.csv   # Data anggota
│   ├── cooperative_management.csv
│   ├── cooperative_outlets.csv
│   ├── cooperative_klus.csv
│   ├── business_partnership_applications.csv
│   ├── upkdk.csv
│   ├── domains.csv
│   ├── villages.csv
│   ├── districts.csv
│   ├── subdistricts.csv
│   ├── provinces.csv
│   ├── dim_klu.csv
│   └── ... (dan file lainnya)
│
├── 📂 result/                   # Output files (hasil generate)
│   ├── DIM_GEOGRAPHY.csv        # ✅ Generated
│   ├── DIM_PERIOD.csv           # ✅ Generated
│   └── FACT_KPI.csv             # ✅ Generated
│
├── 🐍 generate_dimensions.py    # Script untuk generate DIM_GEOGRAPHY & DIM_PERIOD
├── 🐍 generate_fact_kpi.py      # Script untuk generate FACT_KPI
│
└── 📄 README.md                 # File ini! 😄
```

---

## 🛠️ Requirements

### Software yang Dibutuhkan:

- **Python 3.7+** 🐍
  ```bash
  python --version  # Cek versi Python kamu
  ```

- **Libraries Python:**
  ```bash
  pip install pandas numpy
  ```
  
  Atau install semua sekaligus:
  ```bash
  pip install -r requirements.txt
  ```
  
  *(Note: Kalau belum ada `requirements.txt`, install manual aja ya!)*

### Data yang Dibutuhkan:

Pastikan semua file CSV ada di folder `data_source/`:
- ✅ `cooperative.csv`
- ✅ `cooperative_members.csv`
- ✅ `cooperative_management.csv`
- ✅ `cooperative_outlets.csv`
- ✅ `cooperative_klus.csv`
- ✅ `business_partnership_applications.csv`
- ✅ `upkdk.csv`
- ✅ `domains.csv`
- ✅ `cooperative_village_mergers.csv`
- ✅ `villages.csv`
- ✅ `districts.csv`
- ✅ `subdistricts.csv`
- ✅ `provinces.csv`
- ✅ `dim_klu.csv`

---

## 🚀 Cara Menggunakan

### Step 1: Clone atau Download Proyek

```bash
git clone <repo-url>
cd Kemenkop_KPI_Generator
```

Atau download ZIP dan extract! 📦

### Step 2: Siapkan Data Source

Pastikan semua file CSV sudah ada di folder `data_source/`:
```bash
ls data_source/  # Linux/Mac
dir data_source\  # Windows
```

### Step 3: Generate Dimensions (Opsional)

Kalau belum pernah generate atau mau regenerate:

```bash
python generate_dimensions.py
```

**Output:**
- ✅ `result/DIM_GEOGRAPHY.csv`
- ✅ `result/DIM_PERIOD.csv`

**Waktu eksekusi:** ~1-2 menit ⏱️

### Step 4: Generate FACT_KPI (THE MAIN EVENT! 🎯)

```bash
python generate_fact_kpi.py
```

**Output:**
- ✅ `result/FACT_KPI.csv` (atau `FACT_KPI_V001.csv`, `FACT_KPI_V002.csv`, dll)

**Waktu eksekusi:** 
- ⏱️ ~5-15 menit (tergantung spek komputer)
- 📊 Akan generate ~38,000+ rows (satu row per desa yang punya koperasi)

**Progress Log:**
Script akan nunjukin progress real-time:
```
[LOADING]     cooperative.csv                          28.11 MB, 125,941 rows ✓
[LOADING]     cooperative_members.csv                 18.75 MB, 806,234 rows ✓
[PROCESSING]  Village 50/38,053 (0.1%) - ETA: 12m 34s →
[COMPLETE]   Generated 38,053 rows with 56 columns (Time: 8m 23s) ✓
```

---

## 📋 Detail Output Files

### 1. DIM_GEOGRAPHY.csv 🗺️

**Struktur:**
| Column | Type | Description |
|--------|------|-------------|
| `geo_key` | Integer | Primary key (unique) |
| `province_id` | String | Kode provinsi |
| `district_id` | String | Kode kabupaten/kota |
| `subdistrict_id` | String | Kode kecamatan |
| `village_id` | String | Kode desa/kelurahan |
| `province_name` | String | Nama provinsi |
| `district_name` | String | Nama kabupaten/kota |
| `subdistrict_name` | String | Nama kecamatan |
| `village_name` | String | Nama desa/kelurahan |

**Hierarki:**
- Level 1: Provinsi (34 provinsi)
- Level 2: Kabupaten/Kota (500+ kabupaten)
- Level 3: Kecamatan (7000+ kecamatan)
- Level 4: Desa/Kelurahan (80,000+ desa)

### 2. DIM_PERIOD.csv 📅

**Struktur:**
| Column | Type | Description |
|--------|------|-------------|
| `date_key` | Integer | Primary key (unique) |
| `year` | Integer | Tahun (2022-2025) |
| `quarter` | Integer | Quarter (1-4) |
| `month` | Integer | Bulan (1-12) |
| `week` | Integer | Minggu (1-4/5) |
| `period_st` | Date | Tanggal mulai periode |
| `period_end_date` | Date | Tanggal akhir periode |

**Hierarki:**
- Level 1: Tahun (4 tahun)
- Level 2: Quarter (16 quarters)
- Level 3: Bulan (48 bulan)
- Level 4: Minggu (200+ minggu)

### 3. FACT_KPI.csv 📊

**Struktur:**
- **56 kolom** (6 dimension keys + 50 KPI metrics)
- **Grain**: 1 row per `geo_key` (desa) per `date_key` (periode)
- **Total rows**: ~38,000+ (hanya desa yang punya koperasi)

**Dimension Keys:**
- `date_key`, `geo_key`, `outlet_id`, `business_partner_service_id`, `upkdk_id`, `klu_id`

**KPI Categories:**
- Koperasi (8 KPI)
- Anggota (6 KPI)
- Pengurus (4 KPI)
- Gerai (6 KPI)
- KLU (6 KPI)
- Kemitraan (8 KPI)
- UPKDK (5 KPI)
- Domain (2 KPI)
- Geografi (5 KPI)

**Data Types:**
- `BigInt`: Integer besar (untuk count)
- `Dec(18,2)`: Decimal dengan 2 desimal (untuk uang, rata-rata)
- `Dec(5,4)`: Decimal dengan 4 desimal (untuk persentase 0-100)

---

## 🎨 Fitur Keren

### ✨ Real-time Progress Logging
Script nunjukin progress dengan detail:
- File loading dengan ukuran dan row count
- Progress bar dengan ETA
- Waktu eksekusi total

### 🔄 Auto Versioning
File `FACT_KPI.csv` otomatis di-version:
- `FACT_KPI_V001.csv`
- `FACT_KPI_V002.csv`
- dst...

Jadi gak bakal overwrite file sebelumnya! 🎯

### 🛡️ Error Handling
- File not found detection
- Data validation
- Safe division (gak bakal error kalau divide by zero)

### 📈 Data Quality
- **Semua data REAL**, bukan random/faker! ✅
- Semua KPI dihitung dari aggregate data source
- Traceable dan verifiable

---

## 🔍 Troubleshooting

### ❌ Error: File not found

**Problem:**
```
FileNotFoundError: File not found: data_source/cooperative.csv
```

**Solution:**
1. Cek apakah file ada di folder `data_source/`
2. Cek nama file (case-sensitive di Linux/Mac)
3. Pastikan path benar

### ❌ Error: Memory error

**Problem:**
```
MemoryError: Unable to allocate array
```

**Solution:**
1. File `cooperative_management.csv` cukup besar (81 MB)
2. Pastikan RAM cukup (minimal 4GB free)
3. Tutup aplikasi lain yang makan RAM

### ❌ Error: Module not found

**Problem:**
```
ModuleNotFoundError: No module named 'pandas'
```

**Solution:**
```bash
pip install pandas numpy
```

### ⚠️ Warning: Empty result

**Problem:**
FACT_KPI.csv kosong atau sedikit rows

**Solution:**
1. Cek apakah ada koperasi di data source
2. Cek apakah `DIM_GEOGRAPHY.csv` dan `DIM_PERIOD.csv` sudah di-generate
3. Cek log untuk error messages

---

## 📚 Dokumentasi Tambahan

Kalau mau lebih detail, cek file-file ini:

- 📄 `FACT_KPI_GENERATION_DOCUMENTATION.md` - Dokumentasi lengkap proses generasi
- 📄 `fact_kpi_data_types.md` - Data dictionary lengkap
- 📄 `formula_datasource_fact_kpi.md` - Formula KPI detail

---

## 🎯 Quick Start (TL;DR)

```bash
# 1. Install dependencies
pip install pandas numpy

# 2. Generate dimensions (kalau belum ada)
python generate_dimensions.py

# 3. Generate FACT_KPI
python generate_fact_kpi.py

# 4. Done! Check result/
ls result/
```

---

## 🤝 Kontribusi

Kalau nemu bug atau mau improve, silakan:
1. Fork repo ini
2. Buat branch baru
3. Commit changes
4. Push dan buat Pull Request

Atau langsung buat issue kalau ada masalah! 🐛

---

## 📝 License

Proyek ini dibuat untuk Kementerian Koperasi dan UKM Republik Indonesia.

---

## 🙏 Credits

- **Data Source**: Kementerian Koperasi dan UKM
- **Script**: Python + Pandas
- **Made with**: ❤️ dan ☕

---

## 💡 Tips & Tricks

### 💾 Backup Data
Sebelum regenerate, backup dulu file lama:
```bash
cp result/FACT_KPI.csv result/FACT_KPI_backup.csv
```

### ⚡ Speed Up
Kalau mau test dengan data kecil:
Edit `generate_fact_kpi.py`:
```python
TEST_VILLAGE_LIMIT = 100  # Test dengan 100 desa dulu
```

### 📊 Check Output
Quick check hasil:
```python
import pandas as pd
df = pd.read_csv('result/FACT_KPI.csv')
print(df.head())
print(df.info())
```

---

<div align="center">

**Happy Generating! 🎉📊✨**

*Kalau ada pertanyaan, jangan ragu buat issue atau kontak maintainer!*

</div>

