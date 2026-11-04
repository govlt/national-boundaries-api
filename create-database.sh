#!/bin/bash

set -euo pipefail

# Curl options for resilience:
# -f: Fail silently on HTTP errors
# -L: Follow redirects
# --retry 5: Retry up to 5 times
# --retry-delay 5: Wait 5 seconds between retries
# --retry-all-errors: Retry on all errors
# --connect-timeout 20: Abort if connection takes too long
# -A: Custom User Agent with project attribution
CURL_OPTS=(
    -f -L
    --max-redirs 5
    --retry 5
    --retry-delay 5
    --retry-all-errors
    --connect-timeout 20
    -A "NationalBoundariesAPI/1.0 (+https://github.com/govlt/national-boundaries-api)"
)

calculate_md5() {
    local file="$1"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        md5 -r "$file"
    else
        # Linux and other Unix-like systems
        md5sum "$file"
    fi
}

fetch_resource() {
    local url="$1"
    local output_path="$2"

    echo "Downloading: $url -> $output_path"

    # Run curl with the resilient options array
    curl "${CURL_OPTS[@]}" -o "$output_path" "$url"

    # Calculate checksum immediately
    calculate_md5 "$output_path" >> data-sources/data-source-checksums.txt
}

dummy_int="-1"

sql_dummy_cast_to_integer() {
  echo "CASE WHEN $1 IS NULL THEN $dummy_int ELSE CAST($1 AS integer(8)) END"
}

set_back_to_null() {
  ogrinfo -sql "UPDATE $1 SET $2=null WHERE $2=$3" boundaries.sqlite
}

echo "Starting data processing"

rm -rf boundaries.sqlite data-sources
mkdir -p data-sources
touch data-sources/data-source-checksums.txt

echo "Importing counties data into SQLite"
fetch_resource "https://www.registrucentras.lt/aduomenys/?byla=adr_gra_apskritys.json" "data-sources/counties.json"
ogr2ogr -f SQLite boundaries.sqlite data-sources/counties.json -dsco SPATIALITE=YES -lco FID=feature_id -lco GEOMETRY_NAME=geom \
  -sql "SELECT FID AS feature_id, CAST(APS_KODAS AS integer(8)) AS code, APS_PAV as name, APS_PLOTAS as area_ha, APS_R AS created_at FROM counties"
ogrinfo -sql "CREATE UNIQUE INDEX counties_code ON counties(code)" boundaries.sqlite

echo "Importing municipalities data into SQLite"
fetch_resource "https://www.registrucentras.lt/aduomenys/?byla=adr_gra_savivaldybes.json" "data-sources/municipalities.json"
ogr2ogr -append -f SQLite boundaries.sqlite data-sources/municipalities.json -lco FID=feature_id -lco GEOMETRY_NAME=geom \
  -sql "SELECT FID AS feature_id, CAST(SAV_KODAS AS integer(8)) AS code, SAV_PAV as name, SAV_PLOTAS as area_ha, CAST(APS_KODAS AS integer(8)) as county_code, SAV_R AS created_at FROM municipalities"
ogrinfo -sql "CREATE UNIQUE INDEX municipalities_code ON municipalities(code)" boundaries.sqlite
ogrinfo -sql "CREATE INDEX municipalities_county_code ON municipalities(county_code)" boundaries.sqlite

echo "Importing elderships data into SQLite"
fetch_resource "https://www.registrucentras.lt/aduomenys/?byla=adr_gra_seniunijos.json" "data-sources/elderships.json"
ogr2ogr -append -f SQLite boundaries.sqlite data-sources/elderships.json -lco FID=feature_id -lco GEOMETRY_NAME=geom \
  -sql "SELECT FID AS feature_id, CAST(SEN_KODAS AS integer(8)) AS code, SEN_PAV as name, SEN_PLOTAS as area_ha, CAST(SAV_KODAS AS integer(8)) AS municipality_code, SEN_R AS created_at FROM elderships"
ogrinfo -sql "CREATE UNIQUE INDEX elderships_code ON elderships(code)" boundaries.sqlite
ogrinfo -sql "CREATE INDEX elderships_municipality_code_and_name ON elderships(municipality_code, name COLLATE NOCASE)" boundaries.sqlite

