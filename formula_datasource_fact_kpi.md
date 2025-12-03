# KPI Documentation

This document outlines various Key Performance Indicators (KPIs) related to cooperative data, including their descriptions, categories, logical formulas, SQL implementations, and source data.

---

### KPI_01: Total Koperasi Terdaftar
**Description:** Jumlah seluruh koperasi yang tercatat aktif & non-aktif pada minggu tertentu.
**Category:** Koperasi
**Logical Formula:** `COUNT_DISTINCT(cooperative_id)`
**SQL Formula:** `COUNT(DISTINCT cooperative_id)`
**Source Tables:** `cooperative`
**Source Fields:** `cooperative_id`

---

### KPI_02: Total Koperasi per Provinsi
**Description:** Jumlah koperasi per provinsi.
**Category:** Koperasi
**Logical Formula:** `COUNT_DISTINCT(cooperative_id) GROUP BY province_id`
**SQL Formula:** `COUNT(DISTINCT cooperative_id) GROUP BY provinceId`
**Source Tables:** `cooperative`
**Source Fields:** `cooperative_id, provinceId`

---

### KPI_03: Total Koperasi per Kabupaten/Kota
**Description:** Jumlah koperasi per kabupaten/kota.
**Category:** Koperasi
**Logical Formula:** `COUNT_DISTINCT(cooperative_id) GROUP BY district_id`
**SQL Formula:** `COUNT(DISTINCT cooperative_id) GROUP BY districtId`
**Source Tables:** `cooperative`
**Source Fields:** `cooperative_id, districtId`

---

### KPI_04: Rata-rata Modal Awal Koperasi
**Description:** Rata-rata modal awal koperasi pada minggu berjalan.
**Category:** Keuangan
**Logical Formula:** `[DISESUAIKAN: capital adalah VARCHAR → perlu CAST] AVG(capital)`
**SQL Formula:** `AVG(CAST(capital AS NUMERIC))`
**Source Tables:** `cooperative`
**Source Fields:** `capital`

---

### KPI_05: Total Modal Awal Koperasi
**Description:** Akumulasi modal awal seluruh koperasi.
**Category:** Keuangan
**Logical Formula:** `[DISESUAIKAN: capital adalah VARCHAR → perlu CAST] SUM(capital)`
**SQL Formula:** `SUM(CAST(capital AS NUMERIC))`
**Source Tables:** `cooperative`
**Source Fields:** `capital`

---

### KPI_06: Rasio Koperasi Baru vs Total
**Description:** Persentase koperasi dengan registration_type = 'Baru' terhadap total.
**Category:** Koperasi
**Logical Formula:** `(COUNT(registration_type='Baru')/COUNT(all))*100`
**SQL Formula:** `COUNT(*) FILTER (WHERE registration_type='Pendaftaran Baru')*100.0/COUNT(*)`
**Source Tables:** `cooperative`
**Source Fields:** `registration_type`

---

### KPI_07: Rasio Pendaftaran Mandiri vs Pendamping
**Description:** Persentase koperasi yang didaftarkan secara mandiri vs melalui pendamping.
**Category:** Koperasi
**Logical Formula:** `COUNT(filling_method='Mandiri')/COUNT(all)`
**SQL Formula:** `COUNT(*) FILTER (WHERE filling_method='Mandiri')*1.0/COUNT(*)`
**Source Tables:** `cooperative`
**Source Fields:** `filling_method`

---

### KPI_08: Koperasi per 10.000 Penduduk Desa
**Description:** Kepadatan koperasi per desa berdasarkan jumlah penduduk.
**Category:** Demografi
**Logical Formula:** `[DISESUAIKAN: population = total_u17 + total_a17] COUNT_DISTINCT(cooperative_id)/population*10000`
**SQL Formula:** `(COUNT(DISTINCT c.cooperative_id)*10000.0)/(v.total_u17+v.total_a17)`
**Source Tables:** `cooperative c, villages v`
**Source Fields:** `cooperative_id, villageId, total_u17, total_a17`

---

### KPI_09: Total Anggota Koperasi
**Description:** Jumlah anggota koperasi terdaftar.
**Category:** Keanggotaan
**Logical Formula:** `COUNT_DISTINCT(member_id)`
**SQL Formula:** `COUNT(DISTINCT cooperative_member_id)`
**Source Tables:** `cooperative_members`
**Source Fields:** `cooperative_member_id`

