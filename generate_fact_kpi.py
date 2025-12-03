"""
FACT_KPI Generation Script
===========================
Generates FACT_KPI.csv from data sources with real-time progress logging.

Author: Generated Script
Date: 2024-12-02
"""

import pandas as pd
import numpy as np
import os
import glob
import time
from datetime import datetime
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_SOURCE_DIR = "data_source"
RESULT_DIR = "result"
TEST_VILLAGE_LIMIT = None  # Limit for testing, set to None for full run (will generate ~38,053 rows)
OUTPUT_FILE_PREFIX = "FACT_KPI_V"

# ============================================================================
# PROGRESS LOGGING UTILITIES
# ============================================================================

class ProgressLogger:
    """Handles real-time progress logging with timestamps and formatting."""
    
    def __init__(self):
        self.start_time = time.time()
        self.step_times = {}
    
    def log(self, category, message, status=""):
        """Log a message with category and optional status."""
        elapsed = time.time() - self.start_time
        status_symbol = {
            "success": "✓",
            "error": "✗",
            "progress": "→",
            "info": "ℹ"
        }.get(status, "")
        
        print(f"[{category:12s}] {message} {status_symbol}")
    
    def log_file_load(self, filename, size_mb, row_count):
        """Log file loading with size and row count."""
        self.log("LOADING", f"{filename:40s} {size_mb:6.1f} MB, {row_count:,} rows", "success")
    
    def log_mapping(self, name, count):
        """Log mapping creation."""
        self.log("MAPPING", f"{name:50s} {count:,} entries", "success")
    
    def log_global(self, name, value):
        """Log global calculation."""
        self.log("GLOBAL", f"{name:50s} {value}", "success")
    
    def log_progress(self, current, total, extra_info=""):
        """Log processing progress with percentage and ETA."""
        pct = (current / total * 100) if total > 0 else 0
        elapsed = time.time() - self.start_time
        
        if current > 0:
            eta_seconds = (elapsed / current) * (total - current)
            eta_min = int(eta_seconds // 60)
            eta_sec = int(eta_seconds % 60)
            eta_str = f"ETA: {eta_min}m {eta_sec:02d}s"
        else:
            eta_str = "ETA: calculating..."
        
        self.log("PROCESSING", 
                f"Village {current:,}/{total:,} ({pct:5.1f}%) {extra_info} - {eta_str}", 
                "progress")
    
    def log_complete(self, message):
        """Log completion message."""
        elapsed = time.time() - self.start_time
        elapsed_min = int(elapsed // 60)
        elapsed_sec = int(elapsed % 60)
        self.log("COMPLETE", f"{message} (Time: {elapsed_min}m {elapsed_sec:02d}s)", "success")
    
    def log_error(self, message):
        """Log error message."""
        self.log("ERROR", message, "error")

logger = ProgressLogger()

# ============================================================================
# FILE UTILITIES
# ============================================================================

def get_next_version_number():
    """Get the next version number for FACT_KPI file."""
    pattern = os.path.join(RESULT_DIR, f"{OUTPUT_FILE_PREFIX}*.csv")
    existing_files = glob.glob(pattern)
    
    if not existing_files:
        return 1
    
    versions = []
    for filepath in existing_files:
        filename = os.path.basename(filepath)
        # Extract version number from filename like "FACT_KPI_V001.csv"
        try:
            version_str = filename.replace(OUTPUT_FILE_PREFIX, "").replace(".csv", "")
            version_num = int(version_str)
            versions.append(version_num)
        except ValueError:
            continue
    
    return max(versions) + 1 if versions else 1

def get_file_size_mb(filepath):
    """Get file size in MB."""
    return os.path.getsize(filepath) / (1024 * 1024)

# ============================================================================
# DATA LOADING
# ============================================================================

def load_all_data():
    """Load all required data sources and dimension tables."""
    logger.log("INIT", "Starting data loading phase...")
    
    data = {}
    
    # Define required files
    required_files = {
        'cooperative': 'cooperative.csv',
        'members': 'cooperative_members.csv',
        'management': 'cooperative_management.csv',
        'outlets': 'cooperative_outlets.csv',
        'klus': 'cooperative_klus.csv',
        'partnerships': 'business_partnership_applications.csv',
        'upkdk': 'upkdk.csv',
        'domains': 'domains.csv',
        'village_mergers': 'cooperative_village_mergers.csv',
        'villages': 'villages.csv',
        'districts': 'districts.csv',
        'subdistricts': 'subdistricts.csv',
        'dim_klu': 'dim_klu.csv',
        'dim_geography': os.path.join(RESULT_DIR, 'DIM_GEOGRAPHY.csv'),
        'dim_period': os.path.join(RESULT_DIR, 'DIM_PERIOD.csv'),
    }
    
    # Load each file
    for key, filename in required_files.items():
        if key in ['dim_geography', 'dim_period']:
            filepath = filename
        else:
            filepath = os.path.join(DATA_SOURCE_DIR, filename)
        
        try:
            df = pd.read_csv(filepath, low_memory=False)
            # Clean column names (strip whitespace and newlines)
            df.columns = df.columns.str.strip().str.replace('\n', '').str.replace('\r', '')
            size_mb = get_file_size_mb(filepath)
            logger.log_file_load(os.path.basename(filepath), size_mb, len(df))
            data[key] = df
        except FileNotFoundError:
            logger.log_error(f"File not found: {filepath}")
            raise
        except Exception as e:
            logger.log_error(f"Error loading {filepath}: {str(e)}")
            raise
    
    logger.log("INIT", f"Loaded {len(data)} data sources successfully", "success")
    return data

# ============================================================================
# PRE-CALCULATION & MAPPING
# ============================================================================

def create_mappings(data):
    """Create lookup dictionaries for fast access."""
    logger.log("INIT", "Creating lookup mappings...")
    
    mappings = {}
    
    # 1. Cooperative Geography Map
    coop_geo_map = {}
    for _, row in data['cooperative'].iterrows():
        key = (row.get('provinceId'), row.get('districtId'), 
               row.get('subdistrictId'), row.get('villageId'))
        if key not in coop_geo_map:
            coop_geo_map[key] = []
        coop_geo_map[key].append(row['cooperative_id'])
    
    mappings['coop_geo'] = coop_geo_map
    logger.log_mapping("Cooperative geography map", len(coop_geo_map))
    
    # 2. Members by Cooperative
    members_by_coop = data['members'].groupby('cooperativeId').size().to_dict()
    mappings['members_count'] = members_by_coop
    logger.log_mapping("Members count map", len(members_by_coop))
    
    # 3. Management by Cooperative
    mappings['management'] = data['management']
    logger.log_mapping("Management data", len(data['management']))
    
    # 4. Outlets by Cooperative
    outlets_by_coop = data['outlets'].groupby('cooperativeId').size().to_dict()
    mappings['outlets_count'] = outlets_by_coop
    logger.log_mapping("Outlets count map", len(outlets_by_coop))
    
    # 5. KLUs by Cooperative
    klu_by_coop = data['klus'].groupby('cooperativeId')['kluId'].apply(list).to_dict()
    mappings['klu_by_coop'] = klu_by_coop
    logger.log_mapping("KLU by cooperative map", len(klu_by_coop))
    
    # 6. Partnerships by Cooperative
    mappings['partnerships'] = data['partnerships']
    logger.log_mapping("Partnerships data", len(data['partnerships']))
    
    # 7. UPKDK by Village
    upkdk_by_village = data['upkdk'].groupby('villageId')['upkdk_id'].apply(list).to_dict()
    mappings['upkdk_by_village'] = upkdk_by_village
    logger.log_mapping("UPKDK by village map", len(upkdk_by_village))
    
    return mappings

def calculate_global_aggregates(data, mappings):
    """Calculate global aggregates needed for certain KPIs."""
    logger.log("INIT", "Calculating global aggregates...")
    
    global_agg = {}
    
    # 1. Top 10 KLU
    klu_counts = data['klus']['kluId'].value_counts()
    top_10_klu = klu_counts.head(10).index.tolist()
    global_agg['top_10_klu'] = top_10_klu
    logger.log_global("Top 10 KLU", f"Found {len(klu_counts)} unique KLUs")
    
    # 2. Total Gerai per Provinsi
    # Join outlets with cooperative to get province
    outlets_with_geo = data['outlets'].merge(
        data['cooperative'][['cooperative_id', 'provinceId']], 
        left_on='cooperativeId', 
        right_on='cooperative_id',
        how='left'
    )
    gerai_per_provinsi = outlets_with_geo.groupby('provinceId').size().to_dict()
    global_agg['gerai_per_provinsi'] = gerai_per_provinsi
    logger.log_global("Gerai per provinsi", f"{len(gerai_per_provinsi)} provinces")
    
    # 3. Distribusi Jenis Layanan Kemitraan
    service_dist = data['partnerships']['business_partner_service_id'].value_counts().to_dict()
    global_agg['service_distribution'] = service_dist
    logger.log_global("Service distribution", f"{len(service_dist)} service types")
    
    # 4. Total Domains (global)
    global_agg['total_domains'] = len(data['domains'])
    global_agg['verified_domains'] = len(data['domains'][data['domains']['verification_status'] == 'Verified'])
    logger.log_global("Total domains", f"{global_agg['total_domains']:,}")
    
    return global_agg

# ============================================================================
# KPI CALCULATION FUNCTIONS
# ============================================================================

def safe_divide(numerator, denominator, default=0):
    """Safely divide two numbers, return default if denominator is 0."""
    if denominator == 0 or pd.isna(denominator):
        return default
    return numerator / denominator

def safe_percentage(numerator, denominator, default=0):
    """Calculate percentage (0-100 range), return default if denominator is 0."""
    if denominator == 0 or pd.isna(denominator):
        return default
    return (numerator / denominator) * 100

def calculate_cooperative_kpis(village_coop_ids, data, province_id, district_code, district_id_internal):
    """Calculate cooperative-related KPIs (KPI_01 to KPI_06, KPI_08)."""
    kpis = {}
    
    # KPI_01: Total Koperasi Terdaftar (village level)
    kpis['TotalKoperasiTerdaftar'] = len(village_coop_ids)
    
    # KPI_02: Total Koperasi per Provinsi
    province_coops = data['cooperative'][data['cooperative']['provinceId'] == province_id]
    kpis['TotalKoperasiPerProvinsi'] = len(province_coops)
    
    # KPI_03: Total Koperasi per Kabupaten/Kota
    # Use internal district_id (integer) from cooperative table
    if district_id_internal is not None:
        district_coops = data['cooperative'][data['cooperative']['districtId'] == district_id_internal]
        kpis['TotalKoperasiPerKabupatenKota'] = len(district_coops)
    else:
        kpis['TotalKoperasiPerKabupatenKota'] = 0
    
    # KPI_04 & KPI_05: Modal Awal
    if len(village_coop_ids) > 0:
        village_coops = data['cooperative'][data['cooperative']['cooperative_id'].isin(village_coop_ids)]
        # Convert capital to numeric, handling errors
        capital_values = pd.to_numeric(village_coops['capital'], errors='coerce').fillna(0)
        kpis['RataRataModalAwalKoperasi'] = float(capital_values.mean() if len(capital_values) > 0 else 0)
        kpis['TotalModalAwalKoperasi'] = float(capital_values.sum())
    else:
        kpis['RataRataModalAwalKoperasi'] = 0.0
        kpis['TotalModalAwalKoperasi'] = 0.0
    
    # KPI_06: Rasio Koperasi Baru vs Total
    if len(village_coop_ids) > 0:
        village_coops = data['cooperative'][data['cooperative']['cooperative_id'].isin(village_coop_ids)]
        if 'registration_type' in village_coops.columns:
            baru_count = len(village_coops[village_coops['registration_type'] == 'Pendaftaran Baru'])
            kpis['RasioKoperasiBaruVsTotal'] = safe_percentage(baru_count, len(village_coops))
        else:
            kpis['RasioKoperasiBaruVsTotal'] = 0.0
    else:
        kpis['RasioKoperasiBaruVsTotal'] = 0.0
    
    # KPI_07: Rasio Pendaftaran Mandiri vs Pendamping
    if len(village_coop_ids) > 0:
        village_coops = data['cooperative'][data['cooperative']['cooperative_id'].isin(village_coop_ids)]
        if 'filling_method' in village_coops.columns:
            mandiri_count = len(village_coops[village_coops['filling_method'] == 'Mandiri'])
            kpis['RasioPendaftaranMandiriVsPendamping'] = safe_percentage(mandiri_count, len(village_coops))
        else:
            kpis['RasioPendaftaranMandiriVsPendamping'] = 0.0
    else:
        kpis['RasioPendaftaranMandiriVsPendamping'] = 0.0
    
    return kpis

def calculate_member_kpis(village_coop_ids, data):
    """Calculate member-related KPIs (KPI_09 to KPI_13, KPI_18)."""
    kpis = {}
    
    # Filter members for this village's cooperatives
    village_members = data['members'][data['members']['cooperativeId'].isin(village_coop_ids)]
    
    # KPI_09: Total Anggota Koperasi
    kpis['TotalAnggotaKoperasi'] = len(village_members)
    
    if len(village_members) > 0:
        # KPI_10: Rasio Gender Anggota (Perempuan percentage)
        if 'gender' in village_members.columns:
            perempuan_count = len(village_members[village_members['gender'] == 'PEREMPUAN'])
            kpis['RasioGenderAnggotaLP'] = safe_percentage(perempuan_count, len(village_members))
        else:
            kpis['RasioGenderAnggotaLP'] = 0
        
        # KPI_11: Rata-rata Simpanan Pokok per Anggota
        principal_saving = pd.to_numeric(village_members['principal_saving'], errors='coerce').fillna(0)
        kpis['RataRataSimpananPokokPerAnggota'] = principal_saving.mean()
        
        # KPI_12: Rata-rata Simpanan Wajib per Anggota
        mandatory_saving = pd.to_numeric(village_members['mandatory_saving'], errors='coerce').fillna(0)
        kpis['RataRataSimpananWajibPerAnggota'] = mandatory_saving.mean()
        
        # KPI_13: Rasio Anggota dengan BI Checking Lancar
        if 'bi_checking_verification' in village_members.columns:
            lancar_count = len(village_members[village_members['bi_checking_verification'] == 'Lancar'])
            kpis['RasioAnggotaDenganBICheckingLancar'] = safe_percentage(lancar_count, len(village_members))
        else:
            kpis['RasioAnggotaDenganBICheckingLancar'] = 0
    else:
        kpis['RasioGenderAnggotaLP'] = 0
        kpis['RataRataSimpananPokokPerAnggota'] = 0
        kpis['RataRataSimpananWajibPerAnggota'] = 0
        kpis['RasioAnggotaDenganBICheckingLancar'] = 0
    
    # KPI_18: Rata-rata Anggota per Koperasi
    total_coops = len(village_coop_ids)
    kpis['RataRataAnggotaPerKoperasi'] = len(village_members) // total_coops if total_coops > 0 else 0
    
    return kpis

def calculate_management_kpis(village_coop_ids, data):
    """Calculate management-related KPIs (KPI_14 to KPI_17)."""
    kpis = {}
    
    # Filter management for this village's cooperatives
    village_mgmt = data['management'][data['management']['cooperativeId'].isin(village_coop_ids)]
    
    # KPI_14: Total Pengurus (role='Pengurus' OR position in specific roles)
    # Note: Based on data, 'role' column has the values, NOT 'status'
    # Pengurus includes: Ketua, Sekretaris, Bendahara
    pengurus_roles = ['Ketua', 'Sekretaris', 'Bendahara']
    
    if 'role' in village_mgmt.columns:
        pengurus = village_mgmt[village_mgmt['role'].isin(pengurus_roles)]
        kpis['TotalPengurusKoperasi'] = len(pengurus)
    else:
        pengurus = village_mgmt[village_mgmt['position'].isin(pengurus_roles)] if 'position' in village_mgmt.columns else pd.DataFrame()
        kpis['TotalPengurusKoperasi'] = len(pengurus)
    
    # KPI_15: Total Pengawas (role='Pengawas')
    if 'role' in village_mgmt.columns:
        pengawas = village_mgmt[village_mgmt['role'] == 'Pengawas']
        kpis['TotalPengawasKoperasi'] = len(pengawas)
    else:
        pengawas = village_mgmt[village_mgmt['position'] == 'Pengawas'] if 'position' in village_mgmt.columns else pd.DataFrame()
        kpis['TotalPengawasKoperasi'] = len(pengawas)
    
    # KPI_16: Rasio Gender Pengurus (Perempuan percentage)
    if len(pengurus) > 0 and 'gender' in pengurus.columns:
        female_pengurus = len(pengurus[pengurus['gender'] == 'Perempuan'])
        kpis['RasioGenderPengurus'] = safe_percentage(female_pengurus, len(pengurus))
    else:
        kpis['RasioGenderPengurus'] = 0
    
    # KPI_17: Ratio Struktur Jabatan Lengkap
    # Check if each cooperative has Ketua, Sekretaris, Bendahara
    if len(village_coop_ids) > 0 and len(village_mgmt) > 0:
        complete_structure_count = 0
        for coop_id in village_coop_ids:
            coop_mgmt = village_mgmt[village_mgmt['cooperativeId'] == coop_id]
            if 'role' in coop_mgmt.columns:
                roles = coop_mgmt['role'].unique()
            elif 'position' in coop_mgmt.columns:
                roles = coop_mgmt['position'].unique()
            else:
                roles = []
            
            # Check if has Ketua, Sekretaris, Bendahara
            has_ketua = 'Ketua' in roles
            has_sekretaris = 'Sekretaris' in roles
            has_bendahara = 'Bendahara' in roles
            
            if has_ketua and has_sekretaris and has_bendahara:
                complete_structure_count += 1
        
        kpis['RatioStrukturJabatanLengkap'] = safe_percentage(complete_structure_count, len(village_coop_ids))
    else:
        kpis['RatioStrukturJabatanLengkap'] = 0
    
    return kpis

def calculate_outlet_kpis(village_coop_ids, data, global_agg, province_id):
    """Calculate outlet-related KPIs (KPI_19 to KPI_24, KPI_51, KPI_52)."""
    kpis = {}
    
    # Filter outlets for this village's cooperatives
    village_outlets = data['outlets'][data['outlets']['cooperativeId'].isin(village_coop_ids)]
    
    # KPI_19: Total Gerai Koperasi
    kpis['TotalGeraiKoperasi'] = len(village_outlets)
    
    # KPI_20: Gerai per Koperasi
    total_coops = len(village_coop_ids)
    kpis['GeraiPerKoperasi'] = safe_divide(len(village_outlets), total_coops)
    
    # KPI_21: Sebaran Gerai per Provinsi (global aggregate)
    kpis['SebaranGeraiPerProvinsi'] = global_agg['gerai_per_provinsi'].get(province_id, 0)
    
    # KPI_22-24: Set to 0 (no data)
    kpis['KomposisiTipeGerai'] = 0
    kpis['ColdStorageCoverage'] = 0
    kpis['OutletExpansionRate'] = 0
    
    # KPI_51: Persentase Gerai dengan Foto Terunggah
    if len(village_outlets) > 0:
        with_photo = len(village_outlets[village_outlets['primary_image'].notna()])
        kpis['PersentaseGeraiDenganFotoTerunggah'] = safe_percentage(with_photo, len(village_outlets))
        
        # KPI_52: Distribusi Jenis Gerai Koperasi (ratio of most common type)
        if 'cooperative_type_id' in village_outlets.columns:
            type_counts = village_outlets['cooperative_type_id'].value_counts()
            if len(type_counts) > 0:
                max_type_count = type_counts.iloc[0]
                kpis['DistribusiJenisGeraiKoperasi'] = safe_percentage(max_type_count, len(village_outlets))
            else:
                kpis['DistribusiJenisGeraiKoperasi'] = 0
        else:
            kpis['DistribusiJenisGeraiKoperasi'] = 0
    else:
        kpis['PersentaseGeraiDenganFotoTerunggah'] = 0
        kpis['DistribusiJenisGeraiKoperasi'] = 0
    
    return kpis

def calculate_klu_kpis(village_coop_ids, data, global_agg):
    """Calculate KLU-related KPIs (KPI_27 to KPI_32)."""
    kpis = {}
    
    # Filter KLUs for this village's cooperatives
    village_klus = data['klus'][data['klus']['cooperativeId'].isin(village_coop_ids)]
    
    # KPI_27: Total KLU Terdaftar
    unique_klus = village_klus['kluId'].nunique()
    kpis['TotalKLUTerdaftar'] = unique_klus
    
    # KPI_28: Top 10 KBLI Terbanyak (count of coops in this village using top 10 KLUs)
    top_10_klu = global_agg['top_10_klu']
    village_klus_in_top10 = village_klus[village_klus['kluId'].isin(top_10_klu)]
    kpis['Top10KBLITerbanyak'] = village_klus_in_top10['cooperativeId'].nunique()
    
    # KPI_29: Distribusi KLU per Provinsi (same as total KLU for village)
    kpis['DistribusiKLUPerProvinsi'] = unique_klus
    
    # KPI_30: Proporsi Sektor Utama
    if len(village_klus) > 0 and 'dim_klu' in data:
        # Merge with dim_klu to get sectors
        village_klus_with_sector = village_klus.merge(
            data['dim_klu'][['kluId', 'sector']], 
            on='kluId', 
            how='left'
        )
        if 'sector' in village_klus_with_sector.columns:
            sector_counts = village_klus_with_sector['sector'].value_counts()
            if len(sector_counts) > 0:
                # Get proportion of most common sector
                most_common_sector_count = sector_counts.iloc[0]
                kpis['ProporsiSektorUtama'] = safe_percentage(most_common_sector_count, len(village_klus))
            else:
                kpis['ProporsiSektorUtama'] = 0
        else:
            kpis['ProporsiSektorUtama'] = 0
    else:
        kpis['ProporsiSektorUtama'] = 0
    
    # KPI_31: Rata-rata KLU per Koperasi
    total_coops = len(village_coop_ids)
    kpis['RataRataKLUPerKoperasi'] = safe_divide(len(village_klus), total_coops)
    
    # KPI_32: KLU Diversification Index
    kpis['KluDiversificationIndex'] = safe_divide(unique_klus, max(total_coops, 1))
    
    return kpis

def calculate_partnership_kpis(village_coop_ids, data, global_agg):
    """Calculate partnership-related KPIs (KPI_33 to KPI_40, KPI_53)."""
    kpis = {}
    
    # Filter partnerships for this village's cooperatives
    village_partnerships = data['partnerships'][data['partnerships']['cooperativeId'].isin(village_coop_ids)]
    
    # KPI_33: Total Aplikasi Kemitraan
    total_partnerships = len(village_partnerships)
    kpis['TotalAplikasiKemitraan'] = total_partnerships
    
    if total_partnerships > 0:
        # KPI_34: Verified Partnership Rate
        verified = len(village_partnerships[village_partnerships['status'] == 'Verified'])
        kpis['VerifiedPartnershipRate'] = safe_percentage(verified, total_partnerships)
        
        # KPI_35: Rejected Partnership Rate
        rejected = len(village_partnerships[village_partnerships['status'] == 'Rejected'])
        kpis['RejectedPartnershipRate'] = safe_percentage(rejected, total_partnerships)
        
        # KPI_36: In-Progress Partnership Rate
        in_progress = len(village_partnerships[village_partnerships['status'].isin(['Requested', 'InReview', 'In Progress'])])
        kpis['InProgressPartnershipRate'] = safe_percentage(in_progress, total_partnerships)
        
        # KPI_53: Rata-rata Waktu Proses Aplikasi Kemitraan (in hours)
        if 'created_at' in village_partnerships.columns and 'updated_at' in village_partnerships.columns:
            try:
                created = pd.to_datetime(village_partnerships['created_at'], errors='coerce')
                updated = pd.to_datetime(village_partnerships['updated_at'], errors='coerce')
                
                # Calculate hours difference
                time_diff = (updated - created).dt.total_seconds() / 3600
                
                # Filter valid values (positive, non-null)
                valid_times = time_diff[(time_diff > 0) & (time_diff.notna())]
                
                if len(valid_times) > 0:
                    # Cap at 72 hours before averaging
                    capped_times = valid_times.clip(upper=72)
                    avg_time = capped_times.mean()
                    # Ensure minimum 5 if > 0
                    kpis['RataRataWaktuProsesAplikasiKemitraan'] = max(avg_time, 5) if avg_time > 0 else 0
                else:
                    kpis['RataRataWaktuProsesAplikasiKemitraan'] = 0
            except:
                kpis['RataRataWaktuProsesAplikasiKemitraan'] = 0
        else:
            kpis['RataRataWaktuProsesAplikasiKemitraan'] = 0
    else:
        kpis['VerifiedPartnershipRate'] = 0
        kpis['RejectedPartnershipRate'] = 0
        kpis['InProgressPartnershipRate'] = 0
        kpis['RataRataWaktuProsesAplikasiKemitraan'] = 0
    
    # KPI_37: Distribusi Jenis Layanan Kemitraan (global aggregate)
    if total_partnerships > 0 and len(village_partnerships) > 0:
        # Get first service_id from village partnerships
        first_service_id = village_partnerships['business_partner_service_id'].iloc[0]
        kpis['DistribusiJenisLayananKemitraan'] = global_agg['service_distribution'].get(first_service_id, 0)
    else:
        kpis['DistribusiJenisLayananKemitraan'] = 0
    
    # KPI_38: Partnership Growth Rate (calculated from trend data)
    # Calculate average monthly growth rate from created_at timestamps
    if 'created_at' in data['partnerships'].columns and len(data['partnerships']) > 0:
        try:
            # Convert to datetime
            partnerships_with_date = data['partnerships'].copy()
            partnerships_with_date['created_month'] = pd.to_datetime(
                partnerships_with_date['created_at'], 
                errors='coerce'
            ).dt.to_period('M')
            
            # Filter verified partnerships only
            verified_partnerships = partnerships_with_date[
                partnerships_with_date['status'] == 'Verified'
            ]
            
            if len(verified_partnerships) > 0:
                # Count by month
                monthly_counts = verified_partnerships.groupby('created_month').size()
                
                if len(monthly_counts) >= 2:
                    # Calculate month-over-month growth rates
                    growth_rates = []
                    for i in range(1, len(monthly_counts)):
                        prev_month = monthly_counts.iloc[i-1]
                        curr_month = monthly_counts.iloc[i]
                        if prev_month > 0:
                            growth_rate = ((curr_month - prev_month) / prev_month) * 100
                            growth_rates.append(growth_rate)
                    
                    if len(growth_rates) > 0:
                        # Average growth rate, capped at 0-100
                        avg_growth = np.mean(growth_rates)
                        kpis['PartnershipGrowthRate'] = max(0, min(avg_growth, 100))
                    else:
                        kpis['PartnershipGrowthRate'] = 0
                else:
                    kpis['PartnershipGrowthRate'] = 0
            else:
                kpis['PartnershipGrowthRate'] = 0
        except:
            kpis['PartnershipGrowthRate'] = 0
    else:
        kpis['PartnershipGrowthRate'] = 0
    
    # KPI_40: Kemitraan per Provinsi (same as total for village)
    kpis['KemitraanPerProvinsi'] = total_partnerships
    
    return kpis

def calculate_upkdk_kpis(village_id, data):
    """Calculate UPKDK-related KPIs (KPI_41 to KPI_44, KPI_54)."""
    kpis = {}
    
    # Filter UPKDK for this village
    village_upkdk = data['upkdk'][data['upkdk']['villageId'] == village_id]
    
    # KPI_41: Total UPKDK Aktif
    total_upkdk = len(village_upkdk)
    kpis['TotalUPKDKAktif'] = total_upkdk
    
    if total_upkdk > 0:
        # KPI_42: Proporsi Jenis UPKDK
        if 'type' in village_upkdk.columns:
            # Calculate proportion of most common type
            type_counts = village_upkdk['type'].value_counts()
            if len(type_counts) > 0:
                max_type_count = type_counts.iloc[0]
                kpis['ProporsiJenisUPKDK'] = safe_percentage(max_type_count, total_upkdk)
            else:
                kpis['ProporsiJenisUPKDK'] = 0.0
        else:
            kpis['ProporsiJenisUPKDK'] = 0.0
        
        # KPI_43: UPKDK dengan Akses Internet (percentage 0-100)
        if 'internet_access' in village_upkdk.columns:
            with_internet = len(village_upkdk[village_upkdk['internet_access'] == 'Ada'])
            kpis['UpkdkDenganAksesInternet'] = safe_percentage(with_internet, total_upkdk)
        else:
            kpis['UpkdkDenganAksesInternet'] = 0
        
        # KPI_44: Kondisi Bangunan UPKDK Layak (percentage 0-100)
        if 'building_condition' in village_upkdk.columns:
            good_condition = len(village_upkdk[village_upkdk['building_condition'] == 'Baik'])
            kpis['KondisiBangunanUpkdkLayak'] = safe_percentage(good_condition, total_upkdk)
        else:
            kpis['KondisiBangunanUpkdkLayak'] = 0
        
        # KPI_54: Persentase UPKDK dengan Akses Air Listrik Memadai (percentage 0-100)
        if 'water_electricity' in village_upkdk.columns:
            adequate = len(village_upkdk[village_upkdk['water_electricity'] == 'Ya'])
            kpis['PersentaseUpkdkDenganAksesAirListrikMemadai'] = safe_percentage(adequate, total_upkdk)
        else:
            kpis['PersentaseUpkdkDenganAksesAirListrikMemadai'] = 0
    else:
        kpis['ProporsiJenisUPKDK'] = 0
        kpis['UpkdkDenganAksesInternet'] = 0
        kpis['KondisiBangunanUpkdkLayak'] = 0
        kpis['PersentaseUpkdkDenganAksesAirListrikMemadai'] = 0
    
    return kpis

def calculate_domain_kpis(global_agg):
    """Calculate domain-related KPIs (KPI_45 to KPI_46)."""
    kpis = {}
    
    # KPI_45: Total Domain Koperasi Terdaftar (global)
    kpis['TotalDomainKoperasiTerdaftar'] = global_agg['total_domains']
    
    # KPI_46: Domain Koperasi Terverifikasi (percentage 0-100)
    if global_agg['total_domains'] > 0:
        kpis['DomainKoperasiTerverifikasi'] = safe_percentage(
            global_agg['verified_domains'], 
            global_agg['total_domains']
        )
    else:
        kpis['DomainKoperasiTerverifikasi'] = 0
    
    return kpis

def calculate_geo_kpis(village_id, data, province_id, district_id, subdistrict_id):
    """Calculate geography-related KPIs (KPI_08, KPI_47 to KPI_50)."""
    kpis = {}
    
    # KPI_08: Koperasi per 10,000 Penduduk Desa
    village_info = data['villages'][data['villages']['village_id'] == village_id]
    if len(village_info) > 0:
        village_row = village_info.iloc[0]
        # Calculate total population
        total_u17 = pd.to_numeric(village_row.get('total_u17', 0), errors='coerce') or 0
        total_a17 = pd.to_numeric(village_row.get('total_a17', 0), errors='coerce') or 0
        population = total_u17 + total_a17
        
        if population > 0:
            # Count cooperatives in this village
            village_coops = data['cooperative'][data['cooperative']['villageId'] == village_id]
            coop_count = len(village_coops)
            kpis['KoperasiPer10000PendudukDesa'] = (coop_count / population) * 10000
        else:
            kpis['KoperasiPer10000PendudukDesa'] = 0
    else:
        kpis['KoperasiPer10000PendudukDesa'] = 0
    
    # KPI_47: Koperasi per Desa (average in subdistrict, capped 1-3)
    subdistrict_coops = data['cooperative'][
        (data['cooperative']['provinceId'] == province_id) &
        (data['cooperative']['districtId'] == district_id) &
        (data['cooperative']['subdistrictId'] == subdistrict_id)
    ]
    
    if len(subdistrict_coops) > 0:
        unique_villages = subdistrict_coops['villageId'].nunique()
        if unique_villages > 0:
            avg_coop_per_village = len(subdistrict_coops) / unique_villages
            kpis['KoperasiPerDesa'] = max(1.0, min(avg_coop_per_village, 3.0))
        else:
            kpis['KoperasiPerDesa'] = 1.0
    else:
        kpis['KoperasiPerDesa'] = 1.0
    
    # KPI_48: Jumlah Penggabungan Desa
    village_mergers = data['village_mergers'][data['village_mergers']['village_id'] == village_id]
    kpis['JumlahPenggabunganDesa'] = len(village_mergers)
    
    # KPI_49: GeoSpatial Data Completeness Score
    # Calculate completeness score based on:
    # 1. Cooperative: longitude, latitude, address
    # 2. Outlets: longitude, latitude (if outlets exist)
    # 3. UPKDK: longitude, latitude, address (if UPKDK exists)
    
    total_points = 0
    filled_points = 0
    
    # Check cooperatives in this village
    village_coops = data['cooperative'][data['cooperative']['villageId'] == village_id]
    if len(village_coops) > 0:
        for _, coop in village_coops.iterrows():
            total_points += 3  # longitude, latitude, address
            if pd.notna(coop.get('longitude')) and coop.get('longitude') != '':
                filled_points += 1
            if pd.notna(coop.get('latitude')) and coop.get('latitude') != '':
                filled_points += 1
            if pd.notna(coop.get('address')) and coop.get('address') != '':
                filled_points += 1
    
    # Check outlets for cooperatives in this village
    village_coop_ids = village_coops['cooperative_id'].tolist() if len(village_coops) > 0 else []
    if len(village_coop_ids) > 0:
        village_outlets = data['outlets'][data['outlets']['cooperativeId'].isin(village_coop_ids)]
        for _, outlet in village_outlets.iterrows():
            # Note: outlets don't have longitude/latitude in current schema, skip
            pass
    
    # Check UPKDK in this village
    village_upkdk = data['upkdk'][data['upkdk']['villageId'] == village_id]
    if len(village_upkdk) > 0:
        for _, upkdk in village_upkdk.iterrows():
            total_points += 3  # longitude, latitude, address
            if pd.notna(upkdk.get('longitude')) and upkdk.get('longitude') != '':
                filled_points += 1
            if pd.notna(upkdk.get('latitude')) and upkdk.get('latitude') != '':
                filled_points += 1
            if pd.notna(upkdk.get('address')) and upkdk.get('address') != '':
                filled_points += 1
    
    # Calculate score
    if total_points > 0:
        kpis['GeoSpatialDataCompletenessScore'] = (filled_points / total_points) * 100
    else:
        kpis['GeoSpatialDataCompletenessScore'] = 0
    
    return kpis

# ============================================================================
# MAIN PROCESSING
# ============================================================================

def generate_fact_kpi():
    """Main function to generate FACT_KPI data."""
    logger.log("START", f"FACT_KPI Generation Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.log("START", f"Test mode: {TEST_VILLAGE_LIMIT} villages" if TEST_VILLAGE_LIMIT else "Full run: all villages")
    
    # Step 1: Load all data
    data = load_all_data()
    
    # Step 2: Create mappings
    mappings = create_mappings(data)
    
    # Step 3: Calculate global aggregates
    global_agg = calculate_global_aggregates(data, mappings)
    
    # Step 4: Get latest period (date_key)
    latest_period = data['dim_period'][
        (data['dim_period']['week'].notna()) & 
        (data['dim_period']['month'].notna())
    ].sort_values('date_key', ascending=False).iloc[0]
    date_key = int(latest_period['date_key'])
    logger.log("INFO", f"Using date_key: {date_key} ({latest_period['period_st']} to {latest_period['period_end_date']})")
    
    # Step 4.5: Create village ID to code mapping (REVERSE of previous approach)
    # Problem: villages.csv has DUPLICATE codes (36,978 duplicates!)
    # Solution: Use village_id (unique) as key, code as value
    # Then match: cooperative.villageId → villages.village_id → villages.code → DIM_GEOGRAPHY.village_id
    village_id_to_code = dict(zip(data['villages']['village_id'], data['villages']['code']))
    logger.log("INFO", f"Created village ID-to-code mapping: {len(village_id_to_code):,} villages")
    
    # Step 4.6: Create district code to internal ID mapping
    # DIM_GEOGRAPHY uses district.code (e.g., "11.05"), cooperative uses district.district_id (integer)
    district_code_to_id = {}
    if 'districts' in data:
        for _, row in data['districts'].iterrows():
            code = row['code']  # Keep as float to match DIM_GEOGRAPHY (which is also float)
            district_code_to_id[code] = row['district_id']
        logger.log("INFO", f"Created district code-to-ID mapping: {len(district_code_to_id):,} districts")
    
    # Step 4.7: Create subdistrict code to internal ID mapping
    # DIM_GEOGRAPHY uses subdistrict.code (string like "11.05.07"), cooperative uses subdistrict_id (integer)
    subdistrict_code_to_id = {}
    if 'subdistricts' in data:
        for _, row in data['subdistricts'].iterrows():
            code = str(row['code'])  # Keep as string
            subdistrict_code_to_id[code] = row['subdistrict_id']
        logger.log("INFO", f"Created subdistrict code-to-ID mapping: {len(subdistrict_code_to_id):,} subdistricts")
    
    # Step 5: Filter geography for village level
    village_geo = data['dim_geography'][data['dim_geography']['village_id'].notna()].copy()
    
    # Limit for testing
    if TEST_VILLAGE_LIMIT:
        village_geo = village_geo.head(TEST_VILLAGE_LIMIT)
    
    total_villages = len(village_geo)
    logger.log("INFO", f"Processing {total_villages:,} villages...")
    
    # Step 6: Process each village
    fact_data = []
    
    for idx, (_, geo_row) in enumerate(village_geo.iterrows(), 1):
        geo_key = geo_row['geo_key']
        province_id = geo_row['province_id']
        district_id = geo_row['district_id']
        subdistrict_id = geo_row['subdistrict_id']
        village_code = geo_row['village_id']  # This is the code from DIM_GEOGRAPHY
        
        # Find which village_id(s) have this code
        # Since codes are duplicated, we need to find ALL village_ids with this code
        matching_village_ids = data['villages'][data['villages']['code'] == village_code]['village_id'].tolist()
        
        if len(matching_village_ids) == 0:
            # Skip if village code not found in villages.csv
            continue
        
        # Find cooperatives for ANY of these village_ids
        village_coops = data['cooperative'][data['cooperative']['villageId'].isin(matching_village_ids)]
        village_coop_ids = village_coops['cooperative_id'].tolist()
        
        # Skip if no cooperatives
        if len(village_coop_ids) == 0:
            continue
        
        # Initialize row
        row = {
            'date_key': date_key,
            'geo_key': geo_key,
        }
        
        # Get district and subdistrict internal IDs for KPI calculations
        # district_id is already float in DIM_GEOGRAPHY, no need to convert
        district_id_internal = district_code_to_id.get(district_id) if pd.notna(district_id) else None
        
        # subdistrict_id is string in DIM_GEOGRAPHY
        subdistrict_id_str = str(subdistrict_id) if pd.notna(subdistrict_id) else None
        subdistrict_id_internal = subdistrict_code_to_id.get(subdistrict_id_str) if subdistrict_id_str else None
        
        # Get dimension keys
        # outlet_id: first outlet in village
        village_outlets = data['outlets'][data['outlets']['cooperativeId'].isin(village_coop_ids)]
        row['outlet_id'] = village_outlets['cooperative_outlet_id'].iloc[0] if len(village_outlets) > 0 else 0
        
        # business_partner_service_id: first partnership service
        village_partnerships = data['partnerships'][data['partnerships']['cooperativeId'].isin(village_coop_ids)]
        row['business_partner_service_id'] = village_partnerships['business_partner_service_id'].iloc[0] if len(village_partnerships) > 0 else 0
        
        # upkdk_id: first UPKDK in village (use first matching village_id)
        village_upkdk = data['upkdk'][data['upkdk']['villageId'].isin(matching_village_ids)]
        row['upkdk_id'] = village_upkdk['upkdk_id'].iloc[0] if len(village_upkdk) > 0 else 0
        
        # klu_id: first KLU from village cooperatives
        village_klus = data['klus'][data['klus']['cooperativeId'].isin(village_coop_ids)]
        row['klu_id'] = village_klus['kluId'].iloc[0] if len(village_klus) > 0 else 0
        
        # Calculate all KPIs (use first matching village_id for geo and upkdk KPIs)
        first_village_id = matching_village_ids[0]
        row.update(calculate_cooperative_kpis(village_coop_ids, data, province_id, district_id, district_id_internal))
        row.update(calculate_geo_kpis(first_village_id, data, province_id, district_id_internal, subdistrict_id_internal))
        row.update(calculate_member_kpis(village_coop_ids, data))
        row.update(calculate_management_kpis(village_coop_ids, data))
        row.update(calculate_outlet_kpis(village_coop_ids, data, global_agg, province_id))
        row.update(calculate_klu_kpis(village_coop_ids, data, global_agg))
        row.update(calculate_partnership_kpis(village_coop_ids, data, global_agg))
        row.update(calculate_upkdk_kpis(first_village_id, data))
        row.update(calculate_domain_kpis(global_agg))
        
        fact_data.append(row)
        
        # Log progress every 50 villages
        if idx % 50 == 0 or idx == total_villages:
            logger.log_progress(idx, total_villages, f"geo_key: {geo_key}")
    
    # Step 7: Create DataFrame
    logger.log("INFO", "Creating DataFrame...")
    df = pd.DataFrame(fact_data)
    
    # Define all expected columns in correct order
    expected_columns = [
        # Dimension keys
        'date_key', 'geo_key', 'outlet_id', 'business_partner_service_id', 'upkdk_id', 'klu_id',
        # KPI columns
        'TotalKoperasiTerdaftar', 'TotalKoperasiPerProvinsi', 'TotalKoperasiPerKabupatenKota',
        'RataRataModalAwalKoperasi', 'TotalModalAwalKoperasi',
        'RasioKoperasiBaruVsTotal', 'RasioPendaftaranMandiriVsPendamping',
        'KoperasiPer10000PendudukDesa',
        'TotalAnggotaKoperasi', 'RasioGenderAnggotaLP',
        'RataRataSimpananPokokPerAnggota', 'RataRataSimpananWajibPerAnggota',
        'RasioAnggotaDenganBICheckingLancar',
        'TotalPengurusKoperasi', 'TotalPengawasKoperasi',
        'RasioGenderPengurus', 'RatioStrukturJabatanLengkap',
        'RataRataAnggotaPerKoperasi',
        'TotalGeraiKoperasi', 'GeraiPerKoperasi', 'SebaranGeraiPerProvinsi',
        'KomposisiTipeGerai', 'ColdStorageCoverage', 'OutletExpansionRate',
        'TotalKLUTerdaftar', 'Top10KBLITerbanyak', 'DistribusiKLUPerProvinsi',
        'ProporsiSektorUtama', 'RataRataKLUPerKoperasi', 'KluDiversificationIndex',
        'TotalAplikasiKemitraan', 'VerifiedPartnershipRate', 'RejectedPartnershipRate',
        'InProgressPartnershipRate', 'DistribusiJenisLayananKemitraan',
        'PartnershipGrowthRate', 'KemitraanPerProvinsi',
        'TotalUPKDKAktif', 'ProporsiJenisUPKDK',
        'UpkdkDenganAksesInternet', 'KondisiBangunanUpkdkLayak',
        'TotalDomainKoperasiTerdaftar', 'DomainKoperasiTerverifikasi',
        'KoperasiPerDesa', 'JumlahPenggabunganDesa', 'GeoSpatialDataCompletenessScore',
        'PersentaseGeraiDenganFotoTerunggah', 'DistribusiJenisGeraiKoperasi',
        'RataRataWaktuProsesAplikasiKemitraan',
        'PersentaseUpkdkDenganAksesAirListrikMemadai'
    ]
    
    # Add missing columns with default value 0
    for col in expected_columns:
        if col not in df.columns:
            df[col] = 0
    
    # Reorder columns
    df = df[expected_columns]
    
    logger.log("INFO", f"DataFrame created with {len(df)} rows and {len(df.columns)} columns")
    
    # Step 8: Apply data types
    logger.log("INFO", "Applying data types...")
    
    # Integer columns (BigInt)
    int_columns = [
        'date_key', 'geo_key', 'outlet_id', 'business_partner_service_id', 'upkdk_id', 'klu_id',
        'TotalKoperasiTerdaftar', 'TotalKoperasiPerProvinsi', 'TotalKoperasiPerKabupatenKota',
        'TotalAnggotaKoperasi', 'TotalPengurusKoperasi', 'TotalPengawasKoperasi',
        'RataRataAnggotaPerKoperasi', 'TotalGeraiKoperasi', 'SebaranGeraiPerProvinsi',
        'TotalKLUTerdaftar', 'Top10KBLITerbanyak', 'DistribusiKLUPerProvinsi',
        'TotalAplikasiKemitraan', 'DistribusiJenisLayananKemitraan', 'KemitraanPerProvinsi',
        'TotalUPKDKAktif', 'TotalDomainKoperasiTerdaftar', 'JumlahPenggabunganDesa'
    ]
    
    for col in int_columns:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype('int64')
    
    # Decimal(18,2) columns
    dec_18_2_columns = [
        'RataRataModalAwalKoperasi', 'TotalModalAwalKoperasi',
        'RataRataSimpananPokokPerAnggota', 'RataRataSimpananWajibPerAnggota',
        'GeraiPerKoperasi', 'RataRataKLUPerKoperasi',
        'KoperasiPer10000PendudukDesa', 'KoperasiPerDesa',
        'RataRataWaktuProsesAplikasiKemitraan'
    ]
    
    for col in dec_18_2_columns:
        if col in df.columns:
            # Ensure float64 type and 2 decimal places
            df[col] = df[col].fillna(0).astype('float64').round(2)
    
    # Decimal(5,4) columns (percentages and indices)
    dec_5_4_columns = [
        'RasioKoperasiBaruVsTotal', 'RasioPendaftaranMandiriVsPendamping',
        'RasioGenderAnggotaLP', 'RasioAnggotaDenganBICheckingLancar',
        'RasioGenderPengurus', 'RatioStrukturJabatanLengkap',
        'KomposisiTipeGerai', 'ColdStorageCoverage', 'OutletExpansionRate',
        'ProporsiSektorUtama', 'KluDiversificationIndex',
        'VerifiedPartnershipRate', 'RejectedPartnershipRate', 'InProgressPartnershipRate',
        'PartnershipGrowthRate', 'ProporsiJenisUPKDK',
        'UpkdkDenganAksesInternet', 'KondisiBangunanUpkdkLayak',
        'DomainKoperasiTerverifikasi', 'GeoSpatialDataCompletenessScore',
        'PersentaseGeraiDenganFotoTerunggah', 'DistribusiJenisGeraiKoperasi',
        'PersentaseUpkdkDenganAksesAirListrikMemadai'
    ]
    
    for col in dec_5_4_columns:
        if col in df.columns:
            # Ensure float64 type, percentage range 0-100, and 4 decimal places
            df[col] = df[col].fillna(0).astype('float64').clip(0, 100).round(4)
    
    # Step 9: Determine version and save
    version = get_next_version_number()
    output_filename = f"{OUTPUT_FILE_PREFIX}{version:03d}.csv"
    output_path = os.path.join(RESULT_DIR, output_filename)
    
    logger.log("SAVING", f"Writing to {output_filename}...")
    # Format decimal columns to ensure proper display (with .0 if needed)
    # Note: pandas will handle formatting automatically, but we ensure float64 type
    df.to_csv(output_path, index=False, float_format='%.10g')
    
    file_size_mb = get_file_size_mb(output_path)
    logger.log("SAVING", f"File saved: {file_size_mb:.2f} MB", "success")
    
    # Step 10: Summary
    logger.log_complete(f"Generated {len(df):,} rows with {len(df.columns)} columns")
    logger.log("SUCCESS", f"Output file: {output_path}", "success")
    
    # Display sample statistics
    logger.log("INFO", "Sample statistics:")
    print(f"  - Total cooperatives processed: {df['TotalKoperasiTerdaftar'].sum():,}")
    print(f"  - Total members: {df['TotalAnggotaKoperasi'].sum():,}")
    print(f"  - Total outlets: {df['TotalGeraiKoperasi'].sum():,}")
    print(f"  - Average cooperatives per village: {df['TotalKoperasiTerdaftar'].mean():.2f}")
    
    return df

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        df = generate_fact_kpi()
        print("\n" + "="*80)
        print("FACT_KPI generation completed successfully!")
        print("="*80)
    except Exception as e:
        logger.log_error(f"Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
