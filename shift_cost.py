"""Денежная оценка учебной смены по двум рассчитанным вариантам."""
import csv
import json
from pathlib import Path

EPS = 1e-9

def economics(p, before, after):
    saved_min = before['finish_minutes']-after['finish_minutes']
    saved_km = before['travel_km']-after['travel_km']
    fuel_saved_l = saved_km*p['truck_fuel_l_per_100km']/100
    fuel_saved = fuel_saved_l*p['fuel_rub_per_litre']
    fee = after['area_ha']*p['service_rub_per_ha']
    input_cost = p['planning_minutes']/60*p['planner_hour_rub']
    time_value = saved_min/60*p['crew_hour_rub']
    comparable = before['area_ha'] == after['area_ha'] and before['late_area_ha'] == after['late_area_ha'] == 0
    return dict(comparable_same_on_time_area=comparable,
                comparable_within_shift=comparable and before['within_shift'] and after['within_shift'], saved_minutes=saved_min,
                saved_km=saved_km, truck_fuel_saved_l=fuel_saved_l,
                truck_fuel_saved_rub=fuel_saved, freed_time_value_rub=time_value,
                service_fee_rub=fee, extra_input_time_value_rub=input_cost,
                net_time_and_fuel_value_rub=time_value+fuel_saved-fee-input_cost,
                cash_net_if_fixed_crew_pay_rub=fuel_saved-fee,
                crew_hour_break_even_rub=(fee+input_cost-fuel_saved)*60/saved_min if saved_min>EPS else None,
                charge_energy_saved_kwh=0.0)



root = Path(__file__).resolve().parent
settings = json.loads((root / "cost_assumptions.json").read_text(encoding="utf-8"))
with (root / "shift_comparison.csv").open(encoding="utf-8-sig") as f:
    rows = {r["strategy"]:r for r in csv.DictReader(f) if r["scenario"] == "base"}
plans = {}
for key in ["nearest", "optimized"]:
    row = rows[key]
    plan = {k:float(row[k]) for k in ["finish_minutes", "travel_km", "area_ha"]}
    plan.update(late_area_ha=0, within_shift=row["within_shift"].lower()=="true")
    plans[key] = plan
result = economics(settings, plans["nearest"], plans["optimized"])
assert round(result["net_time_and_fuel_value_rub"]) == -398
print(json.dumps(result, ensure_ascii=False, indent=2))
