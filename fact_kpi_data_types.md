# FACT_KPI Data Dictionary

This document provides a comprehensive overview of the `FACT_KPI` table, detailing each column's name, data type, unit of measurement, transaction type, and an example value where applicable.

| Column Name                           | Data Type     | UOM        | Transaction Type | Example Value | Description                                                                 |
| :------------------------------------ | :------------ | :--------- | :--------------- | :------------ | :-------------------------------------------------------------------------- |
| `date_key`                            | `Integer`     |            |                  |               | Unique identifier for the date.                                             |
| `geo_key`                             | `Integer`     |            |                  |               | Unique identifier for geographical location.                                |
| `outlet_id`                           | `Integer`     |            |                  |               | Unique identifier for the outlet.                                           |
| `business_partner_service_id`         | `Integer`     |            |                  |               | Unique identifier for business partner service.                             |
| `upkdk_id`                            | `Integer`     |            |                  |               | Unique identifier for UPKDK.                                                |
| `klu_id`                              | `Integer`     |            |                  |               | Unique identifier for KLU.                                                  |
| `TotalKoperasiTerdaftar`              | `BigInt`      | `unit`     | `Calculated`     | `8000`        | Total number of registered cooperatives.                                    |
| `TotalKoperasiPerProvinsi`            | `BigInt`      | `unit`     | `Calculated`     | `120`         | Total number of cooperatives per province.                                  |
| `TotalKoperasiPerKabupatenKota`       | `BigInt`      | `unit`     | `Calculated`     | `50`          | Total number of cooperatives per district/city.                             |
| `RataRataModalAwalKoperasi`           | `Dec(18,2)`   | `IDR`      | `Load`           | `10000000`    | Average initial capital of cooperatives.                                    |
| `TotalModalAwalKoperasi`              | `Dec(18,2)`   | `IDR`      | `Calculated`     | `10000000`    | Total initial capital of cooperatives.                                      |
| `RasioKoperasiBaruVsTotal`            | `Dec(5,4)`    | `%`        | `Load`           |               | Ratio of new cooperatives to total cooperatives. (range 0-100, percentage)  |
| `RasioPendaftaranMandiriVsPendamping` | `Dec(5,4)`    | `%`        | `Load`           |               | Ratio of independent registrations vs assisted registrations. (range 0-100, percentage) |
| `KoperasiPer10000PendudukDesa`        | `Dec(18,2)`   | `unit`     | `Load`           |               | Number of cooperatives per 10,000 rural residents.                          |
| `TotalAnggotaKoperasi`                | `BigInt`      | `Person`   | `Calculated`     |               | Total number of cooperative members.                                        |
| `RasioGenderAnggotaLP`                | `Dec(5,4)`    | `%`        | `Load`           |               | Gender ratio (Male/Female) of cooperative members. (range 0-100, percentage) |
| `RataRataSimpananPokokPerAnggota`     | `Dec(18,2)`   | `IDR`      | `Load`           |               | Average principal savings per member.                                       |
| `RataRataSimpananWajibPerAnggota`     | `Dec(18,2)`   | `IDR`      | `Load`           |               | Average mandatory savings per member.                                       |
| `RasioAnggotaDenganBICheckingLancar`  | `Dec(5,4)`    | `%`        | `Load`           |               | Ratio of members with smooth BI checking records. (range 0-100, percentage) |
| `TotalPengurusKoperasi`               | `BigInt`      | `unit`     | `Calculated`     |               | Total number of cooperative management.                                     |
| `TotalPengawasKoperasi`               | `BigInt`      | `unit`     | `Calculated`     |               | Total number of cooperative supervisors.                                    |
| `RasioGenderPengurus`                 | `Dec(5,4)`    | `%`        | `Load`           |               | Gender ratio of cooperative management. (range 0-100, percentage)           |
| `RatioStrukturJabatanLengkap`         | `Dec(5,4)`    | `%`        | `Load`           |               | Ratio of complete organizational structure. (range 0-100, percentage)       |
| `RataRataAnggotaPerKoperasi`          | `BigInt`      | `unit`     | `Load`           |               | Average number of members per cooperative.                                  |
| `TotalGeraiKoperasi`                  | `BigInt`      | `unit`     | `Calculated`     |               | Total number of cooperative outlets.                                        |
| `GeraiPerKoperasi`                    | `Dec(18,2)`   | `unit`     | `Load`           |               | Number of outlets per cooperative.                                          |
| `SebaranGeraiPerProvinsi`             | `BigInt`      | `unit`     | `Calculated`     |               | Distribution of outlets per province.                                       |
| `KomposisiTipeGerai`                  | `Dec(5,4)`    | `%`        | `Load`           |               | Composition of outlet types. (range 0-100, percentage)                      |
| `ColdStorageCoverage`                 | `Dec(5,4)`    | `%`        | `Load`           |               | Coverage of cold storage facilities. (range 0-100, percentage)              |
| `OutletExpansionRate`                 | `Dec(5,4)`    | `%`        | `Load`           |               | Rate of outlet expansion. (range 0-100, percentage)                         |
| `TotalKLUTerdaftar`                   | `BigInt`      | `unit`     | `Calculated`     |               | Total registered Business Fields (KLU).                                     |
| `Top10KBLITerbanyak`                  | `BigInt`      | `unit`     | `Calculated`     |               | Top 10 most frequent KBLI (Standard Classification of Business Fields).     |
| `DistribusiKLUPerProvinsi`            | `BigInt`      | `unit`     | `Calculated`     |               | Distribution of KLU per province.                                           |
| `ProporsiSektorUtama`                 | `Dec(5,4)`    | `%`        | `Load`           |               | Proportion of main sectors. (range 0-100, percentage)                       |
| `RataRataKLUPerKoperasi`              | `Dec(18,2)`   | `unit`     | `Load`           |               | Average KLU per cooperative.                                                |
| `KluDiversificationIndex`             | `Dec(5,4)`    | `index`    | `Load`           |               | Index of KLU diversification.                                               |
| `TotalAplikasiKemitraan`              | `BigInt`      | `unit`     | `Calculated`     |               | Total partnership applications.                                             |
| `VerifiedPartnershipRate`             | `Dec(5,4)`    | `%`        | `Load`           |               | Rate of verified partnerships. (range 0-100, percentage)                    |
| `RejectedPartnershipRate`             | `Dec(5,4)`    | `%`        | `Load`           |               | Rate of rejected partnerships. (range 0-100, percentage)                    |
| `InProgressPartnershipRate`           | `Dec(5,4)`    | `%`        | `Load`           |               | Rate of in-progress partnerships. (range 0-100, percentage)                 |
| `DistribusiJenisLayananKemitraan`     | `BigInt`      | `unit`     | `Calculated`     |               | Distribution of partnership service types.                                  |
| `PartnershipGrowthRate`               | `Dec(5,4)`    | `%`        | `Load`           |               | Growth rate of partnerships. (range 0-100, percentage)                      |
| `KemitraanPerProvinsi`                | `BigInt`      | `unit`     | `Calculated`     |               | Partnerships per province.                                                  |
| `TotalUPKDKAktif`                     | `BigInt`      | `unit`     | `Calculated`     |               | Total active UPKDK (Cooperative and MSME Business Development Unit).        |
| `ProporsiJenisUPKDK`                  | `Dec(5,4)`    | `%`        | `Load`           |               | Proportion of UPKDK types. (range 0-100, percentage)                        |
| `UpkdkDenganAksesInternet`            | `Dec(5,4)`    | `%`        | `Load`           |               | Percentage of UPKDK with internet access. (range 0-100, percentage)         |
| `KondisiBangunanUpkdkLayak`           | `Dec(5,4)`    | `%`        | `Load`           |               | Percentage of UPKDK with suitable building conditions. (range 0-100, percentage) |
| `TotalDomainKoperasiTerdaftar`        | `BigInt`      | `unit`     | `Calculated`     |               | Total registered cooperative domains.                                       |
| `DomainKoperasiTerverifikasi`         | `Dec(5,4)`    | `%`        | `Load`           |               | Percentage of verified cooperative domains. (range 0-100, percentage)       |
| `KoperasiPerDesa`                     | `Dec(18,2)`   | `unit`     | `Load`           |               | Number of cooperatives per village.                                         |
| `JumlahPenggabunganDesa`              | `BigInt`      | `unit`     | `Calculated`     |               | Number of merged villages.                                                  |
| `GeoSpatialDataCompletenessScore`     | `Dec(5,4)`    | `score`    | `Load`           |               | Score for completeness of geospatial data.                                  |
| `PersentaseGeraiDenganFotoTerunggah`  | `Dec(5,4)`    | `%`        | `Load`           |               | Percentage of outlets with uploaded photos. (range 0-100, percentage)       |
| `DistribusiJenisGeraiKoperasi`        | `Dec(5,4)`    | `%`        | `Load`           |               | Distribution of cooperative outlet types. (range 0-100, percentage)         |
| `RataRataWaktuProsesAplikasiKemitraan`| `Dec(18,2)`   | `hour`     | `Load`           |               | Average processing time for partnership applications.                       |
| `PersentaseUpkdkDenganAksesAirListrikMemadai` | `Dec(5,4)` | `%`        | `Load`           |               | Percentage of UPKDK with adequate water and electricity access. (range 0-100, percentage) |
