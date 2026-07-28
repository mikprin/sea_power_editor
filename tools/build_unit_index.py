#!/usr/bin/env python3
"""Build the unit glossary CSVs from raw Sea Power unit .ini files.

Source of truth is the game's own files, e.g. share/vessels/ (a copy of
StreamingAssets/original/vessels/). Those are ~8.5 MB and unreadable in bulk, so
this flattens them into two small greppable tables:

    docs/glossary/units.csv           one row per unit alias
    docs/glossary/unit_variants.csv   one row per (alias, variant)
    docs/glossary/unit_weapons.csv    one row per (alias, magazine, ammo slot)
    docs/glossary/ammunition.csv      one row per ammunition alias

Re-run after a game update or after copying in a new category folder:

    python3 tools/build_unit_index.py share/vessels
    python3 tools/build_unit_index.py share/vessels share/aircraft share/land

Categories are taken from the source folder name. Existing rows for a category
are replaced; rows for other categories are left alone, so you can add folders
incrementally.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "docs" / "glossary"
UNITS_CSV = OUT_DIR / "units.csv"
VARIANTS_CSV = OUT_DIR / "unit_variants.csv"
WEAPONS_CSV = OUT_DIR / "unit_weapons.csv"
AMMO_CSV = OUT_DIR / "ammunition.csv"

UNITS_FIELDS = [
    "alias", "category", "unit_type", "role", "ref_field",
    "variant_count", "variants",
    "nations", "service_from", "service_to", "loadouts",
    "displacement_t", "length_m", "beam_m", "max_speed_kt", "telegraph_kt", "armor",
]
VARIANTS_FIELDS = [
    "alias", "category", "variant", "nation", "service_date", "hullnumber",
]
WEAPONS_FIELDS = [
    "alias", "category", "weapon_system", "system_name", "weapon_type",
    "magazine", "ammo_slot", "ammo", "count",
]
AMMO_FIELDS = [
    "alias", "type", "target_type", "guidance", "min_range_nm", "max_range_nm",
    "max_velocity_kt", "warhead", "power", "impact_size", "penetration",
    "mass_kg", "ammo_points",
]

# ammunition/ holds more than weapons: Propulsion, Fueltank, Antenna, Stabilizer,
# Afterburner, Radar, ECM, ESM, Container and friends are sub-components that are
# never a valid Ammunition1= value. Only these Types are real ordnance.
ORDNANCE_TYPES = {
    "Missile", "Torpedo", "Bomb", "Projectile", "RBU", "ASROC", "AerialRocket",
    "MLRS", "Sonobuoy", "Chaff", "Noisemaker", "MOSS", "CIWS", "AirDepthCharge",
    "Paratrooper", "LaserDesignator",
}

# Numeric legend copied from the comment block in any missile .ini.
GUIDANCE = {
    "0": "None", "1": "IR", "2": "SemiActiveRadar", "3": "ActiveRadar",
    "4": "AntiRadiation", "5": "Laser", "6": "TV", "7": "ActiveSonar",
    "8": "PassiveSonar", "9": "Wake",
}
WARHEAD = {
    "0": "BlastFrag", "1": "ArmorPiercing", "2": "HEAT", "3": "Illumination",
    "4": "Cluster", "5": "RunwayCratering",
}

# Vessels, submarines, land units and biologics ship a <alias>_variants.ini whose
# sections are Default/VariantN and are referenced with VariantReference=.
# Aircraft, helicopters and VTOLs ship <alias>_squadrons.ini with Default/SquadronN
# sections, referenced with SquadronReference=. Same shape, different noun.
SIDECARS = (
    ("_variants.ini", "VariantReference", re.compile(r"Variant\d+")),
    ("_squadrons.ini", "SquadronReference", re.compile(r"Squadron\d+")),
)

# Sea Power .ini files use // and # for comments, sometimes mid-line.
_COMMENT = re.compile(r"\s*(//|#).*$")


def parse_ini(path: Path) -> dict[str, dict[str, str]]:
    """Minimal Sea Power .ini reader. Returns {section: {key: value}}.

    Kept deliberately dumb: no interpolation, last key wins, unknown lines
    ignored. Section headers used as decorative separators (e.g. the
    "[---------- Physics ----------]" banners) parse as ordinary sections and
    are harmless.
    """
    data: dict[str, dict[str, str]] = {}
    section = ""
    # Some unit files are UTF-8 with BOM; utf-8-sig strips it so the first
    # [General] header is not swallowed.
    for raw in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith(("//", "#", ";")):
            continue
        if line.startswith("[") and "]" in line:
            section = line[1:line.index("]")]
            data.setdefault(section, {})
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        data.setdefault(section, {})[key.strip()] = _COMMENT.sub("", value).strip()
    return data


def compress_variants(names: list[str], noun: str = "Variant") -> str:
    """'Default,Variant1,Variant2,...,Variant144' -> 'Default,Variant1-144'.

    Ships go up to 144 variants; the uncompressed list is unreadable and the
    numbering is always dense in practice. Any gap is preserved as a separate
    run so the output stays exact. `noun` is Variant or Squadron.
    """
    out: list[str] = []
    run_start = run_end = None
    for name in names:
        m = re.fullmatch(rf"{noun}(\d+)", name)
        if m:
            n = int(m.group(1))
            if run_start is not None and n == run_end + 1:
                run_end = n
                continue
            if run_start is not None:
                out.append(_run(run_start, run_end, noun))
            run_start = run_end = n
            continue
        if run_start is not None:
            out.append(_run(run_start, run_end, noun))
            run_start = run_end = None
        out.append(name)
    if run_start is not None:
        out.append(_run(run_start, run_end, noun))
    return ",".join(out)


def _run(start: int, end: int, noun: str) -> str:
    if start == end:
        return f"{noun}{start}"
    if end == start + 1:
        return f"{noun}{start},{noun}{end}"
    return f"{noun}{start}-{end}"


def first_year(service_date: str) -> int | None:
    """ServiceDate is '1964', '1969|1980', or occasionally junk."""
    m = re.search(r"\b(1[89]\d\d|20\d\d)\b", service_date or "")
    return int(m.group(1)) if m else None


def scan_weapons(alias: str, category: str, base: dict) -> list[dict]:
    """Flatten [WeaponSystemN] -> AssociatedMagazine -> [WeaponMagazineX] ammo.

    A mission overrides a magazine with a sibling section named after the unit,
    e.g. [Taskforce2Vessel1_WeaponSystem1] Ammunition1=... Ammunition1_Count=0,
    so the useful key is the WeaponSystem index plus what it normally holds.
    Magazines with no owning weapon system (decoy launchers, for instance) are
    emitted with a blank weapon_system.
    """
    rows: list[dict] = []
    # Several weapon systems can share one magazine (a twin torpedo mount, a pair
    # of gun houses). Keep every owner so the override target is unambiguous.
    mag_owner: dict[str, list[tuple[str, str, str]]] = {}
    for sect, body in base.items():
        if not re.fullmatch(r"WeaponSystem\d+", sect):
            continue
        mag = body.get("AssociatedMagazine", "")
        if mag:
            mag_owner.setdefault(mag, []).append(
                (sect, body.get("SystemName", ""), body.get("Type", ""))
            )

    for sect, body in base.items():
        if not sect.endswith("Magazine") and not sect.startswith("WeaponMagazine"):
            continue
        owners = sorted(mag_owner.get(sect, []),
                        key=lambda o: int(o[0][len("WeaponSystem"):]))
        system = "+".join(o[0] for o in owners)
        system_name = owners[0][1] if owners else ""
        weapon_type = owners[0][2] if owners else ""
        slots = [k for k in body if re.fullmatch(r"Ammunition\d+", k)]
        for key in sorted(slots, key=lambda k: int(k[len("Ammunition"):])):
            rows.append({
                "alias": alias,
                "category": category,
                "weapon_system": system,
                "system_name": system_name,
                "weapon_type": weapon_type,
                "magazine": sect,
                "ammo_slot": key,
                "ammo": body[key],
                "count": body.get(f"{key}_Count", ""),
            })
    return rows


def scan_ammunition(folder: Path) -> list[dict]:
    """ammunition/ has no variant sidecars - one flat .ini per ordnance type."""
    rows: list[dict] = []
    for path in sorted(folder.glob("*.ini")):
        data = parse_ini(path)
        general = data.get("General", {})
        kind = general.get("Type", "")
        if kind not in ORDNANCE_TYPES:
            continue
        warhead = data.get("WarheadData", {})
        flight = {}
        for sect in ("Kinematics", "Guidance", "Launch", "General", "Ballistics"):
            flight.update(data.get(sect, {}))
        # Range and velocity keys are scattered across sections; merge and pick.
        merged: dict[str, str] = {}
        for body in data.values():
            merged.update(body)
        rows.append({
            "alias": path.stem,
            "type": kind,
            "target_type": general.get("TargetType", ""),
            "guidance": GUIDANCE.get(merged.get("GuidanceType", ""), ""),
            "min_range_nm": merged.get("MinLaunchRange", ""),
            "max_range_nm": merged.get("MaxLaunchRange", ""),
            "max_velocity_kt": merged.get("MaxVelocity", ""),
            "warhead": WARHEAD.get(warhead.get("WarheadType", ""), ""),
            "power": warhead.get("Power", ""),
            "impact_size": warhead.get("ImpactSize", ""),
            "penetration": warhead.get("Penetration", ""),
            "mass_kg": general.get("Mass", ""),
            "ammo_points": general.get("AmmoPoints", ""),
        })
    return rows


def scan_category(folder: Path) -> tuple[list[dict], list[dict], list[dict]]:
    category = folder.name
    units: list[dict] = []
    variants: list[dict] = []
    weapons: list[dict] = []

    sidecar_suffixes = tuple(s for s, _, _ in SIDECARS)
    bases = sorted(
        p for p in folder.glob("*.ini") if not p.name.endswith(sidecar_suffixes)
    )
    for base_path in bases:
        alias = base_path.stem
        base = parse_ini(base_path)
        general = base.get("General", {})
        physics = base.get("Physics", {})

        # AvailableLoadouts lives under [Cargo] on civilians and [WeaponSystems]
        # on warships. This is the vocabulary for LoadoutVariant= in a mission.
        loadouts = ""
        for sect in ("Cargo", "WeaponSystems"):
            if base.get(sect, {}).get("AvailableLoadouts"):
                loadouts = base[sect]["AvailableLoadouts"]
                break

        ref_field, noun, pattern, side_path = "VariantReference", "Variant", None, None
        for suffix, field, pat in SIDECARS:
            candidate = folder / f"{alias}{suffix}"
            if candidate.exists():
                ref_field, noun, pattern, side_path = field, field[:-9], pat, candidate
                break

        names: list[str] = []
        nations: list[str] = []
        years: list[int] = []
        if side_path is not None:
            vdata = parse_ini(side_path)
            # Preserve file order: Default first, then Variant1..N / Squadron1..N.
            for sect, body in vdata.items():
                if sect != "Default" and not pattern.fullmatch(sect):
                    continue
                names.append(sect)
                nation = body.get("Nation", "")
                date = body.get("ServiceDate", "")
                if nation and nation not in nations:
                    nations.append(nation)
                y = first_year(date)
                if y:
                    years.append(y)
                variants.append({
                    "alias": alias,
                    "category": category,
                    "variant": sect,
                    "nation": nation,
                    "service_date": date,
                    "hullnumber": body.get("HullnumberTexture", ""),
                })

        # Skip non-unit config files that happen to live in the folder
        # (e.g. aircraft/shared_settings.ini): no UnitType, no sidecar.
        if not general.get("UnitType") and not names:
            continue

        units.append({
            "alias": alias,
            "category": category,
            "unit_type": general.get("UnitType", ""),
            # [AI] Role is the Air Tasking AllowedUnitRoles vocabulary:
            # Fighter, Bomber, MPA, ASW, ESM, AEW, EW, SEAD, Attack, Recon,
            # Transport, SAR, ASuW, Targeting, Airliner, HeavyBomber.
            "role": base.get("AI", {}).get("Role", ""),
            "ref_field": ref_field,
            "variant_count": len(names),
            "variants": compress_variants(names, noun),
            "nations": "|".join(nations),
            "service_from": min(years) if years else "",
            "service_to": max(years) if years else "",
            "loadouts": loadouts,
            "displacement_t": physics.get("Displacement", ""),
            "length_m": general.get("Length", ""),
            "beam_m": general.get("Beam", ""),
            "max_speed_kt": physics.get("MaxForwardVelocity", ""),
            # TelegraphVelocities is astern,stop,T1,T2,T3,T4,T5 in knots. Only
            # ~50 of 248 hulls override it; the rest use an engine default that
            # is not in the files. Stored raw, comment stripped.
            "telegraph_kt": physics.get("TelegraphVelocities", ""),
            "armor": general.get("ArmorType", ""),
        })
        weapons += scan_weapons(alias, category, base)

    return units, variants, weapons


def merge(path: Path, fields: list[str], rows: list[dict], categories: set[str]) -> None:
    """Replace rows for the scanned categories, keep everything else."""
    kept: list[dict] = []
    if path.exists():
        with path.open(newline="", encoding="utf-8") as fh:
            kept = [r for r in csv.DictReader(fh) if r.get("category") not in categories]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in sorted(kept + rows, key=lambda r: (r["category"], r["alias"])):
            writer.writerow(row)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 1
    all_units: list[dict] = []
    all_variants: list[dict] = []
    all_weapons: list[dict] = []
    all_ammo: list[dict] = []
    categories: set[str] = set()
    for arg in argv[1:]:
        folder = Path(arg)
        if not folder.is_dir():
            print(f"skip: {folder} is not a directory", file=sys.stderr)
            continue
        if folder.name == "ammunition":
            ammo = scan_ammunition(folder)
            print(f"{folder.name}: {len(ammo)} ordnance types")
            all_ammo += ammo
            continue
        units, variants, weapons = scan_category(folder)
        print(f"{folder.name}: {len(units)} units, {len(variants)} variants, "
              f"{len(weapons)} weapon rows")
        all_units += units
        all_variants += variants
        all_weapons += weapons
        categories.add(folder.name)

    if not all_units and not all_ammo:
        print("nothing scanned", file=sys.stderr)
        return 1

    if all_units:
        merge(UNITS_CSV, UNITS_FIELDS, all_units, categories)
        merge(VARIANTS_CSV, VARIANTS_FIELDS, all_variants, categories)
        merge(WEAPONS_CSV, WEAPONS_FIELDS, all_weapons, categories)
    if all_ammo:
        # ammunition.csv has no category column, so it is rewritten wholesale.
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        with AMMO_CSV.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=AMMO_FIELDS)
            writer.writeheader()
            for row in sorted(all_ammo, key=lambda r: r["alias"]):
                writer.writerow(row)
    print(f"wrote {OUT_DIR.relative_to(REPO)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
