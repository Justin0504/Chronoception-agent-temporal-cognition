#!/usr/bin/env python3
"""Emit the provenance of every agent in the panel: what was actually called, when.

Hosted model endpoints have a shelf life set by the vendor, not by the
experiment. All four Chinese-lab endpoints this paper used were withdrawn from
their provider within about twelve weeks of the runs, so "we release our code"
stops meaning "you can run it". What keeps the results auditable is the record
of what was called and the trajectories themselves.

This script reads that record back out of the trajectories rather than restating
it from a table someone has to keep in sync.

    python3 scripts/model_provenance.py
    python3 scripts/model_provenance.py --check-live   # also query the provider
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import glob
import json
import os
import urllib.request
from collections import defaultdict
from pathlib import Path

OUT = Path("pilot-results/model_provenance.csv")

TREES = {
    "pilot-results/*/":            "first-party API",
    "e1-results/*/":               "first-party API",
    "e2-results/*/":               "first-party API",
    "e3-results/*/":               "first-party API",
    "e5-results/*/":               "first-party API",
    "e5b-results/*/":              "first-party API",
    "e11-results/*/":              "first-party API",
    "vultr-results/*/":            "Vultr Serverless Inference",
}


def collect() -> list[dict]:
    agg: dict[tuple, dict] = {}
    for pattern, provider in TREES.items():
        for d in sorted(glob.glob(pattern)):
            label = Path(d).name
            key = (provider, label)
            rec = agg.setdefault(key, {
                "provider": provider, "label": label, "n": 0,
                "first_utc": None, "last_utc": None, "upstream_ids": set(),
            })
            for fp in glob.glob(str(Path(d) / "**" / "*.json"), recursive=True):
                try:
                    j = json.load(open(fp))
                except (OSError, json.JSONDecodeError):
                    continue
                md = j.get("metadata", {})
                rm = md.get("response_metadata", {}) or {}
                rec["n"] += 1
                ts = rm.get("request_started_at")
                if ts is None:
                    steps = j.get("steps") or []
                    ts = steps[0].get("timestamp") if steps else None
                if ts:
                    t = float(ts)
                    rec["first_utc"] = t if rec["first_utc"] is None else min(rec["first_utc"], t)
                    rec["last_utc"] = t if rec["last_utc"] is None else max(rec["last_utc"], t)
                up = rm.get("model") or md.get("model")
                if up:
                    rec["upstream_ids"].add(up)
    rows = []
    for rec in agg.values():
        if not rec["n"]:
            continue
        f = lambda t: (dt.datetime.fromtimestamp(t, dt.UTC).strftime("%Y-%m-%d")
                       if t else "")
        rows.append({
            "provider": rec["provider"], "label": rec["label"], "n": rec["n"],
            "first_utc": f(rec["first_utc"]), "last_utc": f(rec["last_utc"]),
            "upstream_id": ";".join(sorted(rec["upstream_ids"])) or "(not recorded)",
        })
    rows.sort(key=lambda r: (r["provider"], r["label"]))
    return rows


def live_vultr() -> set[str] | None:
    base = os.environ.get("VULTR_BASE_URL", "https://api.vultrinference.com/v1")
    try:
        with urllib.request.urlopen(f"{base}/models", timeout=20) as r:
            return {m["id"] for m in json.loads(r.read().decode()).get("data", [])}
    except Exception as e:
        print(f"  (could not reach {base}: {e})")
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-live", action="store_true",
                    help="query the provider and flag endpoints that are gone")
    args = ap.parse_args()

    rows = collect()
    w = max(len(r["label"]) for r in rows)
    print(f"{'provider':28} {'label':<{w}} {'n':>5}  {'first':10} {'last':10}  upstream id")
    for r in rows:
        print(f"{r['provider']:28} {r['label']:<{w}} {r['n']:5d}  "
              f"{r['first_utc']:10} {r['last_utc']:10}  {r['upstream_id']}")

    if args.check_live:
        live = live_vultr()
        if live is not None:
            print("\nVultr endpoints used by the paper, checked just now:")
            gone = 0
            for r in rows:
                if r["provider"] != "Vultr Serverless Inference":
                    continue
                ok = r["label"] in live
                gone += not ok
                print(f"  {r['label']:<{w}}  {'still listed' if ok else 'WITHDRAWN'}")
            if gone:
                print(f"\n  {gone} of the paper's endpoints are no longer served. The "
                      f"released trajectories remain the record of what they returned.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