---

### KPI_10: Rasio Gender Anggota (L/P)
**Description:** Proporsi anggota laki-laki vs perempuan.
**Category:** Keanggotaan
**Logical Formula:** `COUNT(L)/COUNT(all), COUNT(P)/COUNT(all)`
**SQL Formula:** `COUNT(*) FILTER (WHERE gender='LAKI-LAKI')/COUNT(*)`
**Source Tables:** `cooperative_members`
**Source Fields:** `gender`

---

### KPI_11: Rata-rata Simpanan Pokok per Anggota
**Description:** Rata-rata nilai simpanan pokok per anggota aktif.
**Category:** Keanggotaan
**Logical Formula:** `SUM(principal_saving)/COUNT(member_id)`
**SQL Formula:** `SUM(principal_saving)*1.0/COUNT(cooperative_member_id)`
**Source Tables:** `cooperative_members`
**Source Fields:** `principal_saving`

---

### KPI_12: Rata-rata Simpanan Wajib per Anggota
**Description:** Rata-rata nilai simpanan wajib per anggota.
**Category:** Keanggotaan
**Logical Formula:** `SUM(mandatory_saving)/COUNT(member_id)`
**SQL Formula:** `SUM(mandatory_saving)*1.0/COUNT(cooperative_member_id)`
**Source Tables:** `cooperative_members`
**Source Fields:** `mandatory_saving`

---

### KPI_13: Rasio Anggota dengan BI Checking Lancar
**Description:** Persentase anggota dengan status BI Checking lancar.
**Category:** Risiko
**Logical Formula:** `COUNT(bi_status='Lancar')/COUNT(all)`
**SQL Formula:** `COUNT(*) FILTER (WHERE bi_checking_verification='Lancar')/COUNT(*)`
**Source Tables:** `cooperative_members`
**Source Fields:** `bi_checking_verification`

---

### KPI_14: Total Pengurus Koperasi
**Description:** Jumlah pengurus (board/management) koperasi.
**Category:** Tata Kelola
**Logical Formula:** `COUNT(role='Pengurus')`
**SQL Formula:** `COUNT(*) FILTER (WHERE status='Pengurus')`
**Source Tables:** `cooperative_management`
**Source Fields:** `status`

---

### KPI_15: Total Pengawas Koperasi
**Description:** Jumlah pengawas koperasi.
**Category:** Tata Kelola
**Logical Formula:** `COUNT(role='Pengawas')`
**SQL Formula:** `COUNT(*) FILTER (WHERE status='Pengawas')`
**Source Tables:** `cooperative_management`
**Source Fields:** `status`

---

### KPI_16: Rasio Gender Pengurus
**Description:** Proporsi pengurus laki-laki vs perempuan.
**Category:** Tata Kelola
**Logical Formula:** `COUNT(role='Pengurus' AND gender='L')/COUNT(role='Pengurus')`
**SQL Formula:** `COUNT(*) FILTER (WHERE status='Pengurus' AND gender='LAKI-LAKI')*1.0/COUNT(*) FILTER (WHERE status='Pengurus')`
**Source Tables:** `cooperative_management`
**Source Fields:** `gender, status`

---

### KPI_17: Struktur Jabatan Lengkap
**Description:** Persentase koperasi yang memiliki minimal Ketua, Sekretaris, Bendahara.
**Category:** Tata Kelola
**Logical Formula:** `COUNT(coop with 3 roles)/COUNT(coop)`
**SQL Formula:** `(Aggregated via HAVING COUNT DISTINCT roles)`
**Source Tables:** `cooperative_management`
**Source Fields:** `role, cooperativeId`

---

### KPI_18: Rata-rata Anggota per Koperasi
**Description:** Rata-rata jumlah anggota per koperasi.
**Category:** Keanggotaan
**Logical Formula:** `COUNT(member_id)/COUNT_DISTINCT(cooperative_id)`
**SQL Formula:** `COUNT(cooperative_member_id)*1.0/COUNT(DISTINCT cooperativeId)`
**Source Tables:** `cooperative_members`
**Source Fields:** `cooperative_member_id`

