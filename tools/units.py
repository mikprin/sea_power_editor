#!/usr/bin/env python3
"""Look up Sea Power unit aliases, variants and loadouts.

Reads docs/glossary/units.csv and docs/glossary/unit_variants.csv, which are
generated from the game's own unit .ini files by tools/build_unit_index.py.

    units.py search <text> [--type Vessel] [--nation Soviet] [--year 1985]
    units.py show <alias>
    units.py variants <alias> [--nation Soviet] [--year 1985] [--limit N]
    units.py loadouts <alias>
    units.py nations
    units.py arsenal <alias>              what a unit carries, by weapon system
    units.py ammo <ammo-alias|search>     ordnance stats
    units.py check <mission.ini>

Output is deliberately terse - it is meant to be read into a prompt, not by a
human scrolling. `show` is the one to reach for before writing a unit section.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
UNITS_CSV = REPO / "docs" / "glossary" / "units.csv"
VARIANTS_CSV = REPO / "docs" / "glossary" / "unit_variants.csv"
WEAPONS_CSV = REPO / "docs" / "glossary" / "unit_weapons.csv"
AMMO_CSV = REPO / "docs" / "glossary" / "ammunition.csv"


def load(path: Path) -> list[dict]:
    if not path.exists():
        sys.exit(
            f"{path.relative_to(REPO)} missing. Build it first:\n"
            f"  python3 tools/build_unit_index.py share/vessels"
        )
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def years(service_date: str) -> list[int]:
    return [int(y) for y in re.findall(r"\b(1[89]\d\d|20\d\d)\b", service_date or "")]


def in_service(service_date: str, year: int) -> bool:
    """ServiceDate is a single year, or 'refit|year' style pairs.

    Treated as "entered service at the earliest listed year". Unknown dates pass,
    because a blank date is missing data rather than a hard exclusion.
    """
    ys = years(service_date)
    return not ys or min(ys) <= year


def find_unit(units: list[dict], alias: str) -> dict:
    for u in units:
        if u["alias"] == alias:
            return u
    matches = [u for u in units if alias.lower() in u["alias"].lower()]
    if len(matches) == 1:
        return matches[0]
    if matches:
        sys.exit(
            f"'{alias}' is ambiguous:\n  "
            + "\n  ".join(m["alias"] for m in matches[:20])
        )
    sys.exit(f"no unit alias matching '{alias}'. Try: units.py search {alias}")


def cmd_search(args) -> None:
    units = load(UNITS_CSV)
    q = args.text.lower()
    rows = []
    for u in units:
        haystack = (
            f"{u['alias']} {u['nations']} {u['loadouts']} {u['role']}"
        ).lower()
        if q and q not in haystack:
            continue
        if args.type and u["unit_type"].lower() != args.type.lower():
            continue
        if args.role and args.role.lower() not in u["role"].lower():
            continue
        if args.category and u["category"].lower() != args.category.lower():
            continue
        if args.nation and args.nation.lower() not in u["nations"].lower():
            continue
        if args.year:
            frm = u["service_from"]
            if frm and int(frm) > args.year:
                continue
        rows.append(u)

    if not rows:
        print("no matches")
        return
    for u in rows:
        span = f"{u['service_from']}-{u['service_to']}" if u["service_from"] else "?"
        extra = u["role"] or u["loadouts"]
        print(
            f"{u['alias']:<34} {u['unit_type']:<10} {u['variant_count']:>3}v  "
            f"{span:<10} {u['nations'][:26]:<26} {extra[:34]}"
        )
    print(f"-- {len(rows)} match(es)")


def cmd_show(args) -> None:
    units = load(UNITS_CSV)
    u = find_unit(units, args.alias)
    variants = [v for v in load(VARIANTS_CSV) if v["alias"] == u["alias"]]

    print(f"Type={u['alias']}")
    print(f"  category      {u['category']}  ({u['unit_type']})")
    if u["role"]:
        print(f"  Role          {u['role']}   <- Air Tasking AllowedUnitRoles")
    if u["length_m"] or u["displacement_t"]:
        print(f"  hull          {u['length_m']} m x {u['beam_m']} m, "
              f"{u['displacement_t']} t, armor {u['armor'] or 'n/a'}")
    if u["max_speed_kt"]:
        print(f"  max speed     {u['max_speed_kt']} kt")
    tv = [v.strip() for v in u.get("telegraph_kt", "").split(",") if v.strip()]
    if len(tv) == 7:
        steps = "  ".join(f"T{i}={tv[i + 1]}" for i in range(6))
        print(f"  Telegraph=    {steps}  (astern {tv[0]})")
    elif u["unit_type"] in ("Vessel", "Submarine"):
        print(f"  Telegraph=    engine default; T5 ~ max speed "
              f"({u['max_speed_kt']} kt)")
    print(f"  LoadoutVariant  {u['loadouts'] or '(none - omit the field)'}")
    print(f"  {u['ref_field']}  {u['variants']}  [{u['variant_count']} total]")
    print(f"  nations       {u['nations']}")
    if u["service_from"]:
        print(f"  service       {u['service_from']}-{u['service_to']}")

    section = "Taskforce1Aircraft1" if u["unit_type"] == "Aircraft" else (
        "Taskforce1Helicopter1" if u["unit_type"] == "Helicopter" else (
            "Taskforce1Submarine1" if u["unit_type"] == "Submarine" else (
                "Taskforce1LandUnit1" if u["unit_type"] == "LandUnit"
                else "Taskforce1Vessel1")))
    print(f"  mission section  [{section}] (or Taskforce2.../Neutral...)")

    by_nation: dict[str, list[str]] = {}
    for v in variants:
        by_nation.setdefault(v["nation"] or "?", []).append(v["variant"])
    if len(by_nation) > 1:
        print("  variants by nation:")
        for nation, names in sorted(by_nation.items(), key=lambda kv: -len(kv[1])):
            shown = ",".join(names[:12])
            more = f" (+{len(names) - 12} more)" if len(names) > 12 else ""
            print(f"    {nation:<14} {shown}{more}")
    print("  full list:      tools/units.py variants " + u["alias"])


def cmd_variants(args) -> None:
    units = load(UNITS_CSV)
    u = find_unit(units, args.alias)
    rows = [v for v in load(VARIANTS_CSV) if v["alias"] == u["alias"]]
    if args.nation:
        rows = [v for v in rows if args.nation.lower() in v["nation"].lower()]
    if args.year:
        rows = [v for v in rows if in_service(v["service_date"], args.year)]
    if not rows:
        print("no variants match those filters")
        return
    for v in rows[: args.limit]:
        print(f"{v['variant']:<12} {v['nation']:<14} "
              f"{v['service_date']:<12} {v['hullnumber']}")
    if len(rows) > args.limit:
        print(f"-- showing {args.limit} of {len(rows)}; raise with --limit")
    else:
        print(f"-- {len(rows)} variant(s)")
    print(f"paste: {u[chr(39)+chr(39)] if False else u['ref_field']}={rows[0]['variant']}")


def cmd_loadouts(args) -> None:
    u = find_unit(load(UNITS_CSV), args.alias)
    if not u["loadouts"]:
        print(f"{u['alias']} has no AvailableLoadouts - omit LoadoutVariant=")
        return
    for name in u["loadouts"].split(","):
        print(f"LoadoutVariant={name.strip()}")


def cmd_arsenal(args) -> None:
    u = find_unit(load(UNITS_CSV), args.alias)
    rows = [w for w in load(WEAPONS_CSV) if w["alias"] == u["alias"]]
    if not rows:
        print(f"{u['alias']} carries no ammunition")
        return
    ammo = {a["alias"]: a for a in load(AMMO_CSV)}
    print(f"{u['alias']}:")
    for w in rows:
        a = ammo.get(w["ammo"], {})
        rng = f"{a.get('max_range_nm')} NM" if a.get("max_range_nm") else ""
        print(f"  {w['weapon_system']:<28} {w['system_name']:<28} "
              f"{w['weapon_type']:<10} {w['ammo']:<26} x{w['count']:<6} {rng}")
    print("\nzero a magazine in a mission with a sibling section:")
    w = rows[0]
    first_system = w["weapon_system"].split("+")[0]
    print(f"  [Taskforce2Vessel1_{first_system}]")
    print(f"  {w['ammo_slot']}={w['ammo']}")
    print(f"  {w['ammo_slot']}_Count=0")


def cmd_ammo(args) -> None:
    rows = load(AMMO_CSV)
    exact = [a for a in rows if a["alias"] == args.query]
    hits = exact or [a for a in rows if args.query.lower() in a["alias"].lower()]
    if args.type:
        hits = [a for a in hits if a["type"].lower() == args.type.lower()]
    if args.target:
        hits = [a for a in hits if a["target_type"].lower() == args.target.lower()]
    if not hits:
        print("no matches")
        return
    if len(hits) == 1:
        a = hits[0]
        print(f"Ammunition1={a['alias']}")
        for k, v in a.items():
            if k != "alias" and v:
                print(f"  {k:<16} {v}")
        carriers = [w["alias"] for w in load(WEAPONS_CSV) if w["ammo"] == a["alias"]]
        if carriers:
            shown = ", ".join(sorted(set(carriers))[:12])
            more = f" (+{len(set(carriers)) - 12} more)" if len(set(carriers)) > 12 else ""
            print(f"  carried by       {shown}{more}")
        return
    for a in hits:
        print(f"{a['alias']:<28} {a['type']:<12} {a['target_type']:<6} "
              f"{a['guidance']:<16} {a['max_range_nm']:>7} NM")
    print(f"-- {len(hits)} match(es)")


UNIT_SECTION = re.compile(
    r"^\[(?:Taskforce\d+|Neutral)"
    r"(Vessel|Submarine|Aircraft|Helicopter|LandUnit|Biologic)\d+\]$"
)


def cmd_check(args) -> None:
    """Validate every unit section in a mission .ini against the glossary.

    Catches the silent-failure class: a Type that does not exist, a variant
    outside the unit's range, a LoadoutVariant the hull does not offer, and the
    Variant/Squadron mix-up between vessels and aircraft.
    """
    units = {u["alias"]: u for u in load(UNITS_CSV)}
    valid_variants: dict[str, set[str]] = {}
    for v in load(VARIANTS_CSV):
        valid_variants.setdefault(v["alias"], set()).add(v["variant"])
    known_ammo = {a["alias"] for a in load(AMMO_CSV)}
    unit_systems: dict[str, set[str]] = {}
    for w in load(WEAPONS_CSV):
        for sysname in w["weapon_system"].split("+"):
            if sysname:
                unit_systems.setdefault(w["alias"], set()).add(sysname)

    path = Path(args.mission)
    if not path.exists():
        sys.exit(f"no such file: {path}")

    section = ""
    fields: dict[str, str] = {}
    problems: list[str] = []
    checked = 0
    # <UnitSection>_WeaponSystemN magazine overrides, collected then resolved
    # against the owning unit once the whole file is parsed.
    overrides: list[tuple[str, str, str, dict[str, str]]] = []
    section_type: dict[str, str] = {}

    OVERRIDE = re.compile(r"^(.+)_(WeaponSystem\d+)$")

    def flush() -> None:
        nonlocal checked
        m = OVERRIDE.match(section)
        if m and any(k.startswith("Ammunition") for k in fields):
            overrides.append((section, m.group(1), m.group(2), dict(fields)))
            return
        if not UNIT_SECTION.match(f"[{section}]") or "Type" not in fields:
            return
        checked += 1
        alias = fields["Type"]
        section_type[section] = alias
        u = units.get(alias)
        if u is None:
            problems.append(f"[{section}] Type={alias} -- alias not found in glossary")
            return

        want = u["ref_field"]                      # VariantReference or SquadronReference
        other = ("SquadronReference" if want == "VariantReference"
                 else "VariantReference")
        if other in fields:
            problems.append(
                f"[{section}] {alias} uses {other}= but this unit needs {want}="
            )
        ref = fields.get(want)
        if ref and ref not in valid_variants.get(alias, set()):
            problems.append(
                f"[{section}] {want}={ref} invalid for {alias}; valid: {u['variants']}"
            )

        lo = fields.get("LoadoutVariant")
        if lo:
            allowed = [x.strip() for x in u["loadouts"].split(",") if x.strip()]
            if not allowed:
                problems.append(
                    f"[{section}] {alias} has no AvailableLoadouts but sets "
                    f"LoadoutVariant={lo} -- omit the field"
                )
            elif lo not in allowed:
                problems.append(
                    f"[{section}] LoadoutVariant={lo} invalid for {alias}; "
                    f"valid: {','.join(allowed)}"
                )

    for raw in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = raw.strip()
        if line.startswith("[") and "]" in line:
            flush()
            section = line[1:line.index("]")]
            fields = {}
            continue
        if "=" in line and not line.startswith((";", "#", "//")):
            k, _, v = line.partition("=")
            fields[k.strip()] = re.sub(r"\s*(//|#).*$", "", v).strip()
    flush()

    for label, owner, system, body in overrides:
        alias = section_type.get(owner)
        if alias is None:
            problems.append(
                f"[{label}] overrides {owner}, which has no unit section in this file"
            )
            continue
        systems = unit_systems.get(alias, set())
        if systems and system not in systems:
            problems.append(
                f"[{label}] {alias} has no {system}; it has "
                f"{','.join(sorted(systems))}"
            )
        for key, value in body.items():
            if re.fullmatch(r"Ammunition\d+", key) and value not in known_ammo:
                problems.append(
                    f"[{label}] {key}={value} -- ammunition alias not found"
                )

    for problem in problems:
        print(problem)
    print(f"-- {checked} unit section(s) checked, {len(problems)} problem(s)")
    if problems:
        sys.exit(1)


def cmd_nations(args) -> None:
    counts: dict[str, int] = {}
    for v in load(VARIANTS_CSV):
        counts[v["nation"] or "?"] = counts.get(v["nation"] or "?", 0) + 1
    for nation, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"{nation:<18} {n}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="find aliases by substring")
    s.add_argument("text", nargs="?", default="")
    s.add_argument("--type", help="Vessel|Submarine|Aircraft|Helicopter|VTOL|LandUnit|Biologic")
    s.add_argument("--role", help="Fighter|MPA|ASW|ESM|AEW|EW|SEAD|Attack|Recon|Transport|SAR|...")
    s.add_argument("--category", help="vessels|aircraft|land_units|biologic")
    s.add_argument("--nation")
    s.add_argument("--year", type=int)
    s.set_defaults(func=cmd_search)

    s = sub.add_parser("show", help="spec card for one alias")
    s.add_argument("alias")
    s.set_defaults(func=cmd_show)

    s = sub.add_parser("variants", help="exact variant list")
    s.add_argument("alias")
    s.add_argument("--nation")
    s.add_argument("--year", type=int)
    s.add_argument("--limit", type=int, default=40)
    s.set_defaults(func=cmd_variants)

    s = sub.add_parser("loadouts", help="valid LoadoutVariant values")
    s.add_argument("alias")
    s.set_defaults(func=cmd_loadouts)

    s = sub.add_parser("nations", help="nation keys and variant counts")
    s.set_defaults(func=cmd_nations)

    s = sub.add_parser("arsenal", help="what a unit carries, by weapon system")
    s.add_argument("alias")
    s.set_defaults(func=cmd_arsenal)

    s = sub.add_parser("ammo", help="ordnance stats and who carries it")
    s.add_argument("query", nargs="?", default="")
    s.add_argument("--type", help="Missile|Torpedo|Bomb|Projectile|RBU|ASROC|...")
    s.add_argument("--target", help="AAW|ASuW|ASW")
    s.set_defaults(func=cmd_ammo)

    s = sub.add_parser("check", help="validate unit refs in a mission .ini")
    s.add_argument("mission")
    s.set_defaults(func=cmd_check)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
