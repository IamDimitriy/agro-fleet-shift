import csv
from collections import defaultdict
from math import isclose
from pathlib import Path

root = Path(__file__).resolve().parent
def rows(name):
    with (root / name).open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))
resources = defaultdict(list)
for row in rows("service_intervals.csv"):
    resources[row["resource"]].append((float(row["start"]), float(row["end"])))
for name, windows in resources.items():
    windows.sort()
    assert all(b > a for a,b in windows)
    assert all(a[1] <= b[0]+1e-6 for a,b in zip(windows,windows[1:]))
    print(name, round(sum(b-a for a,b in windows),2), "min")
plans = {r["strategy"]:r for r in rows("shift_comparison.csv") if r["scenario"]=="base"}
a, b = plans["nearest"], plans["optimized"]
assert float(a["area_ha"]) == float(b["area_ha"]) == 120
assert isclose(float(a["finish_minutes"])-float(b["finish_minutes"]),20)
assert isclose(float(a["travel_km"])-float(b["travel_km"]),10)
assert isclose(float(b["finish_minutes"]),float(plans["shortest_drive"]["finish_minutes"]))
print("120 ha; saved in this example: 20 min, 10 km")
