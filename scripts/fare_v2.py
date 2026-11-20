#!/usr/bin/env python3
"""Conservative, date-bounded GTFS Fares v2 for urban Ibagué (2026 only).

Source: Alcaldía de Ibagué, 30 Dec 2025. Does not assign rural or
unconfirmed mixed-branch tariffs and never applies 2026 fares in 2027.
"""
from __future__ import annotations

import csv
import datetime as dt
import re
from pathlib import Path

FARE_SOURCE_URL = "https://ibague.gov.co/portal/noticias/21387-asi-quedaron-definidas-las-tarifas-de-buses-en-ibague"
START_2026 = dt.date(2026, 1, 1)
END_2026 = dt.date(2026, 12, 31)
NETWORK_URBAN = "IBG_URBAN_2026"
NETWORK_UNVERIFIED = "IBG_UNVERIFIED_FARE"
WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
FARE_IDS = {"WK": "IBG_FARE_2026_WK", "SA": "IBG_FARE_2026_SA", "SU": "IBG_FARE_2026_SU"}


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _route_label(route: dict[str, str]) -> str:
    return re.sub(r"^RUTA\s+", "", route["route_short_name"].strip(), flags=re.I).strip()


def _calendar(start: dt.date, end: dt.date, holidays: set[dt.date] | dict[dt.date, str]):
    calendar = []
    for day, mask in (("WK", (1, 1, 1, 1, 1, 0, 0)),
                      ("SA", (0, 0, 0, 0, 0, 1, 0)),
                      ("SU", (0, 0, 0, 0, 0, 0, 1))):
        calendar.append({"service_id": FARE_IDS[day],
                         **{field: str(bit) for field, bit in zip(WEEKDAYS, mask)},
                         "start_date": start.strftime("%Y%m%d"),
                         "end_date": end.strftime("%Y%m%d")})
    exceptions = []
    for date in sorted(holidays):
        if not start <= date <= end or date.weekday() == 6:
            continue
        other = "SA" if date.weekday() == 5 else "WK"
        for service_id, kind in ((FARE_IDS[other], "2"), (FARE_IDS["SU"], "1")):
            exceptions.append({"service_id": service_id,
                               "date": date.strftime("%Y%m%d"), "exception_type": kind})
    return calendar, exceptions


def _active_on(day: dt.date, calendar: list[dict], exceptions: list[dict]) -> set[str]:
    services = {row["service_id"] for row in calendar
                if row[WEEKDAYS[day.weekday()]] == "1"
                and row["start_date"] <= day.strftime("%Y%m%d") <= row["end_date"]}
    for row in exceptions:
        if row["date"] != day.strftime("%Y%m%d"):
            continue
        if row["exception_type"] == "1":
            services.add(row["service_id"])
        else:
            services.discard(row["service_id"])
    return services


