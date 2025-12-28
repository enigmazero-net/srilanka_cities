import csv, re, sys
from pathlib import Path

SRC = Path("data/Postal_Codes.csv")          # original
OUT = Path("data/clean/Postal_Codes.cleaned.csv")
BAD = Path("data/clean/Postal_Codes.bad.csv")

# Remove ASCII control chars except newline; collapse whitespace (tabs/multiple spaces) to single space.
CTRL = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")
WS   = re.compile(r"\s+")

FLOAT = re.compile(r"[-+]?\d+(?:\.\d+)?")

def norm_text(s: str) -> str:
    if s is None:
        return ""
    s = CTRL.sub("", s)
    s = WS.sub(" ", s)
    return s.strip()

def extract_float(s: str):
    s = norm_text(s)
    m = FLOAT.search(s)
    return (float(m.group(0)) if m else None)

def fix_district(area: str, district: str) -> tuple[str, str]:
    # Your file frequently has "... Nuwara" stuck in Area and "Eliya" in District.
    a = norm_text(area)
    d = norm_text(district)

    # If district is "Eliya" (or has it), normalize to "Nuwara Eliya"
    if d == "Eliya" or d.endswith(" Eliya") or d.startswith("Eliya "):
        d = "Nuwara Eliya"

    # If area ends with " Nuwara", remove it (since district becomes Nuwara Eliya)
    if a.endswith(" Nuwara"):
        a = a[: -len(" Nuwara")].strip()

    return a, d

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)

    ok = bad = 0
    with SRC.open("rb") as f:
        raw = f.read()

    # Remove NUL bytes early (binary-safe)
    raw = raw.replace(b"\x00", b"")

    text = raw.decode("utf-8", errors="replace").splitlines()

    # Read with csv on the decoded text
    reader = csv.DictReader(text)
    fields_ok = ["Postal Code", "Area", "District", "Latitude", "Longitude"]
    fields_bad = fields_ok + ["Reason"]

    with OUT.open("w", newline="", encoding="utf-8") as out_f, BAD.open("w", newline="", encoding="utf-8") as bad_f:
        w_ok = csv.DictWriter(out_f, fieldnames=fields_ok)
        w_bad = csv.DictWriter(bad_f, fieldnames=fields_bad)
        w_ok.writeheader()
        w_bad.writeheader()

        for row in reader:
            pc = norm_text(row.get("Postal Code", ""))
            area = row.get("Area", "")
            district = row.get("District", "")
            lat_s = row.get("Latitude", "")
            lon_s = row.get("Longitude", "")

            area, district = fix_district(area, district)
            lat = extract_float(lat_s)
            lon = extract_float(lon_s)

            # Basic validation
            if not pc:
                bad += 1
                w_bad.writerow({
                    "Postal Code": pc, "Area": area, "District": district,
                    "Latitude": norm_text(lat_s), "Longitude": norm_text(lon_s),
                    "Reason": "missing postal code"
                })
                continue

            if lat is None or lon is None:
                bad += 1
                w_bad.writerow({
                    "Postal Code": pc, "Area": area, "District": district,
                    "Latitude": norm_text(lat_s), "Longitude": norm_text(lon_s),
                    "Reason": "lat/lon not numeric"
                })
                continue

            # Sri Lanka bounds sanity (loose)
            if not (4.5 <= lat <= 10.5 and 78.5 <= lon <= 83.5):
                bad += 1
                w_bad.writerow({
                    "Postal Code": pc, "Area": area, "District": district,
                    "Latitude": lat, "Longitude": lon,
                    "Reason": "out of bounds"
                })
                continue

            ok += 1
            w_ok.writerow({
                "Postal Code": pc,
                "Area": area,
                "District": district,
                "Latitude": f"{lat:.6f}",
                "Longitude": f"{lon:.6f}",
            })

    print(f"OK rows:  {ok}")
    print(f"BAD rows: {bad}")
    print(f"Wrote: {OUT}")
    print(f"Wrote: {BAD}")

if __name__ == "__main__":
    sys.exit(main())
