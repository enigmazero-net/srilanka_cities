# Sri Lanka Cities / Postal Codes (Canonical)

This repo contains a cleaned, canonical dataset of Sri Lankan postal codes with place + district + lat/lon.

## Files
- `data/Postal_Codes.canonical.csv` – canonical CSV (Postal Code, Area, District, Latitude, Longitude)
- `data/Postal_Codes.canonical.csv.sha256` – checksum for integrity
- `data/dim_place_sl_latest.json` – latest JSON export (postal_code, place_name, district, lat, lon)
- `data/dim_place_sl_YYYY-MM-DD.json` – dated JSON snapshots
- `data/dim_place_sl_YYYY-MM-DD.sql` – dated SQL snapshots (table data export)
- `scripts/clean_postal_codes.py` – cleaning script used to generate canonical CSV from the raw file

## Notes
The canonical dataset was generated after removing NUL/control characters, normalizing whitespace, and fixing inconsistent district splits.