---

### KPI_19: Total Gerai Koperasi
**Description:** Jumlah seluruh gerai/outlet koperasi.
**Category:** Outlets
**Logical Formula:** `COUNT_DISTINCT(outlet_id)`
**SQL Formula:** `COUNT(DISTINCT cooperative_outlet_id)`
**Source Tables:** `cooperative_outlets`
**Source Fields:** `cooperative_outlet_id`

---

### KPI_20: Gerai per Koperasi
**Description:** Rata-rata jumlah gerai per koperasi.
**Category:** Outlets
**Logical Formula:** `COUNT(outlet_id)/COUNT_DISTINCT(cooperative_id)`
**SQL Formula:** `COUNT(cooperative_outlet_id)*1.0/COUNT(DISTINCT cooperativeId)`
**Source Tables:** `cooperative_outlets`
**Source Fields:** `cooperativeId`

---

### KPI_21: Sebaran Gerai per Provinsi
**Description:** Distribusi jumlah gerai per provinsi.
**Category:** Outlets
**Logical Formula:** `[DISESUAIKAN: perlu join ke cooperative] COUNT(outlet_id) GROUP BY province_id`
**SQL Formula:** `COUNT(o.cooperative_outlet_id) GROUP BY c.provinceId`
**Source Tables:** `outlets + cooperative`
**Source Fields:** `cooperative_outlet_id, provinceId`

---

### KPI_22: Komposisi Tipe Gerai
**Description:** Persentase tipe gerai (simpan pinjam, sembako, LPG, dll.).
**Category:** Outlets
**Logical Formula:** `COUNT(outlet_type)/COUNT(all)`
**SQL Formula:** `COUNT(*) FILTER (WHERE cooperative_type_id=X)/COUNT(*)`
**Source Tables:** `cooperative_outlets`
**Source Fields:** `cooperative_type_id`

---

### KPI_23: Cold Storage Coverage
**Description:** Persentase desa yang memiliki cold-storage.
**Category:** Outlets
**Logical Formula:** `[DISESUAIKAN: join ke desa] COUNT(outlet_type='ColdStorage')/COUNT(village)`
**SQL Formula:** `COUNT(DISTINCT villageId) FILTER (WHERE type ILIKE '%Cold%')`
**Source Tables:** `outlets + geo`
**Source Fields:** `cooperative_type_id, villageId`

---

### KPI_24: Outlet Expansion Rate
**Description:** Pertumbuhan jumlah gerai dibanding minggu sebelumnya.
**Category:** Outlets
**Logical Formula:** `(outlets_week - outlets_prev_week)/outlets_prev_week`
**SQL Formula:** `Based on weekly aggregate COUNT(DISTINCT outlet_id)`
**Source Tables:** `cooperative_outlets`
**Source Fields:** `created_at`

---

### KPI_27: Total KLU Terdaftar
**Description:** Jumlah KLU/KBLI yang digunakan oleh koperasi.
**Category:** KLU
**Logical Formula:** `COUNT_DISTINCT(klu_id)`
**SQL Formula:** `COUNT(DISTINCT kluId)`
**Source Tables:** `cooperative_klus`
**Source Fields:** `kluId`

---

### KPI_28: Top 10 KBLI Terbanyak
**Description:** 10 kode KBLI dengan jumlah koperasi terbanyak.
**Category:** KLU
**Logical Formula:** `TOP_N_BY_COUNT(klu_id, cooperative_id, 10)`
**SQL Formula:** `SELECT kluId, COUNT(DISTINCT cooperativeId) ... LIMIT 10`
**Source Tables:** `cooperative_klus`
**Source Fields:** `kluId, cooperativeId`

---

### KPI_29: Distribusi KLU per Provinsi
**Description:** Penyebaran KLU berdasarkan provinsi.
**Category:** KLU
**Logical Formula:** `COUNT(klu_id) GROUP BY province_id`
**SQL Formula:** `COUNT(*) GROUP BY coop.provinceId`
**Source Tables:** `cooperative_klus + cooperative`
**Source Fields:** `kluId, provinceId`

---