echo "Importing residential areas data into SQLite"
fetch_resource "https://www.registrucentras.lt/aduomenys/?byla=adr_gra_gyvenamosios_vietoves.json" "data-sources/residential_areas.json"
ogr2ogr -append -f SQLite boundaries.sqlite data-sources/residential_areas.json -lco FID=feature_id -lco GEOMETRY_NAME=geom \
  -sql "SELECT FID AS feature_id, GYV_KODAS AS code, GYV_PAV as name, PLOTAS as area_ha, CAST(SAV_KODAS AS integer(8)) AS municipality_code, GYV_R as created_at FROM residential_areas"
ogrinfo -sql "CREATE UNIQUE INDEX residential_areas_code ON residential_areas(code)" boundaries.sqlite
ogrinfo -sql "CREATE INDEX residential_municipality_code_and_name ON residential_areas(municipality_code, name COLLATE NOCASE)" boundaries.sqlite

echo "Importing streets data into SQLite"
fetch_resource "https://www.registrucentras.lt/aduomenys/?byla=adr_gra_gatves.json" "data-sources/streets.json"
ogr2ogr -append -f SQLite boundaries.sqlite data-sources/streets.json -lco FID=feature_id -lco GEOMETRY_NAME=geom \
  -sql "SELECT FID AS feature_id, GAT_KODAS AS code, GAT_PAV as name, GAT_PAV_PI AS full_name, GAT_ILGIS as length_m, GYV_KODAS AS residential_area_code, GTV_R AS created_at FROM streets"
ogrinfo -sql "CREATE UNIQUE INDEX streets_code ON streets(code)" boundaries.sqlite
ogrinfo -sql "CREATE INDEX streets_residential_area_code_and_name ON streets(residential_area_code, name COLLATE NOCASE)" boundaries.sqlite

echo "Importing addresses data into SQLite"
fetch_resource "https://www.registrucentras.lt/aduomenys/?byla=adr_stat_lr.csv" "data-sources/addresses-information.psv"
ogr2ogr -f GPKG data-sources/addresses.gpkg data-sources/addresses-information.psv -nln info

echo "Importing address points for each municipality"
fetch_resource "https://www.registrucentras.lt/aduomenys/?byla=adr_gra_adresai_LT.zip" "data-sources/addresses.json.zip"

ogr2ogr -append -f GPKG data-sources/addresses.gpkg "/vsizip/data-sources/addresses.json.zip" -nln points

ogr2ogr -append -f SQLite boundaries.sqlite data-sources/addresses.gpkg -lco FID=feature_id -nln addresses \
  -sql "SELECT points.fid AS feature_id, points.geom, points.AOB_KODAS as code, CAST(info.sav_kodas AS integer(8)) AS municipality_code, points.gyv_kodas AS residential_area_code, points.gat_kodas AS street_code, info.nr AS plot_or_building_number, info.pasto_kodas AS postal_code, NULLIF(info.korpuso_nr, '') AS building_block_number, points.AOB_R AS created_at FROM points INNER JOIN info USING (AOB_KODAS) ORDER BY AOB_KODAS"
ogrinfo -sql "CREATE UNIQUE INDEX addresses_code ON addresses(code)" boundaries.sqlite
ogrinfo -sql "CREATE INDEX addresses_municipality_code ON addresses(municipality_code, plot_or_building_number)" boundaries.sqlite
ogrinfo -sql "CREATE INDEX addresses_residential_area_code ON addresses(residential_area_code, plot_or_building_number)" boundaries.sqlite
ogrinfo -sql "CREATE INDEX addresses_street_code ON addresses(street_code, plot_or_building_number)" boundaries.sqlite

echo "Importing rooms"
fetch_resource "https://www.registrucentras.lt/aduomenys/?byla=adr_pat_lr.csv" "data-sources/rooms.psv"
ogr2ogr -append -f SQLite boundaries.sqlite data-sources/rooms.psv -lco FID=code \
  -sql "SELECT CAST(PAT_KODAS AS integer(8)) as code, CAST(AOB_KODAS AS integer(8)) AS address_code, PATALPOS_NR AS room_number, PAT_NUO AS created_at FROM rooms"
