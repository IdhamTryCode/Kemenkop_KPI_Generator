"""
Script to generate DIM_GEOGRAPHY and DIM_PERIOD with hierarchical structure
"""

import pandas as pd
from datetime import datetime, timedelta
import calendar

def generate_dim_geography():
    """Generate DIM_GEOGRAPHY from villages.csv and related data sources"""
    print("="*80)
    print("GENERATING DIM_GEOGRAPHY")
    print("="*80)
    
    # Load data sources
    print("\n[1] Loading data sources...")
    villages = pd.read_csv('data_source/villages.csv')
    subdistricts = pd.read_csv('data_source/subdistricts.csv')
    districts = pd.read_csv('data_source/districts.csv')
    provinces = pd.read_csv('data_source/provinces.csv')
    
    print(f"    Villages: {len(villages):,}")
    print(f"    Subdistricts: {len(subdistricts):,}")
    print(f"    Districts: {len(districts):,}")
    print(f"    Provinces: {len(provinces):,}")
    
    # Clean column names
    villages.columns = villages.columns.str.strip()
    subdistricts.columns = subdistricts.columns.str.strip()
    districts.columns = districts.columns.str.strip()
    provinces.columns = provinces.columns.str.strip()
    
    # Create mappings
    print("\n[2] Creating mappings...")
    province_map = dict(zip(provinces['code'], provinces[['province_id', 'name']].values))
    district_map = dict(zip(districts['code'], districts[['district_id', 'name']].values))
    subdistrict_map = dict(zip(subdistricts['code'], subdistricts[['subdistrict_id', 'name']].values))
    
    # Parse codes from villages
    print("\n[3] Parsing village codes...")
    villages['province_code'] = villages['code'].str.split('.').str[0]
    villages['district_code'] = villages['code'].str[:5]  # First 5 chars (XX.XX)
    villages['subdistrict_code_from_code'] = villages['code'].str[:8]  # First 8 chars (XX.XX.XX)
    
    # Build hierarchical dimension
    print("\n[4] Building hierarchical dimension...")
    dim_geo_data = []
    geo_key = 1
    
    # Level 1: Provinces
    print("    Generating province level...")
    for prov_code, (prov_id, prov_name) in province_map.items():
        dim_geo_data.append({
            'geo_key': geo_key,
            'province_id': prov_code,
            'district_id': None,
            'subdistrict_id': None,
            'village_id': None,
            'province_name': prov_name,
            'district_name': None,
            'subdistrict_name': None,
            'village_name': None
        })
        geo_key += 1
    
    # Level 2: Districts
    print("    Generating district level...")
    districts_processed = set()
    for _, district in districts.iterrows():
        district_code = district['code']
        province_code = district['province_code']
        
        if (province_code, district_code) in districts_processed:
            continue
        districts_processed.add((province_code, district_code))
        
        prov_id, prov_name = province_map.get(province_code, (None, None))
        
        dim_geo_data.append({
            'geo_key': geo_key,
            'province_id': province_code,
            'district_id': district_code,
            'subdistrict_id': None,
            'village_id': None,
            'province_name': prov_name,
            'district_name': district['name'],
            'subdistrict_name': None,
            'village_name': None
        })
        geo_key += 1
    
    # Level 3: Subdistricts
    print("    Generating subdistrict level...")
    subdistricts_processed = set()
    for _, subdistrict in subdistricts.iterrows():
        subdistrict_code = subdistrict['code']
        district_code = subdistrict['district_code']
        
        if (district_code, subdistrict_code) in subdistricts_processed:
            continue
        subdistricts_processed.add((district_code, subdistrict_code))
        
        # Get province code from district
        district_info = districts[districts['code'] == district_code]
        if len(district_info) == 0:
            continue
        province_code = district_info.iloc[0]['province_code']
        
        prov_id, prov_name = province_map.get(province_code, (None, None))
        district_name = district_map.get(district_code, [None, None])[1]
        
        dim_geo_data.append({
            'geo_key': geo_key,
            'province_id': province_code,
            'district_id': district_code,
            'subdistrict_id': subdistrict_code,
            'village_id': None,
            'province_name': prov_name,
            'district_name': district_name,
            'subdistrict_name': subdistrict['name'],
            'village_name': None
        })
        geo_key += 1
    
    # Level 4: Villages
    print("    Generating village level...")
    villages_processed = set()
    for _, village in villages.iterrows():
        village_code = village['code']
        subdistrict_code = village['subdistrict_code']
        
        # Skip duplicates
        if village_code in villages_processed:
            continue
        villages_processed.add(village_code)
        
        # Get subdistrict info
        subdistrict_info = subdistricts[subdistricts['code'] == subdistrict_code]
        if len(subdistrict_info) == 0:
            continue
        
        district_code = subdistrict_info.iloc[0]['district_code']
        
        # Get district info
        district_info = districts[districts['code'] == district_code]
        if len(district_info) == 0:
            continue
        province_code = district_info.iloc[0]['province_code']
        
        prov_id, prov_name = province_map.get(province_code, (None, None))
        district_name = district_map.get(district_code, [None, None])[1]
        subdistrict_name = subdistrict_info.iloc[0]['name']
        
        dim_geo_data.append({
            'geo_key': geo_key,
            'province_id': province_code,
            'district_id': district_code,
            'subdistrict_id': subdistrict_code,
            'village_id': village_code,
            'province_name': prov_name,
            'district_name': district_name,
            'subdistrict_name': subdistrict_name,
            'village_name': village['name']
        })
        geo_key += 1
    
    # Create DataFrame
    dim_geography = pd.DataFrame(dim_geo_data)
    
    print(f"\n[5] Generated {len(dim_geography):,} geography records")
    print(f"    Province level: {len(provinces):,}")
    print(f"    District level: {len(districts_processed):,}")
    print(f"    Subdistrict level: {len(subdistricts_processed):,}")
    print(f"    Village level: {len(villages_processed):,}")
    
    # Save to CSV
    output_path = 'result/DIM_GEOGRAPHY.csv'
    dim_geography.to_csv(output_path, index=False)
    print(f"\n[6] Saved to {output_path}")
    
    return dim_geography