def make_2026_fares(routes: list[dict[str, str]], rates: list[dict[str, str]],
                    scope: list[dict[str, str]], start: dt.date, days: int,
                    holidays: set[dt.date] | dict[dt.date, str]):
    """Return tables, fare-only calendar additions, exceptions and audit report.

    Fare timeframes use separate 2026-only service IDs. This avoids applying
    2026 prices to trips that share CT_WK/SA/SU across the 2027 boundary.
    """
    if not 1 <= days <= 366:
        raise ValueError("days must be 1..366")
    expected = {"WK_SA": "3300", "SU_HOLIDAY": "3400"}
    seen = {}
    for row in rates:
        key = row["day_type"]
        if key in seen:
            raise ValueError("Duplicated fare day type: " + key)
        seen[key] = row
    if set(seen) != set(expected):
        raise ValueError("Fare registry requires exactly WK_SA and SU_HOLIDAY")
    for day_type, amount in expected.items():
        row = seen[day_type]
        if (row["amount_cop"] != amount or row["currency"] != "COP"
                or row["valid_from"] != "2026-01-01" or row["valid_until"] != "2026-12-31"
                or row["source_url"] != FARE_SOURCE_URL
                or row["verification_status"] != "official_confirmed"):
            raise ValueError("Inconsistent/unverified 2026 legal fare: " + day_type)
    route_labels = {_route_label(route): route["route_id"] for route in routes}
    if len(route_labels) != len(routes):
        raise ValueError("Ambiguous original route labels")
    decision = {}
    for row in scope:
        key = row["route"]
        if key in decision or row["fare_scope"] not in ("urban_assumed", "unverified"):
            raise ValueError("Invalid/duplicate route fare scope: " + key)
        if not row["reason"].strip():
            raise ValueError("Every fare scope must have rationale: " + key)
        decision[key] = row
    if set(decision) != set(route_labels):
        raise ValueError(f"Unreviewed route fare scope: missing={set(route_labels)-set(decision)}, "
                         f"extra={set(decision)-set(route_labels)}")
    if any("network_id" in r for r in routes):
        raise ValueError("routes.txt already contains network_id; cannot also generate route_networks.txt")

    out_end = start + dt.timedelta(days=days - 1)
    fare_start, fare_end = max(start, START_2026), min(out_end, END_2026)
    report = {"source_url": FARE_SOURCE_URL,
              "tariff_year": 2026,
              "2026_weekday_saturday_cop": 3300,
              "2026_sunday_holiday_cop": 3400,
              "rural_fares": "unknown; never synthesized",
              "year_2027_fares": "unknown; no timeframes valid in 2027",
              "urban_fare_route_labels": sorted(k for k, v in decision.items() if v["fare_scope"] == "urban_assumed"),
              "unpriced_review_route_labels": sorted(k for k, v in decision.items() if v["fare_scope"] == "unverified"),
              "urban_route_scope_status": "provisional (rural/branch ambiguity excluded)",
              "fare_v2_active": fare_start <= fare_end,
              "fare_validity_start": fare_start.isoformat() if fare_start <= fare_end else None,
              "fare_validity_end": fare_end.isoformat() if fare_start <= fare_end else None}
    if fare_start > fare_end:
        return {}, [], [], report

    fare_cal, exceptions = _calendar(fare_start, fare_end, holidays)
    for i in range((fare_end - fare_start).days + 1):
        day = fare_start + dt.timedelta(days=i)
        expected_service = (FARE_IDS["SU"] if day in holidays or day.weekday() == 6 else
                            FARE_IDS["SA"] if day.weekday() == 5 else FARE_IDS["WK"])
        if _active_on(day, fare_cal, exceptions) != {expected_service}:
            raise ValueError(f"Fare holiday schedule mismatch on {day}")

    urban_routes = {route_labels[k] for k, v in decision.items() if v["fare_scope"] == "urban_assumed"}
    if not urban_routes:
        raise ValueError("No urban routes are included in the 2026 fare mapping")
    tables = {
        "networks.txt": [{"network_id": NETWORK_URBAN, "network_name": "Ibagué urbano (tarifa 2026)"},
                         {"network_id": NETWORK_UNVERIFIED, "network_name": "Tarifa no verificada"}],
        "route_networks.txt": [
            {"route_id": route["route_id"],
             "network_id": NETWORK_URBAN if route["route_id"] in urban_routes else NETWORK_UNVERIFIED}
            for route in routes],
        "fare_products.txt": [
            {"fare_product_id": "IBG_URBAN_2026_REGULAR", "fare_product_name": "Pasaje urbano lunes a sábado 2026",
             "amount": "3300", "currency": "COP"},
            {"fare_product_id": "IBG_URBAN_2026_DOM_FEST", "fare_product_name": "Pasaje urbano domingo y festivo 2026",
             "amount": "3400", "currency": "COP"},
        ],
        "timeframes.txt": [
            {"timeframe_group_id": "IBG_2026_REGULAR", "start_time": "00:00:00",
             "end_time": "24:00:00", "service_id": FARE_IDS["WK"]},
            {"timeframe_group_id": "IBG_2026_REGULAR", "start_time": "00:00:00",
             "end_time": "24:00:00", "service_id": FARE_IDS["SA"]},
            {"timeframe_group_id": "IBG_2026_SUNDAY", "start_time": "00:00:00",
             "end_time": "24:00:00", "service_id": FARE_IDS["SU"]},
        ],
        "fare_leg_rules.txt": [
            {"network_id": NETWORK_URBAN, "from_timeframe_group_id": "IBG_2026_REGULAR",
             "fare_product_id": "IBG_URBAN_2026_REGULAR"},
            {"network_id": NETWORK_URBAN, "from_timeframe_group_id": "IBG_2026_SUNDAY",
             "fare_product_id": "IBG_URBAN_2026_DOM_FEST"},
        ],
    }
    report["fare_only_service_ids"] = list(FARE_IDS.values())
    report["fare_only_calendar_exception_rows"] = len(exceptions)
    report["urban_fare_mapped_routes"] = len(urban_routes)
    report["fare_effective_calendar_verified"] = True
    return tables, fare_cal, exceptions, report