ogrinfo -sql "CREATE INDEX rooms_address_code ON rooms(address_code, room_number)" boundaries.sqlite

echo "Importing parcel points for each municipality"
fetch_resource "https://www.registrucentras.lt/aduomenys/?byla=adr_savivaldybes.csv" "data-sources/municipality_list.csv"

csvcut -d "|" -c "SAV_KODAS" "data-sources/municipality_list.csv" | tail -n +2 | while read -r code; do
  [[ -z "$code" ]] && continue
  echo "Processing municipality code: $code"
  fetch_resource "https://www.registrucentras.lt/aduomenys/?byla=gis_pub_parcels_$code.zip" "data-sources/parcels-$code.zip"
  ogr2ogr -append -f GPKG data-sources/parcels.gpkg "/vsizip/data-sources/parcels-$code.zip" -nln polygons
done

echo "Importing purpose groups"
fetch_resource "https://www.registrucentras.lt/aduomenys/?byla=klas_Paskirties_grupes.csv" "data-sources/purpose_groups.psv"
ogr2ogr -append -f SQLite boundaries.sqlite data-sources/purpose_groups.psv -lco FID=group_id \
  -sql "SELECT CAST(pasg_grupe AS integer(8)) AS group_id, pasg_pav AS name, pasg_pav_i AS full_name, pasg_koregavimo_data AS updated_at FROM purpose_groups"

echo "Importing purpose types"
fetch_resource "https://www.registrucentras.lt/aduomenys/?byla=klas_NTR_paskirciu_tipai.csv" "data-sources/purpose_types.psv"
ogr2ogr -append -f SQLite boundaries.sqlite data-sources/purpose_types.psv -lco FID=purpose_id \
  -sql "SELECT CAST(pask_tipas AS integer(8)) AS purpose_id, CAST(pasg_grupe AS integer(8)) AS purpose_group_id, pask_pav AS name, pask_pav_i AS full_name, pask_pav_i_en AS full_name_en, pask_koregavimo_data AS updated_at FROM purpose_types"

echo "Importing status types"
fetch_resource "https://www.registrucentras.lt/aduomenys/?byla=klas_NTR_objektu_statusai.csv" "data-sources/status_types.psv"
ogr2ogr -append -f SQLite boundaries.sqlite data-sources/status_types.psv -lco FID=status_id \
  -sql "SELECT CAST(osta_statusas AS integer(8)) AS status_id, osta_pav AS name, osta_pav_i AS full_name, osta_pav_en AS name_en, osta_pav_i_en AS full_name_en, osta_koregavimo_data AS updated_at FROM status_types"

echo "Finishing parcels data import into SQLite"
ogr2ogr -append -f SQLite boundaries.sqlite data-sources/parcels.gpkg -nln parcels -lco GEOMETRY_NAME=geom \
  -sql "SELECT polygons.unikalus_nr AS unique_number, CAST(polygons.pask_tipas AS integer(8)) AS purpose_id, $(sql_dummy_cast_to_integer polygons.osta_statusas) AS status_id, polygons.geom, polygons.kadastro_nr as cadastral_number, CAST(polygons.sav_kodas AS integer(8)) AS municipality_code, $(sql_dummy_cast_to_integer polygons.seniunijos_kodas) AS eldership_code, CAST(polygons.skl_plotas AS FLOAT) as area_ha, date(polygons.data_rk) as updated_at FROM polygons"
ogrinfo -sql "CREATE INDEX parcels_unique_number ON parcels(unique_number)" boundaries.sqlite
ogrinfo -sql "CREATE INDEX parcels_cadastral_number ON parcels(cadastral_number)" boundaries.sqlite
ogrinfo -sql "CREATE INDEX parcels_municipality_code ON parcels(municipality_code, unique_number COLLATE NOCASE)" boundaries.sqlite

# Replace back dummy values
set_back_to_null parcels status_id $dummy_int
set_back_to_null parcels eldership_code $dummy_int

echo "Finalizing SQLite database"
ogrinfo boundaries.sqlite -sql "VACUUM"

echo "SQLite database created successfully"