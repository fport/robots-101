"""Gerçek deney CSV'sinden başarı oranı ve Wilson %95 aralığı üretir."""
import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path


def summarize(rows):
    if not rows:
        raise ValueError("En az bir deney gerekir")
    ids = [r["episode_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("episode_id değerleri benzersiz olmalı")
    if any(r["success"] not in {"0", "1"} for r in rows):
        raise ValueError("success yalnız 0 veya 1 olabilir; boş sonucu başarı sayma")
    if any(r["success"] == "0" and not r["failure_reason"].strip() for r in rows):
        raise ValueError("Başarısız denemelerin failure_reason alanı dolu olmalı")
    count = len(rows)
    successes = sum(int(r["success"]) for r in rows)
    p = successes/count
    z = 1.96
    denominator = 1 + z*z/count
    center = (p+z*z/(2*count))/denominator
    radius = z*math.sqrt(p*(1-p)/count+z*z/(4*count*count))/denominator
    return {"trials": count, "successes": successes, "success_rate": p,
            "wilson_95_percent": [max(0, center-radius), min(1, center+radius)],
            "failure_reasons": dict(Counter(r["failure_reason"] for r in rows if r["success"] == "0")),
            "note": "Aralık benzer koşullarda bağımsız Bernoulli denemeleri varsayımına dayanır; dağılım kaymasını ölçmez."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    args = parser.parse_args()
    try:
        with args.csv.open(newline="") as handle:
            result = summarize(list(csv.DictReader(handle)))
    except (KeyError, ValueError, OSError) as exc:
        parser.exit(1, f"Değerlendirme hatası: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
