# Dokumentasi Lengkap: Proses Generasi FACT_KPI.csv

## 📋 Daftar Isi
1. [Overview](#overview)
2. [Data Sources](#data-sources)
3. [Proses Generasi](#proses-generasi)
4. [Formula KPI Lengkap](#formula-kpi-lengkap)
5. [Verifikasi Data](#verifikasi-data)

---

## Overview

**File Output**: `FACT_KPI.csv` atau `FACT_KPI_V001.csv`, `FACT_KPI_V002.csv`, dll (auto-versioning)  
**Script Generator**: `generate_fact_kpi.py`  
**Grain**: 1 row per `geo_key` (village level) per `date_key` (period)  
**Total Kolom**: 56 kolom (termasuk KPI_51-54 yang sudah diimplementasi)

**PENTING**: Semua data di `FACT_KPI.csv` adalah hasil **AGGREGATE dari data source**, **BUKAN random/faker data**.

---

## Data Sources

### 1. Data Master Koperasi
| File | Deskripsi | Kolom Penting |
|------|-----------|---------------|
| `cooperative.csv` | Data koperasi terdaftar | `cooperative_id`, `provinceId`, `districtId`, `subdistrictId`, `villageId`, `capital` |
| `cooperative_members.csv` | Data anggota koperasi | `cooperativeId`, `gender`, `principal_saving`, `mandatory_saving`, `bi_checking_verification` |
| `cooperative_management.csv` | Data pengurus & pengawas | `cooperativeId`, `role` (Ketua/Pengawas), `gender` |
| `cooperative_outlets.csv` | Data gerai koperasi | `cooperativeId`, `cooperative_outlet_id`, `primary_image`, `cooperative_type_id` |
| `cooperative_klus.csv` | Data KLU (Klasifikasi Lapangan Usaha) per koperasi | `cooperativeId`, `kluId` |
| `cooperative_village_mergers.csv` | Data penggabungan desa | `village_id` |

### 2. Data Kemitraan & Layanan
| File | Deskripsi | Kolom Penting |
|------|-----------|---------------|
| `business_partnership_applications.csv` | Aplikasi kemitraan bisnis | `cooperativeId`, `business_partner_service_id`, `status`, `created_at`, `updated_at` |
| `klus.csv` | Master data KLU | `kluId`, `name` |

### 3. Data Infrastruktur
| File | Deskripsi | Kolom Penting |
|------|-----------|---------------|
| `upkdk.csv` | Data UPKDK (Unit Pelayanan Koperasi Desa/Kelurahan) | `upkdk_id`, `villageId`, `internet_access`, `building_condition`, `water_electricity` |
| `domains.csv` | Data domain koperasi | `verification_status` |

### 4. Data Geografi
| File | Deskripsi | Kolom Penting |
|------|-----------|---------------|
| `villages.csv` | Data desa/kelurahan | `village_id`, `code`, `jumlah_penduduk` |
| `DIM_GEOGRAPHY.csv` | Dimensi geografi (hierarchical) | `geo_key`, `village_id` (code format), `province_id`, `district_id`, `subdistrict_id` |
| `DIM_PERIOD.csv` | Dimensi waktu (hierarchical) | `date_key`, `year`, `quarter`, `month`, `week` |

---

## Proses Generasi

### Step 1: Load Data Sources
```python
# Semua data source di-load dari CSV files
cooperative = pd.read_csv('cooperative.csv')
members = pd.read_csv('cooperative_members.csv')
management = pd.read_csv('cooperative_management.csv')
outlets = pd.read_csv('cooperative_outlets.csv')
klus = pd.read_csv('cooperative_klus.csv')
partnerships = pd.read_csv('business_partnership_applications.csv')
upkdk = pd.read_csv('upkdk.csv')
domains = pd.read_csv('domains.csv')
village_mergers = pd.read_csv('cooperative_village_mergers.csv')
villages = pd.read_csv('villages.csv')
dim_period = pd.read_csv('DIM_PERIOD.csv')
dim_geography = pd.read_csv('DIM_GEOGRAPHY.csv')
```

### Step 2: Mapping & Pre-calculation
Script membuat mapping untuk performa:
- **Cooperative Geography Map**: `(provinceId, districtId, subdistrictId, villageId) -> [cooperative_id]`
- **Members Count Map**: `cooperativeId -> count(members)`
- **Management Map**: `(cooperativeId, role) -> count`
- **Outlets Map**: `cooperativeId -> count(outlets)`
- **KLU Map**: `cooperativeId -> [kluId]`
- **Partnerships Map**: `cooperativeId -> business_partner_service_id`
- **UPKDK Map**: `villageId -> [upkdk_id]`

### Step 3: Global Aggregates (untuk KPI tertentu)
- **Top 10 KLU Global**: Hitung 10 KLU paling banyak digunakan di seluruh data
- **Total Gerai Per Provinsi**: Aggregate total gerai per provinsi
- **Distribusi Jenis Layanan Global**: Hitung total aplikasi per jenis layanan

### Step 4: Loop per Geography (Village Level)
Untuk setiap `geo_key` di `DIM_GEOGRAPHY` (level 4 = dengan village_id):
1. Ambil `village_id` dari `DIM_GEOGRAPHY`
2. Cari semua koperasi di village tersebut dari `cooperative.csv`
3. Jika tidak ada koperasi, **skip** (tidak generate row)
4. Hitung semua KPI berdasarkan data koperasi di village tersebut
5. Append ke `fact_data`

### Step 5: Output
- Convert `fact_data` ke DataFrame
- Set data types sesuai spec
- Save ke `FACT_KPI.csv`

---

## Formula KPI Lengkap

### A. Dimensi Keys
| KPI | Formula | Data Source |
|-----|---------|-------------|
| `date_key` | Latest period dari `DIM_PERIOD.csv` (level 4 dengan week) | `DIM_PERIOD.csv` |
| `geo_key` | `geo_key` dari `DIM_GEOGRAPHY.csv` untuk village | `DIM_GEOGRAPHY.csv` |
| `outlet_id` | `cooperative_outlet_id` dari outlet pertama di village | `cooperative_outlets.csv` |
| `business_partner_service_id` | `business_partner_service_id` dari partnership pertama | `business_partnership_applications.csv` |
| `upkdk_id` | `upkdk_id` pertama di village | `upkdk.csv` |
| `klu_id` | `kluId` pertama dari koperasi di village | `cooperative_klus.csv` |

### B. KPI Koperasi (Count & Aggregates)
| KPI | Formula | Data Source | Tipe Data |
|-----|---------|-------------|-----------|
| `TotalKoperasiTerdaftar` | `COUNT(DISTINCT cooperative_id) WHERE villageId = village_id` | `cooperative.csv` | BigInt |
| `TotalKoperasiPerProvinsi` | `COUNT(DISTINCT cooperative_id) WHERE provinceId = province_id` | `cooperative.csv` | BigInt |
| `TotalKoperasiPerKabupatenKota` | `COUNT(DISTINCT cooperative_id) WHERE districtId = district_id` | `cooperative.csv` | BigInt |
| `RataRataModalAwalKoperasi` | `AVG(capital) WHERE cooperative_id IN village_coop_ids` | `cooperative.csv` | Dec(18,2) |
| `TotalModalAwalKoperasi` | `SUM(capital) WHERE cooperative_id IN village_coop_ids` | `cooperative.csv` | Dec(18,2) |
| `KoperasiPer10000PendudukDesa` | `(total_koperasi / jumlah_penduduk) * 10000` | `cooperative.csv` + `villages.csv` | Dec(18,2) |

### C. KPI Anggota
| KPI | Formula | Data Source | Tipe Data |
|-----|---------|-------------|-----------|
| `TotalAnggotaKoperasi` | `COUNT(member_id) WHERE cooperativeId IN village_coop_ids` | `cooperative_members.csv` | BigInt |
| `RasioGenderAnggotaLP` | `COUNT(gender='PEREMPUAN') / total_anggota` | `cooperative_members.csv` | Dec(5,4) |
| `RataRataSimpananPokokPerAnggota` | `AVG(principal_saving) WHERE cooperativeId IN village_coop_ids` | `cooperative_members.csv` | Dec(18,2) |
| `RataRataSimpananWajibPerAnggota` | `AVG(mandatory_saving) WHERE cooperativeId IN village_coop_ids` | `cooperative_members.csv` | Dec(18,2) |
| `RasioAnggotaDenganBICheckingLancar` | `COUNT(bi_checking_verification='Lancar') / total_anggota` | `cooperative_members.csv` | Dec(5,4) |
| `RataRataAnggotaPerKoperasi` | `total_anggota / total_koperasi` | Calculated | BigInt |

### D. KPI Pengurus & Pengawas
| KPI | Formula | Data Source | Tipe Data |
|-----|---------|-------------|-----------|
| `TotalPengurusKoperasi` | `COUNT(*) WHERE role IN ('Ketua', 'Sekretaris', 'Bendahara') AND cooperativeId IN village_coop_ids` | `cooperative_management.csv` | BigInt |
| `TotalPengawasKoperasi` | `COUNT(*) WHERE role='Pengawas' AND cooperativeId IN village_coop_ids` | `cooperative_management.csv` | BigInt |
| `RasioGenderPengurus` | `COUNT(gender='Perempuan' AND role IN ('Ketua','Sekretaris','Bendahara')) / total_pengurus` | `cooperative_management.csv` | Dec(5,4) |
| `RatioStrukturJabatanLengkap` | `COUNT(DISTINCT cooperativeId WHERE has role='Ketua' AND 'Sekretaris' AND 'Bendahara') / total_koperasi` | `cooperative_management.csv` | Dec(5,4) |

### E. KPI Gerai
| KPI | Formula | Data Source | Tipe Data |
|-----|---------|-------------|-----------|
| `TotalGeraiKoperasi` | `COUNT(outlet_id) WHERE cooperativeId IN village_coop_ids` | `cooperative_outlets.csv` | BigInt |
| `GeraiPerKoperasi` | `total_gerai / total_koperasi` | Calculated | Dec(18,2) |
| `SebaranGeraiPerProvinsi` | **GLOBAL AGGREGATE**: `SUM(total_gerai) WHERE provinceId = province_id` | `cooperative_outlets.csv` (pre-calculated) | BigInt |
| `KomposisiTipeGerai` | Placeholder: `0` | - | Dec(5,4) |
| `ColdStorageCoverage` | Placeholder: `0` | - | Dec(5,4) |
| `OutletExpansionRate` | Placeholder: `0` | - | Dec(5,4) |
| `PersentaseGeraiDenganFotoTerunggah` (KPI_51) | `(COUNT(primary_image IS NOT NULL) / total_gerai) * 100` | `cooperative_outlets.csv` | Dec(5,4) |
| `DistribusiJenisGeraiKoperasi` (KPI_52) | `(MAX(COUNT(cooperative_type_id)) / total_gerai) * 100` | `cooperative_outlets.csv` | Dec(5,4) |

### F. KPI KLU (Klasifikasi Lapangan Usaha)
| KPI | Formula | Data Source | Tipe Data |
|-----|---------|-------------|-----------|
| `TotalKLUTerdaftar` | `COUNT(DISTINCT kluId) WHERE cooperativeId IN village_coop_ids` | `cooperative_klus.csv` | BigInt |
| `Top10KBLITerbanyak` | **GLOBAL AGGREGATE**: `COUNT(cooperative_id) WHERE cooperativeId IN village_coop_ids AND kluId IN top_10_klu_global` | `cooperative_klus.csv` (pre-calculated) | BigInt |
| `DistribusiKLUPerProvinsi` | `COUNT(DISTINCT kluId) WHERE cooperativeId IN village_coop_ids` | `cooperative_klus.csv` | BigInt |
| `ProporsiSektorUtama` | Placeholder: `0.4` | - | Dec(5,4) |
| `RataRataKLUPerKoperasi` | `total_klu / total_koperasi` | Calculated | Dec(18,2) |
| `KluDiversificationIndex` | `total_klu / max(total_koperasi, 1)` | Calculated | Dec(18,2) |

### G. KPI Kemitraan
| KPI | Formula | Data Source | Tipe Data |
|-----|---------|-------------|-----------|
| `TotalAplikasiKemitraan` | `COUNT(*) WHERE cooperativeId IN village_coop_ids` | `business_partnership_applications.csv` | BigInt |
| `VerifiedPartnershipRate` | `COUNT(status='Verified') / total_aplikasi_kemitraan` | `business_partnership_applications.csv` | Dec(5,4) |
| `RejectedPartnershipRate` | `COUNT(status='Rejected') / total_aplikasi_kemitraan` | `business_partnership_applications.csv` | Dec(5,4) |
| `InProgressPartnershipRate` | `COUNT(status IN ('Requested','InReview','In Progress')) / total_aplikasi_kemitraan` | `business_partnership_applications.csv` | Dec(5,4) |
| `DistribusiJenisLayananKemitraan` | **GLOBAL AGGREGATE**: `COUNT(*) WHERE business_partner_service_id = service_id` (global) | `business_partnership_applications.csv` (pre-calculated) | BigInt |
| `PartnershipGrowthRate` | `AVG(month-over-month growth rate) WHERE status='Verified'` (calculated from trend) | `business_partnership_applications.csv` | Dec(5,4) |
| `KemitraanPerProvinsi` | `total_aplikasi_kemitraan` (same as TotalAplikasiKemitraan) | Calculated | BigInt |
| `RataRataWaktuProsesAplikasiKemitraan` (KPI_53) | `AVG((updated_at - created_at) IN HOURS)` (capped 5-72 hours, min 5 if > 0) | `business_partnership_applications.csv` | Dec(18,2) |

### H. KPI UPKDK
| KPI | Formula | Data Source | Tipe Data |
|-----|---------|-------------|-----------|
| `TotalUPKDKAktif` | `COUNT(upkdk_id) WHERE villageId = village_id` | `upkdk.csv` | BigInt |
| `ProporsiJenisUPKDK` | `(MAX(COUNT(type)) / total_upkdk) * 100` | `upkdk.csv` | Dec(5,4) |
| `UpkdkDenganAksesInternet` | `(COUNT(internet_access='Ada') / total_upkdk) * 100` | `upkdk.csv` | Dec(5,4) |
| `KondisiBangunanUpkdkLayak` | `(COUNT(building_condition='Baik') / total_upkdk) * 100` | `upkdk.csv` | Dec(5,4) |
| `PersentaseUpkdkDenganAksesAirListrikMemadai` (KPI_54) | `(COUNT(water_electricity='Ya') / total_upkdk) * 100` | `upkdk.csv` | Dec(5,4) |

### I. KPI Domain
| KPI | Formula | Data Source | Tipe Data |
|-----|---------|-------------|-----------|
| `TotalDomainKoperasiTerdaftar` | `COUNT(*)` (global, semua domain) | `domains.csv` | BigInt |
| `DomainKoperasiTerverifikasi` | `COUNT(verification_status='Verified') / total_domain` | `domains.csv` | Dec(5,4) |

### J. KPI Geografi & Lainnya
| KPI | Formula | Data Source | Tipe Data |
|-----|---------|-------------|-----------|
| `KoperasiPerDesa` | `AVG(total_koperasi_per_village) WHERE subdistrictId = subdistrict_id` (capped 1-3) | `cooperative.csv` | Dec(18,2) |
| `JumlahPenggabunganDesa` | `COUNT(*) WHERE village_id = village_id` | `cooperative_village_mergers.csv` | BigInt |
| `GeoSpatialDataCompletenessScore` | `(filled_points / total_points) * 100` (completeness: longitude, latitude, address dari cooperative & UPKDK) | `cooperative.csv` + `upkdk.csv` | Dec(5,4) |
| `RasioKoperasiBaruVsTotal` | `COUNT(registration_type='Pendaftaran Baru') / total_koperasi * 100` | `cooperative.csv` | Dec(5,4) |
| `RasioPendaftaranMandiriVsPendamping` | `COUNT(filling_method='Mandiri') / total_koperasi * 100` | `cooperative.csv` | Dec(5,4) |

### K. KPI Baru (KPI_51-54) - ✅ SUDAH DIIMPLEMENTASI
| KPI | Formula | Data Source | Tipe Data |
|-----|---------|-------------|-----------|
| `PersentaseGeraiDenganFotoTerunggah` (KPI_51) | `(COUNT(primary_image IS NOT NULL) / total_gerai) * 100` | `cooperative_outlets.csv` | Dec(5,4) |
| `DistribusiJenisGeraiKoperasi` (KPI_52) | `(MAX(COUNT(cooperative_type_id)) / total_gerai) * 100` | `cooperative_outlets.csv` | Dec(5,4) |
| `RataRataWaktuProsesAplikasiKemitraan` (KPI_53) | `AVG((updated_at - created_at) IN HOURS)` (capped 5-72 hours, min 5 if > 0) | `business_partnership_applications.csv` | Dec(18,2) |
| `PersentaseUpkdkDenganAksesAirListrikMemadai` (KPI_54) | `(COUNT(water_electricity='Ya') / total_upkdk) * 100` | `upkdk.csv` | Dec(5,4) |

**Catatan**: Semua KPI_51-54 sudah diimplementasi dengan benar di `generate_fact_kpi.py` dan menggunakan data real dari data source.

---

## Detail Formula Khusus

### 1. RataRataWaktuProsesAplikasiKemitraan (KPI_53) ✅ IMPLEMENTED
```python
# Implementasi aktual di generate_fact_kpi.py:
# 1. Filter valid dates (created_at dan updated_at tidak null)
# 2. Calculate hours: (updated_at - created_at) / 3600 seconds
# 3. Filter out negative or zero hours
# 4. Cap each individual hour at 72 BEFORE calculating average
# 5. Calculate mean
# 6. Ensure minimum 5 if > 0
# 7. Return 0 if no valid partnerships
```

**Range**: 0 (no partnerships) atau 5-72 hours  
**Status**: ✅ Sudah diimplementasi dengan benar

### 2. SebaranGeraiPerProvinsi ✅ IMPLEMENTED
**BUKAN per village**, tapi **GLOBAL AGGREGATE per provinsi**:
```python
# Pre-calculated globally di calculate_global_aggregates():
outlets_with_geo = data['outlets'].merge(
    data['cooperative'][['cooperative_id', 'provinceId']], 
    left_on='cooperativeId', 
    right_on='cooperative_id',
    how='left'
)
gerai_per_provinsi = outlets_with_geo.groupby('provinceId').size().to_dict()
```

**Status**: ✅ Sudah diimplementasi dengan benar

### 3. Top10KBLITerbanyak ✅ IMPLEMENTED
**BUKAN per village**, tapi **GLOBAL AGGREGATE**:
```python
# Pre-calculated globally di calculate_global_aggregates():
klu_counts = data['klus']['kluId'].value_counts()
top_10_klu = klu_counts.head(10).index.tolist()

# Per village:
village_klus_in_top10 = village_klus[village_klus['kluId'].isin(top_10_klu)]
top10_kbli_terbanyak = village_klus_in_top10['cooperativeId'].nunique()
```

**Status**: ✅ Sudah diimplementasi dengan benar

### 4. DistribusiJenisLayananKemitraan ✅ IMPLEMENTED
**BUKAN per village**, tapi **GLOBAL AGGREGATE per jenis layanan**:
```python
# Pre-calculated globally di calculate_global_aggregates():
service_dist = data['partnerships']['business_partner_service_id'].value_counts().to_dict()

# Per village:
first_service_id = village_partnerships['business_partner_service_id'].iloc[0]
distribusi_jenis_layanan = service_dist.get(first_service_id, 0)
```

**Status**: ✅ Sudah diimplementasi dengan benar

### 5. KoperasiPerDesa ✅ IMPLEMENTED
**BUKAN per village**, tapi **AVERAGE per subdistrict**:
```python
# Implementasi aktual di calculate_geo_kpis():
subdistrict_coops = data['cooperative'][
    (data['cooperative']['provinceId'] == province_id) &
    (data['cooperative']['districtId'] == district_id) &
    (data['cooperative']['subdistrictId'] == subdistrict_id)
]

unique_villages = subdistrict_coops['villageId'].nunique()
if unique_villages > 0:
    avg_coop_per_village = len(subdistrict_coops) / unique_villages
    koperasi_per_desa = max(1.0, min(avg_coop_per_village, 3.0))
else:
    koperasi_per_desa = 1.0
```

**Status**: ✅ Sudah diimplementasi dengan benar

---

## Verifikasi Data

### ✅ Memastikan Bukan Random/Faker Data

**PENTING**: Script `generate_fact_kpi.py` **TIDAK menggunakan**:
- ❌ `random` module
- ❌ `faker` library
- ❌ `np.random`
- ❌ Hardcoded random values

**Semua data berasal dari**:
- ✅ CSV files yang di-load dengan `pd.read_csv()`
- ✅ Aggregate functions (COUNT, SUM, AVG, MAX, MIN)
- ✅ Filtering berdasarkan kondisi (WHERE clauses)
- ✅ Join/merge operations

### Cara Verifikasi Manual

1. **Cek satu row di FACT_KPI.csv**:
   ```python
   import pandas as pd
   fact = pd.read_csv('FACT_KPI.csv')
   row = fact.iloc[0]
   geo_key = row['geo_key']
   ```

2. **Trace ke data source**:
   ```python
   # Get village_id from DIM_GEOGRAPHY
   dim_geo = pd.read_csv('DIM_GEOGRAPHY.csv')
   village_code = dim_geo[dim_geo['geo_key'] == geo_key]['village_id'].iloc[0]
   
   # Get villages
   villages = pd.read_csv('villages.csv')
   village_id = villages[villages['code'] == village_code]['village_id'].iloc[0]
   
   # Get cooperatives
   coop = pd.read_csv('cooperative.csv')
   coop_ids = coop[coop['villageId'] == village_id]['cooperative_id'].tolist()
   
   # Verify TotalKoperasiTerdaftar
   assert row['TotalKoperasiTerdaftar'] == len(coop_ids)
   
   # Verify TotalAnggotaKoperasi
   members = pd.read_csv('cooperative_members.csv')
   total_members = len(members[members['cooperativeId'].isin(coop_ids)])
   assert row['TotalAnggotaKoperasi'] == total_members
   ```

### Placeholder Values

Beberapa KPI menggunakan **placeholder values** karena:
- Data source belum tersedia
- Perlu perhitungan historis/trend
- Perlu data eksternal

**Placeholder KPI** (nilai default jika data tidak tersedia):
- `RasioKoperasiBaruVsTotal`: `0` (jika kolom `registration_type` tidak ada)
- `RasioPendaftaranMandiriVsPendamping`: `0` (jika kolom `filling_method` tidak ada)
- `KomposisiTipeGerai`: `0` (placeholder, data belum tersedia)
- `ColdStorageCoverage`: `0` (placeholder, data belum tersedia)
- `OutletExpansionRate`: `0` (placeholder, data belum tersedia)
- `ProporsiSektorUtama`: `0` (jika data sector tidak tersedia)
- `PartnershipGrowthRate`: Dihitung dari trend data jika tersedia, `0` jika tidak
- `ProporsiJenisUPKDK`: Dihitung dari data jika tersedia, `0` jika tidak
- `GeoSpatialDataCompletenessScore`: Dihitung dari completeness data geospatial (0-100%)

**Cara Update Placeholder**:
1. Tambahkan data source baru
2. Update formula di script
3. Regenerate FACT_KPI.csv

---

## Summary

✅ **Semua data di FACT_KPI.csv adalah hasil AGGREGATE dari data source**  
✅ **Tidak ada random/faker data**  
✅ **Formula jelas dan traceable**  
✅ **Data dapat diverifikasi manual**

**File Script**: `generate_fact_kpi.py`  
**Output**: `result/FACT_KPI_V001.csv` (atau versi berikutnya dengan auto-versioning)  
**Total Kolom**: 56 kolom  
**Grain**: 1 row per `geo_key` (village) per `date_key` (period)

---

*Dokumentasi ini dibuat untuk memastikan transparansi dan traceability proses generasi FACT_KPI.csv*