def get_week_ranges(year, month):
    """Calculate week ranges for a given month"""
    # Get first and last day of month
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, calendar.monthrange(year, month)[1])
    
    weeks = []
    current_date = first_day
    
    week_num = 1
    while current_date <= last_day:
        # Find the start of the week (Monday)
        days_since_monday = current_date.weekday()
        week_start = current_date - timedelta(days=days_since_monday)
        
        # Find the end of the week (Sunday)
        week_end = week_start + timedelta(days=6)
        
        # Adjust to month boundaries
        if week_start < first_day:
            week_start = first_day
        if week_end > last_day:
            week_end = last_day
        
        weeks.append({
            'week': week_num,
            'start': week_start,
            'end': week_end
        })
        
        # Move to next week
        current_date = week_end + timedelta(days=1)
        week_num += 1
    
    return weeks


def generate_dim_period():
    """Generate DIM_PERIOD with hierarchical structure"""
    print("\n" + "="*80)
    print("GENERATING DIM_PERIOD")
    print("="*80)
    
    # Date range: 2022-2025
    start_year = 2022
    end_year = 2025
    
    print(f"\n[1] Generating period dimension from {start_year} to {end_year}...")
    
    dim_period_data = []
    date_key = 1
    
    for year in range(start_year, end_year + 1):
        # Level 1: Year
        dim_period_data.append({
            'date_key': date_key,
            'year': year,
            'quarter': None,
            'month': None,
            'week': None,
            'period_st': f'{year}-01-01',
            'period_end_date': f'{year}-12-31'
        })
        date_key += 1
        
        # Quarters
        for quarter in range(1, 5):
            # Level 2: Quarter
            quarter_start_month = (quarter - 1) * 3 + 1
            quarter_end_month = quarter * 3
            quarter_start_date = datetime(year, quarter_start_month, 1)
            quarter_end_date = datetime(year, quarter_end_month, calendar.monthrange(year, quarter_end_month)[1])
            
            dim_period_data.append({
                'date_key': date_key,
                'year': year,
                'quarter': quarter,
                'month': None,
                'week': None,
                'period_st': quarter_start_date.strftime('%Y-%m-%d'),
                'period_end_date': quarter_end_date.strftime('%Y-%m-%d')
            })
            date_key += 1
            
            # Months in quarter
            for month in range(quarter_start_month, quarter_end_month + 1):
                # Level 3: Month
                month_start_date = datetime(year, month, 1)
                month_end_date = datetime(year, month, calendar.monthrange(year, month)[1])
                
                dim_period_data.append({
                    'date_key': date_key,
                    'year': year,
                    'quarter': quarter,
                    'month': month,
                    'week': None,
                    'period_st': month_start_date.strftime('%Y-%m-%d'),
                    'period_end_date': month_end_date.strftime('%Y-%m-%d')
                })
                date_key += 1
                
                # Weeks in month
                weeks = get_week_ranges(year, month)
                for week_info in weeks:
                    # Level 4: Week
                    dim_period_data.append({
                        'date_key': date_key,
                        'year': year,
                        'quarter': quarter,
                        'month': month,
                        'week': week_info['week'],
                        'period_st': week_info['start'].strftime('%Y-%m-%d'),
                        'period_end_date': week_info['end'].strftime('%Y-%m-%d')
                    })
                    date_key += 1
    
    # Create DataFrame
    dim_period = pd.DataFrame(dim_period_data)
    
    # Convert quarter, month, week to nullable integer type
    # This ensures integers are stored as integers, not floats
    dim_period['quarter'] = dim_period['quarter'].astype('Int64')
    dim_period['month'] = dim_period['month'].astype('Int64')
    dim_period['week'] = dim_period['week'].astype('Int64')
    
    print(f"\n[2] Generated {len(dim_period):,} period records")
    print(f"    Years: {end_year - start_year + 1}")
    print(f"    Quarters: {(end_year - start_year + 1) * 4}")
    print(f"    Months: {(end_year - start_year + 1) * 12}")
    
    # Save to CSV
    output_path = 'result/DIM_PERIOD.csv'
    dim_period.to_csv(output_path, index=False, na_rep='')
    print(f"\n[3] Saved to {output_path}")
    
    return dim_period


if __name__ == '__main__':
    print("\n" + "="*80)
    print("DIMENSION GENERATION SCRIPT")
    print("="*80)
    
    # Generate DIM_GEOGRAPHY
    dim_geo = generate_dim_geography()
    
    # Generate DIM_PERIOD
    dim_period = generate_dim_period()
    
    print("\n" + "="*80)
    print("GENERATION COMPLETE!")
    print("="*80)
    print(f"\nDIM_GEOGRAPHY: {len(dim_geo):,} records")
    print(f"DIM_PERIOD: {len(dim_period):,} records")
    print("\nFiles saved to result/ directory")