### KPI_30: Proporsi Sektor Utama
**Description:** Persentase koperasi per sektor ekonomi utama.
**Category:** KLU
**Logical Formula:** `COUNT(coop WHERE sector=X)/COUNT(all)`
**SQL Formula:** `Requires dim_klu.sector`
**Source Tables:** `cooperative_klus + dim_klu`
**Source Fields:** `kluId, sector`

---

### KPI_31: Rata-rata KLU per Koperasi
**Description:** Rata-rata jumlah KLU yang dimiliki satu koperasi.
**Category:** KLU
**Logical Formula:** `COUNT(klu_id)/COUNT_DISTINCT(cooperative_id)`
**SQL Formula:** `COUNT(kluId)*1.0/COUNT(DISTINCT cooperativeId)`
**Source Tables:** `cooperative_klus`
**Source Fields:** `kluId`

---

### KPI_32: KLU Diversification Index
**Description:** Indeks diversifikasi usaha koperasi berdasarkan sebaran KLU.
**Category:** KLU
**Logical Formula:** `1 - Σ(p_i^2)`
**SQL Formula:** `1 - SUM(POWER(p_i,2))`
**Source Tables:** `cooperative_klus`
**Source Fields:** `kluId`

---

### KPI_33: Total Aplikasi Kemitraan
**Description:** Jumlah aplikasi kemitraan yang diajukan koperasi.
**Category:** Kemitraan
**Logical Formula:** `COUNT(partnership_id)`
**SQL Formula:** `COUNT(business_partnership_application_id)`
**Source Tables:** `business_partnership_applications`
**Source Fields:** `business_partnership_application_id`

---

### KPI_34: Verified Partnership Rate
**Description:** Persentase aplikasi kemitraan berstatus verified.
**Category:** Kemitraan
**Logical Formula:** `COUNT(status='Verified')/COUNT(all)`
**SQL Formula:** `COUNT(*) FILTER (WHERE status='Verified')/COUNT(*)`
**Source Tables:** `business_partnership_applications`
**Source Fields:** `status`

---

### KPI_35: Rejected Partnership Rate
**Description:** Persentase aplikasi kemitraan yang ditolak.
**Category:** Kemitraan
**Logical Formula:** `COUNT(status='Rejected')/COUNT(all)`
**SQL Formula:** `COUNT(*) FILTER (WHERE status='Rejected')/COUNT(*)`
**Source Tables:** `business_partnership_applications`
**Source Fields:** `status`

---

### KPI_36: In-Progress Partnership Rate
**Description:** Persentase aplikasi kemitraan yang masih dalam proses.
**Category:** Kemitraan
**Logical Formula:** `COUNT(status IN ('Requested','InReview'))/COUNT(all)`
**SQL Formula:** `COUNT(*) FILTER (WHERE status IN ('Requested','InReview'))/COUNT(*)`
**Source Tables:** `business_partnership_applications`
**Source Fields:** `status`

---

### KPI_37: Distribusi Jenis Layanan Kemitraan
**Description:** Komposisi jenis layanan kemitraan (BRILink, LPG, merchant, dll.).
**Category:** Kemitraan
**Logical Formula:** `COUNT(partner_type)/COUNT(all)`
**SQL Formula:** `COUNT(*) FILTER (WHERE partnership_with=X)/COUNT(*)`
**Source Tables:** `business_partnership_applications`
**Source Fields:** `partnership_with`

---

### KPI_38: Partnership Growth Rate
**Description:** Pertumbuhan jumlah kemitraan verified dibanding minggu sebelumnya.
**Category:** Kemitraan
**Logical Formula:** `(verified_week-verified_prev_week)/verified_prev_week`
**SQL Formula:** `Based on weekly aggregates`
**Source Tables:** `business_partnership_applications`
**Source Fields:** `status, created_at`

---

### KPI_40: Kemitraan per Provinsi
**Description:** Jumlah kemitraan aktif per provinsi.
**Category:** Kemitraan
**Logical Formula:** `COUNT(partnership_id) GROUP BY province`
**SQL Formula:** `COUNT(bpa.id) GROUP BY coop.provinceId`
**Source Tables:** `business_partnership_applications + cooperative`
**Source Fields:** `status, provinceId`

---

### KPI_41: Total UPK
